# tests/test_api_endpoints.py
"""Integration tests for FastAPI REST API endpoints."""

import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app


@pytest.mark.asyncio
async def test_health_check_endpoint():
    """Validates the /healthz probe endpoint."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.get("/healthz")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "HEALTHY"
        assert data["service"] == "medquad-clinical-assistant"


@pytest.mark.asyncio
async def test_chat_endpoint_valid_payload():
    """Validates the POST /api/v1/chat endpoint with a clinical query."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        payload = {
            "query": "What are the diagnostic markers for Stage II Hodgkin Lymphoma?",
            "clinical_domain": "oncology",
        }
        response = await ac.post("/api/v1/chat", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert "answer" in data
        assert len(data["citations"]) > 0
        assert data["guardrails"]["passed"] is True
        assert data["tokens"]["prompt_tokens"] > 0
        assert "X-Trace-Id" in response.headers


@pytest.mark.asyncio
async def test_eval_endpoint():
    """Validates the POST /api/v1/eval endpoint."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        payload = {
            "golden_query": "What is Stage II Hodgkin Lymphoma?",
            "ground_truth_answer": "Stage II Hodgkin Lymphoma involves lymph node regions on the same side of diaphragm.",
        }
        response = await ac.post("/api/v1/eval", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert "rouge_l_score" in data
        assert "bleu_score" in data
        assert data["passed_gates"] is True
