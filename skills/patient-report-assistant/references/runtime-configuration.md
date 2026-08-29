# Runtime Configuration

## Workbook resolution

Do not hardcode a private/live spreadsheet URL or ID into this public/shareable skill package.

At runtime:

1. use the workbook URL supplied or confirmed by the user;
2. read spreadsheet metadata;
3. identify the current report/source tabs by live names and content;
4. verify the reporting month before any write.

## Current analyzed layout pattern

The analyzed July 2026 example contains three functional tabs:

- `Monthly Report` — aggregate/final report
- `OPD` — daily OPD source-entry grid
- `IPD` — daily IPD source-entry grid

These names are observed configuration, not permanent assumptions. Inspect live metadata every run.

## Day columns

The analyzed OPD/IPD layout uses one row per report indicator and daily columns for days 1–31.

Resolve day columns from the visible header values. Do not rely only on remembered letters such as `C:AG`.

## Row resolution

Resolve a target row primarily by its visible report label and section context.

Do not write to a remembered row number unless the live label at that row has been verified.

## Monthly Report

Treat the aggregate report as mostly formula-driven.

Use the live formula view when deciding whether a report cell is:

- formula-derived,
- a static label,
- a manual-entry field,
- or a placeholder.

## Month rollover

A new month may reuse the same workbook structure or a copied template.

Never carry prior-month counts into a new month unless the user explicitly requests a template-copy workflow that clears source-entry values safely.

## OPD/IPD reporting-period metadata

The OPD and IPD source tabs contain their own reporting-period fields. These represent the **dataset month/year itself**, not the submission date.

For each source tab, update both:

1. the `Month/Year` field near the top of the form;
2. the separate month-name field below it.

Rules:

- use the confirmed dataset month/year;
- do **not** advance these fields to the next month;
- keep OPD and IPD in sync;
- verify both fields after writing.

Example for August 2026 data:

- OPD `Month/Year` -> August 2026
- OPD month-name field -> `August`
- IPD `Month/Year` -> August 2026
- IPD month-name field -> `August`

The next-month rule applies only to the final-report submission date fields such as `Monthly Report!K9` and the matching signature date.

## New-month reset structural preflight

Any future workflow that clears prior-month OPD/IPD entry values must first resolve protected structure separately for each source tab.

Minimum protected structure includes the live `1..31` day-header row on OPD and the independently resolved `1..31` day-header row on IPD.

Never build a single shared row-number assumption for both tabs.
