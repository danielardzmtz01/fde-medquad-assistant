# Troubleshooting & Incident Response Guide — MedQuAD Assistant

## 1. Common Failure Modes & Resolutions

| Symptom / Error | Root Cause | Remediation Procedure |
|---|---|---|
| `403 PermissionDenied` on Vertex AI Search | Missing `roles/discoveryengine.viewer` on Service Account | Verify IAM bindings in `terraform/modules/iam/main.tf` and re-apply Terraform. |
| Scope Lock false positive on clinical query | Overly broad regex matching in `safe_refusal.py` | Check `DIAGNOSTIC_PATTERNS` in `src/backend/app/safety/safe_refusal.py` and refine pattern boundaries. |
| Cloud Run cold-start latency spike (>3s) | Container initialization overhead or min-instances = 0 | Update `min_instances = 1` in `terraform.tfvars` for Staging/Prod to maintain warm container pool. |
| Missing citations in response | Low relevance score from Vertex Search (<0.70) | Review document chunk size and metadata tags in `ingest_medquad.py`; verify data store index status. |
| `BigQuery insert_rows_json` timeout | Transient quota limit or network egress blocking | Ensure Serverless VPC Access connector has private Google access enabled; check BigQuery IAM permissions. |

---

## 2. Distributed Tracing in Google Cloud Trace
To inspect end-to-end execution bottlenecks:
1. Copy the `X-Trace-Id` header from any API response.
2. Navigate to **Google Cloud Console** -> **Trace** -> **Trace Explorer**.
3. Filter by `Trace ID` to inspect latencies across:
   - `HTTP POST /api/v1/chat`
   - `ModelArmorGuardrail.sanitize_input`
   - `ResearcherAgent.search_tool`
   - `Gemini 2.5 Pro Inference`
   - `ReviewerAgent.validate`
