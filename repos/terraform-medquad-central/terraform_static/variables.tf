# terraform_static/variables.tf

variable "parent_resource_id" {
  type        = string
  description = "Parent resource (e.g. 'organizations/123456789012' o 'folders/123456789012')"
}

variable "root_folder_name" {
  type        = string
  description = "Display name for the root platform folder"
  default     = "MedQuAD-Platform"
}

variable "billing_account_id" {
  type        = string
  description = "GCP Billing Account ID (format: XXXXXX-XXXXXX-XXXXXX)"
}

variable "admin_project_id" {
  type        = string
  description = "GCP Project ID for Central Admin"
  default     = "drm-medquad-admin-central"
}

variable "region" {
  type        = string
  description = "Primary GCP Region"
  default     = "us-central1"
}
