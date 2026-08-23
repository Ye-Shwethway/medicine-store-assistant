# Medicine Store Assistant — Project Roadmap

Status: **F0/F1/F2/F3/F4/F5/F5.1/F6A/F6C/F7.1/F7.2A/F7.2B/F7.2C/F7.2D0/F7.2D2/F7.2D3/F7.2D4A/F7.2D4B/F7.2D4C/F7.2D4E/F7.2D4F/F7.2D4G verified; F7.3A minimal MCP audit evidence and F7.3B broad typed reads verified; current refinement is D4.7A hybrid deterministic + model-driven native tool calling before live failover proof; F6B remains test-only; PostgreSQL remains non-canonical**

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

## F7.2D4 current refinement — D4.7A native tool calling

Canonical checkpoint: `docs/checkpoints/F7_2D47A_NATIVE_TOOL_CALLING_PLAN_2026-08-23.md`.

Keep the already accepted deterministic native-read router as a fast path, but add a bounded model-driven native tool loop for tool-capable internal models.

Current work:

- expose every currently implemented and backend-authorized native read tool to a tool-capable internal model;
- initial registry remains `inventory_summary`, `new_unmapped_rows`, `review_reasons`;
- allow the model to request these tools for contextual/ambiguous follow-ups even when the current user message does not contain a deterministic routing keyword;
- validate every requested tool name server-side before execution;
- preserve deterministic fast-path prefetch for explicit inventory/NEW_UNMAPPED/review requests;
- persist exposed-tool and model-tool-call provenance;
- keep native tool execution Owner-only during this refinement until human/location authority intersection is implemented for staff;
- public MCP remains unused for native tools;
- no write/control tools are exposed.

The external MCP 106-action manifest is not automatically copied into the internal model runtime. Only native typed adapters that exist and pass backend authority checks are exposed.

## D4.7 fallback management / failover

Owner fallback configuration UI is implemented. A second saved healthy provider/model can be configured in ordered fallback position. After D4.7A is accepted, run live PRIMARY failure -> FALLBACK success acceptance with full provenance and `fallback_used=true`.

Provider/model assignment never changes agent identity or authority.

## Access-control invariants

Owner-only controls require backend authorization plus UI restriction. UI hiding is not authorization.

Non-owner Chat:

`authenticated user -> global gate -> per-user entitlement -> agent eligibility -> native runtime/tool authority`

Owner always bypasses the global user Chat gate. Global OFF blocks all non-owner Chat before provider calls. Tool authority is an intersection, never a union. During D4.7A, non-owner Chat is reasoning-only for native store tools until explicit human/location authority intersection is wired.

## Immediate implementation order

1. D4.7A hybrid fast-path + model-driven native tool-calling deployment and manual contextual-follow-up acceptance.
2. D4.7 live failover proof with two healthy saved models.
3. D4.8 Owner-only Multi-Agent GROUP/COMPARE/REVIEW/DEBATE execution.
4. Per-user Chat entitlement/allowed-agent UI and human/location tool-authority intersection before staff tool rollout.
5. Expand native typed tools over shared MSA service contracts as product workflows require.
6. D4.9 optional MCP -> native-agent delegation.
7. Continue full actor-aware audit and later controlled writes only after prerequisites.

## Later sequence

1. F7.2D4 — fallback/multi-agent/native-tool hardening
2. F7.3 — full actor-aware Audit / operation ledger
3. F7.4 — Inventory Locations / Store Policy / Preferences
4. F7.5 — Smart Calculator / receipts
5. F7.6 — deterministic Smart Analysis
6. F7.7 — richer internal AI workflows
7. F7.8 — Alerts & Notifications
8. F9 — controlled typed writes after authority/audit/location/idempotency prerequisites
9. F10 — real workflow + fresh migration + Sheet sync validation
10. F11 — explicit canonical DB promotion
11. Telegram/Flutter rollout over proven shared contracts

## Immediate boundary

Proceed with **D4.7A native tool-calling refinement**, then return to D4.7 live failover proof.

Do not enable production inventory writes, AI inventory writes, transfers, Smart Calculator deductions, Telegram/Flutter stock mutations, Sheet mirror conversion, or PostgreSQL canonical promotion.
