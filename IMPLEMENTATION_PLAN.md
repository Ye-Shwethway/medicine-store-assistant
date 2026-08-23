# Medicine Store Assistant — Implementation Plan

Status: **F7.2A/B/C, F7.2D0 custom MCP connectivity + finalized 94-action schema v2, F7.2D2 named Agent Management/multi-agent sessions, F7.2D3 Provider Registry/saved-model catalog, F7.2D4A external MCP named-agent binding, F7.3A minimal MCP audit evidence, and F7.3B broad typed reads are verified foundations; F7.2D4 internal model assignment/fallback/runtime identity continues next; production inventory write authority remains unauthorized**

This file is the execution contract for current MSA implementation order and boundaries.

## 1. Global implementation rules

- Google Sheets remains operationally authoritative until explicit F11 promotion.
- PostgreSQL being deployed does **not** make it canonical.
- F6B remains test-only and must never be silently promoted.
- All humans, AI agents, integrations, and system jobs use typed backend operations.
- Never expose arbitrary SQL, database credentials, VPS shell/filesystem, Google Sheet credentials, plaintext provider keys, passwords/tokens/recovery secrets, or generic unrestricted HTTP proxying to AI/client runtimes.
- Deterministic backend code owns identity, authorization, capability/location policy, constraints, arithmetic, idempotency, transactions, derived state, and committed read-back.
- AI may interpret/reconcile/propose and later execute only explicitly authorized typed operations.
- Significant mutation success requires committed-state read-back.
- Historical committed facts use correction/reversal semantics rather than silent destructive rewriting.
- Secrets never enter Git, browser storage, ordinary logs, prompts, audit payloads, or docs evidence.
- Prefer smallest runnable slices; avoid unnecessary infrastructure.
- Normal continuation uses connected tools, PRs, and the self-hosted runner; do not require routine Termux/SSH/Bamboo/manual Actions work from the Owner.
- Significant implementation/deploy/next-work changes update `ROADMAP.md`, `NEW_CHAT_BOOTSTRAP.md`, this file, and relevant canonical docs.
- Dashboard UI delivery must follow `docs/design/WEB_ASSET_RELEASE_INTEGRITY.md`; changed CSS/JS requires a current HTML entrypoint asset version and browser-visible delivery verification, not only green backend/CI evidence.
- Agent Management production actions use the MSA button system: green `.primary` for constructive primary CTA, `.secondary` for neutral/lifecycle actions, `.danger-action` for destructive/irreversible actions. Browser-default action styling is not acceptable.

## 2. Existing `$msa` workflow parity

Preserve:

1. inspect source evidence;
2. reconcile against current authoritative truth;
3. classify `SAFE`, `REVIEW`, `CONFLICT`, `NEW_UNMAPPED`;
4. execute only Owner-authorized workflow classes;
5. surface material ambiguity;
6. commit through typed backend operation;
7. read affected state back;
8. record actor/operation provenance;
9. report success only after verification.

## 3. Verified foundation

Verified complete/foundational:

- F0/F1/Cloudflare/F2/F3/F4/F5/F5.1/F6A/F6C
- F7.1 read-only Dashboard
- F7.2A canonical human identity/sessions
- F7.2B User Management/profile
- F7.2C Credential + Recovery Lifecycle
- F7.2D0 custom MCP/OAuth connectivity
- F7.2D0 MCP schema finalization v2 — 94 runtime actions
- F7.2D2 named Agent Management + multi-agent session topology
- F7.2D3 Provider Registry + dynamic detailed discovery + tested saved-model catalog
- F7.2D4A external MCP OAuth grant -> named-agent binding
- F7.3A minimal external-MCP actor audit evidence
- F7.3B broad typed row-level shadow reads

F6B remains test-only: 1,646 rows; SAFE 1,417; REVIEW 222; CONFLICT 0; NEW_UNMAPPED 7; `migration_baseline_accepted=false`; `database_canonical=false`.

## 4. F7.2D0 — verified custom MCP foundation

Custom MCP is the verified primary ChatGPT access path:

`ChatGPT Developer Mode -> OAuth/PKCE -> custom MSA MCP -> typed backend`

Current granted external-client scopes are `mcp:connect`, `mcp:read`, and `offline_access`; propose/write/control remain disabled. Custom GPT Actions are optional/fallback only.

### 4.1 Final MCP schema v2 — VERIFIED

Canonical design: `docs/architecture/F7_2D0_MCP_SCHEMA_FINALIZATION_V2.md`

Runtime evidence:

- PR #76
- merge `bed14194661f0f2d6536d1d90b0e79d4e37e6da3`
- deploy run `32637213532`
- issue #26 `status=success`
- schema version `2026-08-23.v2`
- runtime action count `94`
- tool-name SHA-256 `3031969fec8e5e3ea52937b8c00ba3106b6da185e998d161cea855d5db616662`

The v2 catalog is intended to be the long-lived ChatGPT app contract. It already publishes stable typed surfaces for:

- identity/system/schema manifest;
- inventory/usage/movements/lots/location balances and future writes;
- row-level shadow migration diagnostics;
- catalogue/reconciliation/transfers;
- locations/store policy/preferences;
- calculator/receipts;
- deterministic analysis;
- human User Management without credential/password operations;
- named agents, internal-agent invocation, and multi-agent sessions;
- provider/model metadata, tests, saved-model catalog and assignments without credential provisioning/read-back;
- actor-aware Audit search;
- alerts/notifications;
- sync/source ingestion/integrations;
- settings;
- migration baseline and explicit canonicality control.

Schema visibility is not authority. Future tools may return `NOT_ENABLED`, `NOT_AUTHORIZED`, or `SLICE_NOT_AUTHORIZED` until their implementation and policy gates are approved.

Explicit MCP exclusions:

- provider/API-key/credential provisioning or secret read-back;
- password/token/recovery-secret access;
- legacy `msa_agents_rotate_credential` action;
- arbitrary SQL/table/column console;
- DB credentials;
- shell/filesystem access;
- generic unrestricted HTTP proxy.

Schema-change rule after the Owner recreates the ChatGPT MCP app:

1. implement an existing published action where possible;
2. add optional backward-compatible fields rather than new actions;
3. new action names are exceptional and require explicit justification/Owner approval;
4. CI must keep runtime tools identical to the v2 manifest;
5. `msa_system_schema_manifest` is the runtime source for version/count/hash diagnosis.

Before deleting/recreating the ChatGPT app, verify the server manifest reports version `2026-08-23.v2` and count 94. After creating the replacement app, verify its Actions list includes `msa_system_schema_manifest` and `msa_shadow_read_rows` and matches the expected action count before deleting the old app.

## 5. F7.2D2 — VERIFIED COMPLETE

Canonical design: `docs/architecture/F7_2D2_AGENT_MANAGEMENT_AND_MULTI_AGENT_SESSIONS.md`

Checkpoint: `docs/checkpoints/F7_2D2_AGENT_MANAGEMENT_2026-08-23.md`

Implemented Owner-only named agents with stable `agent_id`, editable name/call name, deterministic self-identity context, lifecycle/policy metadata, and persistent multi-agent session topology (`GROUP`, `COMPARE`, `REVIEW`, `DEBATE`).

## 6. F7.2D3 — VERIFIED COMPLETE

Provider Registry and catalog flow now separates provider discovery from Owner-approved usable models:

`Add provider -> provision credential -> Test connection -> Fetch models -> inspect/search detailed catalog -> Test model -> Save to provider catalog -> Enable`

Implemented:

- OpenAI, Gemini, OpenRouter, NanoGPT, generic `OPENAI_COMPATIBLE`;
- server-side write-only provider secret persistence with opaque DB `credential_ref`;
- normalized capabilities/pricing/context metadata and explicit unknowns;
- NanoGPT subscription-included vs paid-only membership where official endpoints provide it;
- tested Owner-saved model catalog that survives discovery refresh;
- internal agent provider/saved-model binding foundation;
- SSRF-safe custom provider URLs and bounded provider responses.

Provider credentials remain Web/VPS-only; the final MCP schema contains metadata/test/catalog controls but no credential provision/read-back action.

## 7. F7.2D4A — VERIFIED COMPLETE — external MCP named-agent binding

Canonical design: `docs/architecture/F7_2D4A_EXTERNAL_MCP_AGENT_BINDING.md`

Checkpoint: `docs/checkpoints/F7_2D4A_MCP_AGENT_BINDING_VERIFIED_2026-08-23.md`

Runtime evidence:

- PR #70
- merge `5f00458b55e85cfe4e3a78f5fb7b2f8517e159e2`
- deploy run `32631778542`
- issue #26 `status=success`
- migration head `0014_mcp_agent_bindings`

Implemented:

- Owner-only active MCP OAuth grant listing without secrets;
- explicit one-to-one active binding between an OAuth grant and named `EXTERNAL_MCP_CLIENT` agent;
- bind/rebind/unbind without ChatGPT reconnect/reauthorization;
- `msa_identity_whoami` named-agent resolution;
- effective authority = live OAuth grant capability ∩ live agent capability scope ∩ authority ceiling;
- disabled/revoked/non-external agents contribute no named-agent authority;
- unbound OAuth stays connected but reports `UNBOUND` and is not attributed to an invented agent;
- external MCP binding remains inbound-only; MSA cannot call back into ChatGPT through MCP;
- production inventory/control-plane system write gates remain closed;
- versioned/no-store MCP binding UI and robust danger style for Revoke;
- direct-child-only MutationObserver rule to prevent self-trigger UI freeze loops.

## 8. F7.3A/B — VERIFIED EARLY FOUNDATIONS

Full F7.3 remains later, but these foundations were intentionally front-loaded:

- append-only external-MCP audit events record actor/agent/client/action/outcome/correlation evidence;
- Dashboard Audit exposes minimal Recent activity;
- `mcp:read` means broad authorized typed operational reads rather than summary-only;
- `msa_shadow_read_rows` supports bounded row-level `SAFE`, `REVIEW`, `CONFLICT`, `NEW_UNMAPPED` inspection plus batch/sheet/search filters;
- detail-read events can be audited;
- raw SQL and secret-bearing auth/security tables remain excluded.

The replacement ChatGPT MCP app must scan the finalized v2 catalog before F7.3B is considered externally usable from ChatGPT.

## 9. Web UI workflow

Default Web path:

`UI/UX Pro Max -> design-system/medicine-store-assistant/MASTER.md + page override -> authenticated API contract -> direct code implementation -> responsive/accessibility/runtime verification`

Figma is optional and not a normal implementation prerequisite.

Browser delivery is part of runtime verification. For every changed Dashboard CSS/JS asset, inspect and update its HTML entrypoint cache identity, reject stale version markers in CI, keep manually versioned assets no-store/no-cache, wait for issue #26 deployment evidence, and verify that live browser behavior corresponds to the deployed source.

## 10. F7.2D4 — Internal model assignment/fallback/runtime identity — NEXT

Purpose: complete provider-backed execution for durable named internal agents without coupling identity or authority to model implementation.

### Required assignment/runtime data

At minimum:

- stable assignment identity;
- `agent_id`;
- primary enabled provider + Owner-saved healthy model reference;
- ordered optional fallbacks;
- required capability expectations;
- request timeout/output policy;
- optional usage/cost budget metadata;
- enabled/disabled assignment state and provenance.

### Rules

- only `INTERNAL_MODEL` agents receive provider/model assignments;
- provider must be enabled;
- model must be in the Owner-saved healthy provider catalog;
- known incompatible capability requirements fail closed;
- unknown capability remains explicit and requires Owner acknowledgement where needed;
- changing assignment never changes stable `agent_id`, call name, capability scope, location scope, authority ceiling, or system write gate;
- fallback order never expands authority;
- disabled/unhealthy provider handling is explicit, with no silent arbitrary substitution.

### Runtime identity

Every internal model call injects current canonical agent identity from MSA configuration, including at least `display_name`, `call_name`, and stable `agent_id`. Do not rely on chat history for an agent remembering its own name.

### First real inference proof

Use an Owner-configured enabled provider/model to prove a narrow non-inventory/read-only inference such as identity response/simple text. Capture provider/model/agent provenance for the later Audit ledger, but do not enable production inventory mutation.

The already-published `msa_agent_invoke` action is the durable external schema slot for later MCP-driven invocation. Until F7.2D4 enables it, it must return a deterministic policy/availability denial.

### Multi-agent readiness

After two or more internal agents have healthy assignments, existing `COMPARE`, `REVIEW`, and `DEBATE` session topology can be activated incrementally. Participants retain separate identities and authority; permissions never union. The finalized schema already publishes `msa_agent_sessions_query` and `msa_agent_sessions_manage` so no connector rebuild should be needed.

### F7.2D4 exit criteria

Pass when:

1. Owner can assign a primary enabled provider/saved model to an internal agent;
2. assignment survives rename without changing `agent_id`;
3. agent card shows actual provider/model;
4. invalid/disabled provider or unhealthy/missing saved model is rejected;
5. known capability mismatch is rejected and unknown capability is explicit;
6. ordered fallback configuration is durable;
7. canonical identity context is assembled server-side for invocation;
8. at least one configured provider/model passes a narrow real inference proof;
9. provider/model changes do not alter authority;
10. no production inventory write, workbook import, or canonical promotion occurs.

## 11. F7.3 — Actor-aware Audit / operation ledger — LATER, AFTER AGENT CONTROL PLANE

Audit is the user-facing operational log surface. It must eventually preserve the full provenance chain:

`human/grantor -> named agent -> runtime/transport/client -> provider/model when relevant -> typed operation -> location/target -> result -> read-back/correlation -> timestamp`

UI filters must include at least:

- date/time range and month;
- human/delegating user;
- named agent;
- runtime/transport/client;
- provider/model where relevant;
- operation type;
- outcome/result/reversal state;
- store/location/target;
- operation/correlation ID.

Monthly archive/history navigation should preserve records; it must not silently delete or rewrite audit history. `msa_audit_search` already reserves this full filter surface in the MCP v2 schema.

## Later sequence

1. **F7.2D4** — internal model assignment/fallback/runtime identity — next
2. **F7.3** — actor-aware Audit / operation ledger
3. **F7.4** — Inventory Locations / Store Policy / Preferences
4. **F7.5** — Smart Calculator / receipts, calculation-only first
5. **F7.6** — deterministic Smart Analysis
6. **F7.7** — internal read-only AI Assistant
7. **F7.8** — Alerts & Notifications
8. **F9** — controlled typed writes only after authority/audit/location/idempotency prerequisites
9. **F10** — real workflow + fresh migration + Sheet sync validation
10. **F11** — explicit canonical promotion

## Immediate execution boundary

Proceed next with **F7.2D4 internal model assignment/fallback/runtime identity** after the Owner recreates/scans the replacement ChatGPT MCP app against schema v2 and confirms the expected Actions list.

Do not enable production inventory writes, AI inventory writes, transfers, Smart Calculator deduction, Telegram/Flutter stock mutation, Sheet mirror conversion, or PostgreSQL canonical promotion during F7.2D4.