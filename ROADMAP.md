# Medicine Store Assistant — Project Roadmap

Status: **F0/F1/F2/F3/F4/F5/F5.1/F6A/F6C/F7.1/F7.2A/F7.2B/F7.2C/F7.2D0/F7.2D2/F7.2D3/F7.2D4A/F7.2D4B/F7.2D4C/F7.2D4E/F7.2D4F/F7.2D4G verified; D4.7A hybrid native tool calling deployed/manual accepted; F7.3A minimal MCP audit evidence and F7.3B broad typed reads verified; current refinement is D4.7B human-friendly response normalization + attachment-ready AI Workspace; F6B remains test-only; PostgreSQL remains non-canonical**

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

## F7.2D4 current refinement — D4.7B response + attachments

Canonical checkpoint: `docs/checkpoints/F7_2D47B_RESPONSE_AND_ATTACHMENTS_PLAN_2026-08-24.md`.

Current work:

- normalize native tool output into human-facing presentation plus preserved raw provenance;
- deterministic spreadsheet serial-date conversion may be supplied by backend while retaining the raw serial value;
- instruct agents to answer the user's question first and omit internal IDs/raw JSON/debug fields unless requested or necessary;
- distinguish retrieved fact, deterministic derived value, and inference;
- prohibit unsupported promises that fixing one blocker automatically changes classification/state;
- add photo and generic file attachment controls to each AI Workspace chat composer contract;
- single-agent Chat persists bounded attachment evidence with conversation/message ownership;
- current Multi-Agent surface shows the same attachment contract but remains disabled until D4.8 execution lands;
- attachment bytes are not yet sent to provider models, OCR, or vision pipelines;
- upload evidence never grants authority.

Attachment foundation is specifically intended for later typed workflows such as issue-paper photo batch intake, Daily Usage extraction, and stock-transfer evidence processing.

## D4.7 fallback management / failover

Owner fallback configuration UI is implemented. Live PRIMARY failure -> ordered FALLBACK success acceptance remains pending. Provider/model assignment never changes agent identity or authority.

## Access-control invariants

Owner-only controls require backend authorization plus UI restriction. UI hiding is not authorization.

Non-owner Chat:

`authenticated user -> global gate -> per-user entitlement -> agent eligibility -> native runtime/tool authority`

Owner always bypasses the global user Chat gate. Global OFF blocks all non-owner Chat before provider calls. Tool authority is an intersection, never a union. Non-owner Chat remains reasoning-only for native store tools until explicit human/location authority intersection is wired.

Attachment access follows the same authenticated workspace and conversation-ownership boundary. Multi-Agent attachment processing remains Owner-only with Multi-Agent execution.

## Immediate implementation order

1. D4.7B response normalization + attachment persistence/UI deployment and manual acceptance.
2. D4.7 live failover proof with two healthy saved models when a stable secondary provider/model is available.
3. D4.8 Owner-only Multi-Agent GROUP/COMPARE/REVIEW/DEBATE execution using the same attachment contract.
4. Per-user Chat entitlement/allowed-agent UI and human/location tool-authority intersection before staff tool rollout.
5. Expand native typed tools and attachment-processing pipelines over shared MSA service contracts as product workflows require.
6. D4.9 optional MCP -> native-agent delegation.
7. Continue full actor-aware audit and later controlled writes only after prerequisites.

## Later sequence

1. F7.2D4 — fallback/multi-agent/native-tool/attachment hardening
2. F7.3 — full actor-aware Audit / operation ledger
3. F7.4 — Inventory Locations / Store Policy / Preferences
4. F7.5 — Smart Calculator / receipts
5. F7.6 — deterministic Smart Analysis
6. F7.7 — richer internal AI workflows, including vision/OCR evidence intake
7. F7.8 — Alerts & Notifications
8. F9 — controlled typed writes after authority/audit/location/idempotency prerequisites
9. F10 — real workflow + fresh migration + Sheet sync validation
10. F11 — explicit canonical DB promotion
11. Telegram/Flutter rollout over proven shared contracts

## Immediate boundary

Proceed with **D4.7B human-friendly response + attachment-ready AI Workspace**, then return to live failover proof when a stable secondary model is available.

Do not enable production inventory writes, AI inventory writes, transfers, Smart Calculator deductions, Telegram/Flutter stock mutations, Sheet mirror conversion, automatic OCR/vision commits, or PostgreSQL canonical promotion.
