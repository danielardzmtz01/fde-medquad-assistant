# src/backend/app/telemetry/tracing.py
"""OpenTelemetry integration with Google Cloud Trace."""

import logging
from contextlib import contextmanager
from app.config import settings

logger = logging.getLogger(__name__)

# Tracer initialization
_tracer = None


def setup_opentelemetry():
    """Initializes OpenTelemetry TracerProvider with CloudTraceSpanExporter when available."""
    global _tracer
    if not settings.otel_enabled:
        logger.info("OpenTelemetry is disabled in settings.")
        return

    try:
        from opentelemetry import trace
        from opentelemetry.sdk.trace import TracerProvider
        from opentelemetry.sdk.trace.export import BatchSpanProcessor
        from opentelemetry.exporter.cloud_trace import CloudTraceSpanExporter

        provider = TracerProvider()
        cloud_trace_exporter = CloudTraceSpanExporter(project_id=settings.project_id)
        provider.add_span_processor(BatchSpanProcessor(cloud_trace_exporter))
        trace.set_tracer_provider(provider)
        _tracer = trace.get_tracer(settings.otel_service_name)
        logger.info("OpenTelemetry Google Cloud Trace exporter initialized successfully.")
    except Exception as e:
        logger.warning(f"OpenTelemetry Cloud Trace exporter setup skipped/mocked ({e})")


def get_tracer():
    """Returns the active tracer instance."""
    global _tracer
    if _tracer is None:
        try:
            from opentelemetry import trace
            _tracer = trace.get_tracer(settings.otel_service_name)
        except Exception:
            _tracer = None
    return _tracer


@contextmanager
def trace_span(name: str):
    """Context manager for tracing execution spans."""
    tracer = get_tracer()
    if tracer:
        with tracer.start_as_current_span(name) as span:
            yield span
    else:
        yield None
