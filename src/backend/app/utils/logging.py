# src/backend/app/utils/logging.py
"""Structured JSON logging configuration for Google Cloud Logging."""

import json
import logging
import sys
from datetime import datetime


class JSONFormatter(logging.Formatter):
    """Formats log records as structured JSON compatible with Google Cloud Logging."""

    def format(self, record: logging.LogRecord) -> str:
        log_entry = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "severity": record.levelname,
            "message": record.getMessage(),
            "logger": record.name,
            "module": record.module,
            "lineno": record.lineno,
        }

        # Embed trace context if present
        trace_id = getattr(record, "trace_id", None)
        if trace_id:
            log_entry["logging.googleapis.com/trace"] = trace_id

        if record.exc_info:
            log_entry["exception"] = self.formatException(record.exc_info)

        return json.dumps(log_entry)


def setup_logging(log_level: str = "INFO"):
    """Configures structured JSON logging for stdout."""
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(JSONFormatter())
    logging.root.setLevel(getattr(logging, log_level.upper(), logging.INFO))
    logging.root.handlers = [handler]
