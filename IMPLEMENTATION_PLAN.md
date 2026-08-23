# Medicine Store Assistant — Implementation Plan

Status: **F7.2D4F grounded native reads and F7.2D4G Chat UX/lifecycle are production/manual accepted; D4.7 fallback configuration UI is implemented; current refinement is D4.7A hybrid deterministic + model-driven native tool calling before live failover proof; production inventory write authority remains unauthorized**

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

Verified in production/manual acceptance:

- stable named agent identity/policy;
- Provider Registry + saved/tested model catalog;
- backend primary + ordered fallback assignment contract for `INTERNAL_MODEL` agents;
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
- real F6B shadow evidence read by native internal agent without public MCP;
- long Chat replies, deterministic USER -> ASSISTANT order, clean display, Copy/select, conversation preview/time, and owner-scoped delete;
- Multi-Agent UI remains Owner-only and execution is not yet wired;
- production inventory writes remain closed.

## 4. AI Workspace architecture — LOCKED

Canonical design: `docs/architecture/F7_2D4_AI_WORKSPACE_AND_ACCESS.md`.

### Control plane

`AI Agent Management` remains **Owner-only** and stores agent lifecycle/policy, provider/model/fallback assignments, reusable multi-agent session definitions, and the global non-owner AI Workspace switch.

Owner-only restrictions must exist in both UI and backend. Hiding controls is not authorization.

### Work plane

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

During D4.7A, native store-tool execution is additionally restricted server-side to Owner sessions until the human/location authority intersection for staff is implemented. Non-owner Chat may still reason but receives no store-tool execution authority.

## 6. Current implementation slices

### D4.4A — Access policy — VERIFIED

Backend-first global gate, per-user entitlement persistence, Owner bypass, and provider-before-denial protection are implemented.

### D4.4B / D4.5 — Durable Chat + AI Workspace UI — VERIFIED

Durable per-user conversations/messages and the separate top-level AI Workspace are production-live.

### D4.6 / F7.2D4F — Grounded native read tools — VERIFIED

Production-live and manually accepted. Native reads use backend/database contracts, not public MCP, and require selected-agent READ capability/authority. F6B remains test/shadow and non-canonical.

### F7.2D4G — Chat UX + lifecycle — VERIFIED

Production/manual acceptance confirmed:

- long NEW_UNMAPPED output reaches its natural end;
- deterministic USER -> ASSISTANT order;
- clean phone-friendly plain-text display;
- Copy + selectable message text;
- conversation-card first-message preview and human-friendly timestamp;
- owner-scoped conversation delete with cascade message cleanup.

Canonical checkpoint: `docs/checkpoints/F7_2D4G_CHAT_UX_LIFECYCLE_PLAN_2026-08-23.md`.

### D4.7 — Fallback management — CONFIGURATION IMPLEMENTED / LIVE FAILOVER PENDING

Canonical checkpoint: `docs/checkpoints/F7_2D47_FALLBACK_MANAGEMENT_PLAN_2026-08-23.md`.

The Owner UI now exposes the existing backend PRIMARY + up to five ordered FALLBACK assignments. Live failover acceptance remains pending until two healthy saved models are configured and a primary failure is forced/observed.

### D4.7A — Hybrid native tool calling — CURRENT

Canonical checkpoint: `docs/checkpoints/F7_2D47A_NATIVE_TOOL_CALLING_PLAN_2026-08-23.md`.

Implement now:

- preserve deterministic keyword routing as a low-latency fast path for explicit inventory/NEW_UNMAPPED/review requests;
- add a bounded model-driven tool-calling loop for OpenAI-compatible saved models that advertise tool support;
- expose every currently implemented and backend-authorized native read tool definition to the model: `inventory_summary`, `new_unmapped_rows`, `review_reasons`;
- allow tool-capable models to request those tools for contextual follow-ups even when the current message does not match a deterministic keyword;
- validate every model-requested tool against the native allowlist before execution;
- cap the loop at four tool rounds;
- persist tools exposed, model-requested tools/arguments, execution status, provider/model attempts, latency, and `mcp_used=false`;
- keep non-owner store-tool execution disabled until human/location authority intersection is implemented;
- do not expose write/control tools;
- do not route internal tools through public MCP.

Provider/model tool support is a capability signal, not authority. Backend authorization remains decisive.

### D4.8 — Owner-only Multi-Agent execution

Use persisted session presets for actual `GROUP`, `COMPARE`, `REVIEW`, `DEBATE` inference in `AI Workspace -> Multi-Agent`.

Backend Owner authorization is mandatory. Each participant keeps separate identity, assignment, and authority; never union privileges.

### D4.9 — Optional MCP delegation

Only after the native workspace is stable, connect MCP delegation slots to the same native runtime for explicit delegation. Direct MCP operations remain direct.

## 7. D4.7A acceptance

This refinement passes when:

1. explicit supported requests still execute the deterministic fast-path read tools;
2. a contextual follow-up such as `investigate this further` can trigger a model-requested native read tool without requiring the user to manually supply facts;
3. the model sees the full currently authorized native read-tool registry;
4. unknown/non-exposed tool names are rejected by the backend and never execute arbitrary code/SQL;
5. selected agent still requires READ capability + READ-or-higher authority ceiling;
6. native store tools execute only for Owner sessions in this slice;
7. provenance records exposed tools and model tool calls;
8. no public MCP call occurs;
9. no production inventory write or canonical DB promotion occurs.

## 8. D4.7 live failover acceptance after D4.7A

When two healthy saved models are configured:

1. primary attempt fails;
2. fallback is attempted in stored order;
3. response succeeds with `fallback_used=true`;
4. attempt provenance includes failed primary and successful fallback;
5. no public MCP call occurs.

## 9. Immediate execution boundary

Proceed with **D4.7A hybrid native tool calling**, deploy and manually verify both fast-path and contextual model-driven tool execution. Then return to the D4.7 live failover test.

Do not enable production inventory writes, AI inventory writes, transfers, Smart Calculator deductions, Telegram/Flutter stock mutations, Sheet mirror conversion, or PostgreSQL canonical promotion in this work.
