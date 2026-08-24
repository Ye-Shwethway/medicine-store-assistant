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
6. `docs/architecture/WORKBOOK_PARITY_MATRIX.md`
7. `docs/architecture/WORKBOOK_FUNCTION_CONTRACT.md`
8. `docs/architecture/INVENTORY_DATA_MODEL.md`
9. `docs/architecture/F2_SCHEMA_DECISION_PROPOSAL.md`
10. `docs/architecture/MIGRATION_AND_SHADOW_VALIDATION.md`
11. `docs/architecture/SHEET_MIRROR_AND_COMPATIBILITY.md`
12. `docs/architecture/MONTHLY_LIFECYCLE.md`
13. `docs/architecture/CMS_CATALOGUE_VERSIONING.md`
14. `docs/checkpoints/F6C_START_2026-08-24.md`
15. issue #26 current deployment evidence when runtime truth matters

Treat newer verified repository/runtime/source evidence as authoritative over remembered chat context.

## Current project priority

The AI Workspace is now an accepted supporting foundation, not the immediate development center.

**Current bounded slice: F6C Workbook Parity Lock.**

**Next bounded slice: F6D Canonical Inventory Schema Parity + Fresh Shadow Import.**

Telegram Attention delivery, GROUP, COMPARE, DEBATE and broader AI expansion are deferred behind the core inventory/database path unless explicitly reprioritized.

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

Lock the real operational workbook contract from authorized current source evidence:

- Main Stock exact columns, formulas, editability and identity/lot behavior;
- Daily Usage A:D sync, Day 1–31 semantics, totals/remaining, remarks/expiry and rollover;
- This Month Received exact projection behavior;
- Reorder exact formula/threshold/rounding behavior;
- Final Reorder copy/edit/submission/archive behavior;
- CMS catalogue/price-list structure, versioning and identity rules;
- transfer/receipt intake structure and mapping/new-lot behavior;
- monthly close / Excel Master copy-reset-archive behavior and required macros/formulas.

Do not fill unknown behavior from memory. Mark it unresolved until source-backed or Owner-confirmed.

## F6D direction after F6C

Implement only schema/domain changes proven necessary by the parity lock, then perform a fresh non-canonical shadow import from an authorized current source snapshot with provenance and reconciliation.

Core identity remains:

- local `product_id` is stable operational identity;
- `lot_id` represents physical/operational lot, normally product + expiry for v1;
- CMS catalogue identity is external/versioned and CMS code alone is never canonical identity;
- stock movement is transaction/ledger based;
- spreadsheet rows/order are projections, not database identifiers.

The existing F6B dataset must not be reused as an accepted baseline merely because it already exists.

## Immediate sequence

1. **CURRENT:** complete F6C source inspection + parity matrix/function contract.
2. Owner-review any unresolved formulas/workflows.
3. Start F6D schema parity changes only after F6C acceptance.
4. Fresh shadow import + reconciliation.
5. Historical bootstrap and shadow calculations.
6. Dual verification against real workbook operations.
7. Selected read-path promotion.
8. Controlled write promotion one operation class at a time.
9. Explicit DB canonical promotion only after all required parity/backup/mirror/month-close/reorder gates pass.

## Immediate boundary

Focus on reproducing the real medicine-store workflow faithfully. Do not promote PostgreSQL, enable production inventory mutation, or invent replacements for workbook behavior that has not yet been source-verified.
