# ADR 0005: Multi-Environment Terraform Architecture and Cloud Build CI/CD

## Status
Accepted

## Context
Deploying enterprise AI infrastructure across development, staging, and production requires strict environment parity, reproducibility, isolation, and automated governance.

## Decision
We organize Terraform into a modular hierarchy with environment isolation:
1. **Reusable Core Modules (`terraform/modules/`)**:
   - `cloud_run`: Serverless container hosting with autoscaling, environment variables, and health checks.
   - `vertex_search`: Discovery Engine Data Store and search engine definitions.
   - `storage`: GCS buckets with versioning, lifecycle management, and encryption.
   - `iam`: Granular Service Accounts with Least Privilege bindings.
   - `bigquery_telemetry`: Telemetry and audit datasets with partitioned tables.
   - `secret_manager`: Secret placeholders and IAM accessor permissions.
   - `networking`: VPC, Serverless VPC Access connector, and firewall rules.
2. **Environment Stacks (`terraform/environments/{dev,staging,prod}/`)**:
   - Each environment maintains independent remote state backends (GCS), configuration values (`terraform.tfvars`), and scaling parameters.
3. **Automated CI/CD via Cloud Build**:
   - Pull requests trigger automated linting (`terraform fmt`, `ruff`), pytests (>80% coverage), and `terraform plan`.
   - Merges to `main` trigger automated deployment to `dev`.
   - Release tags trigger promotion to `staging` and approval-gated deployment to `prod`.

## Consequences
- **Positive**: Strict environment parity, zero manual deployment drift, immutable infrastructure, and enterprise-grade change management.
- **Trade-offs**: Requires initial GCS bucket provisioning for remote state storage.
