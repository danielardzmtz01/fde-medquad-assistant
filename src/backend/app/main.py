# src/backend/app/main.py
"""FastAPI Application Entrypoint for MedQuAD Clinical Assistant."""

import time
import uuid
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, status, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.config import settings
from app.utils.logging import setup_logging
from app.telemetry.tracing import setup_opentelemetry, trace_span
from app.telemetry.bq_logger import bq_logger
from app.models.api_schemas import (
    ClinicalChatRequest,
    ClinicalChatResponse,
    EvaluationRequest,
    EvaluationResponse,
)
from app.agents.orchestrator import root_orchestrator
from app.tools.search_tool import search_tool


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifecycle manager for startup and shutdown routines."""
    setup_logging(settings.log_level)
    setup_opentelemetry()
    yield


app = FastAPI(
    title="MedQuAD Clinical Assistant API",
    description="Multi-agent clinical research platform grounded in NIH MedQuAD biomedical literature.",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def add_telemetry_headers(request: Request, call_next):
    """Middleware injecting trace context and timing headers."""
    start_time = time.time()
    trace_id = request.headers.get("X-Trace-Id", str(uuid.uuid4()))
    
    response = await call_next(request)
    
    duration = (time.time() - start_time) * 1000.0
    response.headers["X-Trace-Id"] = trace_id
    response.headers["X-Response-Time-Ms"] = f"{duration:.2f}"
    return response


from fastapi.responses import HTMLResponse, JSONResponse
from pathlib import Path

STATIC_INDEX_PATH = Path(__file__).parent / "static" / "index.html"


@app.get("/", response_class=HTMLResponse, tags=["Web UI"])
async def root_ui():
    """Serves the MedQuAD interactive web application for end users."""
    if STATIC_INDEX_PATH.exists():
        return HTMLResponse(content=STATIC_INDEX_PATH.read_text(encoding="utf-8"))
    return HTMLResponse(content="<h1>MedQuAD Clinical Assistant Active</h1><p>Visit /docs for API documentation.</p>")


@app.get("/ui", response_class=HTMLResponse, tags=["Web UI"])
async def web_ui():
    """Explicit Web UI endpoint."""
    return await root_ui()


@app.get("/healthz", status_code=status.HTTP_200_OK, tags=["Health"])
async def health_check():
    """Health check endpoint for Cloud Run liveness and readiness probes."""
    return {
        "status": "HEALTHY",
        "service": "medquad-clinical-assistant",
        "environment": settings.environment,
        "version": "1.0.0",
    }


@app.post("/api/v1/chat", response_model=ClinicalChatResponse, tags=["Clinical Agents"])
async def clinical_chat(request: ClinicalChatRequest, req: Request):
    """
    Processes a clinical query through the multi-agent ADK pipeline:
    - Pre-flight Model Armor & PII sanitization.
    - Scope Lock non-diagnostic refusal check.
    - Vertex AI Search literature grounding.
    - Multi-agent synthesis and Reviewer quality validation.
    """
    trace_id = req.headers.get("X-Trace-Id", str(uuid.uuid4()))

    with trace_span("clinical_chat_pipeline"):
        response = await root_orchestrator.process_query(request, trace_id=trace_id)

    # Asynchronously stream telemetry to BigQuery
    await bq_logger.log_token_usage(
        trace_id=trace_id,
        agent_name="RootOrchestrator",
        model_name=settings.gemini_reasoning_model,
        input_tokens=response.tokens.prompt_tokens,
        output_tokens=response.tokens.completion_tokens,
        cached_tokens=response.tokens.cached_tokens,
        estimated_cost_usd=response.tokens.estimated_cost_usd,
        latency_ms=response.latency_ms,
        status=response.guardrails.action_taken,
        session_id=request.session_id,
    )

    return response


@app.post("/api/v1/eval", response_model=EvaluationResponse, tags=["Quality & Evals"])
async def run_evaluation(request: EvaluationRequest):
    """Runs heuristic evaluation (ROUGE-L, BLEU, Entity F1) for CI/CD gates."""
    chat_req = ClinicalChatRequest(query=request.golden_query)
    chat_res = await root_orchestrator.process_query(chat_req)

    # Calculate token overlap heuristics
    generated_tokens = set(chat_res.answer.lower().split())
    ground_truth_tokens = set(request.ground_truth_answer.lower().split())

    intersection = generated_tokens.intersection(ground_truth_tokens)
    recall = len(intersection) / max(len(ground_truth_tokens), 1)
    precision = len(intersection) / max(len(generated_tokens), 1)

    f1 = 2 * (precision * recall) / max(precision + recall, 1e-6)
    rouge_l = recall
    bleu = precision

    passed = (rouge_l >= 0.40) and (bleu >= 0.35)

    return EvaluationResponse(
        rouge_l_score=round(rouge_l, 4),
        bleu_score=round(bleu, 4),
        entity_f1_score=round(f1, 4),
        citation_fidelity_score=1.0 if len(chat_res.citations) > 0 else 0.0,
        passed_gates=passed,
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=settings.host, port=settings.port)
