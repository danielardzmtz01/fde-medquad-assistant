# outputs.tf

output "env_folder_id" {
  value       = google_folder.env_folder.name
  description = "Resource Name of the Environment Subfolder"
}

output "admin_project_id" {
  value       = google_project.admin_project.project_id
  description = "Admin Project ID"
}

output "admin_project_number" {
  value       = google_project.admin_project.number
  description = "Admin Project Number"
}

output "service_project_id" {
  value       = google_project.service_project.project_id
  description = "Service Workload Project ID"
}

output "service_project_number" {
  value       = google_project.service_project.number
  description = "Service Workload Project Number"
}

output "shared_vpc_id" {
  value       = google_compute_network.admin_vpc.id
  description = "Shared VPC Network ID"
}

output "shared_subnet_id" {
  value       = google_compute_subnetwork.admin_subnet.id
  description = "Shared Subnet ID"
}

output "connector_id" {
  value       = google_vpc_access_connector.serverless_conn.id
  description = "Serverless VPC Access Connector ID"
}

output "ncc_spoke_id" {
  value       = google_network_connectivity_spoke.vpc_spoke.id
  description = "NCC VPC Spoke ID attached to Central Hub"
}

output "cloud_run_url" {
  value       = google_cloud_run_v2_service.medquad_backend.uri
  description = "URL of deployed Cloud Run backend service"
}

output "runtime_service_account" {
  value       = google_service_account.medquad_sa.email
  description = "Email of MedQuAD Runtime Service Account"
}

output "corpus_bucket_name" {
  value       = google_storage_bucket.corpus_bucket.name
  description = "Name of Grounding Corpus GCS Bucket"
}

output "datastore_id" {
  value       = google_discovery_engine_data_store.medquad_datastore.data_store_id
  description = "Vertex AI Search Data Store ID"
}

output "search_engine_id" {
  value       = google_discovery_engine_search_engine.medquad_engine.engine_id
  description = "Vertex AI Search Engine ID"
}

output "telemetry_dataset_id" {
  value       = google_bigquery_dataset.telemetry.dataset_id
  description = "BigQuery Telemetry Dataset ID"
}

output "load_balancer_ip" {
  value       = google_compute_global_address.medquad_global_ip.address
  description = "Global Anycast Static IPv4 Address for Cloud Load Balancer"
}

output "custom_domain_url" {
  value       = "https://${var.custom_domain_name}"
  description = "Official HTTPS Custom Domain URL for End Users"
}

