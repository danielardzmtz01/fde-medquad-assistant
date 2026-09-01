# src/backend/app/telemetry/bq_logger.py
"""Asynchronous BigQuery exporter for token usage, latency, and audit logs."""

import logging
from datetime import datetime
from typing import Dict, Any, Optional
from app.config import settings

logger = logging.getLogger(__name__)


class BigQueryTelemetryLogger:
    """Asynchronously logs token metrics and evaluation events to BigQuery."""

    def __init__(self):
        self.project_id = settings.project_id
        self.dataset_id = settings.bq_dataset_id
        self.client = None

    async def log_token_usage(
        self,
        trace_id: str,
        agent_name: str,
        model_name: str,
        input_tokens: int,
        output_tokens: int,
        cached_tokens: int,
        estimated_cost_usd: float,
        latency_ms: float,
        status: str,
        session_id: Optional[str] = None,
    ):
        """Streams a token usage event row into the BigQuery token_usage_events table."""
        row = {
            "timestamp": datetime.utcnow().isoformat(),
            "trace_id": trace_id,
            "session_id": session_id or "",
            "agent_name": agent_name,
            "model_name": model_name,
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "cached_tokens": cached_tokens,
            "estimated_cost_usd": estimated_cost_usd,
            "latency_ms": latency_ms,
            "status": status,
        }

        try:
            from google.cloud import bigquery
            if not self.client:
                self.client = bigquery.Client(project=self.project_id)
            table_ref = f"{self.project_id}.{self.dataset_id}.token_usage_events"
            errors = self.client.insert_rows_json(table_ref, [row])
            if errors:
                logger.warning(f"BigQuery streaming insert returned errors: {errors}")
        except Exception as e:
            logger.debug(f"BigQuery streaming log mocked / skipped: {e}")


bq_logger = BigQueryTelemetryLogger()
