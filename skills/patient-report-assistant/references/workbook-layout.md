# Workbook Layout Contract

## Functional model

The monthly workbook has three roles:

`Paper OPD/IPD forms -> OPD/IPD daily source grids -> Monthly Report aggregates`

The source grids are the routine transcription targets.

The Monthly Report is primarily a derived presentation/reporting surface, but the current approved template also contains a small manual/hybrid specialty-services layer for day-care separation.

## OPD/IPD pattern

Typical structure:

- rows represent report indicators,
- day columns represent calendar days,
- section headers divide service groups,
- some rows use a second-column subtype such as New/Old or Emergency/Elective.

Because templates can change, the skill must inspect the live sheet rather than treating row numbers as API identifiers.

## Monthly Report pattern

The final report contains:

- static labels/headings,
- formulas summing OPD/IPD rows,
- formulas combining report subtotals,
- a small number of manual values,
- administrative/header/signature values,
- and some literal placeholders.

A literal value is not automatically an error and is not automatically a field to populate.

## Approved August 2026 specialty-services model

The Owner-approved August 2026 final report adds a `Day Care Pt` row inside the Specialty services table between `In-patient` and `Total`.

Current operational meaning:

- the OPD daily source grid may include patients later classified as day-care patients;
- those day-care patients must be separated from the final-report Specialty `OPD` row;
- the specialty-specific day-care allocation is currently a manual/Owner-supplied report value;
- the final Specialty `Total` row includes `OPD + In-patient + Day Care Pt`.

Therefore, when a specialty has day-care patients:

`Raw OPD source total = Report Specialty OPD + Report Specialty Day Care Pt`

and:

`Report Specialty Total = Report Specialty OPD + Report Specialty In-patient + Report Specialty Day Care Pt`

The overall `Total No. Day Care Patients` must reconcile to the sum of the specialty `Day Care Pt` row.

The overall OPD Old/New total should reconcile to the adjusted Specialty `OPD` total, not to the raw OPD source total when day-care patients are present.

### Current implementation status

In the Owner-approved August 2026 workbook, the specialty `Day Care Pt` values and the adjusted Specialty `OPD` values are currently manual literals. The `Total` row beneath them remains formula-driven.

Do not automatically replace these approved manual literals with raw OPD formulas. Formula automation for day-care separation is a future template enhancement unless the Owner explicitly authorizes it.

If the live template later restores formulas for these rows, inspect and follow the live formula contract rather than this historical coordinate pattern.

## Structural preservation

Routine data entry must not change:

- tab names,
- row/column order,
- merged ranges,
- print layout,
- formulas,
- number formats,
- borders/fills,
- or report labels.

Any template redesign is outside the routine transcription workflow.

## Protected day-header rows

The OPD and IPD tabs contain multiple structural rows whose day columns are the ordered calendar sequence `1` through `31`.

These rows are **template structure**, not monthly patient data, and every one of them must survive a new-month reset.

### Verified template — protected rows

The latest live/snapshot verification established these complete structural sets:

**OPD — 14 rows**

`5, 18, 21, 22, 25, 31, 46, 57, 64, 78, 83, 86, 101, 114`

**IPD — 14 rows**

`5, 18, 27, 28, 38, 45, 60, 71, 78, 92, 97, 100, 115, 128`

The OPD and IPD lists are intentionally separate. Never assume matching row numbers between the two tabs.

### Mandatory protection rule

Before any new-month clearing/reset operation:

1. inspect OPD across the full used report area and find **every** row whose day columns contain the ordered sequence `1, 2, 3, ... 31`;
2. inspect IPD independently across the full used report area and find **every** such row;
3. compare the live-discovered rows against the expected template structure when a known template is in use;
4. mark the complete discovered set on each tab as protected structure;
5. exclude all protected rows from every value-clearing/reset range;
6. after reset, read back every protected row and verify that the full `1..31` sequence remains intact.

Do not stop after finding the first `1..31` row.

### Structural mismatch rule

The row lists above document the verified template, but runtime safety depends on live discovery.

If:

- the number of discovered day-header rows changes,
- an expected row no longer contains `1..31`,
- an additional `1..31` row appears,
- or OPD/IPD structure has shifted,

do not perform a broad reset using stale coordinates. Re-resolve the live structure first and report the mismatch.

### Never clear structural day values

A month-preparation/reset operation must never delete, blank, replace, renumber, or shift any `1..31` day-header values.

If the complete structural set cannot be resolved confidently for either tab, stop the reset for that tab rather than clearing broad ranges.
