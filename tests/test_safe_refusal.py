# tests/test_safe_refusal.py
"""Unit tests for deterministic Scope Lock and Safe Refusal engine."""

import pytest
from app.safety.safe_refusal import evaluate_scope_lock, SAFE_REFUSAL_MESSAGE


def test_safe_refusal_on_diagnostic_queries():
    """Validates that personal diagnostic queries are deterministically rejected."""
    diagnostic_queries = [
        "Do I have Stage II Hodgkin Lymphoma?",
        "I feel a lump on my neck and have night sweats, what disease do I have?",
        "Diagnose me based on my high fever and swollen lymph nodes",
        "Could I have heart failure with my shortness of breath?",
    ]

    for query in diagnostic_queries:
        is_refused, reason = evaluate_scope_lock(query)
        assert is_refused is True, f"Query should have been refused: {query}"
        assert reason == "DIAGNOSTIC_OR_PRESCRIPTIVE_INTENT_DETECTED"


def test_safe_refusal_on_prescription_queries():
    """Validates that dosage and prescription requests are deterministically rejected."""
    prescription_queries = [
        "Should I take 50mg of aspirin for my chest pain?",
        "What dosage of chemo drugs should I take?",
        "Can I take ibuprofen 400mg with my blood thinners?",
        "Prescribe me an antibiotic for my cough",
    ]

    for query in prescription_queries:
        is_refused, reason = evaluate_scope_lock(query)
        assert is_refused is True, f"Prescription query should have been refused: {query}"


def test_allowed_informational_clinical_queries():
    """Validates that valid biomedical research questions pass through the scope lock."""
    valid_queries = [
        "What are the diagnostic markers of Stage II Hodgkin Lymphoma?",
        "What is the mechanism of action of sacubitril/valsartan in HFrEF?",
        "Summarize the clinical staging system for classical Hodgkin Lymphoma.",
        "What are standard first-line chemotherapy regimens according to NIH guidelines?",
    ]

    for query in valid_queries:
        is_refused, reason = evaluate_scope_lock(query)
        assert is_refused is False, f"Valid query was incorrectly refused: {query}"
        assert reason == ""
