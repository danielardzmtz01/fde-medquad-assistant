# project_admin.tf
# Admin Host GCP Project and Foundation APIs

resource "google_project" "admin_project" {
  name                = "MedQuAD Admin ${upper(var.environment)}"
  project_id          = var.admin_project_id
  folder_id           = google_folder.env_folder.name
  billing_account     = var.billing_account_id
  auto_create_network = false

  labels = {
    environment = var.environment
    role        = "admin-host"
    app         = "medquad-assistant"
    managed_by  = "terraform"
  }
}

locals {
  admin_apis = [
    "iam.googleapis.com",
    "cloudresourcemanager.googleapis.com",
    "serviceusage.googleapis.com",
    "compute.googleapis.com",
    "vpcaccess.googleapis.com",
    "networkconnectivity.googleapis.com",
    "logging.googleapis.com",
    "monitoring.googleapis.com",
  ]
}

resource "google_project_service" "admin_services" {
  for_each                   = toset(local.admin_apis)
  project                    = google_project.admin_project.project_id
  service                    = each.value
  disable_dependent_services = false
  disable_on_destroy         = false
}
