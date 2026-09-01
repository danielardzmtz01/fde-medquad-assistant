# src/backend/app/safety/safe_refusal.py
"""Deterministic Scope Lock Engine for non-diagnostic clinical safety."""

import re
from typing import Tuple

SAFE_REFUSAL_MESSAGE = (
    "**Notice: Medical Research & Information Scope**\n\n"
    "This system is designed exclusively for clinical research, biomedical literature analysis, "
    "and informational queries using authorized NIH datasets. It cannot provide personal medical diagnoses, "
    "individualized treatment plans, or prescription recommendations.\n\n"
    "If you are experiencing medical symptoms or have health concerns, please consult a licensed healthcare professional "
    "or contact emergency medical services immediately."
)

# Diagnostic & Prescriptive Intent Patterns (regex triggers for immediate refusal)
DIAGNOSTIC_PATTERNS = [
    r"\b(do i have|could i have|am i suffering from|diagnose me)\b",
    r"\b(my symptoms are|i feel|i have been having)\b.*\b(what disease|what condition|do i have)\b",
    r"\b(should i take|can i take|how much|what dosage of)\b.*\b(mg|pills|prescribe|aspirin|ibuprofen|antibiotic|chemo)\b",
    r"\b(what should i do for my|treat my|cure my)\b",
    r"\b(prescribe|give me a prescription for)\b",
]

COMPILED_DIAGNOSTIC_PATTERNS = [re.compile(p, re.IGNORECASE) for p in DIAGNOSTIC_PATTERNS]


def evaluate_scope_lock(query: str) -> Tuple[bool, str]:
    """
    Evaluates whether a query violates the non-diagnostic scope lock.
    
    Returns:
        (is_refused: bool, refusal_reason_or_empty: str)
    """
    cleaned_query = query.strip()

    for pattern in COMPILED_DIAGNOSTIC_PATTERNS:
        if pattern.search(cleaned_query):
            return True, "DIAGNOSTIC_OR_PRESCRIPTIVE_INTENT_DETECTED"

    return False, ""
