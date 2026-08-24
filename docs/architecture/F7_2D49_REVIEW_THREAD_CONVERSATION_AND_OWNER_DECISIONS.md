# F7.2D4.9 — Review Thread Conversation and Owner Decisions

Status: **ACTIVE BOUNDED SLICE**

## Purpose

Evolve Multi-Agent Review from a one-pass review viewer into a durable Owner + agent decision room without weakening the existing Review workflow, authority boundaries, or canonicality gates.

## Locked interaction semantics

### 1. Normal Send = conversational continuation

A normal Owner composer send is not a passive note and is not a structured Review pass.

`Owner message -> target resolution -> one authorized native participant turn -> persisted participant reply`

The message and reply remain inside the same durable Review Work Item/thread.

Targeting rules for this bounded slice:

- explicit `@call_name` targets that active native participant;
- if no explicit target is supplied, prefer the configured `SYNTHESIZER`;
- if there is no Synthesizer, use the last configured active participant;
- unknown/ambiguous explicit targets fail closed rather than silently routing elsewhere.

A conversational turn does **not** consume pending external-review feedback and does **not** run the whole Review preset.

### 2. Send review = structured multi-agent pass

`pending/new feedback or explicit Owner review instruction -> configured REVIEW preset in order -> persisted outputs -> WAITING_OWNER`

`Send review` remains the explicit operation for running the full configured Review team. It must not be triggered by ordinary conversation sends.

The Review composer may submit its current text directly as the structured Owner instruction; ordinary discussion messages do not need to be staged merely to make Review actionable.

### 3. Owner Decision = durable authority-bearing evidence, not mutation

The Owner can record a final/intermediate decision as a dedicated `OWNER_DECISION` artifact plus immutable event.

Examples:

- accept option B;
- keep a row unresolved;
- require manual mapping;
- reject a recommendation;
- approve a future execution plan subject to later confirmation.

Recording a decision does **not** mutate inventory, does not make PostgreSQL canonical, and does not by itself grant an agent write authority.

### 4. Future execution chain

The intended later chain is:

`evidence -> agent discussion/review -> Owner decision -> executor agent prepares typed mutation proposal -> required Owner confirmation -> authorized typed backend operation -> read-back -> audit`

Agents must never receive arbitrary SQL/direct DB mutation merely because they are selected as executor. Provider/model choice never grants authority. Future execution must remain inside typed operation + authority-intersection + confirmation policy.

## Persistence contract

Use the existing Work/Artifact/Event substrate.

- `OWNER_MESSAGE`: ordinary conversational Owner turn; `staged_for_review=false` for direct discussion.
- `PARTICIPANT_OUTPUT`: native participant discussion reply; payload marks `discussion_turn=true`, target identity and provenance.
- `OWNER_DECISION`: durable Owner decision; payload contains decision text and optional status metadata.
- Events: `OWNER_DISCUSSION_MESSAGE_SENT`, `NATIVE_DISCUSSION_TURN_COMPLETED`, `OWNER_DECISION_RECORDED`.

No new inventory mutation primitive is introduced in this slice.

## Context contract

A targeted participant receives bounded persisted Review-thread context: original Owner task, prior participant outputs, external reviews, Owner discussion messages, Owner feedback/revisions, and Owner decisions. The current Owner message is clearly marked as the immediate request.

External MCP reviews remain evidence only. They never grant authority.

## UI contract

Within the existing authoritative Multi-Agent Review renderer:

- normal Send invokes the conversational continuation endpoint;
- composer gives a concise targeting hint (`@call_name`; no mention -> Synthesizer/default participant);
- `Send review` stays separate and runs the configured full Review pass;
- provide a distinct `Record decision` action for durable Owner decisions;
- persist and rehydrate Owner messages, participant discussion replies, and Owner decisions in chronological thread order;
- do not add a second renderer or DOM owner.

## Acceptance

Bounded tests must prove:

1. normal Send invokes exactly one targeted/default native participant and persists both turns;
2. normal Send does not call/start `feedback-pass`;
3. explicit valid `@call_name` routes to that participant;
4. invalid explicit target fails closed;
5. `Send review` remains a separate full-preset operation and can use direct Owner instruction text;
6. `Record decision` creates durable `OWNER_DECISION` + event and no inventory mutation;
7. refresh/reopen rehydrates discussion replies and decisions;
8. existing external-review, Review-send-state, export, delete and Web reliability behavior remains intact.

## Boundaries

- Owner-only for this phase.
- Native internal participants only for direct discussion turns.
- No production inventory writes.
- No PostgreSQL canonical promotion.
- No raw DB/SQL authority to agents.
- Telegram attention delivery moves behind this collaboration-semantic slice.