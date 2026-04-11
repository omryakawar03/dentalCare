output "cluster_name" {
  description = "EKS cluster name."
  value       = aws_eks_cluster.this.name
}

output "cluster_endpoint" {
  description = "EKS API endpoint."
  value       = aws_eks_cluster.this.endpoint
}

output "node_group_name" {
  description = "Managed node group name."
  value       = aws_eks_node_group.spot.node_group_name
}

output "update_kubeconfig_command" {
  description = "Command to configure kubectl for this cluster."
  value       = "aws eks update-kubeconfig --region ${var.aws_region} --name ${aws_eks_cluster.this.name}"
}

output "frontend_ecr_repository_url" {
  description = "Frontend ECR repository URL."
  value       = aws_ecr_repository.frontend.repository_url
}

output "backend_ecr_repository_url" {
  description = "Backend ECR repository URL."
  value       = aws_ecr_repository.backend.repository_url
}

output "app_env_secret_name" {
  description = "AWS Secrets Manager secret name for app environment variables."
  value       = aws_secretsmanager_secret.app_env.name
}

output "external_secrets_role_arn" {
  description = "IAM role ARN for External Secrets Operator service account."
  value       = aws_iam_role.external_secrets.arn
}
