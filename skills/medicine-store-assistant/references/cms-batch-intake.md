# CMS Batch / Supply Intake

Use this workflow for a CMS issue paper, transfer sheet, supply paper, image, or equivalent source.

## Extract

Capture only what the source supports:

- CMS Code
- CMS brand or description
- quantity received
- unit
- sale/CMS price
- expiry date
- transfer number
- supply date
- other relevant identifiers

Preserve exact numbers. Separate blank, zero, overwritten, and unreadable values. Do not infer a missing value merely because a similar line suggests one.

## Reconcile before writing

1. Inspect the current `Main Stock` layout, relevant rows, formulas, and existing lot pattern.
2. Compare every source line against local name, code, descriptions, strength/form/size, unit, confirmed mappings, and earlier CMS batches.
3. Classify it as SAFE, REVIEW, CONFLICT, or NEW / UNMAPPED using the main skill rules.
4. Determine whether it maps to:
   - an existing stock lot,
   - a new expiry lot of an existing local item,
   - a new local item,
   - or a mapping that needs confirmation.
5. Do not overwrite an older expiry lot when the new supply has a different expiry date.
6. Write only when the classification and requested operation permit it.

## Optional source preservation

When the workbook's established pattern supports it, preserve the imported batch in a versioned sheet such as `CMS_Batch_<TRANSFER>_<DATE>`. Do not create or rename production sheets merely from this naming example without checking the live system.

## Verify and report

Read back all affected rows. Confirm quantities, prices, expiry values, identities, formulas, unrelated neighboring cells, and visual marks. Report matched lines, new lots/items, conflicts, unreadable fields, warnings, and verification status.
