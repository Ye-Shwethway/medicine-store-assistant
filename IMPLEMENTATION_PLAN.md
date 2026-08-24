# Medicine Store Assistant — Implementation Plan

Status: **D4.8 Review/federation, PR #125 Review/composer UX, and D4.9 Review Thread Conversation + Owner Decisions are deployed and production-verified. F6B remains test-only; PostgreSQL remains non-canonical. Current bounded slice: Telegram notification/Attention delivery over persisted Attention/Event state.**

This file is the execution contract for current MSA implementation order and boundaries.

## 1. Global rules

- Google Sheets/source documents remain operationally authoritative until explicit F11 promotion.
- PostgreSQL being deployed does **not** make it canonical.
- F6B remains test-only and must never be silently promoted.
- All humans, AI agents, integrations, and jobs use typed backend operations.
- Never expose arbitrary SQL, DB credentials, VPS shell/filesystem, Sheet credentials, plaintext provider keys, passwords/tokens/recovery secrets, or unrestricted HTTP proxying to AI/client runtimes.
- Deterministic backend code owns identity, authorization, capability/location policy, constraints, idempotency, transactions, read-back, confirmation and audit semantics.
- Provider/model choice never grants authority; participant privileges never union.
- Significant implementation/deploy/next-work changes update `ROADMAP.md`, `NEW_CHAT_BOOTSTRAP.md`, this file, and relevant canonical docs.
- Web changes obey the canonical Web implementation/ownership/release standards and bounded behavior-level browser gates.

## 2. Canonical execution paths — LOCKED

External MCP:

`ChatGPT/SOL -> existing MSA MCP -> MCP authority intersection -> typed MSA backend -> result`

Native internal agent:

`MSA Web / future Telegram / Flutter / automation -> INTERNAL_MODEL runtime -> assigned provider/model -> native typed-tool adapter -> typed MSA backend -> response`

These are peer paths. Direct authorized MCP actions do not require an internal-agent hop. Internal agents do not normally use public MCP.

## 3. Canonicality / write boundary

- `database_canonical=false`.
- `migration_baseline_accepted=false`.
- F6B snapshot: rows 1,646; SAFE 1,417; REVIEW 222; CONFLICT 0; NEW_UNMAPPED 7.
- No production inventory writes, transfers, Calculator deductions, Telegram/Flutter stock mutations, automatic OCR/vision commit, arbitrary agent DB/SQL mutation, or DB canonical promotion are authorized.

## 4. Accepted AI Workspace foundation

Accepted foundation includes named agents, Provider Registry/saved models, PRIMARY + ordered FALLBACK configuration, native inference, durable Single Chat, bounded native reads, D4.8 Work/Artifact/Review/Event/Attention substrate, per-participant native authority, external MCP federation, feedback passes, export/delete UX, single-surface navigation, Web Production Reliability Hardening, PR #125 composer state hardening, and D4.9 threaded one-agent discussion + Owner Decisions.

## 5. D4.9 — DEPLOYED / ACCEPTED

Canonical architecture: `docs/architecture/F7_2D49_REVIEW_THREAD_CONVERSATION_AND_OWNER_DECISIONS.md`.

PR #127 merge/source SHA:

`c2dc42b38a60a7dc625c0d0748530c74c98ed615`

Production issue #26:

- `status=success`
- source SHA `c2dc42b38a60a7dc625c0d0748530c74c98ed615`
- deploy run `32735227026`

Accepted semantics:

### Normal Send

`Owner message -> deterministic target resolution -> exactly one authorized native participant -> persisted discussion reply`

- explicit selected target routes to that participant;
- otherwise default prefers Synthesizer, then last configured participant;
- invalid explicit target fails closed;
- direct discussion `OWNER_MESSAGE` has `staged_for_review=false`;
- normal Send does not start `feedback-pass`, consume external Review evidence, or run the whole preset.

### Send review

`new structured feedback OR direct Owner review instruction -> full configured REVIEW participant sequence -> WAITING_OWNER`

It remains a separate workflow action from normal conversation.

### Owner Decision

`Record decision` persists `OWNER_DECISION` + immutable `OWNER_DECISION_RECORDED`, with no inventory mutation and no DB promotion.

### Future execution boundary

`evidence -> discussion/review -> Owner decision -> executor agent typed mutation proposal -> required Owner confirmation -> authorized backend operation -> read-back -> audit`

Executor selection never grants arbitrary SQL/direct DB authority.

### Acceptance evidence

- relevant PR-head workflows: 7/7 green;
- Playwright Chromium 390×844 proves structured Review consumption/settled state, targeted one-agent discussion without feedback-pass, Owner Decision persistence, direct structured Review instruction, and export endpoint reuse;
- browser test found a real re-render target hydration cache bug; implementation was fixed by binding hydration state to the live composer DOM node rather than Work Item ID cache;
- exact production SHA confirmed through issue #26.

## 6. CURRENT — Telegram notification / Attention delivery

Purpose: deliver Owner attention from persisted Attention/Event state to Telegram without making Telegram authoritative or required for workflow correctness.

### 6.1 Delivery contract

- Work Item/Event/Attention persistence happens first and remains authoritative.
- Telegram send failure is non-fatal to the underlying workflow transition.
- Notification delivery records its own attempt/result audit evidence.
- Retry policy is bounded and idempotent; repeated processing must not create notification storms.
- Delivery uses typed backend integration boundaries, never direct arbitrary DB mutation by the bot.

### 6.2 Identity / routing

- Owner Telegram identity/linking must be explicit, authenticated and auditable.
- Do not infer a Telegram recipient from display name alone.
- Initial scope is Owner notifications only.

### 6.3 Initial attention cases

Start narrowly with durable events/attention such as:

- Review enters `WAITING_OWNER`;
- external MCP review completes and Owner attention is required;
- later bounded workflow failures that already create durable attention.

Do not broaden to inventory alerts or staff notifications in the same slice.

### 6.4 Authority boundary

Telegram delivery grants no inventory/tool authority. Any future Telegram command/action must go through the same authenticated typed-operation and confirmation policies as Web/MCP/native paths.

## 7. Immediate implementation order

1. **CURRENT:** inspect existing Telegram/bot foundations and lock notification-delivery architecture before code.
2. Implement Owner identity/routing + idempotent delivery attempt records + bounded sender integration.
3. Wire only selected persisted Attention/Event cases; prove send failure is non-fatal.
4. Add focused tests and production evidence, then refresh continuity docs.
5. Add GROUP shared-context collaboration with Owner pause/resume/stop/steer and optional external checkpoints.
6. Add COMPARE, then bounded DEBATE.
7. Return to live PRIMARY -> FALLBACK proof when stable secondary provider/model exists.
8. Add staff entitlement/location authority before staff tool rollout.
9. Expand vision/OCR only as a separate bounded evidence slice.
10. Controlled inventory writes remain later and require explicit canonicality, authority, idempotency, confirmation, audit and read-back prerequisites.

## 8. Immediate boundary

D4.9 is complete. Proceed from the production-verified D4.8/D4.9/Web foundation. Do not enable production inventory mutation, arbitrary agent DB access, or PostgreSQL canonical promotion as part of Telegram delivery.