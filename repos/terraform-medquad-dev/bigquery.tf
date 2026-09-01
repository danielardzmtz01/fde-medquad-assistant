# bigquery.tf
# BigQuery Telemetry Dataset & Partitioned Tables

resource "google_bigquery_dataset" "telemetry" {
  dataset_id                 = "medquad_telemetry_${var.environment}"
  friendly_name              = "MedQuAD Telemetry Dataset (${var.environment})"
  location                   = var.region
  project                    = google_project.service_project.project_id
  delete_contents_on_destroy = var.environment != "prd"
  depends_on                 = [google_project_service.workload_services]

  labels = {
    environment = var.environment
    app         = "medquad-assistant"
    managed_by  = "terraform"
  }
}

resource "google_bigquery_table" "token_usage" {
  dataset_id          = google_bigquery_dataset.telemetry.dataset_id
  table_id            = "token_usage_events"
  project             = google_project.service_project.project_id
  deletion_protection = var.environment == "prd"
  depends_on          = [google_bigquery_dataset.telemetry]

  time_partitioning {
    type  = "DAY"
    field = "timestamp"
  }

  schema = jsonencode([
    { name = "timestamp", type = "TIMESTAMP", mode = "REQUIRED" },
    { name = "trace_id", type = "STRING", mode = "REQUIRED" },
    { name = "session_id", type = "STRING", mode = "NULLABLE" },
    { name = "agent_name", type = "STRING", mode = "REQUIRED" },
    { name = "model_name", type = "STRING", mode = "REQUIRED" },
    { name = "input_tokens", type = "INT64", mode = "REQUIRED" },
    { name = "output_tokens", type = "INT64", mode = "REQUIRED" },
    { name = "cached_tokens", type = "INT64", mode = "REQUIRED" },
    { name = "estimated_cost_usd", type = "FLOAT64", mode = "NULLABLE" },
    { name = "latency_ms", type = "FLOAT64", mode = "REQUIRED" },
    { name = "status", type = "STRING", mode = "REQUIRED" }
  ])
}
