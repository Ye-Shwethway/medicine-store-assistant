# Workbook Parity Matrix

Status: **F6C working artifact — source inspection required**

This document is intentionally incomplete until each item is verified against the current authorized Google Sheet / Excel source. Do not fill unknown behavior from memory or inference.

| Workbook surface | Source fields / behavior to verify | Canonical-domain target | Status |
| --- | --- | --- | --- |
| Main Stock | exact columns, formulas, editable fields, CMS fields, expiry/lot presentation, received/current/reorder fields, row lifecycle | product + lot + catalogue mapping + derived monthly projection | PENDING SOURCE INSPECTION |
| Daily Usage | A:D sync, Day 1–31 edits, totals, remaining, remark, expiry, rollover | normalized usage transactions + monthly projection | PENDING SOURCE INSPECTION |
| This Month Received | exact columns and inclusion/filter rule | receipt/lot current-month projection | PENDING SOURCE INSPECTION |
| Reorder | exact source inputs, formula, thresholds, rounding | deterministic reorder recommendation + working projection | PENDING SOURCE INSPECTION |
| Final Reorder | copy/edit/approval/submission/archive behavior | approved final reorder business record | PENDING SOURCE INSPECTION |
| CMS price/catalogue | columns, retention/version behavior, serial/code/name/price semantics | versioned CMS catalogue identity + mappings | PENDING SOURCE INSPECTION |
| Transfer/batch intake | source document fields, line identity, expiry, quantities, price, mapping flow | receipt batch + receipt lines + lot mapping | PENDING SOURCE INSPECTION |
| Monthly close / Master | opening carry-forward, archive/copy/reset sequence, formula/macro effects | immutable month snapshot + next-month opening projection | PENDING SOURCE INSPECTION |

## Rules

- Current source evidence wins over assumptions.
- CMS code alone never proves product identity.
- Spreadsheet row number/order is not canonical identity.
- Formula/display sheets are projections unless they contain independent business data.
- Any unresolved behavior stays `PENDING SOURCE INSPECTION` or `OWNER REVIEW`; do not invent parity.
