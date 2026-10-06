from uuid import uuid4

import pytest
from fastapi import HTTPException

from app.security.scope import Principal, require_scope


def test_tenant_member_can_access_own_organization():
    org = uuid4()
    require_scope(Principal(uuid4(), org, "MUNICIPAL_ADMIN"), org)


def test_cross_tenant_lookup_is_non_disclosing():
    with pytest.raises(HTTPException) as exc:
        require_scope(Principal(uuid4(), uuid4(), "MUNICIPAL_ADMIN"), uuid4())
    assert exc.value.status_code == 404


def test_ward_officer_is_limited_to_assigned_ward():
    org, assigned, other = uuid4(), uuid4(), uuid4()
    principal = Principal(uuid4(), org, "WARD_OFFICER", assigned)
    require_scope(principal, org, assigned)
    with pytest.raises(HTTPException) as exc:
        require_scope(principal, org, other)
    assert exc.value.status_code == 404
