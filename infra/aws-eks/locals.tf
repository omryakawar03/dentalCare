locals {
  frontend_ecr_repository_name = var.frontend_ecr_repository_name != "" ? var.frontend_ecr_repository_name : "${var.project_name}/frontend"
  backend_ecr_repository_name  = var.backend_ecr_repository_name != "" ? var.backend_ecr_repository_name : "${var.project_name}/backend"
  app_env_secret_name          = var.app_env_secret_name != "" ? var.app_env_secret_name : "${var.project_name}/app/env"
  oidc_provider_host           = replace(aws_eks_cluster.this.identity[0].oidc[0].issuer, "https://", "")
}

