from __future__ import annotations

from typing import Literal

from fastapi import APIRouter, Response, status
from pydantic import BaseModel
from sqlalchemy import text

from app.dashboard_auth import _engine
from app.email_recovery import AutomatedPasswordResetRequest, request_automated_password_recovery

router = APIRouter(prefix="/dashboard/api", tags=["email-recovery"])


class RecoveryIdentifierRequest(BaseModel):
    mode: Literal["username", "email"]
    identifier: str


def _generic() -> dict[str, object]:
    return {
        "requested": True,
        "message": "If the account is eligible, password recovery instructions will be sent.",
    }


@router.post(
    "/password-recovery/request-by-identifier",
    status_code=status.HTTP_202_ACCEPTED,
    summary="Request automated password recovery by username or verified email",
)
def request_password_recovery_by_identifier(
    payload: RecoveryIdentifierRequest,
    response: Response,
) -> dict[str, object]:
    response.headers["Cache-Control"] = "no-store"
    response.headers["Pragma"] = "no-cache"
    identifier = payload.identifier.strip()
    if not identifier:
        return _generic()

    if payload.mode == "username":
        return request_automated_password_recovery(
            AutomatedPasswordResetRequest(username=identifier),
            response,
        )

    engine = _engine()
    try:
        with engine.connect() as connection:
            matches = connection.execute(
                text(
                    """
                    SELECT username
                    FROM users
                    WHERE state = 'ACTIVE'
                      AND recovery_email_verified_at IS NOT NULL
                      AND lower(recovery_email) = lower(:email)
                    ORDER BY user_id
                    LIMIT 2
                    """
                ),
                {"email": identifier},
            ).scalars().all()
    finally:
        engine.dispose()

    # A shared recovery address is intentionally treated as ambiguous rather
    # than choosing an arbitrary account. The public response stays generic.
    if len(matches) != 1:
        return _generic()

    return request_automated_password_recovery(
        AutomatedPasswordResetRequest(username=str(matches[0])),
        response,
    )
