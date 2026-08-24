# F6D Materialization + Catalogue + Reconciliation Checkpoint — 2026-08-25

Status: **shadow Product/Lot/opening materialization verified; live CMS catalogue version imported; deterministic CMS reconciliation plan verified; non-accepted mapping review-state staging in progress. PostgreSQL remains non-canonical.**

## Authority boundary

- `database_canonical=false`
- `migration_baseline_accepted=false`
- live Google workbook/source evidence remains operationally authoritative
- no production inventory mutation is authorized by this checkpoint
- no CMS mapping is accepted solely because code/name/price appears compatible
- no catalogue import or review-state staging changes historical inventory movements

## Main Store shadow materialization — VERIFIED

Fresh staged source evidence remains:

- Main Stock source rows: 823
- Daily Usage source rows: 823
- staged evidence rows: 1,646
- inventory source hash: `c212d7da6192e7e20f340e7b302436f588dfb0fa191459fd572dfdb46f23ba76`

Source-safe materialization produced:

- Products: 670
- Lots: 799
- OPENING_BALANCE movements: 679
- total opening quantity: 72,009
- zero-balance identity-only Lots: 120
- read-back mismatches: 0

Immediate replay created 0 Products, 0 Lots and 0 additional inventory transactions.

Held rather than guessed:

- duplicate Product+Expiry source rows: 4
- inventory-semantic review rows: 14
- Unit-ambiguous rows: 6

## Live CMS catalogue — VERIFIED

Imported reference dataset:

- sheet: `CMS_Price_List_202608`
- title: `August 2026 Updated Price List (Yuan) - 02.08.2026`
- effective date: 2026-08-02
- catalogue version id: `34947c29-6427-4b7c-9fb8-ba8ffe3278b0`
- source hash: `6f221152024c9a06b73f7f7115097abfb688a37a6ba6bf0be78345f3b70dd116`
- catalogue rows: 6,891
- unique CMS codes: 6,891
- duplicate codes: 0
- blank codes: 0
- invalid prices: 0
- blank-price source row: 6442

Catalogue replay reused the same version and did not change Products, Lots, inventory transactions or Product-CMS mappings.

## Deterministic CMS reconciliation — VERIFIED READ ONLY

The planner compares materialized local Products with current Main Stock CMS evidence and the imported catalogue. Code equality is evidence, not identity authority.

Current 670 Product classifications:

- `CONTINUITY_EXACT_NAME_PRICE_SAME`: 526
- `CONTINUITY_EXACT_NAME_PRICE_CHANGED`: 77
- `REVIEW_MULTIPLE_SOURCE_CODES`: 30
- `CMS_DISCONTINUED_LOCAL_RETAINED`: 19
- `REVIEW_CODE_NAME_MISMATCH`: 9
- `UNMAPPED`: 6
- `REVIEW_MISSING_SOURCE_CMS_NAME`: 1
- `REVIEW_MULTIPLE_SOURCE_CMS_NAMES`: 1
- `REVIEW_RECYCLED_CODE`: 1

Thus deterministic continuity candidates = 603 Products and review/unmapped/discontinued/recycled cases = 67 Products.

These counts do **not** mean 603 mappings are accepted. They are candidate evidence only.

## Current bounded implementation

Stage durable non-accepted review state so manual/AI-assisted reconciliation has a persistent queue without crossing acceptance authority.

Required invariant:

- continuity and ordinary ambiguous candidates -> `REVIEW_REQUIRED`
- recycled evidence -> `RECYCLED_CODE`
- discontinued local-retained -> `CMS_DISCONTINUED`
- no accepted CMS code -> `UNMAPPED`
- `ACTIVE_MATCH=0`
- `accepted_operational_price IS NULL` for every staged review row
- source hashes are execution guards
- immediate replay creates no duplicate rows
- Products/Lots/inventory transaction counts remain unchanged

## Next after review-state staging

1. expose/filter review-state evidence for Owner/manual review;
2. add optional AI candidate ranking/explanation for ambiguous cases without granting mutation authority;
3. implement typed mapping acceptance separately;
4. acceptance must record actor/operation/reason/read-back and supersede history safely;
5. only accepted mapping state may feed an authorized operational CMS-price update workflow;
6. PostgreSQL remains shadow/non-canonical until later explicit promotion gates pass.
