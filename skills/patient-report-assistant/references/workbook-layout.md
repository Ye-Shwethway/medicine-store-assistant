# Workbook Layout Contract

## Functional model

The monthly workbook has three roles:

`Paper OPD/IPD forms -> OPD/IPD daily source grids -> Monthly Report aggregates`

The source grids are the routine transcription targets.

The Monthly Report is primarily a derived presentation/reporting surface.

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

The OPD and IPD tabs each contain a structural day-header row with calendar day numbers `1` through `31`.

These day numbers are **template structure**, not monthly patient data.

### Mandatory protection rule

Before any new-month clearing/reset operation:

1. inspect OPD independently and locate the row whose day columns contain the ordered sequence `1, 2, 3, ... 31`;
2. inspect IPD independently and locate its own `1, 2, 3, ... 31` day-header row;
3. mark both resolved rows as protected structure for the current operation;
4. exclude those rows from every value-clearing/reset range;
5. read them back after the reset and verify all day numbers remain intact.

Do not assume the OPD and IPD day-header rows share the same row number.

The analyzed July 2026 workbook currently places both headers on row 5, but this is an observed template fact only, not a permanent coordinate contract.

### Never clear structural day values

A month-preparation/reset operation must never delete, blank, replace, renumber, or shift the `1..31` day values.

If the sequence cannot be resolved confidently on either tab, stop the reset for that tab and report the structural ambiguity rather than clearing broad ranges.
