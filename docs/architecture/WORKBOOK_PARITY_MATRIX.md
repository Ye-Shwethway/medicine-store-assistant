# Workbook Parity Matrix

Status: **F6C working artifact — Main Stock / Daily Usage / CMS / batch source pass completed; rollover and exact legacy reorder formula remain open**

This matrix records only behavior supported by the authorized live `Medicine Store Cloud`, the established MSA skill contract, or explicit Owner confirmation. Unknown behavior remains open rather than inferred.

## Source-resolution rule

- Live Google Sheet = current operational structure/value evidence.
- MSA skill = established operational behavior/authority contract already proven in use.
- Owner-confirmed workflow = accepted business-process evidence.
- Original Excel workbook = required only where exact legacy formulas/macros or close/archive behavior still matter.

A `FORMULA` read of representative current `Main Stock!A:U` and `Daily Usage!A:AM` ranges returned materialized values rather than formula strings. Therefore the Google Sheet must not be treated as the exact formula source for derived Excel behavior.

## Main Stock — verified current operational projection

Current visible populated contract:

| Col | Header | Source-backed meaning | F6C classification | Future target |
| --- | --- | --- | --- | --- |
| A | No. | human-facing sequential order; renumbered after structural insertion | display/order metadata | view row order, never identity |
| B | Items | local operational item/lot-facing name; terminal expiry suffix may distinguish sibling lots | canonical product display name + lot presentation | product + lot projection |
| C | Expiry Date | structured lot expiry field | canonical entity field | lot.expiry_date |
| D | Date Status | current materialized expiry/status output; examples include `Expired`, `NE`, numeric day values | deterministic computed/display field | computed expiry status |
| E | Unit | established local operational unit | canonical entity/config field | product/lot unit policy |
| F | Remaining Stock | base/opening stock used by Daily Usage; must not be overwritten by current calculated balance | canonical monthly/base state | opening/base quantity evidence |
| G | Received Stock | current-month receipt quantity projection; new lot intake puts source quantity here while base F starts at 0 | canonical event-backed projection | SUM(receipts for month/lot) |
| H | Stock Status Today | current calculated balance synchronized from Daily Usage monthly remaining | deterministic computed field | ledger-derived current balance |
| I | Reorder Level | established reorder configuration/threshold | command-backed editable config | reorder config |
| J | This Month Usage | synchronized monthly usage total from Daily Usage | deterministic computed field | SUM(usage for month/lot) |
| K | Stock Remark | materialized reorder/status aid; examples include `Reorder` / `No Reorder` | deterministic computed/display field | reorder/status computation |
| L | Reorder Surplus Factor | established configurable reorder factor; observed value commonly 1.2 | command-backed editable config | reorder config |
| M | Estimated Request Qty | calculated reorder recommendation quantity | deterministic computed field | reorder recommendation |
| N | Shortage Date | calculated/predicted shortage date when applicable | deterministic computed field | forecast output |
| O | CMS Price | current CMS catalogue/mapping price, not receipt-time historical truth | command-backed catalogue/mapping field | versioned catalogue/mapping projection |
| P | Price | Excel-derived pricing output; may include expiry-related logic; MSA explicitly forbids routine writes | deterministic computed field | pricing computation/output |
| Q | Remark | operational remark where source/user explicitly supports it | command-backed editable metadata | lot/product/month note as defined |
| R | Reorder Row | helper ordering/filter output for reorder projection | display/helper only | view helper, not canonical field |
| S | Expiry Filter Helper | helper status (`ALERT`, `OK`, etc.) used for filtering/visual workflow | display/helper only | computed view helper |
| T | Serial Code | current CMS external code mapping; code alone is never local identity | command-backed external mapping field | versioned catalogue mapping |
| U | CS Name | current CMS-facing name/description associated with verified mapping | external mapping projection/metadata | catalogue mapping projection |

### Main Stock identity facts

The live sheet contains multiple rows for one product family with different expiries while sharing the same CMS code, e.g. multiple `10cc Syringe` expiry rows sharing one Serial Code. This confirms:

`local product identity != expiry lot identity != CMS catalogue identity`.

Spreadsheet row number/order is presentation only.

## Daily Usage — verified operational movement view

Current contract is 39 columns:

| Range | Meaning | F6C classification | Future target |
| --- | --- | --- | --- |
| A | No. | synchronized display order from Main Stock | display/order metadata |
| B | Items | synchronized local item/lot-facing name | product + lot projection |
| C | Remaining Stock | synchronized base/opening stock from Main Stock F | monthly/base-state projection |
| D | Received Stock | synchronized current-month received quantity from Main Stock G | receipt projection |
| E:AI | Day 1–31 | actual usage entry cells | canonical usage events projected by date |
| AJ | This Month Usage | deterministic sum of Day 1–31 | computed monthly usage |
| AK | This Month Remaining | `C + D - AJ` | computed current balance |
| AL | Remark | source/user-supported operational remark | command-backed editable metadata |
| AM | Expiry Date | Google-Sheet extension synchronized from Main Stock structured expiry | lot expiry projection |

Established workflow from the MSA skill:

`Main Stock base/structure -> Daily Usage A:D/AM sync -> actual day usage entry -> AJ/AK calculation -> Main Stock J/H reverse sync`.

Actual recorded movement wins over FIFO/FEFO ideals. Day-grid layout is a view; canonical storage should be normalized date + lot + quantity records. Blank and numeric zero remain semantically distinct at the input/view layer.

## CMS catalogue / price list — verified

Current active catalogue structure observed in `CMS_Price_List_202608`:

`Code | Brand Name | Description | Form | Type | Class | Selling Price (¥)`

Classification:

- versioned external catalogue, not product master identity;
- current CMS price is catalogue truth for the active version, not historical receipt price;
- mappings must use code + compatible descriptive evidence;
- retired/recycled/reassigned codes require mapping history rather than silent replacement.

Future target: versioned `catalogue_version` + `catalogue_item` + dated/audited local mapping.

## Transfer / batch intake — verified

Observed batch structure includes:

`No. | Code | Brand Description | Qty Received | Unit | Sale Price (¥) | Exp. Date | Transfer No.`

MSA workflow already establishes:

`source batch -> fixed-asset routing -> identity classification -> existing lot / new expiry lot / new product -> idempotency check -> receipt application or reconciliation-only -> read-back/audit`.

Future target: `receipt_batch` + `receipt_line` + confirmed lot mapping + immutable receipt transaction. Re-reading a historical source must never double-intake quantity.

## Audit — verified

`Audit_Log` currently preserves at least:

`Timestamp | Operation Type | Serial Code | Item Name | Previous Value | Updated Value | Backup Snapshot ID`

This is evidence that material operations already use mutation provenance. Future canonical audit must be richer and actor/idempotency-aware, but the workbook Audit Log remains compatibility/history evidence during migration.

## Lower-priority derived surfaces — Owner-confirmed

| Surface | Confirmed role | Canonical treatment |
| --- | --- | --- |
| This Month Received | filtered/derived rows from Main Stock where current-month received quantity exists | generated receipt projection only |
| Reorder Form | filtered/derived view of Main Stock `Estimated Request Qty` | generated reorder working projection |
| Final Reorder Form | copy of Reorder working output, manually adjusted before submission | approved/final business snapshot when submitted |
| Master Data archive | archive target for final monthly output via macro | historical snapshot/export concern |

These surfaces must not drive separate canonical inventory tables.

## Still open before F6C acceptance

1. Exact legacy reorder formula/threshold/rounding logic behind Main Stock calculated outputs where parity matters.
2. Exact month rollover sequence: how F/G/H/J/day columns reset or carry forward in the original Excel workflow.
3. Exact archive/close macro behavior needed to reproduce historical exports.
4. Store/location semantics for one Main Store plus unlimited Sub Stores, including transfer direction and which views/configuration are store-specific.
5. Whether `Remark` fields are lot-level, month-level, or workflow-specific in all cases.

## Rules

- Current source evidence wins over assumptions.
- CMS code alone never proves product identity.
- Spreadsheet row number/order is not canonical identity.
- Human-facing grid structure is configurable/projection state; typed business semantics remain fixed.
- Any unresolved behavior stays explicit until source-backed or Owner-confirmed.
