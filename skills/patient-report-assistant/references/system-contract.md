# Patient Report Assistant — System Contract

## Purpose

This skill assists with monthly hospital patient-report data entry from staff-completed paper OPD/IPD forms and with verification of the resulting aggregate report.

The present scope is transcription and report verification. It is not a clinical decision-support workflow.

## Standalone boundary

This contract belongs only to `patient-report-assistant`.

It has no dependency on:

- Medicine Store Assistant skill rules,
- Medicine Store Assistant inventory sheets,
- CMS catalogue/mapping logic,
- inventory databases,
- Medicine Store Assistant project roadmap or runtime state.

## Source-of-truth rule

For a transcription task, the photographed or otherwise supplied paper form is the source evidence for what staff recorded.

The live workbook is authoritative for:

- current tab names,
- row/column structure,
- formulas,
- merged cells,
- existing values,
- and the active reporting layout.

A previous month may be used to understand layout, but it must not silently supply current-month counts.

## Exact transcription rule

Do not reinterpret a source value merely to make totals look plausible.

Preserve the difference between:

- `0`
- blank
- unreadable
- crossed out / corrected
- not visible in the image

If a final corrected value can be read confidently, use that final value. Otherwise hold for review.

## Formula protection

Monthly Report formulas are derived logic, not routine data-entry targets.

Never replace, clear, or rewrite formulas during ordinary OPD/IPD transcription.

If a formula appears suspicious, broken, stale, or inconsistent, report it as a validation issue. Formula repair is a separate explicitly authorized operation.

## Manual-field protection

Some Monthly Report cells are intentionally not formula-driven.

Do not infer that a non-formula cell should be populated simply because neighboring fields are formulas. Use `monthly-report-manual-fields.md` and explicit user policy.

## Write authorization

Inspection and planning do not imply write authorization.

When writes are authorized:

- target only verified cells,
- avoid broad destructive ranges,
- preserve formatting/validation/formulas,
- and read back the exact affected ranges.

## Verification

After each write slice:

1. read back the OPD/IPD cells,
2. verify the source values match the form,
3. read the relevant Monthly Report result cells,
4. independently check obvious source sums when practical,
5. report any discrepancy without silently compensating elsewhere.

## Privacy and minimization

Use only the information needed for monthly aggregate reporting.

Do not copy unrelated patient identifiers or clinical details into the workbook when the report requires only aggregate counts.
