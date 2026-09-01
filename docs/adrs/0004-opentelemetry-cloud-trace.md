# ADR 0004: Enterprise Observability with OpenTelemetry and Google Cloud Trace

## Status
Accepted

## Context
High-reliability clinical AI systems require full execution traceability, performance metrics, and cost monitoring across microservices, subagents, vector search queries, and LLM calls.

## Decision
We implement OpenTelemetry (OTEL) SDK integrated with Google Cloud Trace and BigQuery:
1. **Distributed Tracing**: The FastAPI application automatically injects and extracts W3C `traceparent` headers, recording spans for HTTP requests, agent decisions, search calls, and LLM inference.
2. **Telemetry Materialization in BigQuery**: Token usage (input, output, cached tokens), execution latency, model versions, and quality scores are asynchronously exported to BigQuery for analytical querying and Looker dashboarding.
3. **Structured Logging**: Application logs use JSON format with embedded `logging.googleapis.com/trace` metadata for 1:1 log-to-trace correlation in Cloud Logging.

## Consequences
- **Positive**: Complete auditability of every AI decision, deep performance visibility, and exact financial accounting of token costs.
- **Trade-offs**: Minimal latency overhead (<5ms) for asynchronous trace export.
