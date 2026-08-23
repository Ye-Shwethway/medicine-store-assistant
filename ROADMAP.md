# Medicine Store Assistant — Project Roadmap

Status: **F0/F1/F2/F3/F4/F5/F5.1/F6A/F6C/F7.1/F7.2A/F7.2B/F7.2C/F7.2D0/F7.2D2/F7.2D3/F7.2D4A/F7.2D4B/F7.2D4C/F7.2D4E/F7.2D4F/F7.2D4G verified; F7.3A minimal MCP audit evidence and F7.3B broad typed reads verified; current work is D4.7 fallback management + failover provenance; F6B remains test-only; PostgreSQL remains non-canonical**

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

## F7.2D4 current work — D4.7 fallback management

Canonical checkpoint: `docs/checkpoints/F7_2D47_FALLBACK_MANAGEMENT_PLAN_2026-08-23.md`.

The backend already stores and executes one PRIMARY plus up to five ordered FALLBACK models. The missing product work is Owner-facing configuration and live failover acceptance.

Current work:

- expose PRIMARY + ordered FALLBACK chain in Owner-only AI Agent Management;
- use canonical `/model-assignments` chain endpoint;
- select only saved, healthy, currently-discovered models from enabled providers;
- add/remove/reorder up to five fallbacks;
- show fallback count on internal-agent cards;
- preserve backend rejection for non-internal agents and invalid chains;
- once a second healthy saved model is available, force/observe primary failure and verify fallback order + provenance + `fallback_used=true`.

Provider/model assignment never changes agent identity or authority.

## Access-control invariants

Owner-only controls require backend authorization plus UI restriction. UI hiding is not authorization.

Non-owner Chat:

`authenticated user -> global gate -> per-user entitlement -> agent eligibility -> native runtime/tool authority`

Owner always bypasses the global user Chat gate. Global OFF blocks all non-owner Chat before provider calls. Tool authority is an intersection, never a union.

## Immediate implementation order

1. D4.7 fallback configuration UI + persistence/order acceptance.
2. D4.7 live failover proof when two healthy saved models are configured.
3. D4.8 Owner-only Multi-Agent GROUP/COMPARE/REVIEW/DEBATE execution.
4. Per-user Chat entitlement/allowed-agent UI before staff rollout.
5. Expand native typed reads over shared MSA service contracts as needed.
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

Proceed with **D4.7 fallback management + failover provenance**.

Do not enable production inventory writes, AI inventory writes, transfers, Smart Calculator deductions, Telegram/Flutter stock mutations, Sheet mirror conversion, or PostgreSQL canonical promotion.
