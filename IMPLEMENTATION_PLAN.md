# Medicine Store Assistant — Implementation Plan

Status: **F7.2D4F grounded native reads and F7.2D4G Chat UX/lifecycle are production/manual accepted; D4.7A hybrid native tool calling and D4.7B response/attachment UX are manually accepted; D4.7 fallback UI is implemented with live failover proof pending; current implementation target is D4.8 shared Multi-Agent Review substrate + native-only Review execution; production inventory write authority remains unauthorized**

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
- Multi-Agent UI remains Owner-only and execution is not yet wired;
- production inventory writes remain closed.

## 4. AI Workspace architecture — LOCKED

Canonical designs:

- `docs/architecture/F7_2D4_AI_WORKSPACE_AND_ACCESS.md`
- `docs/architecture/F7_2D48_MULTI_AGENT_REVIEW_AND_FEDERATION.md`

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

Accepted behavior includes:

- human-facing normalized answers while preserving raw provenance;
- photo/image and generic file upload controls;
- max four pending attachments, max 8 MB each, MIME allowlist;
- authenticated conversation ownership;
- remove-before-send and bound message persistence;
- JPEG/PNG/WebP thumbnail before send and image rendering in USER messages;
- latest-message conversation-card preview + human-friendly timestamp;
- attachment bytes remain unavailable to provider vision/OCR until a later typed processor is explicitly wired.

## 7. D4.8 — Multi-Agent Review + federation — CURRENT

Canonical architecture: `docs/architecture/F7_2D48_MULTI_AGENT_REVIEW_AND_FEDERATION.md`.

### 7.1 Mandatory product invariant

**External/federated agents are optional.**

A Multi-Agent preset must be able to run entirely with native `INTERNAL_MODEL` agents. The Owner may optionally configure or request an external/federated checkpoint.

Do not design Review, Group, Compare, or Debate such that ChatGPT/MCP is required for normal execution.

### 7.2 Participant classes

Native participant:

- orchestrator-controlled live invocation;
- own identity/provider/model/fallback/tool authority;
- can participate in bounded automatic turns.

Federated participant:

- initially bound ChatGPT/MCP;
- asynchronous persisted work/review exchange;
- not represented as a fake live participant that MSA can force to answer;
- optional in presets/work items.

### 7.3 REVIEW lifecycle

Canonical lifecycle:

`DRAFT -> REVIEWING -> WAITING_EXTERNAL? -> WAITING_OWNER -> APPROVED -> COMMITTABLE -> COMMITTED`

Rules:

- `WAITING_EXTERNAL` is optional and skipped by native-only workflows;
- rejected/needs-fix work returns to `REVIEWING` or `DRAFT`;
- `APPROVED` never means store state changed;
- `COMMITTABLE` means an authorized typed operation is ready after all applicable validation/authority/confirmation/write gates pass;
- `COMMITTED` requires successful typed mutation + read-back/audit evidence;
- current project write gate still prevents production mutation.

### 7.4 Stable orchestration roles

System roles:

- `ANALYST`
- `REVIEWER`
- `SYNTHESIZER`

Presets may apply custom Owner-defined display labels such as `Stock Reviewer` or `Mapping Specialist`. Roles never grant authority.

### 7.5 Shared coordination substrate

Implement durable tables/contracts for:

- **Work Item** — task/objective/status/source channel/session reference;
- **Artifact** — versioned evidence/work product/proposal;
- **Review** — reviewer verdict/findings bound to a specific artifact version;
- **Event** — immutable workflow timeline/provenance;
- **Attention Queue** — durable items needing external/Owner attention or reporting failure/completion.

Actor types must distinguish at least `OWNER`, `USER`, `INTERNAL_AGENT`, `EXTERNAL_MCP_AGENT`, and `SYSTEM`.

**Artifact/review != committed store state.** Persisting a proposed serial code, quantity, expiry, mapping, transfer, or other value must never mutate store data by itself.

### 7.6 REVIEW first implementation

First executable D4.8 mode is native-only REVIEW using existing reusable session presets and the shared attachment contract.

Initial flow:

`Owner task/evidence -> DRAFT -> ANALYST -> REVIEWER -> SYNTHESIZER -> WAITING_OWNER`

A preset may omit roles it does not need. Owner can request revision/re-review before approval.

### 7.7 Optional federation after native REVIEW works

Add bounded MCP work-exchange actions over the same substrate, such as:

- list/read work items visible to the external bound agent;
- read current/versioned artifacts and review history;
- submit an external review against an exact artifact version;
- submit a proposal/review packet;
- request re-review where policy permits.

External review changes workflow/review state only. It does not inherit internal-agent authority and cannot bypass typed-operation authorization.

### 7.8 Telegram attention layer

Telegram is a planned notification/lightweight attention channel, not the workflow source of truth and not the orchestrator.

Notifications may be emitted for internal review completion, external review request, Owner decision required, failures/disagreements, and commit completion.

Web, MCP, and Telegram must surface the same backend Attention Queue. Notification failure must never lose work or advance state.

Typical flow:

`internal agents finish -> work item WAITING_EXTERNAL -> Telegram notifies Owner -> Owner remains in ChatGPT -> MCP reads work item -> ChatGPT submits version-bound review -> workflow continues`

### 7.9 GROUP after REVIEW/federation substrate

GROUP is a bounded shared-context native agentic loop with Owner observation and steering.

Owner controls should later include pause, resume, stop, and inject instruction. External agents are not real-time native Group participants initially, but an optional external checkpoint may pause the loop at `WAITING_EXTERNAL` and resume after a federated review arrives.

### 7.10 COMPARE / DEBATE

COMPARE: participants receive the same task independently and cannot see peers' outputs before their own answer is recorded.

DEBATE: bounded native argument/counterargument rounds followed by synthesis; external participation may be added later only through explicit checkpoint semantics.

## 8. D4.8 security/authority contract

Owner-only Multi-Agent execution requires backend Owner authorization plus UI restriction.

For each native tool call:

`effective_authority = system gate ∩ authenticated human/session authority ∩ calling agent capability/ceiling ∩ location scope ∩ operation class ∩ confirmation policy`

Never union privileges across participants.

Federated submissions are evidence/review inputs. They never gain authority merely by being stored in a session/work item.

Reuse existing attachment ownership/security. Do not create a second upload system.

## 9. D4.8 implementation order

1. DB migration + typed contracts for Work Items, Artifacts, Reviews, Events, Attention Queue.
2. Owner-only APIs for work-item lifecycle/readback and preset-linked native REVIEW.
3. AI Workspace Multi-Agent REVIEW UI using existing photo/file evidence contract.
4. Native `ANALYST -> REVIEWER -> SYNTHESIZER` execution with provenance and Owner steering/re-review.
5. Optional MCP federated read/review submission actions with artifact-version binding.
6. Telegram delivery adapter over Attention Queue/events; delivery failure non-fatal to workflow state.
7. GROUP bounded native loop + Owner pause/resume/stop/steer + optional federated checkpoint.
8. COMPARE and DEBATE execution.
9. Return to live D4.7 failover proof when a stable secondary provider/model is available.

## 10. D4.8 initial acceptance

First REVIEW slice passes when:

1. Owner can select/create a REVIEW preset containing native agents only;
2. session execution is backend Owner-only;
3. task/evidence creates a durable Work Item and versioned Artifact;
4. configured native participants execute in role order with separate provenance;
5. each calling agent retains independent authority; no privilege union occurs;
6. result reaches WAITING_OWNER without any production mutation;
7. Owner can inspect reviews/artifact versions and return work for revision;
8. attachments reuse the existing secured AI Workspace evidence contract;
9. workflow survives reload/restart from persisted state;
10. external ChatGPT/MCP is not required.

Federation acceptance is a later bounded step and must prove version-bound external review without direct DB access or authority escalation.

## 11. Immediate execution boundary

Proceed with **D4.8 shared work/review substrate -> native-only REVIEW mode**. External federation and Telegram notifications come after the native Review substrate is proven.

Do not enable production inventory writes, AI inventory writes, transfers, Smart Calculator deductions, Telegram/Flutter stock mutations, Sheet mirror conversion, automatic OCR/vision commits, or PostgreSQL canonical promotion in this work.
