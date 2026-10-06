# API conventions

All endpoints are versioned under `/api/v1`. OpenAPI is exposed only outside production by default. Use request/response schemas, pagination cursors or bounded page sizes, filtering, stable error codes, request IDs, idempotency keys for create/payment callbacks, and UTC RFC 3339 timestamps.

Planned groups: `/auth`, `/citizens/me`, `/households`, `/wards`, `/departments`, `/complaints`, `/announcements`, `/services`, `/payments`, `/schemes`, `/documents`, `/notifications`, `/emergency`, `/contacts`, `/analytics`, `/ai`, `/admin`, `/audit`, `/security`. Every protected resource is authorized by tenant plus ward/assignment and field-level policy. Citizen resources are self-scoped. Parent levels query aggregates only. Avoid endpoint shapes that reveal database existence across tenants; return a non-disclosing 404 where appropriate. Uploads use short-lived pre-signed URLs to quarantine and are unavailable until scan success.

Starter endpoints: `GET /health/live`, `GET /health/ready` (currently a placeholder), `GET /public/config`. Readiness must check dependencies before use in orchestration. Do not deploy until auth and domain routes are implemented and reviewed.
