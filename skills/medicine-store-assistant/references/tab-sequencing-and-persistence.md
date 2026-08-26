# Tab Sequencing and Persistence Policy

Use this reference when creating, reordering, hiding, unhiding, archiving, or deciding the retention of workbook tabs in the Medicine Store Cloud spreadsheet.

## Goal

Keep the live workbook easy for a human operator to use while preserving assistant evidence and auditability.

The workbook has three broad tab groups:

1. **Human-facing operational tabs** — frequently opened by staff or the Owner.
2. **Human-facing decision tabs** — concise review surfaces such as `Owner_Decision_Inbox`.
3. **Agent/support tabs** — staging, reconciliation, historical evidence, mapping memory, audit, or computation support.

Human operational clarity takes priority over exposing every analytical sheet. Raw evidence that is useful to the agent does not automatically belong in the visible UI.

Tab order and visibility are usability contracts. Reordering or hiding support tabs is allowed when authorized because it does not change the production column contracts inside the compatibility-locked operational sheets.

## Preferred visible daily-use surface

Keep the visible workbook small. When these tabs exist, prefer this front order:

1. `Main Stock`
2. `Daily Usage`
3. `This Month Received`
4. `Final Reorder`
5. `Owner_Decision_Inbox`
6. `Fixed Assets`

This order keeps the four Excel-compatible operational surfaces together, followed by the concise Owner decision surface and fixed-assets ledger.

Do not force the Owner to keep latest CMS price lists, audit logs, mapping registries, batch evidence, historical reorder analysis, or raw AI reasoning tabs visible merely because the agent uses them.

Do not rely on remembered sheet indexes. Discover the live tabs first, then reorder or hide by sheet identity/title.

## Owner Decision Inbox

`Owner_Decision_Inbox` is the preferred human-facing review surface for adaptive reorder and row-lifecycle decisions.

It should summarize only the context needed for a practical decision, such as:

- priority,
- active/current item label,
- usable stock now,
- clear action wording,
- suggested reorder level,
- order this round,
- concise reason / what the agent needs from the Owner,
- Owner decision/override fields.

Do not turn this tab into another raw analytics sheet. Detailed averages, medians, historical peaks, risk flags, lifecycle counts, and other evidence belong in agent/support tabs unless the Owner explicitly asks to see them.

## Agent/support evidence tabs

Agent/support tabs may be hidden from normal view while remaining available for reasoning, audit, reconciliation, and readback.

Examples include:

- `Audit_Log`,
- `Item_Mapping`,
- `CMS_Price_List_YYYYMM`,
- `CMS_Batch_<TRANSFER>_<DATE>`,
- copied/backup operational tabs,
- expiry mismatch review,
- CMS mapping review,
- early-depletion evidence,
- reorder history evidence,
- reorder risk flags,
- family-level reorder foundations,
- lower-reorder reasoning,
- full AI reorder review,
- row lifecycle review,
- Owner-vs-AI comparison evidence,
- temporary computation/reconciliation sheets.

Hiding a support tab is not deletion. Preserve the data and sheet identity so the agent can continue using it.

If a hidden tab becomes necessary for a specific human inspection, it may be temporarily unhidden or the relevant evidence may be summarized in the human-facing decision surface. Do not require the Owner to browse raw support tabs for routine decisions.

## Latest CMS price list

The latest CMS price list remains operationally important but does not need to be permanently visible if the agent can reliably access it and the Owner does not need it for daily navigation.

When a newer CMS price list is imported and verified:

- preserve it as the current versioned price-list evidence,
- move older price-list versions to support/history state,
- hide support price-list tabs when that reduces clutter and does not break workbook behavior,
- do not delete an older price list merely because a new one exists unless the user explicitly authorizes cleanup or archival deletion.

## Audit Log persistence

`Audit_Log` is a durable workbook record and should normally remain permanent, even when hidden from the normal daily-use surface.

It is the compact historical index for significant operations such as:

- batch reconciliation,
- price synchronization,
- identity/code corrections,
- marker cleanup decisions,
- new expiry-lot insertion,
- fixed-asset intake,
- mapping-registry creation or material mapping-state changes,
- reorder reasoning foundation changes that materially affect future recommendations,
- row-lifecycle/cleanup decisions,
- archival or deletion of staging tabs.

Do not remove `Audit_Log` as routine workbook cleanup.

## Item_Mapping lifecycle

`Item_Mapping` is a **durable agent/support registry**, not a temporary review queue.

Its purpose is to preserve dated local-to-CMS mapping evidence, match basis, prior codes, explicit exclusions, and later revalidation state so the agent does not restart every catalogue reconciliation from scratch.

- Keep it in the support group; it may remain hidden in the normal daily-use UI.
- Prefer static/agent-managed values over a large web of live formulas unless a specific formula is intentionally approved.
- Treat `CONFIRMED` mappings as dated evidence that must be revalidated against later catalogues; never convert the tab into a blind `Local Item -> CMS Code` authority.
- Preserve explicit `EXCLUDED` rows so known catalogue omissions/non-sale stock do not repeatedly return as false-positive review items.
- Update `Last Confirmed`, catalogue version, match basis, previous-code/retired state, and notes when material evidence changes.
- Do not delete `Item_Mapping` as normal review cleanup. Rebuilding or replacing the registry is a material lifecycle decision and requires verified preservation of useful history/evidence.

## Reorder evidence lifecycle

Detailed reorder intelligence is primarily agent working state, not human UI.

Durable or semi-durable evidence may include:

- completed-month usage history,
- historical Owner Final Reorder decisions,
- family-level normalization/evidence,
- risk/pattern classifications,
- lifecycle review state,
- confidence/evidence coverage,
- AI-vs-Owner validation results.

Prefer to keep this evidence hidden/support-only while surfacing concise conclusions in `Owner_Decision_Inbox`.

Do not delete historical evidence merely to declutter the workbook. Hide it, move it behind the user-facing group, or archive it externally when appropriate and authorized.

## Temporary review-tab lifecycle

Dedicated review tabs are work queues containing attention-needed rows.

Examples include CMS mapping review, received-stock review, expiry mismatch review, or another bounded reconciliation queue.

Keep a review tab while review/correction is ongoing. Once every actionable row is resolved or intentionally excluded and final state has been read back, the tab may be hidden, archived, or removed from the live workbook when safe and authorized.

If deletion is blocked by the runtime/platform, leaving the completed tab hidden is acceptable; report that cleanup remains manual if needed.

Do not confuse a temporary review tab with durable `Item_Mapping`, reorder-history evidence, or `Audit_Log` history.

## CMS batch-sheet lifecycle

`CMS_Batch_<TRANSFER>_<DATE>` tabs are **staging and reconciliation evidence**, not primary day-to-day operational tabs.

They do not need to remain permanent forever by default.

### While active

Keep a batch tab while:

- intake/reconciliation is still in progress,
- unresolved REVIEW/CONFLICT items depend on it,
- the source is being checked against Main Stock,
- recent verification or rollback comparison may reasonably need the preserved staging view.

Keep these tabs in the support group and hide them from normal daily navigation when appropriate.

### After completion

Once a batch has been fully processed, read-back verified, and durably represented by the authoritative source plus `Audit_Log` and live inventory state, the batch tab becomes archival support rather than operational state.

At that point it may be:

- kept temporarily for convenience,
- hidden at the back of the workbook,
- archived outside the operational workbook when an archive destination exists,
- or deleted from the live workbook **only with explicit user authorization**.

Never silently delete batch tabs as automatic housekeeping.

Before deleting a batch tab, confirm that doing so will not destroy the only available evidence for an unresolved mapping, exact source precision, or historical reconciliation decision.

If a batch tab is removed or externally archived, record the action in `Audit_Log` when material.

## Original source versus staging tab

The actual CMS transfer paper/photo/file remains higher authority than a batch staging tab.

A batch tab is a working preservation/reconciliation artifact. It must not become the only justification for rewriting source truth.

When practical, preserve the original source separately from the operational workbook. `Audit_Log` should identify the transfer and important decisions so the workbook does not depend on permanent visible accumulation of hundreds of batch tabs.

## Helper/computation tabs

Agent-only helper, mapping, computation, or reconciliation tabs belong in the hidden/support group.

Do not move a helper tab forward merely because the assistant uses it frequently. Human operational clarity takes priority.

If a helper sheet becomes genuinely user-facing later, explicitly update this policy and its placement rather than allowing ad hoc tab-order drift.

## Hiding safety

When hiding tabs:

1. Inspect current live sheet titles and IDs.
2. Confirm the target is a support/evidence tab, not one of the required human-facing operational surfaces.
3. Do not hide all sheets; keep the intended visible operational surface available.
4. Do not modify cell values, formulas, ranges, or production columns as part of visibility cleanup.
5. Read spreadsheet metadata back and verify the intended hidden/visible state.
6. Do not describe hidden data as deleted or archived; hiding is presentation only.

## Reordering safety

When reordering tabs:

1. Inspect current live sheet titles and IDs.
2. Reorder tabs only; do not rename them unless separately authorized.
3. Do not modify cell values, formulas, formats, ranges, or production columns as part of tab sequencing.
4. Read spreadsheet metadata back after the reorder and verify the intended sequence.
5. Treat tab order as presentation/organization, not as inventory mutation; add an `Audit_Log` entry when the reorganization is operationally significant or the user requests one.

## Default principle

**Keep the visible workbook small: operational work + concise Owner decisions in front; raw evidence, audit, mappings, history, staging, and computations preserved behind the scenes.**

This reference is intended to grow as new workbook tab types or retention needs are introduced.