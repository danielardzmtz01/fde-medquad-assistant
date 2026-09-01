# artifact_registry.tf
# Central Docker Repository for container images

resource "google_artifact_registry_repository" "container_repo" {
  location      = var.region
  repository_id = "medquad-repo"
  description   = "Central Docker repository for MedQuAD container images"
  format        = "DOCKER"
  project       = google_project.central_admin_project.project_id
  depends_on    = [google_project_service.central_apis]

  labels = {
    environment = "central"
    managed_by  = "terraform"
  }
}
