# System Contract

## Authorized spreadsheet

Resolve the target workbook at runtime. Do not store its live spreadsheet ID in this public repository.

The current operational workbook may be discoverable by its configured title, commonly `Medicine Store Cloud`, but a title is a discovery hint rather than proof. Confirm the exact authorized spreadsheet before every write.

Important sheets may include:

- `Main Stock`
- `Daily Usage`
- `Fixed Assets`
- `CMS_Price_List_YYYYMM` versioned price-list sheets
- `CMS_Batch_<TRANSFER>_<DATE>` batch or transfer sheets
- `Audit_Log`
- `Item_Mapping`

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

The original macro-enabled Excel workbook is a valuable **behavioral specification and historical design source**, not an implementation template that must be copied literally.

Preserve business intent where it remains useful, but do not reproduce long formulas, hidden helper mechanics, VBA orchestration, cloud-sync macros, broken named ranges, or workbook-specific UI machinery merely for compatibility. Prefer a simpler explicit rule, agent-assisted review workflow, or future typed backend behavior when it preserves the same or better operational outcome.

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

`Reorder Level` is a maintained operational parameter, not a permanently fixed constant and not something that should be owned by one rigid formula.

### New item / new lot

When inserting a genuinely new operational item or lot and a reorder level is required, establish an initial baseline from the best available evidence: comparable sibling item history, recent usage, source quantity, expected operational need, existing store convention, or explicit user guidance. Do not invent a high-confidence reorder level from a single weak signal.

A legacy heuristic such as `received quantity - 1` may be historical evidence but is **not** a universal MSA rule.

### Adaptive review

Reorder Level should be periodically reviewable and may be adjusted upward or downward using human and/or AI reasoning supported by observed evidence, including:

- sustained average and median usage,
- recent trend versus long-run baseline,
- repeated stock-outs or early in-month depletion,
- expiry/write-off or excess remaining stock,
- seasonality,
- short-lived spikes that should not permanently inflate the baseline,
- service changes or known upcoming demand,
- supply reliability and lead time,
- pack-size/order constraints where known.

For example, repeated expiry with low usage can justify lowering the level; repeated early depletion can justify increasing it; a temporary seasonal spike should be recognized without blindly making the spike the permanent new baseline.

### Deterministic baseline + reasoned adjustment

Use deterministic arithmetic to produce a reproducible baseline, then allow an authorized human or AI agent to recommend a reasoned adjustment. Preserve enough evidence to explain both the baseline and the adjustment.

LLM reasoning must not replace arithmetic truth. The agent may interpret context, seasonality, anomalies, and operational trade-offs, while quantities, usage statistics, balances, and formula outputs must come from verified data or deterministic computation.

## Estimated Request Qty policy

`Estimated Request Qty` follows the same pattern as Reorder Level:

1. calculate a deterministic baseline from verified current stock, recent usage, reorder level, safety/surplus factor, and any known pack/order constraint;
2. show the baseline as evidence, not unquestionable truth;
3. permit human/AI reasoning to adjust the proposed order when justified by seasonality, sudden temporary spikes, repeated expiry, repeated early depletion, known future events, supply uncertainty, or other verified operational context;
4. record or explain material adjustments so the final request is auditable.

A legacy spreadsheet formula is useful as a baseline reference but does not define the final request quantity for every item and every month.

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
- a connector, repository, skill, backend, MCP service, or shadow database grants access or authority that the runtime does not have.