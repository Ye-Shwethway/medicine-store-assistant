from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Response
from pydantic import BaseModel

from app.credential_lifecycle import PasswordChange, change_password
from app.dashboard_auth import require_dashboard_session

router = APIRouter(prefix="/dashboard/api", tags=["credential-lifecycle"])


class ConfirmedPasswordChange(BaseModel):
    current_password: str
    new_password: str
    confirm_password: str


@router.post("/account/password-confirmed", summary="Change password with confirmation")
def change_password_confirmed(
    payload: ConfirmedPasswordChange,
    response: Response,
    principal: dict[str, str] = Depends(require_dashboard_session),
):
    if payload.new_password != payload.confirm_password:
        raise HTTPException(status_code=400, detail="New passwords do not match")
    return change_password(
        PasswordChange(
            current_password=payload.current_password,
            new_password=payload.new_password,
        ),
        response,
        principal,
    )
