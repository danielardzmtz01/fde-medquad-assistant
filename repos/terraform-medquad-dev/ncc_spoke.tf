# ncc_spoke.tf
# NCC VPC Spoke Attachment linking Shared VPC to Central NCC Hub (fetched dynamically from central state)

resource "google_network_connectivity_spoke" "vpc_spoke" {
  name        = "medquad-spoke-${var.environment}"
  location    = "global"
  description = "NCC VPC Spoke attaching ${var.environment} Shared VPC to Central NCC Hub"
  hub         = data.terraform_remote_state.central.outputs.ncc_hub_id
  project     = google_project.admin_project.project_id

  linked_vpc_network {
    uri = google_compute_network.admin_vpc.self_link
  }

  labels = {
    environment = var.environment
    managed_by  = "terraform"
    role        = "vpc-spoke"
  }
}
