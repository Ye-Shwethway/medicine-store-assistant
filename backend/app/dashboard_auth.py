from __future__ import annotations

import base64
import hashlib
import hmac
import os
import secrets
import time

from fastapi import Cookie, HTTPException, status

PASSWORD_HASH = os.getenv("MSA_DASHBOARD_OWNER_PASSWORD_HASH", "").strip()
SESSION_SECRET = os.getenv("MSA_DASHBOARD_SESSION_SECRET", "").strip()
SESSION_COOKIE = "msa_dashboard_session"
PBKDF2_ITERATIONS = 310_000
MIN_SESSION_SECRET_LENGTH = 32


def _session_ttl_seconds() -> int:
    try:
        value = int(os.getenv("MSA_DASHBOARD_SESSION_TTL_SECONDS", "28800"))
    except ValueError:
        return 28_800
    return min(max(value, 300), 86_400)


SESSION_TTL_SECONDS = _session_ttl_seconds()


def _password_hash_shape_valid(value: str) -> bool:
    parts = value.split(":", 3)
    if len(parts) != 4 or parts[0] != "pbkdf2_sha256":
        return False
    try:
        iterations = int(parts[1])
        salt = _b64decode(parts[2])
        digest = _b64decode(parts[3])
    except (ValueError, TypeError):
        return False
    return iterations >= 100_000 and len(salt) >= 16 and len(digest) == 32


def dashboard_auth_configured() -> bool:
    return _password_hash_shape_valid(PASSWORD_HASH) and len(SESSION_SECRET) >= MIN_SESSION_SECRET_LENGTH


def make_password_hash(password: str, *, salt: bytes | None = None) -> str:
    if not password:
        raise ValueError("password must not be empty")
    salt = salt or secrets.token_bytes(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, PBKDF2_ITERATIONS)
    return "pbkdf2_sha256:{}:{}:{}".format(
        PBKDF2_ITERATIONS,
        base64.urlsafe_b64encode(salt).decode("ascii").rstrip("="),
        base64.urlsafe_b64encode(digest).decode("ascii").rstrip("="),
    )


def _b64decode(value: str) -> bytes:
    return base64.urlsafe_b64decode(value + "=" * (-len(value) % 4))


def verify_password(password: str) -> bool:
    if not dashboard_auth_configured() or not password:
        return False
    try:
        algorithm, iterations_text, salt_text, digest_text = PASSWORD_HASH.split(":", 3)
        if algorithm != "pbkdf2_sha256":
            return False
        iterations = int(iterations_text)
        salt = _b64decode(salt_text)
        expected = _b64decode(digest_text)
    except (ValueError, TypeError):
        return False
    actual = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, iterations)
    return hmac.compare_digest(actual, expected)


def create_session_token() -> str:
    if not dashboard_auth_configured():
        raise RuntimeError("dashboard authentication is not configured")
    expires_at = int(time.time()) + SESSION_TTL_SECONDS
    nonce = secrets.token_urlsafe(12)
    payload = f"owner:{expires_at}:{nonce}"
    signature = hmac.new(SESSION_SECRET.encode("utf-8"), payload.encode("utf-8"), hashlib.sha256).hexdigest()
    return base64.urlsafe_b64encode(f"{payload}:{signature}".encode("utf-8")).decode("ascii").rstrip("=")


def validate_session_token(token: str | None) -> bool:
    if not dashboard_auth_configured() or not token:
        return False
    try:
        decoded = _b64decode(token).decode("utf-8")
        role, expires_text, nonce, signature = decoded.split(":", 3)
        expires_at = int(expires_text)
        payload = f"{role}:{expires_at}:{nonce}"
    except (ValueError, UnicodeDecodeError):
        return False
    if role != "owner" or expires_at < int(time.time()):
        return False
    expected = hmac.new(SESSION_SECRET.encode("utf-8"), payload.encode("utf-8"), hashlib.sha256).hexdigest()
    return hmac.compare_digest(signature, expected)


def require_dashboard_session(
    msa_dashboard_session: str | None = Cookie(default=None, alias=SESSION_COOKIE),
) -> dict[str, str]:
    if not dashboard_auth_configured():
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Dashboard owner access is not provisioned",
        )
    if not validate_session_token(msa_dashboard_session):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Dashboard sign-in required")
    return {"role": "owner"}
