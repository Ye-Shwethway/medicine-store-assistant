# F7.2D4.8 — Native REVIEW Runtime Checkpoint

Status: **merged; deployment evidence pending at document creation**

Date: 2026-08-24

## Scope

This checkpoint records the first executable D4.8 native-only REVIEW backend slice. It builds on the shared Work Item / Artifact / Review / Event / Attention Queue substrate and preserves the canonical separation between native internal agents and external MCP agents.

## Merge anchors

- Substrate PR #100 merge: `4a9f54e17f2b386dfdd390af5850be2100986aac`
- Native REVIEW PR #101 merge: `0ebaba7d62f5cc3d9d3ec95e1cd33b4ccb7c324e`

## Implemented substrate

Production-oriented persistence now includes:

- `workflow_work_items`
- `workflow_artifacts`
- `workflow_reviews`
- `workflow_events`
- `workflow_attention_items`

The compact lifecycle remains:

`DRAFT -> REVIEWING -> WAITING_EXTERNAL? -> WAITING_OWNER -> APPROVED -> COMMITTABLE -> COMMITTED`

`APPROVED` remains review state only and cannot transition directly to `COMMITTED`.

## Stable orchestration roles

Migration `0021_review_orchestration_roles` adds stable role bindings separate from presentation labels:

- `ANALYST`
- `REVIEWER`
- `SYNTHESIZER`

The role binding is stored separately from existing session `role_label` so Owner-defined display labels do not become authority or orchestration semantics.

## Native-only REVIEW execution

Owner-only backend APIs now support:

- assigning/reading stable orchestration roles for an open REVIEW preset;
- starting a native REVIEW work item;
- reading the resulting Work Item, Artifacts, Reviews, Events, and Attention state;
- returning `WAITING_OWNER` work to `REVIEWING` with an Owner revision instruction.

Initial execution flow:

`Owner task -> DRAFT -> REVIEWING -> ordered native participants -> WAITING_OWNER`

Each participant must currently be an ACTIVE `INTERNAL_MODEL` agent. External MCP participation is not required and is not invoked by this runtime.

## Participant isolation and provenance

Each participant is invoked independently through the existing native provider-backed runtime. Session membership does not union participant authority.

Persisted participant provenance includes the selected provider/model, fallback status, latency, and bounded attempt metadata already returned by the native runtime.

Reviewer output is persisted as a Review bound to the exact prior artifact ID/version used as its review target.

## Attachment reuse

The REVIEW start contract can reference existing AI Workspace attachments by conversation/attachment ID. The backend validates Owner ownership and persists only bounded attachment metadata references in the Owner task artifact.

No second upload system was created.

Attachment bytes are still not supplied to provider vision/OCR in this slice. The work item explicitly records attachment processing as `NOT_PROCESSED`.

## Failure and attention state

Native participant invocation failure moves the Work Item to `FAILED`, records a workflow event, and creates a durable Owner attention item.

Successful native REVIEW ends at `WAITING_OWNER` and creates a durable `WAITING_OWNER` attention item.

Notification delivery is not involved in workflow correctness.

## Security/canonicality boundaries

Unchanged:

- Multi-Agent execution is Owner-only in this phase.
- Production inventory writes remain disabled.
- PostgreSQL remains non-canonical.
- F6B remains test-only.
- Artifacts/Reviews do not mutate store state.
- No MCP schema/action-name change was made.
- External/federated review remains a later optional checkpoint.

## CI evidence

PR #101 passed:

- Validate AI Workspace Chat
- Validate backend changes
- Validate MCP agent binding
- Validate MCP audit proof
- Validate saved model catalog

The API/migration validation imports the real FastAPI app and verifies the D4.8 route surface plus the `0020 -> 0021` migration chain.

## Next authorized work

1. Confirm automatic VPS deployment of merge `0ebaba7d62f5cc3d9d3ec95e1cd33b4ccb7c324e` and migration head `0021_review_orchestration_roles`.
2. Add the Owner-facing AI Workspace REVIEW UI for preset selection, role configuration, task submission, progress/provenance, Work Item inspection, and revision/re-review controls.
3. Manually accept a real native-only REVIEW run that reaches `WAITING_OWNER` with durable reload-safe evidence and no inventory mutation.
4. Only after native REVIEW is proven, add optional federated `WAITING_EXTERNAL` MCP work/review exchange.
5. Telegram Attention delivery remains later and must never become the source of truth.
