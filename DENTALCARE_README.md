# DentalCare / ClinicOS

Multi-clinic dental practice platform. Product branding is configurable through backend `APP_NAME`, web `NEXT_PUBLIC_APP_NAME`, and build-time mobile `EXPO_PUBLIC_APP_NAME`.

## Status

The repository is being rebuilt in milestones. Phase 1 delivers architecture decisions, tenant and clinic identity models, RBAC foundations, password/session authentication, bootstrap, API health endpoints, plus starter web and Android applications. Patient, appointment, clinical, finance and inventory workflows are planned milestones and are not yet implemented.

See [the architecture plan](docs/architecture/architecture.md) for the system overview, tenant boundaries, ER diagram, API conventions, navigation, AI/voice and notification architecture, deployment plan, risks and milestone plan.

## Local development

Requirements: Python 3.12+, Node.js 20.9+, npm, Docker Compose.

1. Copy `.env.clinic.example` to the ignored root `.env` file and set unique random local secrets. (For running the API directly with Python, copy `backend/.env.example` to `backend/.env`.)
2. Start the foundation services from the repository root:

   ```powershell
   docker compose -f compose.clinic.yml up -d --build
   ```

3. Apply database migrations:

   ```powershell
   docker compose -f compose.clinic.yml exec backend alembic upgrade head
   ```

4. Create the first owner and clinic memberships. Repeat `--clinic` for every location. Password is entered interactively; no default credential is used:

   ```powershell
   docker compose -f compose.clinic.yml exec backend dentalcare bootstrap-owner `
     --organization "DentalCare Group" --slug dentalcare-group `
     --owner-name "Clinic Owner" --email owner@example.com `
     --clinic "Clinic A" --clinic "Clinic B" --clinic "Clinic C"
   ```

5. API docs: `http://localhost:8000/api/v1/docs`. Liveness: `/health/live`; readiness checks PostgreSQL and Redis at `/health/ready`.

Web: `cd web; npm install; npm run dev` (http://localhost:3000).

Android: `cd mobile; npm install; npx expo start`. Build APK with `eas build --platform android --profile preview`; production AAB uses the `production` profile. Set `EXPO_PUBLIC_API_URL` for the device. Android emulator default: `http://10.0.2.2:8000/api/v1`.

Backend local install: `cd backend; pip install -e '.[dev]'; alembic upgrade head; uvicorn app.main:app --reload`.

## Project map

- `backend/`: FastAPI, SQLAlchemy, Alembic, identity/security and versioned API
- `web/`: Next.js App Router dashboard shell and Redux Toolkit setup
- `mobile/`: Expo Router Android app, secure token storage and API boundary
- `docs/architecture/`: product architecture, data/security boundaries and milestones
- `compose.clinic.yml`: local PostgreSQL, Redis, API and Celery worker services

## Tenant and production safety

Each clinic belongs to an organization. Memberships carry roles; clinic grants constrain access. Every backend query must enforce both. Do not use real patient data in local/demo environments. Before production, complete jurisdiction-specific privacy/legal review, tenant isolation and concurrency tests, password recovery/OTP and account invitation flows, provider webhook verification, backup restore drills, observability, security review, and incident runbooks. This foundation is not a healthcare compliance certification or a complete clinical product.

Secrets belong in a secret manager. When file storage is added, use private object storage and short-lived signed URLs. See `backend/.env.example` for the API configuration contract.
