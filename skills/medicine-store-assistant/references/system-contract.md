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
- a connector, repository, or skill grants access that the runtime does not have.
