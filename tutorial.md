# EKS DevOps Showcase Tutorial

This tutorial shows how to deploy a Dockerized frontend and backend microservice app to Amazon EKS using a Linux VM as the DevOps workstation.

The goal is to create a strong Upwork portfolio project in 2 days:

- AWS EKS managed Kubernetes
- Amazon ECR image storage
- AWS Secrets Manager env storage
- Terraform infrastructure
- Helm application deployment
- GitHub Actions CI/CD
- MongoDB Atlas database
- NGINX ingress controller
- Cost-conscious demo sizing
- Clear screenshots and proposal copy for Upwork

## 1. Project Story

Use this positioning:

> I deployed a Dockerized frontend/backend microservice app to Amazon EKS using Terraform, Amazon ECR, AWS Secrets Manager, External Secrets Operator, Helm, GitHub Actions, MongoDB Atlas, ingress-nginx, health checks, resource limits, rollback support, and cost optimization.

This sells better than "I deployed Docker containers" because clients search for full DevOps outcomes:

- Cloud setup
- Kubernetes deployment
- CI/CD automation
- Infrastructure as Code
- Database connectivity
- Monitoring-ready Kubernetes manifests
- Cost optimization
- Documentation and handover

## 2. Architecture

```mermaid
flowchart LR
    Dev["Linux VM DevOps workstation"] --> TF["Terraform"]
    TF --> EKS["Amazon EKS"]
    TF --> ECR["Amazon ECR"]
    TF --> SM["AWS Secrets Manager"]
    Dev --> Helm["Helm deploy"]
    Dev --> ECR
    Helm --> EKS
    GH["GitHub Actions"] --> EKS
    EKS --> NGINX["ingress-nginx LoadBalancer"]
    EKS --> ESO["External Secrets Operator"]
    ESO --> SM
    NGINX --> FE["Frontend pod"]
    FE --> BE["Backend service"]
    BE --> Atlas["MongoDB Atlas"]
```

## 3. Linux VM Requirements

Use your Linux VM as the workstation. Install these tools:

```bash
git --version
docker --version
aws --version
terraform version
helm version
kubectl version --client
```

Then run the project checker:

```bash
chmod +x scripts/*.sh
./scripts/check-prereqs.sh
```

Expected result: all tools show `[OK]`.

## 4. AWS Setup

Configure AWS credentials on the Linux VM:

```bash
aws configure
```

Use:

- AWS Access Key ID
- AWS Secret Access Key
- Default region, for example `us-east-1`
- Default output format, for example `json`

Confirm access:

```bash
aws sts get-caller-identity
```

## 5. MongoDB Atlas Setup

Use MongoDB Atlas as the managed database.

For a fast demo:

1. Create or use an Atlas cluster.
2. Create a database user.
3. Copy the connection string.
4. Add a Network Access rule.

For the quickest demo, you can temporarily allow:

```text
0.0.0.0/0
```

For a better production story, say this:

> For demo speed I used a temporary broad Atlas network rule, then documented the production hardening step: restrict Atlas access to the application egress path and rotate credentials after delivery.

Do not commit the MongoDB URI to Git.

## 6. Local Docker Smoke Test

Copy the environment template:

```bash
cp .env.example .env
nano .env
```

Set:

```env
FRONTEND_IMAGE=123456789012.dkr.ecr.us-east-1.amazonaws.com/devops-showcase/frontend:latest
BACKEND_IMAGE=123456789012.dkr.ecr.us-east-1.amazonaws.com/devops-showcase/backend:latest
MONGODB_URI=mongodb+srv://user:password@cluster.example.mongodb.net/app?retryWrites=true&w=majority
```

Run:

```bash
docker compose up -d
docker compose ps
```

Optional logs:

```bash
docker compose logs -f backend
```

Stop local containers:

```bash
docker compose down
```

## 7. Create EKS With Terraform

Go to the EKS Terraform folder:

```bash
cd infra/aws-eks
cp terraform.tfvars.example terraform.tfvars
nano terraform.tfvars
```

Example demo config:

```hcl
aws_region                  = "us-east-1"
project_name                = "devops-showcase"
cluster_version             = null
cluster_public_access_cidrs = ["0.0.0.0/0"]
node_instance_types         = ["t3.small"]
node_capacity_type          = "SPOT"
desired_size                = 1
min_size                    = 1
max_size                    = 2
```

Why this config:

- `SPOT` keeps demo worker-node cost lower.
- `desired_size = 1` keeps the demo small.
- `max_size = 2` shows scaling thinking without overbuilding.
- `cluster_public_access_cidrs = ["0.0.0.0/0"]` is convenient for a short demo, but should be restricted for production.

Initialize and apply:

```bash
terraform init
terraform validate
terraform plan
terraform apply
```

Configure kubectl:

```bash
aws eks update-kubeconfig --region us-east-1 --name devops-showcase
kubectl get nodes
```

Expected result: one EKS node is `Ready`.

Capture Terraform outputs:

```bash
FRONTEND_ECR_URL=$(terraform output -raw frontend_ecr_repository_url)
BACKEND_ECR_URL=$(terraform output -raw backend_ecr_repository_url)
AWS_SECRET_NAME=$(terraform output -raw app_env_secret_name)
EXTERNAL_SECRETS_ROLE_ARN=$(terraform output -raw external_secrets_role_arn)
```

## 8. Store Envs In AWS Secrets Manager

Store runtime envs in AWS Secrets Manager. For this app, the key we need is `MONGODB_URI`.

```bash
aws secretsmanager put-secret-value \
  --secret-id "$AWS_SECRET_NAME" \
  --secret-string '{"MONGODB_URI":"mongodb+srv://user:password@cluster.example.mongodb.net/app?retryWrites=true&w=majority"}'
```

Why this is better:

- The MongoDB URI is not stored in Git.
- The MongoDB URI is not stored in GitHub Actions secrets.
- AWS Secrets Manager becomes the source of truth.
- External Secrets Operator syncs the value into Kubernetes.

## 9. Push Images To Amazon ECR

If your frontend and backend Docker images already exist on the Linux VM, retag and push them to ECR:

```bash
IMAGE_TAG=demo
cd ../..

./scripts/retag-push-ecr.sh \
  --frontend-local-image "local-frontend:latest" \
  --backend-local-image "local-backend:latest" \
  --frontend-ecr-url "$FRONTEND_ECR_URL" \
  --backend-ecr-url "$BACKEND_ECR_URL" \
  --tag "$IMAGE_TAG" \
  --aws-region us-east-1
```

If you need to build images first, use your app folders:

```bash
docker build -t local-frontend:latest ./frontend
docker build -t local-backend:latest ./backend
```

Then run the ECR push script above.

## 10. Deploy The App To EKS

Run this from the repo root:

Deploy the app:

```bash
./scripts/deploy.sh \
  --namespace showcase \
  --frontend-image "$FRONTEND_ECR_URL:$IMAGE_TAG" \
  --backend-image "$BACKEND_ECR_URL:$IMAGE_TAG" \
  --cluster-name devops-showcase \
  --aws-region us-east-1 \
  --aws-secret-name "$AWS_SECRET_NAME" \
  --host app.example.com \
  --install-ingress-controller \
  --install-external-secrets \
  --external-secrets-role-arn "$EXTERNAL_SECRETS_ROLE_ARN"
```

What this script does:

- Updates kubeconfig for EKS if `--cluster-name` is provided.
- Installs or updates ingress-nginx.
- Installs or updates External Secrets Operator.
- Creates the `showcase` namespace.
- Creates an ExternalSecret that syncs envs from AWS Secrets Manager.
- Deploys the frontend and backend with Helm.
- Waits for backend and frontend rollout status.

## 11. Verify Deployment

Check pods:

```bash
kubectl -n showcase get pods
```

Check services:

```bash
kubectl -n showcase get svc
kubectl -n ingress-nginx get svc
```

Get the public load balancer:

```bash
kubectl -n ingress-nginx get svc ingress-nginx-controller
```

Check Helm release:

```bash
helm -n showcase list
helm -n showcase history showcase
```

Check rollout:

```bash
kubectl -n showcase rollout status deployment/showcase-microservice-showcase-backend
kubectl -n showcase rollout status deployment/showcase-microservice-showcase-frontend
```

Rollback example:

```bash
helm -n showcase rollback showcase 1
```

## 12. GitHub Actions Setup

In GitHub repository settings, add these secrets:

```text
AWS_ACCESS_KEY_ID
AWS_SECRET_ACCESS_KEY
```

For the fastest demo, use AWS credentials from the same IAM principal that created the EKS cluster with Terraform. If you use a different IAM user or role for GitHub Actions, add an EKS access entry for that principal before running the workflow.

Add these repository variables:

```text
AWS_REGION=us-east-1
EKS_CLUSTER_NAME=devops-showcase
AWS_SECRET_NAME=devops-showcase/app/env
EXTERNAL_SECRETS_ROLE_ARN=arn:aws:iam::123456789012:role/devops-showcase-external-secrets
```

Then run the workflow:

```text
Actions -> Deploy Existing Images -> Run workflow
```

Inputs:

```text
frontend_image = 123456789012.dkr.ecr.us-east-1.amazonaws.com/devops-showcase/frontend:demo
backend_image  = 123456789012.dkr.ecr.us-east-1.amazonaws.com/devops-showcase/backend:demo
host_name      = app.example.com
```

Use the real ECR image URLs from Terraform output for `frontend_image` and `backend_image`.

## 13. Screenshots To Capture For Upwork

Capture these screenshots:

- Terraform apply success
- EKS cluster in AWS console
- EKS managed node group
- `kubectl get nodes`
- `kubectl -n showcase get pods`
- `helm -n showcase history showcase`
- GitHub Actions deployment success
- ECR frontend and backend repositories
- AWS Secrets Manager app env secret
- External Secrets Operator pods
- MongoDB Atlas cluster connected
- Browser showing frontend
- Backend health endpoint if your app has one
- Cost optimization notes from `COST_OPTIMIZATION.md`

Name the portfolio project:

```text
Amazon EKS DevOps Deployment for Docker Microservices With ECR, Secrets Manager, Terraform, Helm, CI/CD, and MongoDB Atlas
```

## 14. Cost Optimization Notes

Say this clearly in the portfolio:

> I used EKS because it is client-recognized managed Kubernetes, then controlled demo cost with one small Spot node group, resource requests/limits, one replica per service, and a documented destroy process after the demo.

Important cost controls:

- Destroy the EKS demo when not presenting it.
- Use one small Spot node group for demo.
- Store images in ECR with lifecycle policies.
- Store envs in AWS Secrets Manager instead of GitHub or Helm values.
- Use On-Demand or mixed nodes for production.
- Use MongoDB Atlas shared/free tier for demo if the app fits.
- Add AWS Budgets for client production setups.
- Use requests and limits in Kubernetes.
- Scale replicas only when testing or when traffic requires it.

Destroy the EKS demo:

```bash
cd infra/aws-eks
terraform destroy
```

## 15. Upwork Project Catalog Post

Use this as your Upwork Project Catalog title:

```text
I will deploy your Docker app to AWS EKS with ECR, Secrets Manager, Terraform, Helm, and CI/CD
```

Use this description:

```text
I will deploy your Dockerized frontend/backend application to Amazon EKS using a production-style DevOps workflow.

You will get Terraform infrastructure, Amazon ECR image storage, AWS Secrets Manager environment handling, External Secrets Operator integration, Kubernetes deployment with Helm, GitHub Actions CI/CD, MongoDB Atlas connection setup, NGINX ingress, health-check ready manifests, resource limits, rollback commands, and a short cost optimization report.

This is best for startups or small teams that already have Docker images but need a reliable AWS Kubernetes deployment without overbuilding the first version.

What I can deliver:
- Amazon EKS cluster setup with Terraform
- Amazon ECR repositories for frontend and backend images
- AWS Secrets Manager setup for app envs
- External Secrets Operator integration
- Managed node group configuration
- Helm chart for frontend and backend
- GitHub Actions deployment workflow
- MongoDB Atlas connection handling through AWS Secrets Manager
- NGINX ingress controller setup
- Kubernetes resource requests and limits
- Rollout and rollback commands
- Deployment documentation
- Cost optimization notes and production upgrade roadmap

Before starting, I need:
- Frontend Docker image
- Backend Docker image
- App ports and health endpoint path
- MongoDB Atlas URI or database access details
- AWS account access or temporary deployment credentials
- Domain or test hostname if ingress is required
```

Suggested packages:

```text
Starter: EKS deployment review and Helm chart cleanup
Delivery: 1 to 2 days

Standard: EKS deployment with Terraform, ECR, Secrets Manager, Helm, and manual deploy docs
Delivery: 2 to 3 days

Advanced: EKS deployment with Terraform, ECR, Secrets Manager, External Secrets Operator, Helm, GitHub Actions CI/CD, ingress, rollback docs, and cost optimization report
Delivery: 3 to 5 days
```

Do not promise full production high availability in the cheap starter tier. Say "production-style" or "production-ready foundation" unless you are also doing private networking, multi-AZ nodes, backups, monitoring, alerting, and security hardening.

## 16. Upwork Tags And Keywords

Use tags like:

```text
DevOps
AWS
Amazon EKS
Amazon ECR
AWS Secrets Manager
Kubernetes
Docker
Terraform
Helm
GitHub Actions
CI/CD
MongoDB Atlas
External Secrets Operator
NGINX
Cloud Infrastructure
Cloud Cost Optimization
Linux
Bash
Microservices
```

Use keyword phrases in your profile and proposals:

```text
AWS EKS deployment
Amazon ECR deployment
AWS Secrets Manager Kubernetes
Docker to Kubernetes
Terraform infrastructure
Helm chart deployment
GitHub Actions CI/CD
MongoDB Atlas Kubernetes
Kubernetes cost optimization
DevOps for startup MVP
EKS rollback and deployment automation
```

## 17. Fast Client Tips

Use this plan for the next 2 days:

Day 1:

- Finish the EKS deployment.
- Capture screenshots.
- Record a 60 to 90 second Loom-style walkthrough.
- Publish one Upwork Project Catalog offer.
- Add the project to your Upwork portfolio.

Day 2:

- Apply to 20 to 30 small DevOps jobs.
- Target jobs where the client already says Docker, AWS, Kubernetes, CI/CD, deployment, or Terraform.
- Send short custom proposals, not long generic messages.
- Offer a fast audit first, then upsell the full deployment.
- Reply quickly when clients message.

Proposal template:

```text
Hi, I can help with this.

I recently built a similar AWS EKS deployment for a Dockerized frontend/backend app using Terraform, Amazon ECR, AWS Secrets Manager, External Secrets Operator, Helm, GitHub Actions, ingress-nginx, and MongoDB Atlas.

For your project, I would first check the Docker images, ECR setup, ports, environment variables, health endpoints, and database connection. Then I can deploy it to EKS with a repeatable Helm release, AWS Secrets Manager env handling, rollback steps, and a short cost optimization note so the AWS bill does not grow unnecessarily.

I can start with a quick deployment audit and then move into implementation if everything is clear.
```

Fast reply message:

```text
Yes, I can start today. Please send the frontend image, backend image, required environment variables, app ports, health endpoint path, and whether you already have AWS/ECR/EKS or need me to create it with Terraform.
```

Best jobs to target:

- "Deploy Docker app to AWS"
- "Kubernetes deployment help"
- "EKS Terraform setup"
- "Push Docker images to ECR"
- "AWS Secrets Manager Kubernetes"
- "CI/CD pipeline for Docker app"
- "MongoDB Atlas connection issue"
- "Helm chart needed"
- "DevOps engineer for MVP deployment"
- "Fix Kubernetes ingress"

Avoid jobs that are too broad for a first quick win:

- Full platform engineering from scratch
- 24/7 production support without clear pay
- Security compliance audits with unclear scope
- Jobs asking for many clouds and many tools in one small budget

## 18. Market Signal References

Recent Upwork Project Catalog examples commonly emphasize the same stack: AWS, Kubernetes, Docker, Terraform, CI/CD, EKS, monitoring, and cost optimization.

References:

- https://www.upwork.com/services/product/development-it-devops-services-aws-kubernetes-ci-cd-cloud-infrastructure-2009574886209242649
- https://www.upwork.com/services/product/development-it-devops-services-aws-kubernetes-azure-oci-digital-ocean-1784476861892730345
- https://www.upwork.com/services/product/development-it-devops-engineer-aws-azure-kubernetes-docker-terraform-argocd-ci-cd-1889682782068892648
- https://www.upwork.com/services/product/development-it-devops-services-docker-aws-cloud-ci-cd-pipelines-kubernetes-1695712325334331392
