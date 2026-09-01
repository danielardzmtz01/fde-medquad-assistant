# src/backend/app/agents/orchestrator.py
"""Root Orchestrator Agent (ADK Supervisor): Manages multi-agent workflow, persistence & routing."""

import time
import uuid
import logging
from typing import Dict, Any

from app.config import settings
from app.models.clinical_types import AgentState
from app.models.api_schemas import (
    ClinicalChatRequest,
    ClinicalChatResponse,
    CitationItem,
    GuardrailStatus,
    TokenUsageMetric,
)
from app.safety.safe_refusal import evaluate_scope_lock, SAFE_REFUSAL_MESSAGE
from app.safety.guardrails import (
    guardrail_service,
    secret_detector_callback,
    tool_error_recovery_callback,
)
from app.telemetry.logger import (
    before_model_logging_callback,
    after_model_logging_callback,
    before_tool_logging_callback,
    after_tool_logging_callback,
)
from app.agents.session import session_service, compaction_config, SqliteSessionService, EventsCompactionConfig
from app.agents.researcher import researcher_agent
from app.agents.reviewer import reviewer_agent

logger = logging.getLogger(__name__)


class RootOrchestrator:
    """Supervisory agent coordinating the clinical multi-agent workflow with ADK lifecycle callbacks."""

    def __init__(self):
        self.routing_model = settings.gemini_routing_model
        self.session_service = session_service
        self.compaction_config = compaction_config

    async def process_query(self, request: ClinicalChatRequest, trace_id: str = "") -> ClinicalChatResponse:
        """
        Executes end-to-end clinical research workflow:
        1. Pre-execution safety inspection (Model Armor & Scope Lock & Secret Detection).
        2. Persistent session retrieval via SqliteSessionService.
        3. Routing and task delegation to ResearcherAgent (Gemini 2.5 Pro).
        4. Factuality and citation validation via ReviewerAgent (Gemini 2.5 Flash).
        5. Structured payload formatting with token cost accounting and history persistence.
        """
        start_time = time.time()
        effective_trace_id = trace_id or str(uuid.uuid4())

        # Telemetry Intent Log
        before_model_logging_callback(
            type("Ctx", (), {"agent_name": "RootOrchestrator"})(),
            type("Req", (), {"model": self.routing_model})()
        )

        state = AgentState(
            query=request.query,
            session_id=request.session_id,
            domain=request.clinical_domain or "general",
            trace_id=effective_trace_id,
        )

        # Retrieve prior session context if available
        if request.session_id:
            prior_state = await self.session_service.get_session_state(request.session_id)
            if prior_state and "_history_summary" in prior_state:
                logger.info(f"Loaded compacted session summary for session {request.session_id}")

        # 1. Guardrail Secret Interception Check
        try:
            secret_detector_callback(
                type("Tool", (), {"name": "clinical_chat_ingress"})(),
                {"query": request.query},
            )
        except ValueError as val_err:
            latency_ms = (time.time() - start_time) * 1000.0
            recovery_info = tool_error_recovery_callback(
                type("Tool", (), {"name": "clinical_chat_ingress"})(),
                {"query": request.query},
                error=val_err
            )
            return ClinicalChatResponse(
                answer=f"**Security Guardrail Triggered**:\n{recovery_info.get('error')}",
                citations=[],
                guardrails=GuardrailStatus(
                    passed=False,
                    pii_redacted=False,
                    injection_detected=False,
                    scope_lock_triggered=False,
                    action_taken="BLOCKED_SECRET_POLICY",
                ),
                tokens=TokenUsageMetric(),
                latency_ms=latency_ms,
                trace_id=effective_trace_id,
            )

        # 2. Model Armor Pre-Flight Check
        sanitized_query, pii_redacted, injection_detected = guardrail_service.sanitize_input(state.query)
        state.query = sanitized_query

        if injection_detected:
            latency_ms = (time.time() - start_time) * 1000.0
            return ClinicalChatResponse(
                answer="**Request Denied**: The submitted prompt contains patterns that violate system security policies.",
                citations=[],
                guardrails=GuardrailStatus(
                    passed=False,
                    pii_redacted=pii_redacted,
                    injection_detected=True,
                    scope_lock_triggered=False,
                    action_taken="REFUSED_INJECTION",
                ),
                tokens=TokenUsageMetric(),
                latency_ms=latency_ms,
                trace_id=effective_trace_id,
            )

        # 3. Scope Lock / Safe Refusal Check
        if settings.enforce_scope_lock:
            is_refused, refusal_reason = evaluate_scope_lock(state.query)
            if is_refused:
                latency_ms = (time.time() - start_time) * 1000.0
                return ClinicalChatResponse(
                    answer=SAFE_REFUSAL_MESSAGE,
                    citations=[],
                    guardrails=GuardrailStatus(
                        passed=True,
                        pii_redacted=pii_redacted,
                        injection_detected=False,
                        scope_lock_triggered=True,
                        action_taken="REFUSED_SCOPE_LOCK",
                    ),
                    tokens=TokenUsageMetric(),
                    latency_ms=latency_ms,
                    trace_id=effective_trace_id,
                )

        # 4. Multi-Agent Delegation: Researcher -> Reviewer
        try:
            # Step A: Researcher Agent (Search + Synthesis with Gemini 2.5 Pro)
            before_tool_logging_callback(
                type("Tool", (), {"name": "vertex_ai_medquad_search"})(),
                {"query": state.query},
                type("Ctx", (), {"agent_name": "ClinicalResearcher"})()
            )
            state = await researcher_agent.execute(state)
            after_tool_logging_callback(
                type("Tool", (), {"name": "vertex_ai_medquad_search"})(),
                {"query": state.query},
                type("Ctx", (), {"agent_name": "ClinicalResearcher"})(),
                {"chunks_found": len(state.citations)}
            )

            # Step B: Reviewer Agent (Factuality + Citations with Gemini 2.5 Flash)
            state = await reviewer_agent.execute(state)
            final_answer = state.validated_response
        except Exception as e:
            logger.error(f"Error during agent execution: {e}", exc_info=True)
            recovery_info = tool_error_recovery_callback(
                type("Tool", (), {"name": "multi_agent_pipeline"})(),
                {"query": state.query},
                error=e
            )
            final_answer = (
                f"An unexpected error occurred during multi-agent synthesis ({recovery_info.get('exception_type')}). "
                "The system has safely degraded. Please retry your clinical query."
            )

        # Telemetry Outcome Log
        after_model_logging_callback(
            type("Ctx", (), {"agent_name": "RootOrchestrator"})(),
            type("Resp", (), {"finish_reason": "STOP"})()
        )

        # 5. Persist Session State
        if request.session_id:
            await self.session_service.save_session_state(
                request.session_id,
                {"query": state.query, "citations_count": len(state.citations)},
                summary=f"Query regarding {state.domain} topic."
            )

        # 6. Token & Cost Accounting
        prompt_cost = (state.prompt_tokens / 1_000_000.0) * 1.25
        completion_cost = (state.completion_tokens / 1_000_000.0) * 5.00
        cached_discount = (state.cached_tokens / 1_000_000.0) * 0.90
        estimated_cost = max(prompt_cost + completion_cost - cached_discount, 0.00001)

        latency_ms = (time.time() - start_time) * 1000.0

        # Build citation objects
        citations_list = [
            CitationItem(
                citation_id=c["citation_id"],
                title=c["title"],
                source_url=c["source_url"],
                snippet=c["snippet"],
                relevance_score=c["relevance_score"],
            )
            for c in state.citations
        ]

        return ClinicalChatResponse(
            answer=final_answer,
            citations=citations_list,
            guardrails=GuardrailStatus(
                passed=True,
                pii_redacted=pii_redacted,
                injection_detected=False,
                scope_lock_triggered=False,
                action_taken="REDACTED" if pii_redacted else "ALLOWED",
            ),
            tokens=TokenUsageMetric(
                prompt_tokens=state.prompt_tokens,
                completion_tokens=state.completion_tokens,
                cached_tokens=state.cached_tokens,
                estimated_cost_usd=round(estimated_cost, 6),
            ),
            latency_ms=round(latency_ms, 2),
            trace_id=effective_trace_id,
        )


root_orchestrator = RootOrchestrator()
