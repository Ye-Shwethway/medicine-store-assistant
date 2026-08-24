# Medicine Store Assistant — New Chat Bootstrap

Use this file for project-development continuity in a fresh chat.

## Canonical repository

`https://github.com/Ye-Shwethway/medicine-store-assistant`

## Mandatory reconciliation order

Before changing code/config/schema/runtime, read:

1. `AGENTS.md`
2. `NEW_CHAT_BOOTSTRAP.md`
3. `ROADMAP.md`
4. `IMPLEMENTATION_PLAN.md`
5. `docs/architecture/F6C_WORKBOOK_PARITY_LOCK.md`
6. `docs/architecture/CONFIGURABLE_OPERATIONAL_VIEW_ENGINE.md`
7. `docs/architecture/STORE_LOCATION_MODEL.md`
8. `docs/architecture/WORKBOOK_PARITY_MATRIX.md`
9. `docs/architecture/WORKBOOK_FUNCTION_CONTRACT.md`
10. `docs/architecture/INVENTORY_DATA_MODEL.md`
11. `docs/architecture/F2_SCHEMA_DECISION_PROPOSAL.md`
12. `docs/architecture/MIGRATION_AND_SHADOW_VALIDATION.md`
13. `docs/architecture/SHEET_MIRROR_AND_COMPATIBILITY.md`
14. `docs/architecture/MONTHLY_LIFECYCLE.md`
15. `docs/architecture/CMS_CATALOGUE_VERSIONING.md`
16. `skills/medicine-store-assistant/SKILL.md`
17. task-relevant files under `skills/medicine-store-assistant/references/`
18. `docs/checkpoints/F6C_START_2026-08-24.md`
19. `docs/checkpoints/F6C_STORE_LOCATION_2026-08-24.md`
20. issue #26 current deployment evidence when runtime truth matters

Treat newer verified repository/runtime/source evidence as authoritative over remembered chat context.

## Current project priority

The AI Workspace is now an accepted supporting foundation, not the immediate development center.

**Current bounded slice: F6C Workbook/Domain Parity Lock. Core Main Stock/Daily Usage/CMS/intake/Store-Location semantics are locked. Remaining blockers: month rollover/carry-forward semantics and exact legacy reorder calculation.**

**Next bounded slice: F6D Canonical Inventory Schema Parity + Fresh Shadow Import.**

Telegram Attention delivery, GROUP, COMPARE, DEBATE and broader AI expansion are deferred behind the core inventory/database path unless explicitly reprioritized.

## Product direction — LOCKED

MSA must support:

- one Main Store plus unlimited Sub Stores;
- human staff and AI agents over one backend;
- Web, Flutter, Telegram, ChatGPT and automation clients;
- durable operation with or without ChatGPT/Google Sheets;
- preset and user-defined spreadsheet-like operational tables.

Core rule:

> **Spreadsheet layout is configurable; inventory semantics are not arbitrary.**

Architecture:

`canonical inventory domain -> field/computation registry -> configurable operational views -> draft/confirm/save -> typed domain commands -> audit/read-back`

Human UI edits and AI-agent MSA actions converge on the same typed backend operation layer. Neither receives arbitrary SQL authority.

## Store / Location — LOCKED CORE

Core rule:

> **Stock belongs to a location; product and catalogue identity do not.**

The same Product/Lot may have balances in Main Store and any number of Sub Stores. Balance is derived per `(store_id, lot_id)`.

Internal transfer preserves product/lot identity and atomically decreases source location plus increases destination location under one typed operation/idempotency identity.

Current schema gap:

- no canonical store/location entity;
- current `inventory_transactions` is lot-only;
- existing F2 movement types do not represent internal transfer.

F6D must correct these gaps.

The current live `Medicine Store Cloud` has no populated Store/Location/Sub Store field in Main Stock or Daily Usage. Treat it as the configured legacy Main Store context during migration rather than changing its production columns.

## Current canonicality boundary

- Google Sheet/source documents remain operationally authoritative.
- PostgreSQL is deployed but **not canonical**.
- Existing F6B data is test-only and not an accepted migration baseline.
- `database_canonical=false`; `migration_baseline_accepted=false`.
- No production inventory write, transfer, Calculator deduction, Telegram/Flutter stock mutation, automatic OCR/vision commit, arbitrary agent SQL/DB mutation, or DB canonical promotion is authorized.

## Accepted AI/Web foundation

Accepted supporting work includes named agents, Provider Registry/saved models, native inference, Single Chat, bounded native reads, D4.8 Work/Artifact/Review/Event/Attention substrate, external MCP federation, feedback passes, Review export/delete/navigation, Web Production Reliability Hardening, D4.9 discussion + durable Owner Decisions, and PR #129 `Talk to -> All agents` ordinary discussion broadcast.

Latest AI UX runtime anchor:

- source SHA `75bfb89eb83b5cedfffa9148db454b1245269593`
- deploy run `32736647711`
- issue #26 `status=success`

Small Review UI polish may be folded into later touched Web work; do not start another extended AI-only slice for cosmetic changes.

## F6C source rules

Use the live Google Sheet repeatedly whenever current field/value behavior matters.

Representative Main Stock/Daily Usage `FORMULA` reads return materialized values, not exact legacy Excel formulas. Therefore do not reconstruct formula/macro behavior from those values alone.

The repo MSA skill remains established operational evidence for:

- local product vs CMS identity vs stock-lot separation;
- expiry-lot suffix normalization;
- Main Stock/Daily Usage synchronization semantics;
- actual movement preservation even when FIFO/FEFO is violated;
- batch-intake idempotency and new-lot behavior;
- recycled CMS identity handling;
- current catalogue price vs historical transaction truth;
- fixed-assets separation;
- Audit_Log/read-back/visual-marking discipline.

## Legacy derived surfaces

Owner-confirmed semantics:

- `This Month Received` — filtered/derived display from Main Stock received activity.
- `Reorder Form` — filtered/derived projection of Main Stock calculated Estimated Reorder Qty.
- `Final Reorder Form` — copied working output that may be manually adjusted before submission.
- Master Data archive — preserves approved/final monthly output.

These are primarily view/working-document/archive concerns and must not drive canonical schema design.

## Remaining F6C blockers

1. Month rollover/carry-forward semantics that affect canonical monthly state.
2. Exact legacy reorder formula/threshold/rounding and store scope.

Do not let cosmetic/report-only Excel behavior block F6D unless it changes inventory truth or required historical reconstruction.

## F6D direction after F6C

Implement only schema/domain changes proven necessary by the parity lock, then perform a fresh non-canonical shadow import from an authorized current source snapshot with provenance and reconciliation.

Core identity remains:

- `store/location` is a canonical dimension, not a separate schema per store;
- local `product_id` is stable operational identity;
- `lot_id` represents physical/operational lot, normally product + expiry for v1;
- CMS catalogue identity is external/versioned and CMS code alone is never canonical identity;
- receipts, usage, adjustments and transfers are typed event/transaction based;
- balances are derived/verified per store+lot from canonical movements;
- spreadsheet rows/order are projections, not database identifiers.

The existing F6B dataset must not be reused as an accepted baseline merely because it already exists.

## Immediate sequence

1. **CURRENT:** resolve/bound month rollover and exact reorder parity gates.
2. Start F6D location-aware Store/Product/Lot/Catalogue/Receipt/Usage/Transfer/Adjustment/Ledger/Audit schema parity.
3. Fresh shadow import + reconciliation bound to Main Store.
4. Prove Main Stock and Daily Usage projections from DB.
5. Add minimal field/computation registry + saved view definitions.
6. Add spreadsheet-like draft/confirm/save editing over typed commands.
7. Dual verification against real workbook operations.
8. Selected read-path promotion.
9. Controlled write promotion one operation class at a time.
10. Explicit DB canonical promotion only after required parity/backup/mirror/month-close/reorder gates pass.

## Immediate boundary

Focus on reproducing the real medicine-store semantics faithfully while keeping presentation configurable. Do not promote PostgreSQL, enable production inventory mutation, or let legacy worksheet layout dictate canonical schema.
