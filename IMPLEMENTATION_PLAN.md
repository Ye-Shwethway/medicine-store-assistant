# Medicine Store Assistant — Implementation Plan

Status: **AI Workspace is accepted supporting infrastructure. F6B remains test-only; PostgreSQL remains non-canonical. F6C has been realigned around the Canonical Inventory Foundation. Exact legacy reorder/monthly Excel formula parity is deferred. Next implementation target: F6D Canonical Inventory Schema Parity + Fresh Shadow Import.**

## 1. Global rules

- Google Sheets/source documents remain operationally authoritative until explicit canonical DB promotion.
- PostgreSQL being deployed does **not** make it canonical.
- F6B is test-only and must never be silently promoted.
- All humans, AI agents, integrations, and jobs use typed backend operations.
- Never expose arbitrary SQL, DB credentials, VPS shell/filesystem, Sheet credentials, plaintext provider keys, passwords/tokens/recovery secrets, or unrestricted HTTP proxying to AI/client runtimes.
- Deterministic backend code owns identity, authorization, constraints, idempotency, transactions, confirmation, read-back and audit semantics.
- Provider/model choice never grants authority; participant privileges never union.
- Significant implementation/deploy/next-work changes update `ROADMAP.md`, `NEW_CHAT_BOOTSTRAP.md`, this file, and relevant architecture docs.

## 2. Accepted supporting foundation

Provider Registry, named agents, native inference, Single Chat, bounded reads, D4.8/D4.9 Work/Artifact/Review/Event/Attention substrate, external MCP federation, Owner Decisions and Web hardening are accepted supporting work.

Do not start another extended AI-only slice unless required for correctness or explicitly reprioritized.

## 3. Product architecture — LOCKED

Primary foundation:

`Product -> Lot -> Store -> Movement -> Balance -> Transfer -> CMS Mapping -> Actor/Audit`

Core rules:

> **Spreadsheet layout is configurable; inventory semantics are not arbitrary.**

> **Stock belongs to a location; product and catalogue identity do not.**

> **Store quantity truth comes from movements; totals and operational quantity columns are projections of that truth.**

Canonical docs:

- `docs/architecture/CANONICAL_INVENTORY_FOUNDATION.md`
- `docs/architecture/STORE_LOCATION_MODEL.md`
- `docs/architecture/CONFIGURABLE_OPERATIONAL_VIEW_ENGINE.md`

Human Web/Flutter edits and AI-agent MSA actions converge on the same authorized typed backend command layer.

## 4. Canonicality / write boundary

- `database_canonical=false`.
- `migration_baseline_accepted=false`.
- Existing F6B shadow data is test evidence only.
- No production inventory write, transfer, Calculator deduction, Telegram/Flutter stock mutation, automatic OCR/vision commit, arbitrary agent DB/SQL mutation, or DB canonical promotion is authorized.

## 5. CURRENT — F6C Foundation Documentation Lock

### 5.1 Canonical Product / Lot

- stable local `product_id`;
- local item name and operational metadata are mutable/display fields, not identity replacements;
- v1 normal lot boundary = Product + Expiry Date;
- moving a lot between stores does not create new Product/Lot identity;
- `No.` is display/order metadata only.

### 5.2 Store / Location

- exactly one configured Main Store plus unlimited Sub Stores;
- balance derived per `(store_id, lot_id)`;
- all balance-changing movements resolve a store;
- usage belongs to the issuing store;
- external receipt resolves destination store;
- internal transfer = one atomic typed operation with linked source-out + destination-in effects;
- current live workbook is treated as legacy Main Store context because it contains no populated Store/Location column.

### 5.3 Quantity semantics

Operational views may expose:

`Opening/Original Qty | Received Qty | Deducted/Used Qty | Current Qty | Total Stock`

Canonical rule:

```text
Current Qty
  = Opening
  + Receipts
  + Transfer In
  + Positive Adjustments
  - Usage
  - Transfer Out
  - Negative Adjustments
```

- `Received Qty` and `Deducted Qty` = period/filter aggregates.
- `Current Qty` = derived/verified location balance.
- `Total Store Stock` = sum of store balances; never a second manually editable truth.
- materialized balance caching may be added only with deterministic reconciliation against the ledger.

### 5.4 Universal CMS Catalogue

- one global/versioned CMS catalogue subsystem;
- CMS catalogue is independent of store/location;
- local Product identity does not use CMS Code as primary key;
- `product_cms_mappings` or equivalent preserves auditable/version-aware mapping;
- current catalogue price remains separate from historical receipt/source price;
- Store/Main Stock views resolve CMS Name/Code/Price through accepted current mapping.

### 5.5 Actor / Audit

Every protected operation resolves:

- stable human user or agent/service-principal identity;
- client/channel;
- operation/idempotency ID;
- timestamp;
- source/reason/evidence;
- approval/review context where applicable;
- outcome + read-back evidence.

AI proposal/review does not itself grant mutation authority.

### 5.6 Workbook/view compatibility

- Main Stock = operational stock/lot projection.
- Daily Usage = monthly pivot/edit view over dated usage events.
- This Month Received = receipt projection.
- Reorder Form = working view.
- Final Reorder = reviewed/adjusted final business output.
- Master archive = legacy compatibility/reporting output.

Do not create canonical tables merely because worksheets exist.

### 5.7 Reorder and calculation realignment

Exact legacy Estimated Reorder Qty formula/threshold/rounding is **not an F6D prerequisite**.

Future reorder is a dynamic intelligence/workflow layer and may combine:

- usage trend/history;
- current/expected stock;
- store-specific demand;
- expiry risk;
- safety stock / lead time / seasonality;
- deterministic calculations;
- AI proposal;
- agent review;
- authorized human adjustment/approval.

F6D must preserve the underlying stock and history needed for these workflows rather than locking the system to one Excel formula.

### 5.8 Monthly formula/macro realignment

Exact Excel reset/archive formulas are deferred unless they change foundational inventory identity, quantity, provenance, transfer meaning or audit truth.

Opening/migration balance provenance remains required.

### 5.9 F6C completion gate

F6C may close once the docs consistently describe Product/Lot/Store/Movement/Balance/Transfer/CMS Mapping/Actor-Audit semantics and any remaining unresolved issue would not force a different canonical foundation.

## 6. NEXT — F6D Canonical Inventory Schema Parity + Fresh Shadow Import

### 6.1 Schema slice

Implement only the minimum foundation:

1. `stores` or equivalent canonical location table;
2. one configured Main Store seed/identity;
3. location-aware `inventory_transactions` / ledger;
4. appropriate movement types including internal transfer effects;
5. receipt batch/line provenance with destination store;
6. explicit transfer header/lines or equivalent atomic typed transfer structure;
7. Product/Lot identity retained independent of location;
8. Universal CMS Catalogue versioning + Product mapping;
9. actor/audit/idempotency coverage for inventory mutations;
10. minimal indexes/queries needed for location balance and total-stock aggregation.

Do not add speculative tables for AI analysis, custom formula engines, or report-only worksheets.

### 6.2 Fresh shadow import

1. take a fresh authorized current source snapshot;
2. bind current workbook source to configured Main Store;
3. import non-canonically with provenance;
4. create/resolve Product and Lot identities;
5. establish migration/opening quantities without fabricating historical transactions;
6. reconcile current receipt/usage/CMS mapping evidence;
7. derive current Main Store balances;
8. explicitly classify unresolved mismatches;
9. do not reuse F6B as accepted baseline.

### 6.3 Foundation proof

Before F6D acceptance, prove in shadow/test:

- location balance derivation;
- all-store Total Stock aggregation;
- same lot represented in multiple stores;
- atomic transfer preserving total system quantity;
- receipt and usage provenance;
- CMS current mapping without historical-price overwrite;
- actor/audit attribution;
- Main Stock and Daily Usage projection generation.

PostgreSQL remains non-canonical after this proof until later promotion gates pass.

## 7. Subsequent implementation sequence

1. finish F6C doc alignment;
2. F6D canonical inventory schema + fresh shadow import;
3. historical bootstrap/reconciliation;
4. shadow balance/projection parity + transfer testing;
5. minimal field/computation registry + saved view definitions;
6. DB-backed Main Stock and Daily Usage presets;
7. spreadsheet-like draft/confirm/save editing over typed commands;
8. dynamic reorder/trend/AI proposal-review workflows;
9. dual verification of real operations;
10. read-path promotion;
11. controlled write promotion per operation class;
12. explicit DB canonicality promotion;
13. Sheet mirror/rebuild, exports, Flutter/Telegram and broader automation.

## 8. Immediate boundary

Keep re-reading the live Google Sheet when source structure/value behavior matters, but stop treating exact spreadsheet formulas as the center of database design.

The immediate engineering target is the canonical inventory foundation.
