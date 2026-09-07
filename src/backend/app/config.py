# src/backend/app/config.py
"""Application configuration using Pydantic Settings."""

import os
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Global configuration settings loaded from environment variables."""

    # Project & Environment
    project_id: str = "fde-medquad-sandbox-dev"
    environment: str = "dev"
    location: str = "us-central1"

    # Vertex AI & Model Settings
    gemini_routing_model: str = "gemini-3.6-flash"
    gemini_reasoning_model: str = "gemini-3.6-pro"
    gemini_eval_model: str = "gemini-3.6-flash"
    vertex_ai_location: str = "us-central1"

    # Vertex AI Search (GEAP)
    data_store_id: str = "medquad-datastore-dev"
    search_engine_id: str = "medquad-search-engine-dev"
    search_max_results: int = 5

    # Storage & Telemetry
    corpus_bucket_name: str = "fde-medquad-sandbox-dev-dev-medquad-corpus"
    bq_dataset_id: str = "medquad_telemetry_dev"

    # AI Safety & Guardrails
    model_armor_enabled: bool = True
    model_armor_template_id: str = "medquad-clinical-safety"
    enforce_scope_lock: bool = True

    # Tracing & Logging
    otel_enabled: bool = True
    otel_service_name: str = "medquad-clinical-assistant"
    log_level: str = "INFO"

    # Session Persistence & History (v2)
    session_storage_type: str = "sqlite"  # Options: "sqlite", "firestore"
    sqlite_db_path: str = "sqlite:///tmp/medquad_sessions.db"
    firestore_collection: str = "clinical_sessions"
    session_retention_days: int = 90

    # Server Settings
    port: int = 8080
    host: str = "0.0.0.0"
    cors_origins: list[str] = ["*"]

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()
