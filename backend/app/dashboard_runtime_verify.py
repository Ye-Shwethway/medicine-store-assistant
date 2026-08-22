from __future__ import annotations

import json
import os
import secrets
import urllib.error
import urllib.request

from sqlalchemy import text

from app.dashboard_auth import (
    SESSION_COOKIE,
    _engine,
    authenticate_user,
    create_session_token,
    ensure_bootstrap_owner,
    revoke_session_token,
)


def _request_json(
    base_url: str,
    path: str,
    cookie: str | None = None,
    *,
    expected_status: int = 200,
    method: str = "GET",
    payload: dict | None = None,
) -> dict:
    headers = {"Accept": "application/json"}
    if cookie:
        headers["Cookie"] = f"{SESSION_COOKIE}={cookie}"
    data = None
    if payload is not None:
        headers["Content-Type"] = "application/json"
        data = json.dumps(payload).encode("utf-8")
    request = urllib.request.Request(f"{base_url}{path}", headers=headers, data=data, method=method)
    try:
        with urllib.request.urlopen(request, timeout=10) as response:
            body = response.read().decode("utf-8")
            if response.status != expected_status:
                raise SystemExit(f"dashboard runtime verification failed: {path} -> HTTP {response.status}")
            return json.loads(body)
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        if exc.code != expected_status:
            raise SystemExit(f"dashboard runtime verification failed: {path} -> HTTP {exc.code}: {body[:240]}") from exc
        return json.loads(body)


def _cleanup_users(engine, user_ids: list[str]) -> None:
    if not user_ids:
        return
    with engine.begin() as connection:
        for user_id in user_ids:
            params = {"user_id": user_id}
            connection.execute(text("DELETE FROM notification_events WHERE subject_user_id = CAST(:user_id AS uuid)"), params)
            connection.execute(text("DELETE FROM account_security_events WHERE target_user_id = CAST(:user_id AS uuid)"), params)
            connection.execute(text("DELETE FROM access_requests WHERE user_id = CAST(:user_id AS uuid)"), params)
            connection.execute(text("DELETE FROM user_sessions WHERE user_id = CAST(:user_id AS uuid)"), params)
            connection.execute(text("DELETE FROM user_roles WHERE user_id = CAST(:user_id AS uuid)"), params)
            connection.execute(text("DELETE FROM users WHERE user_id = CAST(:user_id AS uuid)"), params)


def main() -> None:
    base_url = os.environ.get("MSA_DASHBOARD_VERIFY_BASE_URL")
    if not base_url:
        port = os.environ.get("MSA_API_HOST_PORT", "8088")
        base_url = f"http://127.0.0.1:{port}"
    base_url = base_url.rstrip("/")

    owner = ensure_bootstrap_owner()
    if owner["role"] != "OWNER" or owner["state"] != "ACTIVE" or not owner["user_id"]:
        raise SystemExit("F7.2 verification failed: canonical Owner is invalid")
    owner_cookie = create_session_token(owner["user_id"])

    overview = _request_json(base_url, "/dashboard/api/overview", owner_cookie)
    batch = overview.get("batch")
    if not batch or int(batch.get("row_count") or 0) <= 0:
        raise SystemExit("dashboard runtime verification failed: overview has no test-only batch")
    if overview.get("database_canonical") is not False or overview.get("migration_baseline_accepted") is not False:
        raise SystemExit("dashboard runtime verification failed: authority flags changed")

    rows = _request_json(base_url, "/dashboard/api/rows?limit=5&offset=0", owner_cookie)
    if int(rows.get("count") or 0) <= 0 or not rows.get("items"):
        raise SystemExit("dashboard runtime verification failed: authenticated rows endpoint returned no rows")
    _request_json(base_url, "/dashboard/api/authorization/owner", owner_cookie)

    engine = _engine()
    created_user_ids: list[str] = []
    active_cookie: str | None = None
    reject_username = f"f72b-reject-{secrets.token_hex(5)}"
    username = f"f72b-verify-{secrets.token_hex(5)}"
    password = secrets.token_urlsafe(18)
    try:
        # Public request creates PENDING identity only; it cannot authenticate yet.
        requested = _request_json(
            base_url,
            "/dashboard/api/access-requests",
            expected_status=202,
            method="POST",
            payload={"display_name": "F7.2B verification user", "username": username, "password": password},
        )
        if requested.get("requested") is not True:
            raise SystemExit("F7.2B verification failed: request access response was not accepted")

        with engine.connect() as connection:
            pending = connection.execute(
                text(
                    """
                    SELECT u.user_id::text AS user_id, u.state, ar.status AS request_status,
                           (SELECT COUNT(*) FROM user_roles ur WHERE ur.user_id = u.user_id) AS role_count,
                           (SELECT COUNT(*) FROM account_security_events ase WHERE ase.target_user_id = u.user_id AND ase.event_type = 'ACCESS_REQUEST_CREATED') AS security_events,
                           (SELECT COUNT(*) FROM notification_events ne WHERE ne.subject_user_id = u.user_id AND ne.event_type = 'ACCESS_REQUEST_PENDING') AS notification_events
                    FROM users u JOIN access_requests ar ON ar.user_id = u.user_id
                    WHERE u.username = :username
                    """
                ),
                {"username": username},
            ).mappings().one()
        user_id = pending["user_id"]
        created_user_ids.append(user_id)
        if pending["state"] != "PENDING" or pending["request_status"] != "PENDING" or int(pending["role_count"]) != 0:
            raise SystemExit("F7.2B verification failed: request did not remain pending/unassigned")
        if int(pending["security_events"]) < 1 or int(pending["notification_events"]) < 1:
            raise SystemExit("F7.2B verification failed: pending request events were not persisted")
        if authenticate_user(username, password) is not None:
            raise SystemExit("F7.2B verification failed: pending user authenticated")

        owner_users = _request_json(base_url, "/dashboard/api/users", owner_cookie)
        if not any(item.get("user_id") == user_id and item.get("request_status") == "PENDING" for item in owner_users.get("items", [])):
            raise SystemExit("F7.2B verification failed: Owner User Management did not list pending request")

        approved = _request_json(
            base_url,
            f"/dashboard/api/users/{user_id}/approve",
            owner_cookie,
            method="POST",
            payload={"role": "READ_ONLY"},
        )
        if approved.get("state") != "ACTIVE" or approved.get("role") != "READ_ONLY":
            raise SystemExit("F7.2B verification failed: approval/role assignment failed")

        authenticated = authenticate_user(username, password)
        if authenticated is None or authenticated["user_id"] != user_id or authenticated["role"] != "READ_ONLY":
            raise SystemExit("F7.2B verification failed: approved user authentication failed")
        active_cookie = create_session_token(user_id)
        denied = _request_json(base_url, "/dashboard/api/users", active_cookie, expected_status=403)
        if denied.get("detail") != "Access denied":
            raise SystemExit("F7.2B verification failed: non-Owner User Management did not return Access denied")

        # Ordinary User Management cannot alter the Owner role/account.
        owner_protected = _request_json(
            base_url,
            f"/dashboard/api/users/{owner['user_id']}/role",
            owner_cookie,
            expected_status=403,
            method="PATCH",
            payload={"role": "READ_ONLY"},
        )
        if "Owner account" not in owner_protected.get("detail", ""):
            raise SystemExit("F7.2B verification failed: Owner escalation boundary missing")

        changed = _request_json(
            base_url,
            f"/dashboard/api/users/{user_id}/role",
            owner_cookie,
            method="PATCH",
            payload={"role": "STAFF"},
        )
        if changed.get("role") != "STAFF" or changed.get("sessions_revoked") is not True:
            raise SystemExit("F7.2B verification failed: role change/session revocation failed")
        _request_json(base_url, "/dashboard/api/overview", active_cookie, expected_status=401)
        active_cookie = None

        authenticated = authenticate_user(username, password)
        if authenticated is None or authenticated["role"] != "STAFF":
            raise SystemExit("F7.2B verification failed: changed role not authoritative")
        active_cookie = create_session_token(user_id)

        disabled = _request_json(base_url, f"/dashboard/api/users/{user_id}/disable", owner_cookie, method="POST")
        if disabled.get("state") != "DISABLED" or disabled.get("sessions_revoked") is not True:
            raise SystemExit("F7.2B verification failed: disable failed")
        _request_json(base_url, "/dashboard/api/overview", active_cookie, expected_status=401)
        active_cookie = None
        if authenticate_user(username, password) is not None:
            raise SystemExit("F7.2B verification failed: disabled user authenticated")

        reactivated = _request_json(base_url, f"/dashboard/api/users/{user_id}/reactivate", owner_cookie, method="POST")
        if reactivated.get("state") != "ACTIVE" or reactivated.get("role") != "STAFF":
            raise SystemExit("F7.2B verification failed: reactivate failed")
        authenticated = authenticate_user(username, password)
        if authenticated is None:
            raise SystemExit("F7.2B verification failed: reactivated user did not authenticate")
        active_cookie = create_session_token(user_id)
        revoked = _request_json(base_url, f"/dashboard/api/users/{user_id}/revoke-sessions", owner_cookie, method="POST")
        if revoked.get("sessions_revoked") is not True:
            raise SystemExit("F7.2B verification failed: explicit session revoke failed")
        _request_json(base_url, "/dashboard/api/overview", active_cookie, expected_status=401)
        active_cookie = None

        # Rejection path remains non-authenticating and durable.
        reject_password = secrets.token_urlsafe(18)
        _request_json(
            base_url,
            "/dashboard/api/access-requests",
            expected_status=202,
            method="POST",
            payload={"display_name": "F7.2B rejected user", "username": reject_username, "password": reject_password},
        )
        with engine.connect() as connection:
            rejected_id = connection.execute(
                text("SELECT user_id::text FROM users WHERE username = :username"), {"username": reject_username}
            ).scalar_one()
        created_user_ids.append(rejected_id)
        rejected = _request_json(base_url, f"/dashboard/api/users/{rejected_id}/reject", owner_cookie, method="POST")
        if rejected.get("state") != "DISABLED" or rejected.get("request_status") != "REJECTED":
            raise SystemExit("F7.2B verification failed: rejection path failed")
        if authenticate_user(reject_username, reject_password) is not None:
            raise SystemExit("F7.2B verification failed: rejected user authenticated")

        with engine.connect() as connection:
            event_types = {
                row[0]
                for row in connection.execute(
                    text("SELECT event_type FROM account_security_events WHERE target_user_id = CAST(:user_id AS uuid)"),
                    {"user_id": user_id},
                ).all()
            }
        expected_events = {"ACCESS_REQUEST_CREATED", "ACCESS_APPROVED", "ROLE_CHANGED", "ACCOUNT_DISABLED", "ACCOUNT_REACTIVATED", "SESSIONS_REVOKED"}
        if not expected_events.issubset(event_types):
            raise SystemExit("F7.2B verification failed: account security event history incomplete")
    finally:
        if active_cookie:
            revoke_session_token(active_cookie)
        _cleanup_users(engine, created_user_ids)
        engine.dispose()
        revoke_session_token(owner_cookie)

    print(
        "F7.2A canonical identity runtime=pass "
        f"owner_user_id={owner['user_id']} owner_username={owner['username']} "
        "username_password=pass durable_session=pass owner_rbac=pass access_denied_403=pass disabled_access_revoked=pass "
        f"row_count={int(batch.get('row_count') or 0)} database_canonical=false migration_baseline_accepted=false"
    )
    print(
        "F7.2B user_management_runtime=pass request_pending=pass pending_denied=pass owner_list=pass approve=pass "
        "assign_role=pass non_owner_403=pass owner_escalation_guard=pass role_change_revokes=pass disable=pass "
        "reactivate=pass explicit_session_revoke=pass reject=pass account_events=pass notification_events=pass"
    )


if __name__ == "__main__":
    main()
