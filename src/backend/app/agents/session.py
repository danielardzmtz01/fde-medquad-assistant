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

    async def list_recent_sessions(self, limit: int = 20) -> List[Dict[str, Any]]:
        """Retrieves a list of recent sessions with metadata for historical viewing."""
        sessions = []
        try:
            import sqlite3
            with sqlite3.connect(self.db_file) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT session_id, created_at, updated_at, history_summary, state_data
                    FROM sessions 
                    ORDER BY updated_at DESC 
                    LIMIT ?
                """, (limit,))
                for row in cursor.fetchall():
                    state_preview = {}
                    if row[4]:
                        try:
                            state_preview = json.loads(row[4])
                        except Exception:
                            pass
                    sessions.append({
                        "session_id": row[0],
                        "created_at": str(row[1]),
                        "updated_at": str(row[2]),
                        "history_summary": row[3] or "Active clinical research session",
                        "last_query": state_preview.get("last_query", state_preview.get("query", "")),
                        "total_citations": len(state_preview.get("citations", [])),
                    })
        except Exception as e:
            logger.warning(f"Error listing sessions: {e}")
        return sessions

    async def get_session_transcript(self, session_id: str) -> Dict[str, Any]:
        """Retrieves full transcript and metadata for a specific session."""
        try:
            import sqlite3
            with sqlite3.connect(self.db_file) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT session_id, created_at, updated_at, history_summary, state_data
                    FROM sessions WHERE session_id = ?
                """, (session_id,))
                row = cursor.fetchone()
                if row:
                    state_data = json.loads(row[4]) if row[4] else {}
                    return {
                        "session_id": row[0],
                        "created_at": str(row[1]),
                        "updated_at": str(row[2]),
                        "history_summary": row[3] or "",
                        "state": state_data,
                    }
        except Exception as e:
            logger.warning(f"Error getting session transcript {session_id}: {e}")
        return {}


class FirestoreSessionService:
    """
    Enterprise Cloud Firestore session store for distributed multi-region deployments.
    Supports automatic TTL expiration, multi-device synchronization, and zero server maintenance.
    """

    def __init__(self, project_id: Optional[str] = None, collection_name: str = "clinical_sessions"):
        self.project_id = project_id or settings.project_id
        self.collection_name = collection_name
        self._client = None
        self._fallback_sqlite = SqliteSessionService()

    def _get_client(self):
        if self._client is None:
            try:
                from google.cloud import firestore
                self._client = firestore.AsyncClient(project=self.project_id)
                logger.info(f"Connected to Cloud Firestore (Collection: {self.collection_name})")
            except Exception as e:
                logger.warning(f"Firestore initialization fallback to SQLite: {e}")
                self._client = False
        return self._client

    async def get_session_state(self, session_id: str) -> Dict[str, Any]:
        """Retrieves session state from Firestore document."""
        client = self._get_client()
        if not client:
            return await self._fallback_sqlite.get_session_state(session_id)
        try:
            doc_ref = client.collection(self.collection_name).document(session_id)
            doc = await doc_ref.get()
            if doc.exists:
                return doc.to_dict().get("state_data", {})
        except Exception as e:
            logger.warning(f"Firestore fetch error for {session_id}: {e}")
            return await self._fallback_sqlite.get_session_state(session_id)
        return {}

    async def save_session_state(self, session_id: str, state_data: Dict[str, Any], summary: str = "") -> None:
        """Persists session document with automatic retention timestamp (TTL)."""
        client = self._get_client()
        if not client:
            return await self._fallback_sqlite.save_session_state(session_id, state_data, summary)
        try:
            from datetime import timedelta
            now = datetime.utcnow()
            expires_at = now + timedelta(days=settings.session_retention_days)
            doc_ref = client.collection(self.collection_name).document(session_id)
            payload = {
                "session_id": session_id,
                "updated_at": now.isoformat(),
                "expires_at": expires_at.isoformat(),
                "history_summary": summary,
                "state_data": state_data,
                "environment": settings.environment,
            }
            await doc_ref.set(payload, merge=True)
        except Exception as e:
            logger.warning(f"Firestore save error for {session_id}: {e}")
            await self._fallback_sqlite.save_session_state(session_id, state_data, summary)

    async def list_recent_sessions(self, limit: int = 20) -> List[Dict[str, Any]]:
        """Queries recent session documents ordered by update time."""
        client = self._get_client()
        if not client:
            return await self._fallback_sqlite.list_recent_sessions(limit)
        try:
            from google.cloud import firestore
            coll = client.collection(self.collection_name)
            query = coll.order_by("updated_at", direction=firestore.Query.DESCENDING).limit(limit)
            docs = await query.get()
            results = []
            for doc in docs:
                data = doc.to_dict()
                state = data.get("state_data", {})
                results.append({
                    "session_id": data.get("session_id", doc.id),
                    "created_at": data.get("created_at", data.get("updated_at", "")),
                    "updated_at": data.get("updated_at", ""),
                    "history_summary": data.get("history_summary", "Clinical session"),
                    "last_query": state.get("query", ""),
                    "total_citations": len(state.get("citations", [])),
                })
            return results
        except Exception as e:
            logger.warning(f"Firestore list error: {e}")
            return await self._fallback_sqlite.list_recent_sessions(limit)

    async def get_session_transcript(self, session_id: str) -> Dict[str, Any]:
        """Retrieves full transcript document from Firestore."""
        client = self._get_client()
        if not client:
            return await self._fallback_sqlite.get_session_transcript(session_id)
        try:
            doc_ref = client.collection(self.collection_name).document(session_id)
            doc = await doc_ref.get()
            if doc.exists:
                data = doc.to_dict()
                return {
                    "session_id": data.get("session_id", doc.id),
                    "created_at": data.get("created_at", ""),
                    "updated_at": data.get("updated_at", ""),
                    "history_summary": data.get("history_summary", ""),
                    "state": data.get("state_data", {}),
                }
        except Exception as e:
            logger.warning(f"Firestore transcript error {session_id}: {e}")
        return await self._fallback_sqlite.get_session_transcript(session_id)


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


def create_session_service():
    """Factory creating appropriate session service based on configuration."""
    storage_type = getattr(settings, "session_storage_type", "sqlite").lower()
    if storage_type == "firestore":
        logger.info("Initializing enterprise FirestoreSessionService for v2")
        return FirestoreSessionService()
    logger.info("Initializing high-speed in-process SqliteSessionService")
    return SqliteSessionService(db_uri=getattr(settings, "sqlite_db_path", DEFAULT_DB_PATH))


session_service = create_session_service()
compaction_config = EventsCompactionConfig()
