#!/usr/bin/env bash
set -euo pipefail

aws_region="us-east-1"
frontend_local_image=""
backend_local_image=""
frontend_ecr_url=""
backend_ecr_url=""
image_tag="latest"

usage() {
  cat <<'EOF'
Usage:
  scripts/retag-push-ecr.sh \
    --frontend-local-image local-frontend:latest \
    --backend-local-image local-backend:latest \
    --frontend-ecr-url 123456789012.dkr.ecr.us-east-1.amazonaws.com/devops-showcase/frontend \
    --backend-ecr-url 123456789012.dkr.ecr.us-east-1.amazonaws.com/devops-showcase/backend \
    --tag demo \
    --aws-region us-east-1

Options:
  --frontend-local-image IMAGE     Existing local frontend Docker image. Required.
  --backend-local-image IMAGE      Existing local backend Docker image. Required.
  --frontend-ecr-url URL           Frontend ECR repository URL from Terraform output. Required.
  --backend-ecr-url URL            Backend ECR repository URL from Terraform output. Required.
  --tag TAG                        Tag to push to ECR. Default: latest
  --aws-region REGION              AWS region. Default: us-east-1
  -h, --help                       Show help.
EOF
}

while [ "$#" -gt 0 ]; do
  case "$1" in
    --frontend-local-image)
      frontend_local_image="$2"
      shift 2
      ;;
    --backend-local-image)
      backend_local_image="$2"
      shift 2
      ;;
    --frontend-ecr-url)
      frontend_ecr_url="$2"
      shift 2
      ;;
    --backend-ecr-url)
      backend_ecr_url="$2"
      shift 2
      ;;
    --tag)
      image_tag="$2"
      shift 2
      ;;
    --aws-region)
      aws_region="$2"
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

if [ -z "$frontend_local_image" ] || [ -z "$backend_local_image" ] || [ -z "$frontend_ecr_url" ] || [ -z "$backend_ecr_url" ]; then
  usage >&2
  exit 1
fi

registry="${frontend_ecr_url%%/*}"

aws ecr get-login-password --region "$aws_region" | docker login --username AWS --password-stdin "$registry"

docker tag "$frontend_local_image" "$frontend_ecr_url:$image_tag"
docker tag "$backend_local_image" "$backend_ecr_url:$image_tag"

docker push "$frontend_ecr_url:$image_tag"
docker push "$backend_ecr_url:$image_tag"

printf '\nFrontend image: %s:%s\n' "$frontend_ecr_url" "$image_tag"
printf 'Backend image: %s:%s\n' "$backend_ecr_url" "$image_tag"

