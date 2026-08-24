# Medicine Store Assistant — Project Roadmap

Status: **D4.8 Review/federation, Web Production Reliability Hardening, PR #125 Review/composer UX state hardening, and D4.9 Review Thread Conversation + Owner Decisions are deployed and production-verified. F6B remains test-only; PostgreSQL remains non-canonical. Current bounded target: Telegram notification/Attention delivery over persisted Attention/Event state.**

The live Google workbook/source documents remain operationally authoritative. F6B is test-only and not an accepted migration baseline.

## Delivery policy

`branch -> PR -> main -> automatic VPS deploy for relevant runtime changes -> issue #26 runtime evidence -> continuity docs`

All Web work must follow `WEB_IMPLEMENTATION_STANDARD.md`, `WEB_SURFACE_OWNERSHIP.md`, `WEB_ASSET_RELEASE_INTEGRITY.md`, and `UI_UX_PRO_MAX_INTEGRATION.md`.

## Canonical execution paths — LOCKED

External MCP:

`ChatGPT/SOL -> existing MSA MCP -> MCP authority intersection -> typed MSA backend -> result`

Native internal agent:

`MSA Web / future Telegram / Flutter / automation -> INTERNAL_MODEL runtime -> assigned provider/model -> native typed-tool adapter -> typed MSA backend -> response`

They are peer paths. Direct authorized MCP actions do not require an internal-agent hop. Internal agents do not normally use public MCP. `msa_agent_invoke` is optional delegation/orchestration only.

## Canonicality / authority boundary

- Google Sheet/source documents = current operational source of truth.
- PostgreSQL = deployed shadow/test database, **not canonical**.
- `migration_baseline_accepted=false`; `database_canonical=false`.
- F6B snapshot: 1,646 rows; SAFE 1,417; REVIEW 222; CONFLICT 0; NEW_UNMAPPED 7.
- No production inventory writes, AI inventory writes, transfers, Calculator deductions, Telegram/Flutter stock mutations, automatic OCR/vision commit, arbitrary agent SQL/DB mutation, or DB canonical promotion are authorized.
- Provider/model selection never grants authority. Participant privileges never union.

## D4.8 Review / federation — DEPLOYED / ACCEPTED

Shared durable substrate: Work Item, versioned Artifact, exact-version Review, immutable Event, Attention Queue.

Stable orchestration roles are `ANALYST`, `REVIEWER`, `SYNTHESIZER`; all three are not mandatory. External MCP review remains exact-version evidence only and does not inherit native authority.

Federation tools remain `msa_federated_review_query` and `msa_federated_review_submit`.

## Web reliability — MANDATORY

One authoritative renderer/state owner per interactive subtree; replaceable DOM uses delegated/deterministic binding; frontend/API/persistence/read-back/rehydration is one contract; persistent/async features prove lifecycle behavior; MutationObserver is narrow last-resort glue; critical changed interactions use bounded browser tests; Dashboard assets use content-derived identities; exact deployed SHA is required before declaring Web work live.

Hardening anchor: PR #123 merge `12fe8ed4865027a768b277078ca90648a53103e3`.

## Review/composer UX — DEPLOYED / ACCEPTED

PR #125 merge/source `eff5f7a25f715ba2018436005db8a85198fe88e7`; production deploy run `32732654844`.

Accepted separation:

- ordinary Owner Send and structured `Send review` are different operations;
- `Send review` only runs when new structured feedback/direct instruction exists and duplicate empty passes fail closed;
- Single Chat and Multi-Agent expose normal send controls plus top/composer DOCX/JSON exports.

## D4.9 Review Thread Conversation + Owner Decisions — DEPLOYED / ACCEPTED

Canonical architecture: `docs/architecture/F7_2D49_REVIEW_THREAD_CONVERSATION_AND_OWNER_DECISIONS.md`.

PR #127 merge/source:

`c2dc42b38a60a7dc625c0d0748530c74c98ed615`

Production issue #26 evidence:

- `status=success`
- source SHA `c2dc42b38a60a7dc625c0d0748530c74c98ed615`
- deploy run `32735227026`

Accepted interaction contract:

1. **Normal Send** persists the Owner message, resolves one native Review participant, invokes exactly that one participant, and persists the discussion reply/provenance in the same Work Item.
2. Target selection is deterministic: explicit participant selection; otherwise Synthesizer/default participant. Invalid explicit targets fail closed at the backend.
3. Direct discussion messages use `staged_for_review=false`; they do not consume external Review evidence and do not run the whole preset.
4. **Send review** remains the separate full configured REVIEW pass and can use direct Owner composer text as the structured instruction.
5. **Record decision** persists `OWNER_DECISION` + `OWNER_DECISION_RECORDED`; it performs no inventory mutation and does not promote PostgreSQL.
6. Discussion `PARTICIPANT_OUTPUT` is marked `discussion_turn=true` and is not treated as the latest structured artifact for external-review freezing.
7. Refresh/re-render target hydration is DOM-lifecycle-safe; the Playwright 390×844 smoke caught and closed a stale target-cache bug before merge.
8. PR-head relevant workflows were 7/7 green, including Web production reliability/browser behavior.

Future execution remains locked to:

`evidence -> discussion/review -> Owner decision -> executor agent typed mutation proposal -> required Owner confirmation -> authorized backend operation -> read-back -> audit`

An executor such as Synthesizer never receives arbitrary SQL/direct DB authority merely by being selected.

## CURRENT bounded slice — Telegram Attention delivery

Build Telegram notification delivery over the already-persisted Attention/Event substrate without making Telegram part of workflow correctness.

Required constraints:

- persisted Work/Event/Attention state remains authoritative; Telegram is delivery only;
- notification failure must not roll back or invalidate workflow state;
- Owner routing/Telegram identity linking must be explicit and auditable;
- retries/idempotency must prevent duplicate notification storms;
- use typed backend integration boundaries, not direct DB mutation from the bot;
- start with bounded Owner-attention cases such as `WAITING_OWNER` and external-review completion;
- no inventory mutation authority is added by notification delivery.

## Immediate implementation order

1. **CURRENT:** design and implement bounded Telegram notification/Attention delivery.
2. Verify retry/idempotency and non-fatal delivery failure; deploy and record exact evidence.
3. Add GROUP shared-context collaboration with Owner pause/resume/stop/steer and optional external checkpoints.
4. Add COMPARE while preserving independent answers until comparison.
5. Add bounded DEBATE before synthesis.
6. Return to live PRIMARY -> FALLBACK proof when a stable secondary provider/model exists.
7. Add per-user Chat entitlement/allowed-agent UI plus human/location authority intersection before staff tool rollout.
8. Expand vision/OCR only as a separate bounded evidence-processing slice.
9. Controlled inventory writes remain later and require explicit canonicality, authority, idempotency, confirmation, audit and read-back prerequisites.

## Immediate boundary

Proceed from the production-verified D4.8/D4.9/Web foundation. Do not enable production inventory mutation, arbitrary agent DB access, or PostgreSQL canonical promotion as part of notification/collaboration work.