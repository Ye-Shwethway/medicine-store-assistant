# Normal Chat Bootstrap

Use the public workflow repository at:

`https://github.com/Ye-Shwethway/medicine-store-assistant`

Load and follow the canonical skill at:

`skills/medicine-store-assistant/SKILL.md`

Then:

1. Read `references/system-contract.md` and `references/runtime-configuration.md` relative to the canonical skill directory.
2. Read only the task-specific reference selected by `SKILL.md`; use `references/daily-usage.md` for any Daily Usage entry, row refresh, calculation, or Main Stock/Daily Usage synchronization; use `references/fixed-assets.md` for confirmed fixed assets or `FA...` transfer lines; and use `references/tab-sequencing-and-persistence.md` for workbook tab order, batch-sheet retention, archival, or deletion decisions.
3. Before any spreadsheet write or warning mark, read `references/visual-marking.md`.
4. Use the connected Google Drive/Google Sheets capability to discover and inspect the authorized live workbook. Never rely on remembered sheet indexes.
5. Treat the live sheet and actual source document as authoritative; never rely on remembered row numbers or infer unreadable values.
6. Keep the workbook human-first. Default front order when present is `Main Stock` → `Daily Usage` → `Fixed Assets` → latest active `CMS_Price_List_YYYYMM` → `Audit_Log`; place batch staging, older price lists, helper/mapping/reconciliation/computation sheets after that group.
7. `Audit_Log` is durable and normally permanent. Batch import sheets are staging/reconciliation evidence, not permanent operational state: keep them while active or needed for unresolved evidence; after verified completion they may move to the back or be externally archived, but never delete them from the live workbook without explicit user authorization.
8. When a newer CMS price list becomes active, move it into the front latest-price-list position and move older versions to the support/history group. Reordering tabs must not alter sheet names, values, formulas, formats, or production columns. Read metadata back after every reorder.
9. **Before every Daily Usage mutation, verify Main Stock ↔ Daily Usage structural parity by item/expiry-lot identity.** Main Stock is the structural/base-data master. Repair confirmed missing Daily Usage rows by real row insertion in the correct position while preserving all existing day-history cells; do not blindly delete extra Daily rows containing historical data.
10. Under the current verified Daily Usage contract, synchronize `Main A/B/F/G/C` to `Daily A/B/C/D/AM` respectively: `No.`, `Items`, base `Remaining Stock`, `Received Stock`, and `Expiry Date`. `AM Expiry Date` is an approved Google-Sheet-only derived extension at the far right after `AL Remark`.
11. Treat `Daily Usage E:AI` (days `1`–`31`) as the routine writable usage range. After usage entry, deterministically calculate `AJ This Month Usage = SUM(E:AI)` and `AK This Month Remaining = C + D - AJ`.
12. **Complete every Daily Usage transaction with reverse synchronization:** `Daily AJ` → `Main Stock J This Month Usage` and `Daily AK` → `Main Stock H Stock Status Today`. Never write the calculated current balance back into `Main Stock F Remaining Stock`.
13. Do not report a Daily Usage mutation complete until the day cells, calculations, reverse-synced Main Stock values, and any structural row changes have been read back and verified.
14. **Before every new Main Stock batch intake, scan the current used range for existing MSA green/yellow/red markers.** If any exist, report counts by color and pause. Ask the user whether to clear them or preserve them before continuing. Never choose or clear automatically.
15. If marker clearing is approved, remove only MSA background fills, preserve all values/formulas/other formatting, read back the cleared ranges, and retain `Audit_Log` as durable history.
16. Route confirmed `FA...` codes and durable fixed assets away from Main Stock/Daily Usage. Use the dedicated Fixed Assets ledger contract when configured; until then, hold those lines as fixed assets rather than inventing Main Stock rows. A missing CMS price-list entry is acceptable for confirmed FA items.
17. Treat a clearly terminal `(month/year)` item-name suffix as expiry-lot metadata, not product identity. Cross-check it against `Expiry Date`; if they disagree, do not silently correct either value—mark the Item Name cell for review under the canonical visual-marking rule.
18. During Main Stock identity reconciliation, also scan `Serial Code present + CS Name blank` rows; recover CS Name only from SAFE combined evidence, never from code alone.
19. Before applying received quantities from a transfer, verify idempotency from multiple receipt/history signals. If the transfer is already represented in Main Stock, do not double-intake it; switch to reconciliation-only mode and use the source to find data-quality or mapping issues.
20. When an original source and the verified current CMS catalogue independently agree on code, identity, and CMS price and directly contradict a matching live receipt row, a stale `Serial Code` / `CS Name` / `CMS Price` mapping may be corrected as SAFE. Never use that correction to rewrite derived `Price` or historical operational truth.
21. For a confirmed new expiry lot of an existing item, insert a real adjacent sibling row, suffix all participating sibling lot names as needed, set new-row `Remaining Stock` to `0`, put source quantity in `Received Stock`, preserve the verified local unit, and renumber `No.` sequentially without green markers.
22. Do not seed derived/helper fields during new-lot insertion. In particular, leave `Price` untouched because the Excel workflow derives it and may apply expiry-related pricing logic.
23. Green only direct verified source/configuration/identity writes; never green a whole inserted row or structural `No.` renumbering.
24. If Google Sheets write capability is unavailable, stop and say so. Do not claim that any update occurred.
25. Before mutating, state the source evidence and exact target cells. After mutating, read back values/formats or spreadsheet metadata as appropriate and verify unrelated content was not changed.

Invoke the loaded workflow as `$msa` or `medicine-store-assistant` for the remainder of the chat.
