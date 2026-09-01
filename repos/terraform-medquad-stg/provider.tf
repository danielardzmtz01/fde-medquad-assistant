# provider.tf
# Terraform and Google Provider configurations

terraform {
  required_version = ">= 1.5.0"
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 5.30"
    }
  }
}

provider "google" {
  region                 = var.region
  user_project_override = true
  billing_project        = var.service_project_id
}
