# Medicine Store Assistant — New Chat Bootstrap

Use this file for project-development continuity and reconciliation in a fresh chat.

## Canonical repository

`https://github.com/Ye-Shwethway/medicine-store-assistant`

## Mandatory reconciliation order

Before changing code/config/schema/runtime in a fresh chat, read in this order:

1. `AGENTS.md`
2. `NEW_CHAT_BOOTSTRAP.md`
3. `ROADMAP.md`
4. `IMPLEMENTATION_PLAN.md`
5. `docs/architecture/README.md`
6. `docs/architecture/F7_2D_AI_AGENT_MANAGEMENT.md`
7. `docs/architecture/F7_2D_EXECUTION_PATH_SEPARATION.md`
8. `docs/architecture/F7_2D0_MCP_FULL_CAPABILITY_SCHEMA.md`
9. `docs/architecture/F7_2D0_MCP_SCHEMA_FINALIZATION_V2.md`
10. `docs/architecture/F7_2D2_AGENT_MANAGEMENT_AND_MULTI_AGENT_SESSIONS.md`
11. `docs/architecture/F7_2D4A_EXTERNAL_MCP_AGENT_BINDING.md`
12. `docs/checkpoints/F7_2D0_MCP_CONNECTIVITY_VERIFIED_2026-08-23.md`
13. `docs/checkpoints/F7_2D0_MCP_SCHEMA_V2_VERIFIED_2026-08-23.md`
14. `docs/checkpoints/F7_2D2_AGENT_MANAGEMENT_2026-08-23.md`
15. `docs/checkpoints/F7_2D3_PROVIDER_REGISTRY_VERIFIED_2026-08-23.md`
16. `docs/checkpoints/F7_2D4A_MCP_AGENT_BINDING_VERIFIED_2026-08-23.md`
17. `docs/design/UI_UX_PRO_MAX_INTEGRATION.md` for Web work
18. `docs/design/WEB_ASSET_RELEASE_INTEGRITY.md` for Web release verification
19. task-relevant architecture/checkpoint docs and current runtime/deployment evidence

Treat newer verified repository/runtime evidence as authoritative over remembered chat context.

## Current authority/canonicality boundary

- Google Sheet/source documents remain operationally authoritative.
- PostgreSQL is deployed but **not canonical**.
- F6B staged dataset is **test-only** and not an accepted migration baseline.
- `database_canonical=false`.
- `migration_baseline_accepted=false`.
- No production inventory write, AI inventory write, transfer, Calculator deduction, Telegram/Flutter stock mutation, Sheet mirror conversion, or DB canonical promotion is authorized.

## Delivery policy

Canonical flow:

`branch -> PR -> main -> automatic VPS deploy for runtime changes -> issue #26 evidence -> continuity-doc refresh`

Do not require routine Termux, SSH, tmux, Bamboo/Bamboo Claw, or manual Actions work from the Owner. Runtime secrets remain on the VPS.

For Web changes, changed CSS/JS must have current entrypoint asset versions, manually versioned assets remain no-store/no-cache, and browser delivery must match the deployed SHA.

## Verified foundation

Verified complete/foundational:

- F0/F1/Cloudflare/F2/F3/F4/F5/F5.1/F6A/F6C
- F7.1 read-only Dashboard
- F7.2A canonical human identity/sessions
- F7.2B User Management/profile
- F7.2C Credential + Recovery Lifecycle
- F7.2D0 custom MCP/OAuth connectivity
- F7.2D0 MCP schema finalization **v2.1 — 106 actions**
- F7.2D0 replacement ChatGPT MCP scan/manifest/read/audit acceptance — **verified 2026-08-23**
- F7.2D2 named AI Agent Management + multi-agent session topology
- F7.2D3 Provider Registry + dynamic model catalog + tested saved-model catalog
- F7.2D4A external MCP OAuth grant -> named-agent binding
- F7.3A minimal external-MCP actor audit evidence
- F7.3B broad typed row-level shadow reads, including live replacement-client `NEW_UNMAPPED` proof

## F6B test-only snapshot

- batch `be13d127-5045-4284-a088-0a0b9b024d76`
- rows 1,646
- SAFE 1,417
- REVIEW 222
- CONFLICT 0
- NEW_UNMAPPED 7

Never silently promote this dataset into migration truth.

## Critical architecture invariant — DO NOT DRIFT

MSA has **peer execution paths** over one shared typed backend/authority core.

### External MCP path

`ChatGPT model -> MCP action -> MCP authority gate -> typed MSA backend operation -> result`

The external model is itself the reasoning engine. If an MCP action is implemented and the bound external agent/client has authority, it executes that action **directly**. It does not need an internal agent as an intermediary.

Production proof:

`ChatGPT/SOL -> msa_shadow_read_rows -> shadow backend -> PostgreSQL shadow data -> result`

Audit proof: `IANEO -> msa_shadow_read_rows -> SUCCESS` under `EXTERNAL_MCP` / `EXTERNAL_MCP_CLIENT` / `mcp:read`.

MCP provides typed backend operations, not arbitrary SQL/DB credentials.

### Native internal-agent path

`MSA Web chat / future Telegram / Flutter / automation -> native internal-agent runtime -> assigned provider/model -> internal typed-tool adapter -> typed MSA backend operation -> response`

`INTERNAL_MODEL` agents are first-class MSA runtimes. They must work independently of ChatGPT and independently of the MCP transport. ChatGPT being unavailable must not disable native MSA agents.

### Shared-core rule

MCP actions, Web/API endpoints, and internal-agent tools reuse shared backend domain/service functions wherever practical. Do not chain adapters just to reach the same operation.

In particular:

- internal agents do not call public MCP as their normal tool/data gateway;
- MCP does not call internal agents merely to perform actions the external model can already execute directly;
- Web/API does not route through MCP for ordinary backend operations.

Canonical contract: `docs/architecture/F7_2D_EXECUTION_PATH_SEPARATION.md`.

## `msa_agent_invoke` meaning

`msa_agent_invoke` is an **optional delegation/orchestration bridge**, not the central gateway for MSA operations.

Valid use:

`External MCP model -> msa_agent_invoke -> selected INTERNAL_MODEL agent -> independent specialist analysis/result`

Examples: independent review, specialist delegation, compare/review/debate, or explicitly asking a native internal agent to reason about a task.

Do not add an unnecessary double-agent hop when the external MCP model already has direct authority for the requested typed MSA action.

## Custom MCP — current durable truth

Verified path:

`ChatGPT Developer Mode -> OAuth/PKCE -> https://inventory.drthorne.uk/mcp -> typed MSA backend`

Current external-client scopes: `mcp:connect`, `mcp:read`, `offline_access`; propose/write/control remain disabled.

Schema identity:

- version `2026-08-23.v2.1`
- expected actions **106**
- tool-name SHA-256 `f12fcebfbf2b8cb0dd334e53faea25c9503eb3e99e94a71a378ba1133c3554d0`

Important exclusions:

- no provider/API-key credential provision/read-back through MCP;
- no password/token/recovery-secret action;
- no arbitrary SQL/DB console;
- no shell/filesystem;
- no unrestricted HTTP proxy.

Replacement-client acceptance is complete. PR #80 cleanup preserved the newest active replacement ChatGPT grant and revoked stale duplicate grants/tokens/bindings/client registrations. Production deploy run `32639464966` succeeded and current migration head is `0016_revoke_stale_chatgpt_oauth`.

No further connector recreation is required for the current v2.1 contract.

## Agent Management truth

Each named AI agent has immutable `agent_id`, editable `display_name`, unique `call_name`, runtime mode, lifecycle, capability/location/authority/execution/confirmation policy, and provenance.

Runtime modes include `EXTERNAL_MCP_CLIENT`, `INTERNAL_MODEL`, `EXTERNAL_ACTION_CLIENT`, `SYSTEM_AUTOMATION`.

Provider/model changes never change `agent_id` or authority.

Persistent multi-agent sessions support `GROUP`, `COMPARE`, `REVIEW`, `DEBATE`, ordered participants and role labels. Current topology exists; actual provider-backed multi-agent execution is later.

## Provider Registry truth

Supported provider types:

- OpenAI
- Google Gemini
- OpenRouter
- NanoGPT
- generic `OPENAI_COMPATIBLE`

Provider credentials are write-only and server-side; DB stores opaque credential references. Discovery/test ping proves connectivity only. Owner-saved healthy models are the assignment candidates for internal agents.

## Next authorized slice — F7.2D4 native internal-agent runtime

Do **not** turn MCP into the internal-agent runtime.

Implement in this order:

1. durable primary/fallback assignment contract for `INTERNAL_MODEL` agents;
2. native backend invocation service callable without MCP;
3. canonical identity/policy injection on every internal invocation;
4. real provider-backed single-agent inference;
5. durable conversation/message persistence;
6. MSA Web AI Chat with internal-agent selection;
7. internal typed-tool adapter over shared MSA domain services, not public MCP;
8. provider fallback/failover + provider/model/latency/usage provenance;
9. actual `GROUP` / `COMPARE` / `REVIEW` / `DEBATE` execution;
10. optional MCP -> native-agent delegation via existing `msa_agent_invoke` / session schema slots.

### F7.2D4 survival acceptance

A required acceptance proof must completely remove ChatGPT from the path:

`MSA Web -> selected INTERNAL_MODEL agent -> assigned provider/model -> authorized typed MSA read -> response + audit`

Pass requires multiple selectable internal agents, stable identities across model changes, durable conversations, native typed-tool execution, deterministic failover, and no dependence on MCP for ordinary internal operation.

Production inventory writes remain closed during this slice.

## Later sequence

1. F7.2D4 — native internal-agent runtime/assignment/chat/tools/multi-agent execution
2. F7.3 — full actor-aware Audit / operation ledger
3. F7.4 — Inventory Locations / Store Policy / Preferences
4. F7.5 — Smart Calculator / receipts
5. F7.6 — deterministic Smart Analysis
6. F7.7 — richer internal AI Assistant/product workflows over the native runtime
7. F7.8 — Alerts & Notifications
8. F9 — controlled typed writes after authority/audit/location/idempotency foundations
9. F10 — real workflow + fresh migration + Sheet sync validation
10. F11 — explicit canonical DB promotion
11. Telegram/Flutter rollout over the proven shared contracts
