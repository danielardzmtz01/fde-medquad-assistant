# ncc_hub.tf
# Network Connectivity Center (NCC) Central Hub

resource "google_network_connectivity_hub" "central_hub" {
  name        = "medquad-ncc-hub-central"
  description = "Central Network Connectivity Center Hub connecting all environment spokes"
  project     = google_project.central_admin_project.project_id
  depends_on  = [google_project_service.central_apis]

  labels = {
    role       = "central-hub"
    managed_by = "terraform"
  }
}
