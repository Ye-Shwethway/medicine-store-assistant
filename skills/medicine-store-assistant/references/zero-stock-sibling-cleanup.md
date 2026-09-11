# Zero-Stock Sibling Cleanup

Use this reference whenever `$msa` reviews or deletes zero-stock duplicate/sibling rows from the operational inventory tables.

## Canonical cleanup rule

A zero-stock operational row may be deleted when **at least one valid same operational item/family sibling remains in the table after deletion**.

The primary invariant is:

**Do not allow the operational item/family to disappear completely from the inventory table merely because one or more rows reached zero stock.**

Expiry recency is not, by itself, a keeper requirement. A zero-stock row may be deleted even when it is the newest-expiry sibling, provided another valid same-family representative remains.

## Keeper rule

For each operational item/family:

- preserve at least one valid representative row,
- do not delete the sole remaining row merely because its stock is zero,
- if multiple zero-stock siblings exist, delete redundant rows while preserving at least one representative,
- if any positive-stock or received-stock sibling already preserves the item/family identity, redundant zero-stock siblings may be removed,
- do not require the newest-expiry zero-stock row to be kept solely because it has the latest expiry.

A sole remaining zero-stock item row is a `DORMANT_ITEM_KEEP` unless the Owner explicitly retires/removes that item from the operational catalogue.

## Safety checks before deletion

Before deleting a candidate row:

1. Confirm current `Stock Status Today` is zero.
2. Confirm another valid same operational item/family sibling will remain after deletion.
3. Confirm the candidate is not needed to preserve unresolved identity, mapping, receipt, or audit evidence.
4. Inspect current-month receipt/usage evidence. Do not erase meaningful current-month history unless that evidence is already preserved or the Owner explicitly authorizes the cleanup with the history risk understood.
5. Use current live row numbers immediately before mutation; never rely on stale row indexes.
6. Create a fresh checkpoint before structural deletion.

## Paired-row deletion invariant

`Main Stock` and `Daily Usage` are row-aligned operational surfaces.

When deleting a zero-stock row:

- delete the corresponding row from `Main Stock`,
- delete the corresponding row from `Daily Usage`,
- mirror the same structural deletion to active staging counterparts when production/staging parity is being maintained,
- delete multiple rows bottom-to-top so row shifts cannot corrupt later targets,
- renumber `No.` sequentially afterward where required,
- verify formulas, Main/Daily alignment, production/staging parity, received totals, and row counts,
- record the operation in `Audit_Log` with the checkpoint ID and readback result.

Never delete only one side of the Main Stock / Daily Usage pair.

## Existing-lot and receipt boundary

A zero-stock cleanup decision is separate from receipt intake.

- Same identity + same expiry receipt: merge into the existing lot; do not create a duplicate lot row.
- Same family + new expiry: create a new expiry-lot row.
- New intake/new expiry-lot rows default `Reorder Level` to the actual intake quantity unless an established row-specific value is explicitly retained or the Owner directs otherwise.
- Existing-lot receipt merges do not automatically change the existing Reorder Level.

## Owner-authorized immediate cleanup

The default month-close workflow may defer physical deletion while current-month history is still active. However, when the Owner explicitly authorizes immediate cleanup and the safety checks above prove the row redundant, `$msa` may perform the paired deletion during the active month.

Immediate cleanup must still preserve:

- item/family existence,
- row-pair integrity,
- current operational totals,
- receipt/usage evidence that matters,
- rollback capability through a fresh checkpoint,
- auditability through post-write readback.

## Examples

Delete allowed:

- zero-stock `Cannula 26G` row while `Cannula 26G (5/2028)` remains,
- zero-stock newest-expiry lot while an older same-family sibling still preserves the item identity,
- blank-expiry zero-stock legacy sibling when a valid dated sibling remains.

Delete not allowed:

- the only remaining `Cannula 26G` row if deleting it would remove that item from the table,
- a row with unresolved receipt/mapping evidence needed for reconciliation,
- one side of a Main Stock / Daily Usage pair without the matching paired deletion.

## Canonical shorthand

For zero-stock sibling cleanup, interpret the workflow as:

**identify zero-stock rows → group by operational item/family → verify at least one sibling survives → inspect current-month evidence → checkpoint → paired delete bottom-to-top → renumber → verify formulas/parity/totals → audit → readback**.
