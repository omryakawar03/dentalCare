variable "aws_region" {
  description = "AWS region for the EKS showcase."
  type        = string
  default     = "ap-south-1"
}

variable "project_name" {
  description = "Name prefix for cloud resources."
  type        = string
  default     = "devops-showcase"
}

variable "cluster_version" {
  description = "Optional EKS Kubernetes version. Leave null to use AWS default."
  type        = string
  default     = null
}

variable "cluster_public_access_cidrs" {
  description = "CIDR ranges allowed to reach the public EKS API endpoint. Use 0.0.0.0/0 only for short demos or GitHub-hosted runners."
  type        = list(string)
  default     = ["0.0.0.0/0"]
}

variable "node_instance_types" {
  description = "Instance types for the managed node group."
  type        = list(string)
  default     = ["c7i.large"]
}

variable "node_capacity_type" {
  description = "Use SPOT for low-cost demos or ON_DEMAND for production reliability."
  type        = string
  default     = "ON_DEMAND"

  validation {
    condition     = contains(["ON_DEMAND", "SPOT"], var.node_capacity_type)
    error_message = "node_capacity_type must be ON_DEMAND or SPOT."
  }
}

variable "desired_size" {
  description = "Desired number of worker nodes."
  type        = number
  default     = 1
}

variable "min_size" {
  description = "Minimum number of worker nodes."
  type        = number
  default     = 1
}

variable "max_size" {
  description = "Maximum number of worker nodes."
  type        = number
  default     = 2
}

variable "frontend_ecr_repository_name" {
  description = "ECR repository name for the frontend image. Leave empty to use project_name/frontend."
  type        = string
  default     = "frontend_repo"
}

variable "backend_ecr_repository_name" {
  description = "ECR repository name for the backend image. Leave empty to use project_name/backend."
  type        = string
  default     = "backend_repo"
}

variable "app_env_secret_name" {
  description = "AWS Secrets Manager secret name for app environment variables. Leave empty to use project_name/app/env."
  type        = string
  default     = ""
}

variable "ecr_force_delete" {
  description = "Allow Terraform destroy to delete ECR repositories even when images exist. Keep true for demos; use false for production."
  type        = bool
  default     = true
}

variable "secret_recovery_window_in_days" {
  description = "Secrets Manager recovery window. Use 0 for fast demo teardown; use 7 or more for production."
  type        = number
  default     = 0
}
