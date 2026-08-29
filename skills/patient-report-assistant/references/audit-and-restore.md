# Audit Log and Restore Checkpoint Contract

Status: REQUIRED BEFORE DESTRUCTIVE WORKFLOWS

Purpose: every destructive or state-changing Patient Report Assistant operation must be traceable and reversible.

## Required workbook tabs

Create two dedicated tabs:

- `PRA Audit Log`
- `PRA Restore Checkpoints`

These tabs belong to the Patient Report Assistant workflow and must not be mixed with OPD, IPD, or Monthly Report reporting data.

## PRA Audit Log

Recommended columns:

1. Timestamp
2. Operation ID
3. Operation Type
4. Reporting Month
5. Target Sheet
6. Target Range / Cells
7. Action
8. Before Summary
9. After Summary
10. Checkpoint ID
11. Verification Result
12. Notes

Every write operation must create or append an audit entry.

At minimum, New Month Prepare must record:

- checkpoint creation;
- OPD clear;
- OPD month metadata update;
- IPD clear;
- IPD month metadata update;
- Monthly Report targeted clears;
- Monthly Report period/date updates;
- final verification result.

## PRA Restore Checkpoints

A checkpoint must preserve enough information to restore every cell that will be mutated by the operation.

Recommended columns:

1. Checkpoint ID
2. Created At
3. Operation ID
4. Reporting Month
5. Sheet
6. Range / Cell
7. Previous Value
8. Previous Formula
9. Previous Value Type
10. Restore Status
11. Restored At
12. Notes

For a destructive workflow, capture the pre-write state before the first mutation.

## Checkpoint rule

One logical operation should use one Operation ID and one Checkpoint ID, even when it touches multiple sheets.

For New Month Prepare, the checkpoint must cover:

- all OPD cells that will be cleared or updated;
- all IPD cells that will be cleared or updated;
- every Monthly Report cell that will be cleared or updated.

Do not checkpoint unrelated cells.

## Formula protection

If a targeted cell contains a formula unexpectedly:

- record the formula;
- do not overwrite it;
- abort or narrow the operation;
- report the mismatch.

## Restore behavior

A restore action must:

1. resolve the checkpoint by ID;
2. verify the current workbook/tab identity;
3. restore recorded cells to their exact previous values/formulas;
4. read back restored cells;
5. update Restore Status and Restored At;
6. append a restore event to `PRA Audit Log`.

Never perform an unlogged restore.

## Failure rule

If audit logging or checkpoint creation fails before a destructive operation, abort the destructive operation.

Safety priority:

`checkpoint -> audit planned operation -> mutate -> read back -> verify -> audit result`
