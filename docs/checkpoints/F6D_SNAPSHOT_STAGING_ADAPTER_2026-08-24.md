# F6D Checkpoint — Fresh Snapshot Staging Adapter

Date: 2026-08-24

Status: **implemented and CI-verified; actual live source not yet staged in target shadow runtime; PostgreSQL remains non-canonical**

## Purpose

Upgrade the existing F6B live Google Sheet staging code so a fresh F6D snapshot can be captured with correct Product/Lot/Store/CMS mapping semantics before any shadow materialization.

## Implemented

The adapter now:

- resolves an explicit active Store (`MAIN` by default) and binds the migration batch to it;
- includes Store identity in deterministic snapshot hashing;
- converts Google Sheets numeric date serials to ISO dates;
- strips only a clearly terminal numeric `(month/year)` suffix when producing a Product-name candidate;
- preserves product-defining parentheses such as `(Adult)` and `(China)`;
- preserves the original local item name;
- records whether the terminal expiry suffix disagrees with the structured Expiry Date;
- supports valid no-expiry consumables rather than treating missing expiry alone as REVIEW;
- stages CMS Price, displayed Price, Remark, Serial Code and CS Name;
- normalizes literal `Nil`/equivalent CMS-code placeholders to unmapped;
- derives mapping hints: `ACTIVE_MATCH`, `UNMAPPED`, `REVIEW_REQUIRED`, `RECYCLED_CODE`, `CMS_DISCONTINUED`;
- keeps recycled mappings reviewable instead of auto-syncing;
- keeps CMS-discontinued local stock operationally valid when its inventory arithmetic is otherwise valid;
- accepts current Daily Usage Remaining Stock header variants;
- preserves sheet/row provenance;
- reuses the same migration batch when the exact same Store-bound snapshot is replayed.

## Verification

PR #135 validations on commit `9f7a280c357171c09572c6cdff4d9f4dfdf09b9b`:

- `Validate backend changes` — PASS, run `32750055715`.
- `Validate F6D shadow import staging` — PASS, run `32750055738`.

The targeted staging workflow proves:

- source-shaped date/expiry/Product normalization;
- product-defining parentheses preservation;
- valid no-expiry items;
- recycled/discontinued/unmapped mapping hints;
- PostgreSQL schema upgrade to F6D head;
- Main Store binding;
- staged payload persistence;
- exact snapshot replay idempotency.

## First CI correction

The first staging workflow run failed only because the synthetic test expected two `NEW_UNMAPPED` classifications across Main Stock + Daily Usage. Actual behavior correctly produced one `NEW_UNMAPPED` Main Stock row while its Daily Usage row remained SAFE because CMS mapping state belongs to Main/Product mapping evidence, not Daily Usage.

Expected counts were corrected to the semantically correct result; no staging behavior was weakened.

## Boundary

This checkpoint does **not** mean the real live workbook has been staged yet.

The adapter only captures/classifies source evidence. It does not yet create Product, Lot, CMS mapping, receipt, usage or opening-balance records from the actual live snapshot.

- `database_canonical=false`
- `migration_baseline_accepted=false`
- current Google workbook/source documents remain operationally authoritative

## Next bounded action

1. verify target shadow runtime is on migration `0022_inventory_foundation` and contains the merged adapter;
2. run the adapter against the current live workbook read-only;
3. record migration batch/store/hash/row counts and classification/mapping-hint distributions;
4. replay exact source to prove real-source staging idempotency;
5. review evidence before any source-derived movement materialization.
