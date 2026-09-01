# folder.tf
# Main Root Folder directly under Organization

resource "google_folder" "root_medquad_folder" {
  display_name = var.root_folder_name
  parent       = var.parent_resource_id # e.g. "organizations/123456789012"
}
