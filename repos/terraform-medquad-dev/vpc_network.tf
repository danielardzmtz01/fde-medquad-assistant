# vpc_network.tf
# Shared VPC Network and Subnet inside Admin Host Project

resource "google_compute_network" "admin_vpc" {
  name                    = "medquad-shared-vpc-${var.environment}"
  auto_create_subnetworks = false
  project                 = google_project.admin_project.project_id
  depends_on              = [google_compute_shared_vpc_host_project.host]
}

resource "google_compute_subnetwork" "admin_subnet" {
  name                     = "medquad-subnet-${var.environment}"
  ip_cidr_range            = var.subnet_cidr
  region                   = var.region
  network                  = google_compute_network.admin_vpc.id
  private_ip_google_access = true
  project                  = google_project.admin_project.project_id
}
