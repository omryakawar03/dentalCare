# Authentication and RBAC

## Authentication flow

The Phase 1 bootstrap CLI creates the first owner with an interactive 12+ character password. Passwords use Argon2id. Login uses a generic failure response, dummy-hash verification for unknown accounts, Redis IP and IP/email throttles, and an audit event. The API issues a short-lived signed access token and a high-entropy opaque refresh token. Only the SHA-256 hash of the refresh token is stored. Refresh rotation retains a fixed family expiration so activity cannot extend the session indefinitely.

Refresh rotates the token under a database row lock. Reuse of a rotated token revokes the active token family. Logout revokes the current token record, invalidating its access token too. Web exchanges credentials through a same-origin Next.js handler and receives HttpOnly, Secure-in-production, SameSite=Strict cookies. Android stores tokens in OS-backed SecureStore and serializes refresh requests. Password reset, OTP, MFA, SSO and staff invitations are production milestones and are not implemented in this foundation.

## Authorization model

The authenticated principal must have an active user, active organization membership, and a clinic grant. The permission dependency then resolves active role permissions for the organization-wide role or the exact clinic-scoped role. Composite foreign keys prevent assigning a grant or clinic-scoped role across organizations. Inactive organizations/clinics and memberships are denied. Responses must not reveal whether an inaccessible foreign-tenant record exists.

Seeded roles: `SUPER_ADMIN`, `CLINIC_OWNER`, `DOCTOR`, `DENTIST`, `RECEPTIONIST`, `ACCOUNTANT`, `INVENTORY_MANAGER`, `STAFF`, `PATIENT`. Permissions are explicit keys such as `appointments.manage`, `patients.read_assigned`, `finance.read`, and `inventory.manage`. The first CLI command assigns owner role organization-wide and grants the owner each provisioned clinic.

Super-admin break-glass, patient principals, invitation lifecycle, custom roles, endpoint-level domain coverage and fine-grained assigned-patient policies require later implementation. Never assume a role name alone authorizes access; use permission keys and clinic grants. Every permission change must be audited.
