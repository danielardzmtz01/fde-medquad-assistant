# Multi-Repository GitOps & Environment Promotion Architecture

## 1. Overview & Strategy

To enforce strict isolation, prevent blast radius propagation, and ensure environment reproducibility, the MedQuAD infrastructure follows a **Multi-Repository GitOps model**.

Each environment maintains its own dedicated repository with parameterized Terraform and automated promotion workflows:

```
                      [ CENTRAL / STATIC-INFRA REPO ]
                     (GCS State, Artifact Reg, NCC Hub)
                                     │
                 ┌───────────────────┼───────────────────┐
                 ▼                   ▼                   ▼
         [ DEV REPO ] ──(Promote)─► [ QA REPO ] ──(Promote)─► [ PROD REPO ]
          • Admin VPC                • Admin VPC               • Admin VPC
          • Service Workload         • Service Workload        • Service Workload
```

---

## 2. Repositories Breakdown

| Repository Name | Scope & Responsibilities | Workflows |
|---|---|---|
| **`terraform-medquad-central`** | **Layer 1: Static Infra**<br/>• Central GCS Bucket for remote state<br/>• Central Artifact Registry (`medquad-repo`)<br/>• Central CI/CD Service Account<br/>• Central Network Connectivity Center (NCC) Hub | `terraform_static.yml` |
| **`terraform-medquad-dev`** | **DEV Environment**<br/>• `terraform_admin_networking` (Dev VPC: `10.10.0.0/24`, Connector, NCC Spoke)<br/>• `terraform_service_workload` (Cloud Run Dev, Vertex Search, BigQuery) | • `terraform_admin.yml`<br/>• `terraform_services.yml`<br/>• `deployment_actions.yml` (Promote Dev -> QA) |
| **`terraform-medquad-qa`** | **QA Environment**<br/>• `terraform_admin_networking` (QA VPC: `10.20.0.0/24`, Connector, NCC Spoke)<br/>• `terraform_service_workload` (Cloud Run QA, Vertex Search, BigQuery) | • `terraform_admin.yml`<br/>• `terraform_services.yml`<br/>• `deployment_actions.yml` (Promote QA -> Prod) |
| **`terraform-medquad-prod`** | **PROD Environment**<br/>• `terraform_admin_networking` (Prod VPC: `10.30.0.0/24`, CMEK, NCC Spoke)<br/>• `terraform_service_workload` (Cloud Run HA, Vertex Search, BigQuery) | • `terraform_admin.yml`<br/>• `terraform_services.yml`<br/>• Gated Approval Releases |

---

## 3. GitHub Actions Parametrization Pattern

Within each repository, the Terraform code is identical. GitHub Actions dynamically injects:
1. **Dynamic Backend Configuration (`backend.tf`)**:
   ```yaml
   - name: Setup Terraform Backend
     run: |
       cat <<EOF > backend.tf
       terraform {
         backend "gcs" {
           bucket = "${{ secrets.TF_STATE_BUCKET }}"
           prefix = "terraform/state/${{ vars.ENV_NAME }}/service_workload"
         }
       }
       EOF
   ```
2. **Dynamic Variables Generation (`org_variables.auto.tfvars`)**:
   ```yaml
   - name: Setup Terraform Variables
     run: |
       cat <<EOF > org_variables.auto.tfvars
       service_project_id = "${{ secrets.SERVICE_PROJECT_ID }}"
       region             = "${{ vars.GCP_REGION || 'us-central1' }}"
       environment        = "${{ vars.ENV_NAME }}"
       container_image    = "${{ vars.CONTAINER_IMAGE }}"
       EOF
   ```
3. **Automated Promotion to Next Environment (`deployment_actions.yml`)**:
   * Uses a GitHub token (`TOKEN_USER`) to clone the source repo and push to the target repo (`TARGET_REPO_FN`), preventing direct manual edits in staging/production.
