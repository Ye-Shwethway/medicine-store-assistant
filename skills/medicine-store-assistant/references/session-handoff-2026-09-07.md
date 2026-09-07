# $msa Session Handoff — 2026-09-07

Use this note only for continuity of the Medicine Store Assistant personal-skill/live-Google-Sheet workflow. Do not treat it as standalone product-engineering documentation.

## Current operational objective

A September 2026 intake batch has arrived, but it must **not** be entered into the production `Main Stock` yet.

The Owner still needs computer access to pull/save the authoritative August dataset from the legacy Excel file. Until that dataset is archived and reconciled, the current live Google `Main Stock` / `Daily Usage` must remain unchanged as the August production state.

## Canonical transition strategy

Use the staged-cutover month-close workflow documented in `month-close-archive-and-cleanup.md`:

1. Freeze current production `Main Stock` and `Daily Usage`.
2. Wait for Owner to obtain the August Excel dataset from the computer.
3. Archive/reconcile August evidence before any production month reset.
4. Create paired September staging tabs, not a single isolated copy:
   - `Main Stock STAGING 2026-09`
   - `Daily Usage STAGING 2026-09`
5. Perform cleanup/new-month preparation only on staging copies first.
6. Preserve `Main Stock` ↔ `Daily Usage` row alignment.
7. Recompute zero-stock cleanup eligibility from current state rather than trusting old row numbers.
8. Preserve fresh reorder representatives, dormant/sole representatives, unresolved duplicates, and any row needed for evidence/disposition.
9. After staging verification, wait for Owner to sync/reconcile with the computer workflow.
10. Only after Owner confirms the PC-side sync/reconciliation is complete should a fresh production-cutover checkpoint be created and the canonical production tabs be updated.
11. Process the September intake batch only after the September production state is verified.

## Important current rules

- August Final Reorder was already submitted; do not rewrite it.
- The earlier 23-row zero-stock list is a month-close cleanup queue, not immediate-delete authority.
- Physical cleanup must be paired across `Main Stock` and `Daily Usage`, bottom-to-top, after archive verification.
- Do not clear/reset production `Daily Usage` before August archive evidence is complete.
- `This Month Received` is derived from `Main Stock` received-stock state; do not use it as the primary intake source-of-truth.
- September intake processing uses `received-stock-operational-workflow.md` only after month transition is complete.
- Expiry/return/discard refinements are paused for now; do not resume them unless the Owner asks.

## Live workbook

Spreadsheet: `Medicine Store Cloud`
ID: `1kATvZ3tfhwijd0wKx9m15QHNRIdmFnGdvbesVktpjsE`

Do not perform live production mutations for September preparation until the Owner provides/finishes the August Excel archive step.

## Next conversation start

The next chat should begin by reconciling this handoff note plus the canonical skill references, confirming that production remains frozen, and then waiting for or processing the Owner's August Excel dataset before creating September staging tabs.
