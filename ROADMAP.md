# Medicine Store Assistant — Project Roadmap

Status: **D4.8 native Review, per-participant native reads, external MCP federation, federated feedback loop, single-surface Review UI, export/delete UX, and Web Production Reliability Hardening are deployed and manually exercised; F6B remains test-only; PostgreSQL remains non-canonical. Current bounded target: Review-send state correctness, normal Owner chat send separation, and composer-adjacent DOCX/JSON export controls for Single Chat and Multi-Agent.**

The live Google workbook/source documents remain operationally authoritative. F6B is test-only and not an accepted migration baseline.

## Delivery policy

`branch -> PR -> main -> automatic VPS deploy for relevant runtime changes -> issue #26 runtime evidence -> continuity docs`

Runtime secrets remain only on the VPS.

All Web work must follow:

- `docs/design/WEB_IMPLEMENTATION_STANDARD.md`
- `docs/design/WEB_SURFACE_OWNERSHIP.md`
- `docs/design/WEB_ASSET_RELEASE_INTEGRITY.md`
- `docs/design/UI_UX_PRO_MAX_INTEGRATION.md`

## Canonical execution paths — LOCKED

External MCP:

`ChatGPT/SOL -> existing MSA MCP -> MCP authority intersection -> typed MSA backend -> result`

Native internal agent:

`MSA Web / future Telegram / Flutter / automation -> INTERNAL_MODEL runtime -> assigned provider/model -> native typed-tool adapter -> typed MSA backend -> response`

These are peer paths. Direct authorized MCP actions do not require an internal-agent hop. Internal agents do not normally use public MCP. `msa_agent_invoke` remains optional delegation/orchestration only.

## Data/canonicality boundary

- Google Sheet/source documents = current operational source of truth.
- PostgreSQL = deployed shadow/test database, **not canonical**.
- `migration_baseline_accepted=false`.
- `database_canonical=false`.
- No production inventory writes, AI inventory writes, transfers, Calculator deductions, Telegram/Flutter stock mutations, Sheet mirror conversion, automatic OCR/vision commit, or DB canonical promotion are authorized.

F6B snapshot:

- batch `be13d127-5045-4284-a088-0a0b9b024d76`
- rows 1,646
- SAFE 1,417
- REVIEW 222
- CONFLICT 0
- NEW_UNMAPPED 7

## Verified AI foundation

- named AI Agent Management + capability/authority policy;
- Provider Registry + Owner-saved models;
- PRIMARY + ordered FALLBACK assignment configuration;
- MCP-independent native provider inference;
- durable AI Workspace Single Chat;
- bounded native read tools: `inventory_summary`, `new_unmapped_rows`, `review_reasons`;
- D4.7A model-driven native read-tool loop;
- D4.7B response + attachment evidence UX; attachment bytes still are not sent to provider vision/OCR;
- external MCP actor audit and broad typed reads.

## D4.8 Multi-Agent Review — DEPLOYED / ACCEPTED

Canonical architecture: `docs/architecture/F7_2D48_MULTI_AGENT_REVIEW_AND_FEDERATION.md`.

Shared durable substrate:

- Work Item
- versioned Artifact
- exact-version Review
- immutable Event
- Attention Queue

Actor types include `OWNER`, `USER`, `INTERNAL_AGENT`, `EXTERNAL_MCP_AGENT`, `SYSTEM`.

Stable orchestration roles are `ANALYST`, `REVIEWER`, `SYNTHESIZER`, but a valid REVIEW preset does **not** require all three. Two-agent presets such as `REVIEWER -> SYNTHESIZER` are valid. Roles never grant authority.

Native Review participants independently receive tools only when their own authority permits them. Session privileges never union.

Effective tool authority remains an intersection of system/human/agent/location/operation/confirmation policy.

### Native Review UX now includes

- live participant turns using durable background execution + polling;
- Copy controls and display normalization;
- deterministic native-tool provenance;
- DOCX + JSON point-in-time export;
- audit-preserving Review delete from workspace history;
- single-surface Review navigation with `Back to reviews`;
- Owner feedback composer and real native feedback passes;
- chronological persisted Owner/native/external/Owner-feedback turns.

## External MCP federation — DEPLOYED / END-TO-END PROVEN

MCP schema version: `2026-08-24.v2.2`, 108 tools.

Dedicated federation tools:

- `msa_federated_review_query` — read pending/get exact request;
- `msa_federated_review_submit` — evidence-only exact-version review submission; requires `mcp:propose`, not inventory write authority.

Federation flow proven in production:

`Native Review -> Request external review -> WAITING_EXTERNAL -> ChatGPT/SOL MCP query exact frozen artifact -> external review submit -> WAITING_OWNER -> external bubble persisted in Web -> Owner sends external feedback to native team -> new native feedback pass`

Exact-version/stale-request validation remains fail-closed. External review evidence never inherits internal-agent authority and never mutates inventory.

MCP effective permission is:

`OAuth grant scope ∩ bound named-agent capability ∩ agent authority ceiling`

Connection permission changes are live after save/read-back; reconnect is not required. `mcp:write` is not needed for federated evidence submission.

## Web Production Reliability Hardening — DEPLOYED

Hardening PR #123 merge:

`12fe8ed4865027a768b277078ca90648a53103e3`

Production deploy evidence:

- issue #26: `status=success`
- source SHA: `12fe8ed4865027a768b277078ca90648a53103e3`
- workflow run: `32727105740`

Systemic rules now enforced:

1. one authoritative renderer/state owner per interactive DOM subtree;
2. replaceable DOM uses delegated events or deterministic rebinding;
3. frontend + API + persistence are one paired contract;
4. persistent features must pass fresh-load, same-tab, refresh, and reopen paths;
5. async features must prove intermediate/settled state and polling resume/stop;
6. MutationObserver is last-resort, narrow, idempotent glue;
7. critical controls require behavior-level browser tests where practical;
8. content-derived Dashboard asset identities eliminate manual stale-version drift;
9. browser delivery is not accepted from source/CI evidence alone; exact deployed SHA remains required.

The Dashboard uses semantic-prefix + 12-character content hash asset identities, e.g. `f72d48-review-ui-<hash>`.

A Playwright Chromium mobile-size CI smoke performs the real critical Review interaction path:

`open Review -> external review visible -> Back -> reopen -> external review still visible -> blank Send feedback -> POST feedback-pass -> Owner default feedback bubble`

## Current bounded Web UX slice — ACTIVE

Before moving on to Telegram/GROUP collaboration work, tighten the current chat/review composer behavior:

1. **Review send/request state** — enable only when an actionable unsent review exists; successful persisted send/request settles or disables the control; refresh/reopen must preserve that state; a genuinely new actionable review may enable it again.
2. **Normal Owner send** — expose an independent Telegram-style send control for ordinary Single Chat/Multi-Agent messaging. Normal messaging must never be conflated with Review workflow submission.
3. **Bottom export access** — preserve existing top DOCX/JSON actions and add compact composer-adjacent DOCX/JSON controls on both Single Chat and Multi-Agent so long conversations can be saved without scrolling back to the top.
4. **Reuse, do not fork** — bottom export controls must call the same export implementation as the top controls; new composer controls must extend the authoritative renderer/event owner rather than creating another DOM owner.
5. **Browser behavior gate** — prove pending review -> sent/settled -> refresh/reopen still settled -> new actionable review re-enables; prove normal Send does not call Review endpoints; prove composer-side DOCX/JSON use the same export path on Single and Multi-Agent mobile views.

## Current lifecycle

Canonical Review lifecycle remains:

`DRAFT -> REVIEWING -> WAITING_EXTERNAL? -> WAITING_OWNER -> APPROVED -> COMMITTABLE -> COMMITTED`

`WAITING_EXTERNAL` is optional. `APPROVED` does not mutate store data. Production write gates remain closed.

## Immediate implementation order

1. **CURRENT: complete the bounded Review-send state + normal Send separation + composer-adjacent export UX slice.**
2. Maintain Web reliability discipline and browser-level acceptance for changed critical interactions.
3. Refresh continuity docs with exact PR/main/deployment evidence after acceptance.
4. Add Telegram notification/attention delivery over persisted Attention/Event state; notification failure must remain non-fatal to workflow correctness.
5. Add GROUP as a bounded native shared-context loop with Owner pause/resume/stop/steer and optional external checkpoints.
6. Add COMPARE while preserving independent answers until comparison.
7. Add DEBATE with bounded rounds before synthesis.
8. Return to live PRIMARY -> FALLBACK proof when a stable secondary provider/model is available.
9. Add per-user Chat entitlement/allowed-agent UI plus human/location tool-authority intersection before staff tool rollout.
10. Expand vision/OCR evidence processing only through an explicit bounded slice.
11. Controlled inventory writes remain a later authorization phase after canonicality, authority, idempotency, audit and read-back requirements are satisfied.

## Later sequence

1. D4.8 collaboration/notification expansion
2. F7.3 full actor-aware Audit / operation ledger
3. F7.4 Inventory Locations / Store Policy / Preferences
4. F7.5 Smart Calculator / receipts
5. F7.6 deterministic Smart Analysis
6. F7.7 richer internal AI workflows including vision/OCR evidence intake
7. F7.8 Alerts & Notifications
8. F9 controlled typed writes after prerequisites
9. F10 real workflow + fresh migration + Sheet sync validation
10. F11 explicit canonical DB promotion
11. Telegram/Flutter rollout over proven shared contracts

## Immediate boundary

Proceed from the now-hardened Web/D4.8 foundation. Do not enable production inventory mutation or canonical DB promotion merely because collaboration/federation workflows are working.
