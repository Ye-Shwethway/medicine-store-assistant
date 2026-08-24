# Medicine Store Assistant — Project Roadmap

Status: **F6C Canonical Inventory Foundation is locked. F6D schema foundation is implemented and CI-verified on PostgreSQL 16. PostgreSQL remains non-canonical. Current bounded target: fresh Main-Store shadow snapshot/import + reconciliation.**

The live Google workbook/source documents remain operationally authoritative. `migration_baseline_accepted=false`; `database_canonical=false`.

## Product direction — LOCKED

MSA is a canonical inventory system with configurable spreadsheet-like views and optional AI assistance, not a fixed spreadsheet clone and not an AI-only application.

Foundation:

`Product -> Lot -> Store -> Movement -> Balance -> Transfer -> CMS Mapping -> Actor/Audit`

Core rules:

> **Spreadsheet layout is configurable; inventory semantics are not arbitrary.**

> **Stock belongs to a location; product and catalogue identity do not.**

> **Store quantity truth comes from movements; totals and operational quantity columns are projections of that truth.**

> **AI enhances store operation but must not become a single point of operational failure.**

MSA targets one Main Store plus unlimited Sub Stores, PostgreSQL-backed durable inventory, shared human/AI typed operations, Web/Flutter/Telegram/ChatGPT/automation clients, deterministic fallbacks when AI is unavailable, and AI-assisted reconciliation/analysis when available.

Canonical architecture:

- `docs/architecture/CANONICAL_INVENTORY_FOUNDATION.md`
- `docs/architecture/STORE_LOCATION_MODEL.md`
- `docs/architecture/CMS_MAPPING_LIFECYCLE.md`
- `docs/architecture/REORDER_BASELINE_AND_AI_ENHANCEMENT.md`
- `docs/architecture/CONFIGURABLE_OPERATIONAL_VIEW_ENGINE.md`

## Canonicality / authority boundary

- Google Sheet/source documents remain the current operational source of truth.
- PostgreSQL remains deployed shadow/test only.
- F6B data is test evidence and is not the F6D migration baseline.
- No production inventory write, internal transfer execution, Calculator deduction, Telegram/Flutter stock mutation, automatic OCR/vision commit, arbitrary agent SQL/DB mutation, or DB canonical promotion is authorized.
- Provider/model selection never grants authority; participant privileges never union.

## Accepted supporting foundation

AI Workspace, Provider Registry, named agents, native inference, D4.8/D4.9 Work/Artifact/Review/Event/Attention substrate, external MCP federation, Owner Decisions and Web Production Reliability Hardening remain accepted supporting infrastructure. Do not resume extended AI-only work unless explicitly reprioritized or required for correctness.

## F6C — COMPLETE ARCHITECTURE LOCK

Locked semantics include:

- stable local Product identity;
- v1 normal Lot identity = Product + Expiry Date;
- exactly one configured Main Store plus unlimited Sub Stores;
- same Product/Lot may exist in multiple stores;
- balance is location-scoped and movement-derived;
- Total Store Stock is the sum of location balances, not a second editable truth;
- external receipt and internal transfer are distinct business events;
- internal transfer preserves Product/Lot identity and requires linked source-out + destination-in effects;
- usage/deduction belongs to the actual issuing store;
- Universal CMS Catalogue is global/versioned and separate from local Product identity;
- CMS mappings are historical/auditable lifecycle records, never blind code sync;
- last accepted CMS mapping/operational price remains usable while a newer catalogue is unresolved;
- current catalogue price is separate from historical receipt/source price;
- human and AI operations resolve stable actor identity, operation/idempotency ID, audit and read-back;
- Main Stock and Daily Usage are operational projections/edit surfaces over canonical data.

### Reorder resilience

Exact legacy Estimated Reorder Qty formula parity is not a canonical-schema blocker. Future reorder has a deterministic local/backend baseline plus optional AI enhancement/review. AI outage must not force item-by-item manual calculation.

### CMS assisted mapping

New catalogue versions are deterministically diffed/screened. Ambiguous, recycled, discontinued or new mappings go to review. AI may help rank/explain candidates; manual review remains available when AI is unavailable. Existing accepted mapping/price state keeps ordinary inventory operational.

## F6D — ACTIVE

### Schema foundation — IMPLEMENTED + VERIFIED

Migration `0022_inventory_foundation` introduces:

- canonical `stores` with one deterministic Main Store seed;
- non-null `store_id` on inventory transactions with legacy shadow rows bound to Main Store;
- `TRANSFER_OUT` / `TRANSFER_IN` ledger semantics;
- store-bound migration provenance;
- `receipt_batches` / `receipt_lines` with destination Store and source evidence;
- `inventory_transfers` / `inventory_transfer_lines` with linked paired ledger effects;
- `product_cms_mappings` with lifecycle state and accepted operational price retention;
- `inventory_location_balances` derived view;
- `inventory_total_stock` derived view.

Targeted PostgreSQL CI proves from an empty DB:

- migration to head;
- Main/Sub independent balances;
- total-stock conservation through transfer;
- transfer-line linkage;
- unresolved new CMS candidate does not erase the accepted mapping/price;
- schema downgrade/re-upgrade after removal of synthetic F6D-only business fixtures.

Important downgrade rule: committed F6D-only transfer history must never be silently coerced into old movement semantics merely to make a downgrade succeed. A real downgrade with such data would require an explicit data-migration decision.

### CURRENT — fresh Main Store shadow import

Next bounded work:

1. take a fresh authorized current source snapshot from the live workbook;
2. bind the source batch explicitly to the configured Main Store;
3. create repeatable non-canonical import/reconciliation tooling;
4. resolve stable Product and expiry-Lot identities;
5. establish opening/migration quantities with provenance without fabricating historical transactions;
6. reconcile available receipt, usage and CMS mapping/price evidence;
7. preserve `RECYCLED_CODE`, `CMS_DISCONTINUED`, `REVIEW_REQUIRED` and `UNMAPPED` states rather than forcing clean mappings;
8. derive current Main Store balances;
9. classify every mismatch explicitly;
10. prove useful Main Stock and Daily Usage projections from DB state;
11. keep PostgreSQL non-canonical until explicit later acceptance.

## Subsequent path

1. Fresh F6D shadow import + reconciliation.
2. Historical bootstrap from strongest available evidence without inventing movements.
3. Shadow balance/projection parity and transfer tests.
4. Minimal field/computation registry + saved view definitions.
5. DB-backed Main Stock and Daily Usage presets.
6. Spreadsheet-like draft/confirm/save editing over typed commands.
7. Deterministic reorder baseline engine + versioned strategy attribution.
8. CMS assisted reconciliation workflow + optional AI candidate reasoning.
9. AI-enhanced reorder/trend proposal-review workflows.
10. Dual verification of real operational events.
11. Selected DB read-path promotion.
12. Controlled write promotion one operation class at a time.
13. Explicit DB canonicality promotion only after migration/recovery/reconciliation/write gates pass.
14. Sheet mirror/rebuild, monthly exports, Flutter/Telegram expansion and further automation.

## Immediate boundary

Do not let legacy spreadsheet formulas or report formatting dictate the canonical schema. Continue re-reading the live workbook whenever source behavior matters. The next engineering work is the fresh Main Store shadow import and reconciliation, not production canonical promotion.
