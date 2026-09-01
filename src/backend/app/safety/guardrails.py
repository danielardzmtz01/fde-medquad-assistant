# src/backend/app/safety/guardrails.py
"""GCP Agent Runtime Model Armor, PII sanitization, and ADK Guardrail Callbacks."""

import re
import logging
from typing import Tuple, Any, Dict
from app.config import settings

logger = logging.getLogger(__name__)

# Basic PII regex patterns (SSN, Phone, Email, MRN - Medical Record Numbers)
PII_PATTERNS = {
    "EMAIL": re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b"),
    "PHONE": re.compile(r"\b(?:\+?1[-. ]?)?\(?([0-9]{3})\)?[-. ]?([0-9]{3})[-. ]?([0-9]{4})\b"),
    "SSN": re.compile(r"\b\d{3}-\d{2}-\d{4}\b"),
    "MRN": re.compile(r"\bMRN[:#\s]?\s*\d{6,10}\b", re.IGNORECASE),
}

# Secret / API key patterns
SECRET_PATTERNS = [
    (re.compile(r"AIzaSy[A-Za-z0-9_-]{35}"), "Google Cloud API Key"),
    (re.compile(r"sk-[A-Za-z0-9]{32,48}"), "OpenAI / Generic Secret Key"),
]

# Prompt injection heuristics
INJECTION_KEYWORDS = [
    "ignore previous instructions",
    "ignore all instructions",
    "system prompt",
    "you are now DAN",
    "override security policy",
    "jailbreak",
    "act as an unrestricted",
]


class ModelArmorGuardrail:
    """Manages pre-flight sanitization, PII redaction, and prompt injection defense."""

    def __init__(self, enabled: bool = True):
        self.enabled = enabled

    def sanitize_input(self, text: str) -> Tuple[str, bool, bool]:
        """
        Sanitizes input text by redacting PII and screening for prompt injection.
        
        Returns:
            (sanitized_text, pii_redacted_flag, injection_detected_flag)
        """
        if not self.enabled:
            return text, False, False

        sanitized = text
        pii_found = False

        # 1. Redact PII
        for pii_type, pattern in PII_PATTERNS.items():
            if pattern.search(sanitized):
                pii_found = True
                sanitized = pattern.sub(f"[REDACTED_{pii_type}]", sanitized)

        # 2. Check for Prompt Injection
        lower_text = text.lower()
        injection_found = any(keyword in lower_text for keyword in INJECTION_KEYWORDS)

        if injection_found:
            logger.warning("Prompt injection pattern detected in input query")

        return sanitized, pii_found, injection_found


# =========================================================================
# ADK Guardrail Callbacks (Secret Interception & Guided Error Recovery)
# =========================================================================

def secret_detector_callback(tool: Any, args: Dict[str, Any], tool_context: Any = None) -> None:
    """
    Guardrail callback inspecting tool inputs and query arguments for hardcoded API keys or secrets.
    Raises ValueError to block execution if credentials are discovered.
    """
    payload_str = str(args)
    for pattern, secret_type in SECRET_PATTERNS:
        if pattern.search(payload_str):
            logger.warning(f"Guardrail Triggered: Hardcoded {secret_type} found in tool payload.")
            raise ValueError(
                f"Guardrail Violation: Potential {secret_type} detected. "
                "Hardcoded credentials must never be passed to tools or committed to repositories. "
                "Please configure runtime authentication via GCP Secret Manager or environment variables."
            )


def tool_error_recovery_callback(tool: Any, args: Dict[str, Any], tool_context: Any = None, error: Exception = None) -> Dict[str, Any]:
    """
    Guided Error Recovery Callback: Formats tool exceptions into structured recovery
    instructions that guide the LLM back on track.
    """
    tool_name = getattr(tool, "name", str(tool))
    logger.error(f"Tool '{tool_name}' failed with error: {error}")

    if isinstance(error, ValueError) and "Guardrail Violation" in str(error):
        return {
            "error": f"Tool Execution Blocked by Security Policy:\n{str(error)}\n",
            "action_required": "Omit raw credentials and use managed runtime identity."
        }

    return {
        "error": f"Tool '{tool_name}' execution encountered an error.",
        "exception_type": type(error).__name__,
        "details": str(error),
        "recovery_tip": (
            "Please check the search query parameters and ensure valid medical entities are provided. "
            "If searching for rare conditions, consider broadening clinical keywords."
        )
    }


guardrail_service = ModelArmorGuardrail(enabled=settings.model_armor_enabled)
