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

Production/manual accepted foundations include named AI Agent Management and policy, Provider Registry + tested saved models, PRIMARY + ordered FALLBACK configuration, MCP-independent native inference, server-owned identity injection, durable AI Workspace Chat, bounded native reads, D4.7A model-driven native read tools, D4.7B response/attachment UX, and independent external MCP read/audit access.

Current native read-tool registry:

- `inventory_summary`
- `new_unmapped_rows`
- `review_reasons`

Production inventory writes remain disabled.

## D4.8 deployment anchors

- PR #100 shared substrate merge: `4a9f54e17f2b386dfdd390af5850be2100986aac`
- PR #101 native REVIEW backend merge: `0ebaba7d62f5cc3d9d3ec95e1cd33b4ccb7c324e`
- PR #103 Owner REVIEW UI merge: `c980446a7df27a352721115599a5ecf704797097`
- production migration head: `0021_review_orchestration_roles`
- backend deploy run: `32660149646`
- UI deploy run: `32660684770`
- latest issue #26 deployment: `status=success`, source SHA `c980446a7df27a352721115599a5ecf704797097`
- REVIEW UI asset version: `f72d48-review-ui-1`

## AI Workspace architecture — LOCKED

### AI Agent Management — Owner-only control plane

Contains agent lifecycle/policy, provider/model/fallback assignments, reusable multi-agent session definitions, and global non-owner AI Workspace access setting.

Owner-only requires backend authorization plus UI restriction.

### AI Workspace — work plane

- `Chat` — one selected internal agent; Owner + authorized users.
- `Multi-Agent` — `REVIEW`, `GROUP`, `COMPARE`, `DEBATE`; Owner-only in this phase.
- REVIEW is the only executable Multi-Agent mode currently exposed. GROUP / COMPARE / DEBATE remain later slices and must not be presented as fake active controls.
- Chat and Multi-Agent reuse the same photo/file attachment ownership/evidence architecture.

## Access + authority

Owner always has AI Workspace access. Global OFF hard-blocks non-owner Chat before provider calls. Per-user entitlement foundation is `INHERIT | ALLOW | BLOCK`.

Native tool authority is an intersection:

`system gate ∩ authenticated human/session authority ∩ calling agent capability/ceiling ∩ location scope ∩ operation class ∩ confirmation policy`

Never union privileges. Provider/model assignment never grants authority.

## D4.7A native tool calling — VERIFIED

AI Workspace Chat has an accepted bounded native read-tool loop. Explicit requests may use deterministic prefetch; contextual/ambiguous requests may use model-driven tools when the assigned model supports them. Public MCP is not used. Tool execution is backend-allowlisted and currently read-only.

## D4.7B response + attachments — VERIFIED / ACCEPTED

Chat supports human-friendly responses, bounded ownership-scoped photo/file evidence, previews, remove-before-send, durable binding and reload behavior. Attachment bytes are still not supplied to provider vision/OCR.

## Current work — D4.8 Multi-Agent Review + federation

Canonical architecture: `docs/architecture/F7_2D48_MULTI_AGENT_REVIEW_AND_FEDERATION.md`.

Runtime checkpoint: `docs/checkpoints/F7_2D48_NATIVE_REVIEW_RUNTIME_2026-08-24.md`.

### Critical invariant

**External/federated participation is OPTIONAL.** A Multi-Agent preset must be able to run fully native with internal agents only. Do not require ChatGPT/MCP for Review, Group, Compare, or Debate.

### Deployed shared substrate

The production-oriented D4.8 coordination layer persists:

- Work Items;
- versioned Artifacts;
- exact-version Reviews;
- immutable Events;
- shared Attention items.

Actor types distinguish `OWNER`, `USER`, `INTERNAL_AGENT`, `EXTERNAL_MCP_AGENT`, and `SYSTEM`.

Artifact/review persistence is not committed inventory state and never mutates inventory by itself.

### Deployed native REVIEW

Canonical lifecycle:

`DRAFT -> REVIEWING -> WAITING_EXTERNAL? -> WAITING_OWNER -> APPROVED -> COMMITTABLE -> COMMITTED`

The current native-only executable flow is:

`Owner evidence/task -> DRAFT -> REVIEWING -> ordered native participants -> WAITING_OWNER`

Stable roles `ANALYST`, `REVIEWER`, `SYNTHESIZER` are stored separately from Owner-defined display labels. Roles do not grant authority.

Each active participant must currently be an `INTERNAL_MODEL` agent. Participants execute independently with separate provider/model/fallback/latency provenance. Reviewer records bind to the exact prior Artifact ID/version. Success creates durable `WAITING_OWNER` attention; participant failure creates `FAILED` + durable Owner attention. Owner can return WAITING_OWNER work to REVIEWING with a persisted revision instruction.

### Deployed Owner REVIEW UI

The AI Workspace Multi-Agent tab now provides:

- open REVIEW preset selection;
- stable ANALYST / REVIEWER / SYNTHESIZER configuration with optional display labels;
- Work title + Owner task composer;
- optional references to saved ownership-validated Chat attachments;
- native REVIEW execution;
- reload-safe Recent Review Work Items;
- Work Item detail with Artifacts, exact-version Reviews, provider/model/fallback/latency provenance, Attention state and Event timeline;
- WAITING_OWNER return-for-revision;
- explicit production-mutation-NO and DB-non-canonical messaging.

Dedicated UI assets use version `f72d48-review-ui-1`, are wired into the dashboard entrypoint, and remain no-store/no-cache under the Web release-integrity contract.

### Current REVIEW tool boundary — IMPORTANT

The deployed first REVIEW executor currently uses the **plain native provider invocation path**, not the D4.7A model-driven native read-tool loop.

Therefore the next manual acceptance is explicitly a **provided-evidence/native-reasoning REVIEW**. Do not claim that REVIEW participants independently read current MSA state through native tools yet.

Before relying on Review for current-store operational conclusions, implement a bounded hardening slice that integrates the existing native read tools per participant only when that participant independently passes READ capability/authority checks. Session membership must never union tool authority.

### Current manual acceptance gap

Do **not** mark D4.8 REVIEW fully verified yet. Backend, UI, CI and deployment are complete, but one real Owner browser run still must prove:

1. native-only REVIEW preset;
2. stable role saving;
3. durable Work Item + Artifacts;
4. configured execution order + separate provenance;
5. `WAITING_OWNER` result without inventory mutation;
6. exact-version Review records visible;
7. browser reload rediscovers the same Work Item;
8. return-for-revision persists an Owner instruction and moves state to REVIEWING;
9. ChatGPT/MCP is not required;
10. attachment evidence accurately remains metadata-only / no vision-OCR processing.

### Federation — AFTER NATIVE REVIEW ACCEPTANCE

External ChatGPT/MCP remains asynchronous and optional. First attempt to reuse existing MCP v2.1 long-lived tools with open `action: str` selectors + backend allowlists for bounded work/review exchange and exact artifact-version binding. Do not create a separate MSA MCP backend server. Add new tool names/schema only if existing long-lived slots cannot express the required bounded contract.

Direct MCP typed operations remain valid peer operations; not every MCP task goes through Multi-Agent review.

### Telegram attention layer

Telegram remains future notification/lightweight attention delivery over the same persisted backend state. It is not the source of truth or orchestrator. Notification failure must never lose or advance workflow state.

### GROUP / COMPARE / DEBATE

GROUP follows Review/federation acceptance and becomes a bounded native shared-context loop with Owner steering. COMPARE preserves independent answers until comparison. DEBATE uses bounded native rounds before synthesis.

## Next authorized order

1. **CURRENT:** manually accept one provided-evidence/native-reasoning REVIEW through the deployed Owner UI.
2. Add bounded per-participant D4.7A native read-tool integration for REVIEW.
3. Manually accept one tool-using REVIEW before relying on Multi-Agent for current-store operational conclusions.
4. Add optional federated `WAITING_EXTERNAL` + bounded MCP work/review exchange with exact artifact-version binding, preferring existing v2.1 open-selector slots.
5. Add Telegram notification adapter over Attention Queue/events; delivery failure remains non-fatal to workflow correctness.
6. Add GROUP native bounded loops + Owner pause/resume/stop/steer + optional external checkpoint.
7. Add COMPARE and DEBATE execution.
8. Return to D4.7 live PRIMARY -> FALLBACK proof when a stable secondary model/provider is available.
9. Add per-user Chat entitlement/allowed-agent UI plus human/location tool-authority intersection before staff tool rollout.
10. Expand vision/OCR and controlled-write workflows only through later explicit bounded slices.

## Immediate boundary

Proceed with **one provided-evidence native-only REVIEW manual acceptance -> bounded per-participant native read-tool hardening**. External federation and Telegram come only after native Review is proven. Production inventory writes and canonical DB promotion remain unauthorized.
