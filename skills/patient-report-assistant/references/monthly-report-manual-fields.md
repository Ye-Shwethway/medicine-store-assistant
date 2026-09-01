# Monthly Report Manual-Field Registry

Status: **ACTIVE — updated from the Owner-approved August 2026 final workbook.**

This registry governs observed non-formula fields in `Monthly Report`.

## Status meanings

- `LOCKED` — do not modify unless the Owner explicitly instructs it.
- `OWNER-SUPPLIED` — write only the exact value supplied or explicitly confirmed by the Owner for the current month.
- `AUTO-DATE` — deterministic date rule; may be populated automatically once the reporting month is confirmed.
- `AUTO-PERIOD` — deterministic reporting-period heading.
- `DERIVED` — formula-driven; not a manual-entry target.
- `MANUAL-HYBRID` — current approved template intentionally uses manual report values that must reconcile to source data using a defined rule.
- `UNDECIDED` — rule not yet established.

## Locked administrative fields

### Name of Office — current live `D9`

Rule: **LOCKED**

- Never modify this field unless the Owner explicitly instructs a change.
- Do not infer or normalize the office name.

### BEDDED — current live `D10`

Rule: **LOCKED**

- Never modify this field unless the Owner explicitly instructs a change.
- Do not infer the bed count from hospital context or prior months.

## Report Date

Rule: **AUTO-DATE**

The report is closed and submitted on the first day of the month following the data month.

Therefore:

`Report Date = first day of the next calendar month`

Examples:

- July 2026 data -> `1.8.2026`
- August 2026 data -> `1.9.2026`
- December 2026 data -> `1.1.2027`

Resolve the live cell coordinate before writing; do not rely on a stale remembered address.

## OPD Old / New

Rule: **OWNER-SUPPLIED**

- OPD Old
- OPD New

Write only the exact values supplied by the Owner.

Do not calculate these from the raw OPD daily rows.

In the current approved workflow, OPD Old + New reconciles to the **adjusted Specialty OPD total after day-care patients are separated**, not necessarily to the raw OPD source total.

## Total No. of Day Care Patients

Rule: **OWNER-SUPPLIED**

Write only the exact value supplied or confirmed by the Owner.

The final validation must reconcile this value to the sum of the Specialty `Day Care Pt` row when that row exists.

## Specialty Day Care Pt row

Rule: **OWNER-SUPPLIED / MANUAL-HYBRID**

The Owner-approved August 2026 final report contains a `Day Care Pt` row in the Specialty services table.

Current workflow:

- day-care patients are included in the OPD source counts;
- the Owner identifies the specialty allocation for those day-care patients from the operational patient list/records;
- the Specialty `Day Care Pt` row is entered manually;
- the Specialty `OPD` value must be the raw OPD source total minus the day-care allocation for that specialty.

Do not infer specialty day-care allocation from the aggregate OPD paper form alone.

Do not overwrite an Owner-approved specialty allocation with zero because it is not represented separately on the OPD paper form.

## Specialty OPD / In-patient rows

Rule: **MANUAL-HYBRID in the current approved August 2026 template**

Current approved workbook stores Specialty `OPD` and `In-patient` report values as literals rather than direct source formulas.

Validation rules:

- Specialty OPD = raw OPD source total - Specialty Day Care Pt
- Specialty In-patient = raw IPD source total
- Specialty Total = OPD + In-patient + Day Care Pt

Do not automatically replace approved literals with formulas unless the Owner authorizes a template redesign.

## Elderly — No. of Day Care Patients

Rule: **OWNER-SUPPLIED**

Write only the exact value supplied by the Owner.

Do not infer it from elderly OPD/IPD totals or from the overall day-care total.

## Total number of patients' days

Rule: **OWNER-SUPPLIED**

Write only the exact value supplied by the Owner.

Do not calculate this value from IPD admissions, bed occupancy, or other report rows unless the Owner explicitly establishes a future rule.

## Sub-speciality block

Current Owner rule: **LEAVE AS TEMPLATE / DO NOT ENTER**

These services are not available at the reporting facility.

- Do not populate these cells during monthly reporting.
- Do not infer counts from other specialties.
- Preserve the existing template values/zeros unless the Owner explicitly requests a template change.

## Emergency Department block

Current status of the literal `-` fields: **LEAVE AS TEMPLATE / DO NOT ENTER**

Do not replace `-` with zero or counts unless the Owner explicitly establishes a future ED reporting workflow.

## Signature block

Rules:

- Name — **LOCKED**; do not modify unless the Owner explicitly instructs a change.
- Rank — **LOCKED**; do not modify unless the Owner explicitly instructs a change.
- Date — **AUTO-DATE**; use exactly the same computed report date as the report-date field.

Resolve live coordinates before writing because row insertion can shift the signature block.

## Report-period heading

Rule: **AUTO-PERIOD**

When the reporting month is confirmed, update the heading to that same month/year.

Example:

`Monthly Report for August/2026`

Do not derive the reporting month from the current system date when the user has identified the data month.

## Current automatic/manual summary

Automatically writable after reporting month is confirmed:

- report date = first day of next calendar month
- signature date = same report date
- report-period heading = confirmed data month/year

Owner-supplied/manual-hybrid:

- OPD Old
- OPD New
- Total No. of Day Care Patients
- Specialty Day Care Pt allocation
- adjusted Specialty OPD values when current template stores them as literals
- Specialty In-patient values when current template stores them as literals
- Elderly No. of Day Care Patients
- Total number of patients' days

Never modify without explicit Owner instruction:

- Name of Office
- BEDDED
- signature Name
- signature Rank

Leave as template / do not enter:

- Sub-speciality service block for unavailable specialties
- Emergency Department literal `-` placeholder fields

If the live template changes, re-inspect formula/literal status and row coordinates before applying this registry.
