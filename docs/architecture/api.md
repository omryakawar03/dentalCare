# API contract

REST API under `/api/v1`. FastAPI produces OpenAPI at `/api/v1/openapi.json` and Swagger UI at `/api/v1/docs`.

## Phase 1 endpoints

- `POST /auth/login`, `POST /auth/refresh`, `POST /auth/logout`, `GET /auth/me`
- `GET /clinics` (active memberships, assigned clinics, and `clinics.read` required)
- `GET /health/live`, `GET /health/ready`

Initial account creation is an audited, first-run CLI operation. Public registration is intentionally absent.

## Target domains

`/organizations`, `/memberships`, `/users`, `/patients`, `/appointments`, `/treatments`, `/dental-chart`, `/prescriptions`, `/consents`, `/documents`, `/invoices`, `/payments`, `/expenses`, `/inventory`, `/suppliers`, `/notifications`, `/conversations`, `/promotions`, `/followups`, `/reports`, `/ai`, `/voice`, `/audit`. Provider webhooks have isolated signature verification and idempotency.

Success: `{ "success": true, "data": {}, "message": "...", "meta": {} }`. Error: `{ "success": false, "error": { "code": "...", "message": "...", "fields": {} }, "request_id": "..." }`. Collection APIs will use cursor pagination and stable sort. Mutating requests that can be retried require idempotency keys. Use UTC ISO timestamps and minor-unit integers for money.

Every route authenticates and authorizes on the server; caller-supplied `organization_id`, `clinic_id`, role, or patient ID is a selector, never proof of access. Cross-tenant resource failures return a generic not-found response. Full API contracts will be added with each domain milestone rather than publishing undocumented placeholder routes.
