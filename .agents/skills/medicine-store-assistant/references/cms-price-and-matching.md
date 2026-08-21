# CMS Price Lists and Identity Reconciliation

Use this workflow for a new CMS Excel price list, catalogue reconciliation, Main Stock mapping review, or recycled-code audit.

## Import the catalogue

Typical columns may include Code, Brand Name, Description, Form, Type, Class, and Selling Price.

Preserve the uploaded catalogue content as closely as practical. When authorized, import it into a clearly versioned helper sheet such as `CMS_Price_List_YYYYMM`, after checking the workbook's existing naming convention and avoiding collisions.

## Establish identity compatibility

Never apply `CMS Code match -> automatic price update` as the sole rule. Compare code with descriptive evidence, including local name, brand/short description, long description, strength, formulation, size/type, unit, and prior mapping history.

Block or review automatic propagation when evidence includes:

- the same code with an unrelated product description,
- changed strength or formulation,
- changed device size, gauge, or type,
- an implausible price change paired with description mismatch,
- a code retired and later reused for another item.

Treat these as potential recycled CMS identities. Preserve the mapping history rather than silently replacing it.

## Apply prices safely

When identity is compatible, update only the appropriate current CMS price field allowed by the live sheet contract. Do not overwrite receipt-time prices or other genuine historical transaction truth because the current catalogue changed.

Preserve the local operational item name. Model the relationship as `Local Name <-> CMS catalogue identity/history`, allowing CMS brand or code to change over time.

## Audit

For each reconciled item, retain enough evidence to explain SAFE, REVIEW, CONFLICT, or NEW / UNMAPPED classification. Use `Audit_Log` for significant price synchronization, recycled-code findings, multi-row propagation, or confirmed mapping changes.

Read back affected rows and verify intended prices, identities, formulas, visual marks, and unchanged neighboring cells before reporting success.
