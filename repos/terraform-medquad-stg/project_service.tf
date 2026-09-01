# project_service.tf
# Service Workload GCP Project and Workload APIs

resource "google_project" "service_project" {
  name                = "MedQuAD Service ${upper(var.environment)}"
  project_id          = var.service_project_id
  folder_id           = google_folder.env_folder.name
  billing_account     = var.billing_account_id
  auto_create_network = false

  labels = {
    environment = var.environment
    role        = "service-workload"
    app         = "medquad-assistant"
    managed_by  = "terraform"
  }
}

locals {
  service_apis = [
    "iam.googleapis.com",
    "cloudresourcemanager.googleapis.com",
    "serviceusage.googleapis.com",
    "aiplatform.googleapis.com",
    "discoveryengine.googleapis.com",
    "run.googleapis.com",
    "storage.googleapis.com",
    "bigquery.googleapis.com",
    "secretmanager.googleapis.com",
    "cloudtrace.googleapis.com",
    "logging.googleapis.com",
    "monitoring.googleapis.com",
    "compute.googleapis.com",
    "vpcaccess.googleapis.com",
  ]
}

resource "google_project_service" "workload_services" {
  for_each                   = toset(local.service_apis)
  project                    = google_project.service_project.project_id
  service                    = each.value
  disable_dependent_services = false
  disable_on_destroy         = false
}
