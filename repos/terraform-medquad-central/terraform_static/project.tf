# project.tf
# Central Admin Project and Foundation APIs enablement

resource "google_project" "central_admin_project" {
  name                = "MedQuAD Central Admin"
  project_id          = var.admin_project_id
  folder_id           = google_folder.root_medquad_folder.name
  billing_account     = var.billing_account_id
  auto_create_network = false

  labels = {
    role        = "central-admin"
    app         = "medquad-assistant"
    managed_by  = "terraform"
    environment = "central"
  }
}

resource "google_project_service" "central_apis" {
  for_each = toset([
    "cloudresourcemanager.googleapis.com",
    "serviceusage.googleapis.com",
    "artifactregistry.googleapis.com",
    "cloudbuild.googleapis.com",
    "storage.googleapis.com",
    "iam.googleapis.com",
    "logging.googleapis.com",
    "monitoring.googleapis.com",
    "compute.googleapis.com",
    "networkconnectivity.googleapis.com",
  ])
  project                    = google_project.central_admin_project.project_id
  service                    = each.value
  disable_dependent_services = false
  disable_on_destroy         = false
}
