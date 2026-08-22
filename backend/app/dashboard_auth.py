from __future__ import annotations

import base64
import hashlib
import hmac
import os
import secrets
from datetime import datetime, timedelta, timezone
from typing import Callable

from fastapi import Cookie, Depends, HTTPException, status
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError

from app.db import normalize_database_url

BOOTSTRAP_PASSWORD_HASH = os.getenv("MSA_DASHBOARD_OWNER_PASSWORD_HASH", "").strip()
BOOTSTRAP_OWNER_USERNAME = os.getenv("MSA_DASHBOARD_OWNER_USERNAME", "owner").strip() or "owner"
SESSION_SECRET = os.getenv("MSA_DASHBOARD_SESSION_SECRET", "").strip()
SESSION_COOKIE = "msa_dashboard_session"
PBKDF2_ITERATIONS = 310_000
MIN_SESSION_SECRET_LENGTH = 32
HUMAN_ROLES = frozenset({"OWNER", "ADMIN", "STAFF", "READ_ONLY"})
USER_STATES = frozenset({"PENDING", "ACTIVE", "DISABLED"})


def _session_ttl_seconds() -> int:
    try:
        value = int(os.getenv("MSA_DASHBOARD_SESSION_TTL_SECONDS", "28800"))
    except ValueError:
        return 28_800
    return min(max(value, 300), 86_400)


SESSION_TTL_SECONDS = _session_ttl_seconds()


def _database_url() -> str | None:
    value = os.getenv("DATABASE_URL", "").strip()
    return normalize_database_url(value) if value else None


def _engine():
    url = _database_url()
    if not url:
        raise RuntimeError("database is not configured")
    return create_engine(url, pool_pre_ping=True)


def _b64decode(value: str) -> bytes:
    return base64.urlsafe_b64decode(value + "=" * (-len(value) % 4))


def password_hash_shape_valid(value: str) -> bool:
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


def verify_password_hash(password: str, stored_hash: str) -> bool:
    if not password or not password_hash_shape_valid(stored_hash):
        return False
    try:
        algorithm, iterations_text, salt_text, digest_text = stored_hash.split(":", 3)
        if algorithm != "pbkdf2_sha256":
            return False
        iterations = int(iterations_text)
        salt = _b64decode(salt_text)
        expected = _b64decode(digest_text)
    except (ValueError, TypeError):
        return False
    actual = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, iterations)
    return hmac.compare_digest(actual, expected)


def _principal_dict(row) -> dict[str, str]:
    mapping = row._mapping if hasattr(row, "_mapping") else row
    return {
        "user_id": str(mapping["user_id"]),
        "username": str(mapping["username"]),
        "role": str(mapping["role"]),
        "state": str(mapping["state"]),
        **({"session_id": str(mapping["session_id"])} if "session_id" in mapping else {}),
    }


def ensure_bootstrap_owner() -> dict[str, str]:
    """Materialize the existing Owner bridge in the F2 canonical user model without plaintext access."""
    if len(SESSION_SECRET) < MIN_SESSION_SECRET_LENGTH:
        raise RuntimeError("dashboard session secret is not configured")
    engine = _engine()
    try:
        with engine.begin() as connection:
            existing = connection.execute(
                text(
                    """
                    SELECT u.user_id, u.username, ur.role_code AS role, u.state
                    FROM users u
                    JOIN user_roles ur ON ur.user_id = u.user_id
                    WHERE ur.role_code = 'OWNER'
                    ORDER BY u.created_at, u.user_id
                    LIMIT 1
                    """
                )
            ).first()
            if existing is not None:
                return _principal_dict(existing)

            if not password_hash_shape_valid(BOOTSTRAP_PASSWORD_HASH):
                raise RuntimeError("bootstrap Owner password hash is unavailable")
            if len(BOOTSTRAP_OWNER_USERNAME) > 120:
                raise RuntimeError("bootstrap Owner username is invalid")

            created = connection.execute(
                text(
                    """
                    INSERT INTO users (display_name, username, password_hash, state)
                    VALUES ('Owner', :username, :password_hash, 'ACTIVE')
                    RETURNING user_id, username, state
                    """
                ),
                {"username": BOOTSTRAP_OWNER_USERNAME, "password_hash": BOOTSTRAP_PASSWORD_HASH},
            ).one()
            user_id = str(created._mapping["user_id"])
            connection.execute(
                text("INSERT INTO user_roles (user_id, role_code) VALUES (CAST(:user_id AS uuid), 'OWNER')"),
                {"user_id": user_id},
            )
            return {
                "user_id": user_id,
                "username": str(created._mapping["username"]),
                "role": "OWNER",
                "state": str(created._mapping["state"]),
            }
    finally:
        engine.dispose()


def dashboard_auth_configured() -> bool:
    if len(SESSION_SECRET) < MIN_SESSION_SECRET_LENGTH or not _database_url():
        return False
    try:
        ensure_bootstrap_owner()
        return True
    except (RuntimeError, SQLAlchemyError):
        return False


def authenticate_user(username: str, password: str) -> dict[str, str] | None:
    username = username.strip()
    if not username or not password or len(SESSION_SECRET) < MIN_SESSION_SECRET_LENGTH:
        return None
    try:
        ensure_bootstrap_owner()
        engine = _engine()
        try:
            with engine.connect() as connection:
                row = connection.execute(
                    text(
                        """
                        SELECT u.user_id, u.username, u.password_hash, ur.role_code AS role, u.state
                        FROM users u
                        JOIN user_roles ur ON ur.user_id = u.user_id
                        WHERE lower(u.username) = lower(:username)
                        LIMIT 1
                        """
                    ),
                    {"username": username},
                ).first()
            if row is None or row._mapping["state"] != "ACTIVE":
                return None
            stored_hash = row._mapping["password_hash"]
            if stored_hash is None or not verify_password_hash(password, str(stored_hash)):
                return None
            return _principal_dict(row)
        finally:
            engine.dispose()
    except (RuntimeError, SQLAlchemyError):
        return None


def _session_digest(token: str) -> str:
    return hmac.new(SESSION_SECRET.encode("utf-8"), token.encode("utf-8"), hashlib.sha256).hexdigest()


def create_session_token(user_id: str) -> str:
    if len(SESSION_SECRET) < MIN_SESSION_SECRET_LENGTH:
        raise RuntimeError("dashboard authentication is not configured")
    raw_token = secrets.token_urlsafe(32)
    expires_at = datetime.now(timezone.utc) + timedelta(seconds=SESSION_TTL_SECONDS)
    engine = _engine()
    try:
        with engine.begin() as connection:
            user = connection.execute(
                text(
                    """
                    SELECT user_id, credential_version
                    FROM users
                    WHERE user_id = CAST(:user_id AS uuid) AND state = 'ACTIVE'
                    """
                ),
                {"user_id": user_id},
            ).first()
            if user is None:
                raise RuntimeError("active user not found")
            connection.execute(
                text(
                    """
                    INSERT INTO user_sessions (user_id, token_digest, credential_version, expires_at)
                    VALUES (CAST(:user_id AS uuid), :token_digest, :credential_version, :expires_at)
                    """
                ),
                {
                    "user_id": user_id,
                    "token_digest": _session_digest(raw_token),
                    "credential_version": int(user._mapping["credential_version"]),
                    "expires_at": expires_at,
                },
            )
        return raw_token
    finally:
        engine.dispose()


def resolve_session_token(token: str | None) -> dict[str, str] | None:
    if not token or len(SESSION_SECRET) < MIN_SESSION_SECRET_LENGTH:
        return None
    try:
        engine = _engine()
        try:
            with engine.begin() as connection:
                row = connection.execute(
                    text(
                        """
                        SELECT s.session_id, u.user_id, u.username, ur.role_code AS role, u.state
                        FROM user_sessions s
                        JOIN users u ON u.user_id = s.user_id
                        JOIN user_roles ur ON ur.user_id = u.user_id
                        WHERE s.token_digest = :token_digest
                          AND s.revoked_at IS NULL
                          AND s.expires_at > now()
                          AND s.credential_version = u.credential_version
                          AND u.state = 'ACTIVE'
                        LIMIT 1
                        """
                    ),
                    {"token_digest": _session_digest(token)},
                ).first()
                if row is None:
                    return None
                connection.execute(
                    text("UPDATE user_sessions SET last_seen_at = now() WHERE session_id = CAST(:session_id AS uuid)"),
                    {"session_id": str(row._mapping["session_id"])},
                )
                return _principal_dict(row)
        finally:
            engine.dispose()
    except (RuntimeError, SQLAlchemyError):
        return None


def validate_session_token(token: str | None) -> bool:
    return resolve_session_token(token) is not None


def revoke_session_token(token: str | None) -> None:
    if not token or len(SESSION_SECRET) < MIN_SESSION_SECRET_LENGTH:
        return
    try:
        engine = _engine()
        try:
            with engine.begin() as connection:
                connection.execute(
                    text("UPDATE user_sessions SET revoked_at = COALESCE(revoked_at, now()) WHERE token_digest = :digest"),
                    {"digest": _session_digest(token)},
                )
        finally:
            engine.dispose()
    except (RuntimeError, SQLAlchemyError):
        return


def revoke_user_sessions(user_id: str) -> None:
    engine = _engine()
    try:
        with engine.begin() as connection:
            connection.execute(
                text(
                    """
                    UPDATE user_sessions
                    SET revoked_at = COALESCE(revoked_at, now())
                    WHERE user_id = CAST(:user_id AS uuid) AND revoked_at IS NULL
                    """
                ),
                {"user_id": user_id},
            )
    finally:
        engine.dispose()


def require_dashboard_session(
    msa_dashboard_session: str | None = Cookie(default=None, alias=SESSION_COOKIE),
) -> dict[str, str]:
    if not dashboard_auth_configured():
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Dashboard access is not provisioned",
        )
    principal = resolve_session_token(msa_dashboard_session)
    if principal is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Dashboard sign-in required")
    return principal


def require_roles(*allowed_roles: str) -> Callable[..., dict[str, str]]:
    normalized = frozenset(role.upper() for role in allowed_roles)
    if not normalized or not normalized.issubset(HUMAN_ROLES):
        raise ValueError("allowed_roles must contain canonical human roles")

    def dependency(principal: dict[str, str] = Depends(require_dashboard_session)) -> dict[str, str]:
        if principal["role"] not in normalized:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")
        return principal

    return dependency


require_owner_session = require_roles("OWNER")
