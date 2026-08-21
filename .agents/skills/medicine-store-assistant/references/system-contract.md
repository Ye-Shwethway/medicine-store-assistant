# System Contract

## Authorized spreadsheet

Resolve the target workbook at runtime. Do not store its live spreadsheet ID in this public repository.

The current operational workbook may be discoverable by its configured title, commonly `Medicine Store Cloud`, but a title is a discovery hint rather than proof. Confirm the exact authorized spreadsheet before every write.

Important sheets may include:

- `Main Stock`
- `Daily Usage`
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
