# src/backend/app/models/clinical_types.py
"""Internal domain data types for agent state, chunks, and citations."""

from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any


@dataclass
class ContextChunk:
    """A single medical literature chunk retrieved from Vertex AI Search."""

    chunk_id: str
    title: str
    content: str
    source_uri: str
    relevance_score: float
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class AgentState:
    """Shared state passed between ADK RootOrchestrator and Subagents."""

    query: str
    session_id: Optional[str] = None
    domain: str = "general"
    trace_id: str = ""
    is_safe: bool = True
    scope_lock_triggered: bool = False
    retrieved_chunks: List[ContextChunk] = field(default_factory=list)
    draft_response: str = ""
    validated_response: str = ""
    reviewer_feedback: str = ""
    hallucination_detected: bool = False
    citations: List[Dict[str, Any]] = field(default_factory=list)
    prompt_tokens: int = 0
    completion_tokens: int = 0
    cached_tokens: int = 0
    total_latency_ms: float = 0.0
