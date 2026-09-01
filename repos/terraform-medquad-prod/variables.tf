# variables.tf

variable "state_bucket_name" {
  type        = string
  description = "Name of central GCS state bucket"
  default     = "terraform-medquad-state"
}

variable "billing_account_id" {
  type        = string
  description = "GCP Billing Account ID"
}

variable "environment" {
  type        = string
  description = "Environment identifier"
  default     = "dev"
}

variable "region" {
  type        = string
  description = "GCP Region"
  default     = "us-central1"
}

variable "admin_project_id" {
  type        = string
  description = "Admin / Host GCP Project ID"
  default     = "drm-medquad-admin-dev"
}

variable "service_project_id" {
  type        = string
  description = "Service / Workload GCP Project ID"
  default     = "drm-medquad-service-dev"
}

variable "subnet_cidr" {
  type        = string
  description = "CIDR block for Shared VPC subnet"
  default     = "10.10.0.0/24"
}

variable "connector_cidr" {
  type        = string
  description = "CIDR block (/28) for Serverless VPC Access Connector"
  default     = "10.10.1.0/28"
}

variable "min_connector_instances" {
  type        = number
  description = "Min instances for VPC Connector"
  default     = 2
}

variable "max_connector_instances" {
  type        = number
  description = "Max instances for VPC Connector"
  default     = 3
}

variable "container_image" {
  type        = string
  description = "Container image URI for Cloud Run"
  default     = "us-docker.pkg.dev/cloudrun/container/hello"
}

variable "min_instances" {
  type        = number
  description = "Min Cloud Run instances"
  default     = 0
}

variable "max_instances" {
  type        = number
  description = "Max Cloud Run instances"
  default     = 3
}

variable "cpu_limit" {
  type        = string
  default     = "2"
}

variable "memory_limit" {
  type        = string
  default     = "2Gi"
}

variable "allow_unauthenticated" {
  type        = bool
  default     = true
}
