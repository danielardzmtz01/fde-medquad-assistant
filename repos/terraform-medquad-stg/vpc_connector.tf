# vpc_connector.tf
# Serverless VPC Access Connector inside Shared VPC

resource "google_vpc_access_connector" "serverless_conn" {
  name          = "medquad-conn-${var.environment}"
  region        = var.region
  ip_cidr_range = var.connector_cidr
  network       = google_compute_network.admin_vpc.name
  project       = google_project.admin_project.project_id
  min_instances = var.min_connector_instances
  max_instances = var.max_connector_instances
  depends_on    = [google_compute_network.admin_vpc]
}

# Grant Cloud Run Service Agent of Service Project permission to use the VPC Connector in Host Project
resource "google_project_iam_member" "cloud_run_vpc_access_user" {
  project = google_project.admin_project.project_id
  role    = "roles/vpcaccess.user"
  member  = "serviceAccount:service-${google_project.service_project.number}@serverless-robot-prod.iam.gserviceaccount.com"
}

# Grant Google APIs Service Agent networkUser permission on Host Project
resource "google_project_iam_member" "cloud_services_network_user" {
  project = google_project.admin_project.project_id
  role    = "roles/compute.networkUser"
  member  = "serviceAccount:${google_project.service_project.number}@cloudservices.gserviceaccount.com"
}
