# F7.2D4.9 — Review Thread Conversation and Owner Decisions

Status: **DEPLOYED / PRODUCTION ACCEPTED**

Production anchor: PR #127 merge/source `c2dc42b38a60a7dc625c0d0748530c74c98ed615`; issue #26 `status=success`; deploy run `32735227026`.

## Purpose

Evolve Multi-Agent Review from a one-pass review viewer into a durable Owner + agent decision room without weakening the existing Review workflow, authority boundaries, or canonicality gates.

## Locked interaction semantics

### 1. Normal Send = conversational continuation

A normal Owner composer send is not a passive note and is not a structured Review pass.

`Owner message -> target resolution -> one authorized native participant turn -> persisted participant reply`

The message and reply remain inside the same durable Review Work Item/thread.

Targeting rules:

- explicit participant selection targets that active native participant;
- if no explicit target is supplied, prefer the configured `SYNTHESIZER`;
- if there is no Synthesizer, use the last configured active participant;
- unknown/ambiguous explicit targets fail closed rather than silently routing elsewhere.

A conversational turn does **not** consume pending external-review feedback and does **not** run the whole Review preset.

### 2. Send review = structured multi-agent pass

`pending/new structured feedback or direct Owner review instruction -> configured REVIEW preset in order -> persisted outputs -> WAITING_OWNER`

`Send review` remains the explicit operation for running the full configured Review team. It is not triggered by ordinary conversation sends.

The Review composer can submit its current text directly as the structured Owner instruction; ordinary discussion messages do not need to be staged merely to make Review actionable.

### 3. Owner Decision = durable authority-bearing evidence, not mutation

The Owner can record a final/intermediate decision as a dedicated `OWNER_DECISION` artifact plus immutable event.

Examples include accepting an option, keeping an item unresolved, requiring manual mapping, rejecting a recommendation, or approving a future execution plan subject to later confirmation.

Recording a decision does **not** mutate inventory, does not make PostgreSQL canonical, and does not by itself grant an agent write authority.

### 4. Future execution chain

The intended later chain is:

`evidence -> agent discussion/review -> Owner decision -> executor agent prepares typed mutation proposal -> required Owner confirmation -> authorized typed backend operation -> read-back -> audit`

Agents must never receive arbitrary SQL/direct DB mutation merely because they are selected as executor. Provider/model choice never grants authority. Future execution remains inside typed operation + authority-intersection + confirmation policy.

## Persistence contract

Use the existing Work/Artifact/Event substrate; D4.9 required no schema migration.

- `OWNER_MESSAGE`: ordinary conversational Owner turn; `staged_for_review=false` for direct discussion.
- `PARTICIPANT_OUTPUT`: native participant discussion reply; payload marks `discussion_turn=true`, reply linkage and provenance.
- `OWNER_DECISION`: durable Owner decision; payload records the decision and explicit no-mutation state.
- Events: `OWNER_DISCUSSION_MESSAGE_SENT`, `NATIVE_DISCUSSION_TURN_COMPLETED`, `NATIVE_DISCUSSION_TURN_FAILED`, `OWNER_DECISION_RECORDED`.

No new inventory mutation primitive is introduced.

## Context contract

A targeted participant receives bounded persisted Review-thread context: original Owner task, prior participant outputs, external reviews, Owner discussion messages, Owner feedback/revisions, and Owner decisions. The current Owner message is clearly marked as the immediate request.

External MCP reviews remain evidence only. They never grant authority.

## UI contract

Within the existing authoritative Multi-Agent Review renderer:

- normal Send invokes the one-participant conversational continuation endpoint;
- the composer exposes deterministic participant targeting/default routing;
- `Send review` stays separate and runs the configured full Review pass;
- `Record decision` persists durable Owner decisions;
- Owner messages, discussion replies and Owner decisions rehydrate chronologically;
- discussion replies are not promoted to the latest structured Review artifact for external-review freezing;
- no second renderer or DOM owner is introduced.

## Production implementation

Backend module: `backend/app/multi_agent_review_discussion.py`.

Endpoints:

- `GET /dashboard/api/ai-workspace/multi-agent/work-items/{work_item_id}/discussion-targets`
- `POST /dashboard/api/ai-workspace/multi-agent/work-items/{work_item_id}/discussion-turn`
- `POST /dashboard/api/ai-workspace/multi-agent/work-items/{work_item_id}/decisions`

The discussion endpoint invokes exactly one target through the existing native participant runtime/tool-authority path and persists both Owner and participant evidence. Participant invocation failure is logged as a discussion failure without falsely converting the whole Review Work Item into a completed full-preset pass.

## Acceptance evidence

PR-head relevant workflows were 7/7 green. The Playwright Chromium 390×844 behavior smoke proves:

1. structured external feedback is consumed by `Send review` and settles correctly;
2. normal Send targets exactly one selected participant and does not call `feedback-pass`;
3. discussion reply persists visibly in-thread;
4. Owner Decision persists without calling `feedback-pass` or mutating inventory;
5. direct typed Owner instruction independently enables the structured full Review pass;
6. composer-side exports continue to reuse the existing export endpoints.

The first browser run also found a real target-selector re-render bug: a Work Item-level target-load cache outlived the replaced select DOM node. The accepted implementation binds hydration state to the live select node, so re-render/reopen produces a fresh deterministic target list.

## Boundaries

- Owner-only for this phase.
- Native internal participants only for direct discussion turns.
- No production inventory writes.
- No PostgreSQL canonical promotion.
- No raw DB/SQL authority to agents.
- Telegram Attention delivery follows as a separate bounded slice.