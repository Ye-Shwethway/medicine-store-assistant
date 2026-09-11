# Received Stock Operational Workflow

Use this reference whenever `$msa` processes a newly received medicine/consumable supply, reconciles received quantities into the live workbook, or explains how `This Month Received` relates to `Main Stock` and `Daily Usage`.

This workflow preserves the Excel-compatible operational surfaces while making receipt handling explicit, lot-aware, idempotent, and auditable.

## Core model

Treat the receipt workflow as:

**source evidence -> local-family/identity resolution -> lot resolution -> checkpoint -> Main Stock mutation -> Daily Usage alignment -> derived This Month Received summary -> readback -> Audit_Log**

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
- source unit/presentation wording,
- price,
- expiry date,
- transfer/batch number,
- receipt/supply date,
- source-specific identifiers.

Preserve exact numbers. Distinguish blank, zero, corrected, and unreadable fields. Never convert a requested quantity into received quantity without source evidence.

The source is authoritative for the physical receipt facts, but source wording is not automatic authority for the established local `Items` name or local operational `Unit` convention.

### Local inbound quantity sign rule

MSA records the **local receiving store** state. It does not require CMS-side database access to interpret an inbound transfer.

When the source document clearly represents stock being transferred **into the local hospital/store**, record the local received quantity as a positive magnitude. If the source/issuing report expresses the issuer's movement as a negative number, convert that inbound line to the corresponding positive local `Received Stock` quantity.

Example: issuer report `-100` for a transfer received by the local store -> local `Received Stock +100`.

Do not use absolute value on arbitrary fields or ambiguous movements. First establish from the source document that the line is an inbound receipt for the local store; after that, local receipt quantity is positive by definition.

## Local-family reconciliation gate

Before classifying a line as `NEW_ITEM`, first prove that no safe existing operational family already represents it.

Use, as available:

1. adjacent/same-family rows in the live table,
2. expiry-suffix-normalized local naming,
3. compatible strength/form/size/specification and local Unit,
4. confirmed `Item_Mapping`,
5. current CMS catalogue/price-list evidence,
6. verified older local/baseline rows,
7. authoritative source descriptions and clinically/operationally meaningful synonym relationships.

Preserve the established local operational family name when the receipt is merely a different CMS brand/code/source description for the same local item. Keep CMS/source identity in `Serial Code`, `CS Name`, catalogue evidence, and audit history.

Do not create a new local item merely because the source wording differs from the local operational wording.

## Receipt classification

Before any inventory mutation, resolve each non-fixed-asset receipt line into one of these paths:

### 1. EXISTING_LOT

The source matches an existing Main Stock lot with the same operational identity and the same expiry/lot state.

Action:

- add the verified receipt quantity to that row's current-month `Received Stock` according to the live contract,
- do not create a duplicate lot row,
- preserve the row's existing local identity/configuration unless separately corrected by stronger evidence,
- preserve the existing `Reorder Level`; an additional receipt into an already-established lot does not redefine reorder policy,
- preserve the established local Unit unless separate evidence proves it was wrong,
- verify the mirrored Daily Usage row receives/reflects the same received-stock state.

### 2. NEW_EXPIRY_LOT

The source matches an existing item family but has a distinct expiry date/lot that must remain separate.

Action:

- insert a real Main Stock row adjacent to the same-family rows,
- keep `Remaining Stock` at 0 for the newly received lot when the current workbook uses `Received Stock` for current-month receipts,
- put the actual received quantity in `Received Stock`,
- set the new row's default `Reorder Level` equal to the actual intake/received quantity when no stronger verified reorder configuration is already established for that new row,
- treat that value as an intake default/initial configuration, not as an adaptive reorder conclusion; later reorder review may revise it,
- preserve the established local operational name and Unit for the family,
- apply the canonical expiry-suffix rule below,
- populate only verified identity/configuration fields,
- insert/align the corresponding Daily Usage row in the same structural position,
- verify the new lot appears correctly in `This Month Received` through the live derived mechanism.

Follow `cms-batch-intake.md` for the detailed new-lot insertion contract.

### 3. NEW_ITEM

The source represents a genuinely new local item **after the local-family reconciliation gate finds no safe existing family match**.

Action:

- do not force a fuzzy existing-item match,
- preserve exact source specification,
- create/propose a new Main Stock item only when identity and user authority permit,
- create/align its Daily Usage row,
- initialize stable configuration conservatively,
- set the default `Reorder Level` equal to the actual intake/received quantity unless stronger verified configuration evidence or an explicit Owner instruction says otherwise,
- use a verified local operational Unit rather than blindly copying source form/presentation wording,
- apply the canonical expiry-suffix rule when expiry is known,
- do not invent pack size, usage expectation, CMS mapping, or request quantity without evidence,
- treat later usage and Owner experience as the basis for future reorder intelligence.

### 4. REVIEW / CONFLICT

Identity, expiry, code, specification, quantity, local-family mapping, unit, or prior receipt evidence is materially ambiguous.

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

## Local Unit convention

`Main Stock.Unit` is a local operational pack/count unit, not source dosage-form free text.

Before writing a Unit:

1. use a verified same-family/sibling Unit when available,
2. otherwise inspect verified older local/baseline rows,
3. use source packaging evidence only to resolve the physical operational unit, not to copy a dosage-form label blindly.

Common verified local units include `Pcs`, `Pair`, `Tube`, `Amp`, `Vial`, `Bot`, `Tab`, `Cap`, `Pkt`, `Roll`, `Set`, `Sachet`, and `Cup`.

Do not blindly write source-style values such as `Cream`, `Injection`, `Infusion`, `Oral Suspension`, `Nasal Spray`, `Pieces`, or `OTHER` when the local family uses a different operational unit. Do not globally convert all injections to one unit; resolve `Amp`, `Vial`, `Bot`, or another unit from actual family/packaging evidence.

## Canonical expiry-suffix rule

Treat `Expiry Date` as the live structured expiry field unless stronger source evidence proves it is wrong.

- Nonblank `Expiry Date` requires a terminal `(M/YYYY)` suffix in `Items` matching that structured expiry.
- Missing suffix -> append it.
- Stale/mismatching terminal expiry suffix -> replace it from the verified structured expiry.
- If stronger source evidence proves the structured expiry is wrong, correct `Expiry Date` first, then synchronize the suffix.
- Blank `Expiry Date` -> do not invent a suffix.
- Modify only the terminal expiry marker; preserve all product-defining parentheses, strengths, sizes, brands, manufacturer/country clues, gauge, formulation, and other identity text.

The suffix is lot metadata for identity matching, but it is mandatory naming metadata whenever the structured expiry is known.

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

Receipt intake does not automatically rewrite reorder policy on an **existing established row**. However, a **newly created intake row** needs an initial operational level.

Default rule:

- for `NEW_EXPIRY_LOT` and `NEW_ITEM` rows, if there is no stronger verified reorder configuration or explicit Owner instruction for that new row, initialize `Reorder Level = actual intake/received quantity`,
- for `EXISTING_LOT` receipts, keep the existing `Reorder Level` unchanged,
- do not use the legacy shortcut `Reorder Level = received quantity - 1`,
- do not treat the intake-default level as proof of the ideal long-term target,
- later adaptive reorder review may raise, lower, or otherwise replace the intake default using `reorder-intelligence-and-owner-review.md`.

The receipt amount is therefore a permitted **initialization default for new rows**, not an autonomous adaptive reorder decision for established rows.

## Price and mapping boundary

For a received line:

- preserve verified CMS/source price evidence,
- follow the current CMS matching policy before updating `Serial Code`, `CS Name`, or `CMS Price`,
- do not write derived local `Price` merely because a source price exists,
- do not overwrite historical transaction prices with a current catalogue price,
- do not rely on CMS code alone when identity evidence conflicts.

After intake, perform an identity-completeness pass on touched rows and relevant siblings. `Serial Code present + CS Name blank` is incomplete when SAFE evidence can recover the dependent identity.

For missing `Serial Code` and/or `CS Name`, use this evidence order when available:

**verified adjacent/same-family sibling -> current CMS catalogue/price list -> confirmed Item_Mapping -> verified older local/baseline data or authoritative source document**.

Do not guess. Deliberate `Nil`, `UNMAPPED`, or `EXCLUDED` states are acceptable when evidence remains insufficient.

Use `cms-price-and-matching.md` for identity-sensitive mapping decisions.

## Expiry handling

Expiry is lot-defining receipt evidence.

- same item + different expiry normally means a separate lot row,
- never merge a new fresh receipt into an old expired lot merely because the name/code matches,
- if source expiry conflicts with the existing lot's structured expiry, stop and resolve the lot identity rather than silently overwriting it,
- receiving a fresh replacement does **not** automatically authorize discard, stock removal, or row deletion of an older expired lot,
- after any verified expiry correction or row insertion, apply the canonical expiry-suffix rule globally to affected rows.

For near-expiry return decisions, FOC retention, expired-stock operational use, rare/critical keep exceptions, CMS discard approval, and eventual discard lifecycle, follow `expiry-return-and-discard-lifecycle.md`.

## Mutation protocol

For every actual receipt mutation:

1. inspect source evidence and live target rows,
2. complete marker preflight when this is a new CMS batch intake,
3. run the local-family reconciliation gate,
4. classify each line,
5. complete idempotency checks,
6. create and verify a fresh full-workbook pre-mutation checkpoint,
7. mutate the smallest required Main Stock / Daily Usage structure or values,
8. allow `This Month Received` to derive from Main Stock when that is the live contract,
9. run identity-completeness, local-Unit, and expiry-suffix checks on affected rows,
10. read back affected Main Stock rows,
11. read back corresponding Daily Usage rows,
12. read back relevant `This Month Received` rows,
13. verify unrelated usage/history was not changed,
14. verify row count, numbering, formulas, received totals, and production/staging parity when a staging mirror is intentionally maintained,
15. write `Audit_Log` with the checkpoint ID,
16. read back the audit entry,
17. stop and preserve the checkpoint if verification fails.

Do not reuse an older checkpoint for a distinct receipt mutation slice.

## Human-facing review

Do not force the Owner to inspect raw mapping or evidence tables for routine receipt work.

When review is required, present a compact line such as:

`Source item | Qty received | Expiry | Proposed action | Existing match/lot | What needs Owner decision`

Examples of concise actions:

- `ADD TO EXISTING LOT`
- `CREATE NEW EXPIRY LOT`
- `CREATE NEW ITEM`
- `LOCAL FAMILY REVIEW`
- `IDENTITY REVIEW`
- `POSSIBLE DUPLICATE RECEIPT`
- `FIXED ASSET ROUTE`

## Verification success criteria

A receipt operation is complete only when all applicable checks pass:

- exact source quantity preserved,
- inbound source sign interpreted as a positive local receipt only after confirming the line is incoming to the local store,
- correct local operational item/family and lot identity used,
- no duplicate receipt applied,
- expiry-separated lots preserved,
- every nonblank structured expiry has a matching terminal expiry suffix,
- local operational Unit convention preserved,
- new-row default Reorder Level initialized from actual intake quantity when no stronger configuration applies,
- Main Stock and Daily Usage remain aligned,
- current-month Daily Usage history remains intact,
- `This Month Received` reflects the expected receipt under the live formula contract,
- derived/helper fields were not manually seeded without authority,
- mapping/price changes are evidence-supported,
- recoverable Serial Code/CS Name blanks are resolved and true unresolved states are explicit,
- structural formula/range/parity/totals checks pass,
- checkpoint exists,
- Audit_Log entry exists and is read back.

## Shorthand command

When the Owner says something equivalent to **`process received stock`**, use this default sequence:

**inspect source -> establish local inbound receipt quantities -> inspect live workbook -> marker preflight if batch intake -> local-family reconciliation -> classify lines -> idempotency -> checkpoint -> apply safe existing/new-lot/new-item mutations -> initialize new-row Reorder Level from intake quantity when applicable -> normalize local Unit + expiry suffix + identity completeness -> verify Daily Usage alignment -> verify This Month Received -> verify formulas/parity/totals -> audit -> readback -> summarize true review exceptions**

This workflow is the canonical skill-side receipt process unless the user explicitly requests a narrower operation.