from __future__ import annotations

from typing import Any, Literal

from fastapi import APIRouter, Depends, HTTPException, Response, status
from pydantic import BaseModel
from sqlalchemy import text

from app.dashboard_auth import _engine, require_dashboard_session, require_owner_session

router = APIRouter(prefix="/dashboard/api/ai-workspace", tags=["ai-workspace-access"])


class GlobalWorkspaceAccessInput(BaseModel):
    non_owner_chat_enabled: bool


class UserWorkspaceAccessInput(BaseModel):
    chat_entitlement: Literal["INHERIT", "ALLOW", "BLOCK"]


def _no_store(response: Response) -> None:
    response.headers["Cache-Control"] = "no-store"
    response.headers["Pragma"] = "no-cache"


def _read_policy_for_user(user_id: str) -> dict[str, Any]:
    engine = _engine()
    try:
        with engine.connect() as connection:
            row = connection.execute(
                text(
                    """
                    SELECT s.non_owner_chat_enabled,
                           COALESCE(a.chat_entitlement, 'INHERIT') AS chat_entitlement
                    FROM ai_workspace_settings s
                    LEFT JOIN ai_workspace_user_access a
                      ON a.user_id = CAST(:user_id AS uuid)
                    WHERE s.settings_id = 1
                    """
                ),
                {"user_id": user_id},
            ).mappings().first()
            if row is None:
                raise RuntimeError("AI Workspace settings are unavailable")
            return dict(row)
    finally:
        engine.dispose()


def evaluate_ai_chat_access(principal: dict[str, str]) -> dict[str, Any]:
    if principal["role"] == "OWNER":
        return {
            "allowed": True,
            "reason": "OWNER_BYPASS",
            "non_owner_chat_enabled": None,
            "chat_entitlement": "ALLOW",
        }

    policy = _read_policy_for_user(principal["user_id"])
    global_enabled = bool(policy["non_owner_chat_enabled"])
    entitlement = str(policy["chat_entitlement"])

    if not global_enabled:
        return {
            "allowed": False,
            "reason": "GLOBAL_DISABLED",
            "non_owner_chat_enabled": False,
            "chat_entitlement": entitlement,
        }
    if entitlement == "BLOCK":
        return {
            "allowed": False,
            "reason": "USER_BLOCKED",
            "non_owner_chat_enabled": True,
            "chat_entitlement": entitlement,
        }
    return {
        "allowed": True,
        "reason": "USER_ALLOWED" if entitlement == "ALLOW" else "GLOBAL_INHERIT",
        "non_owner_chat_enabled": True,
        "chat_entitlement": entitlement,
    }


def require_ai_chat_access(
    principal: dict[str, str] = Depends(require_dashboard_session),
) -> dict[str, str]:
    decision = evaluate_ai_chat_access(principal)
    if not decision["allowed"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "code": "AI_WORKSPACE_CHAT_DISABLED",
                "reason": decision["reason"],
                "message": "AI Chat is not enabled for this account.",
                "provider_invoked": False,
            },
        )
    return principal


@router.get("/access", summary="Read current user's effective AI Chat access")
def get_effective_access(
    response: Response,
    principal: dict[str, str] = Depends(require_dashboard_session),
) -> dict[str, Any]:
    _no_store(response)
    decision = evaluate_ai_chat_access(principal)
    return {
        "user_id": principal["user_id"],
        "role": principal["role"],
        **decision,
        "multi_agent_allowed": principal["role"] == "OWNER",
    }


@router.get("/settings", summary="Read Owner AI Workspace settings")
def get_workspace_settings(
    response: Response,
    owner: dict[str, str] = Depends(require_owner_session),
) -> dict[str, Any]:
    del owner
    _no_store(response)
    engine = _engine()
    try:
        with engine.connect() as connection:
            row = connection.execute(
                text(
                    """
                    SELECT settings_id, non_owner_chat_enabled,
                           updated_by_user_id::text AS updated_by_user_id,
                           created_at, updated_at
                    FROM ai_workspace_settings
                    WHERE settings_id = 1
                    """
                )
            ).mappings().one()
            return dict(row)
    finally:
        engine.dispose()


@router.put("/settings", summary="Update Owner AI Workspace settings")
def update_workspace_settings(
    payload: GlobalWorkspaceAccessInput,
    response: Response,
    owner: dict[str, str] = Depends(require_owner_session),
) -> dict[str, Any]:
    _no_store(response)
    engine = _engine()
    try:
        with engine.begin() as connection:
            row = connection.execute(
                text(
                    """
                    UPDATE ai_workspace_settings
                    SET non_owner_chat_enabled=:enabled,
                        updated_by_user_id=CAST(:owner_id AS uuid),
                        updated_at=now()
                    WHERE settings_id=1
                    RETURNING settings_id, non_owner_chat_enabled,
                              updated_by_user_id::text AS updated_by_user_id,
                              created_at, updated_at
                    """
                ),
                {"enabled": payload.non_owner_chat_enabled, "owner_id": owner["user_id"]},
            ).mappings().one()
            return dict(row)
    finally:
        engine.dispose()


@router.put("/users/{user_id}/access", summary="Set one non-Owner user's AI Chat entitlement")
def set_user_workspace_access(
    user_id: str,
    payload: UserWorkspaceAccessInput,
    response: Response,
    owner: dict[str, str] = Depends(require_owner_session),
) -> dict[str, Any]:
    _no_store(response)
    engine = _engine()
    try:
        with engine.begin() as connection:
            target = connection.execute(
                text(
                    """
                    SELECT u.user_id::text AS user_id, u.state, ur.role_code AS role
                    FROM users u
                    LEFT JOIN user_roles ur ON ur.user_id=u.user_id
                    WHERE u.user_id=CAST(:user_id AS uuid)
                    """
                ),
                {"user_id": user_id},
            ).mappings().first()
            if target is None:
                raise HTTPException(status_code=404, detail="User not found")
            if target["role"] == "OWNER":
                raise HTTPException(status_code=409, detail="Owner AI Workspace access is always enabled")

            row = connection.execute(
                text(
                    """
                    INSERT INTO ai_workspace_user_access (
                        user_id, chat_entitlement, updated_by_user_id
                    ) VALUES (
                        CAST(:user_id AS uuid), :entitlement, CAST(:owner_id AS uuid)
                    )
                    ON CONFLICT (user_id) DO UPDATE SET
                        chat_entitlement=EXCLUDED.chat_entitlement,
                        updated_by_user_id=EXCLUDED.updated_by_user_id,
                        updated_at=now()
                    RETURNING user_id::text AS user_id, chat_entitlement,
                              updated_by_user_id::text AS updated_by_user_id,
                              created_at, updated_at
                    """
                ),
                {
                    "user_id": user_id,
                    "entitlement": payload.chat_entitlement,
                    "owner_id": owner["user_id"],
                },
            ).mappings().one()
            return dict(row)
    finally:
        engine.dispose()
