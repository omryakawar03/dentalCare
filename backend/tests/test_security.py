from uuid import uuid4

import jwt

from app.core.security import (
    create_access_token,
    decode_access_token,
    hash_password,
    hash_refresh_token,
    new_refresh_token,
    verify_password,
)


def test_password_hash_is_not_reversible_and_verifies():
    encoded = hash_password("a-long-clinic-password")
    assert encoded != "a-long-clinic-password"
    assert verify_password("a-long-clinic-password", encoded)
    assert not verify_password("wrong-password", encoded)


def test_access_token_is_bound_to_user_and_session():
    user_id, session_id = uuid4(), uuid4()
    token = create_access_token(user_id, session_id)
    payload = decode_access_token(token)
    assert payload["sub"] == str(user_id)
    assert payload["sid"] == str(session_id)
    assert payload["type"] == "access"


def test_access_token_rejects_wrong_token_type():
    user_id, session_id = uuid4(), uuid4()
    token = jwt.encode(
        {"sub": str(user_id), "sid": str(session_id), "iss": "dentalcare-api", "type": "refresh", "exp": 4102444800},
        "change-me-before-deploying-32-characters",
        algorithm="HS256",
    )
    try:
        decode_access_token(token)
        assert False, "refresh tokens must not be accepted as access tokens"
    except jwt.InvalidTokenError:
        pass


def test_refresh_tokens_are_random_and_stored_as_hashes():
    first, second = new_refresh_token(), new_refresh_token()
    assert len(first) >= 60
    assert first != second
    assert hash_refresh_token(first) != first
