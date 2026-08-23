# Medicine Store Assistant — Project Roadmap

Status: **F0/F1/F2/F3/F4/F5/F5.1/F6A/F6C/F7.1/F7.2A/F7.2B/F7.2C/F7.2D0/F7.2D2/F7.2D3/F7.2D4A/F7.2D4B/F7.2D4C verified; F7.3A minimal MCP audit evidence and F7.3B broad typed reads verified; direct MCP and native internal agents are peer paths; F6B remains test-only; AI Workspace access + durable chat is next; PostgreSQL remains non-canonical**

The live Google workbook/source documents remain operationally authoritative. F6B is test-only and not an accepted migration baseline.

## Delivery policy

Canonical flow:

`branch -> PR -> main -> automatic VPS deploy for relevant runtime changes -> issue #26 runtime evidence -> continuity docs`

Runtime secrets remain only on the VPS. Web releases follow `docs/design/WEB_ASSET_RELEASE_INTEGRITY.md`.

## Product direction

MSA is a multi-client intelligent store-operations platform. Web, custom MCP, native internal AI, future Telegram/Flutter, scheduled jobs, and optional external clients reuse the same typed backend contracts and authority engine.

Preserve:

`source evidence -> reconcile current truth -> SAFE / REVIEW / CONFLICT / NEW_UNMAPPED -> authorized typed operation -> committed read-back -> audit`

No AI/client receives arbitrary SQL, DB credentials, VPS shell/filesystem, Sheet credentials, plaintext provider keys, passwords/tokens/recovery secrets, or unrestricted infrastructure access.

## Verified foundation

- F0/F1/Cloudflare/F2/F3/F4/F5/F5.1/F6A/F6C
- F7.1 read-only Dashboard
- F7.2A canonical multi-user identity/sessions
- F7.2B User Management/profile
- F7.2C Credential + Recovery Lifecycle
- F7.2D0 custom MCP/OAuth connectivity + schema `2026-08-23.v2.1` with **106 actions**
- replacement ChatGPT MCP acceptance with live row-level read/audit proof
- F7.2D2 named Agent Management + persisted multi-agent session topology
- F7.2D3 Provider Registry + tested Owner-saved model catalog
- F7.2D4A external MCP OAuth-grant -> named-agent binding
- F7.2D4B native internal-agent PRIMARY + ordered FALLBACK assignment chain
- F7.2D4C MCP-independent native internal-agent provider inference
- F7.3A minimal external-MCP actor audit evidence
- F7.3B broad typed row/detail reads

Native survival proof already passes for provider inference: an `INTERNAL_MODEL` agent responded through `NATIVE_MSA_BACKEND`, using NanoGPT/MiniMax M3, with `MCP used: no` and provider/model/latency provenance.

## F6B test-only snapshot

- batch `be13d127-5045-4284-a088-0a0b9b024d76`
- rows 1,646
- SAFE 1,417
- REVIEW 222
- CONFLICT 0
- NEW_UNMAPPED 7
- `migration_baseline_accepted=false`
- `database_canonical=false`

## Canonical execution-path separation — LOCKED

Canonical contract: `docs/architecture/F7_2D_EXECUTION_PATH_SEPARATION.md`.

External MCP path:

`ChatGPT/SOL -> MCP action -> MCP authority intersection -> typed MSA backend operation -> result`

Native internal-agent path:

`MSA Web / future Telegram / Flutter / automation -> native INTERNAL_MODEL runtime -> assigned provider/model -> internal typed-tool adapter -> typed MSA backend operation -> response`

These are peer paths over one backend/authority core. Direct authorized MCP actions do not require an internal-agent hop. Internal agents do not use public MCP as their normal tool gateway.

`msa_agent_invoke` remains an optional delegation/orchestration bridge only.

## F7.2D4 — Native internal-agent runtime

### Verified now

- D4A external MCP named-agent binding
- D4B primary + ordered fallback assignment contract
- D4C native provider-backed invocation independent of ChatGPT/MCP
- server-owned identity/policy injection
- provider/model/fallback/latency attempt provenance
- Dashboard native-runtime test surface

### Next: AI Workspace + access policy

Canonical contract: `docs/architecture/F7_2D4_AI_WORKSPACE_AND_ACCESS.md`.

Separate the surfaces:

- **AI Agent Management** = Owner-only configuration/control plane.
- **AI Workspace** = operational work plane.

AI Workspace contains:

1. **Chat** — single selected internal agent; Owner + authorized users.
2. **Multi-Agent** — actual `GROUP`, `COMPARE`, `REVIEW`, `DEBATE` execution; **Owner only** for the current phase.

AI Agent Management keeps provider/model assignment, agent policy, reusable multi-agent session definitions, and an Owner-only global non-owner AI Workspace enable/disable switch.

### Access-control invariants

Owner-only controls are protected in both UI and backend. UI hiding is never authorization.

Non-owner Chat authorization occurs before provider invocation:

`authenticated user -> global non-owner gate -> per-user entitlement -> agent eligibility -> native runtime`

Per-user entitlement values:

- `INHERIT`
- `ALLOW`
- `BLOCK`

Rules:

- Owner always allowed.
- Global OFF is a hard kill switch for all non-owner Chat.
- Global ON + user BLOCK -> deny.
- Global ON + INHERIT/ALLOW -> eligible.
- Denied requests make **zero provider API calls**.
- Multi-Agent execution remains Owner-only regardless of Chat entitlement.

When typed tools are attached later, effective authority must intersect system gate, human/user authority, agent authority/capabilities, location scope, operation class, and confirmation policy. Provider/model assignment never expands authority.

## Immediate implementation order

1. AI Workspace access-policy persistence and backend authorization.
2. Per-user Chat entitlement in User Management.
3. Durable conversation/message persistence.
4. Top-level AI Workspace shell with Chat tab and internal-agent selector.
5. Native runtime hookup and persisted messages.
6. Clear denial UX with no provider call when blocked.
7. Internal typed-tool adapter over shared MSA services, initially bounded read-only.
8. Provider failover/provenance completion.
9. Owner-only Multi-Agent execution using persisted session presets.
10. Optional MCP -> native-agent delegation.

## F7.2D4 survival acceptance

Final D4 pass still requires:

`MSA Web -> selected INTERNAL_MODEL agent -> assigned provider/model -> authorized typed MSA read -> response + audit`

with durable conversations, multiple selectable agents, deterministic failover, no public-MCP dependency for ordinary native operation, and no privilege union in multi-agent execution.

## Later sequence

1. F7.2D4 — AI Workspace/chat/tools/multi-agent execution
2. F7.3 — full actor-aware Audit / operation ledger
3. F7.4 — Inventory Locations / Store Policy / Preferences
4. F7.5 — Smart Calculator / receipts
5. F7.6 — deterministic Smart Analysis
6. F7.7 — richer internal AI Assistant workflows
7. F7.8 — Alerts & Notifications
8. F9 — controlled typed writes after authority/audit/location/idempotency prerequisites
9. F10 — real workflow + fresh migration + Sheet sync validation
10. F11 — explicit canonical DB promotion
11. Telegram/Flutter rollout over proven shared contracts

## Immediate boundary

Proceed with **AI Workspace access policy + durable single-agent Chat foundation**.

Do not enable production inventory writes, AI inventory writes, transfers, Smart Calculator deductions, Telegram/Flutter stock mutations, Sheet mirror conversion, or PostgreSQL canonical promotion during this work.

## Canonical architecture/docs

- `IMPLEMENTATION_PLAN.md`
- `NEW_CHAT_BOOTSTRAP.md`
- `docs/architecture/F7_2D_AI_AGENT_MANAGEMENT.md`
- `docs/architecture/F7_2D_EXECUTION_PATH_SEPARATION.md`
- `docs/architecture/F7_2D4_AI_WORKSPACE_AND_ACCESS.md`
- `docs/architecture/F7_2D2_AGENT_MANAGEMENT_AND_MULTI_AGENT_SESSIONS.md`
