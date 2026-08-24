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
7. `docs/architecture/WORKBOOK_PARITY_MATRIX.md`
8. `docs/architecture/WORKBOOK_FUNCTION_CONTRACT.md`
9. `docs/architecture/INVENTORY_DATA_MODEL.md`
10. `docs/architecture/F2_SCHEMA_DECISION_PROPOSAL.md`
11. `docs/architecture/MIGRATION_AND_SHADOW_VALIDATION.md`
12. `docs/architecture/SHEET_MIRROR_AND_COMPATIBILITY.md`
13. `docs/architecture/MONTHLY_LIFECYCLE.md`
14. `docs/architecture/CMS_CATALOGUE_VERSIONING.md`
15. `skills/medicine-store-assistant/SKILL.md`
16. task-relevant files under `skills/medicine-store-assistant/references/`
17. `docs/checkpoints/F6C_START_2026-08-24.md`
18. issue #26 current deployment evidence when runtime truth matters

Treat newer verified repository/runtime/source evidence as authoritative over remembered chat context.

## Current project priority

The AI Workspace is now an accepted supporting foundation, not the immediate development center.

**Current bounded slice: F6C Workbook Parity Lock with canonical-domain/configurable-view separation.**

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

## F6C mission

Lock the inventory semantics from authorized live source evidence and the established MSA skill.

Priority:

1. Main Stock product/lot identity and field semantics.
2. Daily Usage actual movement and month-grid behavior.
3. CMS catalogue/mapping/current-price behavior.
4. Batch intake, idempotency, new expiry lots and fixed-asset routing.
5. Reorder inputs/configuration/calculated recommendation.
6. Month rollover/opening carry-forward and audit semantics.
7. Store/location model for Main Store plus unlimited Sub Stores.

Classify important fields as:

- canonical entity/domain field;
- canonical event/transaction;
- deterministic computed field;
- command-backed editable field;
- display/helper/projection-only field;
- approved snapshot/archive output;
- unresolved Owner decision.

### Legacy derived surfaces

Owner-confirmed semantics:

- `This Month Received` — filtered/derived display from Main Stock received activity.
- `Reorder Form` — filtered/derived projection of Main Stock calculated Estimated Reorder Qty.
- `Final Reorder Form` — copied working output that may be manually adjusted before submission.
- Master Data archive — preserves approved/final monthly output.

These are primarily view/working-document/archive concerns and must not drive canonical schema design.

## Existing MSA skill as operational evidence

The repo skill already captures important proven workflows and constraints, including:

- local product vs CMS identity vs stock-lot separation;
- expiry-lot suffix normalization;
- Main Stock/Daily Usage synchronization semantics;
- actual movement preservation even when FIFO/FEFO is violated;
- batch-intake idempotency and new-lot behavior;
- recycled CMS identity handling;
- current catalogue price vs historical transaction truth;
- fixed-assets separation;
- Audit_Log/read-back/visual-marking discipline.

Do not re-invent these rules during F6C; reconcile them with live source evidence and future canonical-domain design.

## F6D direction after F6C

Implement only schema/domain changes proven necessary by the parity lock, then perform a fresh non-canonical shadow import from an authorized current source snapshot with provenance and reconciliation.

Core identity remains:

- `store/location` is a canonical dimension, not a separate schema per store;
- local `product_id` is stable operational identity;
- `lot_id` represents physical/operational lot, normally product + expiry for v1;
- CMS catalogue identity is external/versioned and CMS code alone is never canonical identity;
- receipts, usage and adjustments are transaction/event based;
- balances are derived/verified from canonical movements;
- spreadsheet rows/order are projections, not database identifiers.

The existing F6B dataset must not be reused as an accepted baseline merely because it already exists.

## Immediate sequence

1. **CURRENT:** complete F6C domain/field classification and parity contracts.
2. Owner-review only genuinely unresolved semantics.
3. Start F6D Store/Product/Lot/Catalogue/Receipt/Usage/Adjustment/Ledger/Audit schema parity.
4. Fresh shadow import + reconciliation.
5. Prove Main Stock and Daily Usage projections from DB.
6. Add minimal field/computation registry + saved view definitions.
7. Add spreadsheet-like draft/confirm/save editing over typed commands.
8. Dual verification against real workbook operations.
9. Selected read-path promotion.
10. Controlled write promotion one operation class at a time.
11. Explicit DB canonical promotion only after required parity/backup/mirror/month-close/reorder gates pass.

## Immediate boundary

Focus on reproducing the real medicine-store semantics faithfully while keeping presentation configurable. Do not promote PostgreSQL, enable production inventory mutation, or let legacy worksheet layout dictate canonical schema.