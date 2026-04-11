#!/usr/bin/env bash
set -euo pipefail

tools=(
  git
  docker
  aws
  terraform
  helm
  kubectl
)

missing=()

for tool in "${tools[@]}"; do
  if command -v "$tool" >/dev/null 2>&1; then
    printf '[OK] %s -> %s\n' "$tool" "$(command -v "$tool")"
  else
    printf '[MISSING] %s\n' "$tool"
    missing+=("$tool")
  fi
done

if [ "${#missing[@]}" -gt 0 ]; then
  printf '\nInstall or fix PATH for: %s\n' "${missing[*]}"
  exit 1
fi

printf '\nAll required DevOps tools are available.\n'

