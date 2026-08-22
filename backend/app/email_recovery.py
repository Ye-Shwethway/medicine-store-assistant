from __future__ import annotations

import hashlib
import hmac
import html
import json
import os
import re
import secrets
import urllib.error
import urllib.request
from datetime import datetime, timedelta, timezone
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Response, status
from pydantic import BaseModel
from sqlalchemy import text

from app.credential_lifecycle import RESET_TTL_SECONDS, _reset_digest
from app.dashboard_auth import SESSION_SECRET, _engine, require_dashboard_session, verify_password_hash
from app.user_management import _account_event, _notification_event

router = APIRouter(prefix="/dashboard/api", tags=["email-recovery"])
EMAIL_RE = re.compile(r"^[^\s@]+@[^\s@]+\.[^\s@]+$")
VERIFICATION_TTL_SECONDS = 1800


class RecoveryEmailSet(BaseModel):
    current_password: str
    email: str


class RecoveryEmailVerify(BaseModel):
    token: str


class AutomatedPasswordResetRequest(BaseModel):
    username: str


def _no_store(response: Response) -> None:
    response.headers["Cache-Control"] = "no-store"
    response.headers["Pragma"] = "no-cache"


def _resend_api_key() -> str:
    return os.getenv("RESEND_API_KEY", "").strip()


def _from_address() -> str:
    return os.getenv("MSA_RECOVERY_EMAIL_FROM", "").strip()


def _public_base_url() -> str:
    return os.getenv("MSA_PUBLIC_BASE_URL", "https://inventory.drthorne.uk").strip().rstrip("/")


def email_delivery_configured() -> bool:
    return bool(_resend_api_key() and _from_address())


def _verification_digest(token: str) -> str:
    if len(SESSION_SECRET) < 32:
        raise RuntimeError("dashboard session secret is not configured")
    return hmac.new(
        SESSION_SECRET.encode("utf-8"),
        ("recovery-email-verification:" + token).encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()


def _send_resend_email(*, to: str, subject: str, html_body: str, idempotency_key: str) -> str:
    if not email_delivery_configured():
        raise RuntimeError("email delivery is not configured")
    payload = json.dumps(
        {
            "from": _from_address(),
            "to": [to],
            "subject": subject,
            "html": html_body,
        }
    ).encode("utf-8")
    request = urllib.request.Request(
        "https://api.resend.com/emails",
        data=payload,
        method="POST",
        headers={
            "Authorization": f"Bearer {_resend_api_key()}",
            "Content-Type": "application/json",
            "Idempotency-Key": idempotency_key,
        },
    )
    try:
        with urllib.request.urlopen(request, timeout=10) as result:
            data = json.loads(result.read().decode("utf-8"))
    except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError, json.JSONDecodeError) as exc:
        raise RuntimeError("email provider delivery failed") from exc
    provider_id = str(data.get("id") or "").strip()
    if not provider_id:
        raise RuntimeError("email provider returned no message id")
    return provider_id


def _verification_email(email: str, token: str) -> str:
    verify_url = f"{_public_base_url()}/dashboard/login#verify-email={token}"
    safe_url = html.escape(verify_url, quote=True)
    return (
        "<div style='font-family:system-ui,-apple-system,sans-serif;max-width:560px;margin:auto'>"
        "<h2>Verify your Medicine Store Assistant recovery email</h2>"
        "<p>This address was added as a password-recovery destination for your account.</p>"
        f"<p><a href='{safe_url}' style='display:inline-block;padding:12px 18px;background:#0f766e;color:white;text-decoration:none;border-radius:8px'>Verify recovery email</a></p>"
        "<p>This verification link expires in 30 minutes. If you did not request this, you can ignore this email.</p>"
        "</div>"
    )


def _reset_email(token: str) -> str:
    reset_url = f"{_public_base_url()}/dashboard/login#reset={token}"
    safe_url = html.escape(reset_url, quote=True)
    return (
        "<div style='font-family:system-ui,-apple-system,sans-serif;max-width:560px;margin:auto'>"
        "<h2>Reset your Medicine Store Assistant password</h2>"
        "<p>A password reset was requested for your account.</p>"
        f"<p><a href='{safe_url}' style='display:inline-block;padding:12px 18px;background:#0f766e;color:white;text-decoration:none;border-radius:8px'>Reset password</a></p>"
        "<p>This link is short-lived and can be used only once. If you did not request a reset, you can ignore this email.</p>"
        "</div>"
    )


@router.get("/account/recovery-email", summary="Read signed-in recovery email state")
def recovery_email_state(
    response: Response,
    principal: dict[str, str] = Depends(require_dashboard_session),
) -> dict[str, Any]:
    _no_store(response)
    engine = _engine()
    try:
        with engine.connect() as connection:
            row = connection.execute(
                text("SELECT recovery_email, recovery_email_verified_at FROM users WHERE user_id = CAST(:user_id AS uuid)"),
                {"user_id": principal["user_id"]},
            ).mappings().one()
        return {
            "email": row["recovery_email"],
            "verified": row["recovery_email_verified_at"] is not None,
            "verified_at": row["recovery_email_verified_at"],
            "delivery_configured": email_delivery_configured(),
        }
    finally:
        engine.dispose()


@router.post("/account/recovery-email", status_code=status.HTTP_202_ACCEPTED, summary="Send recovery email verification")
def set_recovery_email(
    payload: RecoveryEmailSet,
    response: Response,
    principal: dict[str, str] = Depends(require_dashboard_session),
) -> dict[str, Any]:
    _no_store(response)
    email = payload.email.strip().lower()
    if len(email) > 320 or not EMAIL_RE.fullmatch(email):
        raise HTTPException(status_code=400, detail="Enter a valid email address")
    if not email_delivery_configured():
        raise HTTPException(status_code=503, detail="Recovery email delivery is not configured yet")
    token = secrets.token_urlsafe(32)
    expires_at = datetime.now(timezone.utc) + timedelta(seconds=VERIFICATION_TTL_SECONDS)
    engine = _engine()
    verification_id: str | None = None
    try:
        with engine.begin() as connection:
            user = connection.execute(
                text("SELECT password_hash, state FROM users WHERE user_id = CAST(:user_id AS uuid) FOR UPDATE"),
                {"user_id": principal["user_id"]},
            ).mappings().first()
            if user is None or user["state"] != "ACTIVE":
                raise HTTPException(status_code=401, detail="Dashboard sign-in required")
            if not verify_password_hash(payload.current_password, str(user["password_hash"] or "")):
                raise HTTPException(status_code=401, detail="Current password is incorrect")
            connection.execute(
                text("UPDATE recovery_email_verifications SET status='CANCELLED', token_digest=NULL WHERE user_id=CAST(:user_id AS uuid) AND status='ISSUED'"),
                {"user_id": principal["user_id"]},
            )
            created = connection.execute(
                text(
                    """
                    INSERT INTO recovery_email_verifications (user_id, email, token_digest, expires_at)
                    VALUES (CAST(:user_id AS uuid), :email, :token_digest, :expires_at)
                    RETURNING verification_id::text AS verification_id
                    """
                ),
                {
                    "user_id": principal["user_id"],
                    "email": email,
                    "token_digest": _verification_digest(token),
                    "expires_at": expires_at,
                },
            ).mappings().one()
            verification_id = created["verification_id"]
            _account_event(
                connection,
                event_type="RECOVERY_EMAIL_VERIFICATION_REQUESTED",
                target_user_id=principal["user_id"],
                actor_user_id=principal["user_id"],
                details={"verification_id": verification_id},
            )
        try:
            provider_id = _send_resend_email(
                to=email,
                subject="Verify your Medicine Store Assistant recovery email",
                html_body=_verification_email(email, token),
                idempotency_key=f"msa-recovery-email-verify/{verification_id}",
            )
        except RuntimeError as exc:
            with engine.begin() as connection:
                connection.execute(
                    text("UPDATE recovery_email_verifications SET status='CANCELLED', token_digest=NULL WHERE verification_id=CAST(:verification_id AS uuid)"),
                    {"verification_id": verification_id},
                )
            raise HTTPException(status_code=503, detail="Verification email could not be sent. Try again later.") from exc
        return {"verification_sent": True, "email": email, "expires_at": expires_at, "provider_message_id": provider_id}
    finally:
        engine.dispose()


@router.post("/recovery-email-verifications/complete", summary="Verify a recovery email address")
def verify_recovery_email(payload: RecoveryEmailVerify, response: Response) -> dict[str, Any]:
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
                    SELECT v.verification_id::text AS verification_id, v.user_id::text AS user_id, v.email,
                           v.status, v.expires_at, u.state
                    FROM recovery_email_verifications v
                    JOIN users u ON u.user_id=v.user_id
                    WHERE v.token_digest=:token_digest
                    FOR UPDATE
                    """
                ),
                {"token_digest": _verification_digest(token)},
            ).mappings().first()
            if row is None or row["status"] != "ISSUED" or row["state"] != "ACTIVE" or row["expires_at"] <= datetime.now(timezone.utc):
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
                actor_user_id=row["user_id"],
                details={"verification_id": row["verification_id"]},
            )
        return {"verified": True, "message": "Recovery email verified. You can now use automated password recovery."}
    finally:
        engine.dispose()


@router.post("/password-recovery/request", status_code=status.HTTP_202_ACCEPTED, summary="Request automated password recovery")
def request_automated_password_recovery(payload: AutomatedPasswordResetRequest, response: Response) -> dict[str, Any]:
    _no_store(response)
    generic = {"requested": True, "message": "If the account is eligible, password recovery instructions will be sent."}
    username = payload.username.strip()
    if not username:
        return generic
    engine = _engine()
    token: str | None = None
    request_id: str | None = None
    target_email: str | None = None
    user_id: str | None = None
    expires_at: datetime | None = None
    try:
        with engine.begin() as connection:
            user = connection.execute(
                text(
                    """
                    SELECT user_id::text AS user_id, state, recovery_email, recovery_email_verified_at
                    FROM users WHERE lower(username)=lower(:username) LIMIT 1
                    """
                ),
                {"username": username},
            ).mappings().first()
            if user is None or user["state"] != "ACTIVE":
                return generic
            user_id = user["user_id"]
            connection.execute(
                text("UPDATE password_reset_requests SET status='EXPIRED', token_digest=NULL WHERE user_id=CAST(:user_id AS uuid) AND status='ISSUED' AND expires_at<=now()"),
                {"user_id": user_id},
            )
            existing = connection.execute(
                text("SELECT password_reset_request_id::text AS request_id FROM password_reset_requests WHERE user_id=CAST(:user_id AS uuid) AND status IN ('PENDING','ISSUED') LIMIT 1"),
                {"user_id": user_id},
            ).mappings().first()
            if existing is not None:
                return generic
            created = connection.execute(
                text("INSERT INTO password_reset_requests (user_id) VALUES (CAST(:user_id AS uuid)) RETURNING password_reset_request_id::text AS request_id"),
                {"user_id": user_id},
            ).mappings().one()
            request_id = created["request_id"]
            _account_event(connection, event_type="PASSWORD_RESET_REQUESTED", target_user_id=user_id, actor_user_id=None, details={"request_id": request_id, "source": "WEB"})
            _notification_event(connection, event_type="PASSWORD_RESET_REQUESTED", subject_user_id=user_id, payload={"request_id": request_id, "source": "WEB"})
            if user["recovery_email"] and user["recovery_email_verified_at"] is not None and email_delivery_configured():
                token = secrets.token_urlsafe(32)
                target_email = str(user["recovery_email"])
                expires_at = datetime.now(timezone.utc) + timedelta(seconds=RESET_TTL_SECONDS)
                connection.execute(
                    text(
                        """
                        UPDATE password_reset_requests
                        SET status='ISSUED', token_digest=:token_digest, issued_at=now(), expires_at=:expires_at,
                            delivery_channel='EMAIL', delivery_state='PENDING'
                        WHERE password_reset_request_id=CAST(:request_id AS uuid)
                        """
                    ),
                    {"token_digest": _reset_digest(token), "expires_at": expires_at, "request_id": request_id},
                )
                _account_event(connection, event_type="PASSWORD_RESET_AUTO_ISSUED", target_user_id=user_id, actor_user_id=None, details={"request_id": request_id, "channel": "EMAIL"})
        if token and request_id and target_email and user_id and expires_at:
            try:
                provider_id = _send_resend_email(
                    to=target_email,
                    subject="Reset your Medicine Store Assistant password",
                    html_body=_reset_email(token),
                    idempotency_key=f"msa-password-reset/{request_id}",
                )
            except RuntimeError:
                with engine.begin() as connection:
                    connection.execute(
                        text("UPDATE password_reset_requests SET status='PENDING', token_digest=NULL, issued_at=NULL, expires_at=NULL, delivery_state='FAILED' WHERE password_reset_request_id=CAST(:request_id AS uuid)"),
                        {"request_id": request_id},
                    )
                    _notification_event(connection, event_type="PASSWORD_RESET_EMAIL_FAILED", subject_user_id=user_id, payload={"request_id": request_id})
                return generic
            with engine.begin() as connection:
                connection.execute(
                    text("UPDATE password_reset_requests SET delivery_state='SENT', delivery_provider_id=:provider_id, delivered_at=now() WHERE password_reset_request_id=CAST(:request_id AS uuid)"),
                    {"provider_id": provider_id, "request_id": request_id},
                )
                _notification_event(connection, event_type="PASSWORD_RESET_EMAIL_SENT", subject_user_id=user_id, payload={"request_id": request_id})
        return generic
    finally:
        engine.dispose()
