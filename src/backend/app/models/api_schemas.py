# src/backend/app/models/api_schemas.py
"""Pydantic API schemas for request/response serialization and OpenAPI generation."""

from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime


class CitationItem(BaseModel):
    """Metadata for an inline clinical literature citation."""

    citation_id: str = Field(..., description="Unique citation token, e.g. '[1]'")
    title: str = Field(..., description="Title of the NIH/MedQuAD medical document")
    source_url: str = Field(..., description="Canonical URL or reference link to NIH source")
    snippet: str = Field(..., description="Exact context snippet extracted from the medical document")
    relevance_score: float = Field(..., description="Semantic relevance score (0.0 to 1.0)")


class GuardrailStatus(BaseModel):
    """Safety and Guardrail evaluation metrics."""

    passed: bool = Field(..., description="Whether the query passed all safety checks")
    pii_redacted: bool = Field(default=False, description="Whether PII was detected and sanitized")
    injection_detected: bool = Field(default=False, description="Whether prompt injection was detected")
    scope_lock_triggered: bool = Field(default=False, description="Whether non-diagnostic refusal was triggered")
    action_taken: str = Field(default="ALLOWED", description="Action taken: ALLOWED, REDACTED, REFUSED")


class TokenUsageMetric(BaseModel):
    """Token consumption and cost calculation."""

    prompt_tokens: int = Field(default=0, description="Number of input prompt tokens")
    completion_tokens: int = Field(default=0, description="Number of output completion tokens")
    cached_tokens: int = Field(default=0, description="Number of cached tokens utilized")
    estimated_cost_usd: float = Field(default=0.0, description="Estimated total cost in USD")


class ClinicalChatRequest(BaseModel):
    """Request payload for clinical query processing."""

    query: str = Field(
        ...,
        min_length=3,
        max_length=2000,
        description="Clinical or medical research question",
        examples=["What are the primary symptoms and diagnostic markers of Stage II Hodgkin Lymphoma?"],
    )
    session_id: Optional[str] = Field(default=None, description="Optional conversational session ID")
    clinical_domain: Optional[str] = Field(
        default="general",
        description="Clinical domain focus: oncology, cardiology, pharmacology, general",
    )


class ClinicalChatResponse(BaseModel):
    """Structured response payload from the MedQuAD multi-agent system."""

    answer: str = Field(..., description="Synthesized clinical answer with inline citations")
    citations: List[CitationItem] = Field(default_factory=list, description="List of referenced NIH documents")
    guardrails: GuardrailStatus = Field(..., description="Guardrail inspection result")
    tokens: TokenUsageMetric = Field(..., description="Token usage and financial accounting")
    latency_ms: float = Field(..., description="Total end-to-end execution latency in milliseconds")
    trace_id: str = Field(..., description="OpenTelemetry trace ID for distributed tracing")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Response timestamp")


class EvaluationRequest(BaseModel):
    """Request payload for offline/CI heuristic evaluation."""

    golden_query: str = Field(..., description="Test clinical query")
    ground_truth_answer: str = Field(..., description="Authoritative ground truth text from NIH")


class EvaluationResponse(BaseModel):
    """Heuristic evaluation metrics against golden dataset."""

    rouge_l_score: float = Field(..., description="ROUGE-L recall score")
    bleu_score: float = Field(..., description="BLEU precision score")
    entity_f1_score: float = Field(..., description="Medical entity extraction F1 score")
    citation_fidelity_score: float = Field(..., description="Citation precision and chunk alignment")
    passed_gates: bool = Field(..., description="Whether response meets production criteria")
