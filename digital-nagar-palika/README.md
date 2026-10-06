# Digital Nagar Palika

Secure, multilingual, multi-tenant foundation for municipal services in India. The project is structured for incremental production delivery across municipalities, talukas and districts. It is an implementation foundation, not a claim that government integrations, production identity proofing, payment processing, or deployment approvals are already configured.

## Repository map

- `apps/api`: FastAPI API, PostgreSQL/Alembic and scoped authorization foundation.
- `apps/web`: responsive citizen and municipal operations portal (Next.js).
- `apps/mobile`: Android-first Expo citizen app scaffold.
- `packages/contracts`: shared API and domain contracts.
- `infra`: Docker Compose, Terraform starter and Kubernetes/Helm deployment notes.
- `docs`: architecture, security, operations, data model and implementation guide.

## Local development

1. Install Docker Desktop, Python 3.12+, Node.js 22+, and pnpm 10+.
2. Copy `.env.example` to `.env`; replace every development secret before sharing or deploying it.
3. Start PostgreSQL and Redis with `docker compose up -d db redis`.
4. API: `cd apps/api`, create/activate a virtual environment, `pip install -e '.[dev]'`, `alembic upgrade head`, then `uvicorn app.main:app --reload`.
5. Web: `cd apps/web`, `pnpm install`, `pnpm dev`.
6. Mobile: `cd apps/mobile`, `pnpm install`, `pnpm start`.

API docs are at `/api/v1/docs` in local development. The API intentionally has no public endpoint that dumps citizen records. Production auth, OTP delivery, SMS/FCM, GIS, payment gateway, AI provider, malware scanning and government identity verification require approved provider configuration and security review; no credentials or fabricated emergency contacts are included.

## Before a government pilot

Complete the deployment, security, privacy, accessibility, data protection, threat-model and disaster recovery reviews in `docs/`. Configure verified official contacts and schemes from authoritative municipal sources. Use synthetic records until the municipality's lawful data-sharing, retention and access policies are approved. See `docs/implementation-guide-hinglish.md` for the requested 30-step build sequence.
