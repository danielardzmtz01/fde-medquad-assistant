# data.tf
# Read outputs directly from Central Terraform Remote State in GCS

data "terraform_remote_state" "central" {
  backend = "gcs"
  config = {
    bucket = var.state_bucket_name
    prefix = "central/static_infra"
  }
}
