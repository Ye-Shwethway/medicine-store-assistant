from __future__ import annotations

import hashlib
import os
from typing import Any
from uuid import UUID

from mcp.server import MCPServer
from mcp.server.auth.middleware.auth_context import get_access_token
from mcp.server.auth.provider import AccessToken, TokenVerifier
from mcp.server.auth.settings import AuthSettings
from mcp.server.transport_security import TransportSecuritySettings
from mcp.types import ToolAnnotations
from pydantic import AnyHttpUrl
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError

from app.db import normalize_database_url
from app.read_api import current_catalogue, list_catalogue_versions, list_lots, list_products
from app.shadow_read_api import list_shadow_batches, shadow_review_reasons

PUBLIC_BASE_URL = os.getenv("MSA_PUBLIC_BASE_URL", "https://inventory.drthorne.uk").rstrip("/")
MCP_RESOURCE_URL = os.getenv("MSA_MCP_RESOURCE_URL", f"{PUBLIC_BASE_URL}/mcp")
MCP_AUTH_ISSUER_URL = os.getenv("MSA_MCP_AUTH_ISSUER_URL", f"{PUBLIC_BASE_URL}/oauth")
DATABASE_URL = os.getenv("DATABASE_URL", "").strip()

# F7.2D deliberately publishes the durable schema before write authority is enabled.
PRODUCTION_INVENTORY_WRITES_ENABLED = False
CONTROL_PLANE_WRITES_ENABLED = False

READ = ToolAnnotations(read_only_hint=True, open_world_hint=False)
PROPOSE = ToolAnnotations(read_only_hint=False, destructive_hint=False, idempotent_hint=False, open_world_hint=False)
WRITE = ToolAnnotations(read_only_hint=False, destructive_hint=False, idempotent_hint=True, open_world_hint=False)
DESTRUCTIVE = ToolAnnotations(read_only_hint=False, destructive_hint=True, idempotent_hint=True, open_world_hint=False)
AUTHORITY_SCOPES = ("mcp:read", "mcp:propose", "mcp:write", "mcp:control")
AUTHORITY_INDEX = {scope: index for index, scope in enumerate(AUTHORITY_SCOPES)}
CEILING_SCOPE = {"READ": "mcp:read", "PROPOSE": "mcp:propose", "WRITE": "mcp:write", "CONTROL": "mcp:control"}


def _engine():
    if not DATABASE_URL:
        raise RuntimeError("database is not configured")
    return create_engine(normalize_database_url(DATABASE_URL), pool_pre_ping=True)


def _credential_hash(token: str) -> str:
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


class MSAServiceTokenVerifier(TokenVerifier):
    """Resolve bootstrap service credentials or persistent OAuth grants into MCP request context."""

    async def verify_token(self, token: str) -> AccessToken | None:
        if not token or not DATABASE_URL:
            return None
        token_digest = _credential_hash(token)
        engine = _engine()
        try:
            with engine.connect() as connection:
                service_row = connection.execute(
                    text(
                        """
                        SELECT sp.service_principal_id::text AS principal_id,
                               sp.name,
                               sc.scopes
                        FROM service_credentials sc
                        JOIN service_principals sp
                          ON sp.service_principal_id = sc.service_principal_id
                        WHERE sc.key_hash = :key_hash
                          AND sc.revoked_at IS NULL
                          AND sp.status = 'active'
                        LIMIT 1
                        """
                    ),
                    {"key_hash": token_digest},
                ).mappings().first()

                if service_row is not None:
                    scopes = [str(scope) for scope in (service_row["scopes"] or [])]
                    if "mcp:connect" not in scopes and "*" not in scopes:
                        return None
                    principal_id = str(service_row["principal_id"])
                    return AccessToken(
                        token=token,
                        client_id=principal_id,
                        subject=principal_id,
                        scopes=scopes,
                    )

                oauth_row = connection.execute(
                    text(
                        """
                        SELECT t.client_id,
                               g.user_id::text AS user_id,
                               t.oauth_scopes,
                               g.capability_scopes
                        FROM mcp_oauth_tokens t
                        JOIN mcp_oauth_grants g ON g.grant_id = t.grant_id
                        JOIN mcp_oauth_clients c ON c.client_id = t.client_id
                        JOIN users u ON u.user_id = g.user_id
                        WHERE t.token_digest = :token_digest
                          AND t.token_kind = 'ACCESS'
                          AND t.revoked_at IS NULL
                          AND t.expires_at > now()
                          AND g.state = 'ACTIVE'
                          AND c.revoked_at IS NULL
                          AND u.state = 'ACTIVE'
                        LIMIT 1
                        """
                    ),
                    {"token_digest": token_digest},
                ).mappings().first()
        except SQLAlchemyError:
            return None
        finally:
            engine.dispose()

        if oauth_row is None:
            return None

        transport_scopes = {str(scope) for scope in (oauth_row["oauth_scopes"] or [])}
        capability_scopes = {str(scope) for scope in (oauth_row["capability_scopes"] or [])}
        if "mcp:connect" not in transport_scopes:
            return None

        # OAuth grant capabilities remain live lookup data. Named-agent policy is intersected later
        # on every tool call, so bind/unbind and agent policy changes do not require reconnecting.
        granted_scopes = sorted(transport_scopes | capability_scopes)
        return AccessToken(
            token=token,
            client_id=str(oauth_row["client_id"]),
            subject=str(oauth_row["user_id"]),
            scopes=granted_scopes,
        )


def _caller() -> AccessToken | None:
    return get_access_token()


def _bound_agent_context(access: AccessToken | None) -> dict[str, Any] | None:
    if access is None or not DATABASE_URL or not access.client_id or not access.subject:
        return None
    try:
        UUID(str(access.subject))
    except (TypeError, ValueError):
        return None
    engine = _engine()
    try:
        with engine.connect() as connection:
            row = connection.execute(
                text(
                    """
                    SELECT b.grant_id::text AS grant_id,
                           a.agent_id::text AS agent_id,
                           a.display_name,
                           a.call_name,
                           a.runtime_mode,
                           a.state,
                           a.capability_scopes,
                           a.authority_ceiling,
                           a.execution_policy,
                           a.confirmation_policy,
                           c.client_name
                    FROM mcp_oauth_grants g
                    JOIN mcp_oauth_clients c ON c.client_id = g.client_id
                    JOIN mcp_agent_bindings b ON b.grant_id = g.grant_id
                    JOIN ai_agents a ON a.agent_id = b.agent_id
                    WHERE g.client_id = :client_id
                      AND g.user_id = CAST(:subject AS uuid)
                      AND g.state = 'ACTIVE'
                      AND c.revoked_at IS NULL
                    LIMIT 1
                    """
                ),
                {"client_id": access.client_id, "subject": str(access.subject)},
            ).mappings().first()
    except SQLAlchemyError:
        return None
    finally:
        engine.dispose()
    return dict(row) if row is not None else None


def _effective_scopes(access: AccessToken | None) -> set[str]:
    if access is None:
        return set()
    granted = set(access.scopes or [])
    context = _bound_agent_context(access)
    if context is None:
        return granted

    transport = granted - set(AUTHORITY_SCOPES)
    if context["state"] != "ACTIVE" or context["runtime_mode"] != "EXTERNAL_MCP_CLIENT":
        return transport

    agent_capabilities = {str(scope) for scope in (context["capability_scopes"] or [])}
    grant_authority = granted & set(AUTHORITY_SCOPES)
    ceiling_scope = CEILING_SCOPE.get(str(context["authority_ceiling"]), "mcp:read")
    ceiling_index = AUTHORITY_INDEX[ceiling_scope]
    ceiling_allowed = {scope for scope, index in AUTHORITY_INDEX.items() if index <= ceiling_index}
    effective_authority = grant_authority & agent_capabilities & ceiling_allowed
    return transport | effective_authority


def _has_scope(scope: str, tool_name: str) -> bool:
    access = _caller()
    if access is None:
        return False
    scopes = _effective_scopes(access)
    return "*" in scopes or scope in scopes or f"tool:{tool_name}" in scopes


def _deny(tool_name: str, required_scope: str, *, reason: str = "NOT_AUTHORIZED") -> dict[str, Any]:
    return {
        "ok": False,
        "status": reason,
        "tool": tool_name,
        "required_scope": required_scope,
        "database_canonical": False,
        "migration_baseline_accepted": False,
    }


def _gate(tool_name: str, scope: str) -> dict[str, Any] | None:
    if not _has_scope(scope, tool_name):
        return _deny(tool_name, scope)
    return None


def _write_gate(tool_name: str, scope: str = "mcp:write") -> dict[str, Any] | None:
    denied = _gate(tool_name, scope)
    if denied:
        return denied
    if not PRODUCTION_INVENTORY_WRITES_ENABLED:
        return _deny(tool_name, scope, reason="SLICE_NOT_AUTHORIZED")
    return None


def _control_gate(tool_name: str) -> dict[str, Any] | None:
    denied = _gate(tool_name, "mcp:control")
    if denied:
        return denied
    if not CONTROL_PLANE_WRITES_ENABLED:
        return _deny(tool_name, "mcp:control", reason="SLICE_NOT_AUTHORIZED")
    return None


def _not_implemented(tool_name: str, scope: str) -> dict[str, Any]:
    denied = _gate(tool_name, scope)
    if denied:
        return denied
    return _deny(tool_name, scope, reason="NOT_ENABLED")


mcp = MCPServer(
    "Medicine Store Assistant",
    instructions=(
        "Typed Medicine Store Assistant tools. Tool visibility never implies authority. "
        "Respect returned policy status and canonicality boundaries; never claim a mutation succeeded without read-back."
    ),
    token_verifier=MSAServiceTokenVerifier(),
    auth=AuthSettings(
        issuer_url=AnyHttpUrl(MCP_AUTH_ISSUER_URL),
        resource_server_url=AnyHttpUrl(MCP_RESOURCE_URL),
        required_scopes=["mcp:connect"],
    ),
)


@mcp.tool(annotations=READ)
def msa_identity_whoami() -> dict[str, Any]:
    """Return authenticated transport identity and the bound named MSA agent, when configured."""
    access = _caller()
    if access is None:
        return _deny("msa_identity_whoami", "mcp:connect")
    context = _bound_agent_context(access)
    result: dict[str, Any] = {
        "ok": True,
        "status": "AVAILABLE",
        "client_id": access.client_id,
        "subject": access.subject,
        "granted_scopes": sorted(access.scopes or []),
        "effective_scopes": sorted(_effective_scopes(access)),
        "runtime_type": "EXTERNAL_MCP_CLIENT",
        "agent_binding_status": "BOUND" if context else "UNBOUND",
    }
    if context:
        result.update(
            {
                "agent_id": context["agent_id"],
                "agent_display_name": context["display_name"],
                "agent_call_name": context["call_name"],
                "agent_runtime_mode": context["runtime_mode"],
                "agent_state": context["state"],
                "agent_authority_ceiling": context["authority_ceiling"],
                "agent_execution_policy": context["execution_policy"],
                "agent_confirmation_policy": context["confirmation_policy"],
                "mcp_client_name": context["client_name"],
            }
        )
    return result


@mcp.tool(annotations=READ)
def msa_system_status() -> dict[str, Any]:
    """Return MSA runtime boundary status relevant to MCP operations."""
    denied = _gate("msa_system_status", "mcp:read")
    if denied:
        return denied
    return {
        "ok": True,
        "status": "AVAILABLE",
        "service": "medicine-store-assistant",
        "environment": os.getenv("MSA_ENVIRONMENT", "development"),
        "build_sha": os.getenv("MSA_BUILD_SHA", "unknown"),
        "database_canonical": False,
        "migration_baseline_accepted": False,
        "f6b_test_only": True,
        "production_inventory_writes_enabled": PRODUCTION_INVENTORY_WRITES_ENABLED,
        "control_plane_writes_enabled": CONTROL_PLANE_WRITES_ENABLED,
    }


@mcp.tool(annotations=READ)
def msa_system_capabilities() -> dict[str, Any]:
    """Describe server-side MCP capability gates independently from client UI support."""
    denied = _gate("msa_system_capabilities", "mcp:read")
    if denied:
        return denied
    access = _caller()
    scopes = _effective_scopes(access)
    return {
        "ok": True,
        "status": "AVAILABLE",
        "granted_scopes": sorted(access.scopes or []) if access else [],
        "effective_scopes": sorted(scopes),
        "read": "mcp:read" in scopes or "*" in scopes,
        "propose": "mcp:propose" in scopes or "*" in scopes,
        "write": ("mcp:write" in scopes or "*" in scopes) and PRODUCTION_INVENTORY_WRITES_ENABLED,
        "control": ("mcp:control" in scopes or "*" in scopes) and CONTROL_PLANE_WRITES_ENABLED,
        "database_canonical": False,
        "migration_baseline_accepted": False,
    }


@mcp.tool(annotations=READ)
def msa_inventory_read_summary() -> dict[str, Any]:
    """Return the latest bounded shadow inventory migration summary."""
    denied = _gate("msa_inventory_read_summary", "mcp:read")
    if denied:
        return denied
    result = list_shadow_batches(limit=1, offset=0)
    return {"ok": True, "status": "AVAILABLE", **result}


@mcp.tool(annotations=READ)
def msa_inventory_read_search(query: str, limit: int = 20) -> dict[str, Any]:
    """Search active local products by name using a bounded result set."""
    denied = _gate("msa_inventory_read_search", "mcp:read")
    if denied:
        return denied
    bounded = min(max(limit, 1), 50)
    result = list_products(active_only=True, limit=500, offset=0)
    needle = query.strip().casefold()
    items = [item for item in result["items"] if needle in str(item.get("local_name", "")).casefold()][:bounded]
    return {"ok": True, "status": "AVAILABLE", "items": items, "count": len(items), "limit": bounded}


@mcp.tool(annotations=READ)
def msa_inventory_read_item(product_id: str) -> dict[str, Any]:
    """Read one local product by stable product identifier."""
    denied = _gate("msa_inventory_read_item", "mcp:read")
    if denied:
        return denied
    result = list_products(active_only=False, limit=500, offset=0)
    item = next((row for row in result["items"] if str(row.get("product_id")) == product_id), None)
    return {"ok": item is not None, "status": "AVAILABLE" if item else "NOT_FOUND", "item": item}


@mcp.tool(annotations=READ)
def msa_inventory_read_lots(product_id: str | None = None, limit: int = 50) -> dict[str, Any]:
    """Read bounded product-lot data, optionally filtered by product identifier."""
    denied = _gate("msa_inventory_read_lots", "mcp:read")
    if denied:
        return denied
    return {
        "ok": True,
        "status": "AVAILABLE",
        **list_lots(product_id=product_id, active_only=True, limit=min(max(limit, 1), 100), offset=0),
    }


@mcp.tool(annotations=READ)
def msa_inventory_read_location_balance(product_id: str, location_id: str | None = None) -> dict[str, Any]:
    """Read location-aware balance once the F7.4 location model is enabled."""
    return _not_implemented("msa_inventory_read_location_balance", "mcp:read")


@mcp.tool(annotations=READ)
def msa_catalogue_read_current() -> dict[str, Any]:
    """Read current CMS catalogue diagnostics."""
    denied = _gate("msa_catalogue_read_current", "mcp:read")
    if denied:
        return denied
    return {"ok": True, "status": "AVAILABLE", **current_catalogue()}


@mcp.tool(annotations=READ)
def msa_catalogue_read_history(limit: int = 20) -> dict[str, Any]:
    """Read bounded CMS catalogue version history."""
    denied = _gate("msa_catalogue_read_history", "mcp:read")
    if denied:
        return denied
    return {
        "ok": True,
        "status": "AVAILABLE",
        **list_catalogue_versions(limit=min(max(limit, 1), 50)),
    }


@mcp.tool(annotations=PROPOSE)
def msa_reconciliation_classify(source_reference: str, candidate_product_id: str | None = None) -> dict[str, Any]:
    """Classify evidence only after the deterministic reconciliation contract is enabled."""
    return _not_implemented("msa_reconciliation_classify", "mcp:propose")


@mcp.tool(annotations=PROPOSE)
def msa_reconciliation_prepare_batch(source_reference: str, note: str | None = None) -> dict[str, Any]:
    """Prepare a reconciliation proposal without committing inventory truth."""
    return _not_implemented("msa_reconciliation_prepare_batch", "mcp:propose")


@mcp.tool(annotations=READ)
def msa_reconciliation_review_status(proposal_id: str) -> dict[str, Any]:
    """Read a reconciliation proposal/review status when that workflow exists."""
    return _not_implemented("msa_reconciliation_review_status", "mcp:read")


@mcp.tool(annotations=WRITE)
def msa_inventory_write_price(product_id: str, price: float, idempotency_key: str, reason: str | None = None) -> dict[str, Any]:
    """Future typed inventory price write. Present in schema but policy-disabled until authorized."""
    return _write_gate("msa_inventory_write_price") or _deny("msa_inventory_write_price", "mcp:write", reason="NOT_ENABLED")


@mcp.tool(annotations=WRITE)
def msa_inventory_write_metadata(product_id: str, field: str, value: str, idempotency_key: str, reason: str | None = None) -> dict[str, Any]:
    """Future allowlisted product metadata write; arbitrary database columns are never accepted."""
    return _write_gate("msa_inventory_write_metadata") or _deny("msa_inventory_write_metadata", "mcp:write", reason="NOT_ENABLED")


@mcp.tool(annotations=WRITE)
def msa_inventory_write_receive(product_id: str, quantity: float, unit: str, idempotency_key: str, lot_id: str | None = None) -> dict[str, Any]:
    """Future typed stock receipt/batch intake operation."""
    return _write_gate("msa_inventory_write_receive") or _deny("msa_inventory_write_receive", "mcp:write", reason="NOT_ENABLED")


@mcp.tool(annotations=DESTRUCTIVE)
def msa_inventory_write_adjustment(product_id: str, quantity_delta: float, idempotency_key: str, reason: str) -> dict[str, Any]:
    """Future controlled correction/adjustment; never silently rewrites committed history."""
    return _write_gate("msa_inventory_write_adjustment") or _deny("msa_inventory_write_adjustment", "mcp:write", reason="NOT_ENABLED")


@mcp.tool(annotations=WRITE)
def msa_transfer_create(product_id: str, quantity: float, source_location_id: str, destination_location_id: str, idempotency_key: str) -> dict[str, Any]:
    """Future typed Main-to-Sub transfer operation."""
    return _write_gate("msa_transfer_create") or _deny("msa_transfer_create", "mcp:write", reason="NOT_ENABLED")


@mcp.tool(annotations=DESTRUCTIVE)
def msa_transfer_reverse(operation_id: str, idempotency_key: str, reason: str) -> dict[str, Any]:
    """Future reversal linked to an original transfer operation."""
    return _write_gate("msa_transfer_reverse") or _deny("msa_transfer_reverse", "mcp:write", reason="NOT_ENABLED")


@mcp.tool(annotations=READ)
def msa_calculator_calculate(items: list[dict[str, Any]], extra_fee: float = 0.0) -> dict[str, Any]:
    """Future deterministic Smart Calculator operation; current schema placeholder only."""
    return _not_implemented("msa_calculator_calculate", "mcp:read")


@mcp.tool(annotations=WRITE)
def msa_calculator_save_receipt(calculation_id: str, receiver: str | None = None, note: str | None = None) -> dict[str, Any]:
    """Future persisted calculator/receipt operation."""
    return _write_gate("msa_calculator_save_receipt") or _deny("msa_calculator_save_receipt", "mcp:write", reason="NOT_ENABLED")


@mcp.tool(annotations=WRITE)
def msa_calculator_dispense(calculation_id: str, location_id: str, idempotency_key: str) -> dict[str, Any]:
    """Future Sub Store dispense/deduction operation."""
    return _write_gate("msa_calculator_dispense") or _deny("msa_calculator_dispense", "mcp:write", reason="NOT_ENABLED")


@mcp.tool(annotations=READ)
def msa_analysis_stock_health() -> dict[str, Any]:
    """Future deterministic stock-health analysis."""
    return _not_implemented("msa_analysis_stock_health", "mcp:read")


@mcp.tool(annotations=READ)
def msa_analysis_expiry_risk() -> dict[str, Any]:
    """Future deterministic expiry-risk analysis."""
    return _not_implemented("msa_analysis_expiry_risk", "mcp:read")


@mcp.tool(annotations=READ)
def msa_analysis_reorder_outlook() -> dict[str, Any]:
    """Future deterministic reorder outlook with explicit reorder basis."""
    return _not_implemented("msa_analysis_reorder_outlook", "mcp:read")


@mcp.tool(annotations=READ)
def msa_analysis_data_quality() -> dict[str, Any]:
    """Read current shadow REVIEW/CONFLICT/NEW_UNMAPPED reason diagnostics."""
    denied = _gate("msa_analysis_data_quality", "mcp:read")
    if denied:
        return denied
    return {"ok": True, "status": "AVAILABLE", **shadow_review_reasons(migration_batch_id=None)}


# Owner/control-plane tools are intentionally visible in the long-lived schema but remain policy-disabled.
@mcp.tool(annotations=READ)
def msa_users_list() -> dict[str, Any]:
    """Future Owner-only human-user list through MCP."""
    return _not_implemented("msa_users_list", "mcp:control")


@mcp.tool(annotations=READ)
def msa_users_get(user_id: str) -> dict[str, Any]:
    """Future Owner-only human-user detail through MCP."""
    return _not_implemented("msa_users_get", "mcp:control")


@mcp.tool(annotations=WRITE)
def msa_users_approve_request(user_id: str, role: str) -> dict[str, Any]:
    """Future Owner-only access-request approval."""
    return _control_gate("msa_users_approve_request") or _deny("msa_users_approve_request", "mcp:control", reason="NOT_ENABLED")


@mcp.tool(annotations=DESTRUCTIVE)
def msa_users_reject_request(user_id: str) -> dict[str, Any]:
    """Future Owner-only access-request rejection."""
    return _control_gate("msa_users_reject_request") or _deny("msa_users_reject_request", "mcp:control", reason="NOT_ENABLED")


@mcp.tool(annotations=WRITE)
def msa_users_change_role(user_id: str, role: str) -> dict[str, Any]:
    """Future Owner-only human role change."""
    return _control_gate("msa_users_change_role") or _deny("msa_users_change_role", "mcp:control", reason="NOT_ENABLED")


@mcp.tool(annotations=DESTRUCTIVE)
def msa_users_disable(user_id: str) -> dict[str, Any]:
    """Future Owner-only account disable operation."""
    return _control_gate("msa_users_disable") or _deny("msa_users_disable", "mcp:control", reason="NOT_ENABLED")


@mcp.tool(annotations=WRITE)
def msa_users_reactivate(user_id: str) -> dict[str, Any]:
    """Future Owner-only account reactivation."""
    return _control_gate("msa_users_reactivate") or _deny("msa_users_reactivate", "mcp:control", reason="NOT_ENABLED")


@mcp.tool(annotations=DESTRUCTIVE)
def msa_users_revoke_sessions(user_id: str) -> dict[str, Any]:
    """Future Owner-only user-session revocation."""
    return _control_gate("msa_users_revoke_sessions") or _deny("msa_users_revoke_sessions", "mcp:control", reason="NOT_ENABLED")


@mcp.tool(annotations=READ)
def msa_agents_list() -> dict[str, Any]:
    """Future Owner-only AI-agent/external-client list."""
    return _not_implemented("msa_agents_list", "mcp:control")


@mcp.tool(annotations=READ)
def msa_agents_get(agent_id: str) -> dict[str, Any]:
    """Future Owner-only AI-agent detail."""
    return _not_implemented("msa_agents_get", "mcp:control")


@mcp.tool(annotations=WRITE)
def msa_agents_create(name: str, runtime_mode: str) -> dict[str, Any]:
    """Future Owner-only AI-agent creation."""
    return _control_gate("msa_agents_create") or _deny("msa_agents_create", "mcp:control", reason="NOT_ENABLED")


@mcp.tool(annotations=WRITE)
def msa_agents_update_policy(agent_id: str, capability_names: list[str], location_ids: list[str] | None = None) -> dict[str, Any]:
    """Future Owner-only AI-agent capability/location policy update."""
    return _control_gate("msa_agents_update_policy") or _deny("msa_agents_update_policy", "mcp:control", reason="NOT_ENABLED")


@mcp.tool(annotations=WRITE)
def msa_agents_enable(agent_id: str) -> dict[str, Any]:
    """Future Owner-only AI-agent enable operation."""
    return _control_gate("msa_agents_enable") or _deny("msa_agents_enable", "mcp:control", reason="NOT_ENABLED")


@mcp.tool(annotations=DESTRUCTIVE)
def msa_agents_disable(agent_id: str) -> dict[str, Any]:
    """Future Owner-only AI-agent disable operation."""
    return _control_gate("msa_agents_disable") or _deny("msa_agents_disable", "mcp:control", reason="NOT_ENABLED")


@mcp.tool(annotations=DESTRUCTIVE)
def msa_agents_revoke(agent_id: str) -> dict[str, Any]:
    """Future Owner-only AI-agent revocation."""
    return _control_gate("msa_agents_revoke") or _deny("msa_agents_revoke", "mcp:control", reason="NOT_ENABLED")


@mcp.tool(annotations=DESTRUCTIVE)
def msa_agents_rotate_credential(agent_id: str) -> dict[str, Any]:
    """Future Owner-only external/agent credential rotation."""
    return _control_gate("msa_agents_rotate_credential") or _deny("msa_agents_rotate_credential", "mcp:control", reason="NOT_ENABLED")


@mcp.tool(annotations=READ)
def msa_providers_list() -> dict[str, Any]:
    """Future Owner-only provider registry list."""
    return _not_implemented("msa_providers_list", "mcp:control")


@mcp.tool(annotations=READ)
def msa_providers_get(provider_id: str) -> dict[str, Any]:
    """Future Owner-only provider registry detail."""
    return _not_implemented("msa_providers_get", "mcp:control")


@mcp.tool(annotations=WRITE)
def msa_providers_create(provider_type: str, name: str, base_url: str | None = None) -> dict[str, Any]:
    """Future Owner-only provider creation; plaintext provider secrets are never returned."""
    return _control_gate("msa_providers_create") or _deny("msa_providers_create", "mcp:control", reason="NOT_ENABLED")


@mcp.tool(annotations=WRITE)
def msa_providers_update(provider_id: str, name: str | None = None, base_url: str | None = None) -> dict[str, Any]:
    """Future Owner-only provider configuration update."""
    return _control_gate("msa_providers_update") or _deny("msa_providers_update", "mcp:control", reason="NOT_ENABLED")


@mcp.tool(annotations=DESTRUCTIVE)
def msa_providers_disable(provider_id: str) -> dict[str, Any]:
    """Future Owner-only provider disable operation."""
    return _control_gate("msa_providers_disable") or _deny("msa_providers_disable", "mcp:control", reason="NOT_ENABLED")


@mcp.tool(annotations=WRITE)
def msa_providers_test_connection(provider_id: str) -> dict[str, Any]:
    """Future Owner-only provider connectivity test."""
    return _control_gate("msa_providers_test_connection") or _deny("msa_providers_test_connection", "mcp:control", reason="NOT_ENABLED")


@mcp.tool(annotations=WRITE)
def msa_providers_fetch_models(provider_id: str) -> dict[str, Any]:
    """Future Owner-only model-catalog refresh."""
    return _control_gate("msa_providers_fetch_models") or _deny("msa_providers_fetch_models", "mcp:control", reason="NOT_ENABLED")


@mcp.tool(annotations=WRITE)
def msa_providers_test_model(provider_id: str, model_id: str) -> dict[str, Any]:
    """Future Owner-only minimal model compatibility test."""
    return _control_gate("msa_providers_test_model") or _deny("msa_providers_test_model", "mcp:control", reason="NOT_ENABLED")


@mcp.tool(annotations=WRITE)
def msa_providers_assign_model(agent_id: str, provider_id: str, model_id: str) -> dict[str, Any]:
    """Future Owner-only primary model assignment."""
    return _control_gate("msa_providers_assign_model") or _deny("msa_providers_assign_model", "mcp:control", reason="NOT_ENABLED")


@mcp.tool(annotations=WRITE)
def msa_providers_set_fallbacks(agent_id: str, assignments: list[dict[str, str]]) -> dict[str, Any]:
    """Future Owner-only ordered fallback-model assignment."""
    return _control_gate("msa_providers_set_fallbacks") or _deny("msa_providers_set_fallbacks", "mcp:control", reason="NOT_ENABLED")


@mcp.tool(annotations=READ)
def msa_audit_query(limit: int = 50) -> dict[str, Any]:
    """Future bounded actor-aware operational audit query."""
    return _not_implemented("msa_audit_query", "mcp:read")


@mcp.tool(annotations=READ)
def msa_audit_get_operation(operation_id: str) -> dict[str, Any]:
    """Future operation-ledger lookup."""
    return _not_implemented("msa_audit_get_operation", "mcp:read")


@mcp.tool(annotations=READ)
def msa_audit_get_actor_history(actor_id: str, limit: int = 50) -> dict[str, Any]:
    """Future bounded actor-history lookup."""
    return _not_implemented("msa_audit_get_actor_history", "mcp:read")


@mcp.tool(annotations=READ)
def msa_audit_get_reconciliation_history(product_id: str, limit: int = 50) -> dict[str, Any]:
    """Future reconciliation-history lookup."""
    return _not_implemented("msa_audit_get_reconciliation_history", "mcp:read")


@mcp.tool(annotations=READ)
def msa_settings_get() -> dict[str, Any]:
    """Future Owner-only typed global settings read."""
    return _not_implemented("msa_settings_get", "mcp:control")


@mcp.tool(annotations=WRITE)
def msa_settings_update(setting_name: str, value: str) -> dict[str, Any]:
    """Future Owner-only typed setting update; never a generic environment/secret editor."""
    return _control_gate("msa_settings_update") or _deny("msa_settings_update", "mcp:control", reason="NOT_ENABLED")


_mcp_host = PUBLIC_BASE_URL.split("//", 1)[-1].split("/", 1)[0]
transport_security = TransportSecuritySettings(
    allowed_hosts=[_mcp_host, f"{_mcp_host}:*", "127.0.0.1", "127.0.0.1:*", "localhost", "localhost:*"],
    allowed_origins=[PUBLIC_BASE_URL, "https://chatgpt.com", "https://chat.openai.com"],
)

# Mounted by app.main. The host application owns mcp.session_manager.run().
mcp_http_app = mcp.streamable_http_app(
    stateless_http=True,
    json_response=True,
    transport_security=transport_security,
)
