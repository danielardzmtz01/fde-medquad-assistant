# folder.tf
# Subfolder for the environment under Root MedQuAD Folder (fetched dynamically from central state)

resource "google_folder" "env_folder" {
  display_name = upper(var.environment)
  parent       = data.terraform_remote_state.central.outputs.root_medquad_folder_id
}
