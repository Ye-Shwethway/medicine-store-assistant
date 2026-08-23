# Medicine Store Assistant — Project Roadmap

Status: **F0/F1/F2/F3/F4/F5/F5.1/F6A/F6C/F7.1/F7.2A/F7.2B/F7.2C/F7.2D0/F7.2D2/F7.2D3/F7.2D4A/F7.2D4B/F7.2D4C/F7.2D4E/F7.2D4F/F7.2D4G verified; D4.7A hybrid native tool calling deployed/manual accepted; D4.7B response/attachment UX manually accepted; D4.8 shared work/review substrate + Owner-only native REVIEW backend + Owner REVIEW UI deployed through migration 0021; current target is one real provided-evidence native-only REVIEW manual acceptance, followed by bounded per-participant read-tool hardening; F6B remains test-only; PostgreSQL remains non-canonical**

The live Google workbook/source documents remain operationally authoritative. F6B is test-only and not an accepted migration baseline.

## Delivery policy

`branch -> PR -> main -> automatic VPS deploy for relevant runtime changes -> issue #26 runtime evidence -> continuity docs`

Runtime secrets remain only on the VPS. Web releases follow `docs/design/WEB_ASSET_RELEASE_INTEGRITY.md`.

## Product direction

MSA is a multi-client intelligent store-operations platform. Web, custom MCP, native internal AI, future Telegram/Flutter, scheduled jobs, and optional external clients reuse the same typed backend contracts and authority engine.

Preserve:

`source evidence -> reconcile current truth -> SAFE / REVIEW / CONFLICT / NEW_UNMAPPED -> authorized typed operation -> committed read-back -> audit`

No AI/client receives arbitrary SQL, DB credentials, VPS shell/filesystem, Sheet credentials, plaintext provider keys, passwords/tokens/recovery secrets, or unrestricted infrastructure access.

## Verified foundation

- F7.1 read-only Dashboard
- F7.2A canonical multi-user identity/sessions
- F7.2B User Management/profile
- F7.2C Credential + Recovery Lifecycle
- F7.2D0 custom MCP/OAuth schema `2026-08-23.v2.1` with 106 actions and live replacement ChatGPT read/audit acceptance
- F7.2D2 named Agent Management + persisted multi-agent session topology
- F7.2D3 Provider Registry + tested Owner-saved model catalog
- F7.2D4A external MCP OAuth-grant -> named-agent binding
- F7.2D4B backend PRIMARY + ordered FALLBACK assignment chain
- F7.2D4C MCP-independent native provider inference
- F7.2D4E durable top-level AI Workspace Chat
- F7.2D4F bounded native internal-agent reads and grounding
- F7.2D4G Chat UX/lifecycle
- D4.7A hybrid deterministic + model-driven native read-tool calling manually accepted
- D4.7B human-facing response + bounded attachment UX manually accepted
- D4.8 durable Work Item / Artifact / Review / Event / Attention Queue substrate deployed
- D4.8 stable `ANALYST` / `REVIEWER` / `SYNTHESIZER` bindings + Owner-only native REVIEW backend deployed
- D4.8 Owner REVIEW browser UI deployed with reload-safe Work Item history and versioned asset delivery; real manual Review acceptance remains pending
- F7.3A minimal external-MCP actor audit evidence
- F7.3B broad typed row/detail reads

Native survival proof remains live:

`MSA Web -> INTERNAL_MODEL agent -> assigned provider/model -> authorized native typed read -> grounded response + provenance`

Public MCP is not required for this path.

## F6B test-only snapshot

- batch `be13d127-5045-4284-a088-0a0b9b024d76`
- rows 1,646
- SAFE 1,417
- REVIEW 222
- CONFLICT 0
- NEW_UNMAPPED 7
- `migration_baseline_accepted=false`
- `database_canonical=false`

## Canonical execution-path separation — LOCKED

External MCP:

`ChatGPT/SOL -> MCP action -> MCP authority intersection -> typed MSA backend operation -> result`

Native internal agent:

`MSA Web / future Telegram / Flutter / automation -> INTERNAL_MODEL runtime -> assigned provider/model -> internal typed-tool adapter -> typed MSA backend operation -> response`

These are peer paths. Direct MCP actions do not require an internal-agent hop. Internal agents do not use public MCP as their ordinary tool gateway. `msa_agent_invoke` is optional delegation/orchestration only.

## D4.7 native agent foundations

D4.7A accepted hybrid behavior keeps a deterministic fast path plus bounded model-driven native reads. Current native read registry is `inventory_summary`, `new_unmapped_rows`, `review_reasons`. Public MCP is not used by the native tool loop.

D4.7B accepted attachment behavior persists bounded evidence, enforces ownership, renders previews, and explicitly does not claim provider vision/OCR while bytes remain unwired.

Fallback configuration UI is implemented; live PRIMARY -> FALLBACK proof remains pending.

## D4.8 Multi-Agent Review + federation — UI DEPLOYED / MANUAL ACCEPTANCE NEXT

Canonical architecture: `docs/architecture/F7_2D48_MULTI_AGENT_REVIEW_AND_FEDERATION.md`.

Runtime checkpoint: `docs/checkpoints/F7_2D48_NATIVE_REVIEW_RUNTIME_2026-08-24.md`.

Deployment anchors:

- substrate PR #100 merge `4a9f54e17f2b386dfdd390af5850be2100986aac`
- native REVIEW backend PR #101 merge `0ebaba7d62f5cc3d9d3ec95e1cd33b4ccb7c324e`
- Owner REVIEW UI PR #103 merge `c980446a7df27a352721115599a5ecf704797097`
- production migration head `0021_review_orchestration_roles`
- backend deploy run `32660149646`
- UI deploy run `32660684770`
- latest issue #26 source SHA `c980446a7df27a352721115599a5ecf704797097`, `status=success`

Implemented truth:

- native-only Multi-Agent workflows remain first-class and require no external agent;
- durable Work Items, versioned Artifacts, exact-version Reviews, Events, and shared Attention Queue are deployed;
- stable orchestration roles are separate from display labels and never grant authority;
- Owner-only native REVIEW invokes ordered ACTIVE `INTERNAL_MODEL` participants independently and persists provider/model/fallback/latency provenance;
- successful execution stops at `WAITING_OWNER`; participant failure creates `FAILED` + durable attention;
- Owner can inspect Work Items after reload and return WAITING_OWNER work to REVIEWING with a persisted revision instruction;
- existing Chat attachment metadata can be referenced after ownership validation; vision/OCR remains `NOT_PROCESSED`;
- browser UI exposes preset selection, stable role configuration, task/evidence submission, recent Work Items, Artifacts, Reviews, provenance, Attention/timeline, and return-for-revision;
- UI assets are independently versioned at `f72d48-review-ui-1` and deployed under the no-store release contract;
- artifact/review state never mutates inventory by itself;
- no MCP schema/action-name change was required.

Canonical lifecycle remains:

`DRAFT -> REVIEWING -> WAITING_EXTERNAL? -> WAITING_OWNER -> APPROVED -> COMMITTABLE -> COMMITTED`

`WAITING_EXTERNAL` remains optional. `APPROVED` never means store mutation occurred.

### Current REVIEW tool boundary

The first REVIEW executor currently uses the plain native provider invocation path, not the D4.7A model-driven native read-tool loop. Therefore initial manual acceptance is explicitly a **provided-evidence/native-reasoning Review**.

Before relying on REVIEW for current-store operational reasoning, add a bounded hardening slice that integrates native read tools with **per-participant READ authority checks**. Do not expose tools merely because another session participant has authority; session privileges never union.

### Federation

Federated ChatGPT/MCP remains optional and asynchronous. The v2.1 MCP surface uses open action selectors for long-lived tools with backend allowlists, so federation should first reuse existing tool names/slots before schema expansion. A separate MCP backend server is not required.

### Telegram

Telegram remains notification/attention delivery over the same persisted backend state. It is not the source of truth or orchestrator. Notification failure must never advance or lose workflow state.

## Access-control invariants

Owner-only controls require backend authorization plus UI restriction. UI hiding is not authorization.

Non-owner Chat:

`authenticated user -> global gate -> per-user entitlement -> agent eligibility -> native runtime/tool authority`

Owner always bypasses the global user Chat gate. Global OFF blocks non-owner Chat before provider calls. Tool authority is an intersection, never a union. Multi-Agent execution remains Owner-only in this phase.

## Immediate implementation order

1. Manually accept one real provided-evidence/native-reasoning REVIEW through the deployed Owner UI: native-only preset, stable roles, WAITING_OWNER result, Artifacts/Review/provenance inspection, browser reload survival, return-for-revision, and no inventory mutation.
2. Add bounded per-participant native read-tool integration for REVIEW, using existing D4.7A tools only when the calling participant independently has READ authority.
3. Re-accept one tool-using REVIEW before relying on Multi-Agent for current-store operational conclusions.
4. Add optional federated `WAITING_EXTERNAL` + bounded MCP work/review exchange with exact artifact-version binding, preferring existing v2.1 open-selector slots.
5. Add Telegram delivery over Attention Queue/events; notification failure remains non-fatal to workflow correctness.
6. Add GROUP bounded native loops + Owner pause/resume/stop/steer + optional external checkpoints.
7. Add COMPARE and DEBATE execution semantics.
8. Return to D4.7 live failover proof when a stable secondary model/provider is available.
9. Add per-user Chat entitlement/allowed-agent UI plus human/location tool-authority intersection before staff tool rollout.
10. Expand vision/OCR and controlled write workflows only through later explicit bounded slices.

## Later sequence

1. F7.2D4 — fallback/multi-agent/native-tool/attachment hardening
2. F7.3 — full actor-aware Audit / operation ledger
3. F7.4 — Inventory Locations / Store Policy / Preferences
4. F7.5 — Smart Calculator / receipts
5. F7.6 — deterministic Smart Analysis
6. F7.7 — richer internal AI workflows, including vision/OCR evidence intake
7. F7.8 — Alerts & Notifications, including Telegram delivery
8. F9 — controlled typed writes after authority/audit/location/idempotency prerequisites
9. F10 — real workflow + fresh migration + Sheet sync validation
10. F11 — explicit canonical DB promotion
11. Telegram/Flutter rollout over proven shared contracts

## Immediate boundary

Proceed with **one D4.8 provided-evidence native-only manual REVIEW acceptance, then per-participant native read-tool hardening**. External federation remains optional and comes only after native Review is proven. Do not enable production inventory writes, AI inventory writes, transfers, Smart Calculator deductions, Telegram/Flutter stock mutations, Sheet mirror conversion, automatic OCR/vision commits, or PostgreSQL canonical promotion.
