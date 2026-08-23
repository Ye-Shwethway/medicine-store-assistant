# Medicine Store Assistant — Project Roadmap

Status: **F0/F1/F2/F3/F4/F5/F5.1/F6A/F6C/F7.1/F7.2A/F7.2B/F7.2C/F7.2D0/F7.2D2/F7.2D3/F7.2D4A verified; F7.3A minimal MCP audit evidence and F7.3B broad typed reads verified; MCP schema v2.1 finalized at 106 actions and replacement ChatGPT acceptance verified; execution-path architecture realigned so direct MCP and native internal agents are peer paths; F6B remains test-only; F7.2D4 native internal-agent runtime is next; PostgreSQL remains non-canonical**

The live Google workbook/source documents remain operationally authoritative. F6B is a test-only staging exercise and not an accepted migration baseline. A fresh migration candidate is imported only after the redesigned operational workflow, location model, management surfaces, and shadow-validation path are ready and explicitly approved.

## Delivery policy

Canonical flow:

`branch -> PR -> main -> automatic VPS deploy for relevant runtime changes -> issue #26 runtime evidence -> continuity docs`

Normal continuation does not require routine manual VPS/Termux/SSH/tmux/Bamboo/manual Actions work from the Owner. Runtime secrets remain only on the VPS.

Web releases additionally follow `docs/design/WEB_ASSET_RELEASE_INTEGRITY.md`.

## Product direction

MSA is a multi-client intelligent store-operations platform. Web, custom MCP, native internal AI, future Telegram/Flutter, scheduled jobs, and optional external clients reuse the same typed backend contracts and authority engine.

Preserve the `$msa` workflow:

`source evidence -> reconcile current truth -> SAFE / REVIEW / CONFLICT / NEW_UNMAPPED -> Owner-authorized typed operation -> committed read-back -> audit`

No client or AI runtime receives arbitrary SQL, DB credentials, VPS shell/filesystem, Sheet credentials, or unrestricted infrastructure access.

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
- F7.2D0 MCP schema finalization v2.1 — **106 actions verified via PR #78 / deploy run 32637806906**
- F7.2D0 replacement ChatGPT MCP acceptance — **verified 2026-08-23 after PR #80 / deploy run 32639464966**
- F7.2D2 named AI Agent Management + multi-agent session topology — verified via PR #58
- F7.2D3 Provider Registry + saved/tested model catalog — verified via PR #60
- F7.2D4A external MCP OAuth-grant -> named-agent binding — verified via PR #70
- F7.3A minimal external-MCP actor audit evidence — verified via PR #72
- F7.3B broad typed shadow/detail reads — verified via PR #74 + PR #75; live replacement-client row read verified

## F6B test-only snapshot

- batch ID `be13d127-5045-4284-a088-0a0b9b024d76`
- rows **1,646**
- SAFE **1,417**
- REVIEW **222**
- CONFLICT **0**
- NEW_UNMAPPED **7**
- `migration_baseline_accepted=false`
- `database_canonical=false`

## F7.2D0 — Custom MCP — VERIFIED COMPLETE

Verified external path:

`ChatGPT model -> OAuth/PKCE -> custom MSA MCP -> typed backend operation -> result`

Current external scopes are `mcp:connect`, `mcp:read`, and `offline_access`; propose/write/control remain disabled.

Final schema:

- `2026-08-23.v2.1`
- **106 actions**
- hash `f12fcebfbf2b8cb0dd334e53faea25c9503eb3e99e94a71a378ba1133c3554d0`

Replacement acceptance is complete. The bound external agent resolves as `IANEO`; `msa_shadow_read_rows` successfully returned live `NEW_UNMAPPED` detail; Dashboard Audit recorded `IANEO -> msa_shadow_read_rows -> SUCCESS` under `EXTERNAL_MCP` / `EXTERNAL_MCP_CLIENT` / `mcp:read`.

MCP provides typed backend operations, not arbitrary SQL/DB access.

## Canonical execution-path separation — LOCKED

Canonical contract: `docs/architecture/F7_2D_EXECUTION_PATH_SEPARATION.md`.

MSA has one shared backend/authority core with multiple **peer paths**.

### External MCP path

`ChatGPT/SOL -> MCP action -> MCP authority intersection -> typed MSA backend operation -> result`

The external model is itself the reasoning engine. It directly performs authorized MCP actions. Internal agents are not a mandatory intermediary.

### Native internal-agent path

`MSA Web chat / future Telegram / Flutter / automation -> native INTERNAL_MODEL runtime -> assigned provider/model -> internal typed-tool adapter -> typed MSA backend operation -> response`

Native internal agents must remain operational independently of ChatGPT and independently of the public MCP transport.

### Direct Web/API and automation paths

Ordinary Web/API operations and system jobs also reach typed backend services directly under their own identities/policies.

### Shared-core rule

MCP actions, Web/API endpoints, and internal-agent tools reuse shared domain/service functions. Do not chain transports merely to reach the same business operation.

Forbidden architecture drift:

- no internal-agent dependency on public MCP for normal MSA data/tools;
- no forced internal-agent hop for direct authorized MCP actions;
- no ordinary Web/API routing through MCP;
- no duplicate independent business/authority engines per adapter.

## `msa_agent_invoke` role

`msa_agent_invoke` is an **optional delegation/orchestration bridge**.

Valid:

`External MCP model -> msa_agent_invoke -> selected INTERNAL_MODEL agent -> independent specialist analysis/result`

Use for independent review, specialist delegation, compare/review/debate, or deliberate cross-model reasoning.

It is not the central path for actions the external model can already execute directly.

## F7.2D2 — Named Agent Management — VERIFIED

Named agents have stable `agent_id`, editable names/call names, lifecycle, runtime mode, capability/location/authority/execution/confirmation policy, and server-owned deterministic identity context.

Persistent session topology already supports `GROUP`, `COMPARE`, `REVIEW`, `DEBATE`, ordered participants and role labels.

## F7.2D3 — Provider Registry — VERIFIED

Provider Registry supports OpenAI, Gemini, OpenRouter, NanoGPT, and generic `OPENAI_COMPATIBLE`.

Provider secrets are write-only/server-side; PostgreSQL stores opaque references only. Tested Owner-saved healthy models are the candidates for native internal-agent assignment.

Provider/model test ping proves connectivity only; it is not yet a native agent workflow.

## F7.2D4A — External MCP named-agent binding — VERIFIED

The Owner can bind/rebind/unbind a live OAuth grant to a named `EXTERNAL_MCP_CLIENT` agent without reconnecting ChatGPT. Effective external authority is live client/OAuth capability intersected with named-agent policy and system gates.

Current production migration head is `0016_revoke_stale_chatgpt_oauth` after stale duplicate replacement-client state was cleaned up while preserving the newest active grant.

## F7.3A/B — Early Audit + broad reads — VERIFIED FOUNDATIONS

- append-only external MCP actor/client/action/outcome/correlation evidence;
- Dashboard Audit Recent activity;
- broad typed `mcp:read` rather than summary-only access;
- row-level `SAFE`, `REVIEW`, `CONFLICT`, `NEW_UNMAPPED` diagnostics;
- no arbitrary SQL or secret-bearing auth/security surfaces.

Full F7.3 remains later.

## F7.2D4 — Native internal-agent runtime — NEXT

F7.2D4 now explicitly builds a **native MSA-owned provider-backed runtime**, not an MCP-dependent runtime.

Implementation order:

1. primary + ordered fallback assignment contract for `INTERNAL_MODEL` agents;
2. native backend invocation service independent of MCP;
3. canonical server-owned identity/policy injection;
4. real provider-backed single-agent inference;
5. durable conversation/message persistence;
6. MSA Web AI Chat with internal-agent selector;
7. internal typed-tool adapter over shared MSA domain services, not public MCP;
8. deterministic provider failover + provider/model/latency/usage provenance;
9. actual `GROUP`, `COMPARE`, `REVIEW`, `DEBATE` execution;
10. optional MCP -> native-agent delegation through existing `msa_agent_invoke` / session schema slots.

### Survival acceptance

F7.2D4 must prove operation with ChatGPT completely removed from the path:

`MSA Web -> selected INTERNAL_MODEL agent -> assigned provider/model -> authorized typed MSA read -> response + audit`

Pass requires multiple selectable internal agents, stable identity across model changes, durable conversations, native typed-tool execution, deterministic failover, and no MCP dependency for ordinary internal operation.

Production inventory writes remain closed.

## F7.3 — Full Actor-aware Audit / Operation Ledger

Audit eventually preserves:

`human/grantor -> named agent -> runtime/client -> provider/model when relevant -> typed operation -> location/target -> result -> read-back/correlation -> timestamp`

UI requires date/month, human, agent, runtime/client, provider/model, operation/result, location/target, operation/correlation filters, and preserved month/archive history.

## Later sequence

1. **F7.2D4** — native internal-agent runtime/assignment/chat/tools/multi-agent execution
2. **F7.3** — actor-aware Audit / operation ledger
3. **F7.4** — Inventory Locations / Store Policy / Preferences
4. **F7.5** — Smart Calculator / receipts
5. **F7.6** — deterministic Smart Analysis
6. **F7.7** — richer internal AI Assistant workflows over the native runtime
7. **F7.8** — Alerts & Notifications
8. **F9** — controlled typed writes after authority/audit/location/idempotency foundations
9. **F10** — real workflow + fresh migration + Sheet sync validation
10. **F11** — explicit canonical DB promotion
11. Telegram/Flutter rollout over proven shared contracts

## Immediate boundary

Proceed with **F7.2D4 native internal-agent runtime**, starting with assignment/fallback and the MCP-independent native invocation service.

Do not enable production inventory writes, AI inventory writes, transfers, Smart Calculator deductions, Telegram/Flutter stock mutations, Sheet mirror conversion, or PostgreSQL canonical promotion during F7.2D4.

## Canonical architecture/docs

- `IMPLEMENTATION_PLAN.md`
- `NEW_CHAT_BOOTSTRAP.md`
- `docs/architecture/F7_2D_AI_AGENT_MANAGEMENT.md`
- `docs/architecture/F7_2D_EXECUTION_PATH_SEPARATION.md`
- `docs/architecture/F7_2D0_MCP_FULL_CAPABILITY_SCHEMA.md`
- `docs/architecture/F7_2D0_MCP_SCHEMA_FINALIZATION_V2.md`
- `docs/architecture/F7_2D2_AGENT_MANAGEMENT_AND_MULTI_AGENT_SESSIONS.md`
- `docs/architecture/F7_2D4A_EXTERNAL_MCP_AGENT_BINDING.md`
- `docs/checkpoints/F7_2D0_MCP_SCHEMA_V2_VERIFIED_2026-08-23.md`
- `docs/checkpoints/F7_2D4A_MCP_AGENT_BINDING_VERIFIED_2026-08-23.md`
- `docs/architecture/F7_3_ACTOR_AUDIT_AND_OPERATION_LEDGER.md`
- `docs/design/WEB_ASSET_RELEASE_INTEGRITY.md`

## Continuity rule

After every significant architecture decision, implementation slice, deployment/migration result, or next-work change, update `ROADMAP.md`, `NEW_CHAT_BOOTSTRAP.md`, `IMPLEMENTATION_PLAN.md`, and relevant canonical docs.
