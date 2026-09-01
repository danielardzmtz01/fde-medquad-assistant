# iam.tf
# Runtime Service Account and Least-Privilege IAM Bindings

resource "google_service_account" "medquad_sa" {
  account_id   = "medquad-sa-${var.environment}"
  display_name = "MedQuAD Assistant Runtime SA (${var.environment})"
  project      = google_project.service_project.project_id
  depends_on   = [google_project_service.workload_services]
}

locals {
  runtime_roles = [
    "roles/aiplatform.user",
    "roles/discoveryengine.viewer",
    "roles/bigquery.dataEditor",
    "roles/bigquery.jobUser",
    "roles/secretmanager.secretAccessor",
    "roles/cloudtrace.agent",
    "roles/logging.logWriter",
    "roles/monitoring.metricWriter",
  ]
}

resource "google_project_iam_member" "medquad_sa_bindings" {
  for_each = toset(local.runtime_roles)
  project  = google_project.service_project.project_id
  role     = each.value
  member   = "serviceAccount:${google_service_account.medquad_sa.email}"
}
