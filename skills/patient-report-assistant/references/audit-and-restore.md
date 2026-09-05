# Audit Log and External Restore Snapshot Contract

Status: REQUIRED BEFORE DESTRUCTIVE WORKFLOWS

Purpose: keep the operational patient-report workbook clean while preserving traceability and a simple rollback path.

## Main workbook footprint

Only one additional PRA tab is allowed in the operational workbook:

- `PRA Audit Log`

Do **not** create a `PRA Restore Checkpoints` tab in the operational workbook.

## External restore checkpoint model

Before a destructive workflow such as New Month Prepare:

1. create a full pre-mutation copy of the current patient-report workbook;
2. store that copy in the dedicated Google Drive restore folder;
3. record the checkpoint file name and Drive reference in `PRA Audit Log`;
4. only then perform the destructive mutation.

The copied workbook is the rollback checkpoint for the full workbook state, including formulas, formatting, merged cells, OPD, IPD, Monthly Report, and the audit state present at copy time.

## Dedicated Drive folder

Use this logical structure:

`Patient Report Assistant/Restore Checkpoints/`

Do not scatter checkpoint files through My Drive.

## Snapshot naming

Use a human-readable name containing the reporting month and purpose.

Recommended pattern:

`PRA_Checkpoint_<YYYY-MM>_before-new-month-prepare_<timestamp>`

Example:

`PRA_Checkpoint_2026-08_before-new-month-prepare_2026-09-05`

If more than one checkpoint is created on the same day, include time or a unique operation suffix.

## PRA Audit Log

Use these columns:

1. Timestamp
2. Operation ID
3. Operation Type
4. Reporting Month
5. Target Sheet
6. Target Range / Cells
7. Action
8. Before Summary
9. After Summary
10. Checkpoint File
11. Checkpoint File ID / Link
12. Verification Result
13. Notes

Every destructive/state-changing workflow must append audit entries.

At minimum, New Month Prepare records:

- snapshot checkpoint creation;
- OPD clear;
- OPD month metadata update;
- IPD clear;
- IPD month metadata update;
- Monthly Report targeted clears;
- Monthly Report period/date updates;
- final verification result.

## Formula protection

If a targeted cell unexpectedly contains a formula:

- do not overwrite it;
- abort or narrow the operation;
- report the mismatch;
- preserve the external snapshot as the rollback point.

## Restore behavior

A restore action must:

1. identify the exact checkpoint from `PRA Audit Log`;
2. verify that the snapshot belongs to the intended operation/reporting month;
3. restore from that snapshot only with explicit Owner authorization;
4. read back and verify the restored state;
5. append a restore event to `PRA Audit Log`.

Never perform an unlogged restore.

## Failure rule

If snapshot creation fails, or the checkpoint reference cannot be logged before mutation, abort the destructive workflow.

Safety order:

`snapshot -> log checkpoint -> mutate -> read back -> verify -> log result`
