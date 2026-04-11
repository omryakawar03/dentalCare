#!/usr/bin/env bash
set -euo pipefail

release_name="showcase"
namespace="showcase"
frontend_image=""
backend_image=""
mongodb_uri="${MONGODB_URI:-}"
host_name="app.example.com"
cluster_name=""
aws_region="us-east-1"
install_ingress_controller="false"
install_external_secrets="false"
external_secrets_role_arn=""
aws_secret_name="devops-showcase/app/env"

usage() {
  cat <<'EOF'
Usage:
  scripts/deploy.sh \
    --frontend-image 123456789012.dkr.ecr.us-east-1.amazonaws.com/devops-showcase/frontend:latest \
    --backend-image 123456789012.dkr.ecr.us-east-1.amazonaws.com/devops-showcase/backend:latest \
    --cluster-name devops-showcase \
    --aws-region us-east-1 \
    --host app.example.com \
    --aws-secret-name devops-showcase/app/env \
    --install-ingress-controller \
    --install-external-secrets \
    --external-secrets-role-arn arn:aws:iam::123456789012:role/devops-showcase-external-secrets

Options:
  --release-name NAME              Helm release name. Default: showcase
  --namespace NAME                 Kubernetes namespace. Default: showcase
  --frontend-image IMAGE           Full frontend image name and tag. Required.
  --backend-image IMAGE            Full backend image name and tag. Required.
  --mongodb-uri URI                Optional fallback MongoDB Atlas connection string. Prefer AWS Secrets Manager.
  --host HOST                      Ingress host. Default: app.example.com
  --cluster-name NAME              Optional EKS cluster name for aws eks update-kubeconfig.
  --aws-region REGION              AWS region. Default: us-east-1
  --aws-secret-name NAME           AWS Secrets Manager secret name. Default: devops-showcase/app/env
  --install-ingress-controller     Install or update ingress-nginx.
  --install-external-secrets       Install or update External Secrets Operator.
  --external-secrets-role-arn ARN  IAM role ARN for External Secrets Operator service account.
  -h, --help                       Show help.
EOF
}

split_image() {
  local image="$1"
  local tag="${image##*:}"
  local repo="${image%:*}"

  if [ "$repo" = "$image" ] || [[ "$tag" == */* ]]; then
    repo="$image"
    tag="latest"
  fi

  printf '%s\n%s\n' "$repo" "$tag"
}

while [ "$#" -gt 0 ]; do
  case "$1" in
    --release-name)
      release_name="$2"
      shift 2
      ;;
    --namespace)
      namespace="$2"
      shift 2
      ;;
    --frontend-image)
      frontend_image="$2"
      shift 2
      ;;
    --backend-image)
      backend_image="$2"
      shift 2
      ;;
    --mongodb-uri)
      mongodb_uri="$2"
      shift 2
      ;;
    --host)
      host_name="$2"
      shift 2
      ;;
    --cluster-name)
      cluster_name="$2"
      shift 2
      ;;
    --aws-region)
      aws_region="$2"
      shift 2
      ;;
    --aws-secret-name)
      aws_secret_name="$2"
      shift 2
      ;;
    --install-ingress-controller)
      install_ingress_controller="true"
      shift
      ;;
    --install-external-secrets)
      install_external_secrets="true"
      shift
      ;;
    --external-secrets-role-arn)
      external_secrets_role_arn="$2"
      shift 2
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      printf 'Unknown argument: %s\n\n' "$1" >&2
      usage >&2
      exit 1
      ;;
  esac
done

if [ -z "$frontend_image" ] || [ -z "$backend_image" ]; then
  usage >&2
  exit 1
fi

if [ -n "$cluster_name" ]; then
  aws eks update-kubeconfig --region "$aws_region" --name "$cluster_name"
fi

if [ "$install_ingress_controller" = "true" ]; then
  helm repo add ingress-nginx https://kubernetes.github.io/ingress-nginx
  helm repo update
  helm upgrade --install ingress-nginx ingress-nginx/ingress-nginx \
    --namespace ingress-nginx \
    --create-namespace \
    --set controller.service.type=LoadBalancer
fi

if [ "$install_external_secrets" = "true" ]; then
  if [ -z "$external_secrets_role_arn" ]; then
    printf 'Missing --external-secrets-role-arn for External Secrets Operator install.\n' >&2
    exit 1
  fi

  helm repo add external-secrets https://charts.external-secrets.io
  helm repo update
  helm upgrade --install external-secrets external-secrets/external-secrets \
    --namespace external-secrets \
    --create-namespace \
    --set installCRDs=true \
    --set-string "serviceAccount.annotations.eks\.amazonaws\.com/role-arn=$external_secrets_role_arn" \
    --wait
  kubectl wait --for=condition=Established \
    crd/externalsecrets.external-secrets.io \
    crd/clustersecretstores.external-secrets.io \
    --timeout=120s
fi

readarray -t frontend_parts < <(split_image "$frontend_image")
readarray -t backend_parts < <(split_image "$backend_image")

kubectl create namespace "$namespace" --dry-run=client -o yaml | kubectl apply -f -

if [ -n "$mongodb_uri" ]; then
  kubectl -n "$namespace" create secret generic mongodb-atlas \
    --from-literal=MONGODB_URI="$mongodb_uri" \
    --dry-run=client -o yaml | kubectl apply -f -
fi

helm upgrade --install "$release_name" ./helm/microservice-showcase \
  --namespace "$namespace" \
  --set-string "frontend.image.repository=${frontend_parts[0]}" \
  --set-string "frontend.image.tag=${frontend_parts[1]}" \
  --set-string "backend.image.repository=${backend_parts[0]}" \
  --set-string "backend.image.tag=${backend_parts[1]}" \
  --set-string database.existingSecret=mongodb-atlas \
  --set externalSecrets.enabled=true \
  --set-string "externalSecrets.remoteSecretName=$aws_secret_name" \
  --set-string "externalSecrets.awsRegion=$aws_region" \
  --set-string "ingress.host=$host_name"

kubectl -n "$namespace" rollout status "deployment/$release_name-microservice-showcase-backend"
kubectl -n "$namespace" rollout status "deployment/$release_name-microservice-showcase-frontend"
