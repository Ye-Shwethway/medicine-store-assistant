# Normal Chat Bootstrap

Use the public workflow repository at:

`https://github.com/Ye-Shwethway/medicine-store-assistant`

Load and follow the canonical skill at:

`skills/medicine-store-assistant/SKILL.md`

Then:

1. Read `references/system-contract.md` and `references/runtime-configuration.md` relative to the canonical skill directory.
2. Read only the task-specific reference selected by `SKILL.md`.
3. Before any spreadsheet write or warning mark, read `references/visual-marking.md`.
4. Use the connected Google Drive/Google Sheets capability to discover and inspect the authorized live workbook.
5. Treat the live sheet and actual source document as authoritative; never rely on remembered row numbers or infer unreadable values.
6. Treat a clearly terminal `(month/year)` item-name suffix as expiry-lot metadata, not product identity. Cross-check it against `Expiry Date`; if they disagree, do not silently correct either value—mark the Item Name cell for review under the canonical visual-marking rule.
7. During Main Stock identity reconciliation, also scan `Serial Code present + CS Name blank` rows; recover CS Name only from SAFE combined evidence, never from code alone.
8. Before applying received quantities from a transfer, verify idempotency from multiple receipt/history signals. If the transfer is already represented in Main Stock, do not double-intake it; switch to reconciliation-only mode and use the source to find data-quality or mapping issues.
9. When an original source and the verified current CMS catalogue independently agree on code, identity, and CMS price and directly contradict a matching live receipt row, a stale `Serial Code` / `CS Name` / `CMS Price` mapping may be corrected as SAFE. Never use that correction to rewrite derived `Price` or historical operational truth.
10. For a confirmed new expiry lot of an existing item, insert a real adjacent sibling row, suffix all participating sibling lot names as needed, set new-row `Remaining Stock` to `0`, put source quantity in `Received Stock`, preserve the verified local unit, and renumber `No.` sequentially without green markers.
11. Do not seed derived/helper fields during new-lot insertion. In particular, leave `Price` untouched because the Excel workflow derives it and may apply expiry-related pricing logic.
12. Green only direct verified source/configuration/identity writes; never green a whole inserted row or structural `No.` renumbering.
13. If Google Sheets write capability is unavailable, stop and say so. Do not claim that any update occurred.
14. Before mutating, state the source evidence and exact target cells. After mutating, read back values and formats and verify unrelated cells were not changed.

Invoke the loaded workflow as `$msa` or `medicine-store-assistant` for the remainder of the chat.
