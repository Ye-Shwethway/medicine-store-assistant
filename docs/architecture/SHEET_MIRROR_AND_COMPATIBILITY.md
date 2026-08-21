# Sheet Mirror and Compatibility

Status: **design contract — implementation pending**

## Purpose

Preserve the usefulness of Google Sheets and the existing Excel workflow while preventing either workbook format from becoming the only canonical store of inventory history after migration.

## Transition states

### Before database promotion

The current live Google workbook remains authoritative according to the existing MSA skill and source-document hierarchy.

The future database may run in shadow mode but must not silently override live operational truth.

### After database promotion

PostgreSQL becomes canonical for operational identities, transactions, monthly history, and derived state.

Google Sheets becomes a synchronized operational mirror and controlled human interface.

Excel becomes a generated export/archive/report compatibility surface.

## Primary human-facing views

The mirror should preserve the established human workflow around:

1. Main Stock
2. Daily Usage
3. This Month Received
4. Reorder / Final Reorder

These are not independent canonical datasets. They are views, projections, or approved outputs derived from the same canonical product/lot, receipt, usage, adjustment, configuration, and monthly-state records.

`Main Stock` and `Daily Usage` are the primary operational data views. `This Month Received` and the reorder sheets are primarily display/workflow views.

## Main Stock mirror

Main Stock remains a lot-level operational projection.

After database promotion:

- row order is presentation metadata,
- a row maps to a stable `lot_id`, preferably through hidden/protected integration metadata rather than visible human identifiers where feasible,
- inserting/reordering visible rows must not create new canonical identity by accident,
- current stock, current-month usage, expiry, receipt totals, and other derived values come from backend state,
- direct human edits to canonical fields need an explicit ingestion/reconciliation path rather than blind bidirectional cell sync.

The existing skill's local-name, expiry-lot, CMS-matching, and derived-field rules remain compatibility requirements.

## Daily Usage mirror

Preserve the familiar monthly layout:

- `A:D` synchronized/base fields,
- Day 1–31 operational usage projection,
- monthly usage total,
- monthly remaining/current balance,
- remark,
- expiry projection.

In canonical storage, daily usage is date-based normalized transaction data. The Day 1–31 cells are a rendering of those records.

When the Sheet is an authorized input surface, a change to a day cell must be translated into a typed usage operation/delta with idempotency and validation. Do not treat bulk cell contents as an unvalidated replacement of the ledger.

The current pre-promotion Daily Usage contract remains in force until that integration is implemented and verified.

## This Month Received mirror

`This Month Received` is a **display-only filtered view**, not a second receipt ledger.

The legacy Excel behavior is simple: when a Main Stock row has current-month received quantity, the display sheet shows the relevant row and value for convenient review.

The familiar fields are approximately:

- No.
- Items
- Sub Store Qty
- Received Qty
- Unit
- Expiry Date
- Remark

After database promotion, generate this view from canonical receipt and inventory data for the active month. Preserve enough traceability to inspect the underlying receipt/batch when needed, but do not maintain independent mutable receipt truth in this sheet.

## Reorder and Final Reorder mirrors

The legacy workbook separates reorder workflow into two human-facing surfaces:

1. `Reorder` — a synchronized/working view of reorder quantities already calculated from Main Stock,
2. `Final Reorder` — a copied final working document that the user may manually edit before sending to CMS and archiving in the monthly Master package.

Therefore the backend should distinguish:

- deterministic calculated reorder recommendation,
- generated working Reorder projection,
- final user-approved reorder submission.

The calculated recommendation should derive from canonical inventory state and the verified Main Stock reorder formula/algorithm.

The working `Reorder` sheet is display/workflow state and should not become a separate canonical inventory table.

`Final Reorder` is different only when it becomes an approved/submitted business record: preserve that final result in the monthly historical snapshot, including authorized manual changes. Do not silently overwrite it later merely because the underlying calculated recommendation changes.

The exact current reorder formula still must be documented from the established Main Stock/Excel behavior before backend calculation is implemented. Until parity is proven, do not replace the existing formula with a newly invented algorithm.

## Current CMS price list

The live workbook may retain only the latest active CMS catalogue for convenient human review.

The database should retain full historical catalogue versions after migration.

The workbook's current tab order and retention rules continue to apply until database archival has been validated and the user explicitly authorizes any cleanup change.

## Mirror synchronization model

Prefer database-to-Sheet projection as the normal direction after promotion.

For Sheet-originated edits, use one of these controlled paths:

1. explicit input form/helper area that sends typed backend commands,
2. integration process that detects approved editable-cell changes and converts them into domain operations,
3. MSA/Custom GPT orchestration that submits API operations and then refreshes the mirror.

Avoid unrestricted two-way synchronization where arbitrary cell edits overwrite canonical database state.

Display-only sheets such as `This Month Received` and generated `Reorder` should normally be backend/Sheet-derived and not treated as independent input surfaces.

## Sync metadata

The integration may maintain protected/helper metadata such as:

- canonical product/lot ID,
- mirror row/version token,
- last backend revision/sync timestamp,
- sync status/error,
- operation ID for a pending Sheet-originated write.

Keep technical metadata out of the human-facing front area where possible.

## Divergence detection

After database promotion, periodically compare canonical backend projections with the live workbook.

Classify differences such as:

- expected pending sync,
- authorized Sheet-originated input not yet committed,
- formatting/presentation-only difference,
- data divergence requiring review,
- unauthorized/manual canonical-field edit.

Do not silently resolve a material divergence by whichever side was modified most recently.

For display-only derived views, prefer regeneration from canonical data rather than bidirectional conflict resolution.

## Excel compatibility

The system should support generation of a monthly workbook containing the familiar operational/report sheets.

Long-term options include:

- clean data export preserving sheet names/columns,
- export into a compatibility template that contains established formulas/macros,
- later replacement of specific macros only after backend parity is proven.

The canonical backend must not require Excel macros to maintain data integrity.

## Historical workbook exports

Any closed month should be exportable again from PostgreSQL.

An exported workbook is a representation of a historical snapshot. Editing that exported file must not mutate canonical history unless a separate historical-correction workflow explicitly imports an approved change.

A historical `Final Reorder` export should reproduce the final approved/submitted result for that month rather than blindly recomputing a different recommendation from current configuration.

## Offline considerations

Excel may remain useful during connectivity interruptions.

A future offline-import design must explicitly handle:

- export version/month identity,
- edits made offline,
- duplicate/replayed imports,
- conflicts with newer canonical transactions,
- human approval.

Do not implement generic spreadsheet upload-and-replace behavior.

## Safety boundary

A mirror failure must not corrupt canonical data.

If Google Sheets synchronization fails after a canonical API transaction commits:

- retain the committed database transaction,
- mark mirror sync pending/failed,
- retry safely,
- tell the user canonical commit succeeded but the mirror is not yet verified.

Never repeat the canonical stock transaction merely to repair the mirror.
