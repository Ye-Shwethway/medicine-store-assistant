# Medicine Store Assistant — Project Roadmap

Status: **AI Workspace / D4.8-D4.9 is an accepted supporting foundation. F6B remains test-only; PostgreSQL remains non-canonical. Current bounded target: F6C Workbook Parity Lock with canonical-domain/configurable-view separation, followed by F6D Canonical Inventory Schema Parity + Fresh Shadow Import.**

The live Google workbook/source documents remain operationally authoritative. `migration_baseline_accepted=false`; `database_canonical=false`.

## Product direction — LOCKED

MSA is not a fixed spreadsheet clone and not an AI-only application.

Target product:

- one Main Store plus unlimited Sub Stores;
- durable PostgreSQL-backed inventory truth;
- human staff and AI agents working through the same typed operation layer;
- Web, Flutter, Telegram, ChatGPT and automation clients over the same backend;
- persistent operation with or without ChatGPT/Google Sheets;
- spreadsheet-like operational tables that may use presets or user-defined column layouts.

Core rule:

> **Spreadsheet layout is configurable; inventory semantics are not arbitrary.**

Architecture:

`canonical inventory domain -> field/computation registry -> configurable operational views -> draft/confirm/save -> typed domain commands -> audit/read-back`

Human UI edits and AI-agent MSA actions converge on the same authorized typed backend command layer. Neither receives raw SQL authority.

Canonical companion architecture: `docs/architecture/CONFIGURABLE_OPERATIONAL_VIEW_ENGINE.md`.

## Delivery policy

`branch -> PR -> main -> automatic VPS deploy for relevant runtime changes -> issue #26 runtime evidence -> continuity docs`

## Canonicality / authority boundary

- Google Sheet/source documents = current operational source of truth.
- PostgreSQL = deployed shadow/test database, **not canonical**.
- Existing F6B snapshot is test evidence only and must not be silently promoted.
- No production inventory writes, transfers, Calculator deductions, Telegram/Flutter stock mutations, automatic OCR/vision commit, arbitrary agent SQL/DB mutation, or DB canonical promotion are authorized.
- Provider/model selection never grants authority; participant privileges never union.

## Accepted AI Workspace foundation

D4.8/D4.9, external MCP federation, Review thread discussion, Owner Decisions, export/delete UX and Web Production Reliability Hardening are accepted foundations.

PR #129 added ordinary Review-thread `Talk to -> All agents` broadcast while keeping full `Send review` separate. Production deploy evidence:

- source SHA `75bfb89eb83b5cedfffa9148db454b1245269593`
- workflow run `32736647711`
- issue #26 `status=success`

Small Review UI polish may be folded into later touched Web work. Do not keep extending AI collaboration as the immediate product focus.

## CURRENT — F6C Workbook Parity Lock

Canonical architecture:

- `docs/architecture/F6C_WORKBOOK_PARITY_LOCK.md`
- `docs/architecture/CONFIGURABLE_OPERATIONAL_VIEW_ENGINE.md`

Purpose: lock the real inventory semantics before modifying the canonical schema or performing a fresh migration candidate.

### Priority source behavior

1. Main Stock product/lot identity and opening/base stock semantics.
2. Daily Usage actual movement, Day 1–31 editing meaning, monthly aggregate/current balance.
3. CMS catalogue identity/mapping/current price vs historical receipt-price separation.
4. Batch intake, new expiry lots, idempotency and fixed-asset routing.
5. Reorder inputs/configuration/calculated recommendation.
6. Month rollover/opening carry-forward and audit behavior.
7. Main Store/Sub Store location dimension.

### Projection/archive surfaces

Current Owner-confirmed legacy behavior:

- `This Month Received` = filtered/derived display from Main Stock received activity.
- `Reorder Form` = filtered/derived view of Main Stock calculated Estimated Reorder Qty.
- `Final Reorder Form` = copied working output with optional manual adjustment before submission.
- Master Data archive = preservation of approved/final monthly output.

These are lower-priority view/snapshot concerns and must not drive canonical schema design.

### F6C deliverables

- `WORKBOOK_PARITY_MATRIX.md`
- `WORKBOOK_FUNCTION_CONTRACT.md`
- every important operational column classified as entity field, computed field, command-backed editable field, or display/helper field;
- explicit schema/domain gap list;
- fresh shadow-import plan.

## NEXT — F6D Canonical Inventory Schema Parity + Fresh Shadow Import

After F6C is source-verified:

1. lock Store/Location, Product, Lot, Catalogue Mapping, Receipt, Usage, Adjustment, Ledger and Audit identities;
2. adjust only schema/domain pieces proven necessary by parity analysis;
3. take a fresh authorized source snapshot;
4. perform a repeatable non-canonical shadow import;
5. reconcile identities, expiry lots, opening/base stock, receipt totals, usage, CMS mapping/price and balances;
6. prove Main Stock and Daily Usage projections can be generated from the DB;
7. keep unresolved mismatches explicit and remain non-canonical until accepted.

The existing F6B data is not the F6D migration baseline.

## Subsequent inventory/database path

1. **F6C — CURRENT:** domain/workbook parity lock + configurable-view boundary.
2. **F6D:** canonical schema parity + fresh shadow import.
3. Historical bootstrap from strongest available evidence without fabricating transactions.
4. Shadow calculation parity for balances, receipts, usage, CMS data, month outputs and reorder.
5. Minimal field/computation registry + saved view-definition substrate.
6. Main Stock/Daily Usage DB-backed preset views.
7. Spreadsheet-like draft/confirm/save editing over typed commands.
8. Dual verification of real operational events against the live workbook.
9. Selected DB read-path promotion only after repeated parity.
10. Controlled write promotion one operation class at a time with idempotency, authorization, confirmation, audit and read-back.
11. Explicit database canonicality promotion only after migration, backup/restore, month-close/reorder and Sheet-mirror parity are proven.

## Deferred supporting work

Telegram Attention delivery, GROUP, COMPARE, DEBATE, broader vision/OCR and additional AI collaboration features remain later work unless explicitly reprioritized. They must not block the core inventory/database migration path.

## Immediate boundary

Proceed from the live workbook plus the established MSA skill as source-backed operational evidence. The next work is modeling and reproducing the real store semantics, not cloning every worksheet and not adding more AI surface area. No production inventory mutation or PostgreSQL canonical promotion is authorized in F6C/F6D until the explicit acceptance gates are met.