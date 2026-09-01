# iam.tf
# Central CI/CD and Cloud Build IAM Configuration

resource "google_service_account" "cicd_sa" {
  account_id   = "medquad-cicd-sa"
  display_name = "MedQuAD Central CI/CD Automation Service Account"
  project      = google_project.central_admin_project.project_id
  depends_on   = [google_project_service.central_apis]
}

locals {
  cloudbuild_roles = [
    "roles/storage.admin",
    "roles/logging.logWriter",
    "roles/artifactregistry.writer",
  ]
}

resource "google_project_iam_member" "cloudbuild_compute_sa_roles" {
  for_each   = toset(local.cloudbuild_roles)
  project    = google_project.central_admin_project.project_id
  role       = each.value
  member     = "serviceAccount:${google_project.central_admin_project.number}-compute@developer.gserviceaccount.com"
  depends_on = [google_project_service.central_apis]
}

resource "google_project_iam_member" "cloudbuild_sa_roles" {
  for_each   = toset(local.cloudbuild_roles)
  project    = google_project.central_admin_project.project_id
  role       = each.value
  member     = "serviceAccount:${google_project.central_admin_project.number}@cloudbuild.gserviceaccount.com"
  depends_on = [google_project_service.central_apis]
}
