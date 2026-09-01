# Technical Design Document

## FDE Technical Design Document

### Project Name: MedQuAD Clinical Assistant

**FDE Lead(s):** Daniela Rodriguez Martinez (`danielardzmtz@`) (Primary)  
**Last Updated:** August 26, 2026  
**Status:** Approved & Verified in DEV  
**Deployment Region:** `us-central1`  
**GCP Environment:** `drm-medquad-admin-central`, `drm-medquad-admin-dev`, `drm-medquad-service-dev`  

---

### Executive Summary

Clinicians and medical researchers at academic medical centers and research institutes face significant cognitive load and time constraints when navigating thousands of medical guidelines, disease indicators, clinical trial protocols, and treatment pathways. The **MedQuAD Clinical Assistant** is a high-performance, asynchronous agentic platform designed to automate clinical information retrieval and research synthesis over authoritative National Institutes of Health (NIH) literature.

Overcoming traditional LLM hallucination risks and unauthorized medical advice liabilities, the assistant utilizes a **Supervisor-Worker agentic topology** built on Google's **Agent Development Kit (ADK)** and **Gemini 2.5 Pro / Flash**. It delivers grounded, cited biomedical literature with sub-second retrieval latency, zero ungrounded clinical claims, Model Armor safety guardrails, and deterministic "Scope Lock" non-medical advice boundaries.

#### Core "North Star" Metrics

* **Recall Rate**: $\ge$ 90% relevant clinical information retrieval from the NIH MedQuAD grounding index.
* **Precision Rate**: $\ge$ 88% accurate clinical keyword, symptom, and pharmacological extraction.
* **Safety Compliance**: 100% deterministic enforcement of "Safe Refusal" (Scope Lock) non-diagnostic guardrails with $\le$ 0.1 ms latency and \$0.00 token cost.
* **Response Time**: p95 latency $\le$ 2.5 seconds for complex multi-agent clinical synthesis.
* **Grounding Fidelity**: 100% of claims supported by indexed NIH citations with relevance scores $\ge$ 0.85.

---

### System Architecture

#### High-Level Diagram

```
graph TD
    User([Clinician / Researcher]) -->|1. Natural Language Query| FE[React Frontend - TypeScript/Vite]
    FE -->|2. Asynchronous API Request| BE[FastAPI Backend - Cloud Run]
    
    subgraph Backend [FastAPI Backend - Secure Sandbox]
        BE -->|3. Route & Authenticate| GA[Agent Gateway / AuthN]
        GA -->|4. Sanitize Input| MA[Model Armor & Scope Lock Guardrail]
        MA -->|5. Forward Query| CO[Root Orchestrator Agent - Gemini 2.5 Flash]
        
        CO -->|6a. Delegate Research| RA[Researcher Subagent - Gemini 2.5 Pro]
        CO -->|6b. Delegate Validation| RE[Reviewer Subagent - Gemini 2.5 Flash]

        RA -->|7. Search Tool| VAIS[Vertex AI Search - MedQuAD Index]
        RA -->|8. Fetch Mock Records| MDB[Mock Clinical DB Tool]
    end
    
    MDB -->|Query Simulated Records| CS[Cloud SQL PostgreSQL]
    VAIS -->|Semantic Query| GCS[Google Cloud Storage - MedQuAD Corpus]
    
    BE -->|9. Export Spans/Traces| OTEL[OpenTelemetry / Cloud Trace]
    BE -->|10. Stream Logs/Metrics| BQ[BigQuery Telemetry Sink]
```

#### Architecture Principles

* **Modularity**: High-code, decoupled Supervisor-Worker topology using the Google ADK. Individual agents operate as isolated units, allowing models (Gemini 3.6 Pro vs. Gemini 3.6 Flash) and tools to be swapped seamlessly.
* **Scalability**: Hosted on serverless Google Cloud Run v2 with high concurrency (`max_instance_request_concurrency = 40`) and automated scaling bounds (0 to 3 instances in DEV).
* **Resilience**: Defensive retry policies with exponential backoff and jitter handle rate limits. Standardized fallbacks allow graceful degradation (e.g., reverting to cached clinical summaries upon Search endpoint outages).

#### Technical Components & Agent Logic

* **Agent Development Kit (ADK)**: Orchestrates the central supervisor (`RootOrchestrator`) and specialized workers:
  * **ResearcherAgent**: Owns tool execution, formulating semantic queries against NIH MedQuAD datasets and extracting structured citations.
  * **ReviewerAgent**: Acts as an independent clinical quality controller, scoring responses and checking claim factuality against retrieved chunks before final output.
* **Reasoning Strategy**: Employs a structured ReAct (Reasoning and Action) execution loop. The agent plans its task manifest, executes API tools, reviews intermediate payloads, and loops until the clinical success criteria are met.
* **Context & Memory Strategy**: Utilizes an asynchronous PostgreSQL/Firestore-backed session service. Conversational history and short-term context are managed in active state caches, while long-term session summaries are persisted to prevent token bloat.

#### Tooling & External Integrations

* **Tool Registration**: Tool definitions are registered natively inside the ADK framework using explicit Pydantic type schemas (`ClinicalChatRequest`, `ClinicalChatResponse`, `CitationItem`) to enforce strict parameter bounds.
* **Model Context Protocol (MCP)**:
  * **MCP Servers**: Tool logic is encapsulated in isolated MCP servers hosted on Cloud Run.
  * **Transport**: Standard use of Server-Sent Events (SSE) over secure endpoints to facilitate network-isolated, high-performance tool communication.
  * **Discovery**: Dynamic discovery of schema elements via standard JSON-RPC capabilities exposed by the MCP client.
* **Authentication**: The MCP server retrieves API tokens and credentials at runtime from Google Cloud Secret Manager using its unique service account identity.
* **Function Calling Logic**: Standardized exception wrappers handle HTTP 429 and 500 errors natively with graceful fallback responses.

---

### Infrastructure, Security, & IAM

#### GCP Project Structure

* **Admin Central Project**: `drm-medquad-admin-central` (Houses Artifact Registry, NCC Hub, CI/CD Service Account).
* **Admin Host Project (DEV)**: `drm-medquad-admin-dev` (Houses Shared VPC `10.10.0.0/24`, Serverless VPC Access Connector `10.10.1.0/28`, NCC Spoke).
* **Service Workload Project (DEV)**: `drm-medquad-service-dev` (Houses Cloud Run Backend, Vertex AI Search Datastore, BigQuery Telemetry, GCS Corpus Bucket).
* **Region**: `us-central1` (Core deployment target).
* **Deployment Topology**: Multi-project Hub-and-Spoke Shared VPC managed via modular Terraform repositories.

#### User Authentication (AuthN)

* **Identity Provider**: Single Sign-On (SSO) integrated via Google Workspace Cloud Identity.
* **Access Patterns**: API gateways and Cloud Run endpoints are protected using Identity-Aware Proxy (IAP) and IAM Bearer tokens, requiring authenticated JWT headers on all incoming requests.

#### Authorization (AuthZ)

* **Role-Based Access Control (RBAC)**: Group-based access definitions managed via Cloud Identity Groups.
* **Service Accounts**: The application runs under a custom service account (`medquad-sa-dev@drm-medquad-service-dev.iam.gserviceaccount.com`). No default Compute Engine service accounts are used.
* **Least Privilege Mappings**: The runtime service account is restricted to `roles/discoveryengine.editor`, `roles/aiplatform.user`, `roles/bigquery.dataEditor`, and `roles/secretmanager.secretAccessor`.

#### Data Protection & Compliance

* **Encryption**: 100% of data is encrypted in transit using TLS 1.3 and at rest using Google-managed and Customer-Managed Encryption Keys (CMEK) via Cloud KMS.
* **Network Isolation**: Serverless VPC Access Connectors route all Cloud Run backend traffic through the private Shared VPC, eliminating public internet exposure for internal microservices.
* **PII & Sensitive Data**: Pre-flight sanitization pipelines mask inbound query entities before model ingestion.

#### AI Safety & Prompt Management

* **GCP Model Armor**: Standardized integration of Model Armor filters out prompt injection attacks, jailbreak attempts, and toxic behaviors natively.
* **Custom Clinical Guardrails**:
  * **Safe Refusal (Scope Lock)**: A deterministic pre-flight filter intercepts diagnostic queries or prescription requests in **0.07 ms**, returning an educational disclaimer with **$0.00 token cost**.
  * **Toxicity and Hallucination Checks**: Output hooks analyze LLM output against retrieved chunks using a fast semantic pass.
* **Prompt Lifecycle**: Prompts are separated from application logic, versioned in a dedicated prompt repository, and retrieved dynamically at startup.
* **Human-in-the-Loop (HITL)**: Mandatory clinical escalation paths for ambiguous or edge-case medical inquiries.

#### CI/CD Pipeline

* Deployed via GitHub Actions / Cloud Build triggered automatically upon merges to repository branches.
* The pipeline executes code formatting, security linting, and a comprehensive pytest suite (achieving **>80% code coverage**) with automated promotion gates.

---

### Data Engineering & Intelligence

#### Data Sources & Usage

* **Source Systems**: Raw NIH MedQuAD medical Q&A XML/JSON files stored in a secure Google Cloud Storage bucket (`gs://drm-medquad-service-dev-dev-medquad-corpus/`).
* **Data Profiles**: Unstructured and semi-structured clinical Q&A datasets covering over 47,000 medical conditions.
* **Access Patterns**: Real-time semantic search via the Researcher Agent's Vertex AI Search tool.

#### Retrieval & Intelligence Strategy

* **Vector Infrastructure**: Vertex AI Search (Google Enterprise AI Platform / GEAP) acts as the managed RAG engine (`medquad-datastore-dev`).
* **Embedding Strategy**: Automatic document chunking (500-token chunks with 10% overlap), indexed using Vertex AI's standard semantic embedding model (`text-embedding-004`).

---

### Testing & Evaluation Framework

The evaluation strategy employs a hybrid approach, combining deterministic/statistical check pipelines with semantic model assessments.

#### 1. Statistical & Heuristic Evaluations (CI/CD Gates)

These tests execute on every pull request using a golden dataset of 150 clinical questions stored in BigQuery, asserting baseline performance without calling expensive models:

* **ROUGE-L & BLEU Scores**: The system calculates ROUGE-L (recall-focused) and BLEU (precision-focused) scores comparing the generated clinical answer against authoritative NIH ground-truth text. The build pipeline enforces a threshold of **ROUGE-L $\ge$ 0.40** and **BLEU $\ge$ 0.35**.
* **Clinical Entity Overlap (F1-Score)**: Extracts key medical entities (symptoms, drug names, diagnoses) from both output and ground-truth using a lightweight entity matcher. Asserts an entity F1-score of **$\ge$ 0.75**.
* **Deterministic Citation Check**: Parses markdown output to ensure that:
  1. All inline citations (e.g. `[1]`) correspond to active, retrieved search result chunk IDs.
  2. Citation URLs link to verified NIH domains (`medlineplus.gov`, `cancer.gov`, `niddk.nih.gov`).
* **Safe Refusal Verification**: Verifies that diagnostic/prescriptive query test cases deterministically trigger standard refusal text (regex check) rather than generating active advice.

#### 2. Semantic Evaluations (Nightly / Ad-hoc)

* **LLM-as-a-Judge**: Automated pipelines execute using Gemini 2.5 Flash to evaluate unstructured quality dimensions:
  * **Faithfulness**: Verifying the output contains only facts supported by retrieved context chunks (detecting hallucination).
  * **Helpfulness**: Scoring whether the structure is clear and directly addresses the clinical query.

---

### Analytics, Insights & Feedback

#### User Behavior & Engagement

* **User Actions**: Frontends log thumbs-up/down feedback and custom clinician comments directly into BigQuery telemetry tables.
* **Session Metrics**: Tracks session length, recurring clinical workflows, and query complexity to monitor user adoption.

#### Operational & Business Intelligence

* **Usage & Cost**: Models log token consumption (prompt, completion, and cached tokens) to BigQuery (`medquad_telemetry_dev.token_usage_events`), enabling precise cost projections.
* **Performance Trends**: Captures Time to First Token (TTFT), total latency, and per-agent execution times.
* **BI Dashboards**: Exported to Looker Studio to visualize "North Star" performance and financial metrics.

#### Observability & Audit

* **Logging**: FastAPI backend produces structured JSON logs containing trace IDs, exported directly to Cloud Logging.
* **Audit Trails**: Immutable logs capture all sensitive transactions and data retrievals, ensuring compliance with clinical auditing requirements.
