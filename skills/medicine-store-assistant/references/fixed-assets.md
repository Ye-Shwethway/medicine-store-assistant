# Fixed Assets Intake

Use this workflow for fixed assets and durable instruments that must be recorded as received property but must not participate in consumable stock or Daily Usage logic.

## Category boundary

- Treat `FA...` asset codes and clearly identified durable fixed-asset instruments as a separate inventory domain.
- Do **not** insert fixed assets into `Main Stock` or `Daily Usage` merely because they appear on the same CMS transfer paper as medicines or consumables.
- Fixed assets are not governed by consumable depletion, expiry-driven pricing, reorder, FIFO/FEFO, or Daily Usage calculations unless a future explicit asset contract says otherwise.
- The CMS medicine/consumable price catalogue may legitimately contain no matching `FA...` entry. Catalogue absence alone is not an error for a confirmed fixed asset.

## Dedicated ledger

Record fixed assets only in the configured dedicated Fixed Assets spreadsheet/ledger. Its schema must be inspected and approved before the first production write.

Until that ledger exists or its schema is confirmed:

1. Preserve the source transfer evidence.
2. Classify the line as `FIXED ASSET — HOLD FOR ASSET LEDGER` rather than `NEW / UNMAPPED` medicine stock.
3. Do not create a substitute row in Main Stock.
4. Report the held asset count and transfer references to the user.

A future Fixed Assets ledger should preserve at least the source-supported asset code, description, received quantity, unit, source/sale price when present, transfer number, received/transfer date, and any approved location/status fields. Do not invent asset-management fields or lifecycle rules before the live ledger contract is defined.

## Mixed transfers

A single transfer may contain both consumables and fixed assets. Split processing by domain:

- consumable/medicine lines -> normal Main Stock intake/reconciliation rules;
- fixed-asset lines -> dedicated Fixed Assets ledger rules.

Never delay safe consumable processing merely because asset lines are waiting for the separate ledger, but clearly report the held asset subset.

## Verification

After any Fixed Assets write, read back the exact asset rows and verify that no Main Stock or Daily Usage row was created or modified for those assets. Significant asset intake should be traceable through the appropriate audit mechanism once the asset-ledger contract is finalized.
