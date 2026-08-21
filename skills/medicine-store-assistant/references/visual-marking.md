# Visual Marking Protocol

Use direct cell formatting as lightweight operational metadata. Color must complement, never replace, the written report and `Audit_Log` evidence.

## Palette

- **Light green `#D9EAD3` — written and verified:** Apply to each cell whose value the assistant actually writes as part of a successful operation.
- **Light yellow `#FFF2CC` — review required:** Apply to the most relevant target cell when a likely match, unmapped item, unclear source field, expiry-suffix inconsistency, or other pending decision requires user review and the identity-sensitive value is not written.
- **Light red `#F4CCCC` — warning or conflict:** Apply to the disputed target cell when a confirmed mismatch, recycled CMS identity, invalid contradiction, or other blocked high-risk condition needs attention.

When meanings compete on the same cell, use `red > yellow > green`. Never mark a disputed or unverified value green.

## Write behavior

1. Inspect the target values, direct formatting, formulas, and relevant conditional-format rules before mutation.
2. Format only the exact cells affected; never color a whole row merely because one field changed or needs review.
3. Avoid redundant writes. If the intended value already equals the live value, do not rewrite or newly mark it green.
4. When supported, include the value write and its green fill in the same batch operation, then read back both the value and format. Do not claim success until verification passes.
5. Mark only direct assistant mutations green. Do not mark cells that were merely read, compared, or changed indirectly by a formula.
6. Apply only `userEnteredFormat.backgroundColorStyle` with the exact RGB color. Preserve values, formulas, number formats, borders, alignment, validation, notes, and all unrelated formatting.
7. Do not silently replace a meaningful existing fill or a conflicting conditional-format signal. Preserve it and report the conflict unless the user explicitly authorizes replacement.
8. If a warning concerns one field, mark that field. If no single field represents the issue, mark the item-name cell rather than the whole row.
9. **Expiry suffix mismatch:** when a terminal expiry marker in `Items` disagrees with the row's `Expiry Date`, leave both values unchanged and mark the **Item Name / Items cell** light yellow for later review. Use red only when stronger source evidence establishes that one of the values is definitively wrong or the mismatch creates a confirmed high-risk conflict. Do not mark the `Expiry Date` cell merely to force visual agreement.

## Persistence and clearing

- Keep MSA marks persistent by default so the user can review them later.
- Never automatically clear prior MSA marks when starting a new task.
- Clear marks only on explicit request, after inspecting the requested ranges. Remove only colors known to have been applied by MSA; do not reset unrelated or pre-existing formatting.
- Do not create one `Audit_Log` row per color-only action. Continue to audit the underlying significant inventory operation according to the main skill rules.

## Reporting

Always state the meaning and count of applied colors in the completion report. Describe warnings and review items in text as well, so color is never the only signal.
