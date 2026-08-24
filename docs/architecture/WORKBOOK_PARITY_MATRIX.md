# Workbook Parity Matrix

Status: **F6C source-backed working artifact — canonical inventory foundation aligned; exact legacy formulas are compatibility follow-up, not F6D blockers**

This matrix records behavior supported by the authorized live `Medicine Store Cloud`, established MSA skill contract, or explicit Owner confirmation.

## Source-resolution rule

- Live Google Sheet = current operational structure/value evidence.
- MSA skill = established operational behavior/authority contract.
- Owner-confirmed workflow = accepted business-process evidence.
- Original Excel workbook = optional higher-resolution compatibility source where exact legacy formula/macro behavior is later needed.

Representative `FORMULA` reads of current Main Stock/Daily Usage returned materialized values rather than exact Excel formulas. Do not infer exact legacy formulas from those values.

## Main Stock — verified operational projection

| Col | Header | Source-backed meaning | Canonical/view classification | Future target |
| --- | --- | --- | --- | --- |
| A | No. | sequential human-facing order | display/order only | generated view row/order |
| B | Items | local item/lot-facing display name | Product display + Lot presentation | Product + Lot projection |
| C | Expiry Date | structured expiry | canonical Lot field | `lot.expiry_date` |
| D | Date Status | expiry/status output | computed/display | expiry computation |
| E | Unit | operational unit | Product/operational metadata | Product unit policy |
| F | Remaining Stock | opening/base quantity in current workbook flow | migration/selected-period opening context | movement/snapshot-derived opening projection |
| G | Received Stock | current-period receipt quantity | movement aggregate | SUM receipt movements for Store+Lot+period |
| H | Stock Status Today | current calculated balance | movement-derived balance | Store+Lot Current Qty |
| I | Reorder Level | legacy planning/config input | workflow/config metadata | optional planning config |
| J | This Month Usage | monthly usage total | movement aggregate | SUM usage movements for Store+Lot+period |
| K | Stock Remark | reorder/status aid | computed/display | workflow/view output |
| L | Reorder Surplus Factor | legacy planning factor | workflow/config metadata | optional planning config |
| M | Estimated Request Qty | legacy calculated recommendation | workflow/computed output | dynamic reorder proposal output |
| N | Shortage Date | legacy forecast output | workflow/computed output | forecast module output |
| O | CMS Price | current mapped CMS catalogue price | external catalogue projection | current accepted CMS mapping/catalogue price |
| P | Price | compatibility-derived pricing output | computed/display | compatibility/pricing view output |
| Q | Remark | user/source-supported note | metadata; exact scope depends on workflow | typed note/metadata |
| R | Reorder Row | reorder helper | display/helper only | view helper |
| S | Expiry Filter Helper | expiry/filter helper | display/helper only | computed view helper |
| T | Serial Code | current CMS external code mapping | external mapping field | Product-CMS mapping projection |
| U | CS Name | CMS-facing mapped name/description | external mapping projection | CMS catalogue/mapping projection |

### Identity facts

Multiple Main Stock rows can share one CMS code while using different expiries. This confirms:

`local Product identity != expiry Lot identity != CMS catalogue identity`.

`No.` / spreadsheet row is never canonical identity.

## Canonical inventory field direction

A future compact inventory view may use fields such as:

`Local Item Name | CMS Name | Type | Unit | CMS Code | Expiry Date | Original/Opening Qty | Received Qty | Deducted/Used Qty | Current Qty | CMS Price | Store/Location`

These are mapped from canonical entities or movement aggregates rather than stored as one mutable same-shaped table.

### Quantity semantics

For one Store + Lot:

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

`Received Qty`, `Deducted Qty`, and `Current Qty` are query/view outputs over canonical movement truth.

`Total Store Stock` for a Lot is the sum of all location balances, not an independent editable number.

## Daily Usage — verified operational movement view

Current structure is 39 columns:

| Range | Meaning | Classification | Future target |
| --- | --- | --- | --- |
| A | No. | synchronized display order | display/order | generated view order |
| B | Items | synchronized item/lot display | Product + Lot projection | Product/Lot projection |
| C | Remaining Stock | base/opening value | opening projection | Store+Lot selected-period opening |
| D | Received Stock | current-period receipt total | movement aggregate | receipt aggregate |
| E:AI | Day 1-31 | actual usage-entry cells | command-backed edit surface | dated usage movements |
| AJ | This Month Usage | sum of day usage | movement aggregate | usage aggregate |
| AK | This Month Remaining | current simple-sheet balance | computed balance | general Store+Lot ledger-derived Current Qty |
| AL | Remark | operational note | metadata | typed note/metadata |
| AM | Expiry Date | structured expiry projection | Lot field projection | Lot expiry |

Established compatibility workflow:

`Main Stock base/structure -> Daily Usage sync -> day usage entry -> monthly aggregates/current result -> Main Stock current-state projection`.

Future backend stores normalized dated movements, not 31 database quantity columns.

## Store / Location — locked foundation

The live workbook has no populated Store/Location field in Main Stock/Daily Usage. Treat it as the configured legacy Main Store context during migration.

Future rules:

- one Main Store plus unlimited Sub Stores;
- Product/Lot identity shared across stores;
- balance scoped by `(store_id, lot_id)`;
- internal transfer = linked atomic source-out + destination-in;
- Total Stock = sum of location balances;
- views may select one Store or aggregate all Stores.

## CMS catalogue / price list — verified

Current active catalogue structure includes:

`Code | Brand Name | Description | Form | Type | Class | Selling Price (¥)`

Classification:

- global/versioned external catalogue;
- not local Product master identity;
- current catalogue price distinct from historical receipt/source price;
- mapping requires code + compatible descriptive/history evidence;
- retired/recycled/reassigned codes require auditable mapping history.

Future target:

`cms_catalogue_versions + cms_catalogue_items + product_cms_mappings` or semantically equivalent structures.

## Transfer / batch intake — verified source semantics

Observed batch structure includes:

`No. | Code | Brand Description | Qty Received | Unit | Sale Price (¥) | Exp. Date | Transfer No.`

Established intake flow:

`source batch -> fixed-asset routing -> Product/CMS identity -> Lot resolution -> destination Store -> idempotency/review -> receipt application or reconciliation-only -> audit/read-back`.

External receipt is distinct from future internal MSA Store-to-Store transfer.

## Audit — verified

Current Audit_Log preserves significant-operation provenance such as timestamp, operation type, mapping/item context, previous/updated value and backup reference.

Future canonical audit adds stable user/agent identity, client/channel, operation/idempotency ID, source/reason, review/approval context, outcome and read-back.

## Lower-priority derived surfaces — Owner-confirmed

| Surface | Confirmed role | Future treatment |
| --- | --- | --- |
| This Month Received | filtered/derived received rows | generated receipt view |
| Reorder Form | filtered legacy recommendation view | generated planning/work view |
| Final Reorder Form | copied output with manual reasoning/adjustment | reviewed/final business artifact when approved/submitted |
| Master Data archive | legacy archive target | export/snapshot compatibility |

These surfaces do not drive the canonical inventory schema.

## Reorder realignment

Exact legacy Estimated Reorder Qty formula/threshold/rounding is **not required before F6D**.

Future planning can use usage trends/history, store demand, expiry, current/incoming stock, lead time/safety stock, deterministic modules, AI proposal, agent review and human adjustment/approval.

The canonical requirement is preservation of the underlying inventory/history/provenance data needed for those workflows.

## Monthly / archive realignment

Exact workbook reset formulas, close macros and archive formatting are deferred unless a specific behavior changes foundational identity, quantity, provenance, transfer semantics or audit truth.

Migration/opening balance provenance remains foundational.

## Remaining open items

Open questions are now follow-up decisions unless they force a different foundation:

1. exact note/Remark scope in edge cases;
2. Sub Store replenishment business policy and staff location-scope UX;
3. exact future reorder workflow/configuration model;
4. exact legacy Excel export/close formatting if high-fidelity compatibility is later required.

## Rules

- current source evidence wins over assumptions;
- CMS code alone never proves Product identity;
- row/order is never canonical identity;
- Store quantity truth comes from canonical movements;
- spreadsheet layout and calculations may evolve independently of canonical inventory semantics;
- unresolved behavior stays explicit rather than guessed.
