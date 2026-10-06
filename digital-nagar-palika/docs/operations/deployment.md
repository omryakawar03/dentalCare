# Deployment guide

## Local

Copy `.env.example` to `.env`, rotate all sample values, then `docker compose up -d db redis`. Install the API package from `apps/api`, apply `alembic upgrade head`, and launch Uvicorn. Install web/mobile workspace dependencies and start their respective development servers. Local Docker credentials are development-only.

## Staging and production

Provision private network, managed PostgreSQL/PostGIS, Redis, object storage with quarantine/versioning, secrets manager, workload identity, ingress/WAF, DNS/TLS, backups/PITR, observability and private registry through reviewed IaC. Build once, scan, sign and promote the immutable container digest. Apply backward-compatible migrations as a separate reviewed job. Deploy to staging, run integration/accessibility/security/load checks, review DAST and operational dashboards, and obtain authorized production approval. Use canary/rolling deployment and documented rollback; database migrations must be expand/migrate/contract. Never run destructive migrations automatically during app startup.

CI lives at `.github/workflows/ci.yml`; current gates include Ruff, pytest, Semgrep, Gitleaks and Trivy. Add npm audit, OWASP Dependency Check, IaC scan (Checkov/tfsec), SBOM, image build/scan, DAST (ZAP), accessibility and API/E2E stages when corresponding apps and environments are configured. Store deployment credentials as environment-scoped OIDC secrets, not repository variables. Production publish requires protected branch and environment approval.
