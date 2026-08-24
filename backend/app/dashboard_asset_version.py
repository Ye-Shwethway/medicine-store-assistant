from __future__ import annotations

from hashlib import sha256
from pathlib import Path


_SEMANTIC_PREFIX_BY_PRIMARY_ASSET = {
    "dashboard_saved_models.js": "f72d31-",
    "dashboard_agent_assignment_guard.js": "f72d4-preflight-",
    "dashboard_native_agent_test.js": "f72d4d-native-test-",
    "dashboard_ai_workspace_access.js": "f72d4-access-",
    "dashboard_ai_workspace.js": "f72d47b-attachments-",
    "dashboard_multi_agent_review.js": "f72d48-review-ui-",
    "dashboard_multi_agent_live_export.js": "f72d48-live-export-",
    "dashboard_agent_polish.css": "f72d31-agentui-",
    "dashboard_mcp_binding.js": "f72d4a-mcpbind-",
    "dashboard_audit.js": "f73a-mcpaudit-",
}


def asset_bundle_version(asset_dir: Path, *names: str) -> str:
    """Return semantic release identity plus a hash of the exact served bundle files."""
    if not names:
        raise ValueError("At least one Dashboard asset is required")
    digest = sha256()
    for name in names:
        path = asset_dir / name
        digest.update(name.encode("utf-8"))
        digest.update(b"\0")
        digest.update(path.read_bytes())
        digest.update(b"\0")
    prefix = _SEMANTIC_PREFIX_BY_PRIMARY_ASSET.get(names[0], "asset-")
    return prefix + digest.hexdigest()[:12]
