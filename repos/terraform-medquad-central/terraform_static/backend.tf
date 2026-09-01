# terraform_static/backend.tf

terraform {
  backend "gcs" {
    bucket = "terraform-medquad-state"
    prefix = "central/static_infra"
  }
}
