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

Treat these names as discovery hints, not proof of the current live structure. Inspect the spreadsheet before every operational task.

## Mandatory restore checkpoint and audit invariant

Every **operational mutation** of the live workbook must have a verified restore path before the mutation begins.

1. After resolving and inspecting the authorized live workbook, create a **full-workbook pre-mutation checkpoint copy** before changing operational data, formulas, row structure, production-sheet structure, item identity, expiry, quantity, price/mapping fields, or synchronization logic.
2. The checkpoint must be created **before** the first operational mutation in that operation. A copy made after the write is evidence of the resulting state, not a valid pre-mutation restore checkpoint.
3. Give the checkpoint a human-readable name containing the workbook identity, date/time or operation context, and `CHECKPOINT` so it is distinguishable from the live workbook.
4. Preserve the checkpoint's Drive file ID or stable URL and link it to the corresponding `Audit_Log` entry through `Backup Snapshot ID` or the live equivalent field.
5. After the mutation, read the affected cells/rows/structure back and verify the intended state before reporting success.
6. Record every operational mutation in `Audit_Log`. A single logically grouped operation may use one audit row when it clearly summarizes the affected scope, previous state, updated state, and checkpoint ID; do not create one audit row per formatting mark or per cell unless the operation requires that granularity.
7. If the mutation fails or read-back verification fails, stop further mutation, preserve the checkpoint, report the failure, and use the checkpoint as the restore source when rollback is authorized or required.
8. Do not overwrite, delete, or repurpose a checkpoint automatically. Checkpoint retention/cleanup is a separate lifecycle decision and must not destroy the only known restore source for an operation.

**Operational mutation** includes, at minimum: inventory values, usage values, item names/identity, expiry values, quantities, CMS mappings/codes/prices, formulas that drive operational state, row insertion/deletion/reordering, production-column changes, production-tab structural changes, and synchronization writes between operational sheets.

**Exception:** purely cosmetic or review-only maintenance that does not change operational values, formulas, row/tab structure, or business logic—such as clearing or applying an approved visual marker, resizing, or formatting-only cleanup—does not require a full-workbook checkpoint. Such actions still follow the visual-marking and read-back rules when applicable.

This checkpoint rule is a hard safety invariant. Do not perform an operational mutation when a pre-mutation checkpoint cannot be created and verified.

## External compatibility boundary

`Main Stock` and `Daily Usage` synchronize with an existing local Excel workbook and macro system. Preserve their established production range as an external compatibility contract:

- Do not rename or reorder existing columns.
- Do not delete production columns.
- Do not casually add columns inside the established range.
- Do not rewrite formulas or calculated fields without explicit authorization.
- Do not restructure sheets to simplify assistant operations.
- Do not disturb archives, reports, reorder calculations, or synchronization.

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

## Optional assistant metadata

If assistant-specific metadata is needed and the user authorizes it, prefer an `Item_Mapping` helper sheet with fields such as:

- Local Item Name
- CMS Code
- CMS Brand Name
- CMS Long Description
- Form / Strength / Size
- Mapping Status
- First Seen
- Last Confirmed
- Active / Retired / Recycled
- Notes

Treat mappings as dated evidence, not immutable truth. A later catalogue can invalidate an older mapping.

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
- a connector, repository, or skill grants access that the runtime does not have.
