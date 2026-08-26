# CMS Price Lists and Identity Reconciliation

Use this workflow for a new CMS Excel price list, catalogue reconciliation, Main Stock mapping review, or recycled-code audit.

## Import the catalogue

Typical columns may include Code, Brand Name, Description, Form, Type, Class, and Selling Price.

Preserve the uploaded catalogue content as closely as practical. When authorized, import it into a clearly versioned helper sheet such as `CMS_Price_List_YYYYMM`, after checking the workbook's existing naming convention and avoiding collisions.

## Establish identity compatibility

Never apply `CMS Code match -> automatic price update` as the sole rule. Compare code with descriptive evidence, including local name, brand/short description, long description, strength, formulation, size/type, unit, and prior mapping history.

### Local name and CMS name are not required to be text-identical

Treat `Main Stock.Items` as the local operational name and the CMS Brand/Description fields as catalogue identity evidence. A different wording, abbreviation, generic name, local nickname, spelling variant, or inclusion/omission of a brand name is **not by itself a mismatch**.

Do not classify a row as REVIEW or CONFLICT merely because `Items` or the existing `CS Name` is not text-identical to the current CMS Brand Name. If the active ingredient/product family, strength, dosage form, route, size/specification, current code, price, and other available evidence are compatible, the mapping can remain SAFE without rewriting the local name. Examples include local generic wording paired with a branded CMS item, or a local name that already includes the brand in parentheses.

Only treat naming differences as material when they imply a genuinely different drug/product, strength, formulation, route, device type/specification, or other operational identity. Prefer clinically meaningful compatibility over string equality.

### Clinical / pharmaceutical knowledge is part of identity matching

For medicines and clinical supplies, the agent must use relevant domain knowledge when deciding whether two catalogue identities are compatible. A lexical, fuzzy-name, or code-only match is not sufficient when pharmacological or clinical meaning contradicts it.

At minimum, consider when applicable:

- active ingredient / generic drug identity,
- salt or chemical form when clinically meaningful,
- strength and concentration,
- dosage form and route (tablet, injection, cream, eye drop, etc.),
- combination-product ingredients and their strengths,
- device purpose, dimensions, gauge, curve, length, adult/child type, or other clinically meaningful specification.

Examples of hard incompatibility include `ciprofloxacin != tinidazole`, `ceftriaxone != cefoperazone + sulbactam`, and `adrenaline/epinephrine != noradrenaline/norepinephrine`. Do not allow a matching code, similar spelling, same price, or fuzzy text similarity to override such a clinical contradiction.

Use domain knowledge as a safety check, not as permission to invent catalogue facts. If the agent is not sufficiently certain about the pharmacology, formulation, strength, device specification, or exact catalogue candidate, classify the row as REVIEW and do not force a correction. When uncertainty materially affects a mapping decision, prefer authoritative catalogue/source evidence and external verification where appropriate.

Before comparing local names, normalize only harmless variation. A clearly terminal expiry suffix such as `(3/2031)`, `(11/2027)`, or `(8/29)` is lot metadata and should be ignored for product-identity matching. Do not strip product-defining parenthetical text such as brand/manufacturer, country, size/volume, strength, formulation, adult/child type, gauge, or device dimensions.

If a local item name contains an expiry suffix and the row also has an `Expiry Date` value, cross-check them. If they disagree:

- do not silently change either the item name or `Expiry Date`,
- keep identity matching separate from this lot-metadata inconsistency,
- mark the **Item Name cell** yellow for review according to `visual-marking.md`, unless stronger evidence makes the mismatch a confirmed conflict,
- report the mismatch for later user reconciliation.

Treat the dedicated `Expiry Date` column as the structured live expiry field unless a stronger source document proves otherwise.

Block or review automatic propagation when evidence includes:

- the same code with an unrelated product description,
- changed active ingredient, strength, concentration, dosage form, or formulation,
- a different combination drug or clinically different salt/form,
- changed device size, gauge, curve, length, purpose, or type,
- an implausible price change paired with description mismatch,
- a code retired and later reused for another item.

Treat these as potential recycled CMS identities. Preserve the mapping history rather than silently replacing it.

## Recover dependent identity fields

During Main Stock reconciliation, scan beyond blank Serial Codes. Rows can already contain a valid Serial Code while `CS Name` or another dependent identity field remains blank.

For `Serial Code present + CS Name blank` rows:

1. Look up the current catalogue identity for that code.
2. Compare it with the normalized local item name, ignoring only a terminal expiry suffix.
3. Check clinically and operationally meaningful signals such as active ingredient, strength, formulation, size/volume, unit, price plausibility, manufacturer/brand clues, and same-code sibling lots.
4. Write `CS Name` only when the combined evidence is SAFE; do not rely on the code alone.
5. If a same-code sibling lot already has a verified CS Name and the normalized product identity is compatible, that sibling history is strong supporting evidence but not permission to ignore a current contradiction.
6. Mark each successfully written and read-back-verified CS Name cell green according to `visual-marking.md`.

If code-to-catalogue evidence conflicts with the local item, do not populate the dependent identity field. Mark the disputed field red and report the contradiction.

## Correct stale mappings from authoritative evidence

A historical source document can safely correct a stale live CMS mapping when it is corroborated by the current catalogue.

Treat a mapping correction as SAFE when all of the following are true:

1. the original source clearly identifies the item, code, and catalogue/sale price,
2. the current CMS catalogue independently maps that same code to the same compatible product identity and price,
3. the live Main Stock row corresponds to that historical receipt through compatible local identity, expiry, quantity, or other strong receipt evidence,
4. no stronger contradictory evidence exists.

In that case, correct only the stale current mapping fields supported by the evidence, typically `Serial Code`, `CS Name`, and `CMS Price`. This is a mapping reconciliation, not a new intake and not permission to rewrite historical operational truth.

Do not change the derived `Price` field as part of this correction merely because `CMS Price` changes. Preserve the Excel-side pricing/expiry logic and leave `Price` untouched unless its own contract explicitly authorizes a write.

## Apply prices safely

When identity is compatible, update only the appropriate current CMS price field allowed by the live sheet contract. Do not overwrite receipt-time prices or other genuine historical transaction truth because the current catalogue changed.

Preserve the local operational item name unless the user explicitly authorizes reconciling the local identity/specification to authoritative catalogue evidence. Model the relationship as `Local Name <-> CMS catalogue identity/history`, allowing CMS brand or code to change over time.

## Audit

For each reconciled item, retain enough evidence to explain SAFE, REVIEW, CONFLICT, or NEW / UNMAPPED classification. Use `Audit_Log` for significant price synchronization, recycled-code findings, multi-row propagation, historical-source corrections, confirmed mapping changes, or broad CS Name recovery passes.

Read back affected rows and verify intended CMS prices, identities, untouched derived `Price`, formulas, visual marks, and unchanged neighboring cells before reporting success.
