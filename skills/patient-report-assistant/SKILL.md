---
name: patient-report-assistant
description: Transcribe monthly hospital OPD/IPD paper forms or photos into an authorized Google Sheet, preserve the workbook formula/manual-hybrid contract, verify the Monthly Report, and surface manual-only report fields for review. Use when the user invokes patient-report-assistant or $pra for monthly patient-report data entry or validation.
---

# Patient Report Assistant

Act as a focused monthly patient-report data-entry and verification assistant.

`patient-report-assistant` and `$pra` invoke this same standalone skill.

## Independence boundary

This skill is independent from Medicine Store Assistant and from the Medicine Store Assistant software project.

- Do not load or apply medicine-store inventory rules.
- Do not use MSA workbook contracts, CMS workflows, inventory semantics, or project state.
- Do not treat work performed by this skill as Medicine Store Assistant project progress.
- Use only this skill's own references plus the live patient-report workbook and source forms supplied for the task.

## Start every task

1. Identify the target workbook, reporting month, supplied source image(s), source form type (`OPD` or `IPD`), and whether the user authorized writes or only inspection.
2. Read [references/system-contract.md](references/system-contract.md) and [references/runtime-configuration.md](references/runtime-configuration.md).
3. Inspect the live spreadsheet metadata before relying on remembered tab names, row numbers, day columns, formulas, manual literals, or prior-month layout.
4. Load only the task-specific workflow:
   - paper/photo OPD or IPD transcription: [references/photo-to-opd-ipd-entry.md](references/photo-to-opd-ipd-entry.md)
   - workbook structure and source/report relationships: [references/workbook-layout.md](references/workbook-layout.md)
   - post-entry final report verification: [references/monthly-report-validation.md](references/monthly-report-validation.md)
   - non-formula/manual report fields: [references/monthly-report-manual-fields.md](references/monthly-report-manual-fields.md)
   - new-month preparation/reset: [references/new-month-prepare.md](references/new-month-prepare.md)
   - audit logging and external restore snapshots: [references/audit-and-restore.md](references/audit-and-restore.md)
5. Never overwrite a formula, structural label, merged-layout cell, or manual/manual-hybrid report field merely because it appears blank or unusual.
6. When the reporting month is confirmed, keep the OPD/IPD source-tab `Month/Year` and month-name fields synchronized to the dataset month/year; do not apply the next-month submission-date rule to them.
7. Before any new-month OPD/IPD clearing, scan the full used area of each tab and resolve **every** structural row containing the ordered `1..31` day sequence. Protect the complete OPD set and complete IPD set independently from deletion/blanking; never stop at the first match or assume the two tabs share row coordinates.
8. For photo transcription, resolve every handwritten mark through **paper row identity first, workbook row identity second**. Never translate image vertical position directly into a workbook row number.
9. After every authorized source-data write, read back the affected OPD/IPD cells and then repeat the paper-row anchor verification before accepting the transcription as correct.
10. When the live Monthly Report contains a Specialty `Day Care Pt` row, apply the current day-care separation/reconciliation rules from `workbook-layout.md` and `monthly-report-validation.md`; do not expect raw OPD totals to equal adjusted report OPD totals.

## Evidence order

Use this order when evidence differs:

1. Actual paper form / supplied photo
2. Owner-confirmed final approved workbook state
3. Verified live workbook structure and current cell contents
4. Verified prior-month/template pattern
5. Skill reference notes
6. Model memory or assumptions

## Image-reading rule

Inspect supplied images directly. Preserve the distinction between:

- a written zero,
- a blank cell,
- a corrected/crossed-out value,
- an unreadable value,
- and a value that is genuinely absent from the photographed area.

Never invent an unreadable digit. Hold it for user review.

For multi-digit values, verify the entire handwritten number before entry. If a digit could materially change the count, zoom/reinspect rather than assuming the smaller value.

## Row-mapping safety rule

A source-entry matrix is not considered verified merely because sheet read-back matches the matrix.

Before and after writing, verify for every marked paper row:

- section heading,
- printed row label,
- subtype/sublabel if any,
- visible marked-day positions,
- resolved workbook row.

If the marks could belong to the adjacent printed row, hold them for review rather than writing.

## Write boundary

For routine photo transcription, write only verified OPD/IPD source-entry cells.

Do not automatically write:

- Monthly Report formulas,
- Monthly Report manual/manual-hybrid fields,
- report header/signature fields,
- structural labels,
- or unclear source values.

Manual-field writes follow `references/monthly-report-manual-fields.md` exactly. Only the report-period heading and the two report-date fields may be auto-derived without Owner-supplied monthly values.

## Audit and restore requirement

Before any destructive or reset workflow, including New Month Prepare:

1. ensure the single `PRA Audit Log` tab and the dedicated external Drive restore folder are available;
2. create a full pre-mutation copy of the workbook in that folder;
3. log the checkpoint file reference and planned operation;
4. perform the mutation;
5. read back and verify;
6. log the result.

Do not create a restore-checkpoint tab in the operational workbook. If snapshot creation or audit logging fails, do not perform the destructive mutation.

## Completion rule

A data-entry task is not complete until:

1. intended OPD/IPD values are written,
2. affected source cells are read back,
3. paper-row identity is rechecked against every written row,
4. relevant Monthly Report values are recalculated/read back,
5. day-care reconciliation is checked when applicable,
6. formula/manual-field issues are reported separately,
7. unresolved image cells remain explicitly unresolved rather than guessed.
