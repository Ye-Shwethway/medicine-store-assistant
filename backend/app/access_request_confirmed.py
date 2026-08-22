from __future__ import annotations

import html
import secrets
from datetime import datetime, timedelta, timezone
from typing import Any

from fastapi import APIRouter, HTTPException, Response, status
from pydantic import BaseModel
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError

from app.dashboard_auth import _engine, make_password_hash
from app.email_recovery import (
    EMAIL_RE,
    VERIFICATION_TTL_SECONDS,
    _public_base_url,
    _send_resend_email,
    _verification_digest,
    email_delivery_configured,
)
from app.user_management import AccessRequestCreate, _account_event, _notification_event, _validate_access_request

router = APIRouter(prefix="/dashboard/api", tags=["user-management"])


class ConfirmedAccessRequestCreate(BaseModel):
    display_name: str
    username: str
    email: str
    password: str
    confirm_password: str


class AccessEmailVerify(BaseModel):
    token: str


def _no_store(response: Response) -> None:
    response.headers["Cache-Control"] = "no-store"
    response.headers["Pragma"] = "no-cache"


def _access_verification_email(token: str) -> str:
    verify_url = f"{_public_base_url()}/dashboard/login#verify-access-email={token}"
    safe_url = html.escape(verify_url, quote=True)
    return (
        "<div style='font-family:system-ui,-apple-system,sans-serif;max-width:560px;margin:auto'>"
        "<h2>Verify your Medicine Store Assistant email</h2>"
        "<p>Your access request is pending Owner review. Verify this address now so automated password recovery is ready if your request is approved.</p>"
        f"<p><a href='{safe_url}' style='display:inline-block;padding:12px 18px;background:#0f766e;color:white;text-decoration:none;border-radius:8px'>Verify email</a></p>"
        "<p>This verification link expires in 30 minutes. Verification does not grant dashboard access or assign a role.</p>"
        "</div>"
    )


@router.post("/access-requests/confirmed", status_code=status.HTTP_202_ACCEPTED, summary="Request dashboard access with email and password confirmation")
def request_access_confirmed(payload: ConfirmedAccessRequestCreate, response: Response) -> dict[str, Any]:
    _no_store(response)
    if payload.password != payload.confirm_password:
        raise HTTPException(status_code=400, detail="Passwords do not match")

    display_name, username, password = _validate_access_request(
        AccessRequestCreate(
            display_name=payload.display_name,
            username=payload.username,
            password=payload.password,
        )
    )
    email = payload.email.strip().lower()
    if len(email) > 320 or not EMAIL_RE.fullmatch(email):
        raise HTTPException(status_code=400, detail="Enter a valid email address")
    if not email_delivery_configured():
        raise HTTPException(status_code=503, detail="Email verification is not configured yet")

    token = secrets.token_urlsafe(32)
    expires_at = datetime.now(timezone.utc) + timedelta(seconds=VERIFICATION_TTL_SECONDS)
    engine = _engine()
    user_id: str | None = None
    verification_id: str | None = None
    try:
        try:
            with engine.begin() as connection:
                created = connection.execute(
                    text(
                        """
                        INSERT INTO users (display_name, username, password_hash, state, recovery_email)
                        VALUES (:display_name, :username, :password_hash, 'PENDING', :email)
                        RETURNING user_id::text AS user_id
                        """
                    ),
                    {
                        "display_name": display_name,
                        "username": username,
                        "password_hash": make_password_hash(password),
                        "email": email,
                    },
                ).mappings().one()
                user_id = created["user_id"]
                connection.execute(
                    text("INSERT INTO access_requests (user_id) VALUES (CAST(:user_id AS uuid))"),
                    {"user_id": user_id},
                )
                verification = connection.execute(
                    text(
                        """
                        INSERT INTO recovery_email_verifications (user_id, email, token_digest, expires_at)
                        VALUES (CAST(:user_id AS uuid), :email, :token_digest, :expires_at)
                        RETURNING verification_id::text AS verification_id
                        """
                    ),
                    {
                        "user_id": user_id,
                        "email": email,
                        "token_digest": _verification_digest(token),
                        "expires_at": expires_at,
                    },
                ).mappings().one()
                verification_id = verification["verification_id"]
                _account_event(connection, event_type="ACCESS_REQUEST_CREATED", target_user_id=user_id, actor_user_id=None, details={"source": "WEB"})
                _account_event(
                    connection,
                    event_type="RECOVERY_EMAIL_VERIFICATION_REQUESTED",
                    target_user_id=user_id,
                    actor_user_id=None,
                    details={"verification_id": verification_id, "source": "ACCESS_REQUEST"},
                )
                _notification_event(connection, event_type="ACCESS_REQUEST_PENDING", subject_user_id=user_id, payload={"source": "WEB"})
        except IntegrityError:
            return {
                "requested": True,
                "verification_sent": False,
                "message": "If the request can be created, it is pending Owner review. Check your email for a verification link if one was issued.",
            }

        try:
            provider_id = _send_resend_email(
                to=email,
                subject="Verify your Medicine Store Assistant email",
                html_body=_access_verification_email(token),
                idempotency_key=f"msa-access-email-verify/{verification_id}",
            )
        except RuntimeError:
            with engine.begin() as connection:
                connection.execute(
                    text("UPDATE recovery_email_verifications SET status='CANCELLED', token_digest=NULL WHERE verification_id=CAST(:verification_id AS uuid)"),
                    {"verification_id": verification_id},
                )
                _notification_event(
                    connection,
                    event_type="RECOVERY_EMAIL_VERIFICATION_FAILED",
                    subject_user_id=user_id,
                    payload={"verification_id": verification_id, "source": "ACCESS_REQUEST"},
                )
            return {
                "requested": True,
                "verification_sent": False,
                "message": "Access request submitted for Owner review, but the verification email could not be sent. If approved, you can verify an email from Account security after signing in.",
            }

        with engine.begin() as connection:
            _notification_event(
                connection,
                event_type="RECOVERY_EMAIL_VERIFICATION_SENT",
                subject_user_id=user_id,
                payload={"verification_id": verification_id, "provider_message_id": provider_id, "source": "ACCESS_REQUEST"},
            )
        return {
            "requested": True,
            "verification_sent": True,
            "message": "Access request submitted. Check your email to verify your recovery address while the Owner reviews your request.",
        }
    finally:
        engine.dispose()


@router.post("/access-email-verifications/complete", summary="Verify recovery email for a pending access request")
def verify_access_email(payload: AccessEmailVerify, response: Response) -> dict[str, Any]:
    _no_store(response)
    token = payload.token.strip()
    if len(token) < 32 or len(token) > 256:
        raise HTTPException(status_code=400, detail="Verification link is invalid or expired")
    engine = _engine()
    try:
        with engine.begin() as connection:
            row = connection.execute(
                text(
                    """
                    SELECT v.verification_id::text AS verification_id, v.user_id::text AS user_id,
                           v.email, v.status, v.expires_at, u.state
                    FROM recovery_email_verifications v
                    JOIN users u ON u.user_id=v.user_id
                    WHERE v.token_digest=:token_digest
                    FOR UPDATE
                    """
                ),
                {"token_digest": _verification_digest(token)},
            ).mappings().first()
            if row is None or row["status"] != "ISSUED" or row["state"] not in {"PENDING", "ACTIVE"} or row["expires_at"] <= datetime.now(timezone.utc):
                raise HTTPException(status_code=400, detail="Verification link is invalid or expired")
            connection.execute(
                text("UPDATE users SET recovery_email=:email, recovery_email_verified_at=now(), updated_at=now() WHERE user_id=CAST(:user_id AS uuid)"),
                {"email": row["email"], "user_id": row["user_id"]},
            )
            connection.execute(
                text("UPDATE recovery_email_verifications SET status='CONSUMED', consumed_at=now(), token_digest=NULL WHERE verification_id=CAST(:verification_id AS uuid)"),
                {"verification_id": row["verification_id"]},
            )
            _account_event(
                connection,
                event_type="RECOVERY_EMAIL_VERIFIED",
                target_user_id=row["user_id"],
                actor_user_id=None,
                details={"verification_id": row["verification_id"], "source": "ACCESS_REQUEST"},
            )
        return {
            "verified": True,
            "message": "Email verified. Your access request still requires Owner approval before you can sign in.",
        }
    finally:
        engine.dispose()
