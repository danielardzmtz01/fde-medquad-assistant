# cloud_run.tf
# Cloud Run v2 Backend Service with Serverless VPC Access

# 1. Grant Cloud Run Service Agent access to pull images from Central Artifact Registry
resource "google_artifact_registry_repository_iam_member" "cloud_run_agent_ar_reader" {
  project    = data.terraform_remote_state.central.outputs.admin_project_id
  location   = var.region
  repository = "medquad-repo"
  role       = "roles/artifactregistry.reader"
  member     = "serviceAccount:service-${google_project.service_project.number}@serverless-robot-prod.iam.gserviceaccount.com"
}

# 2. Cloud Run Backend Service
resource "google_cloud_run_v2_service" "medquad_backend" {
  name       = "medquad-assistant-${var.environment}"
  location   = var.region
  project    = google_project.service_project.project_id
  ingress    = "INGRESS_TRAFFIC_ALL"
  depends_on = [
    google_project_service.workload_services,
    google_artifact_registry_repository_iam_member.cloud_run_agent_ar_reader,
    google_project_iam_member.cloud_run_vpc_access_user,
    google_project_iam_member.cloud_services_network_user,
  ]

  template {
    service_account = google_service_account.medquad_sa.email

    scaling {
      min_instance_count = var.min_instances
      max_instance_count = var.max_instances
    }

    vpc_access {
      connector = google_vpc_access_connector.serverless_conn.id
      egress    = "PRIVATE_RANGES_ONLY"
    }

    containers {
      image = var.container_image

      resources {
        limits = {
          cpu    = var.cpu_limit
          memory = var.memory_limit
        }
      }

      env {
        name  = "PROJECT_ID"
        value = google_project.service_project.project_id
      }
      env {
        name  = "ENVIRONMENT"
        value = var.environment
      }
      env {
        name  = "LOCATION"
        value = var.region
      }
      env {
        name  = "DATA_STORE_ID"
        value = google_discovery_engine_data_store.medquad_datastore.data_store_id
      }
      env {
        name  = "BQ_DATASET_ID"
        value = google_bigquery_dataset.telemetry.dataset_id
      }
      env {
        name  = "CORPUS_BUCKET_NAME"
        value = google_storage_bucket.corpus_bucket.name
      }
      env {
        name  = "MODEL_ARMOR_ENABLED"
        value = "true"
      }

      ports {
        container_port = 8080
      }

      startup_probe {
        initial_delay_seconds = 5
        period_seconds        = 10
        http_get {
          path = "/"
          port = 8080
        }
      }

      liveness_probe {
        initial_delay_seconds = 10
        period_seconds        = 15
        http_get {
          path = "/"
          port = 8080
        }
      }
    }
  }

  traffic {
    type    = "TRAFFIC_TARGET_ALLOCATION_TYPE_LATEST"
    percent = 100
  }
}

# 3. Secure Invoker IAM Bindings compliant with Domain Restricted Sharing (DRS) Org Policy
resource "google_cloud_run_v2_service_iam_member" "user_invoker_access" {
  project  = google_project.service_project.project_id
  location = var.region
  name     = google_cloud_run_v2_service.medquad_backend.name
  role     = "roles/run.invoker"
  member   = "user:${data.google_client_openid_userinfo.current_user.email}"
}

resource "google_cloud_run_v2_service_iam_member" "cicd_invoker_access" {
  project  = google_project.service_project.project_id
  location = var.region
  name     = google_cloud_run_v2_service.medquad_backend.name
  role     = "roles/run.invoker"
  member   = "serviceAccount:${data.terraform_remote_state.central.outputs.cicd_service_account}"
}
