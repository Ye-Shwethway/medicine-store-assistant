# Medicine Store Assistant — Implementation Plan

Status: **F7.2D4B ordered model assignment and F7.2D4C MCP-independent native provider inference are verified; next work is AI Workspace access policy + durable single-agent Chat; production inventory write authority remains unauthorized**

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

Already verified:

- stable named agent identity/policy;
- Provider Registry + saved/tested model catalog;
- primary + ordered fallback assignment contract for `INTERNAL_MODEL` agents;
- backend rejection of provider/model assignment for non-internal agents;
- MCP-independent native provider invocation;
- server-owned agent identity/policy injection;
- OpenAI-compatible and Gemini provider paths;
- provider/model/fallback/latency attempt provenance;
- native test UI proving `MCP used: no`;
- production inventory writes remain closed.

The current native test is inference-only. Native typed MSA tools are not attached yet.

## 4. AI Workspace architecture — LOCKED

Canonical design: `docs/architecture/F7_2D4_AI_WORKSPACE_AND_ACCESS.md`.

### 4.1 Control plane

`AI Agent Management` remains **Owner-only** and stores:

- agent lifecycle/policy;
- provider/model assignments;
- reusable multi-agent session definitions;
- global non-owner AI Workspace enable/disable setting.

Owner-only restrictions must exist in both UI and backend. Hiding controls is not authorization.

### 4.2 Work plane

Create a separate top-level **AI Workspace**.

Tabs/modes:

- `Chat` — single selected internal agent; Owner plus authorized users.
- `Multi-Agent` — actual GROUP/COMPARE/REVIEW/DEBATE execution; Owner-only for this phase.

Normal users must not see Multi-Agent controls and direct endpoint calls must also be rejected server-side.

## 5. AI Workspace access policy

### 5.1 Owner behavior

Owner always retains AI Workspace access. Global staff/user disable does not disable Owner.

### 5.2 Global non-owner gate

Owner-only setting:

`AI Workspace for non-owner users = ENABLED | DISABLED`

Global OFF is a hard kill switch for all non-owner Chat requests.

A denied request must stop **before provider invocation**. Provider API calls, tokens, and cost must remain zero.

### 5.3 Per-user Chat entitlement

Persist per-user value:

- `INHERIT`
- `ALLOW`
- `BLOCK`

Effective policy:

1. Owner -> ALLOW.
2. Non-owner + global OFF -> DENY.
3. Non-owner + global ON + BLOCK -> DENY.
4. Non-owner + global ON + INHERIT/ALLOW -> eligible to continue.

Per-user ALLOW never overrides global OFF.

### 5.4 Future selected-agent/tool authority

Later user-agent access may further restrict selectable agents.

When typed tools are attached, effective authority is bounded by the intersection of:

- system gate;
- authenticated human/user authority;
- selected agent capability/authority ceiling;
- location scope;
- operation class;
- confirmation policy.

Never union privileges and never allow model/provider choice to expand authority.

## 6. Current implementation slices

### D4.4A — Access-policy persistence + backend authorization

Implement first:

- global AI Workspace non-owner setting;
- per-user Chat entitlement;
- Owner bypass;
- reusable backend authorization helper;
- denial before native provider invocation;
- Owner-only API for the global setting;
- User Management support for editing user entitlement;
- tests proving denied requests never reach provider invocation.

### D4.4B — Conversation/message persistence

Add durable MSA-owned chat state:

- conversation ID;
- authenticated human owner/participant;
- selected internal agent;
- title/lifecycle timestamps;
- messages/roles/timestamps;
- provider/model provenance for assistant messages where relevant.

Initial conversations are single-agent. Multi-agent transcripts come later.

### D4.5 — Top-level AI Workspace Chat UI

Build responsive mobile-first UI:

- separate top-level workspace, not inside AI Agent Management;
- internal-agent selector;
- new/resume conversation;
- conversation history;
- message thread + composer;
- native provider-backed responses;
- compact provenance;
- clear disabled/blocked state.

Ordinary users do not choose provider/model directly.

### D4.6 — Native typed-tool adapter

Attach internal typed tools over shared MSA domain/service functions, not public MCP. Initial proof remains bounded/read-only.

### D4.7 — Failover/provenance completion

Exercise deterministic PRIMARY -> ordered FALLBACK behavior and record provider/model/latency/usage provenance.

### D4.8 — Owner-only Multi-Agent execution

Use persisted session presets for actual `GROUP`, `COMPARE`, `REVIEW`, `DEBATE` inference in `AI Workspace -> Multi-Agent`.

Backend Owner authorization is mandatory. Each participant keeps separate identity, assignment, and authority; never union privileges.

### D4.9 — Optional MCP delegation

Only after the native workspace is stable, connect existing MCP delegation slots to the same native runtime for explicit delegation. Direct MCP operations remain direct.

## 7. Acceptance

AI Workspace foundation passes when:

1. Owner global setting is backend-protected;
2. per-user entitlement is durable;
3. global OFF blocks every non-owner Chat invocation before provider call;
4. Owner remains allowed;
5. Multi-Agent execution endpoints are Owner-only in backend;
6. durable single-agent conversations/messages persist;
7. top-level AI Workspace can select an internal agent and obtain a native response without MCP;
8. blocked users receive deterministic denial UX;
9. provider/model assignment does not alter authority;
10. no production inventory write or canonical DB promotion occurs.

Full F7.2D4 later still requires at least one authorized internal typed MSA read and the complete survival proof:

`MSA Web -> selected INTERNAL_MODEL agent -> assigned provider/model -> authorized typed MSA read -> response + audit`

## 8. Immediate execution boundary

Proceed now with **D4.4A access-policy persistence/backend authorization**, then **D4.4B conversation persistence**, then the top-level **AI Workspace Chat UI**.

Do not enable production inventory writes, AI inventory writes, transfers, Smart Calculator deductions, Telegram/Flutter stock mutations, Sheet mirror conversion, or PostgreSQL canonical promotion in this work.
