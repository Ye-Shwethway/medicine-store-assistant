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
    make_password_hash,
    revoke_session_token,
)


def _request_json(base_url: str, path: str, cookie: str, *, expected_status: int = 200) -> dict:
    request = urllib.request.Request(
        f"{base_url}{path}",
        headers={"Cookie": f"{SESSION_COOKIE}={cookie}", "Accept": "application/json"},
    )
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


def main() -> None:
    base_url = os.environ.get("MSA_DASHBOARD_VERIFY_BASE_URL")
    if not base_url:
        port = os.environ.get("MSA_API_HOST_PORT", "8088")
        base_url = f"http://127.0.0.1:{port}"
    base_url = base_url.rstrip("/")

    owner = ensure_bootstrap_owner()
    if owner["role"] != "OWNER" or owner["state"] != "ACTIVE" or not owner["user_id"]:
        raise SystemExit("F7.2A verification failed: canonical Owner is invalid")
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

    temp_username = f"f72a-verify-{secrets.token_hex(5)}"
    temp_password = secrets.token_urlsafe(18)
    engine = _engine()
    temp_user_id = None
    temp_cookie = None
    try:
        with engine.begin() as connection:
            row = connection.execute(
                text(
                    """
                    INSERT INTO users (username, password_hash, role, state)
                    VALUES (:username, :password_hash, 'READ_ONLY', 'ACTIVE')
                    RETURNING user_id::text
                    """
                ),
                {"username": temp_username, "password_hash": make_password_hash(temp_password)},
            ).one()
            temp_user_id = row[0]

        authenticated = authenticate_user(temp_username, temp_password)
        if authenticated is None or authenticated["user_id"] != temp_user_id or authenticated["role"] != "READ_ONLY":
            raise SystemExit("F7.2A verification failed: username/password authentication did not resolve canonical user")

        temp_cookie = create_session_token(temp_user_id)
        denied = _request_json(base_url, "/dashboard/api/authorization/owner", temp_cookie, expected_status=403)
        if denied.get("detail") != "Access denied":
            raise SystemExit("F7.2A verification failed: authenticated 403 did not return Access denied")

        with engine.begin() as connection:
            connection.execute(
                text("UPDATE users SET state = 'DISABLED', disabled_at = now(), updated_at = now() WHERE user_id = CAST(:user_id AS uuid)"),
                {"user_id": temp_user_id},
            )
        _request_json(base_url, "/dashboard/api/overview", temp_cookie, expected_status=401)
    finally:
        if temp_cookie:
            revoke_session_token(temp_cookie)
        if temp_user_id:
            with engine.begin() as connection:
                connection.execute(text("DELETE FROM users WHERE user_id = CAST(:user_id AS uuid)"), {"user_id": temp_user_id})
        engine.dispose()
        revoke_session_token(owner_cookie)

    print(
        "F7.2A canonical identity runtime=pass "
        f"owner_user_id={owner['user_id']} owner_username={owner['username']} "
        "username_password=pass durable_session=pass owner_rbac=pass access_denied_403=pass disabled_access_revoked=pass "
        f"row_count={int(batch.get('row_count') or 0)} database_canonical=false migration_baseline_accepted=false"
    )


if __name__ == "__main__":
    main()
