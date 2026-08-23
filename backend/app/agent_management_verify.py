from __future__ import annotations

import os
import secrets

import requests
from sqlalchemy import text

from app.dashboard_auth import SESSION_COOKIE, _engine, create_session_token, ensure_bootstrap_owner, make_password_hash

BASE_URL = os.getenv("MSA_DASHBOARD_VERIFY_BASE_URL", "http://127.0.0.1:8080").rstrip("/")


def _check(response: requests.Response, expected: int = 200) -> dict:
    if response.status_code != expected:
        raise RuntimeError(f"{response.request.method} {response.url} -> {response.status_code}: {response.text[:500]}")
    if not response.content:
        return {}
    return response.json()


def main() -> None:
    owner = ensure_bootstrap_owner()
    owner_http = requests.Session()
    owner_http.cookies.set(SESSION_COOKIE, create_session_token(owner["user_id"]), path="/dashboard")

    suffix = secrets.token_hex(5)
    call_a = f"VerifierA-{suffix}"
    call_b = f"VerifierB-{suffix}"
    agent_ids: list[str] = []
    session_ids: list[str] = []
    non_owner_id: str | None = None

    engine = _engine()
    try:
        # Owner-only gate: create a temporary READ_ONLY user/session and prove denial.
        with engine.begin() as connection:
            row = connection.execute(
                text(
                    """
                    INSERT INTO users (display_name, username, password_hash, state)
                    VALUES (:display_name, :username, :password_hash, 'ACTIVE')
                    RETURNING user_id::text AS user_id
                    """
                ),
                {
                    "display_name": "F7.2D2 Verifier",
                    "username": f"f72d2-verifier-{suffix}",
                    "password_hash": make_password_hash(secrets.token_urlsafe(18)),
                },
            ).mappings().one()
            non_owner_id = row["user_id"]
            connection.execute(
                text("INSERT INTO user_roles (user_id, role_code) VALUES (CAST(:user_id AS uuid), 'READ_ONLY')"),
                {"user_id": non_owner_id},
            )
        non_owner_http = requests.Session()
        non_owner_http.cookies.set(SESSION_COOKIE, create_session_token(non_owner_id), path="/dashboard")
        denied = non_owner_http.get(f"{BASE_URL}/dashboard/api/agents", timeout=10)
        if denied.status_code != 403:
            raise RuntimeError(f"non-owner Agent Management expected 403, got {denied.status_code}")

        # Create two durable named identities.
        a = _check(
            owner_http.post(
                f"{BASE_URL}/dashboard/api/agents",
                json={
                    "display_name": "Verifier Analyst",
                    "call_name": call_a,
                    "description": "Temporary F7.2D2 runtime verifier",
                    "runtime_mode": "INTERNAL_MODEL",
                    "capability_scopes": ["mcp:read"],
                    "authority_ceiling": "READ",
                    "execution_policy": "DELEGATED",
                    "confirmation_policy": "READ_ONLY",
                },
                timeout=10,
            ),
            201,
        )
        b = _check(
            owner_http.post(
                f"{BASE_URL}/dashboard/api/agents",
                json={
                    "display_name": "Verifier Reviewer",
                    "call_name": call_b,
                    "runtime_mode": "INTERNAL_MODEL",
                    "capability_scopes": ["mcp:read", "mcp:propose"],
                    "authority_ceiling": "PROPOSE",
                    "execution_policy": "DELEGATED",
                    "confirmation_policy": "PROPOSE_ONLY",
                },
                timeout=10,
            ),
            201,
        )
        agent_ids.extend([a["agent_id"], b["agent_id"]])
        if a["agent_id"] == b["agent_id"]:
            raise RuntimeError("agent ids must be distinct")
        if call_a not in a["identity_context"]:
            # identity context is based on display name, not call name; this branch intentionally verifies name truth below.
            if "Verifier Analyst" not in a["identity_context"]:
                raise RuntimeError("identity context did not include canonical display name")

        # Case-insensitive call-name uniqueness.
        duplicate = owner_http.post(
            f"{BASE_URL}/dashboard/api/agents",
            json={"display_name": "Duplicate", "call_name": call_a.lower()},
            timeout=10,
        )
        if duplicate.status_code != 409:
            raise RuntimeError(f"case-insensitive call-name duplicate expected 409, got {duplicate.status_code}")

        # Rename keeps stable agent_id and updates deterministic self-identity context.
        renamed = _check(
            owner_http.patch(
                f"{BASE_URL}/dashboard/api/agents/{a['agent_id']}",
                json={"display_name": "Verifier Analyst Renamed", "call_name": call_a},
                timeout=10,
            )
        )
        if renamed["agent_id"] != a["agent_id"]:
            raise RuntimeError("rename changed stable agent_id")
        if "Verifier Analyst Renamed" not in renamed["identity_context"] or a["agent_id"] not in renamed["identity_context"]:
            raise RuntimeError("self-identity context did not reflect canonical renamed identity")

        # Persist a multi-agent COMPARE topology with explicit order and roles.
        session = _check(
            owner_http.post(
                f"{BASE_URL}/dashboard/api/agents/sessions",
                json={
                    "session_name": f"Verifier Compare {suffix}",
                    "objective": "Verify multi-agent participant selection and ordering without inference",
                    "mode": "COMPARE",
                    "participants": [
                        {"agent_id": a["agent_id"], "position": 0, "role_label": "Primary"},
                        {"agent_id": b["agent_id"], "position": 1, "role_label": "Reviewer"},
                    ],
                },
                timeout=10,
            ),
            201,
        )
        session_ids.append(session["session_id"])
        if [p["agent_id"] for p in session["participants"]] != [a["agent_id"], b["agent_id"]]:
            raise RuntimeError("session participant ordering mismatch")
        if session["mode"] != "COMPARE":
            raise RuntimeError("session mode mismatch")

        listed = _check(owner_http.get(f"{BASE_URL}/dashboard/api/agents/sessions/list", timeout=10))
        persisted = next((item for item in listed["items"] if item["session_id"] == session["session_id"]), None)
        if not persisted or len(persisted["participants"]) != 2:
            raise RuntimeError("multi-agent session topology did not persist")
        if listed.get("inference_enabled") is not False:
            raise RuntimeError("F7.2D2 must not enable model inference")

        # Disabled agents cannot be selected for an edited session; reactivation restores eligibility.
        _check(owner_http.post(f"{BASE_URL}/dashboard/api/agents/{b['agent_id']}/disable", timeout=10))
        blocked = owner_http.patch(
            f"{BASE_URL}/dashboard/api/agents/sessions/{session['session_id']}",
            json={
                "participants": [
                    {"agent_id": a["agent_id"], "position": 0, "role_label": "Primary"},
                    {"agent_id": b["agent_id"], "position": 1, "role_label": "Reviewer"},
                ]
            },
            timeout=10,
        )
        if blocked.status_code != 409:
            raise RuntimeError(f"disabled session participant expected 409, got {blocked.status_code}")
        _check(owner_http.post(f"{BASE_URL}/dashboard/api/agents/{b['agent_id']}/reactivate", timeout=10))

        closed = _check(owner_http.post(f"{BASE_URL}/dashboard/api/agents/sessions/{session['session_id']}/close", timeout=10))
        if closed["state"] != "CLOSED":
            raise RuntimeError("session close failed")
        reopened = _check(owner_http.post(f"{BASE_URL}/dashboard/api/agents/sessions/{session['session_id']}/reopen", timeout=10))
        if reopened["state"] != "OPEN":
            raise RuntimeError("session reopen failed")

        revoked = _check(owner_http.post(f"{BASE_URL}/dashboard/api/agents/{b['agent_id']}/revoke", timeout=10))
        if revoked["state"] != "REVOKED":
            raise RuntimeError("agent revoke failed")
        cannot_reactivate = owner_http.post(f"{BASE_URL}/dashboard/api/agents/{b['agent_id']}/reactivate", timeout=10)
        if cannot_reactivate.status_code != 409:
            raise RuntimeError(f"revoked agent reactivation expected 409, got {cannot_reactivate.status_code}")

        print(
            "F7.2D2 agent_management_runtime=pass named_identity=pass stable_agent_id=pass "
            "self_identity_context=pass call_name_unique=pass non_owner_403=pass "
            "multi_agent_session=pass compare_topology=pass participant_order=pass "
            "disable_reactivate=pass revoke_guard=pass inference_disabled=pass"
        )
    finally:
        # Verifier data is temporary and must not become product configuration.
        try:
            with engine.begin() as connection:
                if session_ids:
                    connection.execute(
                        text("DELETE FROM ai_agent_sessions WHERE session_id = ANY(CAST(:ids AS uuid[]))"),
                        {"ids": session_ids},
                    )
                if agent_ids:
                    connection.execute(
                        text("DELETE FROM ai_agents WHERE agent_id = ANY(CAST(:ids AS uuid[]))"),
                        {"ids": agent_ids},
                    )
                if non_owner_id:
                    connection.execute(text("DELETE FROM user_sessions WHERE user_id = CAST(:id AS uuid)"), {"id": non_owner_id})
                    connection.execute(text("DELETE FROM user_roles WHERE user_id = CAST(:id AS uuid)"), {"id": non_owner_id})
                    connection.execute(text("DELETE FROM users WHERE user_id = CAST(:id AS uuid)"), {"id": non_owner_id})
        finally:
            engine.dispose()


if __name__ == "__main__":
    main()
