# MedQuAD Clinical Assistant — Customer Presentation Slide Deck & Defense Script

> **Format:** 7 Slides | Delivery Time: ~10 Minutes  
> **Audience Simulation:** Customer Executive Panel (CTO, CIO, CISO, CFO, Head of Clinical Research)

---

## Slide 1: Title & Executive Summary
* **Title:** MedQuAD Clinical Research Assistant: Enterprise-Grade Biomedical Intelligence
* **Presenter:** Daniel Alvarez Martinez (Forward Deployed Engineer, Google Cloud AI)
* **Value Proposition:** Reducing clinical literature review time by >60% while enforcing strict zero-hallucination policies, non-diagnostic guardrails, and least-privilege security on GCP.

---

## Slide 2: The Business & Clinical Problem
* **The Challenge:** Biomedical researchers spend hours manually sifting through thousands of clinical publications to synthesize disease markers, protocols, and ongoing trials.
* **The Risk:** Traditional LLMs hallucinate facts, fail to provide verifiable citations, leak sensitive patient data (PII/PHI), or inadvertently give unauthorized medical advice.
* **Our Solution:** A grounded multi-agent platform powered by Vertex AI Search (NIH MedQuAD corpus), Gemini 2.5, Model Armor guardrails, and enterprise observability.

---

## Slide 3: Functional Capabilities & Live Demonstration
* **Key Features:**
  * **Verified Grounded Synthesis:** Every factual statement has an interactive citation `[1]`, `[2]` linked directly to canonical NIH documentation.
  * **Split-Pane Source Viewer:** Side-by-side verification of original medical literature snippets with relevance confidence scores.
  * **Scope Lock Non-Diagnostic Safety:** Deterministic interception and refusal of personal diagnostic or prescription queries.
  * **Interactive Demo:** Walkthrough of a Stage II Hodgkin Lymphoma diagnostic marker and staging query.

---

## Slide 4: High-Level Architecture (HLA) & Multi-Agent Mesh
* **Architecture Highlights:**
  * **Ingress & Compute:** Google Cloud Run (containerized FastAPI async backend) protected by IAP.
  * **ADK Multi-Agent Mesh:**
    * *RootOrchestrator:* Supervises intent routing and error handling.
    * *ResearcherAgent:* Executes semantic search over Vertex AI Search (NIH corpus) with Gemini 2.5 Pro.
    * *ReviewerAgent:* Independent factuality and citation verification with Gemini 2.5 Flash.
  * **Data Layer:** Versioned GCS bucket indexing into Vertex AI Search (GEAP).

---

## Slide 5: Security, Compliance & Observability (Zero Trust)
* **Security & IAM:**
  * Dedicated custom Service Account (`medquad-sa`) with least-privilege IAM roles.
  * Google Cloud Model Armor filtering prompt injections and redacting PII before model ingestion.
  * Serverless VPC Access connector keeping traffic within private Google network perimeters.
* **Enterprise Observability:**
  * OpenTelemetry distributed tracing integrated with Google Cloud Trace.
  * Granular token usage, cost projections, and audit logs streaming into BigQuery.

---

## Slide 6: Cost Modeling, Latency & Engineering Trade-offs
* **Cost Optimization Strategy:**
  * **Tiered Model Routing:** Gemini 2.5 Flash for high-frequency routing and review gates (10x cost reduction) vs. Gemini 2.5 Pro for deep clinical reasoning.
  * **Prompt Context Caching:** Reusing static medical schemas saves up to 75% on token costs.
  * **Cost per Query:** Average cost of **$0.00035 USD** per complex clinical synthesis.
* **Latency Profile:** Sub-2.0s end-to-end response time with warm Cloud Run instances.

---

## Slide 7: AI-Driven Development (AIDD) & Path to Production
* **Development Methodology:**
  * 100% developed using JetSki and Gemini 3.5 Flash for rapid scaffolding, automated pytest suites (>80% coverage), and statistical evals (ROUGE-L >= 0.40, BLEU >= 0.35, Entity F1 >= 0.75).
* **Multi-Environment Terraform:**
  * Modular IaC with strict environment parity across `dev`, `staging`, and `prod`.
  * Automated CI/CD pipelines via Cloud Build.

---

## Panel Objection Handling Guide (Executive FAQs)

### 🛡️ For the CISO / Security Director:
* **Objection:** *"How do you guarantee this model won't leak sensitive patient data or get hijacked via prompt injections?"*
* **Response:** *"We employ a dual-layer defense: GCP Agent Runtime Model Armor intercepts adversarial patterns and sanitizes PII (SSNs, MRNs, emails) before the query ever touches a model. Additionally, the backend runs in a secure VPC perimeter with least-privilege service account credentials."*

### 🩺 For the Chief Medical Officer (CMO):
* **Objection:** *"What prevents the assistant from giving bad medical advice or diagnosing a patient incorrectly?"*
* **Response:** *"We enforce a deterministic Scope Lock engine before model invocation. Any query with diagnostic or prescriptive intent is immediately intercepted with a standardized research refusal. Furthermore, the ReviewerAgent strictly blocks any output not grounded in retrieved NIH documents."*

### 💰 For the CFO:
* **Objection:** *"How do we manage and predict LLM operating costs as user adoption scales?"*
* **Response:** *"We utilize a tiered model architecture where fast routing runs on Gemini 2.5 Flash, context caching reduces repetitive token costs by 75%, and every single token is recorded in BigQuery for real-time cost auditing in Looker dashboards."*
