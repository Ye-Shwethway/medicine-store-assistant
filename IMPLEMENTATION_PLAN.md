# Medicine Store Assistant — Implementation Plan

Status: **D4.8 native Review, per-participant native reads, external MCP federation, Owner feedback passes, export/delete UX, single-surface Review navigation, Web Production Reliability Hardening, and Review/composer UX state hardening are deployed and production-verified. F6B remains test-only; PostgreSQL remains non-canonical. Current bounded slice: Telegram notification/attention delivery over persisted Attention/Event state.**

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

Production/manual accepted foundations include:

- named AI Agent Management and capability/authority policy;
- Provider Registry + Owner-saved models;
- PRIMARY + ordered FALLBACK assignment configuration;
- MCP-independent native provider inference;
- durable AI Workspace Single Chat;
- bounded native read tools: `inventory_summary`, `new_unmapped_rows`, `review_reasons`;
- D4.7A model-driven native read-tool loop;
- D4.7B response + attachment evidence UX;
- D4.8 shared Work/Review substrate;
- Owner-only native REVIEW orchestration;
- per-participant native read-tool authority;
- external MCP federation with exact-version binding;
- Owner feedback passes back to native participants;
- DOCX + JSON point-in-time export;
- audit-preserving Review delete;
- single-surface Multi-Agent Review navigation and reload-safe history.

Attachment bytes are still not sent to provider vision/OCR. Production inventory writes remain disabled.

## 5. D4.8 shared Work/Review substrate — DEPLOYED / ACCEPTED

Shared durable substrate:

- Work Item
- versioned Artifact
- exact-version Review
- immutable Event
- Attention Queue

Actor types include `OWNER`, `USER`, `INTERNAL_AGENT`, `EXTERNAL_MCP_AGENT`, `SYSTEM`.

Stable orchestration roles are `ANALYST`, `REVIEWER`, `SYNTHESIZER`; valid presets do not require all three. Two-agent `REVIEWER -> SYNTHESIZER` is valid. Roles never grant authority.

Canonical lifecycle:

`DRAFT -> REVIEWING -> WAITING_EXTERNAL? -> WAITING_OWNER -> APPROVED -> COMMITTABLE -> COMMITTED`

`WAITING_EXTERNAL` is optional. `APPROVED` does not mutate store data.

## 6. Per-participant native reads — DEPLOYED / ACCEPTED

Native REVIEW participants independently receive tools only when their own authority permits them.

Effective native tool authority remains:

`system gate ∩ authenticated human/session authority ∩ calling agent capability/ceiling ∩ location scope ∩ operation class ∩ confirmation policy`

Session privileges never union. One participant may not borrow another participant's tool access.

## 7. External MCP federation — DEPLOYED / END-TO-END PROVEN

MCP schema version: `2026-08-24.v2.2`, 108 tools.

Federation tools:

- `msa_federated_review_query`
- `msa_federated_review_submit`

Proven production flow:

`Native Review -> Request external review -> WAITING_EXTERNAL -> ChatGPT/SOL MCP query exact frozen artifact -> external review submit -> WAITING_OWNER -> external review bubble persisted in Web -> Owner feedback -> new native feedback pass`

Federated evidence is exact-artifact-version bound, evidence-only, and does not inherit internal-agent authority or mutate inventory.

Federated submit requires `mcp:propose`, not `mcp:write`.

## 8. Web Production Reliability Hardening — DEPLOYED / MANDATORY

Hardening PR #123 merge: `12fe8ed4865027a768b277078ca90648a53103e3`.

Mandatory invariants:

1. one authoritative renderer/state owner per interactive DOM subtree;
2. no second overlay renderer or MutationObserver patch to resolve ownership conflicts;
3. replaceable DOM uses delegated events or deterministic rebinding;
4. frontend control + API + persistence + read-back + UI rehydration are one paired contract;
5. persistent features prove fresh load, same-tab, refresh, and reopen;
6. async features prove intermediate state, settled state, and polling resume/stop;
7. MutationObserver is last-resort narrow/idempotent glue;
8. critical controls use behavior-level browser tests where practical;
9. content-derived Dashboard asset identities replace manually remembered fixed asset versions;
10. exact deployed SHA is required before declaring browser UI live.

## 9. Review/composer UX state hardening — DEPLOYED / ACCEPTED

PR #125 merge: `eff5f7a25f715ba2018436005db8a85198fe88e7`.

Production issue #26 evidence:

- `status=success`
- source SHA `eff5f7a25f715ba2018436005db8a85198fe88e7`
- deploy run `32732654844`

Implemented contract:

- ordinary Multi-Agent Owner Send persists `OWNER_MESSAGE` without starting a Review pass;
- `Send review` consumes only new/unconsumed Owner or external-review feedback;
- after successful consumption the Review action settles/disabled and remains so after rehydration;
- a new Owner message or new external review makes Review actionable again;
- backend returns 422 if a duplicate empty Review pass is attempted with no new feedback;
- external-review request state is settled for the already-reviewed latest participant artifact;
- Single Chat and Multi-Agent both expose compact normal send controls;
- Single Chat and Multi-Agent both expose composer-adjacent DOCX/JSON actions while retaining top exports;
- bottom and top export actions reuse the same existing export endpoints/contracts;
- content-derived Dashboard bundle identity remains in force.

Browser acceptance at 390×844 proves:

`external feedback pending -> Send review enabled -> review pass sent -> feedback consumed -> Review sent disabled -> Back/reopen still disabled -> normal Owner message sent without feedback-pass call -> reopen shows persisted Owner message -> Send review enabled again`

It also proves composer-side export endpoint reuse for both Single Chat and Multi-Agent. All six relevant PR-head workflows were green before merge, including `Validate Web production reliability`.

## 10. CURRENT bounded slice — Telegram attention delivery

Build Telegram notification delivery over the already-persisted Attention/Event substrate without making Telegram part of workflow correctness.

Required constraints:

- persisted workflow state remains authoritative; Telegram is delivery only;
- notification failure must not roll back or invalidate a valid Work/Event/Attention transition;
- use typed backend integration boundaries rather than direct database mutation from the bot;
- do not grant inventory mutation authority as part of notification delivery;
- Owner routing/identity must be explicit and auditable;
- retries/idempotency must prevent duplicate notification storms;
- start with bounded Owner attention cases such as `WAITING_OWNER` / external-review completion before broad alert expansion.

## 11. Immediate implementation order

1. **CURRENT:** design and implement Telegram notification/attention delivery over persisted Attention/Event state.
2. Add GROUP as a bounded native shared-context loop with Owner pause/resume/stop/steer and optional external checkpoints.
3. Add COMPARE while preserving independent answers until comparison.
4. Add DEBATE with bounded rounds before synthesis.
5. Return to live PRIMARY -> FALLBACK proof when a stable secondary provider/model is available.
6. Add per-user Chat entitlement/allowed-agent UI plus human/location authority intersection before staff tool rollout.
7. Expand vision/OCR evidence processing only through a separate bounded slice.
8. Controlled inventory writes remain later and require explicit canonicality/authority/idempotency/audit/read-back authorization.

## 12. Immediate boundary

Proceed only from the production-verified D4.8/Web foundation. Do not enable production inventory mutation or PostgreSQL canonical promotion as part of notification/collaboration work.
