# F6D Checkpoint — Canonical Inventory Schema Foundation

Date: 2026-08-24

Status: **implemented and CI-verified; PostgreSQL remains non-canonical**

## Scope completed

Migration `0022_inventory_foundation` implements the first location-aware canonical inventory schema slice:

- `stores` with one deterministic configured Main Store seed;
- `store_id` on inventory transactions;
- legacy shadow transaction backfill to Main Store context;
- `TRANSFER_OUT` / `TRANSFER_IN` movement semantics;
- store-bound migration batch provenance;
- `receipt_batches` / `receipt_lines` with destination Store and source evidence;
- `inventory_transfers` / `inventory_transfer_lines` with paired ledger linkage;
- historical/auditable `product_cms_mappings` lifecycle;
- accepted operational CMS price retention independent of unresolved newer mapping candidates;
- `inventory_location_balances` derived view;
- `inventory_total_stock` derived view.

## Verification evidence

PR #134 targeted validation used PostgreSQL 16 from an empty database.

Verified behavior:

1. Alembic upgraded from empty DB to `0022_inventory_foundation`.
2. Seeded Main Store exists.
3. Synthetic Product/Lot opened with quantity 100 in Main Store.
4. Synthetic internal transfer moved 25 from Main to Sub Store.
5. Derived balances became Main = 75, Sub = 25.
6. Derived Total Stock remained 100.
7. Transfer line successfully linked paired `TRANSFER_OUT` / `TRANSFER_IN` ledger transactions.
8. An accepted CMS mapping/price remained active while a separate newer mapping candidate stayed `REVIEW_REQUIRED`.
9. Synthetic F6D-only business fixture was removed.
10. Schema downgraded to `0021_review_orchestration_roles` and re-upgraded to head successfully.

Validation runs on commit `743de479fb185909931fae51694b7f51a887cb5e`:

- `Validate backend changes` — PASS, run `32748981523`.
- `Validate F6D inventory schema` — PASS, run `32748981530`.

## Important downgrade boundary

The first targeted CI attempt proved the F6D business semantics but failed when downgrade attempted to restore the pre-F6D transaction-type constraint while synthetic transfer rows still existed.

This was intentionally fixed in CI by removing only the synthetic F6D fixture before schema downgrade.

Do **not** make migration downgrade silently delete, convert or reinterpret genuine committed `TRANSFER_IN` / `TRANSFER_OUT` history. A real rollback after F6D-only business data exists requires an explicit data-migration/rollback decision.

## Canonicality boundary

This checkpoint does not promote PostgreSQL.

- `database_canonical=false`
- `migration_baseline_accepted=false`
- live Google workbook/source documents remain operationally authoritative
- no production inventory write path was introduced

## Next bounded target

Fresh Main Store shadow import + reconciliation:

1. take a fresh authorized read-only workbook snapshot;
2. hash/stage it as a migration batch bound to Main Store;
3. preserve sheet/row provenance;
4. resolve Product + structured-expiry Lot identities;
5. create provenance-bearing migration opening balances without fabricating history;
6. reconcile CMS mapping lifecycle states including recycled/discontinued/review-required cases;
7. derive Main Store balances and compare with live Main Stock;
8. prove replay idempotency;
9. generate shadow Main Stock/Daily Usage projection evidence;
10. remain non-canonical.
