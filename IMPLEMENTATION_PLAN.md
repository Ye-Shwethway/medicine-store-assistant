# Medicine Store Assistant — Implementation Plan

Status: **F6C architecture is locked. F6D canonical inventory schema foundation is implemented and PostgreSQL-CI verified. PostgreSQL remains non-canonical. Current bounded work: fresh Main Store shadow import + reconciliation.**

## 1. Global rules

- Google Sheets/source documents remain operationally authoritative until explicit canonical DB promotion.
- PostgreSQL being deployed does **not** make it canonical.
- F6B remains test-only and must never be silently promoted or reused as the accepted F6D baseline.
- All humans, AI agents, integrations and jobs use typed backend operations.
- Never expose arbitrary SQL, DB credentials, VPS shell/filesystem, Sheet credentials, plaintext provider keys, passwords/tokens/recovery secrets, or unrestricted HTTP proxying to AI/client runtimes.
- Deterministic backend code owns identity, authorization, constraints, idempotency, transactionality, confirmation, read-back and audit semantics.
- Essential store workflows degrade safely when AI providers are unavailable.
- Significant implementation/deploy/next-work changes update `ROADMAP.md`, `NEW_CHAT_BOOTSTRAP.md`, this file, relevant architecture docs and a bounded checkpoint.

## 2. Locked product architecture

Foundation:

`Product -> Lot -> Store -> Movement -> Balance -> Transfer -> CMS Mapping -> Actor/Audit`

Rules:

- spreadsheet layout is configurable; inventory semantics are not arbitrary;
- stock belongs to a location; Product/CMS identity does not;
- quantity truth comes from movements;
- Total Stock is aggregate truth, never a second editable balance;
- AI enhances workflows but is not an availability dependency.

Canonical docs:

- `docs/architecture/CANONICAL_INVENTORY_FOUNDATION.md`
- `docs/architecture/STORE_LOCATION_MODEL.md`
- `docs/architecture/CMS_MAPPING_LIFECYCLE.md`
- `docs/architecture/REORDER_BASELINE_AND_AI_ENHANCEMENT.md`
- `docs/architecture/CONFIGURABLE_OPERATIONAL_VIEW_ENGINE.md`

## 3. Canonicality / write boundary

- `database_canonical=false`.
- `migration_baseline_accepted=false`.
- no production inventory write/transfer/usage deduction or DB canonical promotion is authorized;
- no arbitrary AI SQL/DB mutation;
- current live workbook remains the operational authority.

## 4. F6C — COMPLETE

Locked semantics:

- stable `product_id`;
- normal v1 Lot = Product + Expiry Date;
- exactly one configured Main Store + unlimited Sub Stores;
- current balance per `(store_id, lot_id)`;
- internal transfer = atomic source-out + destination-in under one operation;
- external receipt = destination Store + source provenance;
- CMS Catalogue = global/versioned external domain;
- Product-CMS mapping = historical/auditable lifecycle, not direct code sync;
- last accepted CMS mapping/operational price remains usable while newer catalogue mapping is unresolved;
- current CMS catalogue price != historical receipt/source price;
- human/agent actor + operation/idempotency + audit/read-back required;
- Main Stock/Daily Usage are projections/edit surfaces, not DB table shapes.

Reorder uses a future deterministic baseline plus optional AI enhancement. Exact legacy formula parity is not required for F6D.

## 5. F6D — ACTIVE

### 5.1 Schema foundation — DONE

Migration `0022_inventory_foundation` implements:

1. `stores` with deterministic seeded `MAIN` store;
2. `store_id` on `inventory_transactions` and legacy shadow-row Main Store backfill;
3. movement types `TRANSFER_OUT` / `TRANSFER_IN`;
4. store association on migration batches;
5. `receipt_batches` / `receipt_lines`;
6. `inventory_transfers` / `inventory_transfer_lines`;
7. historical/auditable `product_cms_mappings` lifecycle;
8. accepted operational CMS price retention;
9. `inventory_location_balances` derived view;
10. `inventory_total_stock` derived view.

### 5.2 Schema proof — DONE

Targeted PostgreSQL 16 CI must and now does prove:

- empty DB -> Alembic head;
- required tables/views exist;
- Main Store seed exists;
- synthetic Main balance 100 -> transfer 25 to Sub -> Main 75 / Sub 25 / total 100;
- transfer header/line links the paired transfer ledger entries;
- an unresolved new CMS candidate does not remove the last accepted mapping/price;
- synthetic F6D-only business data is removed before schema reversibility proof;
- downgrade to `0021_review_orchestration_roles` then re-upgrade to head succeeds.

Do **not** modify downgrade logic to silently delete or reinterpret genuine committed transfer history. A production downgrade containing F6D-only business data would require an explicit data-migration plan.

### 5.3 CURRENT — fresh source snapshot/import

Implement the next bounded slice:

1. fresh read-only snapshot of the authorized live workbook;
2. deterministic source hash + migration batch bound to `MAIN`;
3. source-row capture with sheet/row provenance;
4. stable Product resolution using local operational identity, not CMS Code;
5. Lot resolution using structured Expiry Date under v1 rules;
6. explicit migration/opening transactions for accepted pre-existing lot quantity;
7. reconcile current CMS mapping state into lifecycle statuses without forcing ambiguous matches;
8. preserve last accepted operational CMS price separately from current catalogue candidate price;
9. preserve receipt/usage evidence where source support is strong enough; do not fabricate history;
10. derive Main Store balances and compare with live Main Stock current state;
11. classify SAFE/REVIEW/CONFLICT/NEW_UNMAPPED-style mismatches explicitly;
12. prove import idempotency by replaying the same snapshot without duplicate stock movement;
13. generate shadow Main Stock and Daily Usage projection evidence;
14. remain non-canonical.

### 5.4 Import implementation constraints

- Never identify Product solely from CMS Code.
- Do not infer Product identity solely from item-name expiry suffix.
- Structured Expiry Date is the primary lot-expiry source unless stronger evidence overrides it.
- Preserve local names and suspicious/recycled/discontinued CMS states.
- Do not turn current Main Stock `Received Stock` into a fabricated historical receipt when provenance is insufficient; classify/reconcile instead.
- One explicit `OPENING_BALANCE` per accepted migrated pre-existing lot is the F2 migration representation.
- Normal monthly rollover does not create repeated opening movements.
- Every generated movement requires deterministic operation/idempotency identity and source provenance.

## 6. Later sequence

1. Complete fresh F6D shadow import + reconciliation.
2. Historical bootstrap from strongest available evidence.
3. Shadow balance/projection parity + transfer tests.
4. Field/computation registry + saved views.
5. DB-backed Main Stock/Daily Usage presets.
6. Spreadsheet-like draft/confirm/save editing over typed commands.
7. Deterministic reorder baseline engine.
8. CMS assisted mapping workflow + optional AI candidate reasoning.
9. AI-enhanced reorder/trend proposal-review.
10. Dual verification of real operations.
11. Selected read-path promotion.
12. Controlled write promotion per operation class.
13. Explicit DB canonicality promotion.
14. Sheet mirror/rebuild, exports and multi-client expansion.

## 7. Immediate boundary

The next change should be import/reconciliation tooling and fresh read-only source evidence. Do not start production inventory writes, full AI matching, final reorder engine, or broad UI expansion inside this slice.
