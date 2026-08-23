# F7.2D4.8 — Multi-Agent Review, Federation & Attention Workflow

Status: **approved architecture contract; implementation not started**

Date: 2026-08-24

## Purpose

Define the first production-oriented Multi-Agent orchestration contract for Medicine Store Assistant while preserving the existing execution-path separation between native internal agents and external MCP agents.

The Multi-Agent workspace must support **native-only workflows by default**. External/federated participation is optional and is selected by the Owner in the session preset or requested later as an explicit checkpoint. No Review, Group, Compare, or Debate workflow requires an external agent to exist.

## Core participant model

### Native participants

Native participants are MSA `INTERNAL_MODEL` agents that the backend orchestrator can invoke directly.

They may participate in live/automatic turns because MSA controls their invocation lifecycle.

Each native participant retains its own:

- stable agent identity;
- provider/model/fallback assignment;
- capability grants;
- authority ceiling;
- location scope;
- execution and confirmation policy;
- tool-call provenance.

Session membership never unions participant privileges.

### Federated participants

Federated participants are external reasoning systems that are not directly controlled by the MSA native orchestrator, initially including the bound ChatGPT/MCP agent.

They participate asynchronously through persisted work/review artifacts and MCP actions rather than by pretending MSA can force a live ChatGPT turn.

Federated participation is **optional**.

Examples:

- ChatGPT reviews an issue-paper extraction prepared by native agents;
- ChatGPT submits a review packet created from vision/reasoning performed in the ChatGPT interface;
- ChatGPT reads an internal-agent work item via MCP, reviews it, then submits a version-bound external review;
- a Group workflow pauses at an explicit external checkpoint and resumes after the federated review arrives.

Future federated channels may reuse the same contract.

## Multi-Agent modes

### REVIEW — first implementation priority

REVIEW is the first production mode because it maps directly to real MSA workflows such as issue-paper intake, Daily Usage validation, stock transfer review, catalogue mapping, and reconciliation.

A preset may contain only native participants, for example:

`Analyst -> Reviewer -> Synthesizer -> Owner`

or may optionally include a federated checkpoint:

`Analyst -> Reviewer -> WAITING_EXTERNAL -> Synthesizer -> Owner`

External review is never mandatory unless the Owner explicitly configures the preset or requests it for a specific work item.

### GROUP

GROUP is a shared-context native agentic loop. Native participants can take bounded turns over a shared session thread while the Owner watches and may steer, pause, resume, or stop the session.

Federated agents are not live autonomous Group participants in the initial implementation. They may enter through explicit asynchronous checkpoints such as `WAITING_EXTERNAL`.

### COMPARE

Participants receive the same task independently and do not see one another's answer before their own result is committed to the comparison set. A federated submission may later be added as an optional comparison candidate.

### DEBATE

Native participants receive bounded roles/positions and exchange a limited number of argument/counterargument rounds before synthesis. Initial implementation may remain native-only. External checkpoints can be added later without changing the core work-item model.

## Review lifecycle

Keep the state machine compact and human-readable:

`DRAFT -> REVIEWING -> WAITING_EXTERNAL? -> WAITING_OWNER -> APPROVED -> COMMITTABLE -> COMMITTED`

Optional external review means `WAITING_EXTERNAL` may be skipped entirely.

### DRAFT

A work item exists with source evidence and/or an initial artifact, but review has not begun.

### REVIEWING

Configured native participants are analyzing, checking, revising, or synthesizing artifacts.

A reviewer may return the work item to another review turn without changing store state.

### WAITING_EXTERNAL

Optional state used only when a federated review is explicitly requested by preset or Owner action.

MSA persists the exact artifact version being requested for review and exposes it through bounded MCP reads. The external agent submits a review against that version.

### WAITING_OWNER

Automated/internal/federated review work is complete enough to require Owner attention, decision, clarification, or approval.

### APPROVED

Required review policy has passed. **APPROVED does not mean store data has changed.**

### COMMITTABLE

A typed mutation proposal has been constructed and all current authority, validation, confirmation, idempotency, and system-write-gate prerequisites for execution have passed.

### COMMITTED

The typed operation succeeded, committed read-back/audit evidence exists, and the work item records the resulting operation reference.

A rejected or needs-fix review returns to `REVIEWING` or `DRAFT` according to workflow semantics. Failed execution never silently becomes COMMITTED.

## Shared work/review substrate

Multi-Agent orchestration and MCP federation require a durable coordination layer rather than using chat text as the source of truth.

Initial concepts:

### Work Item

Represents the task being processed.

Examples: issue-paper intake, Daily Usage extraction, stock-transfer proposal, mapping review, reconciliation investigation.

Suggested fields include:

- `work_item_id`
- `work_type`
- `status`
- `title/objective`
- `created_by_actor_type`
- `created_by_actor_id`
- `source_channel`
- `session_id/preset_id` where relevant
- timestamps

### Artifact

Versioned evidence or work product attached to a work item.

Examples: extraction draft, proposed rows, analyst report, synthesis, attachment references, structured candidate mappings.

Suggested fields include:

- `artifact_id`
- `work_item_id`
- `artifact_type`
- `version`
- `actor_type`
- `actor_id`
- structured payload/reference
- timestamps

### Review

A version-bound review of an artifact or work item.

Suggested fields include:

- `review_id`
- `work_item_id`
- `artifact_id`
- reviewed artifact version
- reviewer actor type/id
- verdict/status
- notes / structured findings
- authority/correlation metadata
- timestamps

### Event

Immutable workflow timeline entry such as created, native-review-started, external-review-requested, external-review-received, owner-approved, commit-attempted, committed, failed, or returned-for-revision.

## Actor types

The shared substrate must distinguish at least:

- `OWNER`
- `USER`
- `INTERNAL_AGENT`
- `EXTERNAL_MCP_AGENT`
- `SYSTEM`

External ChatGPT/MCP participation is stored as an external actor with MCP/grant/binding/correlation provenance where available. It is not silently converted into an internal agent.

## Artifact safety invariant

**Artifact/review state is not committed inventory state.**

An internal or external agent may propose a serial code, extracted quantity, expiry date, transfer, or other operation. Persisting that proposal does not mutate canonical/store state.

Only an authorized typed operation may perform a real mutation after the applicable workflow reaches `COMMITTABLE` and the system write/canonicality gates permit it.

Current project boundaries still prohibit production inventory writes.

## MCP federation contract

External MCP gets bounded work-exchange operations, not arbitrary database access.

Future action families may include:

- list/read work items visible to the bound external agent;
- read versioned artifacts/evidence metadata;
- read review history and current status;
- submit external review against a specific artifact version;
- submit a proposed artifact/review packet;
- request internal review/re-review where policy allows;
- acknowledge/mark attention items.

Direct MCP operations remain valid peer operations. Federation does not force every MCP task through Multi-Agent review.

Likewise, internal agents do not require ChatGPT/MCP participation for normal native-only sessions.

## Telegram attention layer

Telegram is planned as a notification and lightweight human-attention channel over the same persisted workflow state.

Telegram is **not** the source of truth and is not the orchestrator.

Useful notifications include:

- internal review finished;
- external review requested;
- Owner decision required;
- workflow failed or needs clarification;
- commit completed;
- important disagreement/conflict detected.

Example:

`WI-104 — external review requested; 12 issue-paper rows extracted, 2 uncertain mappings.`

The Owner may remain in the ChatGPT interface and use MCP to open/review `WI-104` after receiving the Telegram notification.

Notification delivery failure must never lose workflow state. The work item remains visible through Web/MCP and can be rediscovered later.

## Shared attention queue

Web Dashboard, ChatGPT/MCP, and future Telegram should expose the same backend attention queue rather than maintaining separate channel-specific state.

Initial attention categories may include:

- waiting external review;
- waiting Owner review/approval;
- workflow failure;
- unresolved disagreement;
- completed work worth notifying.

## Review roles

Use a small stable set of orchestration roles plus optional Owner-defined labels.

System roles:

- `ANALYST` — produces/updates the primary artifact;
- `REVIEWER` — checks facts, assumptions, evidence, and policy;
- `SYNTHESIZER` — reconciles accepted findings into the next artifact/final recommendation.

A preset may omit roles it does not need and may apply custom labels such as `Stock Reviewer` or `Mapping Specialist` for display/context.

Roles do not grant authority.

## Owner steering

Owner-only Multi-Agent execution must support bounded steering controls over time, including pause/stop/resume and injecting a new Owner instruction into a running or waiting session.

Owner steering changes orchestration instructions, not participant authority.

## Security and authority

Owner-only Multi-Agent execution requires backend authorization in addition to UI restriction.

For every native tool call:

`effective_authority = system gate ∩ authenticated human/session authority ∩ calling agent capability/ceiling ∩ location scope ∩ operation class ∩ confirmation policy`

Privileges are never unioned across agents.

Federated submissions are evidence/review inputs. They do not inherit native-agent authority and do not bypass typed-operation authorization.

## Attachment reuse

REVIEW/GROUP/COMPARE/DEBATE reuse the existing AI Workspace photo/file attachment contract. Do not create a second upload system.

Attachments remain evidence. Future vision/OCR/extraction produces versioned artifacts before any controlled commit.

## Implementation order

1. Persist the work-item/artifact/review/event substrate and attention queue.
2. Wire Owner-only REVIEW mode with native-only presets first.
3. Add optional federated `WAITING_EXTERNAL` checkpoint + bounded MCP work/review actions.
4. Add Telegram notification delivery over persisted attention events; notification failure must not alter workflow correctness.
5. Add GROUP native shared-context loops with Owner steering and optional external checkpoints.
6. Add COMPARE and DEBATE semantics.
7. Expand attachment-driven typed workflows only after the substrate is stable.

## Acceptance principles

D4.8 architecture is satisfied only if:

1. a Review preset can be completely native-only;
2. external/federated review is optional and explicit;
3. native participants can execute without public MCP;
4. ChatGPT/MCP can read a bounded work item and submit a version-bound review when requested;
5. no external agent is represented as a fake live participant when MSA cannot directly invoke it;
6. APPROVED is separated from COMMITTABLE/COMMITTED;
7. work artifacts never mutate store state by themselves;
8. Owner-only Multi-Agent execution is enforced by the backend;
9. participant authorities are intersected independently and never unioned;
10. Telegram/Web/MCP may surface the same attention state without becoming separate sources of truth;
11. notification failure cannot lose or incorrectly advance a workflow;
12. existing non-canonical/test-only/write-gate boundaries remain unchanged.
