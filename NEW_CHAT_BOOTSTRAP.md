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
10. `docs/architecture/F7_2D48_MULTI_AGENT_REVIEW_AND_FEDERATION.md`
11. `docs/checkpoints/F7_2D4F_GROUNDED_NATIVE_READS_PLAN_2026-08-23.md`
12. `docs/checkpoints/F7_2D4G_CHAT_UX_LIFECYCLE_PLAN_2026-08-23.md`
13. `docs/checkpoints/F7_2D47_FALLBACK_MANAGEMENT_PLAN_2026-08-23.md`
14. `docs/checkpoints/F7_2D47A_NATIVE_TOOL_CALLING_PLAN_2026-08-23.md`
15. `docs/checkpoints/F7_2D47B_RESPONSE_AND_ATTACHMENTS_PLAN_2026-08-24.md`
16. current runtime/deployment evidence, especially issue #26
17. `docs/design/UI_UX_PRO_MAX_INTEGRATION.md` and `docs/design/WEB_ASSET_RELEASE_INTEGRITY.md` for Web work

Treat newer verified repository/runtime evidence as authoritative over remembered chat context.

## Current canonicality boundary

- Google Sheet/source documents remain operationally authoritative.
- PostgreSQL is deployed but **not canonical**.
- F6B is test-only and not an accepted migration baseline.
- `database_canonical=false`.
- `migration_baseline_accepted=false`.
- No production inventory write, AI inventory write, transfer, Calculator deduction, Telegram/Flutter stock mutation, Sheet mirror conversion, automatic OCR/vision commit, or DB canonical promotion is authorized.

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
- D4.7A deterministic fast path + model-driven native tool calling; contextual follow-up manual acceptance passed with MiniMax M3;
- D4.7B human-facing response/attachment behavior accepted: photo/file upload, remove-before-send, persisted message binding, JPEG/PNG/WebP previews, latest-message card previews, and explicit no-vision/OCR claim when model bytes are not supplied;
- external MCP direct read/audit remains independent;
- production inventory writes remain disabled.

## AI Workspace architecture — LOCKED

### AI Agent Management — Owner-only control plane

Contains agent lifecycle/policy, provider/model/fallback assignments, reusable multi-agent session definitions, and global non-owner AI Workspace access setting.

Owner-only requires backend authorization plus UI restriction.

### AI Workspace — work plane

- `Chat` — one selected internal agent; Owner + authorized users.
- `Multi-Agent` — `REVIEW`, `GROUP`, `COMPARE`, `DEBATE`; Owner-only in this phase.
- Both composer contracts reuse the same photo/file attachment architecture.

## Access + authority

Owner always has AI Workspace access. Global OFF hard-blocks all non-owner Chat before provider calls. Per-user entitlement foundation is `INHERIT | ALLOW | BLOCK`.

Native tool authority intersects system gate, authenticated human authority, selected-agent capability/ceiling, location scope, operation class, and confirmation policy. Never union privileges. Provider/model assignment never grants authority.

Native store-tool execution is currently backend-restricted to Owner sessions plus selected-agent READ authority. Non-owner Chat is reasoning-only for store tools until explicit human/location tool authority is implemented.

Uploaded attachment evidence is ownership-scoped. Attachment byte/preview endpoints independently enforce authenticated AI Workspace access plus conversation/attachment ownership. An attachment never grants tool/write authority.

## D4.7A native tool calling — VERIFIED

Canonical checkpoint: `docs/checkpoints/F7_2D47A_NATIVE_TOOL_CALLING_PLAN_2026-08-23.md`.

Accepted hybrid behavior:

1. Explicit supported request -> deterministic backend fast-path prefetch -> grounded model answer.
2. If no fast-path evidence exists and the assigned tool-capable model supports tools -> expose currently authorized native read tools -> model requests tools -> backend allowlist/authority validation -> typed result -> final answer.
3. Tool loop is bounded to four rounds.
4. Unsupported providers/models fall back to grounded reasoning and must not claim tool execution.
5. Public MCP is not used.

Current native tool registry:

- `inventory_summary`
- `new_unmapped_rows`
- `review_reasons`

The public MCP schema has 106 actions, but those are not automatically internal-agent tools. Only implemented native typed adapters that are backend-authorized are exposed.

## D4.7B response + attachments — VERIFIED / ACCEPTED

Canonical checkpoint: `docs/checkpoints/F7_2D47B_RESPONSE_AND_ATTACHMENTS_PLAN_2026-08-24.md`.

Accepted current state:

- human-friendly presentation layer with retained provenance;
- deterministic display derivations may be backend-provided while preserving raw source values;
- single-agent Chat has Photo/File upload, bounded persistence, message binding, remove-before-send, image preview, reload persistence, copy/delete/chat-history behavior;
- conversation cards use latest USER/ASSISTANT message preview plus human-friendly interaction time;
- attachment bytes are still not supplied to provider vision/OCR;
- Multi-Agent will reuse the same attachment contract.

## Current architecture/work — D4.8 Multi-Agent Review + federation

Canonical architecture: `docs/architecture/F7_2D48_MULTI_AGENT_REVIEW_AND_FEDERATION.md`.

### Critical invariant

**External/federated participation is OPTIONAL.**

A Multi-Agent preset must be able to run fully native with internal agents only. Do not require ChatGPT/MCP for Review, Group, Compare, or Debate.

### Participant classes

Native participants:

- `INTERNAL_MODEL` agents;
- directly invoked by MSA orchestrator;
- can run live/bounded turns;
- each keeps its own identity, assignment, tools, and authority.

Federated participants:

- initially bound ChatGPT/MCP;
- asynchronous persisted work/review exchange;
- optional checkpoint/candidate/reviewer;
- not presented as a fake live participant that MSA can force to answer.

### REVIEW — first implementation priority

Default native-only example:

`Owner evidence/task -> ANALYST -> REVIEWER -> SYNTHESIZER -> WAITING_OWNER`

Optional federated example:

`Owner evidence/task -> ANALYST -> REVIEWER -> WAITING_EXTERNAL -> SYNTHESIZER -> WAITING_OWNER`

Review lifecycle:

`DRAFT -> REVIEWING -> WAITING_EXTERNAL? -> WAITING_OWNER -> APPROVED -> COMMITTABLE -> COMMITTED`

`WAITING_EXTERNAL` may be skipped. `APPROVED` is not a store mutation. Current production write gate still blocks real inventory mutation.

Stable orchestration roles are `ANALYST`, `REVIEWER`, `SYNTHESIZER`; presets may add custom display labels. Roles never grant authority.

### Shared coordination substrate

D4.8 requires durable:

- Work Items;
- versioned Artifacts;
- version-bound Reviews;
- immutable Events;
- shared Attention Queue.

Actor types distinguish at least `OWNER`, `USER`, `INTERNAL_AGENT`, `EXTERNAL_MCP_AGENT`, `SYSTEM`.

Artifacts/reviews are proposals/evidence/work products, **not committed store state**.

### Federated MCP workflow

After native Review substrate is proven, add bounded MCP operations to read eligible work items/artifacts/reviews and submit version-bound external reviews/proposals.

Direct MCP typed operations remain valid and independent; not every MCP operation must go through Multi-Agent review.

Internal agents also remain independent; external review is never mandatory unless preset/Owner explicitly requests it.

### Telegram attention layer

Telegram is planned as notification/lightweight attention delivery over the same persisted backend workflow state.

Use cases:

- internal review finished;
- external review requested;
- Owner decision required;
- disagreement/failure;
- commit completion.

Telegram is not the source of truth and not the orchestrator. Notification failure must not lose or advance workflow state.

Web Dashboard, ChatGPT/MCP, and Telegram should expose/signal the same Attention Queue.

Target convenience flow:

`native review ends -> WAITING_EXTERNAL -> Telegram notifies Owner -> Owner stays in ChatGPT -> MCP opens work item -> ChatGPT submits review -> MSA continues`

### GROUP

After REVIEW/federation substrate is stable, GROUP becomes a bounded shared-context native agentic loop. Owner can watch and later steer/pause/resume/stop. External agents may participate only through explicit asynchronous checkpoints initially.

COMPARE keeps participants independent until comparison. DEBATE uses bounded native rounds before synthesis.

## Next authorized order

1. Implement D4.8 DB/typed substrate: Work Items, Artifacts, Reviews, Events, Attention Queue.
2. Implement backend Owner-only native-only REVIEW execution using existing presets and attachment contract.
3. Add AI Workspace REVIEW UI + persisted progress/provenance + Owner re-review/steering.
4. Add optional federated `WAITING_EXTERNAL` + bounded MCP work/review actions.
5. Add Telegram notification adapter over Attention Queue/events; delivery failure must remain non-fatal to workflow correctness.
6. Add GROUP native bounded loops + Owner pause/resume/stop/steer + optional external checkpoint.
7. Add COMPARE and DEBATE execution.
8. Return to D4.7 live PRIMARY -> FALLBACK proof when a stable secondary model/provider is available.
9. Add per-user Chat entitlement/allowed-agent UI plus human/location tool-authority intersection before staff tool rollout.
10. Expand native typed tools and vision/OCR processors only through bounded typed workflows.

## Immediate D4.8 acceptance target

First Review slice passes when:

1. Owner can use a REVIEW preset containing native agents only;
2. backend enforces Owner-only execution;
3. task/evidence creates durable Work Item + versioned Artifact;
4. native participants execute in configured role/order with separate provenance;
5. no authority union occurs;
6. workflow reaches WAITING_OWNER without production mutation;
7. Owner can inspect versions/reviews and return work for re-review;
8. existing secured photo/file attachment contract is reused;
9. state survives reload/restart;
10. external ChatGPT/MCP is not required.

## Survival proof

`MSA Web -> selected INTERNAL_MODEL agent -> assigned provider/model -> authorized typed MSA read -> response + provenance`

This proof is already live and must remain independent of public MCP.
