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
