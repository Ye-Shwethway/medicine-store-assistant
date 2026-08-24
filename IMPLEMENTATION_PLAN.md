# Medicine Store Assistant — Implementation Plan

Status: **D4.8 Review/federation and PR #125 Review/composer UX are production-verified. F6B remains test-only; PostgreSQL remains non-canonical. Current bounded slice: D4.9 Multi-Agent conversational continuation + durable Owner Decision semantics.**

This file is the execution contract for current MSA implementation order and boundaries.

## 1. Global rules

- Google Sheets/source documents remain operationally authoritative until explicit F11 promotion.
- PostgreSQL being deployed does **not** make it canonical.
- F6B remains test-only and must never be silently promoted.
- All humans, AI agents, integrations, and system jobs use typed backend operations.
- Never expose arbitrary SQL, DB credentials, VPS shell/filesystem, Sheet credentials, plaintext provider keys, passwords/tokens/recovery secrets, or unrestricted HTTP proxying to AI/client runtimes.
- Deterministic backend code owns identity, authorization, capability/location policy, constraints, idempotency, transactions, read-back, and audit semantics.
- Provider/model choice never grants authority.
- Significant architecture/implementation/deploy/next-work changes update `ROADMAP.md`, `NEW_CHAT_BOOTSTRAP.md`, this file, and relevant canonical docs.
- All Web work must follow `docs/design/WEB_IMPLEMENTATION_STANDARD.md`, `docs/design/WEB_SURFACE_OWNERSHIP.md`, `docs/design/WEB_ASSET_RELEASE_INTEGRITY.md`, and `docs/design/UI_UX_PRO_MAX_INTEGRATION.md`.

## 2. Canonical execution paths — LOCKED

External MCP:

`ChatGPT/SOL -> existing MSA MCP -> MCP authority intersection -> typed MSA backend -> result`

Native internal agent:

`MSA Web / future Telegram / Flutter / automation -> INTERNAL_MODEL runtime -> assigned provider/model -> native typed-tool adapter -> typed MSA backend -> response`

These are peer paths. Direct authorized MCP actions do not require an internal-agent hop. Internal agents do not normally use public MCP. `msa_agent_invoke` remains optional delegation/orchestration only.

## 3. Canonicality and write boundary

- `database_canonical=false`.
- `migration_baseline_accepted=false`.
- F6B snapshot: 1,646 rows; SAFE 1,417; REVIEW 222; CONFLICT 0; NEW_UNMAPPED 7.
- No production inventory writes, AI inventory writes, transfers, Smart Calculator deductions, Telegram/Flutter stock mutations, Sheet mirror conversion, automatic OCR/vision commit, or DB canonical promotion are authorized.

## 4. Verified AI Workspace foundation

Accepted foundation includes named agents, Provider Registry/saved models, PRIMARY + ordered FALLBACK configuration, native inference, durable Single Chat, bounded native reads, D4.8 shared Work/Artifact/Review/Event/Attention substrate, Owner-only native Review, per-participant authority, external MCP federation, feedback passes, export/delete UX, single-surface navigation, and PR #125 composer state hardening.

Attachment bytes are still not sent to provider vision/OCR. Production inventory writes remain disabled.

## 5. Review/federation invariants

- Stable orchestration roles: `ANALYST`, `REVIEWER`, `SYNTHESIZER`; all three are not mandatory.
- Roles never grant authority.
- Participant privileges never union.
- External review is exact-artifact-version bound evidence only.
- `Send review` is a structured full-preset operation, separate from ordinary conversation.
- Web work keeps one authoritative renderer/state owner, delegated/deterministic event wiring, paired frontend/API/persistence/read-back/rehydration contracts, content-derived asset identity, and bounded browser behavior tests.

PR #125 production anchor:

- merge/source SHA `eff5f7a25f715ba2018436005db8a85198fe88e7`
- deploy run `32732654844`
- issue #26 `status=success`

## 6. D4.9 — Review Thread Conversation and Owner Decisions — CURRENT

Canonical architecture: `docs/architecture/F7_2D49_REVIEW_THREAD_CONVERSATION_AND_OWNER_DECISIONS.md`.

### 6.1 Normal Send = one-agent conversational continuation

`Owner message -> target resolution -> one authorized native participant -> persisted reply`

Targeting:

- explicit selected/`@call_name` participant wins;
- otherwise prefer configured `SYNTHESIZER`;
- otherwise use the last configured active participant;
- unknown/ambiguous explicit target fails closed.

Normal Send must not start `feedback-pass`, consume external feedback, or run the whole preset.

### 6.2 Send review = full structured preset

`new external/staged feedback OR direct Owner review instruction -> configured REVIEW participant sequence -> WAITING_OWNER`

The current composer text can be sent directly as the structured Review instruction. Ordinary direct-discussion messages use `staged_for_review=false` and must not accidentally enable Review by themselves.

### 6.3 Owner Decision

A distinct `Record decision` action persists:

- `OWNER_DECISION` artifact;
- `OWNER_DECISION_RECORDED` immutable event;
- explicit `inventory_mutation=false` evidence in this phase.

A decision is durable authority-bearing evidence for later workflows, but it is not itself a store mutation or DB canonical promotion.

### 6.4 Future execution boundary

Later execution path:

`evidence -> agent discussion/review -> Owner decision -> executor agent typed mutation proposal -> required confirmation -> authorized backend operation -> read-back -> audit`

Executor agents never receive arbitrary SQL/direct DB authority. Tool/write authority remains an intersection and provider/model selection never grants it.

### 6.5 UI

In the existing Multi-Agent Review composer:

- participant target selector + normal Send `➤`;
- `Record decision`;
- `Send review` as separate full-preset action;
- rehydrate `OWNER_MESSAGE`, targeted `PARTICIPANT_OUTPUT` discussion replies, and `OWNER_DECISION` chronologically;
- retain top/composer DOCX/JSON and existing federation controls.

### 6.6 Acceptance

Prove:

1. normal Send invokes exactly one selected/default native participant;
2. normal Send never calls `feedback-pass`;
3. valid explicit target routes deterministically; invalid target fails closed;
4. direct typed Review instruction enables/starts full preset separately;
5. Owner Decision persists and causes no inventory mutation;
6. refresh/reopen preserves messages/replies/decisions;
7. existing external Review, export/delete, Review send-state, and browser reliability flows stay green.

## 7. Immediate implementation order

1. **CURRENT:** complete D4.9 backend endpoints + existing-renderer UI integration + bounded tests.
2. PR -> green CI -> main -> automatic deploy -> issue #26 exact-SHA verification.
3. Refresh ROADMAP/IMPLEMENTATION_PLAN/NEW_CHAT_BOOTSTRAP with accepted evidence.
4. Add Telegram notification/attention delivery over persisted Attention/Event state; Telegram failure remains non-fatal.
5. Add GROUP shared-context loop with Owner pause/resume/stop/steer and optional external checkpoints.
6. Add COMPARE, then bounded DEBATE.
7. Return to live PRIMARY -> FALLBACK proof when a stable secondary provider/model exists.
8. Add staff entitlement/location authority UI before staff tool rollout.
9. Expand vision/OCR only as a separate bounded evidence slice.
10. Controlled inventory writes remain later and require explicit canonicality, authority, idempotency, audit, confirmation and read-back prerequisites.

## 8. Immediate boundary

Do not enable production inventory mutation, arbitrary agent DB access, or PostgreSQL canonical promotion as part of D4.9.