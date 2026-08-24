# F6D Main-Primary Materialization Lock — 2026-08-24

Status: **LOCKED / CONTINUING TO IMPLEMENTATION**

## Runtime evidence reconciled

Fresh F6D staging proved that the 1,646 staged records are two worksheet evidence sets combined, not 1,646 canonical inventory lines:

- Main Stock source item rows: one inventory-facing source set;
- Daily Usage source item rows: mirrored/monthly-usage source set for the same domain;
- total staged source records: both sets combined;
- canonical Product/Lot candidates must be derived from Main Stock only.

No Product/Lot/opening-balance materialization had occurred at the time this decision was locked.

## Owner-approved architecture

- Main Stock and Daily Usage are user-facing projections/edit surfaces, not canonical DB tables.
- Canonical storage remains normalized: Product -> Lot -> Store -> Movement -> Balance.
- Main Stock is primary migration identity/current-balance evidence.
- Daily Usage joins to the Main Stock-derived candidate and must not independently create duplicate Product/Lot/balance rows.
- Daily day 1-31 columns are future pivots over dated usage events, not physical DB columns.
- Main Stock quantity columns are projections/aggregates over movement truth, not independent mutable truth columns.
- CMS Catalogue remains a separate global/versioned dataset.
- CMS mapping uncertainty must not automatically block otherwise-safe local Product/Lot inventory materialization.

## Count terminology

From this checkpoint forward, reports must distinguish:

- Main Stock source rows;
- Daily Usage source rows;
- staged source records;
- Main-derived canonical lot candidates;
- unique Products;
- unique Lots.

Do not call the combined staged-source count the inventory row count.

## Immediate implementation

1. update staging summaries to expose per-sheet and candidate counts;
2. implement a dry-run Main-primary materialization planner;
3. detect duplicate/ambiguous Product+Expiry candidate keys before any write;
4. join Daily Usage as evidence only;
5. inspect real planner results;
6. only then materialize source-safe Product/Lot/opening-balance rows in shadow PostgreSQL with idempotent provenance;
7. keep `database_canonical=false` and `migration_baseline_accepted=false`.
