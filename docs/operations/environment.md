# Environment variables

The API template is `backend/.env.example`; the local Compose template is `.env.clinic.example` (copy it to the root `.env`, already ignored by Git). Production secrets belong in AWS Secrets Manager or the chosen secret manager; never commit real values or expose server secrets through `NEXT_PUBLIC_*` or `EXPO_PUBLIC_*`.

| Variable | Purpose | Secret? |
| --- | --- | --- |
| `APP_NAME` | Configurable product branding | No |
| `ENVIRONMENT` | Runtime mode; enables production secret checks | No |
| `DATABASE_URL` | Async PostgreSQL URL (`postgresql+asyncpg`) | Yes |
| `REDIS_URL` | Redis connection for rate limits and jobs | Yes in production |
| `JWT_SECRET` | HS256 signing key; 32+ random characters in production | Yes |
| `JWT_ISSUER` | Token issuer check | No |
| `ACCESS_TOKEN_MINUTES` | Short access-token lifetime | No |
| `REFRESH_TOKEN_DAYS` | Refresh-token family maximum lifetime | No |
| `ALLOWED_ORIGINS` | JSON array of exact browser origins | No |
| `POSTGRES_PASSWORD` | Local compose PostgreSQL password | Yes |
| `CLINIC_API_URL` | Server-side web BFF upstream URL | No |
| `EXPO_PUBLIC_API_URL` | Mobile API URL compiled into the app | No; endpoint only |
| `NEXT_PUBLIC_APP_NAME` | Web product display name | No |
| `EXPO_PUBLIC_APP_NAME` | Mobile product display name at build time | No |

Provider credentials (`S3`, email, SMS, WhatsApp, payment, AI) are intentionally absent until their adapters are implemented and selected. Keep secrets separate by environment, rotate on exposure, and avoid embedding credentials in APK/AAB artifacts.
