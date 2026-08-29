# Photo to OPD/IPD Entry Workflow

Use this workflow when the user provides a photographed or scanned paper OPD/IPD monthly form.

## 0. Synchronize source-tab reporting period

Before transcribing daily counts, confirm the dataset month/year and update the OPD/IPD source-tab reporting-period metadata according to `runtime-configuration.md`.

These fields must use the dataset month itself, never the next month.

## 1. Establish form identity

From the image and live workbook, determine:

- OPD or IPD,
- reporting month/year,
- visible day columns,
- visible row labels,
- whether the photo is complete or only part of the form.

Do not infer OPD/IPD from filename alone when the form itself is visible.

## 2. Read the image

Inspect the image directly.

For each visible source cell, classify it internally as:

- `VALUE(n)` — confidently readable numeric value,
- `ZERO` — explicit written/printed zero,
- `BLANK` — intentionally blank/no mark visible,
- `CORRECTED(n)` — correction is visible and final value is clear,
- `AMBIGUOUS` — cannot read safely,
- `OUT_OF_FRAME` — not actually shown.

Do not convert `BLANK`, `AMBIGUOUS`, or `OUT_OF_FRAME` into zero.

## 3. Resolve workbook coordinates

Inspect the live OPD/IPD tab.

Map each source row by:

1. section heading/context,
2. row label,
3. sublabel where present,
4. day-number header.

Use live labels rather than a remembered fixed row map.

If a source label and workbook label differ slightly in spelling but clearly denote the same printed indicator, the mapping may proceed. If two possible rows exist, hold for review.

## 4. Pre-write comparison

Read the intended target cells before writing.

If a target cell already contains a different nonblank value:

- do not silently overwrite it;
- report the conflict with form value, current sheet value, row label, and day;
- wait for explicit correction authorization unless the user's current instruction already clearly authorizes replacement from the source form.

## 5. Write

Write only confidently resolved source cells.

Prefer a bounded batch update over one-cell-at-a-time mutations.

Do not modify:

- row labels,
- date/day headers,
- formulas,
- formatting,
- merged cells,
- unrelated blank cells.

Ambiguous values remain unwritten.

## 6. Read back

Read the exact written range(s) after the mutation.

Confirm every written value matches the transcription matrix.

## 7. Continue to final-report verification

After source readback, run [monthly-report-validation.md](monthly-report-validation.md).

Report:

- OPD/IPD rows entered,
- number of cells written,
- unresolved/ambiguous cells,
- conflicts not overwritten,
- and Monthly Report verification status.
