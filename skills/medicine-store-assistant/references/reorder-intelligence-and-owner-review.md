# Reorder Intelligence and Owner Review Policy

Use this reference whenever `$msa` analyzes, recommends, reviews, archives, or prepares reorder decisions. It defines the current skill-side operating model for adaptive reorder reasoning without changing the Excel-compatible operational table contracts.

## Core operating principle

The live Google workbook is both an operational interface and an evidence source, but not every evidence sheet is a human UI.

Use this separation:

- **Deterministic calculations** handle balances, usage totals, stock gaps, history statistics, expiry state, and reproducible baseline quantities.
- **AI reasoning** interprets context, seasonality, anomalies, volatility, lifecycle state, historical Owner behavior, and trade-offs.
- **Owner/human judgment** supplies real operational experience, new-item intent, service changes, practical exceptions, and final authority for material changes.
- **Human-facing UI** should expose only the information needed to make a decision; raw evidence can remain hidden as agent/support state.

Do not require the Owner to read many raw data tabs or dozens of evidence columns merely because the agent can use them.

## No automatic mutation from reasoning

Reorder intelligence is review-first.

Until the Owner approves a material change or the user explicitly authorizes an operational mutation:

- do not change `Main Stock Reorder Level` from an AI recommendation,
- do not change `Main Stock Estimated Request Qty` merely to match an AI recommendation,
- do not populate `Final Reorder`,
- do not delete Main Stock rows,
- do not treat a review classification as mutation authority.

Every later operational mutation still follows the full checkpoint + readback + `Audit_Log` protocol from `system-contract.md`.

## Historical evidence model

The original macro workbook is a historical evidence source. Its archived `Master Data` can provide both usage history and archived Final Reorder decisions.

### Completed-month usage evidence

For trend statistics, use completed months rather than mixing a partial current month into long-run historical averages.

A current partial month may be used separately as current evidence, but do not silently include it in completed-month average/median calculations.

Useful family-level historical measures include:

- completed-month coverage count,
- average monthly usage,
- median monthly usage,
- recent 3-month average,
- recent 6-month average,
- historical peak usage,
- same-month-last-year usage where available,
- historical early-depletion/stock-out count.

Expose coverage count so thin history can lower confidence instead of pretending the statistics are equally reliable for every item.

### Historical Owner order evidence

Archived Final Reorder records are a separate evidence class from formula-estimated request quantities.

They represent historical human decisions and may reveal practical behavior that usage-only reasoning misses, such as:

- ordering zero-stock or dormant items,
- preserving service stock despite low recent usage,
- temporarily ordering above a deterministic gap,
- adding new items with no prior history,
- handling known upcoming demand or supply uncertainty.

Do not assume every month is completely archived. Missing monthly Final Reorder records mean missing evidence, not a zero-order decision.

When an archived Final Reorder includes both `Sub Store Qty` and `Request Qty`, derive an **order-day implied target**:

`Owner implied target = Sub Store Qty + Request Qty`

This quantity is often a better historical decision signal than `Request Qty` alone because it expresses the stock position the Owner was trying to create at that snapshot.

Do **not** compare an old `Request Qty` directly with a later live `Order This Round` and call the difference an error. Current stock may have changed through usage, receipts, or other movements. When snapshot dates differ, prefer:

- archived Owner implied target versus current AI `Suggested Reorder Level`, and
- archived request quantity only as supporting evidence about how the Owner acted at that earlier stock state.

Treat the comparison as decision-pattern evidence rather than a simplistic error score.

A hidden/static support sheet may preserve exact archived Owner-order evidence for agent use. Keep the human-facing summary concise.

## Conservative family identity

Reorder history is normally interpreted at the local item family level, not blindly row-by-row.

For historical family normalization:

- normalize case/spacing only as needed,
- remove only a clearly terminal expiry month/year suffix when it is lot metadata,
- preserve strength, formulation, size, gauge, volume, route, product-defining parentheses, brand/manufacturer clues, and other clinically/operationally meaningful identity,
- do not fuzzy-bridge unresolved history families merely to improve coverage.

If no exact conservative history family match exists, classify the history as unresolved/limited and use Owner or stronger identity evidence instead of inventing a match.

## Lot-level state versus family-level demand

A physical stock row and a product-family demand signal are different concepts.

- Usage from an older lot that depleted this month remains valid family demand evidence.
- A zero-stock cleanup-candidate lot should not automatically control the current operational family target when an active representative exists.
- Historical Owner targets may reveal that an apparently obsolete sibling-row level was actually carrying meaningful family-level policy; do not discard that possibility without review.
- Multiple lots of the same family should not duplicate the same historical demand signal into multiple independent reorder recommendations.
- Family reasoning may aggregate current usage across lots while keeping lifecycle/expiry handling row-aware.

## Usable stock versus expired stock

Always distinguish:

- **Usable Current Stock** — stock that can currently support normal service,
- **Expired Stock Qty** — positive stock that is expired and requires separate disposition/review.

Expired stock must not inflate usable stock in request-gap calculations.

However, **expired-stock disposition must not hard-block replenishment**. If usable stock is low/zero and demand evidence supports replenishment, the correct workflow can be:

1. replenish usable stock, and
2. resolve expired-stock disposition in parallel.

Do not force the store to wait for disposal/expiry resolution before considering a needed replacement order.

## Row lifecycle policy

Use row lifecycle reasoning to keep Main Stock concise without losing future reorder identity.

Recommended classifications:

- `ACTIVE_LOT` — positive usable/current stock row or otherwise active operational representative.
- `SAFE_CLEANUP_CANDIDATE` — zero-stock row that is redundant because another same-family usable/current representative exists.
- `FRESH_REORDER_KEEP` — zero-stock row with a fresh/current expiry that must be retained when the positive-stock sibling is expired; use the fresh row as the future reorder representative.
- `DORMANT_ITEM_KEEP` — zero-stock sole representative retained so the item remains available for future ordering/identity.
- `DUPLICATE_ZERO_REVIEW` — multiple zero-stock rows exist but no positive-stock representative; retain at least one suitable/fresh keeper before redundant rows are deleted.
- `EXPIRED_STOCK_REVIEW` — positive expired stock exists and should not be deleted merely as row cleanup.

### Fresh-zero keeper rule

A positive-stock sibling is **not automatically a valid replacement representative** when that stock is expired.

If an item family contains:

- an expired positive-stock row, and
- a fresh/current zero-stock row,

keep the fresh zero-stock row. The operational intent may be to order only fresh stock while separately resolving the expired stock. Do not delete the fresh row merely because another family row has a positive quantity.

Example pattern:

- old/expired lot: stock `10`,
- fresh future-expiry lot: stock `0`.

The fresh row is `FRESH_REORDER_KEEP`; expiry disposition and replenishment remain separate workflows.

When a family has several zero-stock rows and no positive usable representative, prefer preserving a current/fresh representative rather than an obsolete expired row. Do not delete every row in the family.

### Critical distinction: dormant identity is not reorder suppression

`DORMANT_ITEM_KEEP` / `DORMANT_KEEP` means **keep the row/item identity**. It does **not** mean “do not order.”

A dormant sole row may still need a reorder recommendation when current usage, stock-out, known demand, historical Owner behavior, or explicit Owner intent supports replenishment.

This distinction is mandatory. Lifecycle state controls row retention; demand evidence controls reorder need.

### Cleanup mutation boundary

A row classified as cleanup candidate is still review-only until deletion is explicitly authorized.

Before deleting a zero-stock duplicate row:

- verify another appropriate representative row preserves the family identity,
- verify that the supposed representative is not merely an expired-stock row when a fresh zero-stock row should be retained,
- preserve historical usage/order evidence independently of the row deletion,
- ensure no unresolved mapping/receipt/audit evidence depends on the row,
- checkpoint the workbook,
- delete only the approved row(s),
- read back family integrity and row numbering/formulas as required,
- audit the cleanup.

## Reorder risk taxonomy

Risk classifications are attention filters, not final business decisions.

Useful classes include:

- `RAISE_RISK` — evidence suggests current level may be insufficient,
- `LOWER_CANDIDATE` — excess/expiry/low-use evidence suggests current level may be too high,
- `VOLATILE` — demand varies enough that a stable numeric change should be treated cautiously,
- `LIMITED_HISTORY` — evidence coverage is too thin for confident numeric inference,
- `KEEP_REVIEW` — no strong raise/lower signal but routine review may still be useful,
- `OWNER_REVIEW` — conflicting, unresolved, new-item, lifecycle, or practical-context evidence requires human judgment.

Secondary pattern flags may include `SEASONAL_SIGNAL`, `CURRENT_SPIKE`, `HISTORICALLY_VOLATILE`, and `NO_STRONG_PATTERN`.

Operational evidence flags may include current early depletion, repeated historical early depletion, expiry exposure, current spike, stock high relative to history, and same-month-last-year seasonal evidence.

Do not let a single median-zero or low-volume artifact over-classify many items as volatile. Volatility rules must represent meaningful deviation, not merely sparse arithmetic.

## Confidence model

Confidence communicates evidence quality, not permission to mutate.

Typical interpretation:

- `HIGH` — exact identity, adequate history, simple lifecycle/lot state, coherent evidence.
- `MEDIUM` — exact identity but multi-lot, seasonal, volatile, expiry, or other contextual complexity.
- `LOW` — no exact history, thin coverage, unresolved identity, new item, or materially conflicting evidence.

A useful default is to downgrade confidence when historical coverage is limited, but do not turn an arbitrary month-count threshold into an unquestionable business rule.

## Reorder level versus order-this-round

These are separate concepts and must be presented separately to the Owner.

### Suggested Reorder Level

The proposed maintained operational target/threshold for the item family going forward.

### Order This Round

The quantity to request in the current order cycle after considering usable current stock and the approved/suggested target.

A level can be appropriate while the current-cycle request is zero.

Example:

- Usable stock now: `50`
- Suggested reorder level: `49`
- Order this round: `0`

Meaning: current usable stock already covers the suggested target, so no order is needed in this cycle.

## Practical ordering quantity heuristics

Do not assume the mathematically estimated request quantity is the exact quantity a human operator should submit.

Real ordering is discrete and operational. The Owner may reasonably round or reshape a baseline based on packaging, service experience, cost, expiry risk, and expected demand.

Current practical evidence includes:

- many ordinary items are commonly requested in multiples of `10`;
- tablets are often requested in at least multiples of `50`;
- common tablet packaging may be `100 tablets per box`, so an arithmetic baseline such as `220` may reasonably become `250` or `300` when usage is high and expiry risk is low, especially when a box-friendly quantity avoids awkward partial packaging;
- low-frequency or expensive injections may be ordered in small individual counts;
- suspensions, eye drops, cream tubes, and other bottle/tube items may also be ordered in small discrete counts;
- expensive items deserve stronger caution against unnecessary buffer stock;
- high-use, low-expiry-risk items can justify a larger practical buffer than the bare deterministic gap.

These are **heuristics, not universal formulas**. Never invent a pack size or force every item into the same rounding rule. Use verified product/pack evidence when known and Owner experience when product economics or service practice matter.

A useful ordering pipeline is:

1. deterministic baseline,
2. identify item type / known pack or practical order increment,
3. assess usage intensity, expiry risk, cost, supply reliability, and service importance,
4. apply a defensible discrete rounding/buffer adjustment,
5. present the resulting order as a recommendation rather than false precision.

Do not overfit the system to one historical Owner quantity. Human decisions are useful evidence but are not guaranteed to be perfectly optimal.

## Uncertainty and sudden events

Medical-store demand is probabilistic. Exact future patient volume cannot be known in advance.

The goal is not a perfect flat formula that prevents every shortage. Use the available factors to make a reasonable forecast and preserve explicit uncertainty.

Sudden outbreaks, unusual patient mix, service changes, emergency events, supply disruptions, or other shocks can still produce shortages even after a reasonable order. Historical sudden-event shortages are useful evidence, but the system must not pretend they were always predictable.

Prefer robust buffers and Owner review where justified rather than claiming exact certainty.

## Human-facing action wording

Do not expose internal risk labels when a clearer business action can be shown.

Prefer action wording such as:

- `RAISE LEVEL (old -> new)` — target level actually increases,
- `LOWER LEVEL (old -> new)` — target level actually decreases,
- `KEEP LEVEL / ORDER GAP` — target stays the same but current usable stock is below it,
- `LEVEL OK / NO ORDER` — current level/stock already cover the suggested target,
- `RAISE + EXPIRY REVIEW` — replenishment is needed while expiry disposition runs in parallel,
- `HOLD REVIEW` — conflicting/volatile evidence needs context before numeric action,
- `OWNER REVIEW` — human knowledge is primary,
- `NEW ITEM - OWNER DECISION` — no reliable historical basis; Owner decides whether/what to introduce.

Avoid misleading output such as `RAISE (49 -> 49)` when no actual level increase exists.

## Deterministic baseline versus AI adjustment

A numeric recommendation should be explainable as:

1. verified arithmetic baseline,
2. contextual adjustment, if any,
3. final review recommendation.

Evidence that may justify adjustment includes recent 3M/6M demand, same-month-last-year seasonality, repeated early depletion, current partial-month spikes, historical volatility, expiry/write-off pressure, supply reliability/lead time, known future service demand, pack/order-size constraints, and Owner operational experience.

Do not use the LLM as the arithmetic engine. Do not make one historical peak the permanent new level automatically.

## Lowering logic

A lower-level recommendation should normally require coherent evidence such as low recent use, excess stock, expiry/write-off exposure, or sustained overstock.

Be conservative when history is volatile, history coverage is thin, service stock has critical practical value, old peak usage is much higher than recent average, or future demand is uncertain.

A deterministic lower baseline may be adjusted upward by AI/Owner for a safer service-stock floor.

## Owner Decision Inbox

The preferred human-facing review surface is a concise decision inbox, not a raw analytics table.

Recommended reorder decision columns:

1. `Priority`
2. `Item`
3. `Usable Stock Now`
4. `Current Level`
5. `AI Action`
6. `Suggested Reorder Level`
7. `Order This Round`
8. `Owner prior order: Stock + Order = Target` when comparable archived evidence exists
9. `Comparison`
10. `Why / What I need from you`
11. `Your Decision`
12. `Your Level`
13. `Your Request`
14. `Your Note`

The item label should prefer the active/current operational representative, not an obsolete zero-stock/expired sibling row merely because it sorts first.

The Owner should not need to open `Main Stock` just to learn current usable stock or current level for a decision being requested.

Useful comparison labels include:

- `AGREES WITH OWNER TARGET`
- `AI TARGET LOWER`
- `AI TARGET HIGHER`
- `HOLD / CONTEXT NEEDED`
- `OWNER-CONTEXT ITEM`
- `NO PRIOR ORDER EVIDENCE`

When AI and archived Owner targets differ, ask whether the historical target reflects a normal practical buffer or a one-off decision. Do not ask the Owner to inspect the raw archive.

Keep explanations concise and action-oriented. Owner input fields remain blank until the Owner actually decides.

## New items

New items are a first-class Owner decision case.

When the Owner orders an item that has no exact current family/history match:

- do not treat the absence of history as evidence against ordering,
- classify it as new/unmapped/Owner-led,
- preserve the exact item/specification evidence,
- let the Owner decide intended introduction quantity or service-stock rationale,
- later use actual receipts/usage as evidence for future adaptive levels.

A compact evidence-only section may show recently Owner-ordered new/unmatched items without forcing a new decision when the order was already placed.

AI may provide context or comparable-item evidence when safe, but it must not overrule the Owner merely because historical usage is absent.

## Owner-vs-AI validation loop

Use actual archived Final Reorder decisions to improve the reasoning policy.

Prefer comparing **Owner implied target** (`Sub Store Qty + Request Qty`) with AI `Suggested Reorder Level` when the archived and live snapshots differ.

Comparison categories can include:

- **AI reasonable agreement** — Owner implied target and AI target are directionally close,
- **Owner practical adjustment** — Owner historically targeted more/less than current AI reasoning,
- **New/strategic Owner item** — no history; Owner authority dominates,
- **AI missed lifecycle/context** — for example dormant-item reorder incorrectly suppressed,
- **AI expiry-workflow mismatch** — replenishment incorrectly blocked by expiry disposition,
- **snapshot timing difference** — stock/usage changed between order date and analysis date,
- **unresolved identity** — not safe to compare until family/spec mapping is resolved.

Do not train a rigid formula to copy historical Owner quantities. Treat Owner history as another evidence stream that can reveal stable practical heuristics or exceptions.

## Final Reorder boundary

`Final Reorder` remains the exact six-column Excel-compatible output surface defined in `operational-sheet-compatibility.md`.

Reasoning/helper columns never belong in Final Reorder. Only approved current-cycle decisions should be materialized there.

`Remark` remains blank by default and must never be populated with AI rationale unless the user explicitly instructs the exact remark content.

## Agent evidence tabs versus human UI

Raw evidence tabs may contain many columns and may be hidden from normal human view when they remain available to the agent and do not break workbook behavior.

Examples include historical usage evidence, risk flags, family-level foundations, lower-level reasoning, full AI review details, row lifecycle review, archived Owner-order evidence, and Owner-vs-AI comparison evidence.

Do not delete useful evidence merely to reduce visual clutter. Prefer hiding or moving support tabs behind the human-facing group.

The normal visible operational surface should stay small and human-friendly. `Owner_Decision_Inbox` may be visible as the primary review surface while detailed evidence stays hidden/support-only.

## Audit expectations

Material reasoning-layer changes should be auditable even when they do not yet mutate Main Stock.

For operational mutations, always use checkpoint + readback + audit.

For review-only reasoning refinements, record enough context to explain major policy changes when they materially affect future recommendations, especially row lifecycle logic, expired-stock usability rules, family aggregation rules, historical Owner-order evidence, comparison semantics, practical order increments, and human-facing decision semantics.

## Hard boundaries

Never:

- equate a zero-stock sole row with “do not reorder,”
- delete a fresh zero-stock reorder representative merely because an expired sibling has positive stock,
- treat expired stock as usable stock,
- block needed replenishment solely because expired-stock disposition is unresolved,
- assume an old zero-stock sibling's reorder level is meaningless without checking family/Owner evidence,
- duplicate one family demand signal into several independent lot recommendations,
- fuzzy-match unresolved history just to get a statistic,
- force every item into one flat rounding or pack-size formula,
- invent pack size or packaging evidence,
- claim that an estimated request quantity is exact or guaranteed to prevent shortage,
- ask the Owner to inspect large raw evidence tables when a concise decision prompt can carry the needed context,
- call a recommendation `RAISE` when the suggested level is unchanged,
- assume missing archived Final Reorder data means no order was placed,
- compare an archived request quantity directly with a later live request quantity as if both share the same stock snapshot,
- treat archived Owner orders from a different snapshot date as directly comparable without timing context,
- populate `Final Reorder` or its `Remark` from AI reasoning without the required Owner authorization.