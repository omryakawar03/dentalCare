"""One-time, interactive first-tenant bootstrap. Never use default credentials."""

import argparse
import asyncio
import getpass
import re

from pydantic import EmailStr, TypeAdapter
from sqlalchemy import func, select, text

from app.core.database import SessionFactory, engine
from app.core.security import hash_password
from app.models import (
    AuditEvent,
    Clinic,
    ClinicGrant,
    Membership,
    MembershipRole,
    Organization,
    Role,
    User,
)


def slugify(value: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", value.strip().lower()).strip("-")
    if not slug:
        raise ValueError("Name must contain letters or numbers")
    return slug[:76].rstrip("-")


async def bootstrap_owner(name: str, slug: str, email: str, owner_name: str, clinic_names: list[str]) -> None:
    if len(clinic_names) < 3:
        raise ValueError("First-run setup needs the three existing clinics; repeat --clinic for each one")
    email = TypeAdapter(EmailStr).validate_python(email).lower()
    password_hash = hash_password(get_password())
    async with SessionFactory() as db:
        async with db.begin():
            # Serialize first-run commands so two operators cannot create two initial tenants.
            await db.execute(text("SELECT pg_advisory_xact_lock(7420193901)"))
            if await db.scalar(select(func.count(User.id))) != 0:
                raise RuntimeError("Bootstrap is first-run only: user accounts already exist")
            role = await db.scalar(select(Role).where(Role.key == "CLINIC_OWNER"))
            if role is None:
                raise RuntimeError("RBAC roles are missing. Run `alembic upgrade head` first.")
            organization = Organization(name=name.strip(), slug=slugify(slug))
            user = User(
                email=email,
                full_name=owner_name.strip(),
                password_hash=password_hash,
            )
            db.add_all([organization, user])
            await db.flush()
            membership = Membership(organization_id=organization.id, user_id=user.id)
            db.add(membership)
            await db.flush()
            db.add(
                MembershipRole(
                    organization_id=organization.id,
                    membership_id=membership.id,
                    role_id=role.id,
                )
            )
            used_slugs: set[str] = set()
            for clinic_name in clinic_names:
                clinic_slug = slugify(clinic_name)
                if clinic_slug in used_slugs:
                    raise ValueError(f"Clinic names must have distinct slugs: {clinic_name}")
                used_slugs.add(clinic_slug)
                clinic = Clinic(
                    organization_id=organization.id,
                    name=clinic_name.strip(),
                    slug=clinic_slug,
                )
                db.add(clinic)
                await db.flush()
                db.add(
                    ClinicGrant(
                        organization_id=organization.id,
                        membership_id=membership.id,
                        clinic_id=clinic.id,
                    )
                )
            db.add(
                AuditEvent(
                    organization_id=organization.id,
                    actor_user_id=user.id,
                    action="organization.bootstrap",
                    entity_type="organization",
                    entity_id=str(organization.id),
                )
            )
    print(f"Created organization {name!r}, owner {email!r}, and {len(clinic_names)} clinic(s).")


def get_password() -> str:
    password = getpass.getpass("Choose owner password (12+ characters): ")
    if len(password) < 12:
        raise ValueError("Password must contain at least 12 characters")
    confirmation = getpass.getpass("Repeat password: ")
    if password != confirmation:
        raise ValueError("Passwords did not match")
    return password


def main() -> None:
    parser = argparse.ArgumentParser(prog="dentalcare")
    commands = parser.add_subparsers(dest="command", required=True)
    bootstrap = commands.add_parser("bootstrap-owner", help="Create the initial owner and clinics")
    bootstrap.add_argument("--organization", required=True)
    bootstrap.add_argument("--slug", required=True)
    bootstrap.add_argument("--owner-name", required=True)
    bootstrap.add_argument("--email", required=True)
    bootstrap.add_argument("--clinic", action="append", required=True, help="Repeat once for each clinic")
    args = parser.parse_args()
    try:
        asyncio.run(
            bootstrap_owner(args.organization, args.slug, args.email, args.owner_name, args.clinic)
        )
    finally:
        asyncio.run(engine.dispose())


if __name__ == "__main__":
    main()
