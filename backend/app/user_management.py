from __future__ import annotations

import re
from typing import Any, Literal

from fastapi import APIRouter, Depends, HTTPException, Response, status
from pydantic import BaseModel
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError

from app.dashboard_auth import _engine, make_password_hash, require_owner_session, revoke_user_sessions

router = APIRouter(prefix="/dashboard/api", tags=["user-management"])
USERNAME_RE = re.compile(r"^[A-Za-z0-9._-]{3,64}$")
ASSIGNABLE_ROLES = frozenset({"ADMIN", "STAFF", "READ_ONLY"})


class AccessRequestCreate(BaseModel):
    display_name: str
    username: str
    password: str


class RoleChange(BaseModel):
    role: Literal["ADMIN", "STAFF", "READ_ONLY"]


def _no_store(response: Response) -> None:
    response.headers["Cache-Control"] = "no-store"
    response.headers["Pragma"] = "no-cache"


def _validate_access_request(payload: AccessRequestCreate) -> tuple[str, str, str]:
    display_name = payload.display_name.strip()
    username = payload.username.strip()
    password = payload.password
    if not display_name or len(display_name) > 160:
        raise HTTPException(status_code=400, detail="Enter a valid display name")
    if not USERNAME_RE.fullmatch(username):
        raise HTTPException(status_code=400, detail="Username must be 3–64 letters, numbers, dots, dashes, or underscores")
    if len(password) < 10 or len(password) > 256:
        raise HTTPException(status_code=400, detail="Password must be at least 10 characters")
    return display_name, username, password


def _account_event(connection, *, event_type: str, target_user_id: str, actor_user_id: str | None, details: dict[str, Any] | None = None) -> None:
    connection.execute(
        text(
            """
            INSERT INTO account_security_events (event_type, actor_user_id, target_user_id, details)
            VALUES (:event_type, CAST(:actor_user_id AS uuid), CAST(:target_user_id AS uuid), CAST(:details AS jsonb))
            """
        ),
        {
            "event_type": event_type,
            "actor_user_id": actor_user_id,
            "target_user_id": target_user_id,
            "details": __import__("json").dumps(details or {}),
        },
    )


def _notification_event(connection, *, event_type: str, subject_user_id: str, payload: dict[str, Any] | None = None) -> None:
    connection.execute(
        text(
            """
            INSERT INTO notification_events (event_type, subject_user_id, payload)
            VALUES (:event_type, CAST(:subject_user_id AS uuid), CAST(:payload AS jsonb))
            """
        ),
        {
            "event_type": event_type,
            "subject_user_id": subject_user_id,
            "payload": __import__("json").dumps(payload or {}),
        },
    )


def _target_user(connection, user_id: str):
    return connection.execute(
        text(
            """
            SELECT u.user_id::text AS user_id,
                   u.display_name,
                   u.username,
                   u.state,
                   ur.role_code AS role
            FROM users u
            LEFT JOIN user_roles ur ON ur.user_id = u.user_id
            WHERE u.user_id = CAST(:user_id AS uuid)
            LIMIT 1
            """
        ),
        {"user_id": user_id},
    ).mappings().first()


def _require_non_owner_target(connection, user_id: str):
    target = _target_user(connection, user_id)
    if target is None:
        raise HTTPException(status_code=404, detail="User not found")
    if target["role"] == "OWNER":
        raise HTTPException(status_code=403, detail="Owner account requires the separate high-risk Owner flow")
    return target


@router.post("/access-requests", status_code=status.HTTP_202_ACCEPTED, summary="Request dashboard access")
def request_access(payload: AccessRequestCreate, response: Response) -> dict[str, Any]:
    _no_store(response)
    display_name, username, password = _validate_access_request(payload)
    engine = _engine()
    try:
        try:
            with engine.begin() as connection:
                created = connection.execute(
                    text(
                        """
                        INSERT INTO users (display_name, username, password_hash, state)
                        VALUES (:display_name, :username, :password_hash, 'PENDING')
                        RETURNING user_id::text AS user_id
                        """
                    ),
                    {
                        "display_name": display_name,
                        "username": username,
                        "password_hash": make_password_hash(password),
                    },
                ).mappings().one()
                user_id = created["user_id"]
                connection.execute(
                    text("INSERT INTO access_requests (user_id) VALUES (CAST(:user_id AS uuid))"),
                    {"user_id": user_id},
                )
                _account_event(
                    connection,
                    event_type="ACCESS_REQUEST_CREATED",
                    target_user_id=user_id,
                    actor_user_id=None,
                    details={"source": "WEB"},
                )
                _notification_event(
                    connection,
                    event_type="ACCESS_REQUEST_PENDING",
                    subject_user_id=user_id,
                    payload={"source": "WEB"},
                )
        except IntegrityError:
            # Keep public response generic so username existence is not disclosed.
            pass
        return {
            "requested": True,
            "message": "If the request can be created, it is pending Owner review.",
        }
    finally:
        engine.dispose()


@router.get("/users", summary="List human users", dependencies=[Depends(require_owner_session)])
def list_users(response: Response) -> dict[str, Any]:
    _no_store(response)
    engine = _engine()
    try:
        with engine.connect() as connection:
            rows = connection.execute(
                text(
                    """
                    SELECT u.user_id::text AS user_id,
                           u.display_name,
                           u.username,
                           u.state,
                           ur.role_code AS role,
                           ar.status AS request_status,
                           ar.requested_at,
                           ar.resolved_at,
                           u.created_at,
                           u.disabled_at,
                           EXISTS (
                               SELECT 1 FROM user_sessions s
                               WHERE s.user_id = u.user_id
                                 AND s.revoked_at IS NULL
                                 AND s.expires_at > now()
                           ) AS has_active_session
                    FROM users u
                    LEFT JOIN user_roles ur ON ur.user_id = u.user_id
                    LEFT JOIN access_requests ar ON ar.user_id = u.user_id
                    ORDER BY
                        CASE WHEN ar.status = 'PENDING' THEN 0 WHEN u.state = 'ACTIVE' THEN 1 ELSE 2 END,
                        COALESCE(ar.requested_at, u.created_at),
                        u.username
                    """
                )
            ).mappings().all()
        return {"items": [dict(row) for row in rows], "count": len(rows)}
    finally:
        engine.dispose()


@router.post("/users/{user_id}/approve", summary="Approve pending access request")
def approve_user(
    user_id: str,
    payload: RoleChange,
    response: Response,
    owner: dict[str, str] = Depends(require_owner_session),
) -> dict[str, Any]:
    _no_store(response)
    role = payload.role.upper()
    if role not in ASSIGNABLE_ROLES:
        raise HTTPException(status_code=400, detail="Role is not assignable in ordinary User Management")
    engine = _engine()
    try:
        with engine.begin() as connection:
            target = _require_non_owner_target(connection, user_id)
            request_row = connection.execute(
                text("SELECT status FROM access_requests WHERE user_id = CAST(:user_id AS uuid) FOR UPDATE"),
                {"user_id": user_id},
            ).mappings().first()
            if target["state"] != "PENDING" or request_row is None or request_row["status"] != "PENDING":
                raise HTTPException(status_code=409, detail="User does not have a pending access request")
            connection.execute(
                text(
                    """
                    INSERT INTO user_roles (user_id, role_code)
                    VALUES (CAST(:user_id AS uuid), :role)
                    ON CONFLICT (user_id) DO UPDATE SET role_code = EXCLUDED.role_code, assigned_at = now()
                    """
                ),
                {"user_id": user_id, "role": role},
            )
            connection.execute(
                text("UPDATE users SET state = 'ACTIVE', disabled_at = NULL, updated_at = now() WHERE user_id = CAST(:user_id AS uuid)"),
                {"user_id": user_id},
            )
            connection.execute(
                text(
                    """
                    UPDATE access_requests
                    SET status = 'APPROVED', assigned_role = :role, resolved_at = now(), resolved_by_user_id = CAST(:owner_id AS uuid)
                    WHERE user_id = CAST(:user_id AS uuid)
                    """
                ),
                {"user_id": user_id, "role": role, "owner_id": owner["user_id"]},
            )
            _account_event(connection, event_type="ACCESS_APPROVED", target_user_id=user_id, actor_user_id=owner["user_id"], details={"role": role})
            _notification_event(connection, event_type="ACCESS_APPROVED", subject_user_id=user_id, payload={"role": role})
        return {"user_id": user_id, "state": "ACTIVE", "role": role}
    finally:
        engine.dispose()


@router.post("/users/{user_id}/reject", summary="Reject pending access request")
def reject_user(user_id: str, response: Response, owner: dict[str, str] = Depends(require_owner_session)) -> dict[str, Any]:
    _no_store(response)
    engine = _engine()
    try:
        with engine.begin() as connection:
            target = _require_non_owner_target(connection, user_id)
            request_row = connection.execute(
                text("SELECT status FROM access_requests WHERE user_id = CAST(:user_id AS uuid) FOR UPDATE"),
                {"user_id": user_id},
            ).mappings().first()
            if target["state"] != "PENDING" or request_row is None or request_row["status"] != "PENDING":
                raise HTTPException(status_code=409, detail="User does not have a pending access request")
            connection.execute(
                text("UPDATE users SET state = 'DISABLED', disabled_at = now(), updated_at = now() WHERE user_id = CAST(:user_id AS uuid)"),
                {"user_id": user_id},
            )
            connection.execute(
                text(
                    """
                    UPDATE access_requests
                    SET status = 'REJECTED', resolved_at = now(), resolved_by_user_id = CAST(:owner_id AS uuid)
                    WHERE user_id = CAST(:user_id AS uuid)
                    """
                ),
                {"user_id": user_id, "owner_id": owner["user_id"]},
            )
            _account_event(connection, event_type="ACCESS_REJECTED", target_user_id=user_id, actor_user_id=owner["user_id"])
            _notification_event(connection, event_type="ACCESS_REJECTED", subject_user_id=user_id)
        return {"user_id": user_id, "state": "DISABLED", "request_status": "REJECTED"}
    finally:
        engine.dispose()


@router.patch("/users/{user_id}/role", summary="Change a non-Owner human role")
def change_role(
    user_id: str,
    payload: RoleChange,
    response: Response,
    owner: dict[str, str] = Depends(require_owner_session),
) -> dict[str, Any]:
    _no_store(response)
    role = payload.role.upper()
    engine = _engine()
    try:
        with engine.begin() as connection:
            target = _require_non_owner_target(connection, user_id)
            if target["state"] != "ACTIVE":
                raise HTTPException(status_code=409, detail="Only active users can change role")
            connection.execute(
                text(
                    """
                    INSERT INTO user_roles (user_id, role_code)
                    VALUES (CAST(:user_id AS uuid), :role)
                    ON CONFLICT (user_id) DO UPDATE SET role_code = EXCLUDED.role_code, assigned_at = now()
                    """
                ),
                {"user_id": user_id, "role": role},
            )
            revoke_user_sessions(user_id)
            _account_event(
                connection,
                event_type="ROLE_CHANGED",
                target_user_id=user_id,
                actor_user_id=owner["user_id"],
                details={"from": target["role"], "to": role},
            )
        return {"user_id": user_id, "state": "ACTIVE", "role": role, "sessions_revoked": True}
    finally:
        engine.dispose()


@router.post("/users/{user_id}/disable", summary="Disable a non-Owner user")
def disable_user(user_id: str, response: Response, owner: dict[str, str] = Depends(require_owner_session)) -> dict[str, Any]:
    _no_store(response)
    engine = _engine()
    try:
        with engine.begin() as connection:
            target = _require_non_owner_target(connection, user_id)
            if target["state"] == "DISABLED":
                return {"user_id": user_id, "state": "DISABLED", "sessions_revoked": True}
            connection.execute(
                text("UPDATE users SET state = 'DISABLED', disabled_at = now(), updated_at = now() WHERE user_id = CAST(:user_id AS uuid)"),
                {"user_id": user_id},
            )
            revoke_user_sessions(user_id)
            _account_event(connection, event_type="ACCOUNT_DISABLED", target_user_id=user_id, actor_user_id=owner["user_id"])
            _notification_event(connection, event_type="ACCOUNT_DISABLED", subject_user_id=user_id)
        return {"user_id": user_id, "state": "DISABLED", "sessions_revoked": True}
    finally:
        engine.dispose()


@router.post("/users/{user_id}/reactivate", summary="Reactivate a non-Owner user")
def reactivate_user(user_id: str, response: Response, owner: dict[str, str] = Depends(require_owner_session)) -> dict[str, Any]:
    _no_store(response)
    engine = _engine()
    try:
        with engine.begin() as connection:
            target = _require_non_owner_target(connection, user_id)
            if not target["role"]:
                raise HTTPException(status_code=409, detail="Assign an approved role before reactivation")
            connection.execute(
                text("UPDATE users SET state = 'ACTIVE', disabled_at = NULL, updated_at = now() WHERE user_id = CAST(:user_id AS uuid)"),
                {"user_id": user_id},
            )
            _account_event(connection, event_type="ACCOUNT_REACTIVATED", target_user_id=user_id, actor_user_id=owner["user_id"])
            _notification_event(connection, event_type="ACCOUNT_REACTIVATED", subject_user_id=user_id)
        return {"user_id": user_id, "state": "ACTIVE", "role": target["role"]}
    finally:
        engine.dispose()


@router.post("/users/{user_id}/revoke-sessions", summary="Revoke a non-Owner user's sessions")
def revoke_sessions(user_id: str, response: Response, owner: dict[str, str] = Depends(require_owner_session)) -> dict[str, Any]:
    _no_store(response)
    engine = _engine()
    try:
        with engine.begin() as connection:
            _require_non_owner_target(connection, user_id)
            revoke_user_sessions(user_id)
            _account_event(connection, event_type="SESSIONS_REVOKED", target_user_id=user_id, actor_user_id=owner["user_id"])
        return {"user_id": user_id, "sessions_revoked": True}
    finally:
        engine.dispose()
