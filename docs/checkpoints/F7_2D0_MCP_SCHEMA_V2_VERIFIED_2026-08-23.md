# F7.2D0 — MCP Schema v2.1 + Replacement Acceptance Verified — 2026-08-23

Status: **VERIFIED LIVE — replacement ChatGPT MCP scan/manifest/read/audit acceptance complete**

## Schema runtime evidence

- implementation PR: #78
- schema merge SHA: `4e523645ab05063577b0e3fbc4c6ca5f870ce1dd`
- schema deployment run: `32637806906`
- issue #26: `status=success`
- schema family: `msa-mcp`
- schema version: `2026-08-23.v2.1`
- runtime action count: **106**
- stable tool-name SHA-256: `f12fcebfbf2b8cb0dd334e53faea25c9503eb3e99e94a71a378ba1133c3554d0`
- runtime manifest action: `msa_system_schema_manifest`

CI imports production `app.main`, inspects the actual MCP tool manager, and requires its names to match the final 106-action manifest exactly. Extension registration must occur before `mcp_http_app` construction.

## Durable domain coverage

The v2.1 catalog has long-lived typed schema slots for:

- identity/system/schema manifest;
- inventory, usage, movement, lot and location-balance reads plus future typed operational writes;
- row-level shadow migration diagnostics including `NEW_UNMAPPED`;
- CMS catalogue query/manage and reconciliation query/review/commit;
- transfers;
- locations/store policy/preferences;
- calculator/receipts and receipt lifecycle;
- deterministic analysis and reports;
- human User Management without credential/password operations;
- named agents, external-client metadata/lifecycle, internal agent invocation and multi-agent session execution;
- provider/model metadata/testing/saved catalog/assignments/lifecycle without credential provisioning/read-back;
- Audit query/search;
- alerts/notifications;
- scheduled system automations;
- sync/source ingestion/integrations;
- typed settings;
- migration baseline and explicit canonicality control.

Extensible domain `query`/`manage` tools use stable string action selectors plus deterministic backend allowlists to reduce unnecessary future ChatGPT connector rescans.

Visibility does not enable authority. Current external OAuth remains read-only and production write/control gates remain closed.

## Explicit exclusions

The final ChatGPT MCP action catalog intentionally excludes:

- provider API-key or credential provisioning/read-back;
- passwords, reset secrets, bearer/token secret material and secret-manager contents;
- legacy `msa_agents_rotate_credential`;
- arbitrary SQL/table/column query console;
- DB credentials;
- shell/filesystem access;
- generic unrestricted HTTP proxying.

## Replacement OAuth cleanup evidence

The replacement ChatGPT registration initially left stale duplicate OAuth state. PR #80 implemented the one-time Owner-authorized cleanup while preserving the newest ACTIVE replacement grant.

- cleanup PR: #80 — `Revoke stale duplicate ChatGPT OAuth grants`
- merge/deploy SHA: `a669890d4cf34c061f28296f64c306d95d4ee012`
- production deployment run: `32639464966`
- production deployment conclusion: `success`
- Alembic head: `0016_revoke_stale_chatgpt_oauth`

Cleanup semantics:

- keep the newest ACTIVE ChatGPT grant per user/client-name;
- revoke older duplicate grants;
- remove stale bindings for those grants;
- revoke their tokens;
- revoke retired OAuth client registrations that have no active grants;
- do not touch the newest replacement ChatGPT grant.

The cleanup migration is intentionally irreversible because restoring retired OAuth tokens/grants would recreate credentials the Owner explicitly retired.

## Workflow verification

PR #80 head validation runs all completed successfully:

- `Validate backend changes` — success;
- `Validate saved model catalog` — success;
- `Validate MCP audit proof` — success;
- `Validate MCP agent binding` — success.

The production deployment job also completed all deployment steps successfully, including:

- self-hosted runner preflight;
- backend deploy/readiness verification;
- public OAuth authorization/resource metadata verification;
- unauthenticated `/mcp` guard returning the expected HTTP 401;
- deployment status publication to issue #26.

The separate schema validation workflow remains locked to `2026-08-23.v2.1`, exactly 106 runtime actions, exact runtime-name/manifest equality, required permanent action coverage, pre-transport registration ordering, open string selectors for extensible action schemas, and credential/raw-SQL/shell/filesystem exclusions.

## Replacement ChatGPT MCP acceptance — VERIFIED

The replacement client has now passed the full one-time acceptance sequence.

Verified runtime result:

1. OAuth connection succeeds.
2. The replacement client scanned the finalized **106-action** catalog.
3. `msa_system_schema_manifest` is visible.
4. `msa_shadow_read_rows` is visible.
5. Manifest/identity checks report schema `2026-08-23.v2.1` and named agent `IANEO`.
6. Agent binding reports `BOUND`.
7. Read authority is enabled.
8. Write/control remain disabled.
9. A live row-level `NEW_UNMAPPED` read succeeds through `msa_shadow_read_rows`.
10. Dashboard Audit independently records that read as `IANEO -> msa_shadow_read_rows -> SUCCESS`, with `EXTERNAL_MCP`, `EXTERNAL_MCP_CLIENT`, `mcp:read`, timestamp 2026-08-23 19:02:38 local time.

The replacement-app acceptance prerequisite is closed. No further ChatGPT MCP connector recreation is required for the current v2.1 contract.

## Post-v2.1 schema policy

Prefer, in order:

1. implementing an existing published `NOT_ENABLED` action;
2. adding a backend-allowlisted action-string value to an extensible domain action;
3. adding backward-compatible optional inputs;
4. adding a new MCP action name only when the v2.1 domain surfaces cannot safely express the requirement and the Owner explicitly approves the schema change.

Future work must preserve:

- exact manifest/runtime consistency;
- no credential/password/token secret exposure;
- no arbitrary SQL/DB console;
- no shell/filesystem access;
- no generic unrestricted proxy;
- authority independent from schema visibility;
- production write/control gates closed until their owning slices are explicitly authorized.

## Next project boundary

Proceed with **F7.2D4 — internal model assignment/fallback/runtime identity**. The external replacement-client acceptance is no longer a blocker.