# Medicine Store Assistant — Project Roadmap

Status: **F0/F1/F2/F3/F4/F5/F5.1/F6A/F6C/F7.1/F7.2A/F7.2B/F7.2C/F7.2D0/F7.2D2/F7.2D3/F7.2D4A verified complete; F7.3A minimal MCP audit evidence and F7.3B broad typed reads verified; MCP schema v2.1 finalized at 106 actions and replacement ChatGPT acceptance is verified; F6B remains test-only; F7.2D4 internal model assignment/fallback/runtime identity continues next; PostgreSQL remains non-canonical**

The live Google workbook/source documents remain operationally authoritative. The current F6B snapshot is test-only and is not an accepted migration baseline. A fresh migration candidate is imported only after the redesigned operational workflow, location model, management surfaces, and shadow-validation path are ready and explicitly approved.

## Delivery policy

Canonical flow: `branch -> PR -> main -> automatic VPS deploy for relevant runtime changes -> issue #26 runtime evidence -> continuity docs`.

Normal continuation does not require manual VPS commands, Termux/SSH/tmux, Bamboo/Bamboo Claw, or a manual Actions deploy button. Prefer connected tools, repository automation, the repo-scoped self-hosted runner, and durable browser/admin mechanisms.

Runtime secrets remain only on the VPS. Normal backend deployment must not read/import the live workbook.

For Web releases, merge/CI/backend evidence is not sufficient by itself. Changed CSS/JS must have a matching current entrypoint asset version, browser assets remain no-store/no-cache while manual versioning is used, and the live browser delivery chain must be consistent with the deployed SHA. Canonical checklist: `docs/design/WEB_ASSET_RELEASE_INTEGRITY.md`.

## Product direction

MSA is a multi-client intelligent store-operations platform. Web, custom MCP, future Telegram/Flutter, internal AI, scheduled jobs, and optional external clients reuse the same typed backend contracts and authority engine.

Preserve the existing `$msa` workflow:

`source evidence -> reconcile current truth -> SAFE / REVIEW / CONFLICT / NEW_UNMAPPED -> Owner-authorized typed operation -> committed read-back -> audit`

No client or AI agent receives arbitrary SQL, raw database credentials, VPS shell, or unrestricted infrastructure access.

## Verified foundation

- F0 VPS inspection — verified 2026-08-22
- F1 runtime skeleton — verified 2026-08-22
- Cloudflare public HTTPS route — verified 2026-08-22
- F2 PostgreSQL foundation — verified 2026-08-22
- F3 authenticated read-only API — verified 2026-08-22
- F4 synthetic ledger foundation — verified 2026-08-22
- F5 CMS catalogue versioning — verified 2026-08-22
- F5.1 authenticated catalogue read API — verified 2026-08-22
- F6A synthetic shadow migration adapter — verified 2026-08-22
- F6B live-workbook snapshot — **test-only staging exercise**
- F6C authenticated shadow read API — verified 2026-08-22
- F7.1 read-only Web Dashboard — verified 2026-08-22
- F7.2A canonical multi-user identity/sessions — verified via PR #36
- F7.2B User Management/profile — verified via PR #38
- F7.2C Credential + Recovery Lifecycle — verified through PR #49
- F7.2D0 custom MCP full-schema/OAuth connectivity — verified 2026-08-23
- F7.2D0 MCP schema finalization v2.1 — **106-action runtime catalog verified via PR #78 / deploy run 32637806906**
- F7.2D0 replacement ChatGPT MCP acceptance — **verified 2026-08-23 after stale OAuth cleanup PR #80 / deploy run 32639464966**
- F7.2D2 named AI Agent Management + multi-agent session topology — verified 2026-08-23 via PR #58
- F7.2D3 Provider Registry + dynamic model catalog — verified 2026-08-23 via PR #60
- F7.2D4A external MCP OAuth-grant -> named-agent binding — verified 2026-08-23 via PR #70
- F7.3A minimal external-MCP actor audit evidence — verified 2026-08-23 via PR #72
- F7.3B broad typed shadow/detail reads — verified 2026-08-23 via PR #74 + discovery-order hotfix PR #75; live replacement-client row read verified 2026-08-23

## Current F6B test-only snapshot

- batch ID `be13d127-5045-4284-a088-0a0b9b024d76`
- rows **1,646**
- SAFE **1,417**
- REVIEW **222**
- CONFLICT **0**
- NEW_UNMAPPED **7**
- `migration_baseline_accepted=false`
- `database_canonical=false`

## F7.2D0 — Custom MCP access — **VERIFIED COMPLETE**

Primary ChatGPT external-access path is the custom remote MCP service.

Verified path:

`ChatGPT Developer Mode -> OAuth/PKCE -> custom MSA MCP -> typed backend -> authorized reads`

Current external-client scopes are `mcp:connect`, `mcp:read`, and `offline_access`; propose/write/control remain disabled. Custom GPT Actions are optional/fallback only.

The MCP transport publishes a durable full typed schema, while execution remains controlled by live backend policy. `full transport/schema != full current authority`.

### Final MCP schema v2.1 — **VERIFIED LIVE**

PR #78 merged as `4e523645ab05063577b0e3fbc4c6ca5f870ce1dd`; deploy run `32637806906` succeeded and issue #26 reported `status=success`.

The long-lived schema is finalized:

- schema version `2026-08-23.v2.1`;
- **106 runtime actions**;
- runtime tool-name hash `f12fcebfbf2b8cb0dd334e53faea25c9503eb3e99e94a71a378ba1133c3554d0`;
- `msa_system_schema_manifest` reports schema/version/count/hash/build/domain coverage;
- row-level shadow reads are permanent schema actions;
- current/future typed domains cover inventory/usage/movements, catalogue/reconciliation/transfers, locations/store policy/preferences, calculator/receipts, analysis/reports, users, agents/external clients/multi-agent sessions, providers, Audit, alerts/notifications, scheduled automations, sync/source/integration, settings and migration/canonicality control;
- extensible domain-level query/manage tools use stable string selectors with deterministic backend allowlists instead of client-frozen action enums;
- credential/password/token secret provisioning/read-back is excluded;
- legacy `msa_agents_rotate_credential` is removed from final discovery;
- arbitrary SQL/DB console, shell/filesystem and unrestricted proxy actions remain excluded;
- all extensions register before MCP HTTP transport construction;
- CI compares the actual production-style runtime tool manager against the 106-name manifest exactly.

Canonical contract: `docs/architecture/F7_2D0_MCP_SCHEMA_FINALIZATION_V2.md`.

After this point, prefer implementing existing `NOT_ENABLED` actions, adding backend-allowlisted action-string values, or adding backward-compatible optional fields. New MCP action names are exceptional because the replacement ChatGPT app may hold a scanned action snapshot.

### Replacement ChatGPT MCP acceptance — **VERIFIED 2026-08-23**

The one-time replacement-client acceptance is complete.

- PR #80 removed stale duplicate ChatGPT OAuth state while preserving the newest ACTIVE replacement grant.
- PR #80 merge/deploy SHA: `a669890d4cf34c061f28296f64c306d95d4ee012`.
- deployment run `32639464966` completed successfully.
- Alembic head advanced to `0016_revoke_stale_chatgpt_oauth`.
- PR #80 validation runs all passed: backend, saved-model catalog, MCP audit, and MCP agent-binding validations.
- Deploy verification passed backend deployment plus the public MCP OAuth metadata/unauthenticated boundary checks.
- Owner acceptance confirmed the replacement connection resolves to named agent `IANEO`, schema `2026-08-23.v2.1`, action count `106`, read enabled, and write/control disabled.
- A live `NEW_UNMAPPED` row-level read succeeded through `msa_shadow_read_rows`.
- Dashboard Audit independently recorded `IANEO -> msa_shadow_read_rows -> SUCCESS` under `EXTERNAL_MCP` / `EXTERNAL_MCP_CLIENT` / `mcp:read` at 2026-08-23 19:02:38 local time.

The old/replacement-app acceptance gate is therefore closed. No further connector recreation is required for the current v2.1 contract.

## F7.2D2 — Named AI Agent Management & multi-agent sessions — **VERIFIED COMPLETE**

PR #58 merged as `3b385a37b95c1ff79f76883381d8268fa6c49db2`; deploy run `32620386876` / job `97147568336` succeeded.

Verified capabilities:

- Owner-only named `AI_AGENT` principals;
- immutable stable `agent_id`;
- editable `display_name` and case-insensitive unique `call_name`;
- deterministic server-owned self-identity context;
- `ACTIVE` / `DISABLED` / `REVOKED` lifecycle;
- capability/location/authority/execution/confirmation metadata;
- reusable `GROUP`, `COMPARE`, `REVIEW`, `DEBATE` sessions;
- ordered participants and optional role labels;
- non-Owner 403/public anonymous 401;
- production system write gate remains closed.

Canonical checkpoint: `docs/checkpoints/F7_2D2_AGENT_MANAGEMENT_2026-08-23.md`.

## F7.2D3 — Provider Registry + model catalog — **VERIFIED COMPLETE**

PR #60 merged as `882c67b0134edb59156c17e948128de0ca8c3365`; deploy run `32621925138` / job `97151213410` succeeded. Alembic upgraded `0011_ai_agents -> 0012_providers`.

Verified capabilities:

- Owner-only provider registry for OpenAI, Google Gemini, OpenRouter, NanoGPT, and generic `OPENAI_COMPATIBLE`;
- dedicated server-side provider-secret volume; PostgreSQL stores only opaque `credential_ref` rather than plaintext provider keys;
- provider credentials are write-only from the Web control plane and never returned to the browser;
- server-side connection-test and dynamic model-fetch endpoints;
- normalized model catalog with bounded metadata and explicit unknown capability states;
- tested Owner-approved saved-model catalog separated from provider discovery;
- provider state/health remains distinct from model/agent state;
- enable gate requires configured credential, healthy connection test, and successful model fetch;
- custom provider URL validation blocks non-HTTPS/private/loopback/link-local/reserved destinations and redirects;
- provider responses are bounded/sanitized;
- public anonymous Provider Registry returns 401;
- deploy verifier made no inventory mutation/workbook import.

Agent Management UI also separates `External / MCP agents` from `Internal / provider-backed agents`, and agent cards expose `Agent name`, `Origin`, and `Model` metadata.

Canonical checkpoint: `docs/checkpoints/F7_2D3_PROVIDER_REGISTRY_VERIFIED_2026-08-23.md`.

## F7.2D4A — External MCP named-agent binding — **VERIFIED COMPLETE**

PR #70 merged as `5f00458b55e85cfe4e3a78f5fb7b2f8517e159e2`; deploy run `32631778542` succeeded and issue #26 reported `status=success`. Binding schema was introduced at `0014_mcp_agent_bindings`; current production Alembic head is `0016_revoke_stale_chatgpt_oauth` after the one-time duplicate-grant cleanup.

Verified direction:

`ChatGPT/custom MCP client -> OAuth grant -> named EXTERNAL_MCP_CLIENT agent -> live authority intersection -> typed MSA operation`

Key behavior:

- Owner can bind/rebind/unbind a live MCP OAuth grant to a named external MCP agent without reconnecting ChatGPT;
- `msa_identity_whoami` resolves the stable named-agent identity when bound and returns `UNBOUND` rather than inventing identity otherwise;
- effective MCP authority intersects live OAuth grant capability with live agent capability scope and authority ceiling;
- disabled/revoked/non-external agents contribute no named-agent capability authority;
- binding does not make MSA call back into ChatGPT; outbound/internal AI remains provider-backed;
- production inventory write and control-plane system gates remain closed;
- Agent Management includes explicit MCP connection binding UI;
- destructive `Revoke` uses the MSA danger style rather than browser-default styling;
- MCP binding UI uses direct-child MutationObserver semantics only to prevent self-trigger freeze loops;
- replacement-app cleanup keeps the newest ACTIVE ChatGPT grant per user/client-name and revokes older duplicate grants/tokens/bindings and retired client registrations with no active grants.

Canonical checkpoint: `docs/checkpoints/F7_2D4A_MCP_AGENT_BINDING_VERIFIED_2026-08-23.md`.

## F7.3A/B — early Audit proof + broad typed reads — **VERIFIED FOUNDATIONS**

Full F7.3 remains later, but two foundations were intentionally front-loaded to verify real external-agent activity and read coverage:

- append-only `operation_audit_events` captures external MCP actor/client/action/outcome/correlation evidence;
- Dashboard Audit has a minimal Recent activity view;
- `mcp:read` means authorized typed operational reads rather than summary-only access;
- row-level shadow diagnostics support `SAFE`, `REVIEW`, `CONFLICT`, `NEW_UNMAPPED`, batch/sheet/query/limit/offset filters;
- raw SQL and secret-bearing auth/security tables remain excluded;
- live replacement-client acceptance now proves `msa_shadow_read_rows` can read `NEW_UNMAPPED` detail and persist a corresponding `SUCCESS` audit event for named agent IANEO.

## Web implementation workflow

Default Web workflow:

`UI/UX Pro Max -> MSA repo design system -> authenticated API contract -> direct code implementation -> responsive/accessibility/runtime verification`

Figma is optional and only used when explicitly requested.

Every Web release must additionally satisfy `docs/design/WEB_ASSET_RELEASE_INTEGRITY.md`: changed CSS/JS must use a current entrypoint cache identity, stale asset markers must not survive CI, and live browser delivery must match the deployed SHA before the UI is called verified.

## F7.2D4 — Internal model assignment, fallback & runtime identity — **NEXT**

Next continuation:

- assign a primary provider/saved-tested model to a named internal agent;
- optional ordered fallback chain;
- capability compatibility checks;
- timeout/output policy and optional usage/cost metadata;
- server-side injection of canonical agent identity (`display_name` + stable `agent_id`) on every invocation;
- preserve authority independently from provider/model assignment;
- prove a narrow real provider-backed inference using Owner-configured credentials;
- prepare multi-agent compare/review/debate execution across same or different providers.

Changing provider/model never changes `agent_id` or authority. External MCP identities remain separate from internal provider-backed agents.

## F7.3 — Actor-aware Audit & Operation Ledger

Operational/database Audit remains separate from User Management and Agent Management. Actor classes: `HUMAN`, `AI_AGENT`, `SYSTEM`, `INTEGRATION`.

Meaningful operations retain human/delegation, named agent, client/transport, provider/model where relevant, location/policy/outcome/read-back provenance.

The Audit UI must support filtering by date/time or month, human, agent, runtime/client, provider/model where relevant, operation, result, location/target, and operation ID. Historical month/archive navigation preserves records rather than silently deleting or rewriting them.

## Later sequence

1. **F7.2D4** — internal model assignment/fallback/runtime identity — next
2. **F7.3** — actor-aware Audit / operation ledger
3. **F7.4** — Inventory Locations / Store Policy / Preferences
4. **F7.5** — Smart Calculator / receipts, calculation-only first
5. **F7.6** — deterministic Smart Analysis
6. **F7.7** — internal read-only AI Assistant
7. **F7.8** — Alerts & Notifications
8. optional standalone Custom GPT Action path if a concrete need appears
9. **F9** — controlled typed writes only after required authority/audit/location/idempotency foundations
10. **F10** — real workflow + fresh migration + Sheet sync validation
11. **F11** — explicit canonical DB promotion
12. Telegram/Flutter rollout over proven contracts

## Immediate boundary

The next authorized implementation slice is **F7.2D4 internal model assignment/fallback/runtime identity**. The replacement ChatGPT MCP acceptance prerequisite is already satisfied.

Do not enable production inventory writes, AI inventory writes, transfers, Smart Calculator deductions, Telegram/Flutter stock mutations, Sheet mirror conversion, or PostgreSQL canonical promotion as part of F7.2D4.

## Canonical architecture/docs

- `IMPLEMENTATION_PLAN.md`
- `NEW_CHAT_BOOTSTRAP.md`
- `docs/architecture/README.md`
- `docs/architecture/F7_2D_AI_AGENT_MANAGEMENT.md`
- `docs/architecture/F7_2D0_MCP_FULL_CAPABILITY_SCHEMA.md`
- `docs/architecture/F7_2D0_MCP_SCHEMA_FINALIZATION_V2.md`
- `docs/architecture/F7_2D2_AGENT_MANAGEMENT_AND_MULTI_AGENT_SESSIONS.md`
- `docs/architecture/F7_2D4A_EXTERNAL_MCP_AGENT_BINDING.md`
- `docs/checkpoints/F7_2D0_MCP_CONNECTIVITY_VERIFIED_2026-08-23.md`
- `docs/checkpoints/F7_2D0_MCP_SCHEMA_V2_VERIFIED_2026-08-23.md`
- `docs/checkpoints/F7_2D2_AGENT_MANAGEMENT_2026-08-23.md`
- `docs/checkpoints/F7_2D3_PROVIDER_REGISTRY_VERIFIED_2026-08-23.md`
- `docs/checkpoints/F7_2D4A_MCP_AGENT_BINDING_VERIFIED_2026-08-23.md`
- `docs/architecture/F7_3_ACTOR_AUDIT_AND_OPERATION_LEDGER.md`
- `design-system/medicine-store-assistant/MASTER.md`
- `design-system/medicine-store-assistant/pages/dashboard.md`
- `docs/design/UI_UX_PRO_MAX_INTEGRATION.md`
- `docs/design/WEB_ASSET_RELEASE_INTEGRITY.md`

## Continuity rule

After every significant architecture decision, implementation slice, deployment/migration result, or next-work change, update `ROADMAP.md`, `NEW_CHAT_BOOTSTRAP.md`, `IMPLEMENTATION_PLAN.md`, and relevant canonical docs.