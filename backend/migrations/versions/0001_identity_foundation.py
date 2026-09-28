"""Create tenant, identity, RBAC, and audit foundation."""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "0001_identity"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "organizations",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("name", sa.String(160), nullable=False),
        sa.Column("slug", sa.String(80), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_table(
        "clinics",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("organization_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False),
        sa.Column("name", sa.String(160), nullable=False),
        sa.Column("slug", sa.String(80), nullable=False),
        sa.Column("timezone", sa.String(64), nullable=False, server_default="Asia/Kolkata"),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.UniqueConstraint("organization_id", "slug", name="uq_clinic_org_slug"),
        sa.UniqueConstraint("organization_id", "id", name="uq_clinic_org_id"),
    )
    op.create_table(
        "users",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("email", sa.String(320), nullable=False),
        sa.Column("full_name", sa.String(160), nullable=False),
        sa.Column("password_hash", sa.String(256), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("is_platform_admin", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_table(
        "memberships",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("organization_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.UniqueConstraint("organization_id", "user_id", name="uq_membership_org_user"),
        sa.UniqueConstraint("organization_id", "id", name="uq_membership_org_id"),
    )
    op.create_table(
        "roles",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("key", sa.String(48), nullable=False, unique=True),
        sa.Column("label", sa.String(80), nullable=False),
        sa.Column("scope", sa.String(24), nullable=False, server_default="organization"),
    )
    op.create_table(
        "permissions",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("key", sa.String(96), nullable=False, unique=True),
        sa.Column("description", sa.String(200), nullable=False),
    )
    op.create_table(
        "membership_roles",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("organization_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("membership_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("clinic_id", postgresql.UUID(as_uuid=True)),
        sa.Column("role_id", sa.Integer(), sa.ForeignKey("roles.id", ondelete="RESTRICT"), nullable=False),
        sa.UniqueConstraint("membership_id", "role_id", "clinic_id", name="uq_membership_role_clinic", postgresql_nulls_not_distinct=True),
        sa.ForeignKeyConstraint(["organization_id", "membership_id"], ["memberships.organization_id", "memberships.id"], ondelete="CASCADE", name="fk_membership_role_same_org"),
        sa.ForeignKeyConstraint(["organization_id", "clinic_id"], ["clinics.organization_id", "clinics.id"], ondelete="CASCADE", name="fk_membership_role_same_clinic_org"),
    )
    op.create_table(
        "role_permissions",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("role_id", sa.Integer(), sa.ForeignKey("roles.id", ondelete="CASCADE"), nullable=False),
        sa.Column("permission_id", sa.Integer(), sa.ForeignKey("permissions.id", ondelete="CASCADE"), nullable=False),
        sa.UniqueConstraint("role_id", "permission_id", name="uq_role_permission"),
    )
    op.create_table(
        "clinic_grants",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("organization_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("membership_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("clinic_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.UniqueConstraint("membership_id", "clinic_id", name="uq_membership_clinic"),
        sa.ForeignKeyConstraint(["organization_id", "membership_id"], ["memberships.organization_id", "memberships.id"], ondelete="CASCADE", name="fk_clinic_grant_same_membership_org"),
        sa.ForeignKeyConstraint(["organization_id", "clinic_id"], ["clinics.organization_id", "clinics.id"], ondelete="CASCADE", name="fk_clinic_grant_same_org"),
    )
    op.create_table(
        "refresh_sessions",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("family_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("family_expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("token_hash", sa.String(64), nullable=False, unique=True),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("revoked_at", sa.DateTime(timezone=True)),
        sa.Column("replaced_by_id", postgresql.UUID(as_uuid=True)),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_table(
        "audit_events",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("organization_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("organizations.id", ondelete="SET NULL")),
        sa.Column("clinic_id", postgresql.UUID(as_uuid=True)),
        sa.Column("actor_user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id")),
        sa.Column("action", sa.String(96), nullable=False),
        sa.Column("entity_type", sa.String(96), nullable=False),
        sa.Column("entity_id", sa.String(96)),
        sa.Column("outcome", sa.String(24), nullable=False, server_default="success"),
        sa.Column("request_id", sa.String(64)),
        sa.Column("metadata_json", sa.Text()),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    for table, column in [
        ("clinics", "organization_id"), ("memberships", "organization_id"),
        ("memberships", "user_id"), ("membership_roles", "organization_id"),
        ("membership_roles", "membership_id"), ("membership_roles", "clinic_id"),
        ("clinic_grants", "organization_id"), ("clinic_grants", "membership_id"),
        ("clinic_grants", "clinic_id"), ("refresh_sessions", "user_id"),
        ("audit_events", "organization_id"),
    ]:
        op.create_index(f"ix_{table}_{column}", table, [column])
    op.create_index("ix_refresh_user_expiry", "refresh_sessions", ["user_id", "expires_at"])
    op.create_index("ix_refresh_sessions_family_id", "refresh_sessions", ["family_id"])
    op.create_index("ix_audit_org_created", "audit_events", ["organization_id", "created_at"])
    op.create_index("ix_users_email", "users", ["email"], unique=True)
    op.create_index("ix_organizations_slug", "organizations", ["slug"], unique=True)

    permissions = [
        ("clinics.read", "View clinics"),
        ("team.manage", "Manage clinic members and access"),
        ("patients.read_assigned", "View assigned patient records"),
        ("patients.manage", "Register and update patient demographics"),
        ("appointments.manage", "Manage clinic appointments"),
        ("clinical_records.write", "Create clinical records"),
        ("payments.collect", "Record patient payments"),
        ("finance.read", "View financial records and reports"),
        ("inventory.manage", "Manage clinic inventory"),
        ("reports.read", "View clinic analytics and reports"),
        ("organization.manage", "Manage organization settings"),
    ]
    bind = op.get_bind()
    permissions_table = sa.table("permissions", sa.column("key"), sa.column("description"))
    roles_table = sa.table("roles", sa.column("key"), sa.column("label"), sa.column("scope"))
    bind.execute(permissions_table.insert(), [{"key": key, "description": label} for key, label in permissions])
    role_specs = {
        "SUPER_ADMIN": ("Platform administrator", "platform", [key for key, _ in permissions]),
        "CLINIC_OWNER": ("Clinic owner", "organization", [key for key, _ in permissions]),
        "DOCTOR": (
            "Doctor",
            "clinic",
            ["clinics.read", "patients.read_assigned", "appointments.manage", "clinical_records.write"],
        ),
        "DENTIST": (
            "Dentist",
            "clinic",
            ["clinics.read", "patients.read_assigned", "appointments.manage", "clinical_records.write"],
        ),
        "RECEPTIONIST": (
            "Receptionist",
            "clinic",
            ["clinics.read", "patients.manage", "appointments.manage", "payments.collect"],
        ),
        "ACCOUNTANT": ("Accountant", "clinic", ["clinics.read", "finance.read", "reports.read"]),
        "INVENTORY_MANAGER": (
            "Inventory manager",
            "clinic",
            ["clinics.read", "inventory.manage"],
        ),
        "STAFF": ("Staff", "clinic", ["clinics.read"]),
        "PATIENT": ("Patient", "patient", []),
    }
    role_rows = [{"key": key, "label": label, "scope": scope} for key, (label, scope, _) in role_specs.items()]
    bind.execute(roles_table.insert(), role_rows)
    role_permissions_table = sa.table("role_permissions", sa.column("role_id"), sa.column("permission_id"))
    role_result = bind.execute(sa.text("SELECT id, key FROM roles"))
    permission_result = bind.execute(sa.text("SELECT id, key FROM permissions"))
    permission_ids = {row["key"]: row["id"] for row in permission_result.mappings()}
    role_ids = {row["key"]: row["id"] for row in role_result.mappings()}
    grants = [{"role_id": role_ids[role_key], "permission_id": permission_ids[permission_key]} for role_key, (_, _, allowed) in role_specs.items() for permission_key in allowed]
    bind.execute(role_permissions_table.insert(), grants)


def downgrade() -> None:
    bind = op.get_bind()
    if bind.scalar(sa.text("SELECT EXISTS (SELECT 1 FROM organizations) OR EXISTS (SELECT 1 FROM users)")):
        raise RuntimeError("Refusing to drop identity tables while tenant or user data exists")
    for index in [
        "ix_audit_org_created", "ix_refresh_sessions_family_id", "ix_refresh_user_expiry",
        "ix_refresh_sessions_user_id", "ix_clinic_grants_clinic_id", "ix_clinic_grants_membership_id",
        "ix_clinic_grants_organization_id", "ix_membership_roles_membership_id", "ix_memberships_user_id",
        "ix_membership_roles_clinic_id", "ix_membership_roles_organization_id",
        "ix_memberships_organization_id", "ix_clinics_organization_id", "ix_audit_events_organization_id",
        "ix_organizations_slug", "ix_users_email",
    ]:
        table = "audit_events" if index.startswith("ix_audit") else "refresh_sessions" if index.startswith("ix_refresh") else "clinic_grants" if index.startswith("ix_clinic_grants") else "membership_roles" if index.startswith("ix_membership_roles") else "memberships" if index.startswith("ix_memberships") else "clinics" if index.startswith("ix_clinics") else "organizations" if index.startswith("ix_organizations") else "users"
        op.drop_index(index, table_name=table, if_exists=True)
    for table in ["audit_events", "refresh_sessions", "clinic_grants", "role_permissions", "membership_roles", "permissions", "roles", "memberships", "users", "clinics", "organizations"]:
        op.drop_table(table)
