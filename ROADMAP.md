# Medicine Store Assistant — Project Roadmap

Status: **F0/F1/F2/F3/F4/F5/F5.1/F6A/F6C/F7.1/F7.2A/F7.2B/F7.2C/F7.2D0/F7.2D2/F7.2D3/F7.2D4A/F7.2D4B/F7.2D4C/F7.2D4E/F7.2D4F/F7.2D4G verified; D4.7A hybrid native tool calling deployed/manual accepted; D4.7B response/attachment UX manually accepted; current design work is D4.8 Multi-Agent Review + federated work exchange; F6B remains test-only; PostgreSQL remains non-canonical**

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

## D4.8 Multi-Agent Review + federation — APPROVED DESIGN / NEXT

Canonical architecture: `docs/architecture/F7_2D48_MULTI_AGENT_REVIEW_AND_FEDERATION.md`.

Key decisions:

- **native-only Multi-Agent workflows are first-class and require no external agent**;
- `REVIEW` is the first implementation priority;
- `GROUP` is a bounded shared-context native agentic loop with Owner observation/steering;
- `COMPARE` keeps participant answers independent until comparison;
- `DEBATE` uses bounded rounds and may start native-only;
- external ChatGPT/MCP participation is optional and asynchronous/federated, not a fake live native participant;
- Review presets may optionally enter `WAITING_EXTERNAL`; they may also skip external review entirely;
- persisted Work Items, versioned Artifacts, Reviews, Events, and an Attention Queue form the shared coordination substrate;
- Review lifecycle is `DRAFT -> REVIEWING -> WAITING_EXTERNAL? -> WAITING_OWNER -> APPROVED -> COMMITTABLE -> COMMITTED`;
- `APPROVED` never means store mutation occurred;
- federated MCP review is version-bound and does not grant write authority;
- Telegram is planned as a notification/attention layer over the same persisted workflow state, never as the source of truth or orchestrator;
- Web, MCP, and Telegram should surface one backend attention queue;
- existing photo/file evidence contract is reused by Multi-Agent workflows.

Initial orchestration roles are `ANALYST`, `REVIEWER`, and `SYNTHESIZER`, with optional Owner-defined display labels. Roles do not grant authority.

## Access-control invariants

Owner-only controls require backend authorization plus UI restriction. UI hiding is not authorization.

Non-owner Chat:

`authenticated user -> global gate -> per-user entitlement -> agent eligibility -> native runtime/tool authority`

Owner always bypasses the global user Chat gate. Global OFF blocks all non-owner Chat before provider calls. Tool authority is an intersection, never a union. Non-owner Chat remains reasoning-only for native store tools until explicit human/location authority intersection is wired.

Multi-Agent execution remains Owner-only in this phase. Each native participant's authority is evaluated independently; session membership never unions privileges. Federated submissions are evidence/review inputs and do not inherit internal-agent authority.

## Immediate implementation order

1. Persist D4.8 Work Item / Artifact / Review / Event / Attention Queue substrate.
2. Wire Owner-only native-only REVIEW mode first using existing session presets and attachment contract.
3. Add optional federated `WAITING_EXTERNAL` checkpoint and bounded MCP work/review exchange actions.
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

Proceed with **D4.8 shared work/review substrate and native-only REVIEW mode first**. External/federated participation remains optional. Do not enable production inventory writes, AI inventory writes, transfers, Smart Calculator deductions, Telegram/Flutter stock mutations, Sheet mirror conversion, automatic OCR/vision commits, or PostgreSQL canonical promotion.
