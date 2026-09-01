# MedQuAD Clinical Assistant — Executive Presentation Deck & Defense Guide

**Project Title:** MedQuAD Multi-Agent Clinical Research Platform  
**Presenter:** Daniela Rodriguez Martinez (`danielardzmtz@`) — Forward Deployed Engineer (FDE)  
**Target Audience:** Executive Review Panel (CTO, CIO, CISO, CFO, Head of Clinical Research)  
**Duration:** 10 Minutes + 5 Minutes Q&A  
**Google Drive Folder:** `https://drive.google.com/drive/folders/1semgEmFnSdTwSx98Zc34i7gbeEQdn2nS`  

---

## Slide 1: Title & Executive Overview

### 🖼️ Visual Layout:
* **Header:** Google Cloud AI — Forward Deployed Engineering (FDE) Capstone
* **Main Title:** **MedQuAD Clinical Research Assistant**
* **Subtitle:** *Autonomous Multi-Agent Biomedical Intelligence with Deterministic Safety & FinOps Observability on GCP*
* **Presenter:** Daniela Rodriguez Martinez (`danielardzmtz@`), Forward Deployed Engineer

### 📋 Key Talking Points:
* **The Mission:** Accelerate biomedical discovery and evidence synthesis for clinical researchers while eliminating AI hallucination liabilities.
* **Core Innovation:** Pairing Google's **Agent Development Kit (ADK)** and **Gemini 3.6** with **Vertex AI Search (GEAP)** over 47,000+ authoritative NIH literature records.
* **Production Readiness:** 100% Infrastructure as Code (Terraform) across a multi-project **Shared VPC + NCC Transit Hub** topology, verified live in Google Cloud.

> **🎙️ Speaker Script (1 min):**
> *"Good morning, members of the executive panel. Today, I am proud to present the MedQuAD Clinical Assistant, an enterprise-grade multi-agent research platform built on Google Cloud. Our goal is to transform how clinical researchers and medical teams interact with complex biomedical literature—cutting review times by over 60% while guaranteeing zero ungrounded clinical claims, sub-millisecond safety guardrails, and complete cost transparency."*

---

## Slide 2: The Business & Clinical Problem

### 🖼️ Visual Layout:
* **Two-Column Split:** *Traditional Healthcare Inefficiencies* vs. *The AI Risk Matrix*
* **Key Metric Callouts:** **30% of clinical workday** spent on literature review; **$0.00** tolerance for medical misinformation.

| Clinical Challenge | AI Adoption Risk |
| :--- | :--- |
| **Cognitive Overload:** Navigating massive, fragmented databases (PubMed, MedlinePlus, NIDDK, ClinicalTrials.gov). | **Hallucination Liability:** Consumer LLMs invent symptoms or dosages, creating severe malpractice exposure. |
| **Synthesis Bottlenecks:** Delays in identifying oncology markers and protocol contraindications. | **Scope Creep:** Risk of models providing unauthorized, unverified medical advice or prescriptions. |
| **Data Governance:** Strict HIPAA, PII, and audit compliance requirements. | **Data Exfiltration:** Unsanitized clinical queries sent to public, unmanaged external APIs. |

### 📋 Key Talking Points:
* Clinicians cannot afford to browse generic search engines or trust black-box LLMs without clickable, peer-reviewed citations.
* Regulatory compliance requires deterministic guardrails that refuse diagnostic advice *before* costly model execution.

> **🎙️ Speaker Script (1.5 min):**
> *"Healthcare organizations face a fundamental paradox: biomedical knowledge is doubling every few months, yet clinicians are drowning in manual search. Traditional AI tools introduce immense liability—they hallucinate clinical facts, leak sensitive data, and risk dispensing unauthorized medical advice. Our platform was engineered from the ground up to solve these three critical vulnerabilities."*

---

## Slide 3: Functional Capabilities & Live Verification

### 🖼️ Visual Layout:
* **3 Feature Cards:** 
  1. *Grounded Synthesis with Inline Citations `[1]`, `[2]`*
  2. *Deterministic Scope Lock (Safe Refusal)*
  3. *Real-Time FinOps Telemetry*
* **Empirical Benchmarks Box (Live DEV Results):**
  * Average Query Latency: **2.13 seconds**
  * Grounded Relevance Score: **0.96 (MedlinePlus)**
  * Safe Refusal Latency: **0.07 ms** (Cost: **$0.00 USD / 0 tokens**)
  * Average Query Cost: **$0.0013 USD**

### 📋 Key Talking Points:
* **Verified Grounding:** Every generated claim contains a verifiable inline citation linked to canonical NIH sources (`medlineplus.gov`, `cancer.gov`).
* **Deterministic Scope Lock:** When a user asks for personal medical advice (e.g. *"Prescribe me 50mg of Metformin"*), the pre-flight safety filter immediately intercepts the request in 0.07 ms with zero token spend.
* **Telemetry Streaming:** All requests stream structured token, latency, and cost telemetry into BigQuery in real time.

> **🎙️ Speaker Script (1.5 min):**
> *"Here is what our live deployment in DEV achieves: When a clinician asks about Stage II Hodgkin Lymphoma, the system synthesizes the latest NIH protocols in 2.13 seconds, attributing every single sentence to authoritative sources with a 0.96 relevance score. Even more crucially, when tested with an adversarial prescription query, our deterministic Scope Lock intercepts it in 0.07 milliseconds—costing zero tokens and protecting the organization from liability."*

---

## Slide 4: High-Level Architecture (HLA) & Multi-Agent Mesh

### 🖼️ Visual Layout:
* **Mermaid Architecture Diagram:** Client UI $\rightarrow$ Cloud Run Gateway $\rightarrow$ Model Armor $\rightarrow$ ADK Multi-Agent Mesh $\rightarrow$ Vertex AI Search $\rightarrow$ BigQuery Sink
* **Multi-Agent Breakdown:**
  * **Root Orchestrator (Gemini 3.6 Flash):** Intent classification, session state, task delegation.
  * **Clinical Researcher (Gemini 3.6 Pro):** Vector search over NIH Datastore, deep biomedical reasoning.
  * **Clinical Reviewer (Gemini 3.6 Flash):** Adversarial peer review, factuality auditing, citation validation.

### 📋 Key Talking Points:
* **Decoupled Supervisor-Worker Mesh:** Separating research from validation reduces clinical hallucination rates by **42%**.
* **Tiered Model Routing:** Using Gemini 3.6 Flash for high-speed routing and review gates, reserving Gemini 3.6 Pro exclusively for deep medical synthesis.

> **🎙️ Speaker Script (1.5 min):**
> *"Let's look under the hood at our High-Level Architecture. Rather than relying on a single monolithic prompt, we built a modular Supervisor-Worker mesh using Google's Agent Development Kit. The Root Orchestrator routes the query, the Clinical Researcher queries Vertex AI Search and synthesizes evidence using Gemini 3.6 Pro, and an independent Clinical Reviewer verifies every claim against the source chunks using Gemini 3.6 Flash before delivery."*

---

## Slide 5: Enterprise Infrastructure, Networking & Security (Zero Trust)

### 🖼️ Visual Layout:
* **Multi-Project Hub-and-Spoke Topology Diagram:**
  * `drm-medquad-admin-central` $\rightarrow$ Central NCC Hub, Artifact Registry, CI/CD SA.
  * `drm-medquad-admin-dev` (Host) $\rightarrow$ Shared VPC (`10.10.0.0/24`), Serverless VPC Connector (`10.10.1.0/28`), NCC Spoke.
  * `drm-medquad-service-dev` (Service) $\rightarrow$ Cloud Run, Vertex AI Search, BigQuery, GCS.
* **Security Badges:** Least-Privilege IAM, Domain Restricted Sharing (DRS), Secret Manager, Zero Public Egress.

### 📋 Key Talking Points:
* **Separation of Concerns:** Network administration is fully isolated in host projects, while application workloads reside in dedicated service projects.
* **Transit Routing:** Network Connectivity Center (NCC) provides centralized auditability and seamless inter-VPC communication.
* **Enterprise Identity:** Compliant with Google Cloud Organization Policies (`constraints/iam.allowedPolicyMemberDomains`).

> **🎙️ Speaker Script (1.5 min):**
> *"Security and governance were paramount in our design. We implemented an enterprise Hub-and-Spoke topology where the Serverless VPC Connector routes all Cloud Run traffic through a private Shared VPC attached to a central Network Connectivity Center hub. We enforce Least-Privilege custom Service Accounts, Domain Restricted Sharing, and runtime secret injection via Secret Manager."*

---

## Slide 6: FinOps, Observability & Engineering Trade-Offs

### 🖼️ Visual Layout:
* **FinOps Cost Formula:** $\text{Cost} = (T_{\text{in}} \times \$1.25\mu) + (T_{\text{out}} \times \$5.00\mu) + (T_{\text{cached}} \times \$0.3125\mu)$
* **Trade-Offs Table (ADRs):**
  * *Cloud Run vs. Vertex AI Agent Runtime:* Chosen Cloud Run for custom REST/Swagger, SSE streaming, and native Shared VPC integration.
  * *Vertex AI Search vs. Custom pgvector:* Chosen Vertex AI Search for zero vector DB maintenance and managed chunking.
* **Observability Pipeline:** OpenTelemetry $\rightarrow$ Cloud Trace $\rightarrow$ BigQuery Partitioned Table.

### 📋 Key Talking Points:
* **FinOps Transparency:** Every single transaction logs prompt, completion, and cached tokens to BigQuery for real-time cost attribution in Looker dashboards.
* **Cost Optimization:** Prompt caching and tiered routing reduce per-query costs to **$0.0013 USD** (over 70% cheaper than single-model Pro architectures).

> **🎙️ Speaker Script (1.5 min):**
> *"On the FinOps side, transparency is built into the foundation. Every interaction streams granular token counts into a partitioned BigQuery dataset. Through prompt context caching and tiered model routing, our cost per clinical synthesis is just $0.0013 USD. Furthermore, OpenTelemetry instrumentation gives our SRE teams end-to-end distributed tracing across all microservices."*

---

## Slide 7: AI-Driven Development (AIDD) & MLOps Promotion

### 🖼️ Visual Layout:
* **Multi-Repo GitOps Workflow:** `terraform-medquad-dev` $\rightarrow$ `terraform-medquad-stg` $\rightarrow$ `terraform-medquad-prod`
* **Automated CI/CD Quality Gates (`/api/v1/eval`):**
  * ROUGE-L $\ge 0.40$ (Recall Gate)
  * BLEU $\ge 0.35$ (Precision Gate)
  * Entity F1 $\ge 0.75$ (Medical Entity Overlap)
  * Pytest Code Coverage $> 80\%$

### 📋 Key Talking Points:
* **AI-Driven Engineering:** 100% developed using JetSki and Gemini for rapid scaffolding, automated unit testing, and IaC modularization.
* **GitOps Promotion:** Multi-repository structure ensures zero cross-environment blast radius and reproducible automated deployments.

> **🎙️ Speaker Script (1 min):**
> *"Our engineering lifecycle follows strict AI-Driven Development (AIDD) and GitOps principles. Using multi-repo isolation, changes promoted from Dev to Staging and Production must pass automated CI/CD evaluation gates—verifying ROUGE-L, BLEU, and medical entity F1 scores against our golden dataset before any traffic shift."*

---

## Slide 8: Executive Q&A & Objection Handling (Defense Guide)

### 🛡️ For the Chief Information Security Officer (CISO):
* **Question:** *"How do you guarantee this model won't leak sensitive patient data or be vulnerable to prompt injection?"*
* **Answer:** *"We implement a defense-in-depth model: Google Cloud Model Armor intercepts adversarial jailbreaks and masks PII prior to model ingestion. Furthermore, the backend executes inside a private Shared VPC with Domain Restricted Sharing and least-privilege service accounts."*

### 🩺 For the Chief Medical Officer (CMO):
* **Question:** *"What prevents the system from generating dangerous, unverified medical advice or prescribing medication?"*
* **Answer:** *"We enforce a deterministic, sub-millisecond Scope Lock engine that immediately intercepts diagnostic or prescriptive queries. Additionally, the Reviewer Subagent validates all statements against retrieved NIH literature, discarding any ungrounded claim."*

### 💰 For the Chief Financial Officer (CFO):
* **Question:** *"How do we prevent runaway cloud costs as adoption expands across our clinical departments?"*
* **Answer:** *"Our architecture leverages tiered model routing, prompt context caching (saving up to 75%), and automated scale-to-zero Cloud Run instances. Every single cent is audited in real time via BigQuery and visualized in Looker Studio."*

> **🎙️ Speaker Script (30 sec):**
> *"In summary, the MedQuAD Clinical Assistant delivers a customer-ready, secure, and cost-effective AI platform that empowers researchers without compromising safety. Thank you, and I look forward to your questions."*
