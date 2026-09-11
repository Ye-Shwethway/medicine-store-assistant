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
- unit/presentation wording
- sale/CMS price
- expiry date
- transfer number
- supply date
- other relevant identifiers

Preserve exact numbers and source precision. Separate blank, zero, overwritten, and unreadable values. Do not infer a missing value merely because a similar line suggests one. Do not round a source price merely to match an existing sheet display format.

Source wording is evidence, not automatic authority for the local operational `Items` name or local `Unit` vocabulary.

## Route fixed assets before Main Stock matching

Before treating every transfer line as medicine/consumable stock, detect confirmed fixed assets.

- `FA...` codes and clearly durable fixed-asset instruments belong to the dedicated Fixed Assets ledger, not `Main Stock` or `Daily Usage`.
- Do not treat absence from the medicine/consumable CMS price catalogue as an identity failure for a confirmed fixed asset.
- Follow [fixed-assets.md](fixed-assets.md).
- If the dedicated asset ledger or its schema is not yet available, hold those lines as `FIXED ASSET — HOLD FOR ASSET LEDGER` and continue processing safe consumable lines from the same transfer.

## Reconcile before writing

1. Inspect the current `Main Stock` layout, relevant rows, formulas, materialized calculated values, and existing lot pattern.
2. Compare every non-fixed-asset source line against local name, code, descriptions, strength/form/size, unit, confirmed mappings, and earlier CMS batches.
3. Before classifying a source line as a genuinely new local item, perform a **local-family reconciliation gate**:
   - search adjacent/same-family rows in the current live table,
   - compare expiry-suffix-normalized local names,
   - inspect confirmed `Item_Mapping`, current CMS catalogue/price evidence, and verified older local/baseline rows when needed,
   - consider operational synonyms or source functional descriptions that may correspond to an established local family.
4. Preserve the established local operational `Items` family when the source is a new CMS brand/code/description for the same operational item. Keep source/CMS identity in `Serial Code`, `CS Name`, catalogue evidence, and audit history rather than creating a duplicate local family.
5. Classify the line as SAFE, REVIEW, CONFLICT, NEW / UNMAPPED, or route it to the fixed-assets workflow using the main skill rules.
6. Determine whether it maps to:
   - an existing stock lot,
   - a new expiry lot of an existing local item,
   - a new local item,
   - a mapping that needs confirmation,
   - or a fixed asset outside Main Stock.
7. Do not overwrite or merge an older expiry lot when the source has a different expiry date, even when CMS code and item identity are the same.
8. Check idempotency before applying quantities. An existing preserved batch sheet is evidence but not by itself proof that Main Stock was updated; use multiple live receipt/history signals such as code, normalized identity, expiry, received quantity, source price, batch history, or backups. Never double-intake an already processed transfer.
9. If the transfer is already represented, switch to **reconciliation-only mode**. Do not mutate received quantities merely because the original paper has been supplied again. Use the source to identify missing dependent identity fields, stale mappings, unit gaps, expiry-lot inconsistencies, source-transcription errors, or other data-quality problems.
10. Write only when the classification and requested operation permit it.

### Local unit convention gate

`Main Stock.Unit` is a local operational pack/count unit, not a free-text copy of source dosage-form wording.

Before writing a Unit value:

1. Prefer a verified same-family/sibling local unit.
2. If needed, inspect verified older local/baseline rows for the established operational unit.
3. Preserve the local convention when source wording is only a presentation/form label.

Common verified local operational units include values such as `Pcs`, `Pair`, `Tube`, `Amp`, `Vial`, `Bot`, `Tab`, `Cap`, `Pkt`, `Roll`, `Set`, `Sachet`, and `Cup`.

Do not blindly copy source-style values such as `Cream`, `Injection`, `Infusion`, `Oral Suspension`, `Nasal Spray`, `Pieces`, or `OTHER` into `Main Stock.Unit` when the local family has an established operational unit. Do not globally map every injection to `Amp` or `Vial`; use the actual family/packaging evidence because some injectable/infusion products use bottles or other local units.

If the physical pack unit remains ambiguous after sibling/baseline review, hold the Unit for review rather than guessing.

## Historical-source correction

A historical paper source can establish a SAFE correction without re-intaking the transfer.

- When the original source and the verified current CMS catalogue independently agree on the same code, product identity, and catalogue price, and the live row contains a contradictory CMS mapping, correct only the stale current mapping fields supported by that evidence.
- Typical correctable fields are `Serial Code`, `CS Name`, and `CMS Price`.
- Do not use this as permission to rewrite historical usage or derived values. In particular, keep the derived `Price` column untouched unless its own workbook contract explicitly allows a write.
- A matching quantity/expiry receipt in Main Stock strengthens the conclusion that the paper line is the historical source for that row.
- If source and catalogue do not independently agree, retain REVIEW/CONFLICT handling instead of forcing a correction.

## Canonical expiry-suffix rule

For every operational Main Stock row:

- if `Expiry Date` is nonblank, the `Items` name must end with terminal `(M/YYYY)` matching that structured expiry,
- if the suffix is missing, append it,
- if an old terminal expiry suffix disagrees with the verified `Expiry Date`, replace the suffix from the structured expiry,
- if stronger source evidence proves the structured expiry itself is wrong, correct `Expiry Date` first and then synchronize the suffix,
- if `Expiry Date` is blank, do not invent a suffix,
- modify only the terminal expiry marker; preserve all product-defining parentheses, strengths, sizes, brands, country/manufacturer clues, and other operational identity text.

This rule applies globally, not only when an item family has multiple expiry lots.

## New expiry-lot insertion

When a source confirms a new expiry lot for an existing local item:

1. Locate the full same-name sibling family using expiry-suffix-normalized identity and the local-family reconciliation gate above.
2. Insert a real row adjacent to that family; do not append the lot elsewhere or overwrite another expiry lot.
3. Apply the canonical expiry-suffix rule to the new row and any affected sibling rows.
4. For the new row, set `Remaining Stock` to **0** and put the source quantity in `Received Stock`.
5. Initialize `Reorder Level` to the actual intake/received quantity when no stronger verified reorder configuration or explicit Owner instruction already applies to that new row. This is an intake default, not a long-term adaptive reorder conclusion.
6. Preserve the verified local unit convention using the Unit gate above.
7. Populate verified source/identity/configuration fields only. Under the current Main Stock contract these may include `No.`, `Items`, `Expiry Date`, `Unit`, `Remaining Stock`, `Received Stock`, `Reorder Level`, `Reorder Surplus Factor`, `CMS Price`, optional `Remark`, `Serial Code`, and `CS Name`.
8. Do **not** seed `Date Status`, `Stock Status Today`, `This Month Usage`, `Stock Remark`, `Estimated Request Qty`, `Shortage Date`, `Price`, `Reorder Row`, or `Expiry Filter Helper`; treat them as derived/calculated/helper fields unless the live contract proves otherwise. `Price` is specifically derived by the Excel workflow and may reflect expiry-related discount logic.
9. Renumber the `No.` column sequentially from the insertion point through the used range. Do not treat this structural renumbering as user-facing operational data entry.
10. Read back the new row, affected siblings, derived/helper blanks/formulas, and the renumbered tail before declaring success.

## New-item insertion

When a source confirms a genuinely new local item **after the local-family reconciliation gate finds no safe existing operational family**:

- create/align the new Main Stock and Daily Usage row only when identity and user authority permit,
- set `Remaining Stock = 0` and record the actual source quantity in `Received Stock`,
- initialize `Reorder Level = actual intake/received quantity` unless stronger verified configuration evidence or an explicit Owner instruction says otherwise,
- apply the canonical expiry-suffix rule,
- use a verified local operational unit rather than source presentation wording when such a convention can be established,
- treat this as an initial operational default that later reorder intelligence may revise,
- do not invent pack size, usage expectation, CMS mapping, request quantity, or local family identity without evidence.

## Existing-lot receipts

When the source matches an already-established lot:

- add the verified current-month receipt quantity according to the live cumulative receipt contract,
- do not create a duplicate row,
- keep the existing `Reorder Level` unchanged unless a separate reorder decision explicitly changes it,
- preserve the established local item name and unit unless a separate evidence-backed reconciliation corrects them.

## Identity-completeness pass after intake

Before declaring the batch complete, review newly touched rows and relevant siblings for incomplete identity fields.

- `Serial Code present + CS Name blank` is not a finished state when SAFE evidence can recover the dependent name.
- For missing `Serial Code` and/or `CS Name`, use this order when available: **verified adjacent/same-family sibling -> current CMS catalogue/price list -> confirmed Item_Mapping -> verified older local/baseline data or authoritative source document**.
- Do not infer a code from local name alone when evidence remains weak.
- Deliberate `Nil`, `UNMAPPED`, or `EXCLUDED` states are acceptable when evidence is insufficient; guessed mappings are not.
- After the pass, distinguish unresolved rows explicitly from accidental blanks.

Use [cms-price-and-matching.md](cms-price-and-matching.md) for detailed identity-sensitive recovery and conflict handling.

## Optional source preservation

When the workbook's established pattern supports it, preserve the imported batch in a versioned sheet such as `CMS_Batch_<TRANSFER>_<DATE>`. Do not create or rename production sheets merely from this naming example without checking the live system.

When a preserved batch is compared with the original source, correct proven transcription or precision errors in the preserved batch only when the source is clearly authoritative, and verify the exact cells after writing.

## Verify and report

Read back all affected rows. Confirm quantities, source precision, expiry values, global expiry-suffix consistency, local operational names, local Unit conventions, identities, new-row Reorder Level defaults, untouched derived/helper fields, unrelated neighboring cells, and visual marks. Verify Main Stock / Daily Usage alignment, production/staging parity when staging is intentionally maintained as a mirror, `This Month Received` behavior, received totals, and formula integrity after structural changes.

Report marker-preflight decision, matched lines, new lots/items, local-family reconciliations, fixed assets routed/held, conflicts, unreadable fields, warnings, idempotency decisions, reconciliation-only corrections, identity-completeness exceptions, and verification status.