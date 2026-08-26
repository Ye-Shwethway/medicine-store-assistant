# Expiry, Return-to-CMS, and Discard Lifecycle

Use this reference whenever `$msa` evaluates near-expiry stock, return-to-CMS opportunities, expired-stock retention, FOC use, discard preparation, CMS discard approval, or eventual row cleanup.

This workflow is **not discard-centered**. Its goal is to reduce expiry loss while preserving necessary service stock and respecting Owner judgment for rare or critical medicines.

## Core principles

1. `Expired` does not mean `discard now`.
2. `Expired` does not always mean `never use`; local operational policy may allow retained/FOC or emergency use.
3. Return-to-CMS should be considered **before expiry** when excess stock is unlikely to be consumed in time.
4. CMS return eligibility requires more than 3 months remaining shelf life. Operationally, begin return review earlier, around 4 months remaining, to allow transport/processing buffer.
5. A 6-month post-expiry point is a **default discard-review trigger**, not an automatic physical-discard command.
6. Rare/critical items may be retained beyond 6 months under explicit Owner policy or case-by-case Owner decision.
7. Physical discard requires CMS approval when that is the operating policy. Do not reduce stock or delete rows merely because an item is discard-due.
8. Row deletion is the final structural step, only after actual stock disposition is complete and month/archive requirements are satisfied.

## Return-to-CMS window

CMS accepts returns only when more than 3 months of shelf life remain. Because transport and processing can consume time, use approximately **4 months remaining** as the practical review point unless stronger current operational evidence says otherwise.

Do not wait until exactly 3 months remaining if that creates a meaningful risk of missing the acceptance window.

### Return-review inputs

For each near-expiry lot, consider:

- current lot quantity,
- exact expiry date,
- current date / months remaining,
- recent completed-month usage,
- current partial-month usage when relevant,
- demand volatility,
- item criticality/service importance,
- known standby-only use,
- ability to reorder again next month,
- replacement/supply reliability when known,
- pack/order increments when verified,
- whether another fresher lot already exists.

Use deterministic arithmetic for baseline quantities and AI/Owner reasoning for contextual adjustment.

## Keep-versus-return quantity model

Do not assume all near-expiry stock should be returned.

A practical baseline is:

`Return Candidate Qty = max(Current Return-Eligible Qty - Planned Retained Qty, 0)`

`Planned Retained Qty` may be based on one of several modes below.

### Mode A — Forecast-to-expiry retain

Use when demand is regular enough that historical consumption is informative.

Estimate what is reasonably likely to be consumed before expiry, then retain that amount plus any justified safety buffer. The remaining eligible surplus may be returned.

### Mode B — One-month-cover retain

Use when the forecast is uncertain or the Owner wants a conservative fresh-stock strategy.

If the item can normally be requested again the following month, it may be safer to retain only approximately one month of expected use and return the rest while the CMS return window is still open.

This is especially useful when:

- current use is low,
- demand is uncertain,
- expiry loss would otherwise be likely,
- the item is readily reorderable next cycle.

Do not force this mode on items whose service importance or supply reliability makes one-month cover unsafe.

### Mode C — Return all and reorder fresh

For very-low-use or standby-only items, retaining even one month of calculated demand may not be meaningful.

If an item is essentially held as a small standby quantity and has little or no actual usage, the Owner may choose to:

1. return the entire return-eligible lot before the CMS cutoff, and
2. request a fresh minimal standby quantity in a later cycle.

Examples of the **pattern** include items held for services that are not currently active, such as spinal-anesthesia-related stock when major surgery is not being performed. Do not hard-code named medicines into this category merely from model knowledge; use explicit Owner confirmation or verified local history.

The Owner may keep only 1-2 units for some standby items, or return all when a fresh replacement can be requested again. This is an Owner-led operational decision, not a universal formula.

## Suggested return actions

Human-facing action wording may include:

- `MONITOR` — not yet near the return window or no action needed.
- `RETURN REVIEW` — approaching the practical return window; calculate keep/return quantities.
- `KEEP ONE-MONTH COVER / RETURN REST` — conservative retain strategy when reorder next month is practical.
- `RETURN SURPLUS` — retain forecast/safety stock, return the excess.
- `RETURN ALL / REORDER FRESH` — very-low-use or standby item where retaining the current lot is not worthwhile.
- `KEEP FOR USE` — expected consumption before expiry supports keeping the lot.
- `OWNER REVIEW` — criticality, rarity, service context, or supply uncertainty makes automatic advice unsafe.

## Expired-stock operational states

Expired stock must remain physically and logically tracked until its real disposition is complete.

Recommended states:

- `EXPIRED_FOC_WINDOW` — expired but within the local post-expiry operating window; retained and potentially used under local policy.
- `EMERGENCY_RESERVE` — expired stock retained because fresh replacement is not available and the item is critical/rare enough that exceptional use may be necessary.
- `DISCARD_REVIEW_DUE` — default review state after approximately 6 months expired.
- `OWNER_EXCEPTION_KEEP` — Owner explicitly decides to retain beyond the default discard-review point.
- `DISCARD_APPROVAL_PENDING` — discard request submitted to CMS; physical stock remains until approval.
- `DISCARD_APPROVED` — CMS approval received; physical disposal may proceed.
- `DISCARDED` — physical stock has actually been disposed/removed.
- `ROW_CLEANUP_READY` — stock disposition is complete and row/archive constraints permit structural deletion.

These are operational states, not all necessarily columns in the human-facing workbook.

## FOC window

Current operating policy allows many expired medicines to remain in use as FOC for up to approximately **6 months after expiry**.

Do not interpret this as a universal clinical rule outside the user's operational policy. Within `$msa`, treat it as the verified local stock-management workflow supplied by the Owner.

Within this period:

- retain the row,
- keep the expired quantity visible,
- do not count it as ordinary fresh/usable stock for standard replenishment-gap calculations,
- but do not pretend it is nonexistent,
- replacement can still be requested in parallel,
- actual use of the expired quantity must be recorded as it physically occurs.

## Emergency / rare-item exception

Some medicines may be retained and exceptionally used beyond the normal 6-month review point when they are rare, critical, difficult to replace, or operationally valuable as emergency reserve.

Examples supplied by the Owner include patterns such as emergency medicines (for example adrenaline or naloxone when fresh replacement is unavailable) and very rare medicines such as morphine injection that may be retained far longer.

Important:

- the assistant must not independently designate a medicine as indefinite-retain merely from general medical knowledge;
- Owner confirmation or verified local policy is primary;
- once the Owner establishes a durable exception policy for a specific item/family, preserve that as operational evidence so it need not be re-decided every cycle unless conditions change;
- `>6 months expired` remains a review signal, not an automatic discard command.

## Replacement and discard are parallel workflows

A fresh replacement may be requested before, during, or after the FOC period.

Do not block replacement merely because the expired lot is still physically present.

Conversely, do not physically discard the expired lot simply because fresh stock arrived. Apply the real discard policy:

1. determine discard eligibility/review state,
2. prepare/submit CMS discard request when required,
3. wait for approval,
4. perform actual discard,
5. record the disposition,
6. only then consider quantity zeroing / row cleanup under the month-close and paired-row rules.

## Discard approval gate

When CMS approval is required:

- `DISCARD_REVIEW_DUE` does not authorize disposal,
- `DISCARD_APPROVAL_PENDING` means stock stays recorded,
- only verified approval permits actual discard,
- only actual discard permits inventory quantity mutation reflecting disposal,
- row deletion remains a later structural action and must preserve historical evidence.

Do not infer approval from elapsed time.

## Human-facing expiry/return queue

Prefer a concise decision surface. Useful columns include:

1. `Item`
2. `Qty`
3. `Expiry`
4. `Months Left / Months Expired`
5. `Recent Usage`
6. `Suggested Retain Qty`
7. `Suggested Return Qty`
8. `Current State`
9. `Next Action`
10. `Why / What I need from you`
11. `Owner Decision`
12. `Owner Qty / Note`

Do not force the Owner to inspect raw usage-history tables to decide a return.

For return cases, make the action concrete, for example:

- `KEEP ~1 MONTH / RETURN 40`
- `RETURN ALL / REORDER FRESH NEXT CYCLE`
- `KEEP 2 AS STANDBY / RETURN REST`
- `OWNER REVIEW — RARE/CRITICAL`

Only populate exact quantities when the arithmetic and evidence support them.

## Forecast uncertainty

Future patient demand is uncertain. Return decisions should reduce avoidable expiry loss without creating preventable shortages.

Use historical demand as evidence, not certainty. Sudden service changes or emergency demand can still occur.

When evidence is weak, prefer:

- a conservative one-month-cover strategy when reorder next month is reliable,
- a small standby reserve for low-use items when Owner experience supports it,
- or explicit Owner review rather than false precision.

## Integration with reorder reasoning

Near-expiry return analysis and replenishment are related but separate.

- Returning excess stock can reduce the current usable quantity and may justify a future fresh request.
- A planned return should not silently reduce the reorder target before the return actually occurs unless clearly marked as a scenario/proposal.
- Expired stock remains excluded from ordinary fresh-stock gap calculations, but may remain physically available under the local FOC/emergency policy.
- `OWNER_EXCEPTION_KEEP` must not suppress fresh replacement when the Owner wants both a reserve and a fresh lot.

## Integration with month close and row cleanup

Follow [month-close-archive-and-cleanup.md](month-close-archive-and-cleanup.md) for structural row deletion.

Do not delete a row merely because it is expired, return-due, discard-due, approved for discard, or reduced to zero during an active month.

A row becomes structurally cleanup-ready only after:

- return/discard/usage disposition is reflected in actual stock,
- required approvals/evidence are preserved,
- the closed-month history is archived where applicable,
- another appropriate representative row remains when needed,
- paired `Main Stock` / `Daily Usage` cleanup is authorized and checkpointed.

## Mutation boundary

Return/discard reasoning is review-first.

Before any operational mutation:

- inspect live stock and lot identity,
- verify the return/discard source or Owner instruction,
- create a fresh full-workbook checkpoint,
- mutate only the exact approved quantities/rows,
- read back affected `Main Stock`, `Daily Usage`, and relevant summary/support state,
- record the operation in `Audit_Log` with the checkpoint ID.

Never claim a return, discard, or CMS approval occurred unless the source evidence or user instruction establishes that it actually occurred.
