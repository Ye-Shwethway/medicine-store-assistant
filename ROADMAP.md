# Medicine Store Assistant — Project Roadmap

Status: **F0/F1/F2/F3/F4/F5/F5.1/F6A/F6C/F7.1/F7.2A/F7.2B/F7.2C/F7.2D0/F7.2D2/F7.2D3/F7.2D4A/F7.2D4B/F7.2D4C/F7.2D4E/F7.2D4F verified; F7.3A minimal MCP audit evidence and F7.3B broad typed reads verified; direct MCP and native internal agents are peer paths; F6B remains test-only; current work is AI Workspace Chat UX/lifecycle; PostgreSQL remains non-canonical**

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
- F7.2D4E durable top-level AI Workspace Chat
- F7.2D4F bounded native internal-agent reads, grounded responses, and native read provenance
- F7.3A minimal external-MCP actor audit evidence
- F7.3B broad typed row/detail reads

Native survival proof now passes through real store reads: an `INTERNAL_MODEL` agent can read the current F6B test/shadow inventory evidence through `NATIVE_MSA_BACKEND`, with `MCP used: no`, while production writes remain closed.

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
- D4E durable AI Workspace Chat and persisted history
- D4F bounded native read-tool adapter and grounded store-data answers
- server-owned identity/policy injection
- provider/model/fallback/latency attempt provenance
- backend-first AI Workspace access policy
- Owner-only Multi-Agent surface remains isolated from normal user Chat

### Current: Chat UX + lifecycle

Canonical current contract: `docs/checkpoints/F7_2D4G_CHAT_UX_LIFECYCLE_PLAN_2026-08-23.md`.

Current work:

- complete long native-read answers without the old 1024-token Workspace truncation;
- deterministic USER -> ASSISTANT ordering;
- clean plain-text mobile presentation;
- selectable/copyable messages;
- first-message preview + human-friendly last-interaction timestamp on conversation cards;
- authenticated owner-only conversation deletion with cascading message cleanup.

### Access-control invariants

Owner-only controls are protected in both UI and backend. UI hiding is never authorization.

Non-owner Chat authorization occurs before provider invocation:

`authenticated user -> global non-owner gate -> per-user entitlement -> agent eligibility -> native runtime/tool authority`

Rules:

- Owner always allowed.
- Global OFF is a hard kill switch for all non-owner Chat.
- Global ON + user BLOCK -> deny.
- Global ON + INHERIT/ALLOW -> eligible.
- Denied requests make **zero provider API calls**.
- Multi-Agent execution remains Owner-only regardless of Chat entitlement.
- Tool authority is an intersection; provider/model assignment never expands authority.

## Immediate implementation order

1. F7.2D4G Chat UX/lifecycle acceptance.
2. Provider failover/provenance completion under real failure.
3. Expand native typed reads over shared MSA service contracts as needed.
4. Owner-only Multi-Agent execution using persisted session presets.
5. Optional MCP -> native-agent delegation.
6. Continue full actor-aware operational audit and later controlled writes only after prerequisites.

## F7.2D4 survival acceptance

Core survival proof is now present:

`MSA Web -> selected INTERNAL_MODEL agent -> assigned provider/model -> authorized typed MSA read -> response + provenance`

Remaining D4 hardening includes deterministic failover acceptance, broader native tools, and Owner-only Multi-Agent execution without privilege union.

## Later sequence

1. F7.2D4 — Chat/tools/failover/multi-agent execution
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

Proceed with **F7.2D4G AI Workspace Chat UX + lifecycle**.

Do not enable production inventory writes, AI inventory writes, transfers, Smart Calculator deductions, Telegram/Flutter stock mutations, Sheet mirror conversion, or PostgreSQL canonical promotion during this work.

## Canonical architecture/docs

- `IMPLEMENTATION_PLAN.md`
- `NEW_CHAT_BOOTSTRAP.md`
- `docs/architecture/F7_2D_AI_AGENT_MANAGEMENT.md`
- `docs/architecture/F7_2D_EXECUTION_PATH_SEPARATION.md`
- `docs/architecture/F7_2D4_AI_WORKSPACE_AND_ACCESS.md`
- `docs/architecture/F7_2D2_AGENT_MANAGEMENT_AND_MULTI_AGENT_SESSIONS.md`
- `docs/checkpoints/F7_2D4F_GROUNDED_NATIVE_READS_PLAN_2026-08-23.md`
- `docs/checkpoints/F7_2D4G_CHAT_UX_LIFECYCLE_PLAN_2026-08-23.md`
