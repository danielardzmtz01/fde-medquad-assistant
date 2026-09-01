# storage.tf
# GCS Bucket for Grounding Corpus

resource "google_storage_bucket" "corpus_bucket" {
  name                        = "${google_project.service_project.project_id}-${var.environment}-medquad-corpus"
  location                    = var.region
  project                     = google_project.service_project.project_id
  force_destroy               = var.environment != "prd"
  uniform_bucket_level_access = true
  depends_on                  = [google_project_service.workload_services]

  versioning {
    enabled = true
  }

  labels = {
    environment = var.environment
    app         = "medquad-assistant"
    managed_by  = "terraform"
  }
}

resource "google_storage_bucket_iam_member" "sa_corpus_reader" {
  bucket     = google_storage_bucket.corpus_bucket.name
  role       = "roles/storage.objectViewer"
  member     = "serviceAccount:${google_service_account.medquad_sa.email}"
  depends_on = [google_storage_bucket.corpus_bucket]
}
