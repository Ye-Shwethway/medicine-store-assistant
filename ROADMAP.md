# Medicine Store Assistant — Project Roadmap

Status: **F0/F1/F2/F3/F4/F5/F5.1/F6A/F6C/F7.1/F7.2A/F7.2B/F7.2C/F7.2D0/F7.2D2/F7.2D3/F7.2D4A/F7.2D4B/F7.2D4C/F7.2D4E/F7.2D4F/F7.2D4G verified; D4.7A hybrid native tool calling deployed/manual accepted; D4.7B response/attachment UX manually accepted; D4.8 shared work/review substrate + Owner-only native REVIEW backend deployed through migration 0021; current target is Owner REVIEW UI + real end-to-end manual acceptance; F6B remains test-only; PostgreSQL remains non-canonical**

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
- F7.2D4G Chat UX/lifecycle: long output, deterministic USER -> ASSISTANT sequence, clean display, Copy/select, conversation preview/time, owner-scoped delete
- D4.7 Owner UI exposes PRIMARY + ordered FALLBACK assignment chain; live failover proof remains pending
- D4.7A hybrid deterministic + model-driven native read-tool calling; contextual follow-up manual acceptance passed with MiniMax M3
- D4.7B human-facing response normalization + bounded attachments + image preview + dynamic latest-message conversation cards manually accepted
- D4.8 durable Work Item / Artifact / Review / Event / Attention Queue substrate deployed
- D4.8 stable `ANALYST` / `REVIEWER` / `SYNTHESIZER` bindings + Owner-only native-only REVIEW backend deployed; UI/manual acceptance still pending
- F7.3A minimal external-MCP actor audit evidence
- F7.3B broad typed row/detail reads

Native survival proof is live:

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

## D4.7A native tool calling — ACCEPTED

Canonical checkpoint: `docs/checkpoints/F7_2D47A_NATIVE_TOOL_CALLING_PLAN_2026-08-23.md`.

Accepted behavior:

- deterministic keyword router remains the explicit-request fast path;
- tool-capable models can independently request current native read tools for contextual/ambiguous follow-ups;
- current native registry is `inventory_summary`, `new_unmapped_rows`, `review_reasons`;
- every model-selected tool name is backend allowlisted before execution;
- native tool execution remains Owner-only until human/location authority intersection is implemented for staff;
- public MCP is not used;
- no native write/control tools are exposed.

The external MCP 106-action manifest is not copied into the internal model runtime. Only implemented native typed adapters that pass backend authority checks are exposed.

## D4.7B response + attachments — ACCEPTED

Canonical checkpoint: `docs/checkpoints/F7_2D47B_RESPONSE_AND_ATTACHMENTS_PLAN_2026-08-24.md`.

Accepted behavior includes human-facing response normalization, bounded photo/file attachment persistence, authenticated ownership checks, JPEG/PNG/WebP previews before/after send, dynamic latest-message conversation-card previews, and explicit no-vision/OCR claims while provider byte delivery remains unwired.

Attachment evidence is groundwork for later issue-paper photo batch intake, Daily Usage extraction, stock-transfer evidence processing, and other typed workflows.

## D4.7 fallback management / failover

Owner fallback configuration UI is implemented. Live PRIMARY failure -> ordered FALLBACK success acceptance remains pending. Provider/model assignment never changes agent identity or authority.

## D4.8 Multi-Agent Review + federation — BACKEND DEPLOYED / UI + MANUAL ACCEPTANCE NEXT

Canonical architecture: `docs/architecture/F7_2D48_MULTI_AGENT_REVIEW_AND_FEDERATION.md`.

Runtime checkpoint: `docs/checkpoints/F7_2D48_NATIVE_REVIEW_RUNTIME_2026-08-24.md`.

Deployment anchors:

- substrate PR #100 merge `4a9f54e17f2b386dfdd390af5850be2100986aac`
- native REVIEW PR #101 merge `0ebaba7d62f5cc3d9d3ec95e1cd33b4ccb7c324e`
- production migration head `0021_review_orchestration_roles`
- issue #26 deploy run `32660149646` recorded `status=success` for `0ebaba7d62f5cc3d9d3ec95e1cd33b4ccb7c324e`

Implemented backend truth:

- **native-only Multi-Agent workflows remain first-class and require no external agent**;
- durable Work Items, versioned Artifacts, version-bound Reviews, immutable Events, and shared Attention Queue are deployed;
- stable orchestration roles `ANALYST`, `REVIEWER`, `SYNTHESIZER` are stored separately from custom display labels;
- Owner-only native REVIEW API can create a durable work item, invoke ordered ACTIVE `INTERNAL_MODEL` participants independently, persist provider/model/fallback/latency provenance, bind reviewer findings to the exact prior artifact/version, and finish at `WAITING_OWNER`;
- existing AI Workspace attachment ownership contract is reused as metadata evidence; provider vision/OCR byte processing remains unwired;
- participant failure creates `FAILED` + durable Owner attention;
- Owner may return `WAITING_OWNER` work to `REVIEWING` with a persisted revision instruction;
- artifact/review state never mutates inventory by itself;
- no MCP schema/action-name change was required for this backend slice.

Full D4.8 REVIEW acceptance is **not yet complete**. The Owner-facing Review UI and a real manual end-to-end native-only REVIEW run are still required.

Canonical lifecycle remains:

`DRAFT -> REVIEWING -> WAITING_EXTERNAL? -> WAITING_OWNER -> APPROVED -> COMMITTABLE -> COMMITTED`

`WAITING_EXTERNAL` remains optional. `APPROVED` never means store mutation occurred.

Federated ChatGPT/MCP remains optional and asynchronous. The v2.1 MCP surface intentionally uses open action selectors for several long-lived tools with backend allowlists, so federation should first attempt to reuse existing tool names/slots rather than create a new MCP server or gratuitously expand the schema.

Telegram remains a notification/attention layer over the same persisted state. Web, MCP, and Telegram must surface one backend attention queue; notification failure must never advance or lose workflow state.

## Access-control invariants

Owner-only controls require backend authorization plus UI restriction. UI hiding is not authorization.

Non-owner Chat:

`authenticated user -> global gate -> per-user entitlement -> agent eligibility -> native runtime/tool authority`

Owner always bypasses the global user Chat gate. Global OFF blocks all non-owner Chat before provider calls. Tool authority is an intersection, never a union. Non-owner Chat remains reasoning-only for native store tools until explicit human/location authority intersection is wired.

Multi-Agent execution remains Owner-only in this phase. Each native participant's authority is evaluated independently; session membership never unions privileges. Federated submissions are evidence/review inputs and do not inherit internal-agent authority.

## Immediate implementation order

1. Build Owner-facing AI Workspace REVIEW UI over the deployed backend: REVIEW preset selection, stable role configuration, task/evidence submission, progress/provenance inspection, Work Item detail, and return-for-revision controls.
2. Manually accept a real native-only REVIEW run that reaches `WAITING_OWNER`, survives reload/restart from persisted state, exposes versions/reviews/provenance, and performs no inventory mutation.
3. Add optional federated `WAITING_EXTERNAL` checkpoint and bounded MCP work/review exchange, preferring existing v2.1 open-action long-lived slots before any schema-name change.
4. Add Telegram notification delivery over persisted attention events; notification failure must never advance/lose workflow state.
5. Add GROUP bounded native loops + Owner steer/pause/resume/stop + optional external checkpoints.
6. Add COMPARE and DEBATE execution semantics.
7. Return to D4.7 live failover proof when a stable secondary model/provider is available.
8. Per-user Chat entitlement/allowed-agent UI and human/location tool-authority intersection before staff tool rollout.
9. Expand native typed tools and attachment-processing pipelines as real workflows require.
10. D4.9 optional explicit MCP -> native-agent delegation after the shared substrate is stable.

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

Proceed with **D4.8 Owner REVIEW UI + native-only end-to-end manual acceptance first**. External/federated participation remains optional and comes only after native Review is proven. Do not enable production inventory writes, AI inventory writes, transfers, Smart Calculator deductions, Telegram/Flutter stock mutations, Sheet mirror conversion, automatic OCR/vision commits, or PostgreSQL canonical promotion.
