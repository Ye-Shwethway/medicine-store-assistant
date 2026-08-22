from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Response, status
from pydantic import BaseModel

from app.user_management import AccessRequestCreate, request_access

router = APIRouter(prefix="/dashboard/api", tags=["user-management"])


class ConfirmedAccessRequestCreate(BaseModel):
    display_name: str
    username: str
    password: str
    confirm_password: str


@router.post("/access-requests/confirmed", status_code=status.HTTP_202_ACCEPTED, summary="Request dashboard access with password confirmation")
def request_access_confirmed(payload: ConfirmedAccessRequestCreate, response: Response) -> dict[str, Any]:
    if payload.password != payload.confirm_password:
        response.headers["Cache-Control"] = "no-store"
        response.headers["Pragma"] = "no-cache"
        from fastapi import HTTPException
        raise HTTPException(status_code=400, detail="Passwords do not match")
    return request_access(
        AccessRequestCreate(
            display_name=payload.display_name,
            username=payload.username,
            password=payload.password,
        ),
        response,
    )
