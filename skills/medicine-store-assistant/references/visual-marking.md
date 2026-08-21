# Visual Marking Protocol

Use direct cell formatting as lightweight operational metadata. Color must complement, never replace, the written report and `Audit_Log` evidence.

## Palette

- **Light green `#D9EAD3` — written and verified:** Apply to each operational data cell whose value the assistant intentionally writes as part of a successful operation.
- **Light yellow `#FFF2CC` — review required:** Apply to the most relevant target cell when a likely match, unmapped item, unclear source field, expiry-suffix inconsistency, or other pending decision requires user review and the identity-sensitive value is not written.
- **Light red `#F4CCCC` — warning or conflict:** Apply to the disputed target cell when a confirmed mismatch, recycled CMS identity, invalid contradiction, or other blocked high-risk condition needs attention.

When meanings compete on the same cell, use `red > yellow > green`. Never mark a disputed or unverified value green.

## Write behavior

1. Inspect the target values, direct formatting, formulas, and relevant conditional-format rules before mutation.
2. Format only the exact cells affected; never color a whole row merely because one field changed, a new row was inserted, or one field needs review.
3. Avoid redundant writes. If the intended value already equals the live value, do not rewrite or newly mark it green.
4. When supported, include the value write and its green fill in the same batch operation, then read back both the value and format. Do not claim success until verification passes.
5. Mark only direct operational mutations green. Do not mark cells that were merely read, compared, changed indirectly by a formula, or rewritten solely for structural maintenance.
6. **Structural maintenance is not green:** downstream `No.` renumbering after a row insertion must not receive green markers even though the assistant rewrites those cells.
7. For a newly inserted row, green only the verified source/configuration/identity cells that the assistant intentionally seeds. Leave derived/calculated/helper cells unmarked.
8. Apply only `userEnteredFormat.backgroundColorStyle` with the exact RGB color. Preserve values, formulas, number formats, borders, alignment, validation, notes, and all unrelated formatting.
9. Do not silently replace a meaningful existing fill or a conflicting conditional-format signal. Preserve it and report the conflict unless the underlying MSA warning is being explicitly resolved by verified evidence.
10. When an MSA-created warning/conflict is definitively resolved and the same cell is intentionally corrected, the old warning color may be replaced by the appropriate verified state, including green for a direct corrected write.
11. If a warning concerns one field, mark that field. If no single field represents the issue, mark the item-name cell rather than the whole row.
12. **Expiry suffix mismatch:** when a terminal expiry marker in `Items` disagrees with the row's `Expiry Date`, leave both values unchanged and mark the **Item Name / Items cell** light yellow for later review. Use red only when stronger source evidence establishes that one of the values is definitively wrong or the mismatch creates a confirmed high-risk conflict. Do not mark the `Expiry Date` cell merely to force visual agreement.

## New-lot row example

For a newly inserted expiry lot, fields such as `Items`, `Expiry Date`, `Unit`, `Remaining Stock`, `Received Stock`, verified configuration values, `CMS Price`, `Serial Code`, and `CS Name` may be green when actually written and verified. Do not green the `No.` column solely because it was assigned/renumbered, and do not green derived/helper fields such as `Date Status`, `Stock Status Today`, `This Month Usage`, `Stock Remark`, `Estimated Request Qty`, `Shortage Date`, `Price`, `Reorder Row`, or `Expiry Filter Helper`.

## Persistence and clearing

- Keep MSA marks persistent by default so the user can review them later.
- Never automatically clear prior MSA marks when starting a new task.
- Clear marks only on explicit request, after inspecting the requested ranges. Remove only colors known to have been applied by MSA; do not reset unrelated or pre-existing formatting.
- Do not create one `Audit_Log` row per color-only action. Continue to audit the underlying significant inventory operation according to the main skill rules.

## Reporting

Always state the meaning and count of applied colors in the completion report. Describe warnings and review items in text as well, so color is never the only signal.
