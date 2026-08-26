# System Contract

## Authorized spreadsheet

Resolve the target workbook at runtime. Do not store its live spreadsheet ID in this public repository.

The current operational workbook may be discoverable by its configured title, commonly `Medicine Store Cloud`, but a title is a discovery hint rather than proof. Confirm the exact authorized spreadsheet before every write.

Important sheets may include:

- `Main Stock`
- `Daily Usage`
- `This Month Received`
- `Final Reorder`
- `Owner_Decision_Inbox`
- `Fixed Assets`
- `CMS_Price_List_YYYYMM` versioned price-list sheets
- `CMS_Batch_<TRANSFER>_<DATE>` batch or transfer sheets
- `Audit_Log`
- `Item_Mapping`
- hidden reorder/history/lifecycle support sheets

Treat these names as discovery hints, not proof of the current live structure. Inspect the spreadsheet before every operational task.

## Current `$msa` skill versus standalone MSA product

The Git-backed `$msa` skill is the **current direct-use operational agent contract**. It operates the authorized Google workbook through capabilities available in the active ChatGPT/Codex session and follows the rules under `skills/medicine-store-assistant/`.

The repository also contains a separate standalone-system implementation track: VPS backend, Web frontend, PostgreSQL/shadow inventory model, LLM API integration, MCP/internal-agent workflows, and future client integrations. Those implementation layers are sibling project areas; they do not replace, silently extend, or automatically grant authority to the current `$msa` skill.

Until an explicit migration/canonicality decision says otherwise:

- the live authorized Google workbook and source documents remain operationally authoritative for `$msa`;
- PostgreSQL/shadow/runtime data must not be treated as current store truth;
- standalone product capabilities must not be assumed available to the skill merely because their code exists in the repository;
- skill rules and product implementation docs may share business semantics, but their runtime authority, tools, and mutation paths remain distinct.

## Legacy Excel workbook interpretation boundary

The original macro-enabled Excel workbook is a valuable **behavioral specification and historical evidence source**, not an implementation template that must be copied literally.

Preserve business intent where it remains useful, but do not reproduce long formulas, hidden helper mechanics, VBA orchestration, cloud-sync macros, broken named ranges, or workbook-specific UI machinery merely for compatibility. Prefer a simpler explicit rule, agent-assisted review workflow, or future typed backend behavior when it preserves the same or better operational outcome.

The original workbook's archived `Master Data` and historical Final Reorder records may be used as evidence for usage history and prior Owner decisions. Missing monthly archives are missing evidence, not proof that no order was placed.

For the current Google workbook, preserve established production columns and formulas unless the user explicitly authorizes a change. When a legacy rule is intentionally migrated or refined, document the new rule rather than maintaining duplicate old and new logic indefinitely.

## Mandatory restore checkpoint and audit invariant

Every **operational mutation** of the live workbook must have a verified restore path before the mutation begins.

1. After resolving and inspecting the authorized live workbook, create a **full-workbook pre-mutation checkpoint copy** before changing operational data, formulas, row structure, production-sheet structure, item identity, expiry, quantity, price/mapping fields, or synchronization logic.
2. The checkpoint must be created **before** the first operational mutation in that operation. A copy made after the write is evidence of the resulting state, not a valid pre-mutation restore checkpoint.
3. Give the checkpoint a human-readable name containing the workbook identity, date/time or operation context, and `CHECKPOINT` so it is distinguishable from the live workbook.
4. When an authorized dedicated checkpoint folder exists, create or move checkpoint copies there instead of leaving them scattered in Drive root. Moving a checkpoint must preserve its file ID so existing audit references remain valid.
5. Preserve the checkpoint's Drive file ID or stable URL and link it to the corresponding `Audit_Log` entry through `Backup Snapshot ID` or the live equivalent field.
6. After the mutation, read the affected cells/rows/structure back and verify the intended state before reporting success.
7. Record every operational mutation in `Audit_Log`. A single logically grouped operation may use one audit row when it clearly summarizes the affected scope, previous state, updated state, and checkpoint ID; do not create one audit row per formatting mark or per cell unless the operation requires that granularity.
8. If the mutation fails or read-back verification fails, stop further mutation, preserve the checkpoint, report the failure, and use the checkpoint as the restore source when rollback is authorized or required.
9. Do not overwrite, delete, or repurpose a checkpoint automatically. Checkpoint retention/cleanup is a separate lifecycle decision and must not destroy the only known restore source for an operation.

**Operational mutation** includes, at minimum: inventory values, usage values, item names/identity, expiry values, quantities, CMS mappings/codes/prices, formulas that drive operational state, row insertion/deletion/reordering, production-column changes, production-tab structural changes, and synchronization writes between operational sheets.

**Exception:** purely cosmetic or review-only maintenance that does not change operational values, formulas, row/tab structure, or business logic—such as clearing or applying an approved visual marker, resizing, or formatting-only cleanup—does not require a full-workbook checkpoint. Such actions still follow the visual-marking and read-back rules when applicable.

This checkpoint rule is a hard safety invariant. Do not perform an operational mutation when a pre-mutation checkpoint cannot be created and verified.

## Four operational sheet compatibility surfaces

`Main Stock`, `Daily Usage`, `This Month Received`, and `Final Reorder` are compatibility-locked human-facing operational surfaces. Before changing their structure, rebuilding them, or generating a Final Reorder Excel output, read [operational-sheet-compatibility.md](operational-sheet-compatibility.md).

Preserve those four table interfaces even when MSA replaces legacy formulas/macros with simpler rules, agent reasoning, temporary review workflows, or other MSA-native machinery.

The `Final Reorder` table is also a downstream batch-request interoperability contract. Its six-column table format must remain compatible with the original Excel workbook, and its `Remark` column must stay blank unless the user explicitly instructs what to write. Never insert AI rationale, confidence, anomaly notes, or autonomous comments into that Remark field.

## Human-first workbook surface

The workbook may contain many agent/support tabs without exposing them all to the Owner.

Follow [tab-sequencing-and-persistence.md](tab-sequencing-and-persistence.md) for tab order, visibility, persistence, and hiding rules.

The preferred visible daily-use surface is intentionally small and normally centers on:

- `Main Stock`
- `Daily Usage`
- `This Month Received`
- `Final Reorder`
- `Owner_Decision_Inbox` when present
- `Fixed Assets`

Detailed price-list evidence, mapping memory, audit history, batch staging, historical reorder evidence, risk flags, family-level reasoning, and row-lifecycle analysis may remain hidden/support-only when workbook behavior remains intact.

Hiding is presentation only. Do not describe a hidden tab as deleted or archived.

## External compatibility boundary

`Main Stock` and `Daily Usage` synchronize with an existing local Excel workbook and macro system. Preserve their established production range as an external compatibility contract while the current Google-first workflow still depends on it:

- Do not rename or reorder existing columns.
- Do not delete production columns.
- Do not casually add columns inside the established range.
- Do not rewrite formulas or calculated fields without explicit authorization.
- Do not restructure sheets merely to simplify assistant operations.

This compatibility boundary preserves current workbook behavior; it does **not** require the future standalone MSA system to clone Excel formulas or VBA implementation details.

### Approved Daily Usage Google-Sheet extension

The user has explicitly approved one Google-Sheet-side extension to `Daily Usage`: an `Expiry Date` field placed at the far right after the existing `Remark` column.

Under the current live layout this is `AM Expiry Date`, synchronized from the matched `Main Stock` lot's structured `Expiry Date` field. It is a derived/read-only operational aid and is not a routine usage-entry column.

This approval does not authorize insertion of other columns inside the Excel-compatible Daily Usage production range.

## Daily Usage bidirectional synchronization

`Main Stock` is the structural/base-data master for Daily Usage. The canonical Daily Usage flow is defined in `references/daily-usage.md`.

Current approved mapping when the live schema confirms these fields:

- `Main Stock A No.` -> `Daily Usage A No.`
- `Main Stock B Items` -> `Daily Usage B Items`
- `Main Stock F Remaining Stock` -> `Daily Usage C Remaining Stock`
- `Main Stock G Received Stock` -> `Daily Usage D Received Stock`
- `Main Stock C Expiry Date` -> `Daily Usage AM Expiry Date`

Daily usage input belongs in day columns `E:AI` (`1`-`31`). After entry:

- calculate `Daily Usage AJ This Month Usage = SUM(E:AI)`,
- calculate `Daily Usage AK This Month Remaining = C + D - AJ`,
- synchronize `Daily Usage AJ` -> `Main Stock J This Month Usage`,
- synchronize `Daily Usage AK` -> `Main Stock H Stock Status Today`.

Never reverse-sync the calculated current balance into `Main Stock F Remaining Stock`; that field remains the base/opening stock source for Daily Usage.

Before a Daily Usage mutation, verify structural parity by item/lot identity. Repair confirmed missing Daily rows by real row insertion while preserving existing day history. Do not blindly delete extra Daily rows that may contain historical usage.

## Local effective price policy

The legacy workbook establishes a useful price behavior that may be retained or refined explicitly rather than copied as a long formula.

When the live workbook still follows this policy:

- normal stock: local `Price` follows current `CMS Price`;
- stock expiring in the current month (`NE` in the legacy workbook): local `Price = CMS Price × 0.30`;
- expired stock: local `Price = FOC`;
- blank CMS price: local Price remains blank.

Keep **expiry state**, **expiry alert state**, and **pricing state** conceptually separate. The legacy pricing `NE` state means expiry occurs in the current month, while the visual/operational expiry-alert horizon may be broader (for example, under 60 days). Do not conflate a warning horizon with the discount rule.

Do not overwrite `Price` during ordinary mapping, new-lot intake, or CMS reconciliation unless the live formula/derived-price contract is explicitly being migrated or repaired under user authorization.

## Reorder intelligence policy

For reorder analysis, adaptive Reorder Level review, current-cycle request recommendations, row lifecycle, Owner Decision Inbox behavior, historical Owner-order comparison, and Final Reorder preparation, read [reorder-intelligence-and-owner-review.md](reorder-intelligence-and-owner-review.md).

The detailed reference is canonical for these workflows. The following are system-level invariants.

### Reorder Level is adaptive

`Reorder Level` is a maintained operational parameter, not a permanently fixed constant and not something that should be owned by one rigid formula.

A legacy heuristic such as `received quantity - 1` may be historical evidence but is **not** a universal MSA rule.

Use deterministic arithmetic to produce reproducible baselines, then allow authorized AI/human reasoning to interpret seasonality, repeated early depletion, expiry/write-off pressure, volatility, supply reliability, future service demand, and other verified context.

LLM reasoning must not replace arithmetic truth.

### Reorder Level versus Order This Round

Keep these concepts separate:

- **Suggested Reorder Level** = proposed maintained target/threshold going forward.
- **Order This Round** = current-cycle request after considering usable current stock and the approved/suggested target.

A level can be correct while the current-cycle order is zero.

Do not call an action `RAISE` when the suggested level is actually unchanged. Prefer human-readable action wording such as `RAISE LEVEL`, `LOWER LEVEL`, `KEEP LEVEL / ORDER GAP`, or `LEVEL OK / NO ORDER`.

### Usable stock versus expired stock

Expired positive stock is not usable current stock for replenishment-gap calculations.

However, expired-stock disposition and needed replenishment are parallel concerns. Do **not** hard-block a needed order solely because expired stock has not yet been disposed/reconciled.

### Row lifecycle versus reorder need

Row retention and demand are different concerns.

A zero-stock sole representative may be retained as a dormant item so the identity remains available for future ordering. `DORMANT_ITEM_KEEP` / `DORMANT_KEEP` does **not** mean “do not reorder.”

If another same-family active representative exists, a zero-stock obsolete sibling may be a cleanup candidate, but its old row-level reorder state must not define the active family target.

Row deletion remains a separately authorized, checkpointed, audited mutation.

### Family-level reasoning

Use family-level usage/history reasoning conservatively while preserving physical lot separation.

Usage from a lot that depleted this month remains valid demand evidence even if that row becomes a cleanup candidate. Do not duplicate the same family history into several independent lot-level reorder recommendations.

Do not fuzzy-match unresolved historical item families merely to obtain statistics.

### Historical Owner order evidence

Archived Final Reorder decisions are useful evidence of practical human behavior and can reveal new-item introduction, service-stock choices, temporary increases, or other context that usage-only models miss.

Do not assume every month is archived. Missing records are missing evidence, not zero-order decisions.

When comparing an old Owner decision to current AI reasoning, account for snapshot timing; stock and usage may have changed between the order date and the current analysis date.

### New items

Absence of historical usage is not evidence against ordering a new item.

For genuinely new/unmapped items, Owner intent is primary. AI may provide context, comparable evidence, or later learning, but must not suppress the item merely because history is absent.

### Owner-facing decision surface

Do not require the Owner to inspect many raw evidence tabs or wide analytics tables.

Prefer a concise decision surface containing the active/current item label, usable stock now, action wording, suggested reorder level, order this round, a short reason/prompt, and blank Owner override fields.

Detailed averages, medians, peaks, risk flags, lifecycle counts, and reasoning evidence may remain hidden/support-only for agent use.

### Mutation gate

AI classifications and numeric suggestions are review state, not mutation authority.

Do not automatically change Main Stock reorder parameters, delete rows, or populate Final Reorder from the reasoning layer. Material changes require the Owner/user authorization plus the normal checkpoint, readback, and audit workflow.

## Estimated Request Qty policy

`Estimated Request Qty` follows the same pattern as Reorder Level:

1. calculate a deterministic baseline from verified current stock, recent usage, reorder level, safety/surplus factor, and any known pack/order constraint;
2. show the baseline as evidence, not unquestionable truth;
3. permit human/AI reasoning to adjust the proposed order when justified by seasonality, sudden temporary spikes, repeated expiry, repeated early depletion, known future events, supply uncertainty, or other verified operational context;
4. record or explain material adjustments so the final request is auditable.

A legacy spreadsheet formula is useful as a baseline reference but does not define the final request quantity for every item and every month.

Do not equate `Estimated Request Qty` with an approved `Final Reorder Request Qty`.

## Shortage / early-depletion signal

The legacy `Shortage Date` behavior is **not a future forecast**. Its purpose is to notice that an item exhausted before the end of the current month so the operator can respond when planning the next cycle.

Treat this as an actual observed depletion signal, conceptually closer to `Actual Early Depletion Date` or `Stock-Out Date`:

- derive it from verified current-month usage and available stock;
- use it as evidence that the current reorder level/request baseline may be too low;
- do not describe it as a projected future shortage date;
- preserve a separate future forecasting feature for a later design if/when enough historical data exists.

## Optional assistant metadata and mapping memory

`Item_Mapping` is an approved durable assistant/support registry when present. It is mapping memory and evidence, not a blind lookup authority.

Useful fields include:

- Local Item
- CMS Code
- CMS Brand
- CMS Description
- Mapping Status
- First Recorded
- Last Confirmed
- Catalogue Version
- Match Basis
- Previous Code
- Retired / Recycled state
- Notes

Treat mappings as dated evidence, not immutable truth. A later catalogue can invalidate an older mapping. On catalogue refresh, revalidate code **and** clinically/operationally meaningful identity before reuse.

Explicit `EXCLUDED` entries may preserve user decisions that an item should not participate in ordinary CMS matching, such as non-sale/staff-use stock or catalogue-omitted product families. Exclusion prevents repetitive false-positive review; it does not delete the item from Main Stock unless separately authorized.

## Operational truth

Record what physically happened. FIFO/FEFO can generate a warning but cannot redirect or rewrite a historical movement. Preserve lot separation when the workbook tracks different expiry dates separately.

## No-bluff contract

Do not claim that:

- a sheet was updated when it was not,
- an image value was readable when it was not,
- an identity is certain when evidence is ambiguous,
- a CMS code is permanently reliable,
- a write succeeded before read-back verification,
- a restore checkpoint exists when it was not actually created before the mutation,
- an audit record exists when it was not written and read back,
- a hidden tab was deleted or archived when it was only hidden,
- an AI recommendation was applied when it remains review-only,
- a connector, repository, skill, backend, MCP service, or shadow database grants access or authority that the runtime does not have.