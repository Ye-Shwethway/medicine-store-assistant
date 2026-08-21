# Inventory Data Model

Status: **design contract — implementation pending**

## Goal

Represent medicine-store inventory in a way that remains correct when spreadsheet rows are inserted, removed, reordered, renamed, split by expiry lot, or hidden from the operational view.

The model must preserve source truth, lot-level history, monthly history, catalogue history, and auditability without making spreadsheet row numbers canonical identifiers.

The database must also avoid turning convenient Excel/Google display sheets into unnecessary canonical tables. Human-facing worksheets may be generated projections over normalized canonical records.

## Identity layers

MSA already distinguishes three operational concepts. The database keeps them explicit.

### Product

A stable local operational identity, independent of any one expiry lot or current CMS catalogue row.

Candidate fields:

- `product_id` — immutable internal identifier.
- `local_name` — current preferred store-facing name.
- `default_unit` — established operational unit.
- `active` — whether the product should normally appear in current operational views.
- `display_order` — optional human-facing ordering aid; never identity.
- `created_at`, `updated_at`.

Product renaming must not create a new product unless the actual operational identity changed.

### Product lot

A physical/operational stock lot belonging to one product.

Candidate fields:

- `lot_id` — immutable internal identifier.
- `product_id` — parent product.
- `expiry_date` — structured expiry when known.
- `lot_status` — active, depleted, expired, closed, review, or future approved status set.
- `received_identity_snapshot_id` or equivalent — the CMS/source identity context at receipt where needed.
- `created_at`, `closed_at`.

Two otherwise identical products with distinct expiry dates remain distinct lots.

A terminal item-name expiry suffix in the spreadsheet is a presentation aid and compatibility field, not the database primary key.

### CMS catalogue identity

A versioned external catalogue identity, not the local product primary key.

Catalogue codes may change, disappear, or be reused. Therefore no local product or lot should use a CMS code as its immutable primary key.

Mappings between local products/lots and catalogue identities must be version-aware and auditable.

## Transaction ledger

Canonical stock movement is represented by immutable or correction-safe transactions rather than direct mutation of a balance cell.

A general transaction abstraction may contain:

- `transaction_id`.
- `lot_id`.
- `transaction_type`.
- `quantity` using a documented sign convention or positive quantity plus type semantics.
- `effective_date`.
- `source_type`.
- `source_id` / `source_line_id` where applicable.
- `operation_id` / idempotency key.
- `created_at`.
- `created_by_actor`.
- `reason` / `note` for adjustments.
- `reversal_of_transaction_id` where corrections use explicit reversal.

Initial movement types should remain minimal:

- `OPENING_BALANCE`
- `RECEIPT`
- `USAGE`
- `ADJUSTMENT_POSITIVE`
- `ADJUSTMENT_NEGATIVE`

Do not add speculative movement types before a real workflow requires them.

## Receipts

### Receipt batch

Represents one source transfer/intake event.

Candidate fields:

- `receipt_batch_id`.
- `transfer_no`.
- `transfer_date`.
- `from_store`.
- `to_store`.
- `source_document_hash` where available and appropriate.
- `status` — staged, reviewed, committed, reconciled, rejected, etc.
- `created_at`.

### Receipt line

Represents one source line in a batch.

Candidate fields:

- `receipt_line_id`.
- `receipt_batch_id`.
- `source_line_no`.
- `lot_id` after confirmed mapping.
- `quantity_received`.
- `source_unit`.
- `source_price`.
- `source_code`.
- `source_description`.
- `source_expiry_date`.
- mapping decision/status.

For a known transfer format, a uniqueness rule such as `(receipt_batch_id, source_line_no)` should prevent the same source line from being committed twice.

A committed receipt line produces or links to the corresponding canonical `RECEIPT` stock transaction.

### This Month Received projection

`This Month Received` does **not** require a separate canonical table simply because it exists as a worksheet.

It is a filtered/display projection over current-month receipt activity and the relevant lot/product state.

The legacy human-facing view may show fields such as:

- No.
- Items
- Sub Store Qty
- Received Qty
- Unit
- Expiry Date
- Remark

Those values should be generated from canonical receipt, lot, product, and monthly-state data. If a future requirement adds independent user-authored data to this view, model only that new information explicitly rather than duplicating the entire worksheet as a table.

## Usage

Daily Usage is normalized in the database.

Candidate usage record:

- `usage_id`.
- `lot_id`.
- `usage_date`.
- `quantity`.
- `source` — paper form, manual app entry, imported sheet history, etc.
- `operation_id`.
- `created_at`.
- `created_by_actor`.

The spreadsheet's Day 1–31 cells are a monthly projection of these records.

Multiple usage events on the same date and lot may remain separate canonical records while the spreadsheet displays their sum.

## Adjustments

Physical count corrections and other exceptional stock corrections must not silently edit prior receipt or usage history.

Use an explicit adjustment transaction with:

- signed direction/type,
- quantity,
- reason,
- actor,
- timestamp,
- optional approval/reference evidence.

A correction to an erroneous prior transaction should preferably use a documented reversal/correction pattern rather than destructive deletion once the transaction has become operational history.

## Derived balance

For a lot and applicable period/state, the backend derives balance from canonical movements.

Conceptually:

```text
balance = opening
        + receipts
        + positive adjustments
        - usage
        - negative adjustments
```

Exact period carry-forward semantics are defined in `MONTHLY_LIFECYCLE.md`.

If a current-balance snapshot/materialized value is stored, the backend must be able to verify it against the ledger.

## Reorder domain semantics

Do not model the legacy `Reorder` and `Final Reorder` worksheets as independent inventory truth tables merely to reproduce the workbook layout.

Distinguish three concepts:

1. **calculated reorder recommendation** — derived from canonical inventory state and approved reorder configuration/formula,
2. **working Reorder projection** — a display/workflow view of the calculated recommendation,
3. **final reorder submission** — the user-approved result, potentially including authorized manual edits before submission to CMS.

The working projection does not need canonical persistence beyond what is required for computation/audit.

The final approved/submitted reorder is a historical business record and should be preserved with the monthly snapshot when applicable. It must remain distinguishable from the underlying deterministic recommendation so later review can see whether manual changes were made.

The exact reorder formula is a compatibility contract to be documented from the current Main Stock/Excel workflow before backend implementation.

## Monthly snapshot entities

Closed-month history should include immutable snapshots sufficient to reproduce the established operational reports even if later product names, catalogue mappings, or display order change.

Candidate snapshot data includes:

- month identifier.
- lot identifier.
- product-name snapshot.
- expiry snapshot.
- opening balance.
- received total.
- daily or monthly usage summary as required for export.
- closing balance.
- reorder configuration snapshot.
- calculated reorder recommendation where required for audit/reproduction.
- final approved reorder result when one exists.
- catalogue/current-price snapshot where required by the report contract.

The snapshot supplements the ledger for convenient historical reporting; it does not replace canonical source transactions.

## Product lifecycle and deletion semantics

### New row in spreadsheet

A new spreadsheet row may represent:

- a new product,
- a new expiry lot of an existing product,
- a projection/order change only.

The backend must classify which domain change occurred rather than treating every inserted row as a new identity.

### Removed row in spreadsheet

A row disappearing from a current operational view must not automatically delete canonical history.

Prefer lifecycle changes such as:

- product `active = false`,
- lot `status = depleted/closed`,
- view/filter exclusion.

Hard deletion should be limited to records that are provably non-operational setup errors and have no dependent history, with explicit authorization and audit.

## Display order

Operational ordering is presentation metadata.

Store a `display_order`, grouping key, or equivalent only if needed to reproduce the preferred Main Stock sequence.

Changing display order must not alter product, lot, receipt, usage, or catalogue identity.

## Fixed assets

Fixed Assets remain a separate domain and must not be forced into medicine stock transaction tables merely because they share source transfer documents.

The existing skill's Fixed Assets boundary remains authoritative until a separate asset data model is explicitly designed.

## Constraints to preserve from the current skill

- Preserve local operational names unless an authorized rename is requested.
- Preserve distinct expiry lots.
- Never use CMS code alone as identity.
- Preserve actual historical movement even when it violates ideal FIFO/FEFO.
- Preserve structured expiry truth and surface suffix/expiry mismatches for review.
- Keep derived values derivable from canonical inputs.
- Treat display-only/report worksheets as projections unless they introduce genuinely independent business data.
