# F7.2D0 — MCP Full-Capability Schema

Status: **LOCKED DESIGN — build full tool surface once; activate authority progressively**

## 1. Goal

Build the Medicine Store Assistant remote MCP service once as a durable, full-capability protocol surface for ChatGPT and other MCP clients.

The MCP server is intentionally **read/write/admin-capable at the schema level**, while actual execution remains governed by MSA backend policy. Tool existence never implies permission.

This avoids repeatedly rebuilding/reconfiguring the remote connector as MSA evolves from read-only inspection to later controlled writes.

Canonical rule:

`MCP tool availability != execution authority`

Actual authority is computed by the backend from authenticated principal/client identity, capability grants, location scope, operation policy, canonicality/write-state gates, and any required confirmation/review boundary.

## 2. Current product boundary

The full schema may describe future write/control-plane tools now, but the current project boundary remains unchanged:

- Google Sheets remains operationally authoritative;
- PostgreSQL remains non-canonical;
- F6B remains test-only;
- production inventory mutation is not yet authorized;
- AI inventory writes are not yet authorized;
- transfer/dispense/adjustment writes remain disabled until their later slices;
- canonical DB promotion remains an explicit later decision.

Therefore the first deployed credential/policy may discover the complete catalog but only execute currently granted operations.

## 3. Protocol baseline

Implementation must target the current stable MCP specification at coding time and use a maintained Tier-1 SDK where practical.

Current researched direction as of 2026-08-23:

- remote deployment over HTTPS;
- stateless MCP protocol core in specification version 2026-07-28;
- Streamable HTTP-compatible remote service shape;
- JSON Schema 2020-12 tool schemas;
- tool metadata/annotations for read-only, destructive, idempotent, and open-world behavior;
- structured tool outputs where practical;
- authorization compatible with current MCP protected-resource discovery/OAuth requirements when OAuth is used.

Do not hard-code assumptions from an older SSE-only MCP implementation.

## 4. Deployment topology

Preferred shape:

`ChatGPT / MCP client`
`  -> HTTPS`
`msa-mcp remote service`
`  -> authenticated MSA principal/client context`
`  -> capability/location/operation-policy engine`
`  -> typed MSA backend service`
`  -> PostgreSQL / current authoritative integration boundary`

The MCP adapter is a protocol boundary, not a duplicate inventory engine.

Preferred production deployment:

- separate `msa-mcp` application/container;
- bind internally behind existing reverse-proxy/TLS infrastructure;
- stable public MCP endpoint, preferably dedicated hostname or stable path;
- no direct public PostgreSQL exposure;
- independently deployable/revocable MCP adapter;
- reusable typed backend service calls rather than copied business logic.

The official MCP Python SDK should be preferred if it satisfies required transport/auth/deployment behavior. Framework choice is implementation detail and must be verified against the then-current specification before coding.

## 5. Network and transport security

Required controls:

- HTTPS only publicly;
- explicit allowed public Host configuration;
- Origin validation consistent with the MCP transport/security specification;
- DNS-rebinding protection preserved rather than disabled globally;
- bounded request/response sizes;
- sensible connect/read/execution timeouts;
- reverse-proxy forwarding configured explicitly;
- health endpoint separated from MCP data/tool execution;
- no secrets in health output;
- structured logs with token/credential redaction;
- rate limiting/abuse protection at proxy and/or application layer;
- no generic outbound HTTP proxy tool.

## 6. Authentication architecture

The MCP transport does not grant authority by itself.

The long-lived design must support revocable authenticated MSA client/principal identity.

### 6.1 OAuth-capable production design

MCP authorization should be compatible with current protected-resource/OAuth discovery when the chosen ChatGPT connection flow uses OAuth.

The implementation must be able to support, as applicable:

- OAuth protected-resource metadata;
- authorization-server discovery;
- access-token audience/resource binding;
- scope validation;
- refresh-token behavior when the ChatGPT connection requires durable login;
- immediate server-side account/client revocation.

Do not forward unrelated upstream provider tokens as MSA bearer authority.

### 6.2 Scoped service credential compatibility

For development/bootstrap or clients that support a directly configured bearer/service credential, MSA may support a high-entropy revocable external-client credential.

Rules:

- plaintext shown/provisioned only at issuance;
- digest/verifier or secret reference only at rest;
- credential rotation without rebuilding tool schema;
- credential can be disabled/revoked immediately;
- no secret committed to Git or copied into audit payloads.

Static credentials must not become an unrestricted permanent super-token by default.

## 7. Principal and policy model

Every MCP invocation resolves to an MSA execution context containing at least:

- external client ID;
- optional AI `agent_id`;
- optional delegated human `user_id`;
- runtime/client type `EXTERNAL_MCP_CLIENT`;
- active/revoked state;
- granted capabilities/scopes;
- allowed locations;
- operation-policy reference;
- current write/canonicality gates.

For a non-human delegated external MCP call:

`effective_authority = registered_client_scope ∩ agent_capability_scope ∩ location_scope ∩ operation_policy ∩ system_write_gate`

When a human delegation context exists, human authority is additionally intersected.

Provider/model selection never expands authority.

## 8. Tool naming and namespaces

Use stable semantic tool names so the connector can survive implementation growth.

Recommended namespaces/conventions:

- `msa_identity_*`
- `msa_system_*`
- `msa_inventory_read_*`
- `msa_inventory_write_*`
- `msa_catalogue_*`
- `msa_reconciliation_*`
- `msa_transfer_*`
- `msa_calculator_*`
- `msa_analysis_*`
- `msa_users_*`
- `msa_agents_*`
- `msa_providers_*`
- `msa_audit_*`
- `msa_settings_*`

Tool names should be stable after publication. Prefer adding versioned input/output fields or new tool names over silently changing semantics.

## 9. MCP tool annotations

Every tool must declare accurate MCP annotations where supported:

- `readOnlyHint=true` for tools that cannot modify state;
- `destructiveHint=false` for additive/non-destructive writes;
- `destructiveHint=true` for destructive/high-impact mutation;
- `idempotentHint=true` only when retrying identical input is guaranteed not to create an additional effect;
- `openWorldHint=false` for closed MSA-internal operations unless the tool genuinely calls external/open-world systems.

Annotations are client hints only. Backend authorization and confirmation rules remain authoritative.

## 10. Full tool catalog

The schema should be broad enough that future controlled capabilities can be enabled without reconnecting/rebuilding the MCP app, but tool implementations may return a deterministic `NOT_AUTHORIZED` / `NOT_ENABLED` result until their project slice is approved.

### 10.1 Identity and system

- `msa_identity_whoami` — authenticated client/agent/delegation identity, granted capabilities and location scope, no secret material.
- `msa_system_status` — environment/version/canonicality/migration/F6B boundary and subsystem flags.
- `msa_system_capabilities` — capability states such as `AVAILABLE`, `POLICY_DISABLED`, `SLICE_NOT_AUTHORIZED`, `CLIENT_UNSUPPORTED`.

### 10.2 Inventory reads

- `msa_inventory_read_summary`
- `msa_inventory_read_search`
- `msa_inventory_read_item`
- `msa_inventory_read_lots`
- `msa_inventory_read_location_balance`

### 10.3 Catalogue and price reads

- `msa_catalogue_read_current`
- `msa_catalogue_read_history`

### 10.4 Reconciliation/proposal

- `msa_reconciliation_classify` — returns `SAFE`, `REVIEW`, `CONFLICT`, or `NEW_UNMAPPED` plus evidence references.
- `msa_reconciliation_prepare_batch` — proposal/draft only; no inventory commit.
- `msa_reconciliation_review_status`

### 10.5 Inventory writes — schema now, policy disabled until authorized

- `msa_inventory_write_price`
- `msa_inventory_write_metadata`
- `msa_inventory_write_receive`
- `msa_inventory_write_adjustment`

All are typed operations. None accepts arbitrary table names, SQL fragments, or unrestricted column patches.

### 10.6 Transfer and calculator

- `msa_transfer_create`
- `msa_transfer_reverse`
- `msa_calculator_calculate`
- `msa_calculator_save_receipt`
- `msa_calculator_dispense`

Write-capable variants remain disabled until their explicit slices authorize them.

### 10.7 Analysis

- `msa_analysis_stock_health`
- `msa_analysis_expiry_risk`
- `msa_analysis_reorder_outlook`
- `msa_analysis_data_quality`

### 10.8 Human User Management — Owner-only

- `msa_users_list`
- `msa_users_get`
- `msa_users_approve_request`
- `msa_users_reject_request`
- `msa_users_change_role`
- `msa_users_disable`
- `msa_users_reactivate`
- `msa_users_revoke_sessions`

These are control-plane operations and are never general AI capabilities.

### 10.9 AI Agent Management — Owner-only

- `msa_agents_list`
- `msa_agents_get`
- `msa_agents_create`
- `msa_agents_update_policy`
- `msa_agents_enable`
- `msa_agents_disable`
- `msa_agents_revoke`
- `msa_agents_rotate_credential`

An agent/client cannot alter its own authority grant unless a separately designed safe self-service operation explicitly allows it.

### 10.10 Provider Registry — Owner-only

- `msa_providers_list`
- `msa_providers_get`
- `msa_providers_create`
- `msa_providers_update`
- `msa_providers_disable`
- `msa_providers_test_connection`
- `msa_providers_fetch_models`
- `msa_providers_test_model`
- `msa_providers_assign_model`
- `msa_providers_set_fallbacks`

Built-in provider presets: OpenAI, Google Gemini, OpenRouter, NanoGPT.

Generic provider type: `OPENAI_COMPATIBLE`.

Provider keys remain runtime secrets; MCP tools never return plaintext provider secrets.

### 10.11 Audit

- `msa_audit_query`
- `msa_audit_get_operation`
- `msa_audit_get_actor_history`
- `msa_audit_get_reconciliation_history`

Audit reads are bounded and redact secrets/unrestricted prompt transcripts.

### 10.12 Settings — Owner-only

- `msa_settings_get`
- `msa_settings_update`

Only typed settings are permitted. No arbitrary environment-variable or secret editor is exposed.

## 11. Input schema rules

Every mutating tool uses explicit typed fields and, where applicable:

- stable target ID;
- location ID/scope;
- expected/current version or concurrency token;
- idempotency key;
- reason/note;
- reconciliation/proposal reference;
- explicit quantities/prices;
- deterministic preview/dry-run separate from commit mode.

Never accept raw SQL or unrestricted JSON patch against database records.

## 12. Output schema rules

Prefer structured outputs containing:

- `ok`;
- `status`;
- typed result payload;
- `operation_id` where applicable;
- policy/authorization outcome;
- canonicality/test-boundary metadata when relevant;
- committed read-back result for writes;
- machine-readable error code;
- safe human-readable message.

Never return secrets, password hashes, bearer tokens, provider API keys, raw DB DSNs, or sensitive auth material.

## 13. Write execution contract

A write-capable MCP tool may commit only if all gates pass:

1. authenticated active external client/principal;
2. capability allowed;
3. location allowed;
4. operation slice authorized;
5. canonicality/write gate permits this operation;
6. reconciliation/review policy satisfied;
7. deterministic validation succeeds;
8. idempotency/concurrency checks succeed;
9. atomic transaction commits;
10. actor-aware operation/audit record is created;
11. committed state is read back;
12. success is reported only after read-back verifies expected state.

If any gate fails, no partial mutation is permitted.

## 14. Confirmation and risk model

MSA backend policy must never depend solely on whether ChatGPT asks for confirmation. Client-side confirmation is an extra UX/safety layer, not authority.

Tool classes:

- `READ`
- `PROPOSE`
- `WRITE_LOW_RISK`
- `WRITE_REVIEW_REQUIRED`
- `CONTROL_PLANE`
- `DESTRUCTIVE_HIGH_RISK`

Some especially risky operations may remain Web-only even if conceptually represented in MCP design.

## 15. Idempotency and retries

All state-changing operations that may be retried must have deterministic idempotency semantics.

- duplicate same-key/same-payload returns the prior result;
- duplicate same-key/different-payload is rejected;
- `idempotentHint=true` is used only when fully true;
- retries must never double-create movements, receipts, transfers, user mutations, or provider assignments.

## 16. Tool discovery and client-plan differences

The remote server should publish the durable full catalog where practical.

ChatGPT feature availability may differ by plan/workspace/product rollout. Current OpenAI documentation states full modify/write MCP support is rolling out for Business/Enterprise/Edu, while some other plans may have read/fetch limitations.

Therefore:

- server architecture is not reduced to one current ChatGPT plan;
- server policy and client/product limitations are separate;
- write tools may exist but be unusable from a particular ChatGPT environment;
- this never justifies unauthenticated access or policy bypass.

## 17. Tool refresh/versioning

Some ChatGPT custom-app environments require explicit tool/action refresh and may not auto-enable new actions. Minimize connector churn by stabilizing the tool namespace before the first long-lived setup.

Rules:

- stable names/descriptions/schemas;
- backward-compatible additions where possible;
- high-risk tools default policy-disabled;
- semantic breaking changes use versioned replacement rather than silent changes.

## 18. Observability

Record enough to debug MCP without leaking secrets:

- request/correlation ID;
- external client/agent ID;
- tool name;
- policy decision;
- duration;
- outcome/error code;
- operation ID for mutations;
- no credential contents;
- no unrestricted prompt transcript by default.

## 19. Initial deployment acceptance

The first deployment uses the same full-capability server/schema, but only read capabilities are granted initially.

Acceptance:

1. remote HTTPS MCP endpoint reachable;
2. ChatGPT custom app can scan/discover the catalog;
3. authentication works;
4. `msa_identity_whoami` works;
5. `msa_system_status` works;
6. `msa_inventory_read_summary` returns real current MSA backend data;
7. a discoverable but ungranted write tool is rejected by backend policy;
8. invalid/revoked credential is rejected;
9. connector survives service restart/deploy;
10. no production inventory mutation occurs during proof.

This proves the permanent transport/schema foundation without prematurely authorizing writes.

## 20. Later activation sequence

After connectivity proof:

1. Agent/external-client principal management;
2. Provider Registry/model catalog;
3. internal model assignment;
4. F7.3 actor-aware operational audit;
5. location/store policy;
6. calculation/analysis reads;
7. controlled writes only after explicit authorization slices;
8. broader MCP write grants enabled by policy, not by rebuilding the connector.

## 21. Explicit non-goals

The MCP service is never:

- a raw SQL console;
- an SSH/VPS shell;
- a generic filesystem bridge;
- a generic arbitrary HTTP proxy;
- a secret manager that returns plaintext secrets;
- a way to bypass human RBAC or AI-agent capability rules;
- evidence that PostgreSQL has become canonical;
- automatic authorization for inventory mutation.
