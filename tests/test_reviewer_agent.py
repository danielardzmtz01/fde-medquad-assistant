# tests/test_reviewer_agent.py
"""Unit tests for ReviewerAgent."""

import pytest
from app.agents.reviewer import ReviewerAgent


@pytest.mark.asyncio
async def test_reviewer_agent_validation(sample_agent_state):
    """Validates that ReviewerAgent validates factuality and citation alignment."""
    sample_agent_state.draft_response = (
        "Stage II Hodgkin Lymphoma involves two or more lymph node regions on the same side of the diaphragm [1]."
    )

    agent = ReviewerAgent()
    updated_state = await agent.execute(sample_agent_state)

    assert updated_state.validated_response != ""
    assert updated_state.hallucination_detected is False
    assert "GROUNDING" in updated_state.reviewer_feedback or "VERIFIED" in updated_state.reviewer_feedback
