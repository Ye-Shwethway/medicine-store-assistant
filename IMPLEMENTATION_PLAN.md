# Medicine Store Assistant — Implementation Plan

Status: **F7.2D4F grounded native reads and F7.2D4G Chat UX/lifecycle are production/manual accepted; D4.7A hybrid native tool calling and D4.7B response/attachment UX are manually accepted; D4.7 fallback UI is implemented with live failover proof pending; D4.8 shared Work/Review substrate, Owner-only native REVIEW backend, and Owner REVIEW UI are deployed through migration 0021; current target is one provided-evidence native-only REVIEW manual acceptance followed by bounded per-participant read-tool hardening; production inventory write authority remains unauthorized**

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

Production/manual accepted foundations include stable named agents, Provider Registry/saved models, primary + ordered fallback assignment configuration, MCP-independent native provider inference, server-owned identity injection, durable AI Workspace Chat, grounded native reads, hybrid model-driven native read-tool calling, human-facing response normalization, bounded attachment evidence, reload-safe Chat history, and Owner-scoped conversation lifecycle.

Current native read-tool registry:

- `inventory_summary`
- `new_unmapped_rows`
- `review_reasons`

Public MCP is not the native tool gateway.

## 4. AI Workspace architecture — LOCKED

Canonical references:

- `docs/architecture/F7_2D4_AI_WORKSPACE_AND_ACCESS.md`
- `docs/architecture/F7_2D48_MULTI_AGENT_REVIEW_AND_FEDERATION.md`
- `docs/checkpoints/F7_2D48_NATIVE_REVIEW_RUNTIME_2026-08-24.md`

Control plane: `AI Agent Management` remains Owner-only.

Work plane:

- `Chat` — one selected internal agent; Owner + authorized users.
- `Multi-Agent` — `REVIEW`, `GROUP`, `COMPARE`, `DEBATE`; Owner-only in this phase.

Both reuse the same bounded attachment ownership/evidence contract.

## 5. Access and authority

Owner always has AI Workspace access. Global OFF blocks all non-owner Chat before provider calls. Non-owner access uses global gate + per-user entitlement.

Native tool authority remains an intersection:

`system gate ∩ authenticated human/session authority ∩ calling agent capability/ceiling ∩ location scope ∩ operation class ∩ confirmation policy`

Never union privileges. Provider/model selection never grants authority.

## 6. Completed/current slices

### D4.6 / F7.2D4F — Grounded native reads — VERIFIED

Native reads use backend/database contracts, not public MCP. F6B remains test/shadow and non-canonical.

### F7.2D4G — Chat UX/lifecycle — VERIFIED

Long output, deterministic USER -> ASSISTANT order, clean display, Copy/select, richer conversation cards, owner-scoped deletion, and persisted attachment evidence are accepted.

### D4.7 — Fallback management — CONFIGURATION IMPLEMENTED / LIVE FAILOVER PENDING

Owner UI exposes PRIMARY + up to five ordered FALLBACK assignments. Live forced failover proof remains pending.

### D4.7A — Hybrid native tool calling — VERIFIED

Deterministic fast path + bounded model-driven native read-tool loop is accepted for AI Workspace Chat. Backend allowlists every exposed tool; no native write/control tools exist.

### D4.7B — Human response + attachments — VERIFIED / MANUALLY ACCEPTED

Photo/file evidence is ownership-scoped and bounded. Provider vision/OCR byte processing remains unwired.

### D4.8A — Shared Work/Review substrate — DEPLOYED

PR #100 merge: `4a9f54e17f2b386dfdd390af5850be2100986aac`.

Deployed:

- Work Items;
- versioned Artifacts;
- exact-version Reviews;
- immutable Events;
- shared Attention Queue;
- actor types `OWNER`, `USER`, `INTERNAL_AGENT`, `EXTERNAL_MCP_AGENT`, `SYSTEM`;
- lifecycle transition guard with direct `APPROVED -> COMMITTED` forbidden.

Artifact/review persistence exposes no inventory mutation primitive.

### D4.8B — Owner-only native REVIEW backend — DEPLOYED

PR #101 merge: `0ebaba7d62f5cc3d9d3ec95e1cd33b4ccb7c324e`.

Production migration head: `0021_review_orchestration_roles`.

Implemented:

- stable `ANALYST`, `REVIEWER`, `SYNTHESIZER` roles separate from custom display labels;
- open REVIEW preset role assign/read APIs;
- native-only Owner REVIEW execution through ACTIVE `INTERNAL_MODEL` participants;
- Owner task/evidence -> Work Item + Artifact;
- versioned participant Artifacts with provider/model/fallback/latency provenance;
- REVIEWER record bound to exact prior artifact/version;
- success -> `WAITING_OWNER` + durable attention;
- failure -> `FAILED` + durable attention;
- return-for-revision -> `REVIEWING` + persisted Owner instruction;
- no production mutation.

### D4.8C — Owner REVIEW UI — DEPLOYED / MANUAL ACCEPTANCE PENDING

PR #103 merge: `c980446a7df27a352721115599a5ecf704797097`.

Issue #26 deploy run: `32660684770`, `status=success`, source SHA `c980446a7df27a352721115599a5ecf704797097`.

The AI Workspace Multi-Agent tab now exposes:

- open REVIEW preset selection;
- stable role configuration + optional display labels;
- Work title + Owner task composer;
- optional reference to ownership-validated saved Chat attachments;
- native REVIEW execution;
- reload-safe Recent Review work list;
- Work Item detail with Artifacts, Reviews, provider/model/fallback/latency provenance, Attention and Event timeline;
- WAITING_OWNER return-for-revision;
- explicit no-production-mutation/non-canonical messaging.

Dedicated UI assets:

- `dashboard_multi_agent_review.js`
- `dashboard_multi_agent_review.css`
- version `f72d48-review-ui-1`

CI validates real FastAPI routes, JS syntax, responsive UI contract, exact asset-version chain, stale-marker absence, and broad regression suites.

## 7. D4.8 REVIEW lifecycle

`DRAFT -> REVIEWING -> WAITING_EXTERNAL? -> WAITING_OWNER -> APPROVED -> COMMITTABLE -> COMMITTED`

Rules:

- `WAITING_EXTERNAL` is optional;
- rejected/needs-fix work returns to review/draft state;
- `APPROVED` never means store state changed;
- `COMMITTABLE` requires all later typed-operation authority/validation/confirmation/write gates;
- `COMMITTED` requires successful mutation + read-back/audit;
- current write gates still prohibit production mutation.

## 8. Current native REVIEW boundary

The deployed first REVIEW executor uses the **plain native provider invocation path**. It does not yet invoke the D4.7A model-driven native read-tool loop.

Therefore the first manual acceptance is intentionally a **provided-evidence/native-reasoning Review**.

Do not claim REVIEW participants executed current MSA read tools until a hardening slice explicitly integrates them with per-participant READ authority checks.

Required hardening rule:

`tool access for participant N = Owner/session gate ∩ participant N READ capability/ceiling ∩ applicable location/operation policy`

Never borrow or union another participant's authority.

## 9. Initial manual REVIEW acceptance — CURRENT

Pass only when a real Owner browser run proves:

1. an open REVIEW preset contains native agents only;
2. stable roles are saved separately from display labels;
3. task/evidence creates a durable Work Item + Artifact;
4. participants execute in configured order with separate provenance;
5. result reaches `WAITING_OWNER` without inventory mutation;
6. Work Item detail exposes exact-version Review records and Artifacts;
7. browser reload rediscovers the same Work Item from Recent Review work;
8. Owner can return it to `REVIEWING` with a persisted revision instruction;
9. external ChatGPT/MCP is not required;
10. UI accurately states attachments are evidence metadata only and vision/OCR is not processed.

## 10. Next authorized order

1. **CURRENT:** manually accept one provided-evidence/native-reasoning REVIEW through the deployed Owner UI.
2. Add bounded per-participant D4.7A native read-tool integration for REVIEW.
3. Manually accept one tool-using REVIEW before relying on Multi-Agent for current-store operational conclusions.
4. Add optional federated `WAITING_EXTERNAL` work/review exchange with exact artifact-version binding, preferring existing v2.1 open-selector MCP slots before schema expansion.
5. Add Telegram notification delivery over the shared Attention Queue; delivery failure remains non-fatal.
6. Add GROUP bounded native loop + Owner pause/resume/stop/steer + optional federated checkpoint.
7. Add COMPARE and DEBATE execution.
8. Return to live D4.7 failover proof when a stable secondary provider/model is available.

## 11. Immediate boundary

Proceed with **one real provided-evidence native-only REVIEW manual acceptance -> bounded per-participant native read-tool hardening**.

Do not enable production inventory writes, AI inventory writes, transfers, Smart Calculator deductions, Telegram/Flutter stock mutations, Sheet mirror conversion, automatic OCR/vision commits, or PostgreSQL canonical promotion.
