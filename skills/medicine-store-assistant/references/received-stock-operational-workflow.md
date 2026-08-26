# Received Stock Operational Workflow

Use this reference whenever `$msa` processes a newly received medicine/consumable supply, reconciles received quantities into the live workbook, or explains how `This Month Received` relates to `Main Stock` and `Daily Usage`.

This workflow preserves the Excel-compatible operational surfaces while making receipt handling explicit, lot-aware, idempotent, and auditable.

## Core model

Treat the receipt workflow as:

**source evidence -> identity/lot resolution -> checkpoint -> Main Stock mutation -> Daily Usage alignment -> derived This Month Received summary -> readback -> Audit_Log**

Do not treat `This Month Received` as an independent inventory authority when the live workbook shows it is derived from `Main Stock`.

In the current Google workbook, `This Month Received` is a human-facing summary whose populated rows are derived from nonzero `Main Stock Received Stock` values. Its table shape remains compatibility-locked, but the underlying source of receipt truth is the verified source document plus the corresponding Main Stock lot mutation.

## This Month Received semantics

Preserve the eight-column compatibility surface:

1. `No.`
2. `Items`
3. `Request Qty`
4. `Received Qty`
5. `Unit`
6. `Price`
7. `Expiry Date`
8. `Remark`

When the live workbook uses formulas such as FILTER from Main Stock:

- do not overwrite those formulas merely to enter a receipt,
- do not manually duplicate a received quantity into this sheet if the Main Stock mutation will make it appear automatically,
- verify after intake that the expected item/lot appears in `This Month Received` with the correct received quantity, unit, price, and expiry,
- treat `Request Qty` as separate request-history/context when available; it is not the received quantity and must not be inferred from the receipt,
- leave `Remark` unchanged/blank unless the user explicitly supplies a remark.

If the live workbook later changes from derived to manually maintained receipt rows, inspect and follow that verified contract rather than assuming the current formula behavior forever.

## Source authority

Receipt truth starts from actual source evidence such as:

- CMS transfer/supply paper,
- issue paper,
- verified image/photo,
- transfer/batch sheet,
- other authoritative receipt document.

Capture only supported fields, including as available:

- local/CMS item identity,
- CMS code,
- quantity actually received,
- unit,
- price,
- expiry date,
- transfer/batch number,
- receipt/supply date,
- source-specific identifiers.

Preserve exact numbers. Distinguish blank, zero, corrected, and unreadable fields. Never convert a requested quantity into received quantity without source evidence.

## Receipt classification

Before any inventory mutation, resolve each non-fixed-asset receipt line into one of these paths:

### 1. EXISTING_LOT

The source matches an existing Main Stock lot with the same operational identity and the same expiry/lot state.

Action:

- add the verified receipt quantity to that row's current-month `Received Stock` according to the live contract,
- do not create a duplicate lot row,
- preserve the row's existing identity/configuration unless separately corrected by stronger evidence,
- verify the mirrored Daily Usage row receives/reflects the same received-stock state.

### 2. NEW_EXPIRY_LOT

The source matches an existing item family but has a distinct expiry date/lot that must remain separate.

Action:

- insert a real Main Stock row adjacent to the same-family rows,
- keep `Remaining Stock` at 0 for the newly received lot when the current workbook uses `Received Stock` for current-month receipts,
- put the actual received quantity in `Received Stock`,
- populate only verified identity/configuration fields,
- preserve expiry-separated lot naming according to the established suffix rule,
- insert/align the corresponding Daily Usage row in the same structural position,
- verify the new lot appears correctly in `This Month Received` through the live derived mechanism.

Follow `cms-batch-intake.md` for the detailed new-lot insertion contract.

### 3. NEW_ITEM

The source represents a genuinely new local item with no safe current family match.

Action:

- do not force a fuzzy existing-item match,
- preserve exact source specification,
- create/propose a new Main Stock item only when identity and user authority permit,
- create/align its Daily Usage row,
- initialize stable configuration conservatively,
- do not invent a Reorder Level, pack size, usage expectation, CMS mapping, or request quantity without evidence,
- treat later usage and Owner experience as the basis for future reorder intelligence.

### 4. REVIEW / CONFLICT

Identity, expiry, code, specification, quantity, or prior receipt evidence is materially ambiguous.

Action:

- do not mutate that line silently,
- preserve the source and show a concise review question,
- continue processing unrelated SAFE lines when possible.

### 5. FIXED_ASSET

Confirmed fixed assets do not enter Main Stock/Daily Usage. Route according to `fixed-assets.md`.

## Idempotency

Before adding any received quantity, verify the transfer/receipt has not already been applied.

Use multiple signals where available:

- transfer/batch identifier,
- normalized item identity,
- expiry,
- received quantity,
- source price,
- preserved batch evidence,
- Main Stock current-month received state,
- Audit_Log,
- prior checkpoint/receipt evidence.

If the same receipt is already represented, switch to reconciliation-only mode. Never add the quantity twice simply because the source paper is presented again.

## Existing-lot quantity semantics

The live workbook must be inspected before deciding whether a receipt quantity should replace or increment an existing Main Stock `Received Stock` value.

Default operational intent for multiple receipts in the same month is cumulative current-month receipt state:

`new Received Stock = existing verified current-month Received Stock + newly received quantity`

But do not apply this arithmetic blindly if the live row already includes the same transfer. Complete idempotency first.

Do not rewrite `Remaining Stock` merely to make the balance look current. Under the current Daily Usage contract, `Remaining Stock` is the opening/base stock source and `Received Stock` is the current-month inflow; current balance is derived from opening + receipts - usage.

## Main Stock / Daily Usage paired integrity

A receipt mutation is not complete until Main Stock and Daily Usage remain structurally aligned.

For an existing lot:

- verify the corresponding Daily Usage row identity,
- verify its `Received Stock` reflects the intended Main Stock current-month receipt state through the live formula/sync contract,
- do not overwrite day-usage history.

For a new lot/item row:

- insert/repair the corresponding Daily Usage row at the matching structural position,
- preserve all prior Daily Usage rows and current-month day values,
- populate/synchronize only the verified base fields required by the live contract,
- verify `Main Stock B/F/G/C` -> `Daily Usage B/C/D/AM` behavior as applicable.

Never append a new Main Stock lot while leaving Daily Usage structurally misaligned.

## Reorder boundary

Receipt intake must not automatically redefine reorder policy.

Specifically:

- do not use the legacy shortcut `Reorder Level = received quantity - 1` as a general rule,
- do not increase/decrease Reorder Level merely because a batch arrived,
- do not treat the received quantity as proof of the ideal future target,
- keep reorder reasoning separate and use `reorder-intelligence-and-owner-review.md` when a later reorder review is requested.

A receipt quantity may become useful historical evidence later, but it is not itself an adaptive reorder decision.

## Price and mapping boundary

For a received line:

- preserve verified CMS/source price evidence,
- follow the current CMS matching policy before updating `Serial Code`, `CS Name`, or `CMS Price`,
- do not write derived local `Price` merely because a source price exists,
- do not overwrite historical transaction prices with a current catalogue price,
- do not rely on CMS code alone when identity evidence conflicts.

Use `cms-price-and-matching.md` for identity-sensitive mapping decisions.

## Expiry handling

Expiry is lot-defining receipt evidence.

- same item + different expiry normally means a separate lot row,
- never merge a new fresh receipt into an old expired lot merely because the name/code matches,
- when a fresh zero-stock representative already exists for a family with expired stock, prefer using/updating the correct fresh lot identity rather than creating unnecessary duplication,
- if source expiry conflicts with the existing lot's structured expiry, stop and resolve the lot identity rather than silently overwriting it.

## Mutation protocol

For every actual receipt mutation:

1. inspect source evidence and live target rows,
2. complete marker preflight when this is a new CMS batch intake,
3. classify each line,
4. complete idempotency checks,
5. create and verify a fresh full-workbook pre-mutation checkpoint,
6. mutate the smallest required Main Stock / Daily Usage structure or values,
7. allow `This Month Received` to derive from Main Stock when that is the live contract,
8. read back affected Main Stock rows,
9. read back corresponding Daily Usage rows,
10. read back relevant `This Month Received` rows,
11. verify unrelated usage/history was not changed,
12. write `Audit_Log` with the checkpoint ID,
13. read back the audit entry,
14. stop and preserve the checkpoint if verification fails.

Do not reuse an older checkpoint for a distinct receipt mutation slice.

## Human-facing review

Do not force the Owner to inspect raw mapping or evidence tables for routine receipt work.

When review is required, present a compact line such as:

`Source item | Qty received | Expiry | Proposed action | Existing match/lot | What needs Owner decision`

Examples of concise actions:

- `ADD TO EXISTING LOT`
- `CREATE NEW EXPIRY LOT`
- `CREATE NEW ITEM`
- `IDENTITY REVIEW`
- `POSSIBLE DUPLICATE RECEIPT`
- `FIXED ASSET ROUTE`

## Verification success criteria

A receipt operation is complete only when all applicable checks pass:

- exact source quantity preserved,
- correct item/lot identity used,
- no duplicate receipt applied,
- expiry-separated lots preserved,
- Main Stock and Daily Usage remain aligned,
- current-month Daily Usage history remains intact,
- `This Month Received` reflects the expected receipt under the live formula contract,
- derived/helper fields were not manually seeded without authority,
- mapping/price changes are evidence-supported,
- checkpoint exists,
- Audit_Log entry exists and is read back.

## Shorthand command

When the Owner says something equivalent to **`process received stock`**, use this default sequence:

**inspect source -> inspect live workbook -> marker preflight if batch intake -> classify lines -> idempotency -> checkpoint -> apply safe existing/new-lot/new-item mutations -> verify Daily Usage alignment -> verify This Month Received -> audit -> readback -> summarize review exceptions**

This workflow is the canonical skill-side receipt process unless the user explicitly requests a narrower operation.