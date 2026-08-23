# F7.2D0 — MCP Schema Finalization v2.1

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
- the legacy `msa_agents_rotate_credential` action;
- arbitrary SQL, table names, unrestricted database query/patch operations, DB credentials, shell, or filesystem access;
- a generic unrestricted HTTP proxy.

All other planned MSA product/control surfaces should have a stable typed MCP action now so later implementation normally changes availability/policy rather than the ChatGPT connector schema.

## Schema identity

- Schema family: `msa-mcp`
- Finalization version: `2026-08-23.v2.1`
- Expected published actions: **106**
- The server exposes `msa_system_schema_manifest` so clients can compare schema version, expected tool count, stable tool-name hash, build SHA, excluded capability classes, and domain coverage.
- CI imports production `app.main`, inspects the actual MCP runtime tool manager, and requires an exact match with the declared manifest.
- Extension tools must be registered before `mcp_http_app` is constructed.

## Long-lived input-schema rule

For domain-level `query` / `manage` actions, do not freeze future action vocabulary into a closed client-side enum when that would force a ChatGPT app rescan merely to add a safe backend action.

Use stable string action selectors plus deterministic backend allowlists. Visibility of an action string never grants authority, and unknown/unapproved action values must fail closed.

Stable closed fields may still use enums where the concept itself is genuinely fixed.

## Authority classes

Current backend authority remains independent from schema visibility:

- `mcp:read` — authorized typed reads;
- `mcp:propose` — non-committing proposals/outbound AI inference where configured;
- `mcp:write` — typed operational mutations after explicit slice authorization;
- `mcp:control` — Owner/control-plane operations.

Production inventory writes and control-plane system gates remain closed until their authorized slices.

## Durable domains

### Identity and system

- `msa_identity_whoami`
- `msa_system_status`
- `msa_system_capabilities`
- `msa_system_schema_manifest`

### Inventory and stock

Existing typed reads/writes remain, including summary/search/item/lots/location balance, receive/price/metadata/adjustment.

Additional permanent slots:

- `msa_inventory_read_movements`
- `msa_inventory_read_usage`
- `msa_inventory_write_operation` — future backend-allowlisted operational movement such as issue/return/dispose/stocktake with idempotency and policy gates.

### Shadow migration / source diagnostics

- `msa_shadow_read_rows`
- `msa_shadow_read_batch`
- `msa_shadow_read_review_reasons`

These cover row-level `SAFE`, `REVIEW`, `CONFLICT`, and `NEW_UNMAPPED` evidence separately from normalized inventory records.

### CMS catalogue

- `msa_catalogue_read_current`
- `msa_catalogue_read_history`
- `msa_catalogue_query`
- `msa_catalogue_manage`

Catalogue management is schema-visible but Owner/policy-gated and must validate allowlisted fields/actions.

### Reconciliation

- `msa_reconciliation_classify`
- `msa_reconciliation_prepare_batch`
- `msa_reconciliation_review_status`
- `msa_reconciliation_query`
- `msa_reconciliation_review`
- `msa_reconciliation_commit`

`msa_reconciliation_commit` remains disabled until write/canonicality/review/idempotency/read-back requirements are satisfied.

### Transfers

- `msa_transfer_create`
- `msa_transfer_reverse`
- `msa_transfer_query`

### Locations, store policy, preferences

- `msa_locations_query`
- `msa_locations_manage`
- `msa_store_policy_get`
- `msa_store_policy_update`
- `msa_preferences_get`
- `msa_preferences_update`

These reserve F7.4 without requiring future connector changes.

### Calculator and receipts

- `msa_calculator_calculate`
- `msa_calculator_save_receipt`
- `msa_calculator_dispense`
- `msa_receipts_query`
- `msa_receipts_manage`

Receipt management reserves reverse/correct/archive-style typed lifecycle operations; execution remains policy-gated.

### Analysis and reports

- `msa_analysis_stock_health`
- `msa_analysis_expiry_risk`
- `msa_analysis_reorder_outlook`
- `msa_analysis_data_quality`
- `msa_analysis_query`
- `msa_reports_query`
- `msa_reports_manage`

`msa_analysis_query` uses a backend-allowlisted string analysis type so later FIFO/usage/price/movement analyses can be enabled without changing the connector schema. Report tools reserve mismatch/change-log/export workflows.

### Human users

Existing User Management actions remain, plus:

- `msa_users_access_requests`
- `msa_users_update_profile`

No password or recovery-secret operations are published through MCP.

### AI agents, external clients, and multi-agent sessions

Existing Agent Management actions remain except credential rotation, which is explicitly removed from discovery.

Added/reserved:

- `msa_agents_update_identity`
- `msa_agent_invoke`
- `msa_agent_sessions_query`
- `msa_agent_sessions_manage`
- `msa_external_clients_query`
- `msa_external_clients_manage`

External-client management is metadata/binding/lifecycle only; no token or credential issuance/read-back. Agent identity remains stable and independent of provider/model choice.

### Providers and saved model catalog

Existing provider metadata/test/fetch/assignment actions remain. Provider credential provisioning remains Web/VPS-only and is explicitly absent from MCP.

Added/reserved:

- `msa_providers_catalog_query`
- `msa_providers_catalog_manage`
- `msa_providers_lifecycle`

These cover discovered/saved model metadata, assignments, provider enable/disable/retest lifecycle, and non-secret catalog control.

### Audit

Existing audit placeholders remain, plus:

- `msa_audit_search` — future bounded query with date/month, human, agent, runtime/client, provider/model, operation, outcome, location/target, and correlation/operation filters.

Monthly archive/history is a view over preserved records rather than silent deletion.

### Alerts and notifications

- `msa_alerts_query`
- `msa_alerts_manage`
- `msa_notifications_query`
- `msa_notifications_manage`

Backend allowlists action names/settings; notification or integration credentials are never returned or provisioned through these tools.

### Scheduled system automations

- `msa_automations_query`
- `msa_automations_manage`

These reserve the `SYSTEM_AUTOMATION` runtime for scheduled agent/operation jobs without exposing secret material. Backend policy controls permitted operations, schedules, agents and parameters.

### Sync and migration lifecycle

- `msa_sync_query`
- `msa_sync_manage`
- `msa_migration_control`

`msa_migration_control` reserves baseline accept/reject and explicit canonical promotion/demotion workflow. Canonical promotion is schema-visible but remains destructive Owner control and policy-disabled until F11.

### Source evidence / ingestion

- `msa_sources_query`
- `msa_sources_manage`

These reserve scan/OCR/source-evidence ingest/reprocess/archive workflows. No arbitrary filesystem path, shell, URL proxy, credential forwarding, or SQL is permitted.

### Integrations

- `msa_integrations_query`
- `msa_integrations_manage`

These reserve non-secret metadata/status/test/enable/disable management for future Telegram/Flutter/other integrations. Integration credentials are not returned or provisioned through MCP.

### Settings

- `msa_settings_get`
- `msa_settings_update`

Only allowlisted typed settings are valid; no generic environment-variable or secret editor.

## Schema-change policy after v2.1

After the Owner creates the replacement ChatGPT MCP app from this contract:

1. Prefer implementing an existing `NOT_ENABLED` tool rather than adding a new action.
2. Prefer backend-allowlisted new action-string values or optional backward-compatible input fields rather than new tool names.
3. Breaking semantic changes require an explicit versioned replacement and Owner approval.
4. New MCP actions are exceptional and require demonstrating that the v2.1 typed domain tools cannot express the requirement safely.
5. CI must reject manifest drift.
6. Runtime verification must compare `msa_system_schema_manifest` with the ChatGPT Actions list before the old MCP app is deleted.

## Immediate acceptance before MCP recreation

Pass only when:

1. all 106 declared tools register before HTTP transport construction;
2. manifest names/count/hash match runtime registrations exactly;
3. credential/password/token secret actions and raw SQL are absent from the catalog;
4. row-level shadow reads remain present;
5. operational issue/return-style write slot, catalogue/reconciliation/receipt management, external-client control, provider lifecycle, reports, and scheduled automation slots are present;
6. extensible query/manage actions expose open string selectors while backend allowlists remain mandatory;
7. current read-only OAuth authority still denies propose/write/control;
8. existing `whoami`, system status, inventory summary, audit, binding and broad-read regressions pass;
9. production deploy reports exact success SHA;
10. the Owner can then recreate/scan the ChatGPT MCP app once and verify the manifest/action count.
