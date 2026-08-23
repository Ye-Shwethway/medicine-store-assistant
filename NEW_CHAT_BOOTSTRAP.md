# Medicine Store Assistant — New Chat Bootstrap

Use this file for project-development continuity and reconciliation in a fresh chat.

## Canonical repository

`https://github.com/Ye-Shwethway/medicine-store-assistant`

## Mandatory reconciliation order

Before changing code/config/schema/runtime in a fresh chat, read:

1. `AGENTS.md`
2. `NEW_CHAT_BOOTSTRAP.md`
3. `ROADMAP.md`
4. `IMPLEMENTATION_PLAN.md`
5. `docs/architecture/README.md`
6. `docs/architecture/F7_2D_AI_AGENT_MANAGEMENT.md`
7. `docs/architecture/F7_2D_EXECUTION_PATH_SEPARATION.md`
8. `docs/architecture/F7_2D4_AI_WORKSPACE_AND_ACCESS.md`
9. `docs/architecture/F7_2D2_AGENT_MANAGEMENT_AND_MULTI_AGENT_SESSIONS.md`
10. current F7.2D4 checkpoints and runtime/deployment evidence
11. `docs/design/UI_UX_PRO_MAX_INTEGRATION.md` and `docs/design/WEB_ASSET_RELEASE_INTEGRITY.md` for Web work

Treat newer verified repository/runtime evidence as authoritative over remembered chat context.

## Current canonicality boundary

- Google Sheet/source documents remain operationally authoritative.
- PostgreSQL is deployed but **not canonical**.
- F6B is test-only and not an accepted migration baseline.
- `database_canonical=false`.
- `migration_baseline_accepted=false`.
- No production inventory write, AI inventory write, transfer, Calculator deduction, Telegram/Flutter stock mutation, Sheet mirror conversion, or DB canonical promotion is authorized.

## Delivery policy

`branch -> PR -> main -> automatic VPS deploy for runtime changes -> issue #26 evidence -> continuity-doc refresh`

Runtime secrets remain on the VPS. Web asset delivery must follow the release-integrity contract.

## Durable execution-path invariant

MSA has peer execution paths over one shared typed backend/authority core.

External MCP:

`ChatGPT model -> MCP action -> MCP authority gate -> typed MSA backend operation -> result`

Native internal agent:

`MSA Web / future Telegram / Flutter / automation -> INTERNAL_MODEL runtime -> assigned provider/model -> internal typed-tool adapter -> typed MSA backend operation -> response`

Internal agents do not depend on public MCP for ordinary tools/data. Direct authorized MCP actions do not require an internal-agent hop. `msa_agent_invoke` is optional delegation/orchestration only.

## Current verified internal-agent truth

Verified:

- named AI Agent Management and policy persistence;
- Provider Registry + tested Owner-saved model catalog;
- PRIMARY + ordered FALLBACK assignment chain for `INTERNAL_MODEL` agents;
- non-internal model-assignment backend rejection and UI guard;
- MCP-independent native provider inference;
- server-owned identity/policy injection;
- provider/model/fallback/latency attempt provenance;
- Dashboard native-runtime test with `MCP used: no`;
- external MCP direct read/audit path remains independent and working.

The current native runtime is inference-only. Native typed MSA tools are not attached yet.

## AI Workspace architecture — APPROVED

Canonical design: `docs/architecture/F7_2D4_AI_WORKSPACE_AND_ACCESS.md`.

Keep two product planes separate:

### AI Agent Management — Owner-only control plane

Contains:

- agent create/edit/disable/revoke;
- authority/capability/runtime policy;
- provider/model/fallback management;
- reusable multi-agent session definitions;
- global non-owner AI Workspace enable/disable setting.

Owner-only means backend authorization plus UI restriction. Never rely on hidden controls alone.

### AI Workspace — work plane

Top-level product surface with:

- `Chat` — single internal agent; Owner + authorized users.
- `Multi-Agent` — actual GROUP/COMPARE/REVIEW/DEBATE execution; **Owner-only for the current phase**.

Normal users must not see Multi-Agent execution and direct backend calls must reject them.

## AI Workspace access policy

Owner is always allowed.

Global Owner setting:

`AI Workspace for non-owner users = ENABLED | DISABLED`

Global OFF is a hard kill switch for all non-owner Chat. A denied request must terminate before any provider call.

Per-user Chat entitlement in User Management:

- `INHERIT`
- `ALLOW`
- `BLOCK`

Effective behavior:

1. Owner -> allow.
2. Non-owner + global OFF -> deny.
3. Non-owner + global ON + BLOCK -> deny.
4. Non-owner + global ON + INHERIT/ALLOW -> eligible.

Per-user ALLOW does not override global OFF.

When typed tools arrive, effective authority must intersect system gate, authenticated human/user authority, agent authority/capabilities, location scope, operation class, and confirmation policy. Never union privileges.

## Next authorized implementation order

1. global AI Workspace non-owner setting + per-user Chat entitlement persistence;
2. reusable backend authorization helper with Owner bypass and denial-before-provider-call proof;
3. durable conversation/message persistence;
4. top-level AI Workspace shell + Chat tab + internal-agent selector;
5. native invocation hookup + persisted response provenance;
6. blocked/disabled UX;
7. internal typed-tool adapter over shared domain services, initially bounded read-only;
8. failover/provenance completion;
9. Owner-only Multi-Agent execution using persisted session presets;
10. optional MCP -> native-agent delegation.

## Survival acceptance

Full F7.2D4 still requires:

`MSA Web -> selected INTERNAL_MODEL agent -> assigned provider/model -> authorized typed MSA read -> response + audit`

with durable conversations, multiple agents, deterministic failover, no public-MCP dependency for ordinary native operation, and no privilege union.
