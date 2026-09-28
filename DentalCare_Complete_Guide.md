# DentalCare / ClinicOS: End-to-End Build and Launch Guide

**Purpose:** an ordered guide for taking the current repository from local setup through secure multi-clinic production rollout.  
**Product name:** configurable; use DentalCare or ClinicOS during development and change the configured brand later.  
**Guide date:** 28 September 2026.

> **Repository status:** This repository is a Phase 1 foundation: tenant and clinic identity models, RBAC foundations, password/session authentication, owner bootstrap, API health endpoints, and starter web/Android applications. Patient, scheduling, treatment, payments, inventory, patient portal, AI and other workflows below are planned work, not features to advertise as available yet. Treat this as a build plan, not a claim of healthcare compliance.

## 1. Start with product boundaries

1. Name one accountable product owner (the clinic owner) and one clinical safety lead (a dentist).
2. List all three locations, time zones, contact details, working hours, holiday rules, tax/invoice rules, doctors, staff, and the systems/registers being replaced.
3. Map each daily workflow before coding: new patient, booking, arrival/check-in, consultation, treatment, consent, prescription, payment/refund, inventory use, follow-up, cancellation/no-show, and end-of-day reconciliation.
4. Separate organization-wide settings from clinic-specific settings. A single owner may see their organization, but every record remains scoped to authorized clinics.
5. Define patient consent, access, retention, correction, export, deletion, breach-response and backup-restore procedures for the operating jurisdiction. Obtain qualified privacy/legal advice before production; requirements vary by location.
6. Define the first release boundary. Recommended pilot: identity/RBAC, clinic switching, patient registration, appointment calendar, check-in, clinical note/treatment, invoice/payment recording, and audit trail. Add integrations and AI only after those workflows are reliable.
7. Agree measurable acceptance criteria: no cross-clinic reads/writes, no double-booked doctor, reconciled payment totals, usable mobile screens, and a completed restore drill.

## 2. Final architecture

- **Web:** Next.js App Router + TypeScript for owner, administrator, clinician, reception and finance work.
- **Mobile:** Expo + React Native + TypeScript for Android workflows, barcode scan, push, camera and offline drafts.
- **API:** versioned FastAPI service. The server owns authorization and business rules; clients are not trusted.
- **Data:** PostgreSQL as durable source of truth; Redis for queues/cache/short-lived coordination; private object storage for documents.
- **Workers:** Celery-compatible workers for reminders, report generation, exports and provider calls.
- **External services:** provider adapters for messaging, email, payments, push, storage and AI; secrets stay server-side.
- **Tenancy:** organization -> clinics; users receive memberships and clinic grants. Enforce organization and clinic predicates on every request and background task. Never rely on a browser-supplied clinic ID alone.
- **AI:** narrow, typed tools call authorized application services. An LLM never receives database credentials. Mutations require validated actions and explicit confirmation where material.

Request path:

    Web / Android / Patient portal
      -> API v1 (authentication, validation, permission + clinic scope)
      -> domain services (appointments, clinical, finance, stock)
      -> PostgreSQL
      -> outbox / Celery + Redis -> SMS / WhatsApp / email / push / reports
      -> private object storage via short-lived signed URL

Store timestamps in UTC, retain the clinic IANA timezone for display/scheduling, and store money as integer minor units plus ISO currency (INR/paise), never floating point.

## 3. Database ER outline

The outline is a starting contract, not a substitute for migration review. Use UUID primary keys, timestamps, foreign keys, useful indexes, and explicit organization/clinic scope.

    Organization 1---* Clinic
    User *---* Organization via OrganizationMembership
    User *---* Clinic via ClinicMembership -> Role -> Permission
    Clinic 1---* Appointment *---1 Patient
    Doctor(User) 1---* Appointment
    Patient 1---* MedicalHistory / DentalHistory / Document / Consent
    Patient 1---* TreatmentPlan 1---* TreatmentRecord
    TreatmentRecord 1---* DentalChartRecord *---1 Tooth
    Patient 1---* Prescription 1---* PrescriptionItem
    Patient 1---* Invoice 1---* Payment / Refund
    Clinic 1---* Expense
    Clinic 1---* InventoryItem 1---* InventoryTransaction
    Supplier 1---* PurchaseOrder 1---* PurchaseOrderLine
    Clinic 1---* Conversation 1---* Message
    Notification 1---* NotificationDelivery / CommunicationLog
    User 1---* AuditLog; User 1---* AIConversation 1---* AIAction

Important constraints:

1. Add organization_id and, for clinic-owned records, clinic_id. Use composite constraints or service checks to ensure a patient, appointment, payment, file and clinic belong to the same organization.
2. A person may visit multiple clinics. Separate global patient identity/deduplication from clinic chart access and records; never merge charts automatically based only on similar name or phone.
3. Enforce appointment uniqueness transactionally (doctor/resource + clinic + interval). Use a PostgreSQL exclusion constraint or locked slot/booking table and validate overlapping durations/buffers. A pre-check alone is insufficient.
4. Keep clinical notes, prescriptions and consent versions append-only or revisioned. Corrections create attributable amendments; do not silently overwrite history.
5. Financial events are immutable ledger entries with reversal/refund entries, not destructive edits. Keep invoice, payment and gateway settlement states distinct.
6. Derive inventory quantity from immutable stock movements; transfers require paired source/destination movements and a stateful transfer record.
7. Store file metadata/object key in PostgreSQL and bytes in private S3-compatible storage. Issue short-lived signed URLs only after authorization.
8. Index common lookups: organization/clinic + patient phone, normalized name, patient number; doctor + appointment start/status; invoice/payment dates; SKU/barcode; expiry date; audit entity/time.

## 4. API contracts and RBAC

1. Keep routes under /api/v1; publish FastAPI OpenAPI with stable operation IDs, pagination, filters and examples.
2. Standard success envelope: success, data, message, meta. Standard error envelope: success=false plus stable error code, safe user message and request ID. Never return tracebacks.
3. Validate path/query/body with Pydantic v2 and enforce business rules again in services/database constraints.
4. Use short-lived access credentials and rotated/revocable refresh sessions. Hash passwords with Argon2id or a currently approved alternative. Use secure, httpOnly cookies on web and platform secure storage on mobile.
5. Derive user, organization, role and allowed clinics from the verified session. Verify requested clinic context on every operation.
6. Scope reads, updates, exports and file downloads. Use consistent not-found/forbidden behavior that does not leak other clinic record existence.
7. Make important creates, payments and stock operations idempotent. Persist idempotency keys/results for retries.
8. Bound pagination and sorting. Rate-limit login, OTP, public onboarding, exports and AI.
9. Verify gateway webhook signatures and replay protection server-side. A client success screen is never proof of payment.
10. Test foreign clinic IDs, stale slots, duplicate submissions and invalid state transitions.

Model granular permissions such as patients.read, clinical_notes.amend, payments.refund, inventory.adjust, reports.export and users.manage. Bind role grants to organization/clinic memberships rather than scattering role-name checks.

- **SUPER_ADMIN:** platform operations, isolated from routine clinic clinical data.
- **CLINIC_OWNER:** all configured clinics in their organization, financial and staff administration.
- **DOCTOR / DENTIST:** assigned patients/appointments and clinical actions within clinic scope.
- **RECEPTIONIST:** registration, scheduling, check-in, basic demographics and permitted collections.
- **ACCOUNTANT:** invoices, ledger, expenses, reconciliation and finance reports.
- **INVENTORY_MANAGER:** suppliers, purchase, stock movements and expiry alerts.
- **STAFF:** explicitly granted operational access only.
- **PATIENT:** authenticated access to their own portal data only.

For every operation: authenticate -> resolve organization -> verify clinic membership -> check permission -> check record assignment/relationship -> execute scoped query -> audit sensitive change.

## 5. Client navigation and state

### Android

- **Owner:** Home, Clinics, Appointments, Patients, Finance, Inventory, Reports, Inbox, AI/Voice, Settings.
- **Doctor:** Today, Queue, Patients, Clinical workspace (chart, notes, plan, prescription, consent), Follow-ups, Inbox.
- **Reception:** Schedule, Check-in, Add patient, Collect payment, Queries, Follow-ups.
- **Patient:** Home, Bookings, Treatment, Documents, Payments, Chat, Profile/consent.

Use Expo Router role-aware layouts, accessible touch targets, offline indicator, skeleton/empty/error states and confirmation for irreversible actions. Redux Toolkit holds app/session state; RTK Query owns remote cache; local component state stays local. Mark queued drafts unsynced and resolve conflicts explicitly. Do not silently queue payment, prescription or consent finalization.

### Web dashboard

Organization/clinic switcher; Overview; Appointments; Patients; Clinical; Finance; Inventory; Communications; Reports; Team; Settings. Persist and display date range/clinic filters. Use server components for suitable initial/static data and client components for interactive views. API authorization remains authoritative. Use typed API services, Zod + React Hook Form, TanStack Table for large lists, and accessible chart alternatives.

## 6. AI, voice, notifications and files

### AI and voice pipeline

Speech -> transcription -> typed intent + parameters -> permission check -> domain tool -> confirmation for mutation -> action execution -> audit/action record -> response.

1. Start with a narrow, versioned catalog: get_today_appointments, find_available_slots, get_revenue_report, get_low_stock_items, get_expiring_inventory, find_followups, draft_message, create_followup.
2. Each tool receives authenticated user and authorized clinic context from the server, validates a typed schema, applies least privilege and returns minimum necessary data.
3. Separate read and write tools. Draft an action, display clinic/patient/date/amount details, request confirmation, then re-check permissions and state before committing.
4. Disambiguate names, dates, clinics and doctors. Never infer clinical action from unclear speech.
5. No autonomous diagnosis/prescribing. Label clinical decision support and require dentist review.
6. Minimize/redact model context. Store only necessary conversation/action metadata with retention controls. Do not retain raw audio/transcripts indefinitely by default.
7. Provide non-AI paths and fallback on model outage. Evaluate prompt injection, hallucination, ambiguity, unauthorized access and cross-clinic leakage.

### Notifications

Use a transactional outbox: business transaction writes event -> worker claims event -> provider adapter sends -> delivery attempt/provider ID logged -> bounded retry -> dead-letter + staff alert. Deduplicate by event/channel/recipient/template. Implement adapters for push, official WhatsApp Business provider, SMS and email. Keep keys/templates server-side. Respect transactional vs promotional consent, opt-outs and quiet hours. Avoid sensitive clinical text in lock-screen previews.

### Secure patient onboarding and object storage

Use expiring single-use onboarding tokens plus OTP/authentication; never put patient data in a public URL. Store files privately in object storage, scan uploads, limit type/size, keep metadata in PostgreSQL, authorize every access and issue short-lived signed URLs.

## 7. From clean checkout to local development

Prerequisites: Git, Python 3.12+, Node.js 20.9+, npm, Docker Desktop with Compose, and for Android release an Expo/EAS account and Android credentials. Use distinct dev/staging/production credentials.

1. Read README.md, DENTALCARE_README.md, docs/architecture/architecture.md, .env.clinic.example and backend/.env.example.
2. Copy .env.clinic.example to ignored root .env. Replace placeholder passwords and JWT secrets with unique random local values; never reuse production secrets.
3. Start PostgreSQL, Redis, API and worker:

       docker compose -f compose.clinic.yml up -d --build

4. Apply schema migrations:

       docker compose -f compose.clinic.yml exec backend alembic upgrade head

5. Bootstrap the owner and three clinic memberships. The CLI prompts for the password:

       docker compose -f compose.clinic.yml exec backend dentalcare bootstrap-owner --organization "DentalCare Group" --slug dentalcare-group --owner-name "Clinic Owner" --email owner@example.com --clinic "Clinic A" --clinic "Clinic B" --clinic "Clinic C"

6. Inspect API docs at http://localhost:8000/api/v1/docs; liveness at /health/live; readiness at /health/ready.
7. Start the web shell in another terminal:

       cd web
       npm install
       npm run dev

   Open http://localhost:3000. If required, set CLINIC_API_URL=http://localhost:8000/api/v1 and NEXT_PUBLIC_APP_NAME=DentalCare in web/.env.local.
8. Start Android:

       cd mobile
       npm install
       $env:EXPO_PUBLIC_API_URL="http://10.0.2.2:8000/api/v1"
       npx expo start

   10.0.2.2 is Android emulator's host alias. For a physical phone, use a reachable development host/IP on a trusted network.
9. Commit/use lockfiles and review dependency updates/security advisories; do not blindly update production packages.
10. For direct backend work, copy backend/.env.example to backend/.env, install editable with dev extras, migrate, then run uvicorn app.main:app --reload from backend/.

## 8. Implement in product milestones

For each module: confirm workflow/acceptance examples -> review schema/constraints -> define API contract -> implement service/repository -> implement web/mobile states -> add tests -> demo with staff -> document decisions. Keep migrations reviewed and releases reversible where practical.

### Phase 1 - Foundation, tenants and identity (current foundation)

1. Confirm organization/clinic/membership/role/permission relations.
2. Complete invitations, account recovery, MFA/OTP policy, refresh rotation/revocation, device sessions and bootstrap hardening.
3. Implement clinic context resolution and reusable backend authorization dependencies.
4. Add audit service, request IDs, secure errors and rate limits.
5. Test owner access to its clinics and adversarial foreign clinic IDs.
6. Finish web/mobile sign-in, logout, expired-session and clinic switching.

### Phase 2 - Patients, team and appointments

1. Add clinician/staff profile and clinic assignments.
2. Define patient identity, clinic chart relationship, duplicate-review flow and normalized search.
3. Add registration, allergies/history with provenance, documents and access history.
4. Implement working hours, holidays, doctor/resource availability, treatment durations, breaks and buffers.
5. Create atomic booking with overlap-safe DB protection, idempotency and correct time zones.
6. Deliver day/week/month calendar, queue, walk-in, check-in, reschedule, cancellation and no-show tracking.
7. Test competing bookings and clinic isolation at service/API/database layers.

### Phase 3 - Clinical records

1. Create versioned treatment catalog and plans/records with estimates and status.
2. Add adult/pediatric tooth numbering and accessible interactive dental chart.
3. Add append-only consultation/procedure/follow-up notes, prescription documents and print/download.
4. Add consent templates with version/hash, signer, timestamp, clinician and immutable signed record.
5. Add upload scanning, private object storage and scoped signed downloads.
6. Review with dentists; verify amendments, access and retention.

### Phase 4 - Payments and finance

1. Define invoice numbering, tax, discount, rounding, refund and receipt rules for jurisdiction.
2. Implement immutable payment/ledger entries, payment methods and reconciliation.
3. Add gateway adapter, signed webhook verification, idempotency and replay protection.
4. Add expenses, attachments, vendors, recurring schedules and approval policy.
5. Build daily close, outstanding balance and clinic/date-filtered reports.
6. Reconcile reports from transactions; never edit a successful transaction in place.

### Phase 5 - Inventory

1. Add catalog, units, SKU/barcode, supplier, batch/expiry and clinic location.
2. Create stock movement ledger for receive, consume, transfer, damage, expiry and adjustment.
3. Block negative quantity except audited privileged override; protect transfers with paired movements.
4. Add purchase orders, receipt, low-stock and 30/60-day expiry worker jobs.
5. Implement camera barcode scan with manual lookup and retry-safe duplicate handling.

### Phase 6 - Portal, chat and notifications

1. Create authenticated onboarding with expiring single-use link and OTP.
2. Let patients complete profile/history/consent and upload files; staff reviews changes.
3. Implement portal appointments, invoices, documents, requests and secure chat.
4. Add event outbox, provider adapters, templates, communication log and preferences.
5. Add 24-hour/two-hour/post-visit/follow-up jobs with time zone, quiet hours, deduplication and retry.
6. Test providers in sandbox; verify local rules and official WhatsApp Business policies.

### Phase 7 - AI and voice

1. Start with read-only administrative questions over a few scoped tools.
2. Add structured drafts for reminders/summaries; staff reviews before sending.
3. Add voice transcription and typed intents; evaluate accents, noise, time ambiguity and clinic disambiguation.
4. For writes, show confirmation details and revalidate availability/permission/state at confirmation time.
5. Keep clinical output dentist-supervised and add escalation/refusal behavior.
6. Add redaction, retention, provider configuration, cost/latency monitoring and fallback.

### Phase 8 - Analytics, reports and exports

1. Define formulas (cash collected vs billed, refunds, tax, clinic/date attribution).
2. Add authorized clinic/date filters and role-limited exports.
3. Generate large PDF/CSV/XLSX reports asynchronously with expiring authorized links.
4. Show factual revenue, expenses, profit, appointments, patients, treatment mix, no-shows, utilization, workload, balances and stock turnover.
5. Reconcile dashboard metrics against source-ledger fixtures.

### Phase 9 - Security, quality and operations

Add unit, integration/API, DB, RBAC, appointment concurrency, webhook, AI/voice, component, E2E and security tests. Cover registration -> appointment -> check-in -> treatment -> invoice/payment -> follow-up; inventory receive -> scan/use -> expiry; and clinic switching/isolation. Test IDOR, privilege escalation, injection, XSS/CSRF as applicable, JWT rotation, rate limits, uploads and export links. Load-test booking and reports.

Do not use real patient information in development/demo. Use synthetic patients. Before pilot, complete jurisdiction privacy/legal review, security review, provider agreements, retention/incident policies, staff training and backup restore drill. Do not claim certification without evidence.

## 9. Production deployment and operations

1. Create isolated dev/staging/prod environments with distinct data stores, buckets, credentials and providers.
2. Build immutable backend containers; pin dependencies/base image, run non-root, scan and deploy by digest.
3. AWS managed baseline: ECS/Fargate behind ALB; RDS PostgreSQL (Multi-AZ for production); ElastiCache Redis; private encrypted S3; CloudFront/WAF where appropriate; Route 53, Secrets Manager and CloudWatch. Use private subnets and narrow security groups.
4. Run Alembic migrations as a release job after backup, not independently in every replica.
5. Use Secrets Manager/IAM roles, TLS, encryption at rest, least privilege and key rotation.
6. Add health/readiness, redacted structured logs, request IDs, latency/error dashboards, queue age, DB saturation and provider alarms.
7. Define RPO/RTO, backup retention and regional recovery; test restores regularly.
8. Configure WAF/rate limits, CORS, secure headers, upload scanning, retention and audit export.
9. In staging, run smoke/permission tests, migration, restore test and representative load test.
10. Release gradually with owner sign-off, feature flags, rollback criteria and staffed support.

For Android internal APK use:

    eas build --platform android --profile preview

For Play Store AAB use:

    eas build --platform android --profile production

Set app name, application ID, icons, version, deep-link scheme, push configuration and build-time API URL. Test synthetic role accounts, clinic switching, camera, uploads, push, offline drafts, deep links and token expiry. Protect signing credentials and review Play privacy disclosures. Never bundle server secrets in the app.

## 10. Test/release gates

- Unit: scheduling/time zones, ledger arithmetic, inventory movement, permission policy, AI intent validation.
- Integration/API: migrations, clinic scoping, memberships, state transitions, webhooks and retries.
- Concurrency: competing bookings, duplicate webhooks and stock adjustments.
- Security: clinic IDOR, privilege escalation, injection, session rotation, rate limiting, uploads and exports.
- UI: validation, loading/empty/offline/error/denied states, accessibility and responsive layouts.
- E2E: patient registration, appointment, clinical encounter, payment, follow-up, inventory and clinic switching.
- Operations: backup restore, provider credential loss, queue backlog, DB failover and incident runbook.

Release only when workflows, automated checks, tenant permissions, migrations, observability and operational ownership are in place.

## 11. Milestones and sequencing

Durations are planning ranges, not commitments. Parallel work begins only after shared schemas/contracts stabilize.

| Milestone | Outcome | Indicative duration |
|---|---|---:|
| 0. Discovery and jurisdiction review | Workflows, pilot boundary, data map, acceptance criteria | 2-4 weeks |
| 1. Foundation and tenant security | Identity, RBAC, clinic scope, audit, platform setup | 4-7 weeks |
| 2. Patients and appointments | Registration, search, schedule, check-in, reminders baseline | 6-9 weeks |
| 3. Clinical workspace | Treatment, chart, notes, prescription, consent | 6-10 weeks |
| 4. Finance | Invoices, payment ledger, expenses, reconciliation | 5-8 weeks |
| 5. Inventory | Suppliers, batches, barcode, transfers and expiry | 4-7 weeks |
| 6. Portal and communications | Patient onboarding, chat, notification integrations | 6-10 weeks |
| 7. AI/voice | Scoped tools, confirmation, evaluation and controls | 4-8 weeks |
| 8. Reports/release hardening | Exports, security, performance, training and pilot | 6-10 weeks |

## 12. Source tree and ownership

- Foundation/local commands: DENTALCARE_README.md
- Architecture: docs/architecture/architecture.md
- Environment contracts: .env.clinic.example and backend/.env.example
- Local composition: compose.clinic.yml
- Backend: backend/; web: web/; Android: mobile/
- Promotional overview: DentalCare_ClinicOS_Brochure.pdf
- Budget planning: DentalCare_ClinicOS_Costing_INR.pdf

At this guide date, Phase 1 foundation exists. Keep implementation status current; requirements in this guide are not proof a feature shipped.
