# Medicine Store Assistant — Implementation Plan

Status: **F7.2D4E durable AI Workspace Chat is production-accepted; current slice is F7.2D4F grounded native read tools + Chat UI polish; production inventory write authority remains unauthorized**

This file is the execution contract for current MSA implementation order and boundaries.

## 1. Global rules

- Google Sheets remains operationally authoritative until explicit F11 promotion.
- PostgreSQL being deployed does **not** make it canonical.
- F6B remains test-only and must never be silently promoted.
- All humans, AI agents, integrations, and system jobs use typed backend operations.
- Never expose arbitrary SQL, DB credentials, VPS shell/filesystem, Sheet credentials, plaintext provider keys, passwords/tokens/recovery secrets, or unrestricted HTTP proxying to AI/client runtimes.
- Deterministic backend code owns identity, authorization, capability/location policy, constraints, idempotency, transactions, read-back, and audit semantics.
- Provider/model choice never grants authority.
- Significant architecture/implementation/deploy/next-work changes update `ROADMAP.md`, `NEW_CHAT_BOOTSTRAP.md`, this file, and relevant canonical docs.
- Web delivery follows `docs/design/WEB_ASSET_RELEASE_INTEGRITY.md`.

## 2. Canonical execution paths

External MCP:

`ChatGPT model -> MCP action -> MCP authority intersection -> typed MSA backend operation -> result`

Native internal agent:

`MSA Web / future Telegram / Flutter / automation -> INTERNAL_MODEL runtime -> assigned provider/model -> internal typed-tool adapter -> typed MSA backend operation -> response`

These are peer paths. Internal agents do not depend on public MCP for ordinary work. Direct MCP actions do not require an internal-agent intermediary. `msa_agent_invoke` is optional delegation/orchestration only.

## 3. Verified native-agent foundation

Verified in production:

- stable named agent identity/policy;
- Provider Registry + saved/tested model catalog;
- primary + ordered fallback assignment contract for `INTERNAL_MODEL` agents;
- backend rejection of provider/model assignment for non-internal agents;
- MCP-independent native provider invocation;
- server-owned agent identity/policy injection;
- OpenAI-compatible and Gemini provider paths;
- provider/model/fallback/latency attempt provenance;
- native test UI proving `MCP used: no`;
- AI Workspace backend access policy with Owner bypass/global non-owner gate/per-user entitlement foundation;
- durable single-agent conversations/messages;
- top-level `AI Workspace` Chat with named-agent selection and persisted conversation history;
- Multi-Agent UI remains Owner-only and execution is not yet wired;
- production inventory writes remain closed.

## 4. AI Workspace architecture — LOCKED

Canonical design: `docs/architecture/F7_2D4_AI_WORKSPACE_AND_ACCESS.md`.

### 4.1 Control plane

`AI Agent Management` remains **Owner-only** and stores agent lifecycle/policy, provider/model assignments, reusable multi-agent session definitions, and the global non-owner AI Workspace switch.

Owner-only restrictions must exist in both UI and backend. Hiding controls is not authorization.

### 4.2 Work plane

Top-level **AI Workspace** is the operational surface.

- `Chat` — single selected internal agent; Owner plus authorized users.
- `Multi-Agent` — future GROUP/COMPARE/REVIEW/DEBATE execution; Owner-only for this phase.

## 5. AI Workspace access policy

1. Owner -> always ALLOW.
2. Non-owner + global OFF -> DENY before any provider request.
3. Non-owner + global ON + per-user BLOCK -> DENY.
4. Non-owner + global ON + INHERIT/ALLOW -> eligible to continue.
5. Per-user ALLOW never overrides global OFF.

When typed tools are attached, effective authority remains an intersection of system gate, authenticated human authority, selected agent capability/ceiling, location scope, operation class, and confirmation policy. Never union privileges.

## 6. Current implementation slices

### D4.4A — Access policy — VERIFIED

Backend-first global gate, per-user entitlement persistence, Owner bypass, and provider-before-denial protection are implemented.

### D4.4B / D4.5 — Durable Chat + AI Workspace UI — VERIFIED

Durable per-user conversations/messages and the separate top-level AI Workspace are production-live. Manual acceptance confirmed provider-backed replies and persistence after refresh.

### D4.6 / F7.2D4F — Grounded native read tools — CURRENT

Implement now:

- harden native grounding/language instructions;
- do not invent MSA/store-specific facts;
- attach bounded native read adapters directly over MSA backend/database read contracts, **not MCP**;
- initial reads: latest inventory/shadow summary, bounded `NEW_UNMAPPED` rows, bounded review-reason summary;
- execute read adapters only after AI Workspace access + conversation ownership + selected-agent validation;
- require selected agent READ capability/authority before store data is supplied;
- persist native tool provenance with the assistant message;
- keep the provider unable to request arbitrary backend operations in this slice;
- realign AI Workspace buttons/tabs/composer with the Dashboard visual system on mobile;
- keep production writes disabled.

Canonical slice contract: `docs/checkpoints/F7_2D4F_GROUNDED_NATIVE_READS_PLAN_2026-08-23.md`.

### D4.7 — Failover/provenance completion

Exercise deterministic PRIMARY -> ordered FALLBACK behavior under real failure and record complete provider/model/latency/usage provenance.

### D4.8 — Owner-only Multi-Agent execution

Use persisted session presets for actual `GROUP`, `COMPARE`, `REVIEW`, `DEBATE` inference in `AI Workspace -> Multi-Agent`.

Backend Owner authorization is mandatory. Each participant keeps separate identity, assignment, and authority; never union privileges.

### D4.9 — Optional MCP delegation

Only after the native workspace is stable, connect MCP delegation slots to the same native runtime for explicit delegation. Direct MCP operations remain direct.

## 7. F7.2D4F acceptance

This slice passes when:

1. asking Chat for the inventory summary causes an authorized native read and returns actual test/shadow summary evidence;
2. asking for `NEW_UNMAPPED` rows returns bounded real rows rather than invented rows;
3. a selected agent without READ authority receives no store data;
4. Burmese/general prompts are instructed not to fabricate current MSA facts and to follow the user's language when practical;
5. assistant message provenance records which native read tools were requested/executed;
6. public MCP is not used by this native tool path;
7. mobile AI Workspace controls match the Dashboard UI language;
8. no production inventory write or canonical DB promotion occurs.

The larger survival proof remains:

`MSA Web -> selected INTERNAL_MODEL agent -> assigned provider/model -> authorized typed MSA read -> response + provenance`

## 8. Immediate execution boundary

Proceed with **F7.2D4F grounded bounded reads + UI polish**, deploy, manually verify inventory-summary and `NEW_UNMAPPED` prompts, then sync checkpoint/continuity docs.

Do not enable production inventory writes, AI inventory writes, transfers, Smart Calculator deductions, Telegram/Flutter stock mutations, Sheet mirror conversion, or PostgreSQL canonical promotion in this work.
