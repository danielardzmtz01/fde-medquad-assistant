# terraform_static/outputs.tf

output "root_medquad_folder_id" {
  value       = google_folder.root_medquad_folder.name
  description = "Resource Name of the MedQuAD Root Folder"
}

output "admin_project_id" {
  value       = google_project.central_admin_project.project_id
  description = "Project ID of Central Admin"
}

output "admin_project_number" {
  value       = google_project.central_admin_project.number
  description = "Project Number of Central Admin"
}

output "ncc_hub_id" {
  value       = google_network_connectivity_hub.central_hub.id
  description = "Central Network Connectivity Center (NCC) Hub ID"
}

output "artifact_registry_repo" {
  value       = "${var.region}-docker.pkg.dev/${google_project.central_admin_project.project_id}/${google_artifact_registry_repository.container_repo.repository_id}"
  description = "Central Artifact Registry Docker repo URI"
}

output "cicd_service_account" {
  value       = google_service_account.cicd_sa.email
  description = "Central CI/CD Service Account Email"
}
