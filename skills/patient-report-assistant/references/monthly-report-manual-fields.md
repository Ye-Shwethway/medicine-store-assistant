# Monthly Report Manual-Field Registry

Status: **ACTIVE — current owner rules locked from the analyzed July 2026 workbook.**

This registry governs observed non-formula fields in `Monthly Report`.

## Status meanings

- `LOCKED` — do not modify unless the Owner explicitly instructs it.
- `OWNER-SUPPLIED` — write only the exact value supplied by the Owner for the current month.
- `AUTO-DATE` — deterministic date rule; may be populated automatically once the reporting month is confirmed.
- `DERIVED` — formula-driven; not a manual-entry target.
- `UNDECIDED` — rule not yet established.

## Locked administrative fields

### Name of Office — `D9`

Rule: **LOCKED**

- Never modify this field unless the Owner explicitly instructs a change.
- Do not infer or normalize the office name.
- Do not copy a value from another workbook/month as a write action unless explicitly asked.

### BEDDED — `D10`

Rule: **LOCKED**

- Never modify this field unless the Owner explicitly instructs a change.
- Do not infer the bed count from hospital context or prior months.

## Report Date — `K9`

Rule: **AUTO-DATE**

The report is closed and submitted on the first day of the month following the data month.

Therefore:

`Report Date = first day of the next calendar month`

Examples:

- July 2026 data -> `1.8.2026`
- August 2026 data -> `1.9.2026`
- December 2026 data -> `1.1.2027`

Requirements:

1. Confirm the reporting month/year before writing.
2. Compute the next calendar month correctly across year boundaries.
3. Preserve the workbook's expected date display convention unless the user explicitly requests another format.
4. Do not derive the date from the current system date when the report month is known.

## OPD Old / New — `E15`, `E16`

Rule: **OWNER-SUPPLIED**

- `E15` — No. of OPD patient — Old
- `E16` — No. of OPD patient — New

Write only the exact values supplied by the Owner.

Do not calculate these from OPD daily rows.
Do not infer them from total OPD counts.
If the Owner has not provided the values, leave them unchanged and report them as awaiting Owner input.

## Total No. of Day Care Patients — `G18`

Rule: **OWNER-SUPPLIED**

Write only the exact value supplied by the Owner.

Do not derive this field from other visible day-care values unless the Owner establishes a future formula/rule.

## Elderly — No. of Day Care Patients — `M18`

Rule: **OWNER-SUPPLIED**

Write only the exact value supplied by the Owner.

Do not infer it from elderly OPD/IPD totals or from `G18`.

## Total number of patients' days — `G19`

Rule: **OWNER-SUPPLIED**

Write only the exact value supplied by the Owner.

Do not calculate this value from IPD admissions, bed occupancy, or other report rows unless the Owner explicitly establishes a future rule.

## Sub-speciality block

The analyzed July 2026 example contains Neuro Surgery, Paediatric Surgery and Urosurgery OPD/IPD/Total cells in rows 29–31.

Current Owner rule: **LEAVE AS TEMPLATE / DO NOT ENTER**

These services are not available at the reporting facility.

- Do not populate these cells during monthly reporting.
- Do not infer counts from other specialties.
- Preserve the existing template values/zeros unless the Owner explicitly requests a template change.

## Emergency Department block

The analyzed example contains literal `-` placeholders:

- `F114` — Total Patients in ED
- `F116` — Admitted Patients from ED
- `F117` — Refer Patients from ED
- `F118` — Triage Red
- `F119` — Triage Yellow
- `F120` — Triage Green
- `F121` — Brought Death
- `F122` — ED Death

`F115` (Day care Patients) is formula-driven from the report and is **DERIVED**, not manual.

Current status of the literal `-` fields: **LEAVE AS TEMPLATE / DO NOT ENTER**

Do not replace `-` with zero or counts unless the Owner explicitly establishes a future ED reporting workflow.

## Signature block

Observed in the July 2026 example:

- `K145` — Name
- `K146` — Rank
- `K147` — Date

Rules:

- `K145` Name — **LOCKED**; do not modify unless the Owner explicitly instructs a change.
- `K146` Rank — **LOCKED**; do not modify unless the Owner explicitly instructs a change.
- `K147` Date — **AUTO-DATE**; use exactly the same computed report date as `K9`.

Therefore, for August 2026 data:

- `K9` = `1.9.2026`
- `K147` = `1.9.2026`

## Report-period heading

The report heading contains the reporting month/year, for example:

`Monthly Report for July/2026`

Rule: **AUTO-PERIOD**

When the reporting month is confirmed, update the heading to that same month/year.

Examples:

- July 2026 data -> `Monthly Report for July/2026`
- August 2026 data -> `Monthly Report for August/2026`
- December 2026 data -> `Monthly Report for December/2026`

Do not derive the reporting month from the current system date when the user has identified the data month.

## Current automatic/manual summary

Automatically writable after reporting month is confirmed:

- `K9` Report Date = first day of next calendar month
- `K147` Signature Date = same value as `K9`
- report-period heading = confirmed data month/year

Owner-supplied only:

- `E15` OPD Old
- `E16` OPD New
- `G18` Total No. of Day Care Patients
- `M18` Elderly No. of Day Care Patients
- `G19` Total number of patients' days

Never modify without explicit Owner instruction:

- `D9` Name of Office
- `D10` BEDDED
- `K145` Name
- `K146` Rank

Leave as template / do not enter:

- Sub-speciality service block for unavailable specialties
- Emergency Department literal `-` placeholder fields

No other manual-entry fields are currently identified in the analyzed July 2026 `Monthly Report` layout. If the live template changes, re-inspect formula/literal status before applying this registry.
