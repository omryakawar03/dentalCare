# Cost Optimization Plan

## Recommended Demo Architecture

Use Amazon EKS with one small managed node group for the two-day showcase.

Why:

- It demonstrates the managed Kubernetes platform many Upwork clients already search for.
- It supports a clean Terraform + Helm + GitHub Actions story.
- It still keeps spend controlled by using one small node group and destroying the cluster when the demo is finished.

## Database

Use MongoDB Atlas M0 for the demo if the app fits the limits. Upgrade to M2 or M5 only when data size, performance, or production needs require it.

## Images And Secrets

Use Amazon ECR for frontend and backend images. Use lifecycle policies to keep only the last few demo images so old tags do not pile up.

Use AWS Secrets Manager as the source of truth for runtime environment variables. External Secrets Operator syncs those values into Kubernetes, so secrets do not need to be stored in GitHub Actions or Helm values.

## Cloud Cost Controls

- Use one small managed node group for the demo.
- Use Spot capacity for the showcase, then switch to On-Demand for production.
- Keep ECR lifecycle policies enabled.
- Use `gp3` storage instead of older general-purpose EBS defaults.
- Put CPU and memory requests/limits in the Helm chart.
- Keep one replica for demo and raise replicas only during performance testing.
- Install one ingress controller for the showcase and remove it with the cluster after the demo.
- Destroy the EKS cluster when not presenting it.
- Add an AWS Budget in production.
- Use MongoDB Atlas alerts for storage and connection growth.

## Upgrade Path

Start:

- Amazon EKS
- One small managed node group
- One frontend replica
- One backend replica
- MongoDB Atlas shared tier

When the client needs production resilience:

- Move nodes into private subnets
- Add autoscaling node groups
- Add External Secrets Operator
- Add managed ingress with TLS
- Add Prometheus, Grafana, and log aggregation
- Add backup, restore, and incident runbooks
