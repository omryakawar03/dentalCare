# Testing strategy

## Current status

Phase 1 includes unit tests for Argon2 password verification, JWT subject/session binding and token-type rejection, plus refresh-token entropy/hash handling. Python source compilation passed in the current workspace. The project test suite could not run because the workspace Python has no `pytest`, FastAPI, SQLAlchemy or other declared dependencies installed; Docker and Python 3.12 are unavailable here.

## Required test suites by milestone

- Unit: password/token rotation, permission evaluation, Zod/Pydantic validation, service invariants, money math and provider retry rules.
- PostgreSQL integration: tenant composite constraints, migration upgrade/downgrade empty DB, clinic/organization isolation, refresh replay/session revocation, appointment exclusion/locking, ledger reversal and webhook idempotency.
- API authorization: a Clinic A user must receive no data and cause no mutation for Clinic B, including guessed UUIDs, query filters, exports, uploads and AI tools.
- Concurrency: simultaneous booking, stock decrement, payment webhook retries and AI confirmation replay.
- Frontend: login/BFF cookie flags, form validation, permission-denied/loading/offline states and clinic switch.
- Mobile: secure storage, expired-session refresh, offline draft behavior, barcode permission and APK startup.
- E2E: first-owner bootstrap; staff access setup; patient registration/onboarding; slot booking; dentist treatment flow; payment; stock transfer/expiry alert.
- Security: IDOR/broken access control, SQL injection, XSS/CSRF, rate-limit bypass, upload validation, JWT abuse, privilege escalation, secrets in bundles/logs and cross-clinic export.

Never use live patient data in tests. Use disposable isolated databases and fake payment/notification providers. Performance tests must reflect measured clinic volumes and concurrency.
