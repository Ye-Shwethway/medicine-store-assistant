# Medicine Store Assistant — Implementation Plan

Status: **F7.2D4F grounded native reads and F7.2D4G Chat UX/lifecycle are production/manual accepted; D4.7A hybrid native tool calling and D4.7B response/attachment UX are manually accepted; D4.7 fallback UI is implemented with live failover proof pending; D4.8 shared Work/Review substrate and Owner-only native REVIEW backend are deployed through migration 0021; current target is Owner REVIEW UI + real end-to-end manual acceptance; production inventory write authority remains unauthorized**

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
- deterministic fast-path native reads plus bounded model-driven tool calls for contextual follow-ups;
- bounded photo/file attachment persistence, image previews, dynamic latest-message conversation cards, and explicit no-vision/OCR boundary;
- production inventory writes remain closed.

Deployed but still awaiting full end-to-end UI/manual acceptance:

- D4.8 Work Item / Artifact / Review / Event / Attention Queue substrate;
- stable REVIEW orchestration roles separate from display labels;
- Owner-only native REVIEW backend execution through ACTIVE `INTERNAL_MODEL` participants;
- version-bound reviewer records and per-participant provider/model/fallback/latency provenance;
- durable WAITING_OWNER / workflow-failure attention state.

## 4. AI Workspace architecture — LOCKED

Canonical designs:

- `docs/architecture/F7_2D4_AI_WORKSPACE_AND_ACCESS.md`
- `docs/architecture/F7_2D48_MULTI_AGENT_REVIEW_AND_FEDERATION.md`
- `docs/checkpoints/F7_2D48_NATIVE_REVIEW_RUNTIME_2026-08-24.md`

### Control plane

`AI Agent Management` remains **Owner-only** and stores agent lifecycle/policy, provider/model/fallback assignments, reusable multi-agent session presets, and the global non-owner AI Workspace switch.

Owner-only restrictions must exist in both UI and backend. Hiding controls is not authorization.

### Work plane

Top-level **AI Workspace** is the operational surface.

- `Chat` — single selected internal agent; Owner plus authorized users.
- `Multi-Agent` — `REVIEW`, `GROUP`, `COMPARE`, `DEBATE`; Owner-only for this phase.

Both composer contracts reuse the same photo/file attachment architecture. Upload evidence never changes agent or human authority.

## 5. AI Workspace access policy

1. Owner -> always ALLOW.
2. Non-owner + global OFF -> DENY before any provider request.
3. Non-owner + global ON + per-user BLOCK -> DENY.
4. Non-owner + global ON + INHERIT/ALLOW -> eligible to continue.
5. Per-user ALLOW never overrides global OFF.

Effective typed-tool authority remains an intersection of system gate, authenticated human authority, selected-agent capability/ceiling, location scope, operation class, and confirmation policy. Never union privileges.

Native store-tool execution is currently restricted server-side to Owner sessions until the human/location authority intersection for staff is implemented. Non-owner Chat may still reason but receives no store-tool execution authority.

## 6. Completed/current slices

### D4.4A — Access policy — VERIFIED

Backend-first global gate, per-user entitlement persistence, Owner bypass, and provider-before-denial protection are implemented.

### D4.4B / D4.5 — Durable Chat + AI Workspace UI — VERIFIED

Durable per-user conversations/messages and the separate top-level AI Workspace are production-live.

### D4.6 / F7.2D4F — Grounded native read tools — VERIFIED

Production-live and manually accepted. Native reads use backend/database contracts, not public MCP, and require selected-agent READ capability/authority. F6B remains test/shadow and non-canonical.

### F7.2D4G — Chat UX + lifecycle — VERIFIED

Production/manual acceptance confirmed: long output, deterministic USER -> ASSISTANT order, clean display, Copy/select, richer dynamic conversation cards, and owner-scoped deletion.

### D4.7 — Fallback management — CONFIGURATION IMPLEMENTED / LIVE FAILOVER PENDING

The Owner UI exposes PRIMARY + up to five ordered FALLBACK assignments. Live failover acceptance remains pending until a stable secondary model/provider is available and a primary failure is forced/observed.

### D4.7A — Hybrid native tool calling — VERIFIED

Production/manual acceptance confirmed: deterministic fast path + bounded model-driven native tool calls, backend allowlist validation, no public MCP dependency, no native write/control tools.

### D4.7B — Human response contract + attachments — VERIFIED / MANUALLY ACCEPTED

Canonical checkpoint: `docs/checkpoints/F7_2D47B_RESPONSE_AND_ATTACHMENTS_PLAN_2026-08-24.md`.

Accepted behavior includes human-facing normalized answers, bounded photo/file persistence, authenticated ownership, image preview, latest-message cards, and explicit no-vision/OCR boundaries while provider byte delivery remains unwired.

### D4.8A — Shared work/review substrate — DEPLOYED

PR #100 merge: `4a9f54e17f2b386dfdd390af5850be2100986aac`.

Deployed persistence/contracts:

- Work Items;
- versioned Artifacts;
- version-bound Reviews;
- immutable Events;
- shared Attention Queue;
- actor types `OWNER`, `USER`, `INTERNAL_AGENT`, `EXTERNAL_MCP_AGENT`, `SYSTEM`;
- compact lifecycle transition guard with direct `APPROVED -> COMMITTED` forbidden.

Artifacts/reviews expose no inventory mutation primitive.

### D4.8B — Owner-only native REVIEW backend — DEPLOYED / MANUAL ACCEPTANCE PENDING

PR #101 merge: `0ebaba7d62f5cc3d9d3ec95e1cd33b4ccb7c324e`.

Deployment evidence: issue #26 recorded `status=success`, workflow run `32660149646`, production migration head `0021_review_orchestration_roles`.

Implemented backend behavior:

- stable `ANALYST`, `REVIEWER`, `SYNTHESIZER` role binding stored separately from custom display labels;
- role assign/read APIs for open REVIEW presets;
- REVIEW execution is backend Owner-only and native-only in this slice;
- every participant must be ACTIVE `INTERNAL_MODEL` and is invoked independently through the existing native runtime;
- Owner task/evidence creates a durable Work Item + `OWNER_TASK` artifact;
- existing AI Workspace attachment metadata can be referenced after Owner ownership validation; no second upload system; attachment bytes remain `NOT_PROCESSED` for vision/OCR;
- participant outputs persist as versioned Artifacts with native provider/model/fallback/latency provenance;
- REVIEWER records are bound to the exact prior artifact ID/version;
- success ends at `WAITING_OWNER` and creates durable Owner attention;
- participant invocation failure ends at `FAILED` and creates durable workflow-failure attention;
- Owner may return `WAITING_OWNER` work to `REVIEWING` with a persisted revision instruction;
- no production store mutation occurs.

Full first REVIEW acceptance is still pending because the Owner-facing Multi-Agent REVIEW UI and a real manual run have not yet been accepted.

## 7. D4.8 — Multi-Agent Review + federation — CURRENT

Canonical architecture: `docs/architecture/F7_2D48_MULTI_AGENT_REVIEW_AND_FEDERATION.md`.

### 7.1 Mandatory product invariant

**External/federated agents are optional.** A Multi-Agent preset must be able to run entirely with native `INTERNAL_MODEL` agents. Do not require ChatGPT/MCP for Review, Group, Compare, or Debate.

### 7.2 REVIEW lifecycle

`DRAFT -> REVIEWING -> WAITING_EXTERNAL? -> WAITING_OWNER -> APPROVED -> COMMITTABLE -> COMMITTED`

Rules:

- `WAITING_EXTERNAL` is optional and skipped by native-only workflows;
- rejected/needs-fix work returns to `REVIEWING` or `DRAFT`;
- `APPROVED` never means store state changed;
- `COMMITTABLE` requires all applicable typed-operation authority/validation/confirmation/write gates;
- `COMMITTED` requires successful typed mutation + read-back/audit evidence;
- current project write gate still prevents production mutation.

### 7.3 Stable orchestration roles

System roles are `ANALYST`, `REVIEWER`, `SYNTHESIZER`. Presets may apply Owner-defined display labels; roles never grant authority.

### 7.4 Shared coordination substrate

Durable Work Items, versioned Artifacts, version-bound Reviews, immutable Events, and Attention Queue are now deployed. **Artifact/review != committed store state.**

### 7.5 Native REVIEW current runtime

Current backend flow:

`Owner task/evidence -> DRAFT -> REVIEWING -> ordered native participants -> WAITING_OWNER`

The Owner UI still needs to expose preset selection, stable role configuration, task/evidence submission, progress/provenance, Work Item inspection, and revision/re-review controls before manual acceptance.

### 7.6 Optional federation after native REVIEW acceptance

After native REVIEW is manually proven, add bounded MCP work exchange to list/read eligible work items, read exact artifact versions/review history, submit version-bound external reviews/proposals, and acknowledge attention where policy permits.

Prefer the existing v2.1 long-lived MCP tools with open `action: str` selectors + backend allowlists before introducing any new tool name/schema. A separate MCP backend server is not required.

External review changes workflow/review state only. It never inherits internal-agent authority and cannot bypass typed-operation authorization.

### 7.7 Telegram attention layer

Telegram remains notification/lightweight attention delivery over the same persisted state, not the workflow source of truth or orchestrator. Notification failure must never lose or advance workflow state.

### 7.8 GROUP / COMPARE / DEBATE

GROUP comes after REVIEW/federation substrate acceptance and uses bounded native shared-context turns with Owner pause/resume/stop/steer. COMPARE preserves independence until comparison. DEBATE uses bounded native rounds before synthesis.

## 8. D4.8 security/authority contract

Owner-only Multi-Agent execution requires backend Owner authorization plus UI restriction.

For each native tool call:

`effective_authority = system gate ∩ authenticated human/session authority ∩ calling agent capability/ceiling ∩ location scope ∩ operation class ∩ confirmation policy`

Never union privileges across participants. Federated submissions remain evidence/review inputs only. Reuse existing attachment ownership/security.

## 9. D4.8 implementation order

1. **DONE / DEPLOYED:** Work Item / Artifact / Review / Event / Attention Queue substrate.
2. **DONE / DEPLOYED BACKEND:** Owner-only preset-linked native REVIEW runtime + stable orchestration roles + work-item readback/revision transition.
3. **CURRENT:** AI Workspace Multi-Agent REVIEW UI using the existing photo/file evidence contract.
4. **CURRENT ACCEPTANCE AFTER UI:** real native `ANALYST -> REVIEWER -> SYNTHESIZER` run with persisted provenance, reload survival, Work Item/review inspection, and Owner return-for-revision.
5. Optional MCP federated `WAITING_EXTERNAL` work/review exchange with exact artifact-version binding.
6. Telegram delivery adapter over Attention Queue/events; delivery failure non-fatal to workflow correctness.
7. GROUP bounded native loop + Owner pause/resume/stop/steer + optional federated checkpoint.
8. COMPARE and DEBATE execution.
9. Return to live D4.7 failover proof when a stable secondary provider/model is available.

## 10. D4.8 initial acceptance

First REVIEW slice passes only when:

1. Owner can select/use a REVIEW preset containing native agents only;
2. session execution is backend Owner-only;
3. task/evidence creates a durable Work Item and versioned Artifact;
4. configured native participants execute in role/order with separate provenance;
5. each calling agent retains independent authority; no privilege union occurs;
6. result reaches WAITING_OWNER without production mutation;
7. Owner can inspect reviews/artifact versions and return work for revision;
8. attachments reuse the existing secured AI Workspace evidence contract;
9. workflow survives reload/restart from persisted state;
10. external ChatGPT/MCP is not required.

Backend/CI/deploy evidence now covers much of 2–8 structurally, but UI + real manual execution/reload inspection are required before marking the slice verified.

## 11. Immediate execution boundary

Proceed with **Owner-facing D4.8 REVIEW UI -> real native-only manual acceptance**. External federation and Telegram notifications come only after native Review is proven.

Do not enable production inventory writes, AI inventory writes, transfers, Smart Calculator deductions, Telegram/Flutter stock mutations, Sheet mirror conversion, automatic OCR/vision commits, or PostgreSQL canonical promotion in this work.
