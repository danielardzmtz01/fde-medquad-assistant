---
name: fde-agent-framework
description: >-
  Enterprise Agent & Landing Zone framework calibrated to Google Cloud's Forward Deployed
  Engineering (FDE) Capstone Rubric (100% Exemplary / Customer-Ready grade). Enforces strict
  multi-agent ADK Supervisor-Worker meshes, deterministic safety (Scope Lock / Model Armor),
  FinOps observability, and multi-repo Terraform Landing Zones (one repo per environment plus
  static central infrastructure). Use whenever designing, scaffolding, refactoring, or defending
  any Google Cloud enterprise agentic AI project.
---

# FDE Agent Excellence & Enterprise Landing Zone Framework

This skill defines the mandatory architectural, security, FinOps, and DevOps standards required to achieve an **Exemplary (100% Customer-Ready)** score on the official **Forward Deployed Engineering (FDE) Capstone Rubric** (`go/fde-capstone-project`).

Whenever scaffolding, reviewing, or documenting an agentic AI system on Google Cloud, you MUST enforce the patterns defined herein.

---

## 1. Core Architectural Pillars (The FDE Rubric Standards)

Every production-grade agent project must satisfy six core architectural dimensions:

```
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                        FDE Agent Excellence: 6 Rubric Dimensions                       │
├────────────────────────────────────────────────────────────────────────────────────────┤
│ 1. Architecture & Design    │ 4-Tier HLA, Vector Search, 10 ADRs, OpenAPI, Runbooks     │
│ 2. Security & Compliance    │ Zero-Trust IAP, Least-Privilege IAM, CMEK, Scope Lock    │
│ 3. Reliability & Resilience │ Cloud Run v2, OpenTelemetry Tracing, BigQuery Telemetry  │
│ 4. Performance & FinOps     │ Mathematical Costing, Prompt Caching (75%), Scale-to-0   │
│ 5. Operational Excellence   │ Multi-Repo GitOps, Golden Dataset CI/CD Gates (ROUGE/F1) │
│ 6. Designing for Change     │ ADK Supervisor-Worker Mesh, Externalized Config, SSE     │
└────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Mandatory Terraform Landing Zone Architecture (Multi-Repo GitOps)

### 2.1 The Golden Rule: Dedicated Repository per Environment + Static Infra
> [!IMPORTANT]
> **NEVER** use a monolithic Terraform repository or mix environment state files.
> All enterprise agent projects MUST implement **four distinct Git repositories**:
> 1. `terraform-<project>-central` (Static Infrastructure & Central Governance)
> 2. `terraform-<project>-dev` (Development Environment)
> 3. `terraform-<project>-stg` (Staging Environment)
> 4. `terraform-<project>-prod` (Production Environment)

### 2.2 Repository Breakdown & Responsibilities

#### 1. `terraform-<project>-central` (Static & Shared Services)
* **Resource Hierarchy:** Root folder (`folders.tf`) containing segregated environment folders (`DEV`, `STG`, `PRD`).
* **Central Admin Project (`*-admin-central`):**
  * **Artifact Registry (`<project>-repo`):** Central immutable container supply chain. Images are built, vulnerability-scanned, and cryptographically signed once, then promoted immutably (`DEV` → `STG` → `PRD`) without rebuilds.
  * **Network Connectivity Center (NCC) Hub (`<project>-ncc-hub-central`):** Transit routing core replacing $O(N^2)$ VPC Peering meshes with $O(N)$ Hub-and-Spoke connectivity.
  * **CI/CD Automation Service Account (`<project>-cicd-sa`):** Granted `roles/compute.xpnAdmin` at the folder level to automate Shared VPC bindings.

#### 2. `terraform-<project>-dev` (DEV Environment Repo)
* **Host Project (`*-admin-dev`):**
  * Shared VPC Network (`10.10.0.0/24`) with Private Google Access (PGA) enabled.
  * Serverless VPC Access Connector (`10.10.1.0/28`) for private container egress.
  * NCC Spoke attached to `<project>-ncc-hub-central`.
  * Egress/Ingress Firewall rules blocking all unauthorized lateral movement.
* **Service Project (`*-service-dev`):**
  * **Cloud Run v2 Workload Backend:**
    * Configuration: 2 vCPU, 2 GiB RAM, 40 concurrent requests per container.
    * Auto-scaling: Scale-to-zero (`min_instance_count = 0`, `max_instance_count = 3`) to optimize cost in DEV.
    * Private Egress: `all-traffic` forced through Serverless VPC Connector (Zero Public IP exposure).
  * **Serverless Network Endpoint Group (NEG):** Maps Cloud Run backend to Cloud Load Balancing / Identity-Aware Proxy (IAP).
  * **Vertex AI Search Engine & Datastore (`<project>-datastore-dev`):** Vector search over enterprise corpus with chunking (500 tokens, 10% overlap) and cosine similarity cutoff (≥ 0.80).
  * **Corpus Cloud Storage Bucket:** CMEK-encrypted with Cloud KMS, object versioning, and lifecycle rules.
  * **BigQuery Telemetry Sink:** Partitioned daily by `timestamp`, clustered by `model_name` and `user_email`.
  * **Secret Manager:** Ephemeral runtime injection of Model Armor keys and API tokens.

#### 3. `terraform-<project>-stg` (Staging Environment Repo)
* **Environment Parity:** Identical topology to DEV, isolated state bucket, validated via automated deployment promotion gates.

#### 4. `terraform-<project>-prod` (Production Environment Repo)
* **Production Hardening:**
  * Cloud Run v2: `min_instance_count = 1` (warm instances to eliminate cold starts), `max_instance_count = 100`.
  * Multi-region or multi-zone failover redundancy.
  * Mandatory Cloud Armor WAF policies (DDoS mitigation, rate limiting at 100 req/min, OWASP Top 10 rules).
  * Strict Domain Restricted Sharing (`constraints/iam.allowedPolicyMemberDomains`).

### 2.3 Separation of Duties (SoD) & Blast Radius Isolation
* **NetOps / SecOps:** Manage Host Projects (`*-admin-*`), IP allocations, and firewall policies without access to clinical data or AI models.
* **DevOps / AI Engineers:** Deploy code, agents, and datastores in Service Projects (`*-service-*`) without the capability to expose public IPs or alter VPC routing.
* **Blast Radius Containment:** Separate remote GCS backend state buckets (`backend.tf`) per environment prevent catastrophic state file lockouts or accidental cross-environment destruction.

---

## 3. Cognitive Multi-Agent Architecture (Google ADK Blueprint)

### 3.1 Supervisor-Worker Topology
Never rely on a single monolithic LLM prompt. Distribute cognitive tasks across specialized subagents using Google's **Agent Development Kit (ADK)**:

```
                                [ 👤 Clinician / User ]
                                           │
                                           ▼ (HTTPS + IAP JWT)
                                 [ ⚡ FastAPI Backend ]
                                           │
                                           ▼ (Pre-Flight Filter)
                             [ 🛡️ Deterministic Scope Lock ]
                                           │
               ┌───────────────────────────┴───────────────────────────┐
               ▼ (Prescriptive/PII/Injection)                          ▼ (Valid Domain Inquiry)
    [ ❌ REFUSED_SCOPE_LOCK ]                                 [ 🧠 Root Orchestrator (Flash) ]
    • Latency: 0.07 ms                                        • Session State (SQLite)
    • Tokens: 0 ($0.00 cost)                                  • Turn Compaction (>10 turns)
    • Safe Advisory Notice                                    • Task Triage & Delegation
                                                                       │
                                                                       ▼
                                                          [ 🔬 Researcher Agent (Pro T=0.2) ]
                                                          • Vertex AI Search (GEAP)
                                                          • Deep Biomedical Synthesis
                                                          • Inline Citations [1], [2]
                                                                       │
                                                                       ▼ (Draft + Sources)
                                                          [ 🔍 Reviewer Agent (Flash T=0.0) ]
                                                          • Adversarial Factuality Audit
                                                          • 100% Entailment Verification
                                                          • Hallucination Stripping
                                                                       │
                                                                       ▼ (Approved JSON)
                                                          [ ⚡ FastAPI Streamer (SSE) ]
                                                           │                        │
                                                           ▼ (2.13s Latency)         ▼ (Async Stream)
                                                    [ 🖥️ Client UI ]         [ 📊 BigQuery Telemetry ]
                                                                             ($0.0013 / query)
```

### 3.2 Subagent Role Specifications

| Subagent Role | Model Engine | Parameters | Core Responsibilities | Cognitive Guardrail |
| :--- | :--- | :--- | :--- | :--- |
| **Root Orchestrator** | **Gemini 3.6 Flash** | Low latency, `top_p=0.95` | Intent triage, session recovery, worker delegation, turn compaction. | **Zero Tool Hallucination:** Dispatches strictly to vetted subagents; forbidden from generating clinical facts. |
| **Domain Researcher** | **Gemini 3.6 Pro** | `temperature = 0.2`, `top_k=40` | Vector & keyword search on Vertex AI Search, evidence synthesis, citations `[1]`, `[2]`. | **Corpus Confinement:** Restricted to authoritative datastore; forbidden from extrapolating unsupported claims. |
| **Adversarial Reviewer** | **Gemini 3.6 Flash** | `temperature = 0.0` (zero-variance) | Adversarial factuality audit, claim entailment check, citation URL verification. | **Strict Binary Approval:** Excises 100% of ungrounded sentences; blocks output if citations do not match context. |

### 3.3 Context & Session Management
* **`SqliteSessionService`:** Persists session IDs, turn history, and agent state in SQLite with JSON serialization, maintaining conversational continuity across stateless Cloud Run instances.
* **`EventsCompactionConfig` & `LlmEventSummarizer`:** When conversational turns exceed 10, Gemini 3.6 Flash automatically compresses older context into an executive structured summary (< 1,200 tokens), preventing token window overflow and cutting multi-turn costs by **>75%**.

### 3.4 ADK Lifecycle Callbacks
1. `before_model_logging_callback`: Logs model intent and starts an OpenTelemetry span.
2. `after_model_logging_callback`: Captures finish reason, tokens, and latency, closing the trace span.
3. `before_tool_logging_callback` / `after_tool_logging_callback`: Logs sanitized tool parameters, durations, and outcomes.
4. `secret_detector_callback`: High-speed regex scanner blocking hardcoded API keys (`AIzaSy...`, `sk-...`, `Bearer ...`).
5. `tool_error_recovery_callback`: Translates HTTP 429/504 exceptions into structured recovery guidance with exponential backoff.

---

## 4. Security, Compliance & AI Safety (Model Armor & Scope Lock)

Every project must enforce multi-layered defense-in-depth:

| Layer | Mechanism | Target Threat / Scope | SLA / Impact |
| :--- | :--- | :--- | :--- |
| **1. Ingress Filter** | Google Cloud Model Armor | PII/PHI redaction (SSN, MRN, phone, email) & prompt injection / jailbreaks. | Pre-flight inspection; sanitizes input streams. |
| **2. Scope Lock** | Local Regex & AST Intent Classifier | Detects diagnostic and prescriptive medical/financial advice. | **0.07 ms latency, 0 tokens ($0.00 cost)**; returns safe advisory notice. |
| **3. Memory Guardrail** | ADK `secret_detector_callback` | Intercepts accidental leakage of cloud provider credentials or API tokens. | Zero-latency memory scan before payload dispatch. |
| **4. Network Controls** | Shared VPC, Serverless VPC Access, DRS | Domain Restricted Sharing (`iam.allowedPolicyMemberDomains`), zero public egress. | Guarantees all traffic remains on Google's private fiber backbone via PGA. |

---

## 5. FinOps, Mathematical Cost Modeling & Observability

### 5.1 Mathematical Cost Attribution Formula
Every project defense must present an exact token cost formula:

$$\text{Cost} = \left( T_{\text{in}} \times \frac{\$1.25}{10^6} \right) + \left( T_{\text{out}} \times \frac{\$5.00}{10^6} \right) + \left( T_{\text{cached}} \times \frac{\$0.3125}{10^6} \right)$$

* **Prompt Context Caching:** Static system schemas and corpus instructions achieve a **75% discount** on cached tokens.
* **Tiered Routing Savings:** Reserving Gemini Pro exclusively for synthesis while using Gemini Flash for triage and review delivers a **62% net cost reduction** vs. monolithic Pro implementations.
* **Live Benchmark Target:** Average end-to-end query cost must remain $\le \$0.0020\text{ USD}$ (target: **\$0.0013 USD**).

### 5.2 Distributed Tracing & BigQuery Telemetry Sink
* **OpenTelemetry SDK:** Instruments trace IDs across client, API, and agent spans, propagating trace context to **Google Cloud Trace**.
* **BigQuery Streaming Table (`token_usage_events`):** Asynchronously records `session_id`, `user_email`, `model_name`, `input_tokens`, `output_tokens`, `cached_tokens`, `latency_ms`, `grounding_score`, and `estimated_cost_usd`.

---

## 6. Operational Excellence & CI/CD Evaluation Gates

### 6.1 Automated Quality Gates (`/api/v1/eval`)
Before code promotion from `DEV` to `STG` or `PRD`, CI/CD pipelines must execute automated evaluation against a curated **Golden Dataset**:

* **ROUGE-L Score:** $\ge 0.40$ (Clinical/domain recall verification).
* **BLEU Score:** $\ge 0.35$ (Terminology precision).
* **Entity F1-Score:** $\ge 0.75$ (Domain entity overlap).
* **Unit & Integration Test Coverage:** Pytest suite with $\ge 80\%$ code coverage.

---

## 7. Deliverable Standards for 100% Defense Rating

When preparing the project for customer or capstone presentation, ensure the following assets are produced:

1. **Codebase Repository (GitHub):** Clean root directory with `src/backend/`, `src/frontend/`, `repos/`, `tests/`, `Makefile`, and `README.md`.
2. **Master Technical Design Document (Google Docs):** 10 exhaustive sections formatted with `bluedoc`, containing structured Markdown tables (no raw ASCII boxes) and clean Unicode typography.
3. **Architecture Diagrams:** Crisp vector PNGs with **pure white backgrounds (`#FFFFFF`)**, large high-contrast typography, and no overlapping SVG `<tspan>` tags:
   * Diagram 1: Multi-Environment Resource Topology (Hub-and-Spoke with NCC and Shared VPC).
   * Diagram 2: High-Level System Architecture (4-Tier Ingress, Compute, Agent Mesh, Storage/Telemetry).
   * Diagram 3: Multi-Agent Execution Sequence Diagram (15-step dual-branch workflow).
4. **Executive Slide Deck (Google Slides):** 5 to 9 slides covering Mission, Problem, Live Benchmarks, HLA, Infrastructure, FinOps, Lifecycle, and Q&A Objection Handling (CISO, CMO, CFO), complete with timed speaker notes.
