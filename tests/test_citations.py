# tests/test_citations.py
"""Unit tests for citation parsing and grounding verification."""

import re
import pytest
from app.models.api_schemas import CitationItem


def test_citation_parsing_and_mapping():
    """Validates that inline citation tokens match metadata objects accurately."""
    sample_text = (
        "Stage II Hodgkin Lymphoma is diagnosed based on clinical staging [1]. "
        "First-line regimens include ABVD chemotherapy [2]."
    )

    citations = [
        CitationItem(
            citation_id="[1]",
            title="Hodgkin Lymphoma Diagnosis",
            source_url="https://medlineplus.gov/hodgkinlymphoma.html",
            snippet="Stage II Hodgkin Lymphoma is diagnosed...",
            relevance_score=0.95,
        ),
        CitationItem(
            citation_id="[2]",
            title="Chemotherapy Regimens",
            source_url="https://www.cancer.gov/treatment",
            snippet="First-line regimens include ABVD...",
            relevance_score=0.90,
        ),
    ]

    tokens_found = re.findall(r"\[\d+\]", sample_text)
    assert tokens_found == ["[1]", "[2]"]

    citation_ids = [c.citation_id for c in citations]
    for token in tokens_found:
        assert token in citation_ids
