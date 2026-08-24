# Workbook Function Contract

Status: **F6C source-backed compatibility contract — canonical foundation takes precedence over exact formula parity**

Purpose: preserve the real operational meaning of the existing workbook while allowing the future backend to use a normalized, location-aware inventory foundation and configurable views.

Core rules:

> **Spreadsheet layout is configurable; inventory semantics are not arbitrary.**

> **Stock belongs to a location; product and catalogue identity do not.**

> **AI assistance must degrade to safe deterministic/manual operation rather than block the store.**

## Evidence hierarchy

1. exact source document / physical movement evidence;
2. verified live operational workbook state;
3. verified current CMS catalogue;
4. established MSA skill workflow and confirmed mappings;
5. Owner-confirmed business process;
6. model inference only when explicitly labeled as proposal.

Representative Google Sheet `FORMULA` reads returned materialized values, not exact legacy Excel formula strings. Therefore do not reconstruct Excel formulas/macros from those values alone.

## Main Stock

### Role

Main Stock is the primary human stock/lot operational view. It is not the canonical database table design.

### Identity

- one local Product can have multiple expiry Lots;
- sibling expiry rows may share the same CMS code;
- `No.` / row order is presentation metadata;
- terminal expiry suffix is lot presentation metadata, not Product identity;
- structured Expiry Date is the stronger lot field unless stronger source evidence says otherwise.

### Field semantics

Current source-backed classifications remain in `WORKBOOK_PARITY_MATRIX.md`.

Important future mapping:

- Local item name -> Product display metadata;
- Expiry Date -> Lot;
- Unit / Type -> Product/operational metadata;
- CMS Code / CMS Name / CMS Price -> accepted Product-to-CMS mapping/catalogue projection with mapping lifecycle status;
- Remaining/Original/Open stock -> migration or selected-period opening context;
- Received Stock -> receipt movement aggregate;
- This Month Usage -> dated usage aggregate;
- Stock Status Today / Current Qty -> ledger-derived current balance;
- reorder/helper/status fields -> configurable workflow/computed/view outputs.

`Price` remains compatibility/derived output and is not routine canonical movement truth.

### New expiry lot

When verified evidence establishes a new expiry of an existing Product:

1. preserve Product identity;
2. create a new Lot;
3. preserve receipt/source provenance;
4. represent quantity through receipt/opening movement semantics rather than copying neighboring balances;
5. keep sibling ordering only as view metadata.

## Daily Usage

### Role

Daily Usage is the operational consumption-entry view. Day 1-31 is a monthly pivot over dated usage events.

Established compatibility flow:

`Main Stock structure/base projection -> Daily Usage -> day usage entry -> monthly aggregates/current balance -> Main Stock current-state projection`.

### Forward fields

Current established mapping includes:

- Main Stock No. -> Daily Usage No.;
- Items -> Items;
- Remaining Stock -> Remaining Stock;
- Received Stock -> Received Stock;
- structured Expiry Date -> far-right Expiry Date.

Structural matching must use Product/Lot meaning rather than row number as identity.

### Usage entry

Canonical future meaning:

`record_usage(store_id, lot_id, effective_date, quantity, source, operation_id, actor)`

Rules:

- record the actual Store/Lot/date/quantity;
- do not rewrite history merely to satisfy FIFO/FEFO advice;
- multiple same-day events may remain separate canonically while the cell displays their sum;
- correction versus additional usage must be semantically distinguished.

### Monthly compatibility values

Current workbook behavior includes:

`This Month Usage = SUM(Day 1..31)`

and a current remaining value derived from opening/base + receipts - usage in the current simple sheet flow.

In the future backend, the general current balance also includes transfers and adjustments. Both Main Stock and Daily Usage therefore become projections of the same Store+Lot ledger state.

Do not reverse-sync a calculated current balance into canonical opening history.

## CMS catalogue and mapping

Canonical companion: `CMS_MAPPING_LIFECYCLE.md`.

The current CMS price list is a versioned external catalogue with Code, name/description, form/type/class and selling price information.

It is not the local Product master.

The live workbook contains real mapping complexity:

- `Recycled ID` examples;
- `CMS Discontinued (Local Stock Retained)` examples;
- same-code local rows whose meanings differ, which may represent stale/historical mapping or local staff error;
- local names that differ from CMS catalogue descriptions.

Therefore the workbook `Serial Code` / `CS Name` cells are operational mapping state/evidence, not proof that code equality is correct identity.

Rules:

- CMS code alone never proves Product identity;
- evaluate descriptive evidence and mapping history;
- do not silently decide whether a conflict is a CMS error, historical state, or local staff error;
- mappings remain historical/auditable/version-aware;
- a new catalogue is reconciled against accepted mapping state rather than blindly synchronized;
- AI may assist candidate ranking/explanation when available;
- manual mapping/review remains supported when AI is unavailable;
- last accepted mapping remains usable until a newer mapping is explicitly accepted;
- current catalogue price is distinct from last accepted operational price and historical receipt/source price;
- catalogue updates do not fabricate stock movement or rewrite historical receipt price.

### Price fallback

If a newer CMS catalogue exists but an affected Product cannot yet be safely reconciled:

- keep the last accepted mapping;
- keep the last accepted operational price available;
- flag the mapping/price as not yet reconciled to the newest catalogue;
- do not force a zero/null price;
- do not adopt a new code's price solely because the code string matches.

This preserves the current practical store behavior where an older accepted price can remain in use until the next mapping/price review is completed.

## Batch / receipt intake

Observed staging evidence includes source code/description, quantity, unit, price, expiry and transfer/document number.

Canonical future flow:

`source evidence -> classify consumable/fixed asset -> resolve Product/CMS identity -> resolve Lot -> resolve destination Store -> idempotency/review -> commit receipt -> audit/read-back`

Rules:

- same Product + different expiry normally creates a new Lot;
- repeated evidence must not double-intake;
- already-applied historical transfers may be reconciliation-only;
- fixed assets stay separate;
- receipt destination Store is explicit in the future backend.

## Store / Location

Canonical architecture: `STORE_LOCATION_MODEL.md` and `CANONICAL_INVENTORY_FOUNDATION.md`.

The current live workbook contains no populated Store/Location field in Main Stock/Daily Usage, so it is treated as the configured legacy Main Store context for migration.

The same Product/Lot may hold quantity in multiple stores. Balance is per `(store_id, lot_id)`.

Internal transfer preserves Product/Lot identity and atomically creates linked source-out + destination-in movement effects.

## Quantity / Total Stock

The human-facing inventory may show Original/Opening, Received, Deducted, Current and Total Stock columns.

These are not independent mutable truths.

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

Total Store Stock for a Lot is the sum of its location balances.

## This Month Received

Owner-confirmed role: filtered/derived display of current-period received activity.

It has no known independent canonical stock truth. Generate it from receipt + Product/Lot/Store state.

## Reorder / Final Reorder

Canonical companion: `REORDER_BASELINE_AND_AI_ENHANCEMENT.md`.

Owner-confirmed legacy flow:

`Main Stock Estimated Reorder Qty -> filtered Reorder Form -> copy to Final Reorder -> manual reasoning/adjustment -> submit/archive`

### Future treatment

The exact legacy calculation is **not a canonical database formula requirement**, but the useful baseline behavior must survive AI outages.

Required two-layer model:

1. deterministic baseline calculation from structured local/backend stock, usage and configuration;
2. optional AI/advanced enhancement/review.

AI unavailable:

`canonical stock/history -> deterministic baseline -> human review/adjustment -> final reorder`

AI available:

`canonical stock/history -> deterministic baseline -> AI enhancement/review -> human/authorized workflow -> final reorder`

Therefore:

- exact old Estimated Reorder Qty formula/threshold/rounding is non-blocking for F6D;
- the future backend must eventually supply a deterministic baseline strategy so users do not calculate every item manually during AI outage;
- old fields remain useful compatibility/reference outputs;
- the foundational DB must preserve stock/history/provenance/configuration needed for baseline and richer planning;
- a final approved reorder may later be stored as a durable reviewed business artifact/snapshot;
- deterministic baseline, AI reasoning/review and final human-approved result remain distinguishable.

## Audit

The live workbook already preserves significant-operation history with previous value, updated value and backup reference.

Future backend extends this with stable human/agent identity, client/channel, operation/idempotency ID, source/reason, approval/review context, outcome and read-back evidence.

A mutation is not complete until the intended resulting state can be read back and attributed.

CMS mapping/price changes must also preserve prior accepted state so recycled/discontinued or mistaken changes can be reconstructed.

## Monthly lifecycle / Excel Master

Legacy close/reset/archive behavior remains compatibility evidence.

Exact formulas/macros are not a foundation blocker unless a specific behavior changes canonical Product/Lot/Store identity, stock quantity, source provenance, transfer meaning or audit truth.

Foundational requirement retained:

- migration/opening balance must be explicit and provenance-bearing;
- closed/report snapshots, when added, are Store+Lot scoped and derive from canonical history;
- do not fabricate new stock movements merely to imitate monthly spreadsheet resets.

## Completion rule

F6C is sufficient for F6D when Product, Lot, Store, Movement, Balance, Transfer, CMS Mapping and Actor/Audit semantics are explicit and Main Stock/Daily Usage can be explained as projections/edit surfaces over them.

This condition is now met for entering the bounded F6D schema slice. Exact reorder formula parity, cosmetic/report-only formulas, and legacy macro formatting do not block F6D.
