# shared_vpc.tf
# Shared VPC Host, IAM permissions, and Service Project Attachment

data "google_client_openid_userinfo" "current_user" {}

# Automatically grant Compute Shared VPC Admin role to the user and CI/CD SA on the environment folder
resource "google_folder_iam_member" "env_folder_xpn_admin_user" {
  folder = google_folder.env_folder.name
  role   = "roles/compute.xpnAdmin"
  member = "user:${data.google_client_openid_userinfo.current_user.email}"
}

resource "google_folder_iam_member" "env_folder_xpn_admin_cicd" {
  folder = google_folder.env_folder.name
  role   = "roles/compute.xpnAdmin"
  member = "serviceAccount:${data.terraform_remote_state.central.outputs.cicd_service_account}"
}

# Automatically grant on root folder as well
resource "google_folder_iam_member" "root_folder_xpn_admin_user" {
  folder = data.terraform_remote_state.central.outputs.root_medquad_folder_id
  role   = "roles/compute.xpnAdmin"
  member = "user:${data.google_client_openid_userinfo.current_user.email}"
}

resource "google_folder_iam_member" "root_folder_xpn_admin_cicd" {
  folder = data.terraform_remote_state.central.outputs.root_medquad_folder_id
  role   = "roles/compute.xpnAdmin"
  member = "serviceAccount:${data.terraform_remote_state.central.outputs.cicd_service_account}"
}

resource "google_compute_shared_vpc_host_project" "host" {
  project = google_project.admin_project.project_id
  depends_on = [
    google_project_service.admin_services,
    google_folder_iam_member.env_folder_xpn_admin_user,
    google_folder_iam_member.env_folder_xpn_admin_cicd,
    google_folder_iam_member.root_folder_xpn_admin_user,
    google_folder_iam_member.root_folder_xpn_admin_cicd,
  ]
}

resource "google_compute_shared_vpc_service_project" "service_attachment" {
  host_project    = google_project.admin_project.project_id
  service_project = google_project.service_project.project_id
  depends_on = [
    google_compute_shared_vpc_host_project.host,
    google_project_service.workload_services,
  ]
}
