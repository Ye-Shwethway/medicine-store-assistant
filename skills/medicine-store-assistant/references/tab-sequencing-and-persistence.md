# Tab Sequencing and Persistence Policy

Use this reference when creating, reordering, archiving, or deciding the retention of workbook tabs in the Medicine Store Cloud spreadsheet.

## Goal

Keep the live workbook easy for a human operator to use while preserving assistant evidence and auditability.

The workbook has two broad tab groups:

1. **User-facing operational tabs** — frequently opened by staff or the user.
2. **Assistant/support tabs** — staging, reconciliation, historical evidence, mapping memory, or computation support.

Tab order is a usability contract. Reordering tabs is allowed when authorized because it does not change the production column contracts inside `Main Stock` or `Daily Usage`.

## Canonical front-of-workbook order

Keep these tabs at the front when they exist:

1. `Main Stock`
2. `Daily Usage`
3. `Fixed Assets`
4. the **latest active CMS price-list tab**, for example `CMS_Price_List_202608`
5. `Audit_Log`

After those, place assistant/support tabs such as:

- `Item_Mapping`,
- `CMS_Batch_<TRANSFER>_<DATE>` staging/evidence tabs,
- older CMS price-list versions,
- temporary review tabs,
- reconciliation/computation sheets,
- future assistant-only support tabs.

Do not rely on remembered sheet indexes. Discover the live tabs first, then reorder by sheet identity/title.

## Latest CMS price list

The current/latest CMS price-list sheet is user-facing because it is operationally useful for price checking and reconciliation.

When a newer CMS price list is imported and verified:

- move the new latest price-list tab into the front user-facing position,
- move older price-list tabs behind `Audit_Log` with the assistant/support group,
- do not delete an older price list merely because a new one exists unless the user explicitly authorizes cleanup or archival deletion.

## Audit Log persistence

`Audit_Log` is a durable workbook record and should normally remain permanent.

It is the compact historical index for significant operations such as:

- batch reconciliation,
- price synchronization,
- identity/code corrections,
- marker cleanup decisions,
- new expiry-lot insertion,
- fixed-asset intake,
- mapping-registry creation or material mapping-state changes,
- archival or deletion of staging tabs.

Do not remove `Audit_Log` as routine workbook cleanup.

## Item_Mapping lifecycle

`Item_Mapping` is a **durable assistant/support registry**, not a temporary review queue.

Its purpose is to preserve dated local-to-CMS mapping evidence, match basis, prior codes, explicit exclusions, and later revalidation state so the agent does not restart every catalogue reconciliation from scratch.

- Keep it behind the user-facing group and `Audit_Log`.
- Prefer static/agent-managed values over a large web of live formulas unless a specific formula is intentionally approved.
- Treat `CONFIRMED` mappings as dated evidence that must be revalidated against later catalogues; never convert the tab into a blind `Local Item -> CMS Code` authority.
- Preserve explicit `EXCLUDED` rows so known catalogue omissions/non-sale stock do not repeatedly return as false-positive review items.
- Update `Last Confirmed`, catalogue version, match basis, previous-code/retired state, and notes when material evidence changes.
- Do not delete `Item_Mapping` as normal review cleanup. Rebuilding or replacing the registry is a material lifecycle decision and requires verified preservation of useful history/evidence.

## Temporary review-tab lifecycle

Dedicated review tabs are temporary work queues containing only attention-needed rows.

Examples include CMS mapping review, received-stock review, expiry mismatch review, or another bounded reconciliation queue.

Keep a review tab while review/correction is ongoing. Once every actionable row is resolved or intentionally excluded and final state has been read back, the tab may be removed from the live workbook. If deletion is blocked by the runtime/platform, leaving the completed tab in place is acceptable; report that cleanup remains manual.

Do not confuse a temporary review tab with durable `Item_Mapping` memory or `Audit_Log` history.

## CMS batch-sheet lifecycle

`CMS_Batch_<TRANSFER>_<DATE>` tabs are **staging and reconciliation evidence**, not primary day-to-day operational tabs.

They do not need to remain permanent forever by default.

### While active

Keep a batch tab while:

- intake/reconciliation is still in progress,
- unresolved REVIEW/CONFLICT items depend on it,
- the source is being checked against Main Stock,
- recent verification or rollback comparison may reasonably need the preserved staging view.

Place these tabs after the user-facing group.

### After completion

Once a batch has been fully processed, read-back verified, and durably represented by the authoritative source plus `Audit_Log` and live inventory state, the batch tab becomes archival support rather than operational state.

At that point it may be:

- kept temporarily for convenience,
- moved to the back of the workbook,
- archived outside the operational workbook when an archive destination exists,
- or deleted from the live workbook **only with explicit user authorization**.

Never silently delete batch tabs as automatic housekeeping.

Before deleting a batch tab, confirm that doing so will not destroy the only available evidence for an unresolved mapping, exact source precision, or historical reconciliation decision.

If a batch tab is removed or externally archived, record the action in `Audit_Log` when material.

## Original source versus staging tab

The actual CMS transfer paper/photo/file remains higher authority than a batch staging tab.

A batch tab is a working preservation/reconciliation artifact. It must not become the only justification for rewriting source truth.

When practical, preserve the original source separately from the operational workbook. `Audit_Log` should identify the transfer and important decisions so the workbook does not depend on permanent accumulation of hundreds of batch tabs.

## Helper/computation tabs

Assistant-only helper, mapping, computation, or reconciliation tabs belong after the user-facing and audit tabs.

Do not move a helper tab forward merely because the assistant uses it frequently. Human operational clarity takes priority.

If a helper sheet becomes genuinely user-facing later, explicitly update this policy and its placement rather than allowing ad hoc tab-order drift.

## Reordering safety

When reordering tabs:

1. Inspect current live sheet titles and IDs.
2. Reorder tabs only; do not rename them unless separately authorized.
3. Do not modify cell values, formulas, formats, ranges, or production columns as part of tab sequencing.
4. Read spreadsheet metadata back after the reorder and verify the intended sequence.
5. Treat tab order as presentation/organization, not as data mutation; add an Audit_Log entry only when the reorganization is operationally significant or the user requests one.

## Default principle

**Human-facing operational tabs first; durable audit next; durable mapping memory and assistant staging/history/support last.**

This reference is intended to grow as new workbook tab types or retention needs are introduced.
