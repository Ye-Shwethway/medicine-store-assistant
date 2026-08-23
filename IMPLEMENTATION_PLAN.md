# Medicine Store Assistant — Implementation Plan

Status: **F7.2D4F grounded native read tools are production-accepted; current slice is F7.2D4G AI Workspace Chat UX + lifecycle; production inventory write authority remains unauthorized**

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
- bounded native read tools for inventory/shadow summary, `NEW_UNMAPPED`, and review reasons;
- manual acceptance proving real F6B shadow data can be read by the native internal agent without public MCP;
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

Effective typed-tool authority remains an intersection of system gate, authenticated human authority, selected-agent capability/ceiling, location scope, operation class, and confirmation policy. Never union privileges.

## 6. Current implementation slices

### D4.4A — Access policy — VERIFIED

Backend-first global gate, per-user entitlement persistence, Owner bypass, and provider-before-denial protection are implemented.

### D4.4B / D4.5 — Durable Chat + AI Workspace UI — VERIFIED

Durable per-user conversations/messages and the separate top-level AI Workspace are production-live. Manual acceptance confirmed provider-backed replies and persistence after refresh.

### D4.6 / F7.2D4F — Grounded native read tools — VERIFIED

Production-live and manually accepted:

- hardened grounding/language boundary;
- bounded native reads over backend/database contracts, not public MCP;
- inventory/shadow summary;
- bounded `NEW_UNMAPPED` rows;
- bounded review-reason summary;
- selected-agent READ capability/authority requirement;
- native tool provenance persisted with assistant messages;
- production writes remain disabled.

Acceptance evidence showed 1,646 F6B rows with SAFE 1,417 / REVIEW 222 / CONFLICT 0 / NEW_UNMAPPED 7 and real NEW_UNMAPPED row payloads.

### F7.2D4G — Chat UX + lifecycle — CURRENT

Canonical slice contract: `docs/checkpoints/F7_2D4G_CHAT_UX_LIFECYCLE_PLAN_2026-08-23.md`.

Implement now:

- prevent long native-read replies from ending at the old 1024-token workspace default;
- deterministic USER -> ASSISTANT ordering when paired rows share a transaction timestamp;
- clean phone-friendly plain-text response presentation without raw Markdown markers;
- explicit Copy control plus selectable/long-press message text;
- conversation-card first-user-message preview;
- human-friendly last-interaction timestamp;
- owner-of-conversation backend DELETE + cascade message cleanup;
- safe delete UX and selection fallback;
- preserve access policy, read-only tool scope, and non-canonical boundary.

### D4.7 — Failover/provenance completion

Exercise deterministic PRIMARY -> ordered FALLBACK behavior under real failure and record complete provider/model/latency/usage provenance.

### D4.8 — Owner-only Multi-Agent execution

Use persisted session presets for actual `GROUP`, `COMPARE`, `REVIEW`, `DEBATE` inference in `AI Workspace -> Multi-Agent`.

Backend Owner authorization is mandatory. Each participant keeps separate identity, assignment, and authority; never union privileges.

### D4.9 — Optional MCP delegation

Only after the native workspace is stable, connect MCP delegation slots to the same native runtime for explicit delegation. Direct MCP operations remain direct.

## 7. F7.2D4G acceptance

This slice passes when:

1. a long 7-row NEW_UNMAPPED response reaches a natural end rather than output-budget truncation;
2. persisted turns render deterministically USER then ASSISTANT;
3. normal display does not expose raw `#`, `**`, backtick, or pipe-table formatting clutter;
4. message text is selectable and every saved message has a Copy action;
5. conversation cards show first-message preview plus human-friendly `updated_at`;
6. an authenticated user can delete only their own conversation and its messages disappear with it;
7. refresh preserves remaining conversations and sequence;
8. public MCP remains unused by the native Chat path;
9. no production inventory write or canonical DB promotion occurs.

## 8. Immediate execution boundary

Proceed with **F7.2D4G Chat UX + lifecycle**, deploy, manually verify long-response completion/sequence/copy/card metadata/delete, then sync deployment evidence and continuity docs.

Do not enable production inventory writes, AI inventory writes, transfers, Smart Calculator deductions, Telegram/Flutter stock mutations, Sheet mirror conversion, or PostgreSQL canonical promotion in this work.
