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
10. `docs/checkpoints/F7_2D4F_GROUNDED_NATIVE_READS_PLAN_2026-08-23.md`
11. `docs/checkpoints/F7_2D4G_CHAT_UX_LIFECYCLE_PLAN_2026-08-23.md`
12. current runtime/deployment evidence, especially issue #26
13. `docs/design/UI_UX_PRO_MAX_INTEGRATION.md` and `docs/design/WEB_ASSET_RELEASE_INTEGRITY.md` for Web work

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

Verified in production:

- named AI Agent Management and policy persistence;
- Provider Registry + tested Owner-saved model catalog;
- PRIMARY + ordered FALLBACK assignment chain for `INTERNAL_MODEL` agents;
- non-internal model-assignment backend rejection and UI guard;
- MCP-independent native provider inference;
- server-owned identity/policy injection;
- provider/model/fallback/latency attempt provenance;
- Dashboard native-runtime test with `MCP used: no`;
- backend-first AI Workspace access policy;
- durable top-level AI Workspace Chat with persisted per-user conversations;
- bounded native read tools for current inventory/shadow summary, NEW_UNMAPPED rows, and review reasons;
- manual native-read acceptance against real F6B test/shadow evidence;
- external MCP direct read/audit path remains independent and working;
- production inventory writes remain disabled.

## AI Workspace architecture — LOCKED

Canonical design: `docs/architecture/F7_2D4_AI_WORKSPACE_AND_ACCESS.md`.

Keep two product planes separate.

### AI Agent Management — Owner-only control plane

Contains agent lifecycle/policy, provider/model/fallback management, reusable multi-agent session definitions, and the global non-owner AI Workspace switch.

Owner-only means backend authorization plus UI restriction. Never rely on hidden controls alone.

### AI Workspace — work plane

- `Chat` — single internal agent; Owner + authorized users.
- `Multi-Agent` — actual GROUP/COMPARE/REVIEW/DEBATE execution; **Owner-only for the current phase** and not yet wired.

## AI Workspace access + tool authority

Owner is always allowed.

Global Owner setting:

`AI Workspace for non-owner users = ENABLED | DISABLED`

Global OFF is a hard kill switch for all non-owner Chat. A denied request terminates before any provider call.

Per-user Chat entitlement:

- `INHERIT`
- `ALLOW`
- `BLOCK`

Effective behavior:

1. Owner -> allow.
2. Non-owner + global OFF -> deny.
3. Non-owner + global ON + BLOCK -> deny.
4. Non-owner + global ON + INHERIT/ALLOW -> eligible.

Native tool authority is an intersection of system gate, authenticated human authority, selected-agent capabilities/ceiling, location scope, operation class, and confirmation policy. Never union privileges. Provider/model choice never expands authority.

## Current work — F7.2D4G

F7.2D4F is accepted. The native Chat can read real F6B test/shadow data without public MCP.

Current slice fixes mobile Chat UX/lifecycle defects observed during manual acceptance:

- long answers ending at the old workspace output budget;
- nondeterministic USER/ASSISTANT ordering for equal transaction timestamps;
- literal Markdown markers in replies;
- no explicit copy action / selectable-message contract;
- weak conversation cards with no first-message preview or human-friendly last-interaction time;
- no conversation deletion.

Implement backend-owned deletion, deterministic sequence, larger bounded response budgets, clean text presentation, Copy/selection, richer cards, and delete UX. Do not widen store authority.

## Next authorized implementation order

1. F7.2D4G Chat UX/lifecycle acceptance.
2. deterministic PRIMARY -> FALLBACK real-failure acceptance and provenance completion.
3. expand native typed reads over shared MSA services as product workflows require.
4. Owner-only Multi-Agent execution using persisted session presets.
5. optional MCP -> native-agent delegation.

## Survival acceptance

Core native survival proof is now present:

`MSA Web -> selected INTERNAL_MODEL agent -> assigned provider/model -> authorized typed MSA read -> response + provenance`

Remaining D4 hardening must preserve no-public-MCP dependency for ordinary native work and no privilege union.
