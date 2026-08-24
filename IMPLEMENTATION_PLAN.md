# Medicine Store Assistant — Implementation Plan

Status: **D4.8 native Review, per-participant native reads, external MCP federation, Owner feedback passes, export/delete UX, single-surface Review navigation, and Web Production Reliability Hardening are deployed and production-verified. F6B remains test-only; PostgreSQL remains non-canonical. Current bounded slice: Review-send state correctness + normal chat send separation + composer-adjacent DOCX/JSON export controls for Single Chat and Multi-Agent.**

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

MCP effective permission is:

`OAuth grant scope ∩ bound named-agent capability ∩ agent authority ceiling`

Saved permission changes are live after backend read-back; reconnect is not required.

## 8. Web Production Reliability Hardening — DEPLOYED / MANDATORY

Hardening PR #123 merge:

`12fe8ed4865027a768b277078ca90648a53103e3`

Production evidence:

- issue #26 `status=success`
- source SHA `12fe8ed4865027a768b277078ca90648a53103e3`
- deploy run `32727105740`

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

The accepted Playwright Chromium mobile smoke currently proves:

`open Review -> external review visible -> Back -> reopen -> external review still visible -> blank Send feedback -> POST feedback-pass -> persisted default Owner feedback bubble`

## 9. CURRENT bounded Web UX slice — Review-send + composer actions

This slice must be completed before moving to the next collaboration feature.

### 9.1 Review-send state correctness

The Review workflow action must represent an actual unsent/pending review request, not a generic chat send.

Required behavior:

- Review send/request control is enabled only while an actionable unsent review request exists.
- After successful submit/request and persisted read-back, the control becomes disabled or otherwise clearly settled (`Review sent` / equivalent).
- Refresh/reopen must rehydrate the same settled state; it must not become clickable again merely because the page re-rendered.
- A newly created actionable review request may enable the control again.
- Duplicate accidental submits must remain blocked by backend semantics even if the frontend regresses.

### 9.2 Normal Owner chat send is a separate control

Single Chat and Multi-Agent conversational messaging must have a normal send control independent of Review workflow actions.

- Use a compact Telegram-style send icon/button in the composer region.
- Normal send must target the ordinary conversation/message endpoint/path only.
- It must not trigger federated Review request/submit semantics.
- Review action state must not disable normal Owner messaging.

### 9.3 Composer-adjacent export controls

Long AI conversations should not require scrolling to the page top to save a snapshot.

- Keep existing top-level export actions for discoverability.
- Add compact DOCX and JSON export controls immediately above/adjacent to the composer region.
- Apply this to both Single Chat and Multi-Agent surfaces where point-in-time export exists.
- Reuse the existing export contract; do not fork a second export implementation.

### 9.4 Ownership and browser acceptance

- Extend the existing authoritative Single Chat and Multi-Agent renderers; do not introduce a second renderer for the same subtree.
- Reuse delegated events/deterministic binding as required by the Web standard.
- Preserve content-derived asset identity.
- Add bounded browser behavior coverage for the changed critical flows only.

Required behavior proof:

`pending review -> Review enabled -> submit/request -> persisted settled/disabled -> refresh/reopen still settled -> new actionable review -> enabled again`

Also prove:

- normal composer Send posts a normal message and does not call the Review endpoint;
- composer-side DOCX/JSON controls invoke the same export path as the existing top controls;
- both Single Chat and Multi-Agent mobile layouts expose the new controls without top-scroll dependency.

## 10. Immediate implementation order

1. **CURRENT:** complete the Review-send state + normal Send separation + composer-adjacent DOCX/JSON export slice above.
2. Keep browser-level acceptance bounded to these changed critical interactions and retain all Web reliability invariants.
3. Refresh continuity docs with exact PR/main/deployment evidence after acceptance.
4. Add Telegram notification/attention delivery over persisted Attention/Event state; notification failure remains non-fatal.
5. Add GROUP as a bounded native shared-context loop with Owner pause/resume/stop/steer and optional external checkpoints.
6. Add COMPARE while preserving independent answers until comparison.
7. Add DEBATE with bounded rounds before synthesis.
8. Return to live PRIMARY -> FALLBACK proof when a stable secondary provider/model is available.
9. Add per-user Chat entitlement/allowed-agent UI plus human/location authority intersection before staff tool rollout.
10. Expand vision/OCR evidence processing only through a separate bounded slice.
11. Controlled inventory writes remain later and require explicit canonicality/authority/idempotency/audit/read-back authorization.

## 11. Immediate boundary

Proceed only from the hardened D4.8/Web foundation. Do not enable production inventory mutation or PostgreSQL canonical promotion as part of this UX slice.
