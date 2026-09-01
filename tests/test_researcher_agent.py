# tests/test_researcher_agent.py
"""Unit tests for ResearcherAgent."""

import pytest
from app.agents.researcher import ResearcherAgent
from app.models.clinical_types import AgentState


@pytest.mark.asyncio
async def test_researcher_agent_execution(sample_agent_state):
    """Validates that ResearcherAgent fetches grounded chunks and synthesizes citations."""
    agent = ResearcherAgent()
    updated_state = await agent.execute(sample_agent_state)

    assert len(updated_state.retrieved_chunks) > 0
    assert len(updated_state.citations) > 0
    assert "[1]" in updated_state.draft_response
    assert updated_state.prompt_tokens > 0
    assert updated_state.completion_tokens > 0
