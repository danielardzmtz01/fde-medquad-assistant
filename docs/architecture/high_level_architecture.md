# High-Level Architecture (HLA) — MedQuAD Clinical Assistant

## 1. Executive Summary

**MedQuAD Clinical Assistant** is an enterprise-grade multi-agent clinical research platform engineered for Google Cloud Platform (GCP). It enables medical researchers and clinicians to query authoritative NIH literature rapidly and safely, guaranteeing zero-hallucination policies, non-diagnostic guardrails, least-privilege IAM security, and comprehensive observability.

```mermaid
flowchart TB
    subgraph ClientLayer ["Client & Ingress Layer"]
        User["Clinician / Medical Researcher"]
        UI["React 18 + TypeScript + Tailwind UI<br/>(Split-Pane Citation Viewer)"]
        IAP["Google Cloud Identity-Aware Proxy (IAP)"]
    end

    subgraph ServiceLayer ["API Gateway & Compute (Google Cloud Run)"]
        FastAPI["FastAPI Async Backend<br/>(Python 3.11)"]
        Guard["Safety & Guardrails Layer<br/>• GCP Model Armor (PII & Injection)<br/>• Scope Lock Engine (Safe Refusal)"]
    end

    subgraph AgentLayer ["ADK Multi-Agent Mesh"]
        Root["Root Orchestrator Agent<br/>(Intent Routing & Synthesis)"]
        Researcher["Researcher Agent<br/>(NIH MedQuAD Literature Search)"]
        Reviewer["Reviewer Agent<br/>(Clinical Factuality & Grounding Validation)"]
    end

    subgraph GroundingLayer ["Managed Intelligence & Grounding"]
        VAIS["Vertex AI Search (GEAP)<br/>(MedQuAD Grounding Engine)"]
        GCS["Google Cloud Storage<br/>(Raw NIH XML/JSON Corpus)"]
        GeminiFlash["Gemini 2.5 Flash<br/>(Routing & Reviewer)"]
        GeminiPro["Gemini 2.5 Pro<br/>(Deep Clinical Reasoning)"]
    end

    subgraph SecurityLayer ["Security & Identity"]
        IAM["Granular Service Accounts<br/>(Principle of Least Privilege)"]
        SecMgr["Secret Manager<br/>(API Tokens & Keys)"]
        VPC["Serverless VPC Access<br/>(Secure Private Networking)"]
    end

    subgraph ObservabilityLayer ["Enterprise Observability"]
        OTEL["OpenTelemetry SDK (OTEL)"]
        Trace["Google Cloud Trace<br/>(Distributed Tracing)"]
        Logging["Google Cloud Logging<br/>(Structured JSON Logs)"]
        BQ["BigQuery Telemetry<br/>(Token Usage, Latency, Audit)"]
    end

    %% Flow Connections
    User --> UI
    UI --> IAP
    IAP --> FastAPI
    FastAPI --> Guard
    Guard --> Root
    Root -->|Task Delegation| Researcher
    Researcher -->|Vector Semantic Query| VAIS
    VAIS -.->|Indexed from| GCS
    Researcher -->|Literature Context| GeminiPro
    Researcher -->|Draft Synthesis| Reviewer
    Reviewer -->|Factuality & Citation Check| GeminiFlash
    Reviewer -->|Validated Findings| Root
    Root -->|Final Payload + Citations| FastAPI
    FastAPI -->|Streamed Response| UI

    %% Telemetry Links
    FastAPI -.-> OTEL
    OTEL -.-> Trace
    FastAPI -.-> Logging
    FastAPI -.-> BQ
    FastAPI -.-> SecMgr
    FastAPI -.-> IAM
```

---

## 2. Multi-Agent Orchestration Flow

```mermaid
sequenceDiagram
    autonumber
    actor Clinician as Clinician / Researcher
    participant UI as Web Frontend
    participant API as FastAPI Backend
    participant Guard as Model Armor / Guardrails
    participant Root as Root Orchestrator (ADK)
    participant Res as Researcher Agent
    participant VAIS as Vertex AI Search
    participant Rev as Reviewer Agent
    participant BQ as BigQuery Telemetry

    Clinician->>UI: Submits Query: "What are diagnostic markers of Stage II Hodgkin Lymphoma?"
    UI->>API: POST /api/v1/chat (with JWT / Bearer Token)
    API->>Guard: Pre-execution inspection (PII, Injection, Diagnostic Intent)
    alt Diagnostic or Prescriptive query detected
        Guard-->>API: Safe Refusal Triggered (Scope Lock)
        API-->>UI: Returns standardized non-diagnostic refusal message
    else Valid clinical research query
        Guard->>Root: Sanitized User Query
        Root->>Res: Delegate research task (Topic: Oncology)
        Res->>VAIS: Semantic Search query (MedQuAD NIH corpus)
        VAIS-->>Res: Retrieved NIH Context Chunks with Source URIs
        Res->>Res: Synthesize clinical findings with inline citations [1], [2]
        Res->>Rev: Transfer draft synthesis + retrieved context chunks
        Rev->>Rev: Evaluate Grounding Recall, Factuality & Hallucination score
        Rev-->>Root: Validated clinical response + verified citations metadata
        Root-->>API: Final structured payload + tokens & latency metrics
        API->>BQ: Async export of tokens, latency, trace ID & audit record
        API-->>UI: Streamed response + Split-pane citation metadata
        UI-->>Clinician: Displays answer with clickable NIH references
    end
```

---

## 3. Core Architectural Decisions

1. **Multi-Agent Separation of Concerns**: Instead of a monolithic prompt, the system decouples search, synthesis, and validation into specialized agents orchestrated by Google ADK.
2. **Model Tiering Strategy**: High-frequency routing and review operations execute on **Gemini 2.5 Flash** (<400ms latency, 10x lower cost), while intensive medical synthesis runs on **Gemini 2.5 Pro**.
3. **Defense-in-Depth AI Safety**: Model Armor intercepts adversarial prompts and redacts PII before model calls, while a deterministic Scope Lock engine guarantees that the assistant never offers medical diagnoses or treatment prescriptions.
4. **End-to-End Observability**: Standardized OpenTelemetry tracing correlates HTTP requests, agent spans, tool calls, and model invocations into Google Cloud Trace, with granular token usage materializing in BigQuery for Looker financial reporting.
