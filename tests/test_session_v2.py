# tests/test_session_v2.py
"""Unit tests for v2 persistent session history and long-term archiving."""

import pytest
import os
from httpx import AsyncClient, ASGITransport
from app.main import app
from app.agents.session import SqliteSessionService, FirestoreSessionService, create_session_service


@pytest.mark.asyncio
async def test_sqlite_session_lifecycle(tmp_path):
    """Tests session creation, update, listing, and transcript retrieval in SQLite."""
    db_file = tmp_path / "test_sessions.db"
    service = SqliteSessionService(db_uri=f"sqlite:///{db_file}")

    # 1. Save session
    session_id = "test-session-001"
    state_data = {
        "query": "What are the side effects of Metformin?",
        "citations": [{"citation_id": "[1]", "title": "NIH Drug Info"}],
        "prompt_tokens": 120,
        "completion_tokens": 45,
        "cached_tokens": 0,
    }
    await service.save_session_state(session_id, state_data, summary="Metformin side effects inquiry")

    # 2. Retrieve session state
    retrieved = await service.get_session_state(session_id)
    assert retrieved["query"] == "What are the side effects of Metformin?"
    assert retrieved["_history_summary"] == "Metformin side effects inquiry"

    # 3. List recent sessions
    sessions = await service.list_recent_sessions(limit=10)
    assert len(sessions) >= 1
    assert sessions[0]["session_id"] == session_id
    assert sessions[0]["total_citations"] == 1

    # 4. Get transcript
    transcript = await service.get_session_transcript(session_id)
    assert transcript["session_id"] == session_id
    assert transcript["state"]["query"] == "What are the side effects of Metformin?"


@pytest.mark.asyncio
async def test_firestore_session_service_graceful_fallback(tmp_path):
    """Tests that FirestoreSessionService falls back gracefully when not in GCP environment."""
    firestore_svc = FirestoreSessionService(project_id="test-project", collection_name="test_clinical_sessions")
    
    session_id = "test-session-firestore-002"
    state_data = {"query": "Hodgkin Lymphoma protocols", "citations": []}

    # Should fall back to SQLite without raising exceptions
    await firestore_svc.save_session_state(session_id, state_data, summary="Hodgkin investigation")
    retrieved = await firestore_svc.get_session_state(session_id)
    assert retrieved.get("query") == "Hodgkin Lymphoma protocols"

    sessions = await firestore_svc.list_recent_sessions(limit=5)
    assert any(s["session_id"] == session_id for s in sessions)


@pytest.mark.asyncio
async def test_api_session_endpoints():
    """Tests REST endpoints GET /api/v1/sessions and GET /api/v1/sessions/{id}."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        # 1. Trigger a chat to create a session
        chat_res = await ac.post("/api/v1/chat", json={
            "query": "What is Hodgkin Lymphoma?",
            "session_id": "api-test-session-999"
        })
        assert chat_res.status_code == 200

        # 2. List sessions
        list_res = await ac.get("/api/v1/sessions")
        assert list_res.status_code == 200
        data = list_res.json()
        assert "sessions" in data
        assert data["total_sessions"] >= 1

        # 3. Fetch specific session
        session_res = await ac.get("/api/v1/sessions/api-test-session-999")
        assert session_res.status_code == 200
        session_data = session_res.json()
        assert session_data["session_id"] == "api-test-session-999"

        # 4. Archive session to BigQuery
        archive_res = await ac.post("/api/v1/sessions/api-test-session-999/archive")
        assert archive_res.status_code == 200
        archive_data = archive_res.json()
        assert archive_data["status"] == "ARCHIVED"
        assert archive_data["session_id"] == "api-test-session-999"
