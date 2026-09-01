# Deployment Runbook — MedQuAD Clinical Assistant

## 1. Prerequisites & GCP Environment Setup
1. **Google Cloud Project**: An active GCP sandbox project (e.g. `fde-medquad-sandbox-dev`).
2. **GCP APIs Enabled**:
   ```bash
   gcloud services enable \
     aiplatform.googleapis.com \
     discoveryengine.googleapis.com \
     run.googleapis.com \
     storage.googleapis.com \
     bigquery.googleapis.com \
     secretmanager.googleapis.com \
     cloudtrace.googleapis.com \
     cloudbuild.googleapis.com \
     vpcaccess.googleapis.com \
     compute.googleapis.com
   ```
3. **Google Cloud SDK & Terraform**: `gcloud auth application-default login` and `terraform >= 1.5.0`.

---

## 2. Infrastructure Provisioning via Terraform

### Step A: Initialize Terraform Backend
Navigate to the desired environment directory:
```bash
cd terraform/environments/dev
```

### Step B: Plan and Apply Resources
```bash
# Review planned resources (IAM, GCS, Vertex AI Search, BigQuery, VPC, Cloud Run)
terraform init
terraform plan -var="project_id=YOUR_PROJECT_ID"

# Apply configuration
terraform apply -auto-approve -var="project_id=YOUR_PROJECT_ID"
```

---

## 3. Data Corpus Ingestion into Vertex AI Search

### Step A: Upload MedQuAD Corpus to GCS
```bash
python src/data_pipeline/ingest_medquad.py \
  --input src/data_pipeline/sample_data/medquad_sample.json \
  --bucket YOUR_PROJECT_ID-dev-medquad-corpus
```

### Step B: Verify Data Store Ingestion
1. Open the Google Cloud Console -> **Vertex AI Search and Conversation** -> **Data Stores**.
2. Confirm that `medquad-datastore-dev` shows active documents indexed.

---

## 4. Local Development & Testing

```bash
# Install backend dependencies
pip install -r src/backend/requirements.txt

# Run FastAPI backend locally
uvicorn app.main:app --app-dir src/backend --reload --port 8080

# In another terminal, run frontend UI
cd src/frontend
npm install
npm run dev
```

---

## 5. Verification & Health Probes

```bash
# Smoke test health endpoint
curl -X GET http://localhost:8080/healthz

# Test clinical query endpoint
curl -X POST http://localhost:8080/api/v1/chat \
  -H "Content-Type: application/json" \
  -d '{"query": "What are diagnostic markers of Stage II Hodgkin Lymphoma?"}'
```
