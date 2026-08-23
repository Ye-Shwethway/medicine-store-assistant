# F7.2D0 — MCP Schema v2 Verified Checkpoint — 2026-08-23

Status: **VERIFIED LIVE — ready for one-time ChatGPT custom MCP app recreation/scan**

## Runtime evidence

- implementation PR: #76
- merge SHA: `bed14194661f0f2d6536d1d90b0e79d4e37e6da3`
- deployment run: `32637213532`
- issue #26: `status=success`
- deploy backend step: success
- public MCP OAuth boundary verification: success

## Final schema identity

- schema family: `msa-mcp`
- schema version: `2026-08-23.v2`
- runtime action count: **94**
- stable tool-name SHA-256: `3031969fec8e5e3ea52937b8c00ba3106b6da185e998d161cea855d5db616662`
- runtime manifest action: `msa_system_schema_manifest`

CI imports production `app.main`, inspects the actual MCP tool manager, and requires its names to match the final manifest exactly. Extension registration also must occur before `mcp_http_app` construction.

## Durable domain coverage

The v2 catalog has stable schema slots for:

- identity/system/schema manifest;
- inventory, usage, movement, lot and location-balance reads plus future typed writes;
- row-level shadow migration diagnostics including `NEW_UNMAPPED`;
- CMS catalogue and reconciliation;
- transfers;
- locations/store policy/preferences;
- calculator/receipts;
- deterministic analysis;
- human User Management without credential/password operations;
- named agents, internal agent invocation and multi-agent session execution;
- provider/model metadata/testing/saved catalog/assignments without credential provisioning/read-back;
- Audit query/search;
- alerts/notifications;
- sync/source ingestion/integrations;
- typed settings;
- migration baseline and explicit canonicality control.

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

## Replacement ChatGPT MCP acceptance

Do not delete the old ChatGPT custom app until the replacement app has been created against `https://inventory.drthorne.uk/mcp` and scanned successfully.

Pass the replacement only when:

1. OAuth connects successfully;
2. Actions includes `msa_system_schema_manifest`;
3. Actions includes `msa_shadow_read_rows`;
4. the scanned action count is **94**;
5. a read-only identity/system call succeeds;
6. `msa_system_schema_manifest` reports `2026-08-23.v2`, count 94, and the expected hash;
7. `NEW_UNMAPPED` row-level read succeeds;
8. Audit Recent activity records that external MCP read under the bound named agent;
9. propose/write/control remain denied for the current read-only agent.

Only after these checks should the old ChatGPT MCP app be removed.

## Post-v2 schema policy

Prefer implementing existing `NOT_ENABLED` actions or extending their optional inputs backward-compatibly. New action names are exceptional and require explicit proof that the v2 domain surfaces cannot safely express the requirement, because ChatGPT custom apps may hold a scanned action snapshot.
