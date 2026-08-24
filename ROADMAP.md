# Medicine Store Assistant — Project Roadmap

Status: **D4.8 native Review, per-participant native reads, external MCP federation, federated feedback loop, single-surface Review UI, export/delete UX, Web Production Reliability Hardening, and Review/composer UX state hardening are deployed and production-verified. F6B remains test-only; PostgreSQL remains non-canonical. Current bounded target: D4.9 Multi-Agent conversational continuation + durable Owner Decision semantics.**

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
- DOCX + JSON point-in-time export at both top and composer regions;
- audit-preserving Review delete from workspace history;
- single-surface Review navigation with `Back to reviews`;
- ordinary Owner messages and explicit `Send review` as separate operations;
- chronological persisted Owner/native/external/feedback turns.

## External MCP federation — DEPLOYED / END-TO-END PROVEN

MCP schema version: `2026-08-24.v2.2`, 108 tools.

Dedicated federation tools:

- `msa_federated_review_query`
- `msa_federated_review_submit`

Federation flow proven in production:

`Native Review -> Request external review -> WAITING_EXTERNAL -> ChatGPT/SOL MCP query exact frozen artifact -> external review submit -> WAITING_OWNER -> external bubble persisted in Web -> Owner sends feedback to native team -> new native feedback pass`

Exact-version/stale-request validation remains fail-closed. External review evidence never inherits internal-agent authority and never mutates inventory.

MCP effective permission is:

`OAuth grant scope ∩ bound named-agent capability ∩ agent authority ceiling`

## Web Production Reliability Hardening — DEPLOYED

Hardening PR #123 merge: `12fe8ed4865027a768b277078ca90648a53103e3`.

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

## Review/composer UX state hardening — DEPLOYED / ACCEPTED

PR #125 merge: `eff5f7a25f715ba2018436005db8a85198fe88e7`.

Production deploy evidence from issue #26:

- `status=success`
- source SHA `eff5f7a25f715ba2018436005db8a85198fe88e7`
- workflow run `32732654844`

Accepted behavior:

1. ordinary Owner chat send and Review submission are separate operations;
2. `Send review` consumes only new/unconsumed Review feedback and duplicate empty passes fail closed;
3. Single Chat and Multi-Agent expose compact send controls plus top/composer DOCX/JSON exports;
4. Playwright mobile behavior coverage proves persisted/reopen Review send state and export endpoint reuse.

## D4.9 Review Thread Conversation + Owner Decisions — ACTIVE

Canonical architecture: `docs/architecture/F7_2D49_REVIEW_THREAD_CONVERSATION_AND_OWNER_DECISIONS.md`.

This slice upgrades the current persist-only Multi-Agent Owner message into a useful conversational continuation while keeping structured Review explicit.

Locked semantics:

- **Normal Send** -> persist Owner message -> resolve one native target -> invoke one authorized participant -> persist native discussion reply.
- Explicit `@call_name` targets that participant; no mention defaults to Synthesizer, otherwise last configured participant.
- Unknown explicit targets fail closed.
- **Send review** -> separate full configured REVIEW preset pass over new feedback/direct Owner instruction.
- **Record decision** -> persist dedicated `OWNER_DECISION` artifact + immutable event; no inventory mutation.
- Future executor agents may only perform typed authorized operations after Owner decision/confirmation; never arbitrary SQL/direct DB authority.

Required acceptance:

1. normal Send invokes exactly one participant and never starts `feedback-pass`;
2. valid/invalid explicit targeting behaves deterministically/fail-closed;
3. direct `Send review` remains full-preset and separate;
4. Owner Decision persists and rehydrates without mutation;
5. existing federation/export/delete/Web reliability behavior remains intact.

## Current lifecycle

Canonical Review lifecycle remains:

`DRAFT -> REVIEWING -> WAITING_EXTERNAL? -> WAITING_OWNER -> APPROVED -> COMMITTABLE -> COMMITTED`

Conversational turns do not need to change the Work Item lifecycle state. `WAITING_EXTERNAL` remains optional. `APPROVED` does not mutate store data.

## Immediate implementation order

1. **CURRENT: implement D4.9 targeted/default native discussion turns + durable Owner Decision artifacts in the existing Review thread.**
2. Preserve explicit structured `Send review` as the full-preset operation and allow direct Owner review instruction.
3. Add bounded browser/backend behavior proof and production deployment evidence; refresh continuity docs after acceptance.
4. Add Telegram notification/attention delivery over persisted Attention/Event state; notification failure remains non-fatal.
5. Add GROUP as a bounded native shared-context loop with Owner pause/resume/stop/steer and optional external checkpoints.
6. Add COMPARE while preserving independent answers until comparison.
7. Add DEBATE with bounded rounds before synthesis.
8. Return to live PRIMARY -> FALLBACK proof when a stable secondary provider/model is available.
9. Add per-user Chat entitlement/allowed-agent UI plus human/location tool-authority intersection before staff tool rollout.
10. Expand vision/OCR evidence processing only through an explicit bounded slice.
11. Controlled inventory writes remain a later authorization phase after canonicality, authority, idempotency, audit and read-back requirements are satisfied.

## Later sequence

1. D4.8/D4.9 collaboration and notification expansion
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

Proceed from the production-verified D4.8/Web foundation. Do not enable production inventory mutation, arbitrary agent DB access, or canonical DB promotion as part of D4.9.