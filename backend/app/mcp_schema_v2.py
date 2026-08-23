from __future__ import annotations

import hashlib
import os
from typing import Any, Literal

from mcp.types import ToolAnnotations

from app.mcp_server import _control_gate, _deny, _gate, _not_implemented, mcp

SCHEMA_VERSION = "2026-08-23.v2"
READ = ToolAnnotations(read_only_hint=True, open_world_hint=False)
PROPOSE = ToolAnnotations(read_only_hint=False, destructive_hint=False, idempotent_hint=False, open_world_hint=False)
OUTBOUND = ToolAnnotations(read_only_hint=False, destructive_hint=False, idempotent_hint=False, open_world_hint=True)
WRITE = ToolAnnotations(read_only_hint=False, destructive_hint=False, idempotent_hint=True, open_world_hint=False)
DESTRUCTIVE = ToolAnnotations(read_only_hint=False, destructive_hint=True, idempotent_hint=True, open_world_hint=False)

FINAL_TOOL_NAMES = tuple(sorted((
    "msa_identity_whoami",
    "msa_system_status",
    "msa_system_capabilities",
    "msa_inventory_read_summary",
    "msa_inventory_read_search",
    "msa_inventory_read_item",
    "msa_inventory_read_lots",
    "msa_inventory_read_location_balance",
    "msa_catalogue_read_current",
    "msa_catalogue_read_history",
    "msa_reconciliation_classify",
    "msa_reconciliation_prepare_batch",
    "msa_reconciliation_review_status",
    "msa_inventory_write_price",
    "msa_inventory_write_metadata",
    "msa_inventory_write_receive",
    "msa_inventory_write_adjustment",
    "msa_transfer_create",
    "msa_transfer_reverse",
    "msa_calculator_calculate",
    "msa_calculator_save_receipt",
    "msa_calculator_dispense",
    "msa_analysis_stock_health",
    "msa_analysis_expiry_risk",
    "msa_analysis_reorder_outlook",
    "msa_analysis_data_quality",
    "msa_users_list",
    "msa_users_get",
    "msa_users_approve_request",
    "msa_users_reject_request",
    "msa_users_change_role",
    "msa_users_disable",
    "msa_users_reactivate",
    "msa_users_revoke_sessions",
    "msa_agents_list",
    "msa_agents_get",
    "msa_agents_create",
    "msa_agents_update_policy",
    "msa_agents_enable",
    "msa_agents_disable",
    "msa_agents_revoke",
    "msa_agents_rotate_credential",
    "msa_providers_list",
    "msa_providers_get",
    "msa_providers_create",
    "msa_providers_update",
    "msa_providers_disable",
    "msa_providers_test_connection",
    "msa_providers_fetch_models",
    "msa_providers_test_model",
    "msa_providers_assign_model",
    "msa_providers_set_fallbacks",
    "msa_audit_query",
    "msa_audit_get_operation",
    "msa_audit_get_actor_history",
    "msa_audit_get_reconciliation_history",
    "msa_settings_get",
    "msa_settings_update",
    "msa_shadow_read_rows",
    "msa_shadow_read_batch",
    "msa_shadow_read_review_reasons",
    "msa_system_schema_manifest",
    "msa_inventory_read_movements",
    "msa_catalogue_query",
    "msa_reconciliation_query",
    "msa_reconciliation_review",
    "msa_transfer_query",
    "msa_locations_query",
    "msa_locations_manage",
    "msa_store_policy_get",
    "msa_store_policy_update",
    "msa_preferences_get",
    "msa_preferences_update",
    "msa_receipts_query",
    "msa_analysis_query",
    "msa_users_access_requests",
    "msa_users_update_profile",
    "msa_agent_invoke",
    "msa_agent_sessions_query",
    "msa_agent_sessions_manage",
    "msa_providers_catalog_query",
    "msa_providers_catalog_manage",
    "msa_audit_search",
    "msa_alerts_query",
    "msa_alerts_manage",
    "msa_notifications_query",
    "msa_notifications_manage",
    "msa_sync_query",
    "msa_sync_manage",
    "msa_sources_query",
    "msa_sources_manage",
    "msa_integrations_query",
    "msa_integrations_manage",
    "msa_migration_control",
)))
FINAL_TOOL_COUNT = len(FINAL_TOOL_NAMES)
FINAL_TOOL_HASH = hashlib.sha256("\n".join(FINAL_TOOL_NAMES).encode("utf-8")).hexdigest()


@mcp.tool(annotations=READ)
def msa_system_schema_manifest() -> dict[str, Any]:
    """Return the durable MSA MCP schema identity used to detect stale client action snapshots."""
    denied = _gate("msa_system_schema_manifest", "mcp:read")
    if denied:
        return denied
    return {
        "ok": True,
        "status": "AVAILABLE",
        "schema_family": "msa-mcp",
        "schema_version": SCHEMA_VERSION,
        "expected_tool_count": FINAL_TOOL_COUNT,
        "tool_name_sha256": FINAL_TOOL_HASH,
        "build_sha": os.getenv("MSA_BUILD_SHA", "unknown"),
        "excluded_capability_classes": [
            "credential_or_secret_provisioning_and_readback",
            "password_or_token_secret_access",
            "arbitrary_sql_or_database_console",
            "shell_or_filesystem_access",
        ],
        "domains": [
            "identity", "system", "inventory", "shadow_migration", "catalogue", "reconciliation",
            "transfer", "locations", "store_policy", "preferences", "calculator", "receipts",
            "analysis", "users", "agents", "multi_agent_sessions", "providers", "audit",
            "alerts", "notifications", "sync", "sources", "integrations", "settings", "migration_control",
        ],
        "database_canonical": False,
        "migration_baseline_accepted": False,
    }


@mcp.tool(annotations=READ)
def msa_inventory_read_movements(
    product_id: str | None = None,
    location_id: str | None = None,
    movement_type: str | None = None,
    start_at: str | None = None,
    end_at: str | None = None,
    limit: int = 100,
    offset: int = 0,
) -> dict[str, Any]:
    """Future bounded inventory movement/history read by product, location, type, or date range."""
    return _not_implemented("msa_inventory_read_movements", "mcp:read")


@mcp.tool(annotations=READ)
def msa_catalogue_query(
    action: Literal["search", "get"],
    query: str | None = None,
    cms_id: str | None = None,
    serial_code: str | None = None,
    limit: int = 50,
    offset: int = 0,
) -> dict[str, Any]:
    """Future typed CMS catalogue search/detail query without arbitrary database access."""
    return _not_implemented("msa_catalogue_query", "mcp:read")


@mcp.tool(annotations=READ)
def msa_reconciliation_query(
    action: Literal["list", "get", "evidence", "history"],
    proposal_id: str | None = None,
    product_id: str | None = None,
    classification: str | None = None,
    status: str | None = None,
    limit: int = 50,
    offset: int = 0,
) -> dict[str, Any]:
    """Future bounded reconciliation proposal/evidence/history query."""
    return _not_implemented("msa_reconciliation_query", "mcp:read")


@mcp.tool(annotations=WRITE)
def msa_reconciliation_review(
    proposal_id: str,
    decision: Literal["approve", "reject", "reopen"],
    reason: str | None = None,
) -> dict[str, Any]:
    """Future Owner policy-gated reconciliation review decision; no authority is implied by visibility."""
    return _control_gate("msa_reconciliation_review") or _deny("msa_reconciliation_review", "mcp:control", reason="NOT_ENABLED")


@mcp.tool(annotations=READ)
def msa_transfer_query(
    action: Literal["list", "get", "history", "status"],
    transfer_id: str | None = None,
    product_id: str | None = None,
    source_location_id: str | None = None,
    destination_location_id: str | None = None,
    start_at: str | None = None,
    end_at: str | None = None,
    limit: int = 50,
    offset: int = 0,
) -> dict[str, Any]:
    """Future bounded transfer list/detail/history/status read."""
    return _not_implemented("msa_transfer_query", "mcp:read")


@mcp.tool(annotations=READ)
def msa_locations_query(
    action: Literal["list", "get"],
    location_id: str | None = None,
    location_type: str | None = None,
    active_only: bool = True,
    limit: int = 100,
    offset: int = 0,
) -> dict[str, Any]:
    """Future F7.4 location/store query."""
    return _not_implemented("msa_locations_query", "mcp:read")


@mcp.tool(annotations=WRITE)
def msa_locations_manage(
    action: Literal["create", "update", "disable", "reactivate"],
    location_id: str | None = None,
    name: str | None = None,
    location_type: str | None = None,
    parent_location_id: str | None = None,
    metadata: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Future Owner-only typed location create/update/lifecycle control."""
    return _control_gate("msa_locations_manage") or _deny("msa_locations_manage", "mcp:control", reason="NOT_ENABLED")


@mcp.tool(annotations=READ)
def msa_store_policy_get(location_id: str | None = None) -> dict[str, Any]:
    """Future typed store/location policy read."""
    return _not_implemented("msa_store_policy_get", "mcp:read")


@mcp.tool(annotations=WRITE)
def msa_store_policy_update(location_id: str | None, settings: dict[str, Any]) -> dict[str, Any]:
    """Future Owner-only allowlisted store policy update."""
    return _control_gate("msa_store_policy_update") or _deny("msa_store_policy_update", "mcp:control", reason="NOT_ENABLED")


@mcp.tool(annotations=READ)
def msa_preferences_get(scope: Literal["global", "user", "location"] = "global", scope_id: str | None = None) -> dict[str, Any]:
    """Future typed non-secret MSA preference read."""
    return _not_implemented("msa_preferences_get", "mcp:read")


@mcp.tool(annotations=WRITE)
def msa_preferences_update(
    scope: Literal["global", "user", "location"],
    settings: dict[str, Any],
    scope_id: str | None = None,
) -> dict[str, Any]:
    """Future allowlisted non-secret preference update."""
    return _control_gate("msa_preferences_update") or _deny("msa_preferences_update", "mcp:control", reason="NOT_ENABLED")


@mcp.tool(annotations=READ)
def msa_receipts_query(
    action: Literal["list", "get", "history", "reversal_status"],
    receipt_id: str | None = None,
    product_id: str | None = None,
    receiver: str | None = None,
    start_at: str | None = None,
    end_at: str | None = None,
    limit: int = 50,
    offset: int = 0,
) -> dict[str, Any]:
    """Future bounded calculator/receipt history query."""
    return _not_implemented("msa_receipts_query", "mcp:read")


@mcp.tool(annotations=READ)
def msa_analysis_query(
    analysis_type: Literal["stock_health", "expiry_risk", "reorder_outlook", "data_quality", "usage", "price", "movement"],
    product_id: str | None = None,
    location_id: str | None = None,
    start_at: str | None = None,
    end_at: str | None = None,
    limit: int = 100,
) -> dict[str, Any]:
    """Future typed deterministic analysis selector with bounded filters."""
    return _not_implemented("msa_analysis_query", "mcp:read")


@mcp.tool(annotations=READ)
def msa_users_access_requests(
    action: Literal["list", "get"],
    request_id: str | None = None,
    status: str | None = None,
    limit: int = 50,
    offset: int = 0,
) -> dict[str, Any]:
    """Future Owner-only access-request query without credentials or password material."""
    return _not_implemented("msa_users_access_requests", "mcp:control")


@mcp.tool(annotations=WRITE)
def msa_users_update_profile(
    user_id: str,
    display_name: str | None = None,
    recovery_email: str | None = None,
    metadata: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Future Owner-only typed non-credential human profile update."""
    return _control_gate("msa_users_update_profile") or _deny("msa_users_update_profile", "mcp:control", reason="NOT_ENABLED")


@mcp.tool(annotations=OUTBOUND)
def msa_agent_invoke(
    agent_id: str,
    instruction: str,
    context: dict[str, Any] | None = None,
    max_output_tokens: int | None = None,
) -> dict[str, Any]:
    """Future invoke of one named INTERNAL_MODEL agent using its saved provider/model assignment."""
    return _not_implemented("msa_agent_invoke", "mcp:propose")


@mcp.tool(annotations=READ)
def msa_agent_sessions_query(
    action: Literal["list", "get", "participants", "runs", "results"],
    session_id: str | None = None,
    mode: str | None = None,
    state: str | None = None,
    limit: int = 50,
    offset: int = 0,
) -> dict[str, Any]:
    """Future multi-agent session topology/run/result query."""
    return _not_implemented("msa_agent_sessions_query", "mcp:read")


@mcp.tool(annotations=OUTBOUND)
def msa_agent_sessions_manage(
    action: Literal["create", "update", "run", "close"],
    session_id: str | None = None,
    name: str | None = None,
    mode: Literal["GROUP", "COMPARE", "REVIEW", "DEBATE"] | None = None,
    participant_agent_ids: list[str] | None = None,
    instruction: str | None = None,
) -> dict[str, Any]:
    """Future create/update/run/close multi-agent sessions; execution never unions participant authority."""
    denied = _gate("msa_agent_sessions_manage", "mcp:control")
    if denied:
        return denied
    return _deny("msa_agent_sessions_manage", "mcp:control", reason="NOT_ENABLED")


@mcp.tool(annotations=READ)
def msa_providers_catalog_query(
    action: Literal["discovered_models", "saved_models", "assignments", "model_health"],
    provider_id: str | None = None,
    agent_id: str | None = None,
    model_id: str | None = None,
    query: str | None = None,
    limit: int = 100,
    offset: int = 0,
) -> dict[str, Any]:
    """Future Owner-only provider/model catalog metadata query; never returns provider credentials."""
    return _not_implemented("msa_providers_catalog_query", "mcp:control")


@mcp.tool(annotations=WRITE)
def msa_providers_catalog_manage(
    action: Literal["save_model", "remove_saved_model", "enable_saved_model", "disable_saved_model", "unassign_model"],
    provider_id: str | None = None,
    model_id: str | None = None,
    agent_id: str | None = None,
) -> dict[str, Any]:
    """Future Owner-only non-secret provider saved-model/assignment control."""
    return _control_gate("msa_providers_catalog_manage") or _deny("msa_providers_catalog_manage", "mcp:control", reason="NOT_ENABLED")


@mcp.tool(annotations=READ)
def msa_audit_search(
    start_at: str | None = None,
    end_at: str | None = None,
    month: str | None = None,
    human_user_id: str | None = None,
    agent_id: str | None = None,
    runtime_type: str | None = None,
    client_id: str | None = None,
    provider_id: str | None = None,
    model_id: str | None = None,
    operation: str | None = None,
    outcome: str | None = None,
    location_id: str | None = None,
    target_id: str | None = None,
    correlation_id: str | None = None,
    operation_id: str | None = None,
    limit: int = 100,
    offset: int = 0,
) -> dict[str, Any]:
    """Future full actor-aware bounded Audit search with month/date/actor/runtime/provider/operation/result filters."""
    return _not_implemented("msa_audit_search", "mcp:read")


@mcp.tool(annotations=READ)
def msa_alerts_query(
    action: Literal["list", "get", "rules", "history"],
    alert_id: str | None = None,
    status: str | None = None,
    severity: str | None = None,
    location_id: str | None = None,
    limit: int = 100,
    offset: int = 0,
) -> dict[str, Any]:
    """Future bounded alerts/rules/history query."""
    return _not_implemented("msa_alerts_query", "mcp:read")


@mcp.tool(annotations=WRITE)
def msa_alerts_manage(
    action: Literal["acknowledge", "snooze", "create_rule", "update_rule", "disable_rule"],
    alert_id: str | None = None,
    rule_id: str | None = None,
    settings: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Future policy-gated alert acknowledgement/snooze and Owner alert-rule management."""
    return _control_gate("msa_alerts_manage") or _deny("msa_alerts_manage", "mcp:control", reason="NOT_ENABLED")


@mcp.tool(annotations=READ)
def msa_notifications_query(
    action: Literal["list", "get", "history", "preferences"],
    notification_id: str | None = None,
    status: str | None = None,
    channel: str | None = None,
    limit: int = 100,
    offset: int = 0,
) -> dict[str, Any]:
    """Future bounded notification/history/preference query."""
    return _not_implemented("msa_notifications_query", "mcp:read")


@mcp.tool(annotations=WRITE)
def msa_notifications_manage(
    action: Literal["mark_read", "mark_unread", "update_preferences", "test_delivery"],
    notification_id: str | None = None,
    settings: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Future notification-state/preference/test-delivery control without exposing channel credentials."""
    return _control_gate("msa_notifications_manage") or _deny("msa_notifications_manage", "mcp:control", reason="NOT_ENABLED")


@mcp.tool(annotations=READ)
def msa_sync_query(
    action: Literal["status", "history", "get_job", "diagnostics"],
    sync_job_id: str | None = None,
    source_kind: str | None = None,
    limit: int = 50,
    offset: int = 0,
) -> dict[str, Any]:
    """Future F10 sync status/history/job diagnostics query."""
    return _not_implemented("msa_sync_query", "mcp:read")


@mcp.tool(annotations=WRITE)
def msa_sync_manage(
    action: Literal["preview", "run", "retry", "cancel"],
    source_kind: str,
    sync_job_id: str | None = None,
    options: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Future typed sync preview/run/retry/cancel; never accepts raw credentials or arbitrary SQL."""
    return _control_gate("msa_sync_manage") or _deny("msa_sync_manage", "mcp:control", reason="NOT_ENABLED")


@mcp.tool(annotations=READ)
def msa_sources_query(
    action: Literal["list", "get", "status", "preview"],
    source_id: str | None = None,
    source_kind: str | None = None,
    status: str | None = None,
    limit: int = 50,
    offset: int = 0,
) -> dict[str, Any]:
    """Future typed source-evidence/ingest preview query; no arbitrary filesystem or HTTP proxy access."""
    return _not_implemented("msa_sources_query", "mcp:read")


@mcp.tool(annotations=WRITE)
def msa_sources_manage(
    action: Literal["ingest", "reprocess", "archive"],
    source_kind: str,
    source_reference: str,
    options: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Future bounded approved-source ingest/reprocess/archive operation."""
    return _control_gate("msa_sources_manage") or _deny("msa_sources_manage", "mcp:control", reason="NOT_ENABLED")


@mcp.tool(annotations=READ)
def msa_integrations_query(
    action: Literal["list", "get", "status", "history"],
    integration_id: str | None = None,
    integration_type: str | None = None,
    limit: int = 50,
    offset: int = 0,
) -> dict[str, Any]:
    """Future integration metadata/status/history query without credentials."""
    return _not_implemented("msa_integrations_query", "mcp:control")


@mcp.tool(annotations=WRITE)
def msa_integrations_manage(
    action: Literal["test", "enable", "disable"],
    integration_id: str,
) -> dict[str, Any]:
    """Future Owner-only integration test/lifecycle control; credential provisioning is excluded."""
    return _control_gate("msa_integrations_manage") or _deny("msa_integrations_manage", "mcp:control", reason="NOT_ENABLED")


@mcp.tool(annotations=DESTRUCTIVE)
def msa_migration_control(
    action: Literal["accept_baseline", "reject_baseline", "promote_canonical", "demote_canonical"],
    migration_batch_id: str | None = None,
    reason: str | None = None,
    confirmation_reference: str | None = None,
) -> dict[str, Any]:
    """Future explicit Owner migration-baseline/canonicality control; schema-visible but F11-policy-disabled."""
    return _control_gate("msa_migration_control") or _deny("msa_migration_control", "mcp:control", reason="NOT_ENABLED")
