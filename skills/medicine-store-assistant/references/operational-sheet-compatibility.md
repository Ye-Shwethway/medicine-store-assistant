# Operational Sheet Compatibility Contract

Use this reference whenever `$msa` reads, writes, rebuilds, exports, or proposes structural changes to the four Excel-compatible operational surfaces.

The original macro-enabled workbook `Medicine_Store_Pang_Hseng.xlsm` is the compatibility source for these table shapes. MSA may simplify the surrounding workflow and replace legacy formulas/macros with clearer logic, but it must not casually redesign these four human-facing table contracts.

## Hard compatibility surfaces

The following four sheets are compatibility-locked operational UI surfaces:

1. `Main Stock`
2. `Daily Usage`
3. `This Month Received`
4. `Final Reorder` / exported Final Reorder Form

Other helper, review, mapping, analytics, reconciliation, and temporary workflow sheets may use MSA-native structures unless another contract explicitly says otherwise.

## Main Stock

Preserve the original production header sequence when the live sheet confirms it:

1. `No.`
2. `Items`
3. `Expiry Date`
4. `Date Status`
5. `Unit`
6. `Remaining Stock`
7. `Received Stock`
8. `Stock Status Today`
9. `Reorder Level`
10. `This Month Usage`
11. `Stock Remark`
12. `Reorder Surplus Factor`
13. `Estimated Request Qty`
14. `Shortage Date`
15. `CMS Price`
16. `Price`
17. `Remark`
18. `Reorder Row`
19. `Expiry Filter Helper`
20. `Serial Code`
21. `CS Name`

Do not insert assistant metadata inside this production range. Use support sheets such as `Item_Mapping` instead.

## Daily Usage

Preserve the legacy `A:AL` production sequence:

- `A No.`
- `B Items`
- `C Remaining Stock`
- `D Received Stock`
- `E:AI` day columns `1` through `31`
- `AJ This Month Usage`
- `AK This Month Remaining`
- `AL Remark`

### Approved Google-only extension

The current Google workflow additionally uses:

- `AM Expiry Date`

This is an approved Google-Sheet-side extension and is not part of the original Excel format yet. Do not move it into the legacy `A:AL` range.

## This Month Received

Preserve the original eight-column table header and order:

1. `No.`
2. `Items`
3. `Request Qty`
4. `Received Qty`
5. `Unit`
6. `Price`
7. `Expiry Date`
8. `Remark`

MSA may improve how these rows are derived or reconciled, but the user-facing table contract remains this shape unless the user explicitly changes it.

## Final Reorder / Final Reorder Form

This output is an external interoperability contract because the user exports it to Excel and submits it as the next batch request.

The data table must preserve the original six-column order and headers:

1. `No`
2. `Items\n(ပစ္စည်းအမျိုးအမည်)`
3. `Sub Store\n(Qty)`
4. `Request\n(Qty)`
5. `Unit`
6. `Remark`

The exact line breaks or cosmetic wrapping may vary between Google Sheets and generated Excel when needed for compatibility, but the visible wording, column order, and meaning must remain equivalent to the original Excel table.

### Final Reorder export rules

- Do not add assistant-only columns to the export.
- Do not rename or reorder the six table columns.
- Titles, logos, form numbers, decorative headers, and legacy branding outside the table are not required unless the user explicitly requests them.
- Preserve the table as a clean Excel-compatible request form suitable for the user's downstream batch-request workflow.
- `Remark` must be blank by default.
- **Never populate `Remark` autonomously.** Only write a Remark value when the user explicitly instructs what to write, and write only the requested content.
- AI reasoning, reorder rationale, confidence, anomaly notes, seasonality notes, and review explanations belong in MSA review/support views or audit evidence, not in the exported `Remark` column unless explicitly requested by the user.

## Separation of UI compatibility from intelligence

Compatibility of these four table shapes does not mean MSA must clone the legacy formulas or VBA implementation.

MSA may use simpler and better logic behind the scenes, including:

- deterministic baseline calculations,
- `Item_Mapping` evidence,
- temporary review tabs,
- human/AI reasoning for reorder adjustments,
- explicit expiry and pricing policies,
- audit/checkpoint workflows,
- generated reports.

The rule is:

> **Preserve the four operational table interfaces; modernize the machinery behind them.**

## Structural mutation rule

Any change to the headers, order, meaning, or production range of these four surfaces requires explicit user authorization. Do not infer permission merely because MSA can calculate the same information another way.
