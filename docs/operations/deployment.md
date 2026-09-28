# Deployment and operations

## Local foundation

`compose.clinic.yml` runs PostgreSQL 17, Redis 7, FastAPI and a Celery worker. Next.js and Expo use their own development commands. Apply Alembic migrations before first-owner bootstrap. Local password/secret defaults are for local use only.

## Production target

Start with AWS ECS/Fargate for API and worker; use RDS PostgreSQL Multi-AZ, ElastiCache Redis, private S3 with KMS, ALB/WAF, Route 53, Secrets Manager and CloudWatch/OpenTelemetry. Deliver static web through CloudFront where deployment mode permits. Add EKS only when the team needs its operational model. Keep databases/cache in private subnets; only the API ingress should be public.

Deploy immutable images with IaC, CI lint/security/build gates, staged migrations, TLS, least-privilege IAM, secret rotation, encrypted point-in-time backups and tested restoration. Define RPO/RTO, retention and incident runbooks before patient data is loaded. Log request IDs and operational events, but not credentials, tokens, patient notes or document contents. Configure liveness/readiness and alert on API latency/errors, database health, queue age, provider failures and payment webhook failures. Do not claim a compliance certification without independent assessment and evidence.

The current compose is a development foundation, not a production deployment definition. AWS templates must be reviewed and tailored for the actual region, jurisdiction and organization before use.
