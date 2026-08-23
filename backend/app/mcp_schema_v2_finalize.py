from __future__ import annotations

import hashlib
from typing import Any

from mcp.types import ToolAnnotations

import app.mcp_schema_v2 as schema
from app.mcp_server import _not_implemented, mcp

READ = ToolAnnotations(read_only_hint=True, open_world_hint=False)
EXCLUDED_TOOL_NAMES = ("msa_agents_rotate_credential",)

# The Owner explicitly excluded credential management from the long-lived MCP schema.
# MCPServer exposes a public remove_tool API; remove the legacy placeholder before
# the HTTP transport app is constructed so it is absent from tools/list.
mcp.remove_tool("msa_agents_rotate_credential")


@mcp.tool(annotations=READ)
def msa_inventory_read_usage(
    product_id: str | None = None,
    location_id: str | None = None,
    start_at: str | None = None,
    end_at: str | None = None,
    limit: int = 100,
    offset: int = 0,
) -> dict[str, Any]:
    """Future bounded Daily Usage/issue history read by product, location, or date range."""
    return _not_implemented("msa_inventory_read_usage", "mcp:read")


# Replace the legacy credential action in the declared manifest with the durable
# operational usage-read surface. msa_system_schema_manifest resolves these globals
# at call time, so it reports the finalized transport catalog.
_names = set(schema.FINAL_TOOL_NAMES)
_names.discard("msa_agents_rotate_credential")
_names.add("msa_inventory_read_usage")
schema.FINAL_TOOL_NAMES = tuple(sorted(_names))
schema.FINAL_TOOL_COUNT = len(schema.FINAL_TOOL_NAMES)
schema.FINAL_TOOL_HASH = hashlib.sha256("\n".join(schema.FINAL_TOOL_NAMES).encode("utf-8")).hexdigest()
