# Monthly Report Validation Workflow

Run this after OPD/IPD data entry or when the user asks to verify the final monthly report.

## 1. Inspect formulas, not only displayed values

Read the relevant Monthly Report range with formula visibility.

Classify relevant result cells as:

- formula-derived,
- manual value,
- placeholder,
- or blank.

Do not mistake a displayed total for a hardcoded number without checking its underlying formula.

The current approved template may intentionally contain manual literals in the Specialty `OPD`, `In-patient`, and `Day Care Pt` rows. Do not automatically classify those literals as broken formulas; validate them against the source/reconciliation rules below.

## 2. Verify source linkage

For formula-derived totals affected by the current source entry:

- confirm the formula still exists,
- confirm referenced OPD/IPD tabs and ranges exist,
- confirm the formula covers the intended day span,
- and compare the displayed result with an independent source sum when practical.

For daily OPD/IPD source formulas, the intended month span is Day 1 through Day 31, normally `C:AG` in the current source-grid layout. If the live day columns differ, resolve them from the live header rather than hardcoding letters.

## 3. Day-care specialty reconciliation

The Owner-approved August 2026 final form separates day-care patients inside the Specialty services table.

Day-care patients are currently present inside the raw OPD source counts and must be removed from the final-report Specialty `OPD` row, then displayed separately in `Day Care Pt`.

For every specialty with a day-care allocation, verify:

`Raw OPD source total = Report Specialty OPD + Report Specialty Day Care Pt`

Verify In-patient independently:

`Raw IPD source total = Report Specialty In-patient`

Verify the final specialty total:

`Report Specialty Total = OPD + In-patient + Day Care Pt`

Then verify the overall relationships:

- sum of Specialty `Day Care Pt` = `Total No. Day Care Patients`;
- sum of adjusted Specialty `OPD` values = OPD Old + OPD New when the current Owner workflow uses those fields as the adjusted OPD total;
- do **not** compare OPD Old + New directly to the raw OPD source total when day-care patients are present.

The day-care specialty allocation is currently Owner-supplied/manual. Do not infer which specialty a day-care patient belongs to from the aggregate OPD paper form alone.

## 4. Detect, do not silently repair

Surface issues such as:

- formula replaced by a literal where the live approved template expects a formula,
- broken reference,
- unexpected range boundary,
- source total not matching report result,
- day-care reconciliation mismatch,
- blank manual field,
- stale prior-month administrative value.

Do not repair formulas during routine transcription unless the user separately authorizes formula correction.

## 5. Manual-field routing

For non-formula cells that appear to require reporting input, consult [monthly-report-manual-fields.md](monthly-report-manual-fields.md).

Follow the active registry exactly. Current automatic non-formula fields are the report-period heading, report date, and signature date. Owner-supplied, locked, and leave-as-template fields must not be inferred.

## 6. Final report

Return a concise verification summary:

- source-entry readback: PASS / ISSUES
- paper-row remap verification: PASS / ISSUES
- formula propagation: PASS / ISSUES
- day-care reconciliation: PASS / ISSUES / NOT APPLICABLE
- manual fields: COMPLETE / MISSING / UNDECIDED
- unresolved image values
- any formula/template anomaly requiring user review
