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
11. `docs/checkpoints/F7_2D48_NATIVE_REVIEW_RUNTIME_2026-08-24.md`
12. `docs/checkpoints/F7_2D4F_GROUNDED_NATIVE_READS_PLAN_2026-08-23.md`
13. `docs/checkpoints/F7_2D4G_CHAT_UX_LIFECYCLE_PLAN_2026-08-23.md`
14. `docs/checkpoints/F7_2D47_FALLBACK_MANAGEMENT_PLAN_2026-08-23.md`
15. `docs/checkpoints/F7_2D47A_NATIVE_TOOL_CALLING_PLAN_2026-08-23.md`
16. `docs/checkpoints/F7_2D47B_RESPONSE_AND_ATTACHMENTS_PLAN_2026-08-24.md`
17. current runtime/deployment evidence, especially issue #26
18. `docs/design/UI_UX_PRO_MAX_INTEGRATION.md` and `docs/design/WEB_ASSET_RELEASE_INTEGRITY.md` for Web work

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

Deployed D4.8 backend state, not yet fully manually accepted:

- Work Item / Artifact / Review / Event / Attention Queue substrate;
- stable `ANALYST`, `REVIEWER`, `SYNTHESIZER` role bindings separate from custom labels;
- Owner-only native REVIEW execution through ACTIVE `INTERNAL_MODEL` participants;
- exact prior-artifact/version binding for reviewer records;
- durable provider/model/fallback/latency provenance;
- durable WAITING_OWNER and workflow-failure attention state;
- Owner return-for-revision transition and persisted revision instruction.

## D4.8 deployment anchors

- PR #100 substrate merge: `4a9f54e17f2b386dfdd390af5850be2100986aac`
- PR #101 native REVIEW merge: `0ebaba7d62f5cc3d9d3ec95e1cd33b4ccb7c324e`
- production migration head: `0021_review_orchestration_roles`
- issue #26 deployment: `status=success`, workflow run `32660149646`, source SHA `0ebaba7d62f5cc3d9d3ec95e1cd33b4ccb7c324e`

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

Accepted current state includes human-friendly presentation with retained provenance, bounded attachment persistence, image previews, dynamic latest-message conversation cards, and explicit no-vision/OCR boundaries. Multi-Agent reuses the same attachment ownership/evidence contract rather than creating a second upload system.

## Current work — D4.8 Multi-Agent Review + federation

Canonical architecture: `docs/architecture/F7_2D48_MULTI_AGENT_REVIEW_AND_FEDERATION.md`.

Runtime checkpoint: `docs/checkpoints/F7_2D48_NATIVE_REVIEW_RUNTIME_2026-08-24.md`.

### Critical invariant

**External/federated participation is OPTIONAL.** A Multi-Agent preset must be able to run fully native with internal agents only. Do not require ChatGPT/MCP for Review, Group, Compare, or Debate.

### Current deployed REVIEW backend

Native-only target flow:

`Owner evidence/task -> DRAFT -> REVIEWING -> ordered native participants -> WAITING_OWNER`

Canonical lifecycle:

`DRAFT -> REVIEWING -> WAITING_EXTERNAL? -> WAITING_OWNER -> APPROVED -> COMMITTABLE -> COMMITTED`

`WAITING_EXTERNAL` may be skipped. `APPROVED` is not a store mutation. Current production write gate still blocks real inventory mutation.

Stable orchestration roles `ANALYST`, `REVIEWER`, `SYNTHESIZER` are deployed separately from Owner-defined display labels. Roles never grant authority.

The backend now persists Work Items, versioned Artifacts, exact-version Reviews, Events, and Attention items. Each native participant executes through its own INTERNAL_MODEL identity/provider assignment; session privileges never union. Existing attachment metadata references are ownership-validated and marked `NOT_PROCESSED` for vision/OCR in this slice.

Successful execution ends at `WAITING_OWNER`; failures create `FAILED` + Owner attention. Owner can return WAITING_OWNER work to REVIEWING with a persisted revision instruction.

### Current acceptance gap

Do **not** call D4.8 REVIEW fully verified yet. The Owner-facing Multi-Agent REVIEW UI is still missing, and a real configured native-only REVIEW run has not yet been manually inspected/accepted through reload-safe persisted state.

### Federated MCP workflow — AFTER NATIVE REVIEW ACCEPTANCE

External ChatGPT/MCP remains asynchronous and optional. First try to reuse existing v2.1 long-lived MCP tools with open `action: str` selectors + backend allowlists for bounded work/review exchange and exact artifact-version review binding. Do not create a separate MCP backend server. Introduce new MCP tool names/schema only if the existing long-lived slots cannot express the required bounded contract.

Direct MCP typed operations remain peer operations; not every MCP operation goes through Multi-Agent review.

### Telegram attention layer

Telegram is future notification/lightweight attention delivery over the same persisted backend state. It is not the source of truth or orchestrator. Notification failure must never lose or advance workflow state.

### GROUP / COMPARE / DEBATE

GROUP follows REVIEW/federation acceptance and is a bounded native shared-context loop with Owner steering. COMPARE preserves independent answers until comparison. DEBATE uses bounded native rounds before synthesis.

## Next authorized order

1. Build the Owner-facing AI Workspace REVIEW UI over the deployed backend: preset selection, stable role configuration, task/evidence submission, progress/provenance, Work Item detail, and return-for-revision.
2. Manually accept a real native-only REVIEW run reaching WAITING_OWNER; inspect durable artifacts/reviews/provenance after reload and prove no inventory mutation.
3. Add optional federated `WAITING_EXTERNAL` + bounded MCP work/review exchange using existing open-selector slots when sufficient.
4. Add Telegram notification adapter over Attention Queue/events; delivery failure remains non-fatal to workflow correctness.
5. Add GROUP native bounded loops + Owner pause/resume/stop/steer + optional external checkpoint.
6. Add COMPARE and DEBATE execution.
7. Return to D4.7 live PRIMARY -> FALLBACK proof when a stable secondary model/provider is available.
8. Add per-user Chat entitlement/allowed-agent UI plus human/location tool-authority intersection before staff tool rollout.
9. Expand native typed tools and vision/OCR processors only through bounded typed workflows.

## Immediate D4.8 acceptance target

First Review slice passes only when:

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

## Immediate boundary

Proceed with **D4.8 Owner REVIEW UI -> real native-only manual acceptance**. External federation and Telegram come only after native Review is proven. Production inventory writes and canonical DB promotion remain unauthorized.
