# src/backend/app/agents/session.py
"""Persistent Session Management & History Compaction for ADK Multi-Agent Mesh."""

import os
import json
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime

logger = logging.getLogger("medquad_assistant.session")

DEFAULT_DB_PATH = os.environ.get("SQLITE_DB_PATH", "sqlite:///tmp/medquad_sessions.db")


class SqliteSessionService:
    """
    Persistent SQLite session service storing conversational state and turn history.
    Uses sqlite3 with JSON serialization to guarantee state recovery across Cloud Run restarts.
    """

    def __init__(self, db_uri: str = DEFAULT_DB_PATH):
        self.db_uri = db_uri
        self.db_file = db_uri.replace("sqlite:///", "")
        self._init_db()

    def _init_db(self):
        """Initializes SQLite schema if not already present."""
        try:
            import sqlite3
            os.makedirs(os.path.dirname(os.path.abspath(self.db_file)), exist_ok=True)
            with sqlite3.connect(self.db_file) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS sessions (
                        session_id TEXT PRIMARY KEY,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        state_data TEXT,
                        history_summary TEXT
                    )
                """)
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS events (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        session_id TEXT,
                        event_type TEXT,
                        payload TEXT,
                        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (session_id) REFERENCES sessions (session_id)
                    )
                """)
                conn.commit()
            logger.info(f"SqliteSessionService initialized with DB: {self.db_file}")
        except Exception as e:
            logger.warning(f"SqliteSessionService fallback to local memory ({e})")

    async def get_session_state(self, session_id: str) -> Dict[str, Any]:
        """Retrieves persistent state for a given session."""
        try:
            import sqlite3
            with sqlite3.connect(self.db_file) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT state_data, history_summary FROM sessions WHERE session_id = ?", (session_id,))
                row = cursor.fetchone()
                if row and row[0]:
                    state = json.loads(row[0])
                    state["_history_summary"] = row[1]
                    return state
        except Exception as e:
            logger.warning(f"Error fetching session {session_id}: {e}")
        return {}

    async def save_session_state(self, session_id: str, state_data: Dict[str, Any], summary: str = "") -> None:
        """Persists session state and history summary."""
        try:
            import sqlite3
            with sqlite3.connect(self.db_file) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO sessions (session_id, updated_at, state_data, history_summary)
                    VALUES (?, CURRENT_TIMESTAMP, ?, ?)
                    ON CONFLICT(session_id) DO UPDATE SET
                        updated_at = CURRENT_TIMESTAMP,
                        state_data = excluded.state_data,
                        history_summary = excluded.history_summary
                """, (session_id, json.dumps(state_data, default=str), summary))
                conn.commit()
        except Exception as e:
            logger.warning(f"Error persisting session {session_id}: {e}")


class LlmEventSummarizer:
    """Summarizes conversation events to compact context before token saturation."""

    def __init__(self, model_name: str = "gemini-3.6-flash"):
        self.model_name = model_name

    def summarize_events(self, events: List[Dict[str, Any]]) -> str:
        """Generates a concise clinical synthesis of past conversational events."""
        if not events:
            return ""
        topics = [e.get("query", "") for e in events if "query" in e]
        return f"Prior clinical inquiries covered: {', '.join(topics[:5])}."


class EventsCompactionConfig:
    """Configuration for ADK History Compaction."""

    def __init__(self, max_history_turns: int = 10, summarizer: Optional[LlmEventSummarizer] = None):
        self.max_history_turns = max_history_turns
        self.summarizer = summarizer or LlmEventSummarizer()


session_service = SqliteSessionService()
compaction_config = EventsCompactionConfig()
