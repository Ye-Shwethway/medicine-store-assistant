from __future__ import annotations

import hashlib
import hmac
import os
import secrets
from datetime import datetime, timedelta, timezone
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Response, status
from pydantic import BaseModel
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError

from app.dashboard_auth import (
    SESSION_SECRET,
    _engine,
    make_password_hash,
    require_dashboard_session,
    require_owner_session,
    verify_password_hash,
)
from app.user_management import USERNAME_RE, _account_event, _notification_event

router = APIRouter(prefix="/dashboard/api", tags=["credential-lifecycle"])


def _reset_ttl_seconds() -> int:
    try:
        value = int(os.getenv("MSA_PASSWORD_RESET_TTL_SECONDS", "1800"))
    except ValueError:
        return 1800
    return min(max(value, 300), 3600)


RESET_TTL_SECONDS = _reset_ttl_seconds()


class UsernameChange(BaseModel):
    current_password: str
    new_username: str


class PasswordChange(BaseModel):
    current_password: str
    new_password: str


class PasswordResetRequestCreate(BaseModel):
    username: str


class PasswordResetComplete(BaseModel):
    token: str
    new_password: str


def _no_store(response: Response) -> None:
    response.headers["Cache-Control"] = "no-store"
    response.headers["Pragma"] = "no-cache"


def _validate_password(password: str) -> None:
    if len(password) < 10 or len(password) > 256:
        raise HTTPException(status_code=400, detail="Password must be 10–256 characters")


def _reset_digest(token: str) -> str:
    if len(SESSION_SECRET) < 32:
        raise RuntimeError("dashboard session secret is not configured")
    return hmac.new(
        SESSION_SECRET.encode("utf-8"),
        ("password-reset:" + token).encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()


def _revoke_sessions(connection, user_id: str) -> None:
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


def _current_user_for_update(connection, user_id: str):
    return connection.execute(
        text(
            """
            SELECT u.user_id::text AS user_id,
                   u.username,
                   u.password_hash,
                   u.state,
                   u.credential_version,
                   ur.role_code AS role
            FROM users u
            JOIN user_roles ur ON ur.user_id = u.user_id
            WHERE u.user_id = CAST(:user_id AS uuid)
            FOR UPDATE
            """
        ),
        {"user_id": user_id},
    ).mappings().first()


@router.patch("/account/username", summary="Change the signed-in username")
def change_username(
    payload: UsernameChange,
    response: Response,
    principal: dict[str, str] = Depends(require_dashboard_session),
) -> dict[str, Any]:
    _no_store(response)
    new_username = payload.new_username.strip()
    if not USERNAME_RE.fullmatch(new_username):
        raise HTTPException(status_code=400, detail="Username must be 3–64 letters, numbers, dots, dashes, or underscores")
    engine = _engine()
    try:
        try:
            with engine.begin() as connection:
                user = _current_user_for_update(connection, principal["user_id"])
                if user is None or user["state"] != "ACTIVE":
                    raise HTTPException(status_code=401, detail="Dashboard sign-in required")
                if not verify_password_hash(payload.current_password, str(user["password_hash"] or "")):
                    raise HTTPException(status_code=401, detail="Current password is incorrect")
                if user["username"].casefold() == new_username.casefold():
                    raise HTTPException(status_code=400, detail="Choose a different username")
                connection.execute(
                    text(
                        """
                        UPDATE users
                        SET username = :username,
                            credential_version = credential_version + 1,
                            updated_at = now()
                        WHERE user_id = CAST(:user_id AS uuid)
                        """
                    ),
                    {"username": new_username, "user_id": principal["user_id"]},
                )
                _revoke_sessions(connection, principal["user_id"])
                _account_event(
                    connection,
                    event_type="USERNAME_CHANGED",
                    target_user_id=principal["user_id"],
                    actor_user_id=principal["user_id"],
                    details={"from": user["username"], "to": new_username},
                )
        except IntegrityError as exc:
            raise HTTPException(status_code=409, detail="Username is unavailable") from exc
        return {"changed": True, "username": new_username, "sessions_revoked": True, "sign_in_again": True}
    finally:
        engine.dispose()


@router.post("/account/password", summary="Change the signed-in password")
def change_password(
    payload: PasswordChange,
    response: Response,
    principal: dict[str, str] = Depends(require_dashboard_session),
) -> dict[str, Any]:
    _no_store(response)
    _validate_password(payload.new_password)
    engine = _engine()
    try:
        with engine.begin() as connection:
            user = _current_user_for_update(connection, principal["user_id"])
            if user is None or user["state"] != "ACTIVE":
                raise HTTPException(status_code=401, detail="Dashboard sign-in required")
            stored_hash = str(user["password_hash"] or "")
            if not verify_password_hash(payload.current_password, stored_hash):
                raise HTTPException(status_code=401, detail="Current password is incorrect")
            if verify_password_hash(payload.new_password, stored_hash):
                raise HTTPException(status_code=400, detail="Choose a different password")
            connection.execute(
                text(
                    """
                    UPDATE users
                    SET password_hash = :password_hash,
                        credential_version = credential_version + 1,
                        updated_at = now()
                    WHERE user_id = CAST(:user_id AS uuid)
                    """
                ),
                {"password_hash": make_password_hash(payload.new_password), "user_id": principal["user_id"]},
            )
            _revoke_sessions(connection, principal["user_id"])
            connection.execute(
                text(
                    """
                    UPDATE password_reset_requests
                    SET status = 'CANCELLED', token_digest = NULL
                    WHERE user_id = CAST(:user_id AS uuid)
                      AND status IN ('PENDING','ISSUED')
                    """
                ),
                {"user_id": principal["user_id"]},
            )
            _account_event(
                connection,
                event_type="PASSWORD_CHANGED",
                target_user_id=principal["user_id"],
                actor_user_id=principal["user_id"],
            )
        return {"changed": True, "sessions_revoked": True, "sign_in_again": True}
    finally:
        engine.dispose()


@router.post("/password-reset-requests", status_code=status.HTTP_202_ACCEPTED, summary="Request a password reset")
def request_password_reset(payload: PasswordResetRequestCreate, response: Response) -> dict[str, Any]:
    _no_store(response)
    username = payload.username.strip()
    generic = {
        "requested": True,
        "message": "If the account is eligible, the reset request is pending Owner review.",
    }
    if not username:
        return generic
    engine = _engine()
    try:
        with engine.begin() as connection:
            user = connection.execute(
                text(
                    """
                    SELECT user_id::text AS user_id, state
                    FROM users
                    WHERE lower(username) = lower(:username)
                    LIMIT 1
                    """
                ),
                {"username": username},
            ).mappings().first()
            if user is None or user["state"] != "ACTIVE":
                return generic
            user_id = user["user_id"]
            connection.execute(
                text(
                    """
                    UPDATE password_reset_requests
                    SET status = 'EXPIRED', token_digest = NULL
                    WHERE user_id = CAST(:user_id AS uuid)
                      AND status = 'ISSUED'
                      AND expires_at <= now()
                    """
                ),
                {"user_id": user_id},
            )
            existing = connection.execute(
                text(
                    """
                    SELECT 1
                    FROM password_reset_requests
                    WHERE user_id = CAST(:user_id AS uuid)
                      AND status IN ('PENDING','ISSUED')
                    LIMIT 1
                    """
                ),
                {"user_id": user_id},
            ).first()
            if existing is None:
                created = connection.execute(
                    text(
                        """
                        INSERT INTO password_reset_requests (user_id)
                        VALUES (CAST(:user_id AS uuid))
                        RETURNING password_reset_request_id::text AS request_id
                        """
                    ),
                    {"user_id": user_id},
                ).mappings().one()
                _account_event(
                    connection,
                    event_type="PASSWORD_RESET_REQUESTED",
                    target_user_id=user_id,
                    actor_user_id=None,
                    details={"request_id": created["request_id"], "source": "WEB"},
                )
                _notification_event(
                    connection,
                    event_type="PASSWORD_RESET_REQUESTED",
                    subject_user_id=user_id,
                    payload={"request_id": created["request_id"], "source": "WEB"},
                )
        return generic
    finally:
        engine.dispose()


@router.get("/password-reset-requests", summary="List password reset requests")
def list_password_reset_requests(
    response: Response,
    owner: dict[str, str] = Depends(require_owner_session),
) -> dict[str, Any]:
    _no_store(response)
    engine = _engine()
    try:
        with engine.begin() as connection:
            connection.execute(
                text(
                    """
                    UPDATE password_reset_requests
                    SET status = 'EXPIRED', token_digest = NULL
                    WHERE status = 'ISSUED' AND expires_at <= now()
                    """
                )
            )
            rows = connection.execute(
                text(
                    """
                    SELECT pr.password_reset_request_id::text AS request_id,
                           pr.user_id::text AS user_id,
                           u.display_name,
                           u.username,
                           u.state,
                           ur.role_code AS role,
                           pr.status,
                           pr.requested_at,
                           pr.issued_at,
                           pr.expires_at
                    FROM password_reset_requests pr
                    JOIN users u ON u.user_id = pr.user_id
                    LEFT JOIN user_roles ur ON ur.user_id = u.user_id
                    WHERE pr.status IN ('PENDING','ISSUED','EXPIRED')
                    ORDER BY
                        CASE pr.status WHEN 'PENDING' THEN 0 WHEN 'ISSUED' THEN 1 ELSE 2 END,
                        pr.requested_at DESC
                    LIMIT 100
                    """
                )
            ).mappings().all()
        return {"items": [dict(row) for row in rows], "count": len(rows), "owner_user_id": owner["user_id"]}
    finally:
        engine.dispose()


@router.post("/password-reset-requests/{request_id}/issue", summary="Issue a one-time password reset link")
def issue_password_reset(
    request_id: str,
    response: Response,
    owner: dict[str, str] = Depends(require_owner_session),
) -> dict[str, Any]:
    _no_store(response)
    token = secrets.token_urlsafe(32)
    expires_at = datetime.now(timezone.utc) + timedelta(seconds=RESET_TTL_SECONDS)
    engine = _engine()
    try:
        with engine.begin() as connection:
            request_row = connection.execute(
                text(
                    """
                    SELECT pr.password_reset_request_id::text AS request_id,
                           pr.user_id::text AS user_id,
                           pr.status,
                           u.state,
                           u.username
                    FROM password_reset_requests pr
                    JOIN users u ON u.user_id = pr.user_id
                    WHERE pr.password_reset_request_id = CAST(:request_id AS uuid)
                    FOR UPDATE
                    """
                ),
                {"request_id": request_id},
            ).mappings().first()
            if request_row is None:
                raise HTTPException(status_code=404, detail="Reset request not found")
            if request_row["status"] != "PENDING" or request_row["state"] != "ACTIVE":
                raise HTTPException(status_code=409, detail="Reset request is not eligible for issuance")
            connection.execute(
                text(
                    """
                    UPDATE password_reset_requests
                    SET status = 'ISSUED',
                        token_digest = :token_digest,
                        issued_at = now(),
                        expires_at = :expires_at,
                        issued_by_user_id = CAST(:owner_id AS uuid)
                    WHERE password_reset_request_id = CAST(:request_id AS uuid)
                    """
                ),
                {
                    "token_digest": _reset_digest(token),
                    "expires_at": expires_at,
                    "owner_id": owner["user_id"],
                    "request_id": request_id,
                },
            )
            _account_event(
                connection,
                event_type="PASSWORD_RESET_ISSUED",
                target_user_id=request_row["user_id"],
                actor_user_id=owner["user_id"],
                details={"request_id": request_id, "expires_at": expires_at.isoformat()},
            )
            _notification_event(
                connection,
                event_type="PASSWORD_RESET_ISSUED",
                subject_user_id=request_row["user_id"],
                payload={"request_id": request_id, "expires_at": expires_at.isoformat()},
            )
        return {
            "issued": True,
            "request_id": request_id,
            "username": request_row["username"],
            "expires_at": expires_at.isoformat(),
            "reset_fragment": f"#reset={token}",
            "reset_path": f"/dashboard/login#reset={token}",
        }
    finally:
        engine.dispose()


@router.post("/password-resets/complete", summary="Complete a one-time password reset")
def complete_password_reset(payload: PasswordResetComplete, response: Response) -> dict[str, Any]:
    _no_store(response)
    _validate_password(payload.new_password)
    token = payload.token.strip()
    if len(token) < 32 or len(token) > 256:
        raise HTTPException(status_code=400, detail="Reset link is invalid or expired")
    engine = _engine()
    try:
        with engine.begin() as connection:
            request_row = connection.execute(
                text(
                    """
                    SELECT pr.password_reset_request_id::text AS request_id,
                           pr.user_id::text AS user_id,
                           pr.status,
                           pr.expires_at,
                           u.state,
                           u.password_hash
                    FROM password_reset_requests pr
                    JOIN users u ON u.user_id = pr.user_id
                    WHERE pr.token_digest = :token_digest
                    FOR UPDATE
                    """
                ),
                {"token_digest": _reset_digest(token)},
            ).mappings().first()
            if (
                request_row is None
                or request_row["status"] != "ISSUED"
                or request_row["state"] != "ACTIVE"
                or request_row["expires_at"] is None
                or request_row["expires_at"] <= datetime.now(timezone.utc)
            ):
                if request_row is not None and request_row["status"] == "ISSUED":
                    connection.execute(
                        text(
                            """
                            UPDATE password_reset_requests
                            SET status = 'EXPIRED', token_digest = NULL
                            WHERE password_reset_request_id = CAST(:request_id AS uuid)
                            """
                        ),
                        {"request_id": request_row["request_id"]},
                    )
                raise HTTPException(status_code=400, detail="Reset link is invalid or expired")
            if verify_password_hash(payload.new_password, str(request_row["password_hash"] or "")):
                raise HTTPException(status_code=400, detail="Choose a different password")
            user_id = request_row["user_id"]
            connection.execute(
                text(
                    """
                    UPDATE users
                    SET password_hash = :password_hash,
                        credential_version = credential_version + 1,
                        updated_at = now()
                    WHERE user_id = CAST(:user_id AS uuid)
                    """
                ),
                {"password_hash": make_password_hash(payload.new_password), "user_id": user_id},
            )
            _revoke_sessions(connection, user_id)
            connection.execute(
                text(
                    """
                    UPDATE password_reset_requests
                    SET status = CASE
                            WHEN password_reset_request_id = CAST(:request_id AS uuid) THEN 'CONSUMED'
                            ELSE 'CANCELLED'
                        END,
                        consumed_at = CASE
                            WHEN password_reset_request_id = CAST(:request_id AS uuid) THEN now()
                            ELSE consumed_at
                        END,
                        token_digest = NULL
                    WHERE user_id = CAST(:user_id AS uuid)
                      AND status IN ('PENDING','ISSUED')
                    """
                ),
                {"request_id": request_row["request_id"], "user_id": user_id},
            )
            _account_event(
                connection,
                event_type="PASSWORD_RESET_COMPLETED",
                target_user_id=user_id,
                actor_user_id=user_id,
                details={"request_id": request_row["request_id"]},
            )
        return {"completed": True, "sessions_revoked": True, "message": "Password reset complete. Sign in with the new password."}
    finally:
        engine.dispose()
