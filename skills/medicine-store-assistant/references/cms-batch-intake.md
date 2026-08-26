# CMS Batch / Supply Intake

Use this workflow for a CMS issue paper, transfer sheet, supply paper, image, or equivalent source.

For the actual received-stock mutation path after source extraction/classification, also read [received-stock-operational-workflow.md](received-stock-operational-workflow.md). That reference is canonical for existing-lot versus new-lot/new-item routing, cumulative current-month receipt semantics, `Main Stock` / `Daily Usage` paired integrity, `This Month Received` derived-summary behavior, and receipt verification.

## Mandatory marker preflight

Before mutating `Main Stock` for any new batch intake:

1. Inspect the current used range for existing MSA background markers.
2. Count light green `#D9EAD3`, light yellow `#FFF2CC`, and light red `#F4CCCC` markers.
3. If no existing MSA markers are present, continue.
4. If any are present, report the counts by color and **pause before intake writes**. Ask the user whether to clear the old MSA markers or preserve them and continue.
5. Do not choose automatically. If clear is approved, remove only background fills confidently attributable to MSA, preserve all values/formulas/other formatting, and read back the cleared ranges before proceeding.
6. Marker cleanup is visual-session hygiene only. `Audit_Log` remains the historical operation trail and must not be cleared or rewritten merely because markers were removed.

This preflight prevents markers from previous work from being visually mixed with the incoming batch.

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

Preserve exact numbers and source precision. Separate blank, zero, overwritten, and unreadable values. Do not infer a missing value merely because a similar line suggests one. Do not round a source price merely to match an existing sheet display format.

## Route fixed assets before Main Stock matching

Before treating every transfer line as medicine/consumable stock, detect confirmed fixed assets.

- `FA...` codes and clearly durable fixed-asset instruments belong to the dedicated Fixed Assets ledger, not `Main Stock` or `Daily Usage`.
- Do not treat absence from the medicine/consumable CMS price catalogue as an identity failure for a confirmed fixed asset.
- Follow [fixed-assets.md](fixed-assets.md).
- If the dedicated asset ledger or its schema is not yet available, hold those lines as `FIXED ASSET — HOLD FOR ASSET LEDGER` and continue processing safe consumable lines from the same transfer.

## Reconcile before writing

1. Inspect the current `Main Stock` layout, relevant rows, formulas, materialized calculated values, and existing lot pattern.
2. Compare every non-fixed-asset source line against local name, code, descriptions, strength/form/size, unit, confirmed mappings, and earlier CMS batches.
3. Classify it as SAFE, REVIEW, CONFLICT, NEW / UNMAPPED, or route it to the fixed-assets workflow using the main skill rules.
4. Determine whether it maps to:
   - an existing stock lot,
   - a new expiry lot of an existing local item,
   - a new local item,
   - a mapping that needs confirmation,
   - or a fixed asset outside Main Stock.
5. Do not overwrite or merge an older expiry lot when the source has a different expiry date, even when CMS code and item identity are the same.
6. Check idempotency before applying quantities. An existing preserved batch sheet is evidence but not by itself proof that Main Stock was updated; use multiple live receipt/history signals such as code, normalized identity, expiry, received quantity, source price, batch history, or backups. Never double-intake an already processed transfer.
7. If the transfer is already represented, switch to **reconciliation-only mode**. Do not mutate received quantities merely because the original paper has been supplied again. Use the source to identify missing dependent identity fields, stale mappings, unit gaps, expiry-lot inconsistencies, source-transcription errors, or other data-quality problems.
8. Write only when the classification and requested operation permit it.

## Historical-source correction

A historical paper source can establish a SAFE correction without re-intaking the transfer.

- When the original source and the verified current CMS catalogue independently agree on the same code, product identity, and catalogue price, and the live row contains a contradictory CMS mapping, correct only the stale current mapping fields supported by that evidence.
- Typical correctable fields are `Serial Code`, `CS Name`, and `CMS Price`.
- Do not use this as permission to rewrite historical usage or derived values. In particular, keep the derived `Price` column untouched unless its own workbook contract explicitly allows a write.
- A matching quantity/expiry receipt in Main Stock strengthens the conclusion that the paper line is the historical source for that row.
- If source and catalogue do not independently agree, retain REVIEW/CONFLICT handling instead of forcing a correction.

## New expiry-lot insertion

When a source confirms a new expiry lot for an existing local item:

1. Locate the full same-name sibling family using expiry-suffix-normalized identity.
2. Insert a real row adjacent to that family; do not append the lot elsewhere or overwrite another expiry lot.
3. If the family contains multiple expiry lots, add a terminal `(month/year)` suffix to participating sibling item names that lack one, using each row's own `Expiry Date`.
4. For the new row, set `Remaining Stock` to **0** and put the source quantity in `Received Stock`.
5. Preserve the verified local unit convention. For gloves, use `Pair` when that is the established Main Stock unit even if the source report uses a different presentation label.
6. Populate verified source/identity/configuration fields only. Under the current Main Stock contract these may include `No.`, `Items`, `Expiry Date`, `Unit`, `Remaining Stock`, `Received Stock`, `Reorder Level`, `Reorder Surplus Factor`, `CMS Price`, optional `Remark`, `Serial Code`, and `CS Name`.
7. Do **not** seed `Date Status`, `Stock Status Today`, `This Month Usage`, `Stock Remark`, `Estimated Request Qty`, `Shortage Date`, `Price`, `Reorder Row`, or `Expiry Filter Helper`; treat them as derived/calculated/helper fields unless the live contract proves otherwise. `Price` is specifically derived by the Excel workflow and may reflect expiry-related discount logic.
8. Renumber the `No.` column sequentially from the insertion point through the used range. Do not treat this structural renumbering as user-facing operational data entry.
9. Read back the new row, affected siblings, derived/helper blanks, and the renumbered tail before declaring success.

## Optional source preservation

When the workbook's established pattern supports it, preserve the imported batch in a versioned sheet such as `CMS_Batch_<TRANSFER>_<DATE>`. Do not create or rename production sheets merely from this naming example without checking the live system.

When a preserved batch is compared with the original source, correct proven transcription or precision errors in the preserved batch only when the source is clearly authoritative, and verify the exact cells after writing.

## Verify and report

Read back all affected rows. Confirm quantities, source precision, expiry values, identities, untouched derived/helper fields, unrelated neighboring cells, and visual marks. Report marker-preflight decision, matched lines, new lots/items, fixed assets routed/held, conflicts, unreadable fields, warnings, idempotency decisions, reconciliation-only corrections, and verification status.
