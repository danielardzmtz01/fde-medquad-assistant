# src/backend/app/telemetry/logger.py
"""Structured JSON Logger with PII/Secret Scrubbing and ADK Intent vs. Outcome Callbacks."""

import re
import json
import logging
import time
from typing import Any, Dict
from app.telemetry.tracing import get_tracer

logger = logging.getLogger("medquad_assistant.telemetry")
logger.setLevel(logging.INFO)

# Regex scrubbing patterns for secrets and sensitive medical identifiers
SCRUB_PATTERNS = [
    (re.compile(r"AIzaSy[A-Za-z0-9_-]{35}"), "[REDACTED_GOOGLE_API_KEY]"),
    (re.compile(r"sk-[A-Za-z0-9]{32,48}"), "[REDACTED_API_KEY]"),
    (re.compile(r"\b\d{3}-\d{2}-\d{4}\b"), "[REDACTED_SSN]"),
    (re.compile(r"\bMRN[:#\s]?\s*\d{6,10}\b", re.IGNORECASE), "[REDACTED_MRN]"),
    (re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b"), "[REDACTED_EMAIL]"),
]


class JSONFormatter(logging.Formatter):
    """Custom logging formatter that outputs structured JSON with PII and credential scrubbing."""

    def format(self, record: logging.LogRecord) -> str:
        log_data = {
            "timestamp": self.formatTime(record, self.datefmt),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }

        # Include extra metadata if passed
        if hasattr(record, "extra_metadata"):
            log_data["metadata"] = getattr(record, "extra_metadata")

        log_str = json.dumps(log_data)

        # Apply regex scrubbers
        for pattern, replacement in SCRUB_PATTERNS:
            log_str = pattern.sub(replacement, log_str)

        return log_str


# Attach custom handler to root / module logger
_stream_handler = logging.StreamHandler()
_stream_handler.setFormatter(JSONFormatter())
logger.addHandler(_stream_handler)
logger.propagate = False

# Active OpenTelemetry spans dictionary for intent vs outcome matching
active_telemetry_spans: Dict[str, Any] = {}


# =========================================================================
# ADK Intent vs. Outcome Callbacks
# =========================================================================

def before_model_logging_callback(callback_context: Any, llm_request: Any) -> None:
    """Logs the agent's intent to call the LLM model (Intent Tracking)."""
    tracer = get_tracer()
    agent_name = getattr(callback_context, "agent_name", "orchestrator")
    model_name = getattr(llm_request, "model", "gemini-3.6-pro")

    extra = {
        "event": "llm_call_intent",
        "agent_name": agent_name,
        "model": model_name,
    }
    logger.info(
        f"Agent '{agent_name}' is intending to invoke model '{model_name}'",
        extra={"extra_metadata": extra},
    )

    if tracer:
        span = tracer.start_span(f"llm_intent_{agent_name}")
        span.set_attribute("model", str(model_name))
        span.set_attribute("agent", str(agent_name))
        active_telemetry_spans[f"model_{id(llm_request)}"] = span


def after_model_logging_callback(callback_context: Any, llm_response: Any) -> None:
    """Logs the outcome of the LLM model invocation (Outcome Tracking)."""
    agent_name = getattr(callback_context, "agent_name", "orchestrator")
    finish_reason = getattr(llm_response, "finish_reason", "completed")

    extra = {
        "event": "llm_call_outcome",
        "agent_name": agent_name,
        "finish_reason": str(finish_reason),
    }
    logger.info(
        f"Agent '{agent_name}' received model response successfully with finish_reason: {finish_reason}",
        extra={"extra_metadata": extra},
    )

    for key, span in list(active_telemetry_spans.items()):
        if key.startswith("model_"):
            span.set_attribute("finish_reason", str(finish_reason))
            span.end()
            active_telemetry_spans.pop(key, None)


def before_tool_logging_callback(tool: Any, args: Dict[str, Any], tool_context: Any = None) -> None:
    """Logs the agent's intent to execute a tool (Tool Intent Tracking)."""
    tracer = get_tracer()
    tool_name = getattr(tool, "name", str(tool))
    agent_name = getattr(tool_context, "agent_name", "researcher")

    clean_args = json.loads(json.dumps(args, default=str))
    # Truncate large payloads in logs
    for k, v in clean_args.items():
        if isinstance(v, str) and len(v) > 150:
            clean_args[k] = v[:150] + "... [TRUNCATED]"

    extra = {
        "event": "tool_execution_intent",
        "agent_name": agent_name,
        "tool_name": tool_name,
        "arguments": clean_args,
    }
    logger.info(
        f"Agent '{agent_name}' is executing tool '{tool_name}'",
        extra={"extra_metadata": extra},
    )

    if tracer:
        span = tracer.start_span(f"tool_exec_{tool_name}")
        span.set_attribute("tool_name", tool_name)
        span.set_attribute("agent", agent_name)
        active_telemetry_spans[f"tool_{tool_name}_{id(tool_context)}"] = span


def after_tool_logging_callback(tool: Any, args: Dict[str, Any], tool_context: Any = None, tool_response: Any = None) -> Any:
    """Logs the outcome of the tool execution (Tool Outcome Tracking)."""
    tool_name = getattr(tool, "name", str(tool))
    agent_name = getattr(tool_context, "agent_name", "researcher")

    clean_result = str(tool_response)[:250] + "... [TRUNCATED]" if len(str(tool_response)) > 250 else str(tool_response)
    is_error = isinstance(tool_response, dict) and "error" in tool_response

    extra = {
        "event": "tool_execution_outcome",
        "agent_name": agent_name,
        "tool_name": tool_name,
        "status": "FAILED" if is_error else "SUCCESS",
        "result_preview": clean_result,
    }
    logger.info(
        f"Agent '{agent_name}' completed tool '{tool_name}' with status: {extra['status']}",
        extra={"extra_metadata": extra},
    )

    span_id = f"tool_{tool_name}_{id(tool_context)}"
    span = active_telemetry_spans.pop(span_id, None)
    if span:
        span.set_attribute("status", extra["status"])
        span.end()

    return tool_response
