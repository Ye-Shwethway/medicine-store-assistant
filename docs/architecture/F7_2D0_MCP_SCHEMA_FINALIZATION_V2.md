# F7.2D0 — MCP Schema Finalization v2

Status: **LOCKED IMPLEMENTATION CONTRACT — one long-lived ChatGPT MCP schema; capability activation remains policy-gated**

## Goal

Finalize the Medicine Store Assistant MCP action catalog before the Owner recreates the ChatGPT custom MCP app. The objective is to avoid repeated app deletion/recreation as later MSA slices become available.

Canonical rule:

`published tool schema != current execution authority`

A tool may be visible now and return `NOT_ENABLED`, `NOT_AUTHORIZED`, or `SLICE_NOT_AUTHORIZED` until its backend slice and authority gates are explicitly enabled.

## Explicit exclusions

The final MCP schema does **not** expose:

- provider API-key / credential provisioning or credential read-back;
- passwords, password reset secrets, session/token digests, OAuth secret material, or secret-manager contents;
- arbitrary SQL, table names, unrestricted database query/patch operations, DB credentials, shell, or filesystem access.

All other planned MSA product/control surfaces should have a stable typed MCP action now so later implementation normally changes availability/policy rather than the ChatGPT connector schema.

## Schema identity

- Schema family: `msa-mcp`
- Finalization version: `2026-08-23.v2`
- Expected published actions: **94**
- The server exposes `msa_system_schema_manifest` so clients can compare schema version, expected tool count, stable tool-name hash, build SHA, excluded capability classes, and domain coverage.
- CI compares the declared manifest against all `@mcp.tool` registrations in `mcp_server.py`, `mcp_shadow_reads.py`, and `mcp_schema_v2.py`.
- Extension tools must be registered before `mcp_http_app` is constructed.

## Authority classes

Current backend authority remains independent from schema visibility:

- `mcp:read` — authorized typed reads;
- `mcp:propose` — non-committing proposals/outbound AI inference where configured;
- `mcp:write` — typed operational mutations after explicit slice authorization;
- `mcp:control` — Owner/control-plane operations.

Production inventory writes and control-plane system gates remain closed until their authorized slices.

## Durable domains

### Identity and system

Existing:
- `msa_identity_whoami`
- `msa_system_status`
- `msa_system_capabilities`

Added:
- `msa_system_schema_manifest`

### Inventory and stock

Existing:
- `msa_inventory_read_summary`
- `msa_inventory_read_search`
- `msa_inventory_read_item`
- `msa_inventory_read_lots`
- `msa_inventory_read_location_balance`
- `msa_inventory_write_price`
- `msa_inventory_write_metadata`
- `msa_inventory_write_receive`
- `msa_inventory_write_adjustment`

Added:
- `msa_inventory_read_movements` — bounded stock-movement/history query by product/location/date/type.

### Shadow migration / source diagnostics

Permanent schema actions:
- `msa_shadow_read_rows`
- `msa_shadow_read_batch`
- `msa_shadow_read_review_reasons`

These cover row-level `SAFE`, `REVIEW`, `CONFLICT`, and `NEW_UNMAPPED` evidence separately from normalized inventory records.

### CMS catalogue

Existing:
- `msa_catalogue_read_current`
- `msa_catalogue_read_history`

Added:
- `msa_catalogue_query` — typed search/detail query without arbitrary DB access.

### Reconciliation

Existing:
- `msa_reconciliation_classify`
- `msa_reconciliation_prepare_batch`
- `msa_reconciliation_review_status`

Added:
- `msa_reconciliation_query` — list/get proposal/evidence/history through one typed read surface;
- `msa_reconciliation_review` — future Owner review/approve/reject/reopen action.

### Transfers

Existing:
- `msa_transfer_create`
- `msa_transfer_reverse`

Added:
- `msa_transfer_query` — list/get/history/status query.

### Locations, store policy, preferences

Added:
- `msa_locations_query`
- `msa_locations_manage`
- `msa_store_policy_get`
- `msa_store_policy_update`
- `msa_preferences_get`
- `msa_preferences_update`

These reserve F7.4 without requiring future connector changes.

### Calculator and receipts

Existing:
- `msa_calculator_calculate`
- `msa_calculator_save_receipt`
- `msa_calculator_dispense`

Added:
- `msa_receipts_query` — list/get/history/reversal-status query.

### Analysis

Existing:
- `msa_analysis_stock_health`
- `msa_analysis_expiry_risk`
- `msa_analysis_reorder_outlook`
- `msa_analysis_data_quality`

Added:
- `msa_analysis_query` — typed analysis selector plus bounded product/location/date filters for future analysis growth.

### Human users

Existing User Management actions remain.

Added:
- `msa_users_access_requests` — list/get pending/history without credentials;
- `msa_users_update_profile` — typed non-credential profile/admin metadata update.

No password or recovery-secret operations are published through MCP.

### AI agents and multi-agent sessions

Existing Agent Management actions remain.

Added:
- `msa_agent_invoke` — future named internal-agent inference through its saved provider/model assignment;
- `msa_agent_sessions_query` — list/get participants/runs/results;
- `msa_agent_sessions_manage` — create/update/close session topology and invoke configured session runs through policy-gated actions.

Agent identity remains stable and independent of provider/model choice.

### Providers and saved model catalog

Existing provider metadata/test/fetch/assignment actions remain. Provider credential provisioning remains Web/VPS-only and is explicitly absent from MCP.

Added:
- `msa_providers_catalog_query` — discovered models, saved models, assignments, health/capability metadata;
- `msa_providers_catalog_manage` — save/remove model, enable/disable saved model, unassign assignment, and related non-secret catalog control.

### Audit

Existing audit placeholders remain.

Added:
- `msa_audit_search` — future bounded query with date/month, human, agent, runtime/client, provider/model, operation, outcome, location/target, and correlation/operation filters.

Monthly archive/history is a view over preserved records rather than silent deletion.

### Alerts and notifications

Added:
- `msa_alerts_query`
- `msa_alerts_manage`
- `msa_notifications_query`
- `msa_notifications_manage`

Query tools cover alerts/rules/notification history. Manage tools reserve acknowledge/snooze/rule/preference operations under appropriate policy.

### Sync and migration lifecycle

Added:
- `msa_sync_query` — status/history/job diagnostics;
- `msa_sync_manage` — future preview/run/retry/cancel typed sync operations;
- `msa_migration_control` — future baseline accept/reject and explicit canonical promotion/demotion workflow.

Canonical promotion is visible at schema level but must remain destructive Owner control and policy-disabled until F11.

### Source evidence / ingestion

Added:
- `msa_sources_query` — list/get/status/preview diagnostics for typed source evidence;
- `msa_sources_manage` — future bounded ingest/reprocess/archive operations for approved source kinds.

No arbitrary filesystem path, shell, URL proxy, or credential forwarding is permitted.

### Integrations

Added:
- `msa_integrations_query`
- `msa_integrations_manage`

These reserve non-secret metadata/status/test/enable/disable management for future Telegram/Flutter/other integrations. Integration credentials are not returned or provisioned through MCP.

### Settings

Existing:
- `msa_settings_get`
- `msa_settings_update`

Only allowlisted typed settings are valid; no generic environment-variable or secret editor.

## Schema-change policy after v2

After the Owner creates the replacement ChatGPT MCP app from this contract:

1. Prefer implementing an existing `NOT_ENABLED` tool rather than adding a new action.
2. Prefer adding optional backward-compatible input fields rather than replacing actions.
3. Breaking semantic changes require an explicit versioned replacement and Owner approval.
4. New MCP actions are exceptional and require demonstrating that the v2 typed domain tools cannot express the requirement safely.
5. CI must reject manifest drift.
6. Runtime verification must compare `msa_system_schema_manifest` with the ChatGPT Actions list before the old MCP app is deleted.

## Immediate acceptance before MCP recreation

Pass only when:

1. all 94 declared tools register before HTTP transport construction;
2. manifest names/count/hash match source registrations exactly;
3. credentials/raw SQL are absent from the catalog;
4. row-level shadow reads remain present;
5. current read-only OAuth authority still denies propose/write/control;
6. existing `whoami`, system status, inventory summary, and audit evidence regressions pass;
7. production deploy reports exact success SHA;
8. the Owner can then recreate/scan the ChatGPT MCP app once and verify the manifest/action count.
