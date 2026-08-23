# Medicine Store Assistant — New Chat Bootstrap

Use this file for project-development continuity and reconciliation in a fresh chat.

## Canonical repository

`https://github.com/Ye-Shwethway/medicine-store-assistant`

## Mandatory reconciliation order

Before changing code/config/schema/runtime, read:

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
12. `docs/checkpoints/F7_2D47_FALLBACK_MANAGEMENT_PLAN_2026-08-23.md`
13. current runtime/deployment evidence, especially issue #26
14. `docs/design/UI_UX_PRO_MAX_INTEGRATION.md` and `docs/design/WEB_ASSET_RELEASE_INTEGRITY.md` for Web work

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

## Durable execution-path invariant

External MCP:

`ChatGPT model -> MCP action -> MCP authority gate -> typed MSA backend operation -> result`

Native internal agent:

`MSA Web / future Telegram / Flutter / automation -> INTERNAL_MODEL runtime -> assigned provider/model -> internal typed-tool adapter -> typed MSA backend operation -> response`

They are peer paths. Internal agents do not depend on public MCP for ordinary work. Direct authorized MCP actions do not require an internal-agent hop. `msa_agent_invoke` is optional delegation/orchestration only.

## Verified internal-agent truth

Production/manual accepted:

- named AI Agent Management and persisted authority/policy;
- Provider Registry + tested Owner-saved models;
- backend PRIMARY + ordered FALLBACK chain for `INTERNAL_MODEL` agents;
- server rejection of model assignment for non-internal agents;
- MCP-independent native provider inference;
- provider/model/fallback/latency attempt provenance;
- backend-first AI Workspace access policy;
- durable top-level AI Workspace Chat;
- bounded grounded native reads over F6B test/shadow evidence;
- long response handling, deterministic USER -> ASSISTANT ordering, clean display, Copy/select, richer conversation cards, and owner-scoped conversation deletion;
- external MCP direct read/audit remains independent;
- production inventory writes remain disabled.

## AI Workspace architecture — LOCKED

### AI Agent Management — Owner-only control plane

Contains agent lifecycle/policy, provider/model/fallback assignments, reusable multi-agent session definitions, and global non-owner AI Workspace access setting.

Owner-only requires backend authorization plus UI restriction.

### AI Workspace — work plane

- `Chat` — one selected internal agent; Owner + authorized users.
- `Multi-Agent` — GROUP/COMPARE/REVIEW/DEBATE execution; Owner-only for this phase and not yet wired.

## Access + authority

Owner always has AI Workspace access. Global OFF hard-blocks all non-owner Chat before provider calls. Per-user entitlement foundation is `INHERIT | ALLOW | BLOCK`.

Native tool authority intersects system gate, authenticated human authority, selected-agent capability/ceiling, location scope, operation class, and confirmation policy. Never union privileges. Provider/model assignment never grants authority.

## Current work — D4.7 fallback management

Canonical checkpoint: `docs/checkpoints/F7_2D47_FALLBACK_MANAGEMENT_PLAN_2026-08-23.md`.

Backend support already exists for one PRIMARY + up to five ordered FALLBACK models. Current work exposes that chain in Owner-only AI Agent Management:

- primary provider/model selectors;
- add/remove/reorder fallback models;
- only healthy, saved, currently-discovered models from enabled providers;
- canonical `/model-assignments` chain endpoint;
- persisted order on reopen;
- fallback count on agent cards;
- non-internal assignment controls remain unavailable and server-rejected.

Live failover acceptance requires at least two healthy saved models. When available, prove PRIMARY failure -> ordered FALLBACK success with `fallback_used=true` and complete attempt provenance, without public MCP.

## Next authorized order

1. D4.7 fallback configuration UI deployment + manual persistence/order acceptance.
2. D4.7 live failover proof when a second healthy saved model exists.
3. D4.8 Owner-only Multi-Agent execution.
4. per-user Chat entitlement/allowed-agent UI before staff rollout.
5. native typed-tool expansion as product workflows require.
6. D4.9 optional MCP -> native-agent delegation.

## Survival proof

`MSA Web -> selected INTERNAL_MODEL agent -> assigned provider/model -> authorized typed MSA read -> response + provenance`

This proof is already live and must remain independent of public MCP.
