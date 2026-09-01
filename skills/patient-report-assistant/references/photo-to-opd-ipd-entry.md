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

### Multi-digit guard

A multi-digit handwritten count must be verified as a whole value before entry. Do not collapse a partially visible or lightly written digit into a smaller number. If a cell may be `40` versus `10`, `14` versus `4`, etc., zoom/reinspect the source before classifying it as `VALUE(n)`.

## 3. Resolve workbook coordinates

Inspect the live OPD/IPD tab.

### Mandatory two-stage row anchoring

Never map a handwritten mark directly from image vertical position to a workbook row number.

For every row that contains a mark, resolve in two stages:

1. **Paper row identity** — identify the printed section heading, printed row label, and subtype/sublabel on the photographed form itself.
2. **Workbook row identity** — match that paper-row identity to the live workbook using section heading + row label + subtype/sublabel.

Only after both identities are resolved may the day cell be mapped.

Before writing a page, build an internal row-anchor table containing at minimum:

- section heading,
- paper row label,
- paper subtype/sublabel if any,
- resolved live workbook row,
- visible day span.

Use live labels rather than a remembered fixed row map.

If a source label and workbook label differ slightly in spelling but clearly denote the same printed indicator, the mapping may proceed. If two possible rows exist, hold for review.

### Adjacent-row shift guard

For every nonblank handwritten mark, visually check the printed row label immediately above and below the mark before finalizing the row assignment.

This is mandatory when:

- handwriting touches or approaches a horizontal grid line,
- two adjacent rows have similar clinical labels,
- the row is near a section boundary,
- the same day contains marks in neighboring rows,
- or the source image is angled/skewed.

Do not use a repeated vertical offset across a page as a substitute for reading each row label.

### Duplicate/omission guard

After the first transcription pass, perform a second independent pass over all visibly marked source cells on that page.

For each printed row, compare:

- number of visible marked cells on paper,
- day positions of those marks,
- number/day positions planned for the workbook row.

If a visible paper row has marks but the planned workbook row is empty, or an adjacent workbook row has those marks instead, stop and resolve the mismatch before writing.

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

Read-back matching is necessary but not sufficient: it only proves that the planned matrix was written correctly. It does **not** prove that the matrix was mapped to the correct paper rows. Therefore, after read-back, repeat the row-anchor check for every written row against the source image.

## 7. Continue to final-report verification

After source readback, run [monthly-report-validation.md](monthly-report-validation.md).

Report:

- OPD/IPD rows entered,
- number of cells written,
- unresolved/ambiguous cells,
- conflicts not overwritten,
- and Monthly Report verification status.
