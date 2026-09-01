terraform {
  backend "gcs" {
    bucket = "terraform-medquad-state"
    prefix = "prd"
  }
}
