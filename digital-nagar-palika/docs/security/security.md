# Security and privacy baseline

## Identity and authorization

Use an approved identity provider or reviewed OTP flow. Enforce OTP resend/attempt limits, SIM-swap and abuse controls where supported, short-lived access tokens, refresh rotation/reuse detection, Argon2id for local passwords, CSRF defenses for cookie sessions, secure cookies, session revocation and MFA for privileged officials. Authorization is deny-by-default RBAC plus organization/ward/assignment ABAC. Validate scope on every request and background job. Use step-up approval for role changes, household corrections, emergency numbers, official publications and high-priority closure.

## Data protection

Classify public/internal/confidential/restricted-personal data. Minimize fields, mask contact details, encrypt transit and storage, use managed secret storage, restrict exports, track consent/legal basis, and set approved retention/deletion schedules. Do not log tokens, OTPs, full phone numbers, private document contents or citizen complaint bodies by default. QR payloads contain opaque, non-sensitive IDs only. Sensitive local data requires encrypted device storage and automatic expiry; offline write queues must be minimized and conflict-reviewed.

## Application and supply chain

Validate/encode input and output, parameterize SQL, use restrictive CORS and CSP, request-size limits, rate limiting, anti-automation, SSRF-safe outbound fetches, MIME/content sniffing and malware quarantine for files, dependency pinning/updates, secret scanning, SAST, container/IaC scanning and DAST in staging. CI should block configurable critical/high findings and permit time-limited, approved exceptions. Use SBOMs and signed images in production. Never display scanner results to citizen roles.

## AI boundaries

AI features are disabled until an approved provider is configured. Redact PII, pass only relevant excerpts, retrieve only approved municipal sources, label untrusted complaint/document content, validate output against schemas and cite sources. Provide abstention when unsupported. AI can draft/classify/summarize; it cannot decide eligibility, reject/approve service, change status, or execute admin tools. Preserve human review and AI audit metadata.

## Incident readiness

Create owner/on-call contacts, severity matrix, breach escalation path, evidence retention, recovery exercises and tested credential rotation before pilot. Keep audit append-only and replicate to separately controlled immutable retention. Security dashboards and IP/device details are restricted to a designated security role with access logging.
