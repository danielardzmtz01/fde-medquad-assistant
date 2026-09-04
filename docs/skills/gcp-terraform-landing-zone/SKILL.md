---
name: gcp-terraform-landing-zone
description: >-
  Enterprise Multi-Repo Terraform Landing Zone framework for Google Cloud Platform (GCP).
  Enforces a 4-repository GitOps topology (Central/Static Infra + DEV + STG + PRD), Shared VPC
  Host/Service project separation of duties (SoD), Network Connectivity Center (NCC) Hub-and-Spoke,
  immutable Artifact Registry supply chain, keyless Workload Identity Federation (WIF), and
  Zero-Trust security perimeters for any GCP workload.
---

# GCP Enterprise Terraform Landing Zone Framework (Multi-Repo GitOps)

A standardized, enterprise-grade Infrastructure as Code (IaC) framework for orchestrating secure, compliant, and scalable environments on Google Cloud Platform. 

This framework is **workload-agnostic**: use it to deploy containerized microservices (Cloud Run, GKE), serverless architectures, AI/ML platforms (Vertex AI), data lakes (BigQuery, Dataproc), or traditional virtual machines (Compute Engine).

---

## 1. Core Architectural Tenets

Every GCP deployment adhering to this framework MUST enforce five foundational principles:

```
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                        Enterprise GCP Landing Zone: 5 Core Tenets                      │
├────────────────────────────────────────────────────────────────────────────────────────┤
│ 1. Multi-Repo GitOps Isolation │ 1 Repo per Environment + 1 Central Static Infra Repo  │
│ 2. Separation of Duties (SoD)  │ Host Projects (NetOps) vs. Service Projects (DevOps)  │
│ 3. Zero Public Egress          │ Private Google Access (PGA) + Serverless VPC Access   │
│ 4. Hub-and-Spoke Transit (NCC) │ Network Connectivity Center Hub replaces VPC Peering  │
│ 5. Immutable Supply Chain      │ Central Artifact Registry (Build Once, Promote Everywhere)│
└────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## 2. The 4-Repository GitOps Topology

> [!IMPORTANT]
> **Monolithic Terraform repositories and mixed state files are strictly prohibited.**
> All enterprise deployments must be partitioned into **four independent Git repositories**:

```
organization-root/
│
├── 📁 terraform-<workload>-central/   # Repository 1: Central Governance & Static Infra
│   └── terraform_static/             # Root folder, env folders, Central Admin Project,
│                                     # Artifact Registry, NCC Hub, CI/CD Service Account.
│
├── 📁 terraform-<workload>-dev/       # Repository 2: Development Environment
│   ├── Host Project (*-admin-dev)    # Shared VPC, Serverless VPC Connector, NCC Spoke
│   └── Service Project (*-service-dev)# Cloud Run / GKE / Storage / IAM / Compute
│
├── 📁 terraform-<workload>-stg/       # Repository 3: Staging Environment (Parity with DEV)
│   ├── Host Project (*-admin-stg)    # Shared VPC, Serverless VPC Connector, NCC Spoke
│   └── Service Project (*-service-stg)# Staging workloads and datastores
│
└── 📁 terraform-<workload>-prod/      # Repository 4: Production Environment (Hardened)
    ├── Host Project (*-admin-prod)   # Shared VPC, Serverless VPC Connector, NCC Spoke
    └── Service Project (*-service-prod)# Production workloads, CMEK, Cloud Armor WAF
```

---

## 3. Detailed Repository Specifications

### 3.1 Repository 1: `terraform-<workload>-central` (Static & Shared Services)

Manages persistent organization resources that exist outside environment lifecycles.

#### Responsibilities:
1. **Resource Hierarchy (`folder.tf`):**
   * Creates the workload root folder (e.g., `folders/<folder_id>`).
   * Creates segregated environment child folders: `DEV`, `STG`, `PRD`.
2. **Central Admin Project (`project.tf`):**
   * Provisions `*-admin-central` linked to the central billing account.
3. **Immutable Container Supply Chain (`artifact_registry.tf`):**
   * Central Docker repository (`<workload>-repo`).
   * Vulnerability scanning (Container Analysis API) & Binary Authorization integration.
   * Container images are built, scanned, and signed once here; they are promoted immutably without rebuilding.
4. **Network Connectivity Center Hub (`ncc_hub.tf`):**
   * Provisions `medquad-ncc-hub-central` (or `<workload>-ncc-hub-central`).
   * Acts as the centralized transit core for environment Shared VPC spokes.
5. **CI/CD Automation Identity (`iam.tf`):**
   * Provisions `<workload>-cicd-sa`.
   * Assigned `roles/compute.xpnAdmin` and `roles/resourcemanager.folderAdmin` at the root folder level to automate Shared VPC bindings.
6. **Remote State Backend (`backend.tf`):**
   * Stored in a dedicated, versioned Cloud Storage bucket: `*-central-tfstate`.

```
terraform-<workload>-central/
├── .github/workflows/
│   └── terraform_static.yml     # Automated CI/CD pipeline for static resources
├── terraform_static/
│   ├── backend.tf               # GCS state bucket config
│   ├── provider.tf              # google, google-beta providers
│   ├── folder.tf                # Root and env folder definitions
│   ├── project.tf               # Central Admin project creation
│   ├── artifact_registry.tf     # Immutable container registry
│   ├── ncc_hub.tf               # Network Connectivity Center Hub
│   ├── iam.tf                   # CI/CD SA and folder-level role bindings
│   ├── variables.tf             # Parameter declarations
│   ├── terraform.tfvars.example # Example parameter values
│   └── outputs.tf               # Exported Hub URI, Registry URI, Folder IDs
└── .gitignore
```

---

### 3.2 Repositories 2, 3 & 4: `terraform-<workload>-<env>` (DEV, STG, PRD)

Each environment repository orchestrates two tightly decoupled projects to enforce **Separation of Duties (SoD)**:

#### 1. Host Project (`*-admin-<env>`):
* **Shared VPC (`shared_vpc.tf` & `vpc_network.tf`):**
  * Dedicated CIDR range per environment (e.g., DEV: `10.10.0.0/24`, STG: `10.20.0.0/24`, PRD: `10.30.0.0/24`).
  * **Private Google Access (PGA)** enabled on all subnets (eliminates external internet routing for Google APIs).
  * Explicit firewall rules blocking unauthorized ingress/egress.
* **Serverless VPC Access Connector (`vpc_connector.tf`):**
  * Dedicated `/28` CIDR range (e.g., DEV: `10.10.1.0/28`, STG: `10.20.1.0/28`, PRD: `10.30.1.0/28`).
  * Minimum 2 instances, maximum 10 instances (`e2-micro` in DEV/STG, `f1-micro` or `e2-standard-4` in PRD).
* **NCC Transit Spoke (`ncc_spoke.tf`):**
  * Attaches the environment's Shared VPC as a spoke to the Central NCC Hub (`ncc_hub.id`).

#### 2. Service Project (`*-service-<env>`):
* **Project Association:** Bound to the Host Project via `google_compute_shared_vpc_service_project`.
* **Compute & Workload Execution (`cloud_run.tf` / `gke.tf` / `compute.tf`):**
  * Private egress configured with `vpc_access.egress = "ALL_TRAFFIC"` through the Serverless VPC Connector.
  * Zero public IP addresses assigned.
* **Zero-Trust Ingress (`load_balancer_iap.tf`):**
  * Global External HTTPS Application Load Balancer with Google-managed SSL (TLS 1.2/1.3).
  * Cloud Armor WAF security policy (DDoS, rate limiting, OWASP Top 10).
  * Identity-Aware Proxy (IAP) enforcing corporate SSO / MFA before traffic reaches compute.
  * Serverless Network Endpoint Group (NEG) mapping ALB backend directly to Cloud Run.
* **Storage & Encryption (`storage.tf` & `secrets.tf`):**
  * Cloud Storage buckets with Customer-Managed Encryption Keys (CMEK) via Cloud KMS.
  * Secret Manager with runtime secret accessor bindings.
* **Observability & Telemetry (`bigquery.tf` / `monitoring.tf`):**
  * Partitioned and clustered BigQuery datasets for runtime audit logs, telemetry, and FinOps tracking.

```
terraform-<workload>-<env>/
├── .github/workflows/
│   ├── terraform_admin.yml      # CI/CD for Host project networking
│   └── terraform_services.yml   # CI/CD for Service project workloads
├── backend.tf                   # Isolated remote GCS state (e.g. *-dev-tfstate)
├── provider.tf                  # Google & Google-Beta providers
├── data.tf                      # Remote state lookups to Central Admin
├── folder.tf                    # Environment folder binding
├── project_admin.tf             # Host Project creation & API enablement
├── project_service.tf           # Service Project creation & Shared VPC binding
├── vpc_network.tf               # Custom VPC network and subnets with PGA
├── shared_vpc.tf                # Shared VPC Host enablement & attachment
├── vpc_connector.tf             # Serverless VPC Access Connector (/28 subnet)
├── ncc_spoke.tf                 # Network Connectivity Center VPC Spoke
├── iam.tf                       # Least-Privilege IAM & cross-project service agent grants
├── cloud_run.tf (or compute.tf) # Serverless compute with private egress
├── load_balancer_iap.tf         # HTTPS LB + IAP + Cloud Armor WAF + Serverless NEG
├── storage.tf                   # GCS buckets with CMEK & lifecycle rules
├── secrets.tf                   # Secret Manager secrets & access policies
├── bigquery.tf                  # BigQuery telemetry & audit datasets
├── variables.tf                 # Input variables (CIDRs, environment names, regions)
└── outputs.tf                   # Output URLs, service endpoints, connector IDs
```

---

## 4. Standardized CIDR Allocation Matrix

To prevent IP collisions across environments and allow seamless hybrid expansion, adhere to this non-overlapping CIDR allocation:

| Environment | Shared VPC Subnet | Serverless VPC Access Connector | Purpose |
| :--- | :--- | :--- | :--- |
| **DEV** | `10.10.0.0/24` | `10.10.1.0/28` | Development compute, internal services & PGA |
| **STG** | `10.20.0.0/24` | `10.20.1.0/28` | Staging compute, pre-release verification |
| **PRD** | `10.30.0.0/24` | `10.30.1.0/28` | Production workloads, high-availability clusters |
| **Central / Transit** | `10.0.0.0/24` | N/A | Central administrative services & NCC transit |

---

## 5. Enterprise IAM & Cross-Project Delegation Rules

### 5.1 Strict Prohibition of Primitive Roles
Under no circumstances may `roles/owner`, `roles/editor`, or `roles/viewer` be granted to any service account or user. Use predefined, granular roles.

### 5.2 Mandatory Cross-Project Service Agent Grants
Because resources run in the Service Project while networking and container images reside in other projects, the following IAM delegations MUST be defined in `iam.tf`:

1. **Shared VPC Egress Permission:**
   The Google Cloud Run Service Agent of the **Service Project** must have `roles/vpcaccess.user` in the **Host Project**:
   ```hcl
   resource "google_project_iam_member" "cloudrun_vpc_access" {
     project = google_project.admin_project.project_id
     role    = "roles/vpcaccess.user"
     member  = "serviceAccount:service-${google_project.service_project.number}@serverless-robot-prod.iam.gserviceaccount.com"
   }
   ```

2. **Central Container Registry Pull Permission:**
   The Cloud Run Service Agent of the **Service Project** must have `roles/artifactregistry.reader` in the **Central Admin Project**:
   ```hcl
   resource "google_project_iam_member" "cloudrun_central_ar" {
     project = var.central_admin_project_id
     role    = "roles/artifactregistry.reader"
     member  = "serviceAccount:service-${google_project.service_project.number}@serverless-robot-prod.iam.gserviceaccount.com"
   }
   ```

3. **Workload Identity & Ephemeral Credentials:**
   Workload runtime service accounts (e.g., `<workload>-sa-<env>`) obtain short-lived OAuth 2.0 tokens from the metadata server. Long-lived exported JSON keys (`.json`) are blocked via organizational policy: `constraints/iam.disableServiceAccountKeyCreation`.

---

## 6. Zero-Trust Security Baseline

Every implementation of this framework must include the following security controls:

* **Domain Restricted Sharing (DRS):** Organization policy constraint `constraints/iam.allowedPolicyMemberDomains` restricts IAM grants exclusively to approved corporate customer/Google Cloud domains.
* **Customer-Managed Encryption Keys (CMEK):** Storage buckets, database instances, and BigQuery datasets must be encrypted using Cloud KMS keys (`AES-256-GCM`) with 90-day automatic key rotation.
* **Identity-Aware Proxy (IAP):** Endpoints validate corporate credentials and append the cryptographically signed `X-Goog-IAP-JWT-Assertion` header. Application backends verify the signature against Google's public JWKS endpoint.
* **Private Egress Enforced:** Compute containers do not receive external public IP addresses. All outbound traffic to Google APIs traverses Google's private internal fiber network via Private Google Access.

---

## 7. Promotion Workflow & CI/CD GitOps Lifecycle

```
[ Developer Commit ] ──► [ Feature Branch ]
                                │
                                ▼ (Automated Terraform Plan)
                       [ PR to `dev` Branch ] ──► [ Auto-Apply to DEV ]
                                                       │
                                                       ▼ (Smoke Tests & Evals Pass)
                                              [ PR to `stg` Branch ] ──► [ Auto-Apply to STG ]
                                                                              │
                                                                              ▼ (Security / Manual Approval)
                                                                     [ PR to `prod` Branch ] ──► [ Zero-Downtime PRD Apply ]
```

* **State Isolation:** Each environment repository maintains its own isolated remote GCS state bucket (`*-dev-tfstate`, `*-stg-tfstate`, `*-prod-tfstate`) with object versioning enabled. State locks prevent concurrent applies.
* **Keyless CI/CD:** GitHub Actions / Cloud Build authenticate to Google Cloud via **Workload Identity Federation (WIF)**, eliminating the need to store long-lived service account keys in repository secrets.

---

## 8. Reusable Scaffolding Checklist

When bootstrapping a new workload with this framework, execute these steps in order:

- [ ] **Step 1: Central Admin Setup**
  - [ ] Initialize `terraform-<workload>-central`.
  - [ ] Apply `folder.tf`, `project.tf`, `artifact_registry.tf`, `ncc_hub.tf`, `iam.tf`.
  - [ ] Export Hub ID, Artifact Registry repository URL, and Folder IDs.
- [ ] **Step 2: DEV Environment Setup**
  - [ ] Initialize `terraform-<workload>-dev`.
  - [ ] Configure `backend.tf` pointing to the DEV state bucket.
  - [ ] Apply Host Project resources (`project_admin.tf`, `vpc_network.tf`, `vpc_connector.tf`, `ncc_spoke.tf`).
  - [ ] Apply Service Project resources (`project_service.tf`, `iam.tf`, `storage.tf`, `cloud_run.tf`, `load_balancer_iap.tf`).
- [ ] **Step 3: STG & PRD Promotion**
  - [ ] Clone topology into `terraform-<workload>-stg` and `terraform-<workload>-prod`.
  - [ ] Update CIDR blocks according to the allocation matrix (`10.20.0.0/24` for STG, `10.30.0.0/24` for PRD).
  - [ ] Configure environment-specific scaling bounds (DEV: 0-3, STG: 0-5, PRD: 1-100).
  - [ ] Verify cross-project IAM grants (`roles/vpcaccess.user`, `roles/artifactregistry.reader`).
