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
- `database_canonical=false`.
- `migration_baseline_accepted=false`.
- No production inventory write, AI inventory write, transfer, Calculator deduction, Telegram/Flutter stock mutation, Sheet mirror conversion, automatic OCR/vision commit, arbitrary agent SQL/DB mutation, or DB canonical promotion is authorized.

F6B snapshot: rows 1,646; SAFE 1,417; REVIEW 222; CONFLICT 0; NEW_UNMAPPED 7.

## Delivery policy

`branch -> PR -> main -> automatic VPS deploy for runtime changes -> issue #26 evidence -> continuity-doc refresh`

## Durable execution-path invariant

External MCP:

`ChatGPT/SOL -> existing MSA MCP -> MCP authority intersection -> typed MSA backend -> result`

Native internal agent:

`MSA Web / future Telegram / Flutter / automation -> INTERNAL_MODEL runtime -> assigned provider/model -> native typed-tool adapter -> typed MSA backend -> response`

They are peer paths. Direct authorized MCP actions do not require an internal-agent hop. Internal agents do not normally use public MCP. `msa_agent_invoke` remains optional delegation/orchestration only.

## Production-verified foundation

- named AI Agent Management and capability/authority policy;
- Provider Registry + Owner-saved models;
- PRIMARY + ordered FALLBACK configuration;
- durable Single Chat and bounded native read tools;
- D4.8 Work/Artifact/Review/Event/Attention substrate;
- native Multi-Agent REVIEW with per-participant authority;
- external MCP federation and feedback passes;
- Review export/delete/single-surface navigation;
- Web Production Reliability Hardening;
- PR #125 Review/composer UX state hardening.

Native read-tool registry remains `inventory_summary`, `new_unmapped_rows`, `review_reasons`. Attachment bytes are still not sent to provider vision/OCR. Production inventory writes remain disabled.

## D4.8 Review/federation truth

Shared durable substrate: Work Item, versioned Artifact, exact-version Review, immutable Event, Attention Queue.

Actor types include `OWNER`, `USER`, `INTERNAL_AGENT`, `EXTERNAL_MCP_AGENT`, `SYSTEM`.

Stable roles are `ANALYST`, `REVIEWER`, `SYNTHESIZER`; all three are not mandatory. Roles never grant authority and participant privileges never union.

Canonical Review lifecycle:

`DRAFT -> REVIEWING -> WAITING_EXTERNAL? -> WAITING_OWNER -> APPROVED -> COMMITTABLE -> COMMITTED`

`WAITING_EXTERNAL` is optional. `APPROVED` never means inventory mutation occurred.

External MCP federation uses `msa_federated_review_query` + `msa_federated_review_submit`; submission is exact-version evidence only and requires `mcp:propose`, not inventory write authority.

## Web reliability — mandatory

One authoritative renderer/state owner per interactive subtree; no overlay renderer to repair ownership conflicts; replaceable DOM uses delegated events/deterministic rebinding; frontend/API/persistence/read-back/rehydration is one contract; persistent/async features prove reload lifecycle; MutationObserver is narrow last-resort glue; critical changed controls use bounded behavior-level browser tests; Dashboard bundle identities are content-derived; exact deployed SHA is required before declaring UI live.

## Production anchors before D4.9

PR #123 Web hardening merge: `12fe8ed4865027a768b277078ca90648a53103e3`.

PR #125 Review/composer UX merge: `eff5f7a25f715ba2018436005db8a85198fe88e7`.

PR #125 production issue #26 evidence:

- `status=success`
- source SHA `eff5f7a25f715ba2018436005db8a85198fe88e7`
- workflow run `32732654844`

Continuity PR #126 merge: `9294aa47fa2853aa2b53d7669c7540a553a00342`.

## D4.9 Review Thread Conversation + Owner Decisions — CURRENT

Canonical architecture: `docs/architecture/F7_2D49_REVIEW_THREAD_CONVERSATION_AND_OWNER_DECISIONS.md`.

The key semantic correction is that Multi-Agent normal Send is no longer intended as a passive persist-only note.

### Normal Send

`Owner message -> target resolution -> exactly one authorized native participant -> persisted discussion reply`

- explicit selected/`@call_name` target routes to that participant;
- no target defaults to configured Synthesizer, otherwise last configured participant;
- unknown/ambiguous target fails closed;
- normal Send does not start the full Review preset or consume external Review feedback;
- direct discussion `OWNER_MESSAGE` uses `staged_for_review=false`.

### Send review

`new structured feedback OR direct Owner review instruction -> configured REVIEW preset in order -> WAITING_OWNER`

The composer text can be sent directly as the structured Review instruction. `Send review` remains distinct from normal conversation.

### Owner Decision

A distinct `Record decision` operation persists `OWNER_DECISION` plus `OWNER_DECISION_RECORDED`. It is durable Owner authority/evidence for later workflows but performs **no inventory mutation** and does not promote the DB.

### Future execution chain — locked direction

`evidence -> discussion/review -> Owner decision -> executor agent typed mutation proposal -> required Owner confirmation -> authorized typed backend operation -> read-back -> audit`

An executor such as Synthesizer never receives arbitrary SQL/direct DB authority. Provider/model selection never grants authority.

### D4.9 implementation surface

- backend `multi_agent_review_discussion.py` extends the existing Work/Artifact/Event substrate; no schema migration is required;
- `discussion-targets` lists active native participants and default target;
- `discussion-turn` persists Owner message, invokes one native participant using existing native/read-tool authority, persists reply/provenance;
- `decisions` persists Owner decision + event only;
- existing authoritative Multi-Agent renderer exposes target selection, normal Send, `Record decision`, and separate `Send review`;
- discussion replies are not treated as the latest structured artifact for external-review freezing.

## D4.9 acceptance target

1. normal Send invokes exactly one selected/default native participant;
2. normal Send never starts `feedback-pass`;
3. target resolution is deterministic and invalid target fails closed;
4. typed direct Review instruction starts the separate full preset;
5. Owner Decision persists without inventory mutation;
6. refresh/reopen preserves discussion and decisions;
7. existing federation, export/delete, Review send-state, and Web reliability tests remain green;
8. after merge, exact main SHA must be verified through issue #26 before production acceptance.

## Next authorized order

1. **CURRENT:** complete D4.9, CI/browser acceptance, deploy and exact-SHA verification.
2. Refresh continuity docs with the accepted PR/deployment evidence.
3. Add Telegram notification/attention delivery over persisted Attention/Event state; delivery failure remains non-fatal.
4. Add GROUP shared-context collaboration with Owner pause/resume/stop/steer and optional external checkpoints.
5. Add COMPARE, then bounded DEBATE.
6. Return to live PRIMARY -> FALLBACK proof when a stable secondary model/provider is available.
7. Add staff entitlement/location authority UI before staff tool rollout.
8. Expand vision/OCR only as a separate bounded evidence-processing slice.
9. Controlled store writes remain later and require explicit canonicality/authority/idempotency/audit/confirmation/read-back authorization.

## Immediate boundary

Proceed from the production-verified D4.8/Web foundation. D4.9 does not authorize production inventory mutation, arbitrary agent DB access, or PostgreSQL canonical promotion.