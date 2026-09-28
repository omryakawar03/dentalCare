# Core workflow contracts

These are planned domain workflows; only identity, clinic grants and authentication exist in Phase 1.

## Owner setup and clinic access

Apply migrations → bootstrap owner → provision clinics → invite staff through expiring purpose-bound links → verify identity → assign organization/clinic roles and grants → audit each change. Never use public signup for staff.

## Patient onboarding

Search and duplicate-check within authorized organization → create minimal demographics → issue random hashed, expiring, purpose-scoped onboarding token → send via opted-in channel → require identity proof/OTP before sensitive collection → capture profile, histories and versioned consent → log delivery/access. A link alone cannot expose clinic records.

## Appointment booking

Resolve patient/clinic/provider → query working hours, breaks, holidays and duration → present available slots → reserve in a database transaction using a conflict constraint/lock → commit only if still available → write outbox event for confirmation/reminders. On conflict return `APPOINTMENT_SLOT_UNAVAILABLE` and refresh slots.

## Clinical visit

Check in → doctor opens authorized record → append note and treatment plan/procedure entries → update tooth chart with author/time/history → obtain appropriate versioned consent → create prescription/follow-up → sign/finalize with an amendment path. Never overwrite prior clinical history.

## Financial close and stock movement

Invoice lines are immutable snapshots; record cash/UPI/card/bank/payment-gateway amounts in minor units. Reconcile online payment only from a signature-verified idempotent webhook; correct/refund using reversal entries. Stock is an append-only batch-aware movement ledger; transfer posts paired source/destination events in one transaction and cannot silently produce negative stock.
