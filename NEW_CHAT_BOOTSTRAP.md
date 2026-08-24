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
11. `docs/architecture/F7_2D49_REVIEW_THREAD_CONVERSATION_AND_OWNER_DECISIONS.md`
12. `docs/checkpoints/F7_2D48_NATIVE_REVIEW_RUNTIME_2026-08-24.md`
13. `docs/checkpoints/WEB_PRODUCTION_RELIABILITY_2026-08-24.md`
14. `docs/design/WEB_IMPLEMENTATION_STANDARD.md`
15. `docs/design/WEB_SURFACE_OWNERSHIP.md`
16. `docs/design/WEB_ASSET_RELEASE_INTEGRITY.md`
17. `docs/design/UI_UX_PRO_MAX_INTEGRATION.md`
18. issue #26 current deployment evidence

Treat newer verified repository/runtime evidence as authoritative over remembered chat context.

## Current canonicality boundary

- Google Sheet/source documents remain operationally authoritative.
- PostgreSQL is deployed but **not canonical**.
- F6B is test-only and not an accepted migration baseline.
- `database_canonical=false`; `migration_baseline_accepted=false`.
- F6B snapshot: rows 1,646; SAFE 1,417; REVIEW 222; CONFLICT 0; NEW_UNMAPPED 7.
- No production inventory write, transfer, Calculator deduction, Telegram/Flutter stock mutation, automatic OCR/vision commit, arbitrary agent SQL/DB mutation, or DB canonical promotion is authorized.

## Delivery policy

`branch -> PR -> main -> automatic VPS deploy for runtime changes -> issue #26 evidence -> continuity-doc refresh`

## Durable execution-path invariant

External MCP:

`ChatGPT/SOL -> existing MSA MCP -> MCP authority intersection -> typed MSA backend -> result`

Native internal agent:

`MSA Web / future Telegram / Flutter / automation -> INTERNAL_MODEL runtime -> assigned provider/model -> native typed-tool adapter -> typed MSA backend -> response`

They are peer paths. Direct authorized MCP actions do not require an internal-agent hop. Provider/model assignment never grants authority; participant privileges never union.

## Production-verified AI Workspace foundation

- named AI Agent Management and capability/authority policy;
- Provider Registry + Owner-saved models and PRIMARY/FALLBACK configuration;
- durable Single Chat + bounded native read tools;
- D4.8 Work/Artifact/Review/Event/Attention substrate;
- native Multi-Agent REVIEW with per-participant authority;
- external MCP federation and feedback passes;
- Review export/delete/single-surface navigation;
- Web Production Reliability Hardening;
- PR #125 Review/composer UX state hardening;
- D4.9 targeted/default one-agent discussion + durable Owner Decisions.

Native read tools remain `inventory_summary`, `new_unmapped_rows`, `review_reasons`. Attachment bytes are still not sent to provider vision/OCR. Production inventory writes remain disabled.

## Web reliability — mandatory

One authoritative renderer/state owner per interactive subtree; no overlay renderer to repair ownership conflicts; replaceable DOM uses delegated/deterministic rebinding; frontend/API/persistence/read-back/rehydration is one contract; persistent/async features prove lifecycle behavior; MutationObserver is narrow last-resort glue; critical changed controls use bounded behavior-level browser tests; Dashboard asset identities are content-derived; exact deployed SHA is required before declaring Web work live.

## Production anchors

PR #123 Web hardening merge: `12fe8ed4865027a768b277078ca90648a53103e3`.

PR #125 Review/composer UX merge/source: `eff5f7a25f715ba2018436005db8a85198fe88e7`; deploy run `32732654844`.

Continuity PR #126 merge: `9294aa47fa2853aa2b53d7669c7540a553a00342`.

## D4.9 Review Thread Conversation + Owner Decisions — DEPLOYED / ACCEPTED

Canonical architecture: `docs/architecture/F7_2D49_REVIEW_THREAD_CONVERSATION_AND_OWNER_DECISIONS.md`.

PR #127 merge/source:

`c2dc42b38a60a7dc625c0d0748530c74c98ed615`

Issue #26 production evidence:

- `status=success`
- source SHA `c2dc42b38a60a7dc625c0d0748530c74c98ed615`
- workflow run `32735227026`

### Normal Send

`Owner message -> deterministic participant target -> exactly one authorized native participant -> persisted reply`

- owner can select a Review participant;
- default prefers Synthesizer, otherwise last configured participant;
- invalid explicit target fails closed;
- direct discussion messages persist as `OWNER_MESSAGE` with `staged_for_review=false`;
- discussion replies persist as `PARTICIPANT_OUTPUT` with `discussion_turn=true` and provenance;
- ordinary discussion does not start `feedback-pass` or consume external Review evidence.

### Send review

Separate full-preset operation:

`new structured feedback OR direct Owner review instruction -> configured REVIEW participant sequence -> WAITING_OWNER`

A typed composer instruction can start the structured pass directly; normal discussion is not required as a staging step.

### Owner Decision

`Record decision` persists `OWNER_DECISION` + `OWNER_DECISION_RECORDED`. It performs no inventory mutation and does not make PostgreSQL canonical.

### Future execution direction

`evidence -> discussion/review -> Owner decision -> executor agent typed mutation proposal -> required Owner confirmation -> authorized backend operation -> read-back -> audit`

Executor selection, including Synthesizer, never grants raw SQL/direct DB authority.

### D4.9 acceptance evidence

- relevant PR-head workflows 7/7 green;
- Playwright Chromium 390×844 proves structured Review consumption/settled state, targeted one-agent discussion without feedback-pass, Owner Decision persistence, direct full Review instruction, and export endpoint reuse;
- browser testing caught a real target-selector re-render cache bug; the implementation was corrected so target hydration belongs to the live DOM node lifecycle rather than a stale Work Item cache;
- exact deployed main SHA verified through issue #26.

## CURRENT bounded slice — Telegram notification / Attention delivery

Build Telegram delivery over persisted Attention/Event state while keeping workflow correctness independent of Telegram.

Locked constraints:

- persisted Work/Event/Attention state is authoritative; Telegram is delivery only;
- send failure does not roll back or invalidate workflow state;
- Owner Telegram identity/routing is explicit, authenticated and auditable;
- retries/idempotency prevent duplicate notification storms;
- bot uses typed backend integration boundaries, not arbitrary DB mutation;
- initial scope is Owner attention only, starting with `WAITING_OWNER` and external-review-completion cases;
- Telegram notification capability grants no inventory mutation authority.

## Next authorized order

1. **CURRENT:** inspect existing Telegram/bot foundations and lock bounded notification-delivery architecture before code.
2. Implement identity/routing, idempotent delivery attempts, bounded sender integration and selected Attention/Event triggers.
3. Prove failure is non-fatal, deploy, verify exact SHA, refresh continuity docs.
4. Add GROUP shared-context collaboration with Owner pause/resume/stop/steer and optional external checkpoints.
5. Add COMPARE, then bounded DEBATE.
6. Return to live PRIMARY -> FALLBACK proof when stable secondary provider/model exists.
7. Add staff entitlement/location authority before staff tool rollout.
8. Expand vision/OCR only as a separate bounded evidence-processing slice.
9. Controlled store writes remain later and require explicit canonicality/authority/idempotency/confirmation/audit/read-back authorization.

## Immediate boundary

Proceed from production-verified D4.8/D4.9/Web foundations. Do not enable production inventory mutation, arbitrary agent DB access, or PostgreSQL canonical promotion as part of Telegram notification delivery.