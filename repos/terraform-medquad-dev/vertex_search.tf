# vertex_search.tf
# Vertex AI Search (GEAP) Data Store & Search Engine

resource "google_discovery_engine_data_store" "medquad_datastore" {
  location                    = "global"
  data_store_id               = "medquad-datastore-${var.environment}"
  display_name                = "MedQuAD NIH Clinical Corpus (${var.environment})"
  industry_vertical           = "GENERIC"
  content_config              = "CONTENT_REQUIRED"
  solution_types              = ["SOLUTION_TYPE_SEARCH"]
  create_advanced_site_search = false
  project                     = google_project.service_project.project_id
  depends_on                  = [google_project_service.workload_services]

  lifecycle {
    ignore_changes = [
      document_processing_config,
    ]
  }
}

resource "google_discovery_engine_search_engine" "medquad_engine" {
  engine_id         = "medquad-search-engine-${var.environment}"
  collection_id     = "default_collection"
  location          = "global"
  display_name      = "MedQuAD Search Engine (${var.environment})"
  data_store_ids    = [google_discovery_engine_data_store.medquad_datastore.data_store_id]
  industry_vertical = "GENERIC"
  project           = google_project.service_project.project_id

  search_engine_config {
    search_tier = "SEARCH_TIER_ENTERPRISE"
  }
}
