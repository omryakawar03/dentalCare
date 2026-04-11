# AWS EKS Terraform

This creates a cost-conscious EKS showcase:

- Managed EKS control plane
- One small managed node group
- ECR repositories for frontend and backend images
- AWS Secrets Manager secret for app envs
- IAM role for External Secrets Operator
- Spot capacity by default for demo cost reduction
- Fast demo teardown defaults for ECR and Secrets Manager
- Default VPC and subnets for fast setup
- Control plane logs enabled for a stronger DevOps story

## Usage

```bash
cp terraform.tfvars.example terraform.tfvars
nano terraform.tfvars
terraform init
terraform apply
aws eks update-kubeconfig --region us-east-1 --name devops-showcase
```

Set the first app secret value after Terraform creates the secret metadata:

```bash
AWS_SECRET_NAME=$(terraform output -raw app_env_secret_name)
aws secretsmanager put-secret-value \
  --secret-id "$AWS_SECRET_NAME" \
  --secret-string '{"MONGODB_URI":"mongodb+srv://..."}'
```

Get the ECR URLs:

```bash
terraform output -raw frontend_ecr_repository_url
terraform output -raw backend_ecr_repository_url
```

For a production client, change:

- `node_capacity_type` to `ON_DEMAND`
- `cluster_public_access_cidrs` to your office/VPN CIDR
- `node_instance_types` to a right-sized instance family
- `desired_size` and `min_size` to at least `2`

Destroy the demo when finished:

```bash
terraform destroy
```
