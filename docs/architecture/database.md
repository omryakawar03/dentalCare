# Database design

This is the target relational design. The current migration implements the Phase 1 identity foundation; later domain tables listed here remain milestones.

The ER diagram and tenant key rules are in [the architecture overview](architecture.md#database-er-diagram-foundation-and-target-domains). PostgreSQL is authoritative. Every organization-owned entity has `organization_id`; clinic operations also have `clinic_id`. Composite foreign keys bind clinic and membership references to the same organization. UUID public identifiers prevent easy enumeration but never replace authorization.

## Foundation tables (implemented)

- `organizations`, `clinics`, `users`
- `memberships`, `roles`, `permissions`, `membership_roles`, `role_permissions`, `clinic_grants`
- `refresh_sessions`, `audit_events`

## Domain tables (planned)

Patients and clinical history; appointments and availability; treatment plans/records, chart entries, prescriptions and consent versions; documents; invoices, payments/allocations/refunds, expenses; inventory items/batches/transactions, suppliers and purchase orders; notification outbox/delivery logs; conversations/messages; follow-ups/campaigns; AI conversations/actions.

Use integer minor currency units with ISO currency codes, UTC timestamps, append-only ledger and clinical history, version columns for editable records, explicit soft disable for memberships/clinics, and foreign keys instead of application-only references. Do not cascade-delete clinical or financial history. Documents live outside PostgreSQL in private object storage.

## Index and isolation approach

Index tenant + clinic + status/date for high-use schedules, patients, invoices, inventory and reports. Search name/phone/email/identifier within tenant; protect sensitive search fields with the required matching strategy and audit export/search access. Add RLS only after transaction-local tenant context is consistently applied by the connection/session layer. Pool reuse must never inherit tenant context. Tenant-isolation tests must attempt cross-organization IDs on every read/write family.
