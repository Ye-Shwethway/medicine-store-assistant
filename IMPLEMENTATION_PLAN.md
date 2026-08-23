# Medicine Store Assistant — Implementation Plan

Status: **F7.2A/B/C, F7.2D0 custom MCP connectivity + finalized 106-action schema v2.1 + replacement ChatGPT acceptance, F7.2D2 named Agent Management/session topology, F7.2D3 Provider Registry/saved-model catalog, F7.2D4A external MCP named-agent binding, F7.3A minimal MCP audit evidence, and F7.3B broad typed reads are verified foundations; F7.2D4 now continues as native internal-agent runtime + assignment/fallback + chat/tools/multi-agent execution; production inventory write authority remains unauthorized**

This file is the execution contract for current MSA implementation order and boundaries.

## 1. Global rules

- Google Sheets remains operationally authoritative until explicit F11 promotion.
- PostgreSQL being deployed does **not** make it canonical.
- F6B remains test-only and must never be silently promoted.
- All humans, AI agents, integrations, and system jobs use typed backend operations.
- Never expose arbitrary SQL, DB credentials, VPS shell/filesystem, Sheet credentials, plaintext provider keys, passwords/tokens/recovery secrets, or unrestricted HTTP proxying to AI/client runtimes.
- Deterministic backend code owns identity, authorization, capability/location policy, constraints, arithmetic, idempotency, transactions, derived state, committed read-back, and audit semantics.
- Significant mutation success requires committed-state read-back.
- Historical committed facts use correction/reversal semantics rather than silent destructive rewriting.
- Provider/model choice never grants authority.
- Prefer smallest runnable slices and avoid unnecessary infrastructure.
- Significant architecture/implementation/deploy/next-work changes update `ROADMAP.md`, `NEW_CHAT_BOOTSTRAP.md`, this file, and relevant canonical docs.
- Web delivery must follow `docs/design/WEB_ASSET_RELEASE_INTEGRITY.md`.

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
- F7.2D0 MCP schema finalization **v2.1 — 106 actions**
- F7.2D0 replacement ChatGPT MCP acceptance — **verified 2026-08-23**
- F7.2D2 named Agent Management + multi-agent session topology
- F7.2D3 Provider Registry + saved/tested model catalog
- F7.2D4A external MCP OAuth grant -> named-agent binding
- F7.3A minimal external-MCP actor audit evidence
- F7.3B broad typed row-level shadow reads with live `NEW_UNMAPPED` proof

F6B remains test-only: 1,646 rows; SAFE 1,417; REVIEW 222; CONFLICT 0; NEW_UNMAPPED 7; `migration_baseline_accepted=false`; `database_canonical=false`.

## 4. Canonical execution-path separation — REQUIRED

Canonical contract: `docs/architecture/F7_2D_EXECUTION_PATH_SEPARATION.md`.

MSA has one shared typed backend/authority core and multiple **peer** execution paths.

### 4.1 External MCP path

`ChatGPT model -> MCP action -> MCP authority intersection -> typed MSA backend operation -> result`

The external model performs the reasoning and directly invokes authorized implemented MCP actions. Internal agents are **not** a required hop.

Verified example:

`ChatGPT/SOL -> msa_shadow_read_rows -> shadow backend -> PostgreSQL shadow rows -> result`

Audit proof: `IANEO -> msa_shadow_read_rows -> SUCCESS` under `EXTERNAL_MCP` / `EXTERNAL_MCP_CLIENT` / `mcp:read`.

MCP gives typed operation access, not arbitrary SQL/DB access.

### 4.2 Native internal-agent path

`MSA Web chat / future Telegram / Flutter / automation -> native internal-agent runtime -> assigned provider/model -> internal typed-tool adapter -> typed MSA backend operation -> response`

`INTERNAL_MODEL` agents are first-class MSA runtimes. They must operate without ChatGPT and without the public MCP transport.

### 4.3 Shared backend rule

MCP actions, Web/API endpoints, and internal-agent tools reuse shared domain/service functions. They do not call one another merely to reach the same operation.

Forbidden drift:

- do not make internal agents depend on MCP for ordinary MSA data/tools;
- do not make direct MCP actions depend on internal agents;
- do not route normal Web/API operations through MCP;
- do not duplicate business/authority rules per adapter.

### 4.4 `msa_agent_invoke`

`msa_agent_invoke` is an **optional delegation/orchestration bridge**, not the central operation gateway.

Valid use:

`External MCP model -> msa_agent_invoke -> selected INTERNAL_MODEL agent -> independent analysis/result`

Use it for specialist delegation, independent review, compare/review/debate, or other deliberate internal-agent reasoning. Do not add this hop when the external MCP model already has direct authority for the requested MSA action.

## 5. Custom MCP foundation — VERIFIED

Primary external ChatGPT path:

`ChatGPT Developer Mode -> OAuth/PKCE -> custom MSA MCP -> typed backend`

Current external scopes: `mcp:connect`, `mcp:read`, `offline_access`; propose/write/control remain disabled.

Final schema:

- version `2026-08-23.v2.1`
- 106 actions
- tool-name SHA-256 `f12fcebfbf2b8cb0dd334e53faea25c9503eb3e99e94a71a378ba1133c3554d0`

Replacement-client acceptance is complete. PR #80 cleanup/deploy succeeded; production migration head is `0016_revoke_stale_chatgpt_oauth`.

Schema visibility is not authority. Prefer enabling existing published actions or extending stable backend-allowlisted selectors/backward-compatible inputs rather than adding new action names.

## 6. Agent Management + Provider Registry — VERIFIED

Agent identity:

- immutable `agent_id`;
- editable `display_name` / unique `call_name`;
- runtime mode/lifecycle/capability/location/authority/execution/confirmation policy;
- provider/model changes never change identity or authority.

Runtime modes include `EXTERNAL_MCP_CLIENT`, `INTERNAL_MODEL`, `EXTERNAL_ACTION_CLIENT`, `SYSTEM_AUTOMATION`.

Multi-agent topology already persists `GROUP`, `COMPARE`, `REVIEW`, `DEBATE`, ordered participants and role labels.

Provider Registry supports OpenAI, Gemini, OpenRouter, NanoGPT, generic `OPENAI_COMPATIBLE`. Provider credentials are write-only/server-side; tested Owner-saved healthy models are assignment candidates.

Provider test ping proves connectivity only. It is not an internal-agent workflow.

## 7. F7.2D4 — Native internal-agent runtime — NEXT

Purpose: create MSA-owned provider-backed agents that remain usable independently of ChatGPT while preserving the already-strong direct MCP path.

### Slice D4.1 — Assignment/fallback contract

Implement:

- stable assignment ID;
- `INTERNAL_MODEL` agent ID;
- primary enabled provider + Owner-saved healthy model;
- ordered optional fallback chain;
- capability expectations;
- timeout/max-output policy;
- optional usage/cost budget metadata;
- enabled/disabled state and provenance.

Rules:

- known incompatible capability fails closed;
- unknown capability remains explicit;
- no silent arbitrary substitution;
- fallback never expands authority;
- provider/model/fallback changes never alter `agent_id` or authority.

### Slice D4.2 — Native invocation service

Create a backend service callable directly by MSA-owned runtimes:

`caller -> resolve agent -> resolve assignment -> inject identity/policy -> provider call -> normalize -> audit -> response`

This service must have no dependency on ChatGPT or public MCP.

### Slice D4.3 — Canonical runtime identity

Every invocation injects current server-owned:

- `display_name`;
- `call_name`;
- stable `agent_id`;
- runtime identity;
- bounded policy/authority context.

Never rely on chat history for agent self-identity.

### Slice D4.4 — Conversation/message persistence

Add durable MSA-owned chat state:

- conversation ID;
- selected internal agent;
- participants/owner user;
- messages/roles/timestamps;
- model/provider provenance where relevant;
- conversation lifecycle/history.

### Slice D4.5 — Web AI Chat + agent selector

Build MSA-owned chat UI with:

- multiple selectable internal agents;
- new/resume conversation;
- conversation history;
- selected agent identity/state/provider/model display;
- native real provider-backed responses;
- responsive mobile-first UX.

This is the permanent survival surface. ChatGPT must not be required.

### Slice D4.6 — Internal typed-tool adapter

Internal agents call shared MSA domain/service functions through an internal typed-tool layer. They do **not** call the public MCP endpoint for ordinary tool/data access.

The internal tool semantics may mirror MCP/domain contracts where useful, but authority is evaluated under the internal agent's own context.

Initial proof should remain read-only and bounded.

### Slice D4.7 — Provider failover/provenance

Implement ordered fallback with explicit failure reasons. Record:

- selected provider/model;
- fallback used yes/no;
- fallback reason;
- latency;
- available token/usage/cost metadata.

Fail clearly when the approved chain is exhausted.

### Slice D4.8 — Multi-agent execution

Activate persisted `GROUP`, `COMPARE`, `REVIEW`, `DEBATE` topology for actual inference. Each participant retains separate identity, provider/model assignment, and authority. Never union privileges.

### Slice D4.9 — Optional MCP delegation adapter

Only after the native runtime exists, enable the already-published `msa_agent_invoke` / session MCP slots to call the same native runtime for explicit delegation.

This adapter is optional orchestration. Direct MCP actions remain direct.

### F7.2D4 acceptance

Pass only when:

1. multiple internal agents can be created and independently assigned models;
2. primary + ordered fallback assignment is durable;
3. native invocation works with no MCP dependency;
4. canonical identity is injected server-side;
5. Web AI Chat can select an internal agent and obtain a real provider-backed response;
6. conversation/message history persists;
7. at least one authorized internal typed MSA read succeeds through shared backend services, not public MCP;
8. failover is deterministic and provenance is recorded;
9. multi-agent execution can be enabled incrementally without privilege union;
10. optional MCP delegation can call a selected native agent without becoming the core runtime;
11. survival proof passes with ChatGPT completely out of the loop:

`MSA Web -> selected INTERNAL_MODEL agent -> provider/model -> authorized typed MSA read -> response + audit`

12. provider/model changes do not alter authority;
13. no production inventory write, workbook import, or DB canonical promotion occurs.

## 8. F7.3 — Full Actor-aware Audit / Operation Ledger — AFTER F7.2D4

Audit must preserve:

`human/grantor -> named agent -> runtime/client -> provider/model when relevant -> typed operation -> location/target -> result -> read-back/correlation -> timestamp`

UI needs date/month, human, agent, runtime/client, provider/model, operation/result, location/target, and operation/correlation filters plus preserved history/archive navigation.

## 9. Later sequence

1. F7.2D4 — native internal-agent runtime/assignment/chat/tools/multi-agent execution
2. F7.3 — actor-aware Audit / operation ledger
3. F7.4 — Inventory Locations / Store Policy / Preferences
4. F7.5 — Smart Calculator / receipts
5. F7.6 — deterministic Smart Analysis
6. F7.7 — richer internal AI Assistant/product workflows over the native runtime
7. F7.8 — Alerts & Notifications
8. F9 — controlled typed writes after authority/audit/location/idempotency prerequisites
9. F10 — real workflow + fresh migration + Sheet sync validation
10. F11 — explicit canonical promotion
11. Telegram/Flutter rollout over proven shared contracts

## Immediate execution boundary

Proceed with **F7.2D4 native internal-agent runtime**, beginning with assignment/fallback contract and native invocation service.

Do not enable production inventory writes, AI inventory writes, transfers, Smart Calculator deductions, Telegram/Flutter stock mutations, Sheet mirror conversion, or PostgreSQL canonical promotion in this slice.
