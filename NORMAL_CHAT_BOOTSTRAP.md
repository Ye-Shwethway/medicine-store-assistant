# Normal Chat Bootstrap

Use the public workflow repository at:

`https://github.com/Ye-Shwethway/medicine-store-assistant`

Load and follow the canonical skill at:

`skills/medicine-store-assistant/SKILL.md`

Then:

1. Read `references/system-contract.md` and `references/runtime-configuration.md` relative to the canonical skill directory.
2. Read only the task-specific reference selected by `SKILL.md`; use `references/fixed-assets.md` for confirmed fixed assets or `FA...` transfer lines.
3. Before any spreadsheet write or warning mark, read `references/visual-marking.md`.
4. Use the connected Google Drive/Google Sheets capability to discover and inspect the authorized live workbook.
5. Treat the live sheet and actual source document as authoritative; never rely on remembered row numbers or infer unreadable values.
6. **Before every new Main Stock batch intake, scan the current used range for existing MSA green/yellow/red markers.** If any exist, report counts by color and pause. Ask the user whether to clear them or preserve them before continuing. Never choose or clear automatically.
7. If marker clearing is approved, remove only MSA background fills, preserve all values/formulas/other formatting, read back the cleared ranges, and retain `Audit_Log` as durable history.
8. Route confirmed `FA...` codes and durable fixed assets away from Main Stock/Daily Usage. Use the dedicated Fixed Assets ledger contract when configured; until then, hold those lines as fixed assets rather than inventing Main Stock rows. A missing CMS price-list entry is acceptable for confirmed FA items.
9. Treat a clearly terminal `(month/year)` item-name suffix as expiry-lot metadata, not product identity. Cross-check it against `Expiry Date`; if they disagree, do not silently correct either value—mark the Item Name cell for review under the canonical visual-marking rule.
10. During Main Stock identity reconciliation, also scan `Serial Code present + CS Name blank` rows; recover CS Name only from SAFE combined evidence, never from code alone.
11. Before applying received quantities from a transfer, verify idempotency from multiple receipt/history signals. If the transfer is already represented in Main Stock, do not double-intake it; switch to reconciliation-only mode and use the source to find data-quality or mapping issues.
12. When an original source and the verified current CMS catalogue independently agree on code, identity, and CMS price and directly contradict a matching live receipt row, a stale `Serial Code` / `CS Name` / `CMS Price` mapping may be corrected as SAFE. Never use that correction to rewrite derived `Price` or historical operational truth.
13. For a confirmed new expiry lot of an existing item, insert a real adjacent sibling row, suffix all participating sibling lot names as needed, set new-row `Remaining Stock` to `0`, put source quantity in `Received Stock`, preserve the verified local unit, and renumber `No.` sequentially without green markers.
14. Do not seed derived/helper fields during new-lot insertion. In particular, leave `Price` untouched because the Excel workflow derives it and may apply expiry-related pricing logic.
15. Green only direct verified source/configuration/identity writes; never green a whole inserted row or structural `No.` renumbering.
16. If Google Sheets write capability is unavailable, stop and say so. Do not claim that any update occurred.
17. Before mutating, state the source evidence and exact target cells. After mutating, read back values and formats and verify unrelated cells were not changed.

Invoke the loaded workflow as `$msa` or `medicine-store-assistant` for the remainder of the chat.
