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
11. `docs/checkpoints/F7_2D48_NATIVE_REVIEW_RUNTIME_2026-08-24.md`
12. `docs/checkpoints/WEB_PRODUCTION_RELIABILITY_2026-08-24.md`
13. `docs/design/WEB_IMPLEMENTATION_STANDARD.md`
14. `docs/design/WEB_SURFACE_OWNERSHIP.md`
15. `docs/design/WEB_ASSET_RELEASE_INTEGRITY.md`
16. `docs/design/UI_UX_PRO_MAX_INTEGRATION.md`
17. issue #26 current deployment evidence

Treat newer verified repository/runtime evidence as authoritative over remembered chat context.

## Current canonicality boundary

- Google Sheet/source documents remain operationally authoritative.
- PostgreSQL is deployed but **not canonical**.
- F6B is test-only and not an accepted migration baseline.
- `database_canonical=false`.
- `migration_baseline_accepted=false`.
- No production inventory write, AI inventory write, transfer, Calculator deduction, Telegram/Flutter stock mutation, Sheet mirror conversion, automatic OCR/vision commit, or DB canonical promotion is authorized.

F6B snapshot:

- rows 1,646
- SAFE 1,417
- REVIEW 222
- CONFLICT 0
- NEW_UNMAPPED 7

## Delivery policy

`branch -> PR -> main -> automatic VPS deploy for runtime changes -> issue #26 evidence -> continuity-doc refresh`

## Durable execution-path invariant

External MCP:

`ChatGPT/SOL -> existing MSA MCP -> MCP authority intersection -> typed MSA backend -> result`

Native internal agent:

`MSA Web / future Telegram / Flutter / automation -> INTERNAL_MODEL runtime -> assigned provider/model -> native typed-tool adapter -> typed MSA backend -> response`

They are peer paths. Internal agents do not depend on public MCP for ordinary work. Direct authorized MCP actions do not require an internal-agent hop. `msa_agent_invoke` remains optional delegation/orchestration only.

## Verified native AI foundation

Production/manual accepted foundations include:

- named AI Agent Management and capability/authority policy;
- Provider Registry + tested Owner-saved models;
- PRIMARY + ordered FALLBACK configuration;
- MCP-independent native inference;
- durable AI Workspace Single Chat;
- bounded native read tools;
- D4.7A model-driven native read tools;
- D4.7B response/attachment evidence UX;
- D4.8 native Multi-Agent Review, per-participant native reads, federation and feedback passes.

Native read-tool registry:

- `inventory_summary`
- `new_unmapped_rows`
- `review_reasons`

Attachment bytes are still not sent to provider vision/OCR. Production inventory writes remain disabled.

## D4.8 Multi-Agent Review — CURRENT TRUTH

Shared durable substrate:

- Work Item
- versioned Artifact
- exact-version Review
- immutable Event
- Attention Queue

Actor types include `OWNER`, `USER`, `INTERNAL_AGENT`, `EXTERNAL_MCP_AGENT`, `SYSTEM`.

Stable roles are `ANALYST`, `REVIEWER`, `SYNTHESIZER`, but all three are **not mandatory**. A two-agent `REVIEWER -> SYNTHESIZER` preset is valid. Roles are orchestration semantics and never grant authority.

Native Review participants independently receive read tools only when their own capability/authority allows them. Never union participant privileges.

### Review UI/runtime capabilities now deployed

- live participant turns via durable background execution + polling;
- deterministic native-tool provenance;
- Copy and response-display normalization;
- DOCX + JSON point-in-time export;
- audit-preserving Review delete;
- single-surface Multi-Agent Review chat with `Back to reviews`;
- chronological Owner/native/external/Owner-feedback history;
- Owner feedback composer and actual native feedback passes;
- refresh/reopen persistence for external MCP review bubbles and workflow state.

Canonical lifecycle:

`DRAFT -> REVIEWING -> WAITING_EXTERNAL? -> WAITING_OWNER -> APPROVED -> COMMITTABLE -> COMMITTED`

`WAITING_EXTERNAL` is optional. `APPROVED` never means inventory mutation occurred.

## External MCP federation — DEPLOYED / PROVEN

MCP schema: `2026-08-24.v2.2`, 108 tools.

Federation tools:

- `msa_federated_review_query`
- `msa_federated_review_submit`

Federated evidence flow proven end-to-end:

`Native Review -> Owner Request external review -> WAITING_EXTERNAL -> ChatGPT/SOL queries exact frozen artifact -> external MCP review submit -> WAITING_OWNER -> external review appears durably in Web -> Owner sends feedback to native team -> new native feedback pass`

Federated submit requires `mcp:propose`, not `mcp:write`.

Effective MCP scope:

`live OAuth grant ∩ bound named-agent capability ∩ authority ceiling`

A saved permission change is live after backend read-back; reconnect is not required.

External review is evidence-only, exact-artifact-version bound, and does not inherit internal-agent authority or mutate inventory.

## Web Production Reliability — MANDATORY

A series of D4.8 Web regressions exposed systemic integration weaknesses: stale manual asset identity, multiple renderers touching the same interactive subtree, direct event listeners lost after `innerHTML` replacement, backend state that was not consistently rehydrated, live paths behaving differently from refresh/reopen paths, and CI that proved strings/routes existed without proving buttons worked.

Those failure classes are now addressed by mandatory standards and automation.

Read before any Web change:

- `docs/design/WEB_IMPLEMENTATION_STANDARD.md`
- `docs/design/WEB_SURFACE_OWNERSHIP.md`
- `docs/design/WEB_ASSET_RELEASE_INTEGRITY.md`

Critical rules:

1. one authoritative renderer/state owner per interactive DOM subtree;
2. no second overlay renderer/MutationObserver to patch an ownership conflict;
3. replaceable DOM uses delegated events or deterministic rebinding;
4. frontend + API + backend persistence + read-back + rehydration form one paired contract;
5. persistent features must pass fresh load, same-tab, refresh and reopen;
6. async features must prove intermediate state, settled state and polling start/resume/stop;
7. MutationObserver is last-resort narrow/idempotent glue;
8. critical controls require behavior-level browser tests where practical;
9. mobile views require an obvious return/back path;
10. exact deployed SHA is required before declaring browser UI live.

### Content-derived asset identity

Dashboard bundle identities are now automatically derived from the exact served file content while preserving semantic prefixes, for example:

`f72d48-review-ui-<12-char-hash>`

Do not reintroduce manually remembered fixed asset versions for migrated bundles.

### Browser interaction gate

The Web reliability CI includes a real Playwright Chromium mobile-size smoke that proves:

`open Review -> external review visible -> Back -> reopen -> external review still visible -> blank Send feedback -> POST feedback-pass -> persisted default Owner feedback bubble`

`grep`, route existence and JS syntax remain supporting checks only; they are not sufficient Web acceptance by themselves.

## Web hardening deployment anchor

PR #123 merge:

`12fe8ed4865027a768b277078ca90648a53103e3`

Issue #26 production evidence:

- `status=success`
- source SHA `12fe8ed4865027a768b277078ca90648a53103e3`
- workflow run `32727105740`

All 13 relevant regression workflows were green on the accepted PR head before merge, including the new Web production reliability browser smoke.

## Access + authority invariant

Owner-only controls require backend authorization plus UI restriction. UI hiding is not authorization.

Tool authority remains an intersection:

`system gate ∩ authenticated human/session authority ∩ calling agent capability/ceiling ∩ location scope ∩ operation class ∩ confirmation policy`

Provider/model assignment never grants authority. Session participant privileges never union.

## Next authorized order

1. Keep the new Web reliability standard as a blocking requirement for every future Dashboard slice.
2. Continue from the proven D4.8 federation/native feedback foundation; do not reintroduce dual-renderer patch patterns.
3. Add Telegram notification/attention delivery over persisted Attention/Event state; notification failure remains non-fatal.
4. Add GROUP as a bounded native shared-context loop with Owner pause/resume/stop/steer and optional external checkpoints.
5. Add COMPARE, preserving independent answers until comparison.
6. Add DEBATE with bounded rounds before synthesis.
7. Return to live PRIMARY -> FALLBACK proof when a stable secondary model/provider is available.
8. Add per-user Chat entitlement/allowed-agent UI plus human/location authority intersection before staff tool rollout.
9. Expand vision/OCR only through a separate bounded evidence-processing slice.
10. Controlled store writes remain later and require explicit canonicality/authority/idempotency/audit/read-back authorization.

## Immediate boundary

Proceed from the now-hardened D4.8/Web foundation. Production inventory mutation and PostgreSQL canonical promotion remain unauthorized.
