# F7.2D4.8 — Native REVIEW Runtime Checkpoint

Status: **backend + Owner REVIEW UI deployed; real end-to-end manual acceptance pending**

Date: 2026-08-24

## Scope

This checkpoint records the first executable D4.8 native-only REVIEW backend and browser UI. It builds on the shared Work Item / Artifact / Review / Event / Attention Queue substrate and preserves the canonical separation between native internal agents and external MCP agents.

## Merge and deployment anchors

- Substrate PR #100 merge: `4a9f54e17f2b386dfdd390af5850be2100986aac`
- Native REVIEW backend PR #101 merge: `0ebaba7d62f5cc3d9d3ec95e1cd33b4ccb7c324e`
- Native REVIEW UI PR #103 merge: `c980446a7df27a352721115599a5ecf704797097`
- backend deploy run: `32660149646`
- UI deploy run: `32660684770`
- latest deployed source SHA: `c980446a7df27a352721115599a5ecf704797097`
- VPS deploy status: `success`

## Implemented substrate

Production-oriented persistence includes:

- `workflow_work_items`
- `workflow_artifacts`
- `workflow_reviews`
- `workflow_events`
- `workflow_attention_items`

The compact lifecycle remains:

`DRAFT -> REVIEWING -> WAITING_EXTERNAL? -> WAITING_OWNER -> APPROVED -> COMMITTABLE -> COMMITTED`

`APPROVED` remains review state only and cannot transition directly to `COMMITTED`.

## Stable orchestration roles

Migration `0021_review_orchestration_roles` stores stable role bindings separate from presentation labels:

- `ANALYST`
- `REVIEWER`
- `SYNTHESIZER`

Owner-defined display labels remain presentation/context only and never become authority.

## Native-only REVIEW execution

Owner-only backend APIs support:

- assigning/reading stable orchestration roles for an open REVIEW preset;
- starting a native REVIEW work item;
- listing recent Owner REVIEW work items for reload/recovery;
- reading Work Item, Artifacts, Reviews, Events, and Attention state;
- returning `WAITING_OWNER` work to `REVIEWING` with an Owner revision instruction.

Initial flow:

`Owner task -> DRAFT -> REVIEWING -> ordered native participants -> WAITING_OWNER`

Each participant must currently be an ACTIVE `INTERNAL_MODEL` agent. External MCP participation is not required and is not invoked by this runtime.

## Owner REVIEW UI

The deployed AI Workspace Multi-Agent tab now exposes the real REVIEW slice rather than a fake/future composer.

Current UI supports:

- open REVIEW preset selection;
- stable ANALYST / REVIEWER / SYNTHESIZER role configuration;
- optional custom display labels;
- Work title + Owner task submission;
- optional reference to existing ownership-validated Chat attachment evidence;
- native REVIEW execution;
- reload-safe Recent Review work list;
- Work Item detail with Artifacts, exact-version Reviews, Attention and Event timeline;
- provider/model/fallback/latency provenance display;
- WAITING_OWNER return-for-revision control;
- explicit `Production mutation: NO` / non-canonical messaging.

GROUP, COMPARE, and DEBATE remain clearly deferred and are not presented as active fake controls.

## Browser release integrity

The REVIEW UI uses dedicated assets:

- `dashboard_multi_agent_review.js`
- `dashboard_multi_agent_review.css`

Current asset version key:

`f72d48-review-ui-1`

Dashboard HTML generation references that exact version. Asset responses remain `Cache-Control: no-store, max-age=0` with compatible no-cache headers.

PR #103 CI validated:

- real FastAPI REVIEW route surface;
- reload-safe work-item list route;
- JavaScript syntax;
- key REVIEW UI controls;
- responsive CSS contract;
- exact asset version reference and stale-marker guard;
- broad backend/native-runtime/access/MCP regression suites.

Issue #26 then recorded successful deployment of merge `c980446a7df27a352721115599a5ecf704797097` via workflow run `32660684770`.

## Participant isolation and provenance

Each participant is invoked independently through the existing native provider-backed runtime. Session membership does not union participant authority.

Persisted participant provenance includes selected provider/model, fallback status, latency, and bounded attempt metadata.

Reviewer output is persisted as a Review bound to the exact prior artifact ID/version used as its review target.

### Current native-tool boundary

The first REVIEW executor currently uses the plain native provider invocation path. It does **not yet enter the model-driven native read-tool loop** used by AI Workspace Chat.

Therefore the first manual REVIEW acceptance must be treated as a **provided-evidence/native-reasoning Review**. Do not claim that REVIEW participants independently executed current MSA read tools until a later bounded hardening slice explicitly integrates the tool loop with per-participant READ authority checks.

When that hardening is implemented, tool visibility/execution must remain independently gated per participant; session membership must never union tool authority.

## Attachment reuse

The REVIEW start contract can reference existing AI Workspace attachments by conversation/attachment ID. The backend validates Owner ownership and persists bounded attachment metadata references in the Owner task artifact.

No second upload system was created.

Attachment bytes are still not supplied to provider vision/OCR. The Work Item records attachment processing as `NOT_PROCESSED`.

## Failure and attention state

Native participant invocation failure moves the Work Item to `FAILED`, records a workflow event, and creates durable Owner attention.

Successful native REVIEW ends at `WAITING_OWNER` and creates a durable `WAITING_OWNER` attention item.

Notification delivery is not involved in workflow correctness.

## Security/canonicality boundaries

Unchanged:

- Multi-Agent execution is Owner-only in this phase.
- Production inventory writes remain disabled.
- PostgreSQL remains non-canonical.
- F6B remains test-only.
- Artifacts/Reviews do not mutate store state.
- No MCP schema/action-name change was required.
- External/federated review remains a later optional checkpoint.

## Current acceptance boundary

Backend + UI + deployment evidence are complete, but the full first REVIEW acceptance target is **not yet complete** because a real configured native-only REVIEW run has not yet been manually inspected through the Owner UI.

Do not mark D4.8 REVIEW verified until a real run:

1. uses a native-only REVIEW preset;
2. reaches `WAITING_OWNER`;
3. shows ordered participant Artifacts + exact-version Review records + provenance;
4. survives browser reload through the Recent Review work list;
5. can be returned to `REVIEWING` with a persisted revision instruction;
6. demonstrates no inventory mutation;
7. does not require ChatGPT/MCP.

## Next authorized work

1. Manually accept one provided-evidence/native-reasoning REVIEW run through the deployed Owner UI.
2. If the UI/runtime behavior is accepted, add bounded per-participant native read-tool integration as a Review hardening sub-slice before relying on Review for current-store operational reasoning.
3. Only after native REVIEW is proven, add optional federated `WAITING_EXTERNAL` MCP work/review exchange.
4. Telegram Attention delivery remains later and must never become the source of truth.
