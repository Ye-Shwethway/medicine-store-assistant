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
13. `docs/checkpoints/F7_2D47A_NATIVE_TOOL_CALLING_PLAN_2026-08-23.md`
14. current runtime/deployment evidence, especially issue #26
15. `docs/design/UI_UX_PRO_MAX_INTEGRATION.md` and `docs/design/WEB_ASSET_RELEASE_INTEGRITY.md` for Web work

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
- Owner fallback configuration UI exists; live failover proof still pending;
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

During current D4.7A rollout, native store-tool execution is backend-restricted to Owner sessions plus selected-agent READ authority. Non-owner Chat is reasoning-only for store tools until explicit human/location tool authority is implemented.

## Current work — D4.7A native tool calling

Canonical checkpoint: `docs/checkpoints/F7_2D47A_NATIVE_TOOL_CALLING_PLAN_2026-08-23.md`.

The first safe native-read slice used deterministic current-message keyword routing. Keep that as a fast path, but add model-driven tool selection for tool-capable internal models.

Current native tool registry:

- `inventory_summary`
- `new_unmapped_rows`
- `review_reasons`

Current hybrid behavior:

1. Explicit supported request -> deterministic backend fast-path prefetch -> grounded model answer.
2. If no fast-path evidence exists and the assigned OpenAI-compatible model advertises tool support -> expose all currently authorized native read tools -> model may request tools -> backend allowlist/authority validation -> typed result -> model final answer.
3. Tool loop is bounded to four rounds.
4. Unsupported providers/models fall back to normal grounded reasoning; they must not claim tool execution.
5. Public MCP is not used.

Important: the public MCP schema has 106 actions, but those are not automatically internal-agent tools. Only native typed adapters that are implemented and backend-authorized are exposed to internal models.

## Next authorized order

1. Deploy D4.7A and manually verify explicit fast path plus contextual model-driven tool calling.
2. Run D4.7 live PRIMARY -> FALLBACK proof with two healthy saved models.
3. D4.8 Owner-only Multi-Agent execution.
4. Per-user Chat entitlement/allowed-agent UI plus human/location tool-authority intersection before staff tool rollout.
5. Expand native typed tools as product workflows require.
6. D4.9 optional MCP -> native-agent delegation.

## Manual acceptance prompt for D4.7A

Use an Owner AI Workspace conversation with a tool-capable internal model.

First ask an explicit request such as:

`Show the current NEW_UNMAPPED rows.`

Then in the same conversation ask a contextual follow-up without tool keywords, for example:

`Investigate this further and verify anything you need from MSA instead of asking me to supply the facts.`

Expected: the second turn may request one or more exposed native read tools itself; provenance records exposed/tool-called names; no public MCP is used; no write occurs.

## Survival proof

`MSA Web -> selected INTERNAL_MODEL agent -> assigned provider/model -> authorized typed MSA read -> response + provenance`

This proof is already live and must remain independent of public MCP.
