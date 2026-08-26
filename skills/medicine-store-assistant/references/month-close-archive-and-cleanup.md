# Month-Close Archive and Paired Cleanup Workflow

Use this reference whenever `$msa` closes a month, prepares a new month, archives Daily Usage, or physically deletes zero-stock duplicate rows from `Main Stock` / `Daily Usage`.

This workflow preserves the legacy Excel operating intent (`archive to Master Data` then `Prepare Data`) while replacing macro-only assumptions with explicit, checkpointed Google Sheets operations.

## Core rule

**Do not physically delete a Main Stock row during an active month merely because it reached zero stock.**

`Main Stock` and `Daily Usage` are row-aligned operational surfaces. If a row has current-month usage or receipt evidence, deleting the row before month close can destroy or misalign the month's operational history.

During the active month, classify a redundant zero-stock row as pending cleanup. Perform physical deletion only after the closed month has been durably archived and verified.

## Main Stock / Daily Usage paired-row invariant

`Main Stock` and `Daily Usage` must remain aligned by operational row identity.

When a physical row is eventually removed:

- delete the corresponding row from `Main Stock`,
- delete the corresponding row from `Daily Usage`,
- perform both as one controlled mutation slice,
- delete rows bottom-to-top so earlier row indexes do not shift before later deletions,
- verify item alignment, formulas, numbering, and used-range integrity afterward.

Never delete only the Main Stock row while leaving the mirrored Daily Usage row behind.

## Active-month lifecycle state

A zero-stock row that is otherwise redundant may be classified as:

`PENDING_MONTH_CLOSE_CLEANUP`

Meaning:

- zero current stock,
- another appropriate same-family operational representative exists,
- the row is eligible for future cleanup,
- but the current month has not yet been archived/closed, so physical deletion is deferred.

This classification is a timing gate, not a reversal of the underlying cleanup decision.

### Rows that must not enter pending cleanup automatically

Do not mark a row for cleanup if it is:

- `FRESH_REORDER_KEEP`,
- `DORMANT_ITEM_KEEP`,
- the sole remaining representative of its item/family,
- part of an unresolved duplicate-zero keeper decision,
- a positive-stock expired row requiring disposition review,
- required to preserve an unresolved identity/mapping/receipt/audit trail.

If an expired positive-stock sibling exists and a fresh/current zero-stock sibling exists, keep the fresh zero-stock row as the future reorder representative.

## Current-month usage protection

Before any row deletion, inspect the corresponding `Daily Usage` row.

Current-month evidence includes, as applicable:

- opening / remaining stock context,
- received stock,
- day columns 1-31,
- `This Month Usage`,
- `This Month Remaining`,
- remarks,
- expiry metadata.

If any meaningful current-month evidence exists, do not physically delete the row until the month-close archive has been written and verified.

Even when a row has no current-month usage, prefer one consistent month-close cleanup cycle instead of opportunistic mid-month deletion unless the user explicitly requests an immediate exception and the paired-row integrity is proven safe.

## Month-close trigger

Run this workflow when the Owner asks to close the current month, prepare the next month, or equivalent wording such as:

- `prepare new month`,
- `close August`,
- `archive this month and prepare September`,
- `month-end cleanup`.

Do not infer that month close has happened merely because the calendar date changed. Use the user's explicit operational instruction or a clearly established workflow trigger.

## Full month-close workflow

### 1. Inspect live state

Before mutation:

- inspect current `Main Stock` and `Daily Usage`,
- verify their row alignment,
- inspect relevant formulas and used ranges,
- identify current month/year,
- identify all `PENDING_MONTH_CLOSE_CLEANUP` / safe redundant zero-stock rows,
- re-check keeper exceptions against the latest live state.

Do not rely on stale row numbers from an earlier review because rows may have been inserted or moved during the month.

### 2. Create and verify a full-workbook checkpoint

Create a new full copy in the configured Medicine Store Assistant checkpoint folder.

Record:

- checkpoint title,
- Drive file ID,
- URL,
- intended month-close operation.

Verify the checkpoint exists before continuing.

Never reuse an older checkpoint for a new month-close mutation slice.

### 3. Archive the closed month before cleanup

Create or append durable closed-month evidence before deleting any current operational row.

The archive should preserve enough information to reconstruct what happened during the month. At minimum preserve, where available:

- closed month and year,
- stable local item identity,
- lot/expiry identity,
- opening / remaining stock context,
- received stock,
- day-by-day usage or an equivalent faithfully preserved monthly usage record,
- total monthly usage,
- closing stock,
- unit,
- reorder level / relevant reorder state,
- shortage/early-depletion evidence,
- CMS identity fields when useful for historical reconciliation,
- Final Reorder / Owner-order evidence when part of the closed-month workflow.

The archive is evidence. Do not rewrite the historical month to make FIFO/FEFO or another ideal workflow appear cleaner than the actual recorded usage.

If a durable historical archive structure already exists, append to it rather than inventing a second incompatible history system.

### 4. Verify archive completeness

Before cleanup, read the archived month back and confirm:

- the intended month is present,
- item/lot identities are preserved,
- monthly usage values match the closing operational sheet,
- zero-stock rows with usage were captured,
- important receipt/reorder/expiry context was not lost,
- archive row count / coverage is plausible relative to the live month-close state.

If verification fails, stop. Preserve the checkpoint and do not delete rows.

### 5. Recompute cleanup eligibility from the live workbook

After archive verification, re-evaluate the cleanup queue from current live rows.

A row can proceed to paired deletion only when all are true:

1. current stock is zero,
2. another appropriate same-family representative safely preserves operational identity,
3. the row is not the fresh/current keeper while the positive sibling is expired,
4. closed-month usage/receipt history is safely archived,
5. no unresolved mapping, receipt, or audit dependency requires the physical row,
6. deletion has been authorized by the Owner or falls within an explicitly authorized month-close cleanup batch.

### 6. Preserve required keeper rows

For every family being cleaned:

- preserve at least one valid operational representative,
- prefer a current/fresh representative over an obsolete expired one when selecting a future reorder row,
- never delete every row in a family merely because every row currently has zero stock,
- keep a sole zero-stock item row as `DORMANT_ITEM_KEEP` unless the Owner explicitly retires the item.

### 7. Delete paired rows bottom-to-top

Build the final deletion list using the **current** Main Stock row numbers immediately before deletion.

Sort descending by row number.

For each approved row index, delete the matching row from both:

- `Main Stock`,
- `Daily Usage`.

Use a single controlled batch when practical. The descending order is mandatory to prevent row-shift corruption.

Do not delete rows from archived evidence/history tabs as part of operational cleanup.

### 8. Re-establish new-month operational state

After paired cleanup, prepare the next month while preserving the four compatibility-locked table interfaces.

For `Daily Usage`:

- preserve headers and column order,
- preserve the item row alignment with Main Stock,
- clear/reset prior-month manual day entries only after archive verification,
- establish the new month's opening/received/remaining behavior according to the live workbook formulas/contracts,
- do not erase stable item identity or expiry context needed for the new month.

For `Main Stock`:

- preserve item/lot identity and current stock state,
- retain valid reorder-level configuration unless a separate authorized reorder mutation changes it,
- preserve fresh zero-stock reorder representatives and dormant item identities.

Do not redesign the operational tables as part of month preparation.

### 9. Repair / verify derived formulas and numbering

After structural deletion/reset:

- verify sequential `No.` values where required,
- verify `Main Stock` and `Daily Usage` item alignment,
- verify `Main Stock` derived columns,
- verify `Daily Usage` derived columns (`C`, `D`, `AJ`, `AK`, and other approved formula regions),
- scan for `#REF!`, `#N/A`, `#VALUE!`, `#ERROR!`, or formula displacement,
- verify downstream helper/review surfaces still bind to the intended data.

Do not silently patch unrelated formulas outside the month-close impact area unless a clearly broken dependency requires repair and the repair is auditable.

### 10. Read back the new-month state

Read back representative beginning, middle, and end rows plus every affected family when practical.

Confirm:

- deleted rows are gone from both Main Stock and Daily Usage,
- keeper rows remain,
- Daily Usage is ready for the new month,
- archived closed-month data remains intact,
- current stock values were not accidentally changed by structural cleanup,
- Final Reorder is not rewritten merely because a month was closed.

### 11. Audit the operation

Write an `Audit_Log` entry containing:

- closed month,
- archive destination/range or archive identifier,
- number of archived rows/items,
- number of paired rows deleted,
- important keeper exceptions,
- new-month preparation summary,
- checkpoint ID,
- verification result.

Read the audit row back before reporting success.

## Failure / rollback behavior

If any stage fails after the checkpoint:

- stop further mutation,
- preserve the checkpoint,
- report exactly which stage failed,
- do not continue deleting rows after an archive or alignment verification failure,
- restore only when authorized or clearly required by the established recovery contract.

Never claim month close succeeded until archive, paired-row integrity, new-month state, and audit readback have all been verified.

## Relationship to Final Reorder

Month close and Final Reorder are related evidence streams but different operations.

- A Final Reorder already submitted for the closed month is historical Owner-order evidence.
- Closing the month does not authorize changing that submitted Final Reorder.
- Preserve the archived Final Reorder decision when available.
- The next month's reorder analysis happens later from the new live state and accumulated history.

## Relationship to reorder reasoning

Current-month zero-stock rows may contain valuable usage evidence. Their usage remains part of family demand history even after the physical operational row is later deleted.

Therefore:

- row deletion is operational cleanup,
- historical usage preservation is permanent evidence,
- deleting a row must never erase the family demand history that justified past or future reorder reasoning.

## Human-facing cleanup UI

During the active month, a concise cleanup queue may show:

- Main Row,
- Item,
- Expiry,
- Stock,
- Cleanup state,
- concise reason,
- Owner decision/note when needed.

Once a row is approved but deferred until month close, prefer wording such as:

`PENDING MONTH-CLOSE CLEANUP`

rather than implying it can be safely deleted immediately.

Do not expose full Daily Usage history in the Owner inbox merely to justify the timing rule. The agent should inspect that evidence behind the scenes.

## Hard boundaries

Never:

- delete a Main Stock row without handling the corresponding Daily Usage row,
- delete a current-month row with usage/receipt evidence before the month is durably archived and verified,
- assume zero stock means historical evidence is disposable,
- delete a fresh zero-stock reorder representative because an expired positive-stock sibling exists,
- delete every zero-stock row in a family and accidentally remove the item's future reorder identity,
- use stale row numbers for a structural deletion batch,
- delete rows top-to-bottom when multiple row deletions would shift later indexes,
- clear the new month's Daily Usage until the closed month archive is verified,
- rewrite actual historical usage to make an idealized workflow appear true,
- alter an already-submitted Final Reorder merely as part of month close,
- skip checkpoint, readback, or audit for paired operational row deletion.

## Canonical shorthand

When the Owner says **`prepare new month`**, interpret the operational workflow as:

**inspect → checkpoint → archive closed month → verify archive → recompute cleanup queue → paired Main Stock + Daily Usage deletion bottom-to-top → prepare new-month Daily Usage → verify formulas/alignment → audit → readback**.
