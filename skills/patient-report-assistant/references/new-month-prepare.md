# New Month Prepare Workflow

Status: ACTIVE

Purpose: prepare the OPD, IPD, and Monthly Report tabs for a new reporting month without damaging structural rows, formulas, locked administrative values, or unresolved template fields.

## Preconditions

Before any mutation:

1. Confirm the target reporting month and year.
2. Inspect the live workbook and resolve the current OPD, IPD, and Monthly Report tabs.
3. Load `system-contract.md`, `runtime-configuration.md`, `workbook-layout.md`, and `monthly-report-manual-fields.md`.
4. Ensure the Audit Log and Restore Checkpoint mechanism is available.
5. Create a restore checkpoint before clearing any prior-month data.
6. Record the planned operation in the audit trail.

If a restore checkpoint cannot be created, do not perform the destructive clear.

## OPD reset

Starting from row 6 through the live used reporting area:

- clear prior-month values only in columns `C:AG`;
- preserve columns `A:B`;
- discover every structural row containing the ordered calendar sequence `1..31`;
- exclude every discovered structural day-header row from clearing;
- do not stop after the first match;
- do not assume OPD and IPD use the same protected rows.

Current analyzed template expectation:

`5, 18, 21, 22, 25, 31, 46, 57, 64, 79, 84, 87, 101, 115`

The runtime must still verify the live structure before mutation.

After clearing:

- update the OPD `Month/Year` field to the dataset month/year;
- update the standalone OPD month-name field to the dataset month;
- verify every protected `1..31` row remains intact.

## IPD reset

Starting from row 6 through the live used reporting area:

- clear prior-month values only in columns `C:AG`;
- preserve columns `A:B`;
- discover every structural row containing the ordered calendar sequence `1..31`;
- exclude every discovered structural day-header row from clearing;
- do not stop after the first match;
- resolve IPD independently from OPD.

Current analyzed template expectation:

`5, 18, 27, 28, 38, 45, 60, 71, 78, 93, 97, 100, 115, 128`

The runtime must still verify the live structure before mutation.

After clearing:

- update the IPD `Month/Year` field to the dataset month/year;
- update the standalone IPD month-name field to the dataset month;
- verify every protected `1..31` row remains intact.

## Monthly Report preparation

Do not broad-clear the Monthly Report.

Only perform the following targeted actions.

### Automatically update

- report-period heading -> confirmed dataset month/year;
- top report date -> first day of the next calendar month;
- bottom signature date -> exactly the same date as the top report date.

Example for August 2026:

- heading -> `Monthly Report for August/2026`
- top report date -> `1.9.2026`
- bottom signature date -> `1.9.2026`

### Clear previous-month owner-supplied fields

Clear these fields so stale values cannot be carried into the new month:

- `E15` — OPD Old
- `E16` — OPD New
- `G18` — Total No. of Day Care Patients
- `M18` — Elderly No. of Day Care Patients
- `G19` — Total number of patients' days

Leave these blank until the Owner explicitly supplies the new month values.

### Never modify during New Month Prepare

- `D9` — Name of Office
- `D10` — BEDDED
- `K145` — Name
- `K146` — Rank
- Sub-speciality template cells
- Emergency Department literal `-` placeholders
- formula cells
- structural labels
- merged layout cells
- formatting

## Verification

After the operation:

1. Read back OPD protected day-header rows.
2. Read back IPD protected day-header rows.
3. Confirm OPD/IPD cleared regions contain no stale prior-month data outside protected structure.
4. Confirm OPD/IPD month fields match the dataset month/year.
5. Confirm Monthly Report heading matches the dataset month/year.
6. Confirm both report date fields equal the first day of the next month.
7. Confirm the five Owner-supplied Monthly Report fields are blank.
8. Confirm locked/admin/template fields are unchanged.
9. Confirm formulas remain formulas.
10. Record completion and verification result in the Audit Log.

A New Month Prepare run is not complete until all verification checks pass.
