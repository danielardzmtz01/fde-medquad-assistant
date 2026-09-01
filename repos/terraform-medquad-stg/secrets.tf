# secrets.tf
# Secret Manager for AI Safety & Guardrails API Keys

resource "google_secret_manager_secret" "model_armor_api_key" {
  secret_id  = "medquad-model-armor-api-key-${var.environment}"
  project    = google_project.service_project.project_id
  depends_on = [google_project_service.workload_services]

  replication {
    auto {}
  }
}
