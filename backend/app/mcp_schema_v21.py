from __future__ import annotations

import hashlib
from typing import Any

from mcp.types import ToolAnnotations

import app.mcp_schema_v2 as schema
from app.mcp_server import _control_gate, _deny, _gate, _not_implemented, mcp

READ = ToolAnnotations(read_only_hint=True, open_world_hint=False)
OUTBOUND = ToolAnnotations(read_only_hint=False, destructive_hint=False, idempotent_hint=False, open_world_hint=True)
WRITE = ToolAnnotations(read_only_hint=False, destructive_hint=False, idempotent_hint=True, open_world_hint=False)
DESTRUCTIVE = ToolAnnotations(read_only_hint=False, destructive_hint=True, idempotent_hint=True, open_world_hint=False)

# These v2 query/manage tools originally used closed Literal enums for action selectors.
# A ChatGPT custom app may snapshot those enums, forcing a future rescan merely to add a
# new safe action. Replace them before transport construction with open string selectors;
# backend implementations must enforce explicit allowlists per action at execution time.
_REPLACE_WITH_OPEN_ACTION_SCHEMA = (
    "msa_catalogue_query",
    "msa_reconciliation_query",
    "msa_reconciliation_review",
    "msa_transfer_query",
    "msa_locations_query",
    "msa_locations_manage",
    "msa_preferences_get",
    "msa_preferences_update",
    "msa_receipts_query",
    "msa_analysis_query",
    "msa_users_access_requests",
    "msa_agent_sessions_query",
    "msa_agent_sessions_manage",
    "msa_providers_catalog_query",
    "msa_providers_catalog_manage",
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
)
for _tool_name in _REPLACE_WITH_OPEN_ACTION_SCHEMA:
    mcp.remove_tool(_tool_name)


@mcp.tool(annotations=READ)
def msa_catalogue_query(
    action: str,
    query: str | None = None,
    cms_id: str | None = None,
    serial_code: str | None = None,
    limit: int = 50,
    offset: int = 0,
) -> dict[str, Any]:
    """Typed CMS catalogue query. Backend allowlists supported actions such as search/get."""
    return _not_implemented("msa_catalogue_query", "mcp:read")


@mcp.tool(annotations=READ)
def msa_reconciliation_query(
    action: str,
    proposal_id: str | None = None,
    product_id: str | None = None,
    classification: str | None = None,
    status: str | None = None,
    limit: int = 50,
    offset: int = 0,
) -> dict[str, Any]:
    """Typed reconciliation proposal/evidence/history query; action values are backend-allowlisted."""
    return _not_implemented("msa_reconciliation_query", "mcp:read")


@mcp.tool(annotations=WRITE)
def msa_reconciliation_review(proposal_id: str, decision: str, reason: str | None = None) -> dict[str, Any]:
    """Future Owner reconciliation review decision; backend allowlists decision values."""
    return _control_gate("msa_reconciliation_review") or _deny("msa_reconciliation_review", "mcp:control", reason="NOT_ENABLED")


@mcp.tool(annotations=READ)
def msa_transfer_query(
    action: str,
    transfer_id: str | None = None,
    product_id: str | None = None,
    source_location_id: str | None = None,
    destination_location_id: str | None = None,
    start_at: str | None = None,
    end_at: str | None = None,
    limit: int = 50,
    offset: int = 0,
) -> dict[str, Any]:
    """Typed transfer list/detail/history/status query with backend-allowlisted actions."""
    return _not_implemented("msa_transfer_query", "mcp:read")


@mcp.tool(annotations=READ)
def msa_locations_query(
    action: str,
    location_id: str | None = None,
    location_type: str | None = None,
    active_only: bool = True,
    limit: int = 100,
    offset: int = 0,
) -> dict[str, Any]:
    """Future F7.4 location/store query with backend-allowlisted actions."""
    return _not_implemented("msa_locations_query", "mcp:read")


@mcp.tool(annotations=WRITE)
def msa_locations_manage(
    action: str,
    location_id: str | None = None,
    name: str | None = None,
    location_type: str | None = None,
    parent_location_id: str | None = None,
    metadata: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Future Owner typed location management; action and metadata keys are backend-allowlisted."""
    return _control_gate("msa_locations_manage") or _deny("msa_locations_manage", "mcp:control", reason="NOT_ENABLED")


@mcp.tool(annotations=READ)
def msa_preferences_get(scope: str = "global", scope_id: str | None = None) -> dict[str, Any]:
    """Future typed non-secret MSA preference read; backend validates scope names."""
    return _not_implemented("msa_preferences_get", "mcp:read")


@mcp.tool(annotations=WRITE)
def msa_preferences_update(scope: str, settings: dict[str, Any], scope_id: str | None = None) -> dict[str, Any]:
    """Future allowlisted non-secret preference update; backend validates scope and setting keys."""
    return _control_gate("msa_preferences_update") or _deny("msa_preferences_update", "mcp:control", reason="NOT_ENABLED")


@mcp.tool(annotations=READ)
def msa_receipts_query(
    action: str,
    receipt_id: str | None = None,
    product_id: str | None = None,
    receiver: str | None = None,
    start_at: str | None = None,
    end_at: str | None = None,
    limit: int = 50,
    offset: int = 0,
) -> dict[str, Any]:
    """Future bounded receipt history/detail query; backend allowlists action values."""
    return _not_implemented("msa_receipts_query", "mcp:read")


@mcp.tool(annotations=READ)
def msa_analysis_query(
    analysis_type: str,
    product_id: str | None = None,
    location_id: str | None = None,
    start_at: str | None = None,
    end_at: str | None = None,
    limit: int = 100,
) -> dict[str, Any]:
    """Future deterministic analysis selector; backend allowlists analysis types such as FIFO/data-quality/usage/price."""
    return _not_implemented("msa_analysis_query", "mcp:read")


@mcp.tool(annotations=READ)
def msa_users_access_requests(
    action: str,
    request_id: str | None = None,
    status: str | None = None,
    limit: int = 50,
    offset: int = 0,
) -> dict[str, Any]:
    """Future Owner access-request query without credential/password material."""
    return _not_implemented("msa_users_access_requests", "mcp:control")


@mcp.tool(annotations=READ)
def msa_agent_sessions_query(
    action: str,
    session_id: str | None = None,
    mode: str | None = None,
    state: str | None = None,
    limit: int = 50,
    offset: int = 0,
) -> dict[str, Any]:
    """Future multi-agent session topology/run/result query; backend allowlists action/mode values."""
    return _not_implemented("msa_agent_sessions_query", "mcp:read")


@mcp.tool(annotations=OUTBOUND)
def msa_agent_sessions_manage(
    action: str,
    session_id: str | None = None,
    name: str | None = None,
    mode: str | None = None,
    participant_agent_ids: list[str] | None = None,
    instruction: str | None = None,
) -> dict[str, Any]:
    """Future create/update/run/close multi-agent sessions; backend validates action/mode and never unions authority."""
    denied = _gate("msa_agent_sessions_manage", "mcp:control")
    if denied:
        return denied
    return _deny("msa_agent_sessions_manage", "mcp:control", reason="NOT_ENABLED")


@mcp.tool(annotations=READ)
def msa_providers_catalog_query(
    action: str,
    provider_id: str | None = None,
    agent_id: str | None = None,
    model_id: str | None = None,
    query: str | None = None,
    limit: int = 100,
    offset: int = 0,
) -> dict[str, Any]:
    """Future Owner provider/model catalog metadata query; never returns provider credentials."""
    return _not_implemented("msa_providers_catalog_query", "mcp:control")


@mcp.tool(annotations=WRITE)
def msa_providers_catalog_manage(
    action: str,
    provider_id: str | None = None,
    model_id: str | None = None,
    agent_id: str | None = None,
) -> dict[str, Any]:
    """Future Owner non-secret saved-model/assignment control; backend allowlists actions."""
    return _control_gate("msa_providers_catalog_manage") or _deny("msa_providers_catalog_manage", "mcp:control", reason="NOT_ENABLED")


@mcp.tool(annotations=READ)
def msa_alerts_query(
    action: str,
    alert_id: str | None = None,
    status: str | None = None,
    severity: str | None = None,
    location_id: str | None = None,
    limit: int = 100,
    offset: int = 0,
) -> dict[str, Any]:
    """Future bounded alerts/rules/history query; backend allowlists actions."""
    return _not_implemented("msa_alerts_query", "mcp:read")


@mcp.tool(annotations=WRITE)
def msa_alerts_manage(
    action: str,
    alert_id: str | None = None,
    rule_id: str | None = None,
    settings: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Future alert acknowledgement/snooze/rule management; backend validates actions and setting keys."""
    return _control_gate("msa_alerts_manage") or _deny("msa_alerts_manage", "mcp:control", reason="NOT_ENABLED")


@mcp.tool(annotations=READ)
def msa_notifications_query(
    action: str,
    notification_id: str | None = None,
    status: str | None = None,
    channel: str | None = None,
    limit: int = 100,
    offset: int = 0,
) -> dict[str, Any]:
    """Future bounded notification/history/preference query; backend allowlists actions."""
    return _not_implemented("msa_notifications_query", "mcp:read")


@mcp.tool(annotations=WRITE)
def msa_notifications_manage(
    action: str,
    notification_id: str | None = None,
    settings: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Future notification state/preference/test-delivery control without exposing channel credentials."""
    return _control_gate("msa_notifications_manage") or _deny("msa_notifications_manage", "mcp:control", reason="NOT_ENABLED")


@mcp.tool(annotations=READ)
def msa_sync_query(
    action: str,
    sync_job_id: str | None = None,
    source_kind: str | None = None,
    limit: int = 50,
    offset: int = 0,
) -> dict[str, Any]:
    """Future F10 sync status/history/job diagnostics query; backend allowlists actions."""
    return _not_implemented("msa_sync_query", "mcp:read")


@mcp.tool(annotations=WRITE)
def msa_sync_manage(
    action: str,
    source_kind: str,
    sync_job_id: str | None = None,
    options: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Future typed sync preview/run/retry/cancel; backend allowlists actions/options and never accepts credentials/SQL."""
    return _control_gate("msa_sync_manage") or _deny("msa_sync_manage", "mcp:control", reason="NOT_ENABLED")


@mcp.tool(annotations=READ)
def msa_sources_query(
    action: str,
    source_id: str | None = None,
    source_kind: str | None = None,
    status: str | None = None,
    limit: int = 50,
    offset: int = 0,
) -> dict[str, Any]:
    """Future typed source-evidence/ingest diagnostics; backend allowlists actions and approved source kinds."""
    return _not_implemented("msa_sources_query", "mcp:read")


@mcp.tool(annotations=WRITE)
def msa_sources_manage(
    action: str,
    source_kind: str,
    source_reference: str,
    options: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Future bounded source ingest/reprocess/archive; no arbitrary filesystem/HTTP proxy/credential forwarding."""
    return _control_gate("msa_sources_manage") or _deny("msa_sources_manage", "mcp:control", reason="NOT_ENABLED")


@mcp.tool(annotations=READ)
def msa_integrations_query(
    action: str,
    integration_id: str | None = None,
    integration_type: str | None = None,
    limit: int = 50,
    offset: int = 0,
) -> dict[str, Any]:
    """Future integration metadata/status/history query without credentials."""
    return _not_implemented("msa_integrations_query", "mcp:control")


@mcp.tool(annotations=WRITE)
def msa_integrations_manage(action: str, integration_id: str) -> dict[str, Any]:
    """Future Owner integration test/lifecycle control; backend allowlists actions and credential provisioning is excluded."""
    return _control_gate("msa_integrations_manage") or _deny("msa_integrations_manage", "mcp:control", reason="NOT_ENABLED")


@mcp.tool(annotations=DESTRUCTIVE)
def msa_migration_control(
    action: str,
    migration_batch_id: str | None = None,
    reason: str | None = None,
    confirmation_reference: str | None = None,
) -> dict[str, Any]:
    """Future Owner baseline/canonicality control; backend allowlists actions and F11 policy remains authoritative."""
    return _control_gate("msa_migration_control") or _deny("msa_migration_control", "mcp:control", reason="NOT_ENABLED")


# Additional long-lived slots found during the final roadmap/workflow audit.
@mcp.tool(annotations=WRITE)
def msa_inventory_write_operation(
    action: str,
    product_id: str,
    quantity: float,
    unit: str,
    idempotency_key: str,
    location_id: str | None = None,
    lot_id: str | None = None,
    reason: str | None = None,
    reference_id: str | None = None,
) -> dict[str, Any]:
    """Future typed issue/return/dispose/stocktake-style inventory operation; backend allowlists action values."""
    denied = _gate("msa_inventory_write_operation", "mcp:write")
    if denied:
        return denied
    return _deny("msa_inventory_write_operation", "mcp:write", reason="SLICE_NOT_AUTHORIZED")


@mcp.tool(annotations=WRITE)
def msa_catalogue_manage(
    action: str,
    cms_id: str | None = None,
    serial_code: str | None = None,
    fields: dict[str, Any] | None = None,
    source_reference: str | None = None,
) -> dict[str, Any]:
    """Future Owner typed CMS catalogue/version lifecycle control; backend allowlists action/field keys."""
    return _control_gate("msa_catalogue_manage") or _deny("msa_catalogue_manage", "mcp:control", reason="NOT_ENABLED")


@mcp.tool(annotations=DESTRUCTIVE)
def msa_reconciliation_commit(
    proposal_id: str,
    idempotency_key: str,
    confirmation_reference: str | None = None,
) -> dict[str, Any]:
    """Future commit of an approved reconciliation proposal after all authority/canonicality/read-back gates pass."""
    denied = _gate("msa_reconciliation_commit", "mcp:write")
    if denied:
        return denied
    return _deny("msa_reconciliation_commit", "mcp:write", reason="SLICE_NOT_AUTHORIZED")


@mcp.tool(annotations=DESTRUCTIVE)
def msa_receipts_manage(
    action: str,
    receipt_id: str,
    idempotency_key: str | None = None,
    reason: str | None = None,
) -> dict[str, Any]:
    """Future typed receipt reverse/correct/archive lifecycle operation; backend allowlists actions."""
    denied = _gate("msa_receipts_manage", "mcp:write")
    if denied:
        return denied
    return _deny("msa_receipts_manage", "mcp:write", reason="SLICE_NOT_AUTHORIZED")


@mcp.tool(annotations=WRITE)
def msa_agents_update_identity(
    agent_id: str,
    display_name: str | None = None,
    call_name: str | None = None,
    description: str | None = None,
) -> dict[str, Any]:
    """Future Owner named-agent identity metadata update; stable agent_id never changes."""
    return _control_gate("msa_agents_update_identity") or _deny("msa_agents_update_identity", "mcp:control", reason="NOT_ENABLED")


@mcp.tool(annotations=READ)
def msa_external_clients_query(
    action: str,
    client_id: str | None = None,
    grant_id: str | None = None,
    agent_id: str | None = None,
    status: str | None = None,
    limit: int = 50,
    offset: int = 0,
) -> dict[str, Any]:
    """Future Owner external-client/OAuth-grant/binding metadata query without token or credential material."""
    return _not_implemented("msa_external_clients_query", "mcp:control")


@mcp.tool(annotations=DESTRUCTIVE)
def msa_external_clients_manage(
    action: str,
    client_id: str | None = None,
    grant_id: str | None = None,
    agent_id: str | None = None,
) -> dict[str, Any]:
    """Future Owner bind/unbind/disable/revoke external-client metadata control; no credential issuance/read-back."""
    return _control_gate("msa_external_clients_manage") or _deny("msa_external_clients_manage", "mcp:control", reason="NOT_ENABLED")


@mcp.tool(annotations=WRITE)
def msa_providers_lifecycle(action: str, provider_id: str) -> dict[str, Any]:
    """Future Owner provider enable/disable/retest lifecycle control without credential provisioning."""
    return _control_gate("msa_providers_lifecycle") or _deny("msa_providers_lifecycle", "mcp:control", reason="NOT_ENABLED")


@mcp.tool(annotations=READ)
def msa_reports_query(
    action: str,
    report_id: str | None = None,
    report_type: str | None = None,
    start_at: str | None = None,
    end_at: str | None = None,
    limit: int = 50,
    offset: int = 0,
) -> dict[str, Any]:
    """Future bounded report/mismatch/change-log/export-status query; backend allowlists report types/actions."""
    return _not_implemented("msa_reports_query", "mcp:read")


@mcp.tool(annotations=WRITE)
def msa_reports_manage(
    action: str,
    report_type: str,
    filters: dict[str, Any] | None = None,
    format: str | None = None,
) -> dict[str, Any]:
    """Future typed report generation/export request; backend allowlists report types, filters and formats."""
    return _control_gate("msa_reports_manage") or _deny("msa_reports_manage", "mcp:control", reason="NOT_ENABLED")


@mcp.tool(annotations=READ)
def msa_automations_query(
    action: str,
    automation_id: str | None = None,
    status: str | None = None,
    limit: int = 50,
    offset: int = 0,
) -> dict[str, Any]:
    """Future SYSTEM_AUTOMATION schedule/job/history query without secret material."""
    return _not_implemented("msa_automations_query", "mcp:control")


@mcp.tool(annotations=WRITE)
def msa_automations_manage(
    action: str,
    automation_id: str | None = None,
    agent_id: str | None = None,
    schedule: str | None = None,
    operation: str | None = None,
    parameters: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Future Owner scheduled automation create/update/enable/disable/run control; backend allowlists operations/parameters."""
    return _control_gate("msa_automations_manage") or _deny("msa_automations_manage", "mcp:control", reason="NOT_ENABLED")


# Publish the hardened long-lived manifest. The legacy credential action was already
# replaced by msa_inventory_read_usage in mcp_schema_v2_finalize before this module.
_NEW_TOOL_NAMES = {
    "msa_inventory_write_operation",
    "msa_catalogue_manage",
    "msa_reconciliation_commit",
    "msa_receipts_manage",
    "msa_agents_update_identity",
    "msa_external_clients_query",
    "msa_external_clients_manage",
    "msa_providers_lifecycle",
    "msa_reports_query",
    "msa_reports_manage",
    "msa_automations_query",
    "msa_automations_manage",
}
schema.SCHEMA_VERSION = "2026-08-23.v2.1"
schema.FINAL_TOOL_NAMES = tuple(sorted(set(schema.FINAL_TOOL_NAMES) | _NEW_TOOL_NAMES))
schema.FINAL_TOOL_COUNT = len(schema.FINAL_TOOL_NAMES)
schema.FINAL_TOOL_HASH = hashlib.sha256("\n".join(schema.FINAL_TOOL_NAMES).encode("utf-8")).hexdigest()
