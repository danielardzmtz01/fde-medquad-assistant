# tests/conftest.py
"""Pytest fixtures and test environment configuration."""

import pytest
import sys
from pathlib import Path

# Ensure src/backend is on sys.path
backend_path = Path(__file__).resolve().parent.parent / "src" / "backend"
if str(backend_path) not in sys.path:
    sys.path.insert(0, str(backend_path))

from app.models.clinical_types import ContextChunk, AgentState


@pytest.fixture
def sample_clinical_chunks():
    """Returns sample grounded NIH clinical literature chunks."""
    return [
        ContextChunk(
            chunk_id="chunk-1",
            title="Hodgkin Lymphoma: Diagnosis, Symptoms, and Staging",
            content=(
                "Stage II Hodgkin Lymphoma is characterized by the involvement of two or more lymph node regions "
                "on the same side of the diaphragm. Common symptoms include painless lymphadenopathy and B symptoms."
            ),
            source_uri="https://medlineplus.gov/hodgkinlymphoma.html",
            relevance_score=0.95,
        ),
        ContextChunk(
            chunk_id="chunk-2",
            title="Treatment Regimens for Hodgkin Lymphoma",
            content=(
                "Standard first-line therapy includes chemotherapy regimens such as ABVD or escalated BEACOPP."
            ),
            source_uri="https://www.cancer.gov/types/lymphoma/patient/adult-hodgkin-treatment-pdq",
            relevance_score=0.88,
        ),
    ]


@pytest.fixture
def sample_agent_state(sample_clinical_chunks):
    """Returns an initialized AgentState object."""
    return AgentState(
        query="What are the diagnostic criteria for Stage II Hodgkin Lymphoma?",
        session_id="test-session-123",
        domain="oncology",
        trace_id="test-trace-abc-123",
        retrieved_chunks=sample_clinical_chunks,
    )
