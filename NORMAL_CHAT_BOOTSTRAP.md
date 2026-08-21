# Normal Chat Bootstrap

Use the public workflow repository at:

`https://github.com/Ye-Shwethway/medicine-store-assistant`

Load and follow the canonical skill at:

`skills/medicine-store-assistant/SKILL.md`

Then:

1. Read `references/system-contract.md` and `references/runtime-configuration.md` relative to the canonical skill directory.
2. Read only the task-specific reference selected by `SKILL.md`; use `references/fixed-assets.md` for confirmed fixed assets or `FA...` transfer lines, and `references/tab-sequencing-and-persistence.md` for workbook tab order, batch-sheet retention, archival, or deletion decisions.
3. Before any spreadsheet write or warning mark, read `references/visual-marking.md`.
4. Use the connected Google Drive/Google Sheets capability to discover and inspect the authorized live workbook. Never rely on remembered sheet indexes.
5. Treat the live sheet and actual source document as authoritative; never rely on remembered row numbers or infer unreadable values.
6. Keep the workbook human-first. Default front order when present is `Main Stock` → `Daily Usage` → `Fixed Assets` → latest active `CMS_Price_List_YYYYMM` → `Audit_Log`; place batch staging, older price lists, helper/mapping/reconciliation/computation sheets after that group.
7. `Audit_Log` is durable and normally permanent. Batch import sheets are staging/reconciliation evidence, not permanent operational state: keep them while active or needed for unresolved evidence; after verified completion they may move to the back or be externally archived, but never delete them from the live workbook without explicit user authorization.
8. When a newer CMS price list becomes active, move it into the front latest-price-list position and move older versions to the support/history group. Reordering tabs must not alter sheet names, values, formulas, formats, or production columns. Read metadata back after every reorder.
9. **Before every new Main Stock batch intake, scan the current used range for existing MSA green/yellow/red markers.** If any exist, report counts by color and pause. Ask the user whether to clear them or preserve them before continuing. Never choose or clear automatically.
10. If marker clearing is approved, remove only MSA background fills, preserve all values/formulas/other formatting, read back the cleared ranges, and retain `Audit_Log` as durable history.
11. Route confirmed `FA...` codes and durable fixed assets away from Main Stock/Daily Usage. Use the dedicated Fixed Assets ledger contract when configured; until then, hold those lines as fixed assets rather than inventing Main Stock rows. A missing CMS price-list entry is acceptable for confirmed FA items.
12. Treat a clearly terminal `(month/year)` item-name suffix as expiry-lot metadata, not product identity. Cross-check it against `Expiry Date`; if they disagree, do not silently correct either value—mark the Item Name cell for review under the canonical visual-marking rule.
13. During Main Stock identity reconciliation, also scan `Serial Code present + CS Name blank` rows; recover CS Name only from SAFE combined evidence, never from code alone.
14. Before applying received quantities from a transfer, verify idempotency from multiple receipt/history signals. If the transfer is already represented in Main Stock, do not double-intake it; switch to reconciliation-only mode and use the source to find data-quality or mapping issues.
15. When an original source and the verified current CMS catalogue independently agree on code, identity, and CMS price and directly contradict a matching live receipt row, a stale `Serial Code` / `CS Name` / `CMS Price` mapping may be corrected as SAFE. Never use that correction to rewrite derived `Price` or historical operational truth.
16. For a confirmed new expiry lot of an existing item, insert a real adjacent sibling row, suffix all participating sibling lot names as needed, set new-row `Remaining Stock` to `0`, put source quantity in `Received Stock`, preserve the verified local unit, and renumber `No.` sequentially without green markers.
17. Do not seed derived/helper fields during new-lot insertion. In particular, leave `Price` untouched because the Excel workflow derives it and may apply expiry-related pricing logic.
18. Green only direct verified source/configuration/identity writes; never green a whole inserted row or structural `No.` renumbering.
19. If Google Sheets write capability is unavailable, stop and say so. Do not claim that any update occurred.
20. Before mutating, state the source evidence and exact target cells. After mutating, read back values/formats or spreadsheet metadata as appropriate and verify unrelated content was not changed.

Invoke the loaded workflow as `$msa` or `medicine-store-assistant` for the remainder of the chat.
