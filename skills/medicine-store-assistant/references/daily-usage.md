# Daily Usage Synchronization and Paper-Form Workflow

Use this workflow for any `Daily Usage` task, including paper-form entry, row refresh/synchronization, monthly usage calculation, or synchronization back to `Main Stock`.

## Core role

`Main Stock` is the structural/base-data master for `Daily Usage`.

`Daily Usage` is the operational usage-entry surface for day-by-day consumption and the calculation source for current monthly usage and remaining stock.

The complete flow is:

`Main Stock -> Daily Usage structural/base sync -> day usage entry -> Daily Usage calculation -> Main Stock reverse sync`

Do not treat these as independent optional steps when a Daily Usage mutation is performed.

## Current Daily Usage column contract

Always inspect the live sheet before relying on remembered coordinates. Under the current approved contract:

- `A` — `No.`: synchronized from `Main Stock!A`
- `B` — `Items`: synchronized from `Main Stock!B`
- `C` — `Remaining Stock`: synchronized from `Main Stock!F`
- `D` — `Received Stock`: synchronized from `Main Stock!G`
- `E:AI` — day columns `1` through `31`: routine writable usage-entry range
- `AJ` — `This Month Usage`: deterministic calculated field
- `AK` — `This Month Remaining`: deterministic calculated field
- `AL` — `Remark`: preserve existing semantics; write only when supported by the source or explicitly requested
- `AM` — `Expiry Date`: approved Google-Sheet extension synchronized from `Main Stock!C`; derived/read-only in routine Daily Usage work

The day columns `E:AI` are the only routine usage-entry cells. Do not use `A:D`, `AJ:AK`, or `AM` as manual usage-entry fields.

## Mandatory structural parity preflight

Before every Daily Usage mutation, compare the live `Main Stock` and `Daily Usage` structures by item/lot identity, not by row number alone.

The goal is for Daily Usage to represent the same ordered stock-lot rows as Main Stock while preserving historical day entries.

### Forward synchronization mapping

Synchronize these fields from Main Stock to Daily Usage:

- `Main Stock!A No.` -> `Daily Usage!A No.`
- `Main Stock!B Items` -> `Daily Usage!B Items`
- `Main Stock!F Remaining Stock` -> `Daily Usage!C Remaining Stock`
- `Main Stock!G Received Stock` -> `Daily Usage!D Received Stock`
- `Main Stock!C Expiry Date` -> `Daily Usage!AM Expiry Date`

Use verified item/lot identity and order. Do not blindly copy row N in Main Stock to row N in Daily Usage when structural drift is possible.

### Missing Daily Usage rows

If Main Stock contains a confirmed item/expiry-lot row that Daily Usage lacks:

1. identify the correct position from the Main Stock order and sibling-lot family,
2. insert a real row at that position in Daily Usage,
3. populate the synchronized fields `A:D` and `AM`,
4. leave `E:AI` blank for the newly introduced row unless actual source evidence supplies usage,
5. calculate `AJ` and `AK` according to this contract,
6. preserve all pre-existing Daily Usage day-history values on surrounding rows by using structural row insertion rather than overwriting or offset copying.

### Extra or conflicting Daily Usage rows

Do not silently delete a Daily Usage row merely because it has no immediate Main Stock counterpart.

- If the row contains historical usage, remarks, or otherwise meaningful data, classify the discrepancy for review before deletion or remapping.
- If an obsolete/duplicate row can be proven safe to remove without losing operational history, deletion still requires the operation to be explicit and read-back verified.

Historical usage preservation takes priority over forcing superficial row-number parity.

## Expiry Date mirror

`Daily Usage!AM Expiry Date` is an approved Google-Sheet-only derived extension when it is absent from the local Excel Daily Usage sheet.

- Source of truth: the matched lot's structured `Main Stock!C Expiry Date`.
- Place it at the far right after the existing `AL Remark` column.
- Preserve a date representation compatible with Main Stock, normally `mmm-yyyy` for displayed month/year stock expiry.
- Do not infer an expiry from an item-name suffix when the structured Main Stock expiry is blank or conflicting.
- If Main Stock item-name suffix and structured expiry disagree, preserve the Main Stock conflict rules; do not silently manufacture agreement in Daily Usage.

## Read source literally

When the user supplies a Daily Usage paper form, photo, scan, or transcription, identify as available:

- item or row,
- day/date column,
- quantity used,
- remarks or corrections.

Inspect the live sheet so item/lot and day-column alignment comes from current evidence. If handwriting, cell alignment, or the target lot is unclear, state the uncertainty instead of inventing a value.

## Record actual movement

Write actual consumption only to the corresponding day column in `E:AI`.

If the form records usage against a particular row or expiry lot, write it to that corresponding lot. Do not move it to an older or near-expiry lot to satisfy FIFO/FEFO. The source form is the historical movement evidence.

Preserve the distinction between blank and numeric zero.

If a target day cell already contains a value, determine from the source whether the new evidence is a replacement/correction or an additional quantity. Do not automatically add or overwrite without evidence for the intended semantics.

## Deterministic calculations

After structural synchronization and after every usage mutation, calculate the affected Daily Usage rows deterministically.

### This Month Usage

`AJ This Month Usage = SUM(E:AI)`

- Sum numeric day usage across day 1 through day 31.
- Treat blank day cells as zero for arithmetic while preserving them as blank cells.
- Do not use model estimation or narrative reasoning for arithmetic.

### This Month Remaining

`AK This Month Remaining = C Remaining Stock + D Received Stock - AJ This Month Usage`

If no day usage has been recorded, `AJ` is `0` and `AK` equals `C + D`.

`C Remaining Stock` remains the synchronized base/opening stock from Main Stock. Do not replace it with the newly calculated current balance.

## Mandatory reverse synchronization to Main Stock

After `AJ` and `AK` are calculated, synchronize the result back to the same verified Main Stock item/lot:

- `Daily Usage!AJ This Month Usage` -> `Main Stock!J This Month Usage`
- `Daily Usage!AK This Month Remaining` -> `Main Stock!H Stock Status Today`

Do not reverse-sync Daily `AK` into `Main Stock!F Remaining Stock`. `Main Stock!F` remains the base/opening stock field used by the forward synchronization contract.

Match by verified item/lot identity and current structure; do not assume row numbers remain aligned without the parity preflight.

For a routine Daily Usage entry, the reverse synchronization is part of the same transaction, not an optional follow-up. Do not report the Daily Usage operation complete while the corresponding Main Stock `H`/`J` values remain stale.

## Full refresh versus affected-row refresh

A full Daily Usage refresh may be performed when structural drift exists or the user asks for reconciliation:

1. synchronize structure and `A:D`/`AM` from Main Stock,
2. preserve existing `E:AI` usage history and `AL` remarks,
3. recalculate `AJ` and `AK` for all matched rows,
4. reverse-sync `AJ`/`AK` to Main Stock `J`/`H`.

For ordinary paper-form intake when structural parity is already verified, recalculate and reverse-sync only the affected rows unless a wider inconsistency is detected.

## FIFO / FEFO advisory

After faithfully recording actual usage, optionally warn about:

- newer batch used before older batch,
- near-expiry stock bypassed,
- apparently expired stock used,
- possible wastage risk.

Warnings never modify recorded usage.

## Verification contract

After a Daily Usage transaction, read back as applicable:

1. structural row placement and synchronized `A:D`,
2. `AM Expiry Date`,
3. affected day cells in `E:AI`,
4. calculated `AJ` and `AK`,
5. matched `Main Stock!J This Month Usage`,
6. matched `Main Stock!H Stock Status Today`,
7. neighboring rows/cells needed to prove historical usage was not shifted or overwritten.

Do not claim completion until this read-back succeeds.

Use `Audit_Log` for material structural refreshes, repaired row drift, ambiguous historical-row resolution, or other significant multi-row synchronization. Routine individual usage entry does not require an audit row unless otherwise significant.

## Default principle

**Main Stock defines the lot rows and base stock; Daily Usage records actual day usage; Daily Usage calculates the monthly totals/current balance; those calculated results return to Main Stock.**
