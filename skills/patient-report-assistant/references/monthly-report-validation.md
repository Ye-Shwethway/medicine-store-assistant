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

## 2. Verify source linkage

For formula-derived totals affected by the current source entry:

- confirm the formula still exists,
- confirm referenced OPD/IPD tabs and ranges exist,
- confirm the formula covers the intended day span,
- and compare the displayed result with an independent source sum when practical.

## 3. Detect, do not silently repair

Surface issues such as:

- formula replaced by a literal,
- broken reference,
- unexpected range boundary,
- source total not matching report result,
- blank manual field,
- stale prior-month administrative value.

Do not repair formulas during routine transcription unless the user separately authorizes formula correction.

## 4. Manual-field routing

For non-formula cells that appear to require reporting input, consult [monthly-report-manual-fields.md](monthly-report-manual-fields.md).

Follow the active registry exactly. Current automatic non-formula fields are the report-period heading, `K9` report date, and `K147` signature date. Owner-supplied, locked, and leave-as-template fields must not be inferred.

## 5. Final report

Return a concise verification summary:

- source-entry readback: PASS / ISSUES
- formula propagation: PASS / ISSUES
- manual fields: COMPLETE / MISSING / UNDECIDED
- unresolved image values
- any formula/template anomaly requiring user review
