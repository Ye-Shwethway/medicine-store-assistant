from __future__ import annotations

import importlib.util
from pathlib import Path

from fastapi import HTTPException

from app import ai_workspace_access as access
from app.main import app


def main() -> None:
    paths = set(app.openapi()["paths"])
    required = {
        "/dashboard/api/ai-workspace/access",
        "/dashboard/api/ai-workspace/settings",
        "/dashboard/api/ai-workspace/users/{user_id}/access",
        "/dashboard/api/ai-workspace/agents/{agent_id}/invoke",
    }
    missing = required - paths
    if missing:
        raise SystemExit(f"missing AI Workspace paths: {sorted(missing)}")

    original = access._read_policy_for_user
    try:
        access._read_policy_for_user = lambda user_id: {
            "non_owner_chat_enabled": False,
            "chat_entitlement": "ALLOW",
        }
        blocked = access.evaluate_ai_chat_access({"user_id": "u", "role": "STAFF"})
        assert blocked["allowed"] is False
        assert blocked["reason"] == "GLOBAL_DISABLED"

        access._read_policy_for_user = lambda user_id: {
            "non_owner_chat_enabled": True,
            "chat_entitlement": "BLOCK",
        }
        blocked_user = access.evaluate_ai_chat_access({"user_id": "u", "role": "STAFF"})
        assert blocked_user["allowed"] is False
        assert blocked_user["reason"] == "USER_BLOCKED"

        allowed_owner = access.evaluate_ai_chat_access({"user_id": "owner", "role": "OWNER"})
        assert allowed_owner["allowed"] is True
        assert allowed_owner["reason"] == "OWNER_BYPASS"

        access._read_policy_for_user = lambda user_id: {
            "non_owner_chat_enabled": True,
            "chat_entitlement": "INHERIT",
        }
        allowed_staff = access.evaluate_ai_chat_access({"user_id": "u", "role": "STAFF"})
        assert allowed_staff["allowed"] is True
        assert allowed_staff["reason"] == "GLOBAL_INHERIT"
    finally:
        access._read_policy_for_user = original

    source = Path(access.__file__).read_text(encoding="utf-8")
    assert "Depends(require_ai_chat_access)" in source
    assert "provider_invoked" in source
    assert "invoke_native_agent" in source
    assert source.index("Depends(require_ai_chat_access)") < source.index("result = invoke_native_agent")

    migration_path = Path(__file__).parents[1] / "alembic" / "versions" / "0017_ai_workspace_access.py"
    spec = importlib.util.spec_from_file_location("workspace_migration", migration_path)
    migration = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(migration)
    assert migration.revision == "0017_ai_workspace_access"
    assert migration.down_revision == "0016_revoke_stale_chatgpt_oauth"

    print("ai_workspace_access_policy=pass")


if __name__ == "__main__":
    main()
