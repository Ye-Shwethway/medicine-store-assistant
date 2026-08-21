# Architecture Decisions and Open Questions

Status: **review checklist — implementation not yet authorized**

This file separates decisions already agreed in principle from questions that must be answered before their corresponding implementation slice begins.

## Agreed / locked direction

### Repository

- Keep the existing public `medicine-store-assistant` repository.
- Preserve `skills/medicine-store-assistant/` as the canonical independently installable Git-backed skill.
- Add future backend/runtime/integration code as sibling areas in the same repository.
- Never commit production credentials or operational data to the public repository.

### Canonical data direction

- Move toward PostgreSQL on the existing VPS as the future canonical transaction datastore.
- Do not promote PostgreSQL merely because it is deployed; require staged shadow validation and explicit promotion.
- Database identities are stable product/lot IDs, not spreadsheet row numbers.
- Preserve separate expiry lots.
- CMS code alone is never local product identity.
- Canonical stock movement is ledger/transaction based.
- Derived balances and totals are deterministic backend calculations.

### Human operational model

Keep four first-class operational views:

1. Main Stock
2. Daily Usage
3. This Month Received
4. Final Reorder

After promotion, these are projections of canonical data rather than separate independent truths.

### Historical model

- Preserve monthly history in PostgreSQL.
- Close each month into an immutable normal snapshot package sufficient to reproduce the four core views.
- Preserve the ability to export historical monthly Excel workbooks.
- Store full CMS catalogue versions historically rather than only store-matched rows.
- Keep historical transaction prices separate from current catalogue price.

### AI boundary

- AI interprets evidence, proposes/reviews mappings, explains anomalies, and orchestrates typed domain operations.
- Deterministic code/database constraints own arithmetic, validation, idempotency, atomic transactions, audit, and canonical state.
- No GPT/Telegram/Flutter/Sheet client receives arbitrary SQL access.

### Infrastructure direction

- Prefer the existing VPS before adding new recurring infrastructure cost.
- Use PostgreSQL on the VPS.
- Cloudflare Free/custom domain may provide the stable public front door/DNS/proxy/TLS layer.
- Clients use a stable inventory API hostname, not the VPS IP.
- Keep the architecture portable if Cloudflare/VPS provider/client technology changes.

### Client direction

- Trial a private MSA Custom GPT using Actions against the VPS Inventory API.
- Keep Custom GPT Actions as an adapter, not a canonical dependency.
- Telegram and Flutter later use the same versioned backend API.
- Google Sheets remains the operational mirror/compatibility surface after DB promotion.

## Must decide before database schema implementation

### 1. Opening-balance representation

Choose the exact canonical model for brought-forward stock:

- one opening transaction per lot per migration/month boundary,
- explicit monthly opening snapshot plus lifetime transaction ledger,
- another model that preserves auditability without duplicate counting.

The choice must keep month-to-month reconciliation simple and unambiguous.

### 2. Lot identity granularity

Expiry clearly separates lots, but decide how to handle same product + same expiry received in multiple transfers/prices:

- merge into one operational lot while preserving receipt-line history,
- maintain separate physical receipt lots,
- hybrid rule based on operational need.

Do not infer this solely from current spreadsheet row structure.

### 3. Product identity vs local display name

Define when a local rename is:

- harmless display-name change on the same product,
- evidence of a genuinely distinct product identity.

### 4. Quantity precision

Define units/precision rules:

- integer-only for pieces/tablets/etc.,
- decimal quantities for selected liquids/weights if needed,
- conversion rules if source and local units differ.

### 5. Negative stock policy

Decide whether negative calculated stock is:

- blocked,
- privileged-only,
- temporarily allowed with hard warning because late paperwork can occur.

### 6. Historical correction policy

Define how to correct:

- an open-month mistake,
- a closed-month mistake,
- an erroneous migration opening balance,
- an incorrect catalogue mapping that did not change physical movement.

Prefer explicit reversal/amendment over destructive history rewrite.

## Must inspect existing Excel before reorder implementation

### 7. Final Reorder algorithm

Do not implement until the actual Excel formulas/macros are inspected and documented.

Need to capture:

- source columns/inputs,
- reorder level semantics,
- surplus factor behavior,
- estimated request quantity,
- shortage date influence if any,
- expiry effects,
- rounding rules,
- exclusions/manual overrides,
- exact month-close/finalization behavior.

### 8. This Month Received contract

Inspect the current Excel sheet/macro to determine:

- whether it is line-level or item/lot aggregated,
- how multiple batches are represented,
- what prices/expiry/source metadata are retained,
- month transition/archive behavior.

## Must decide before Custom GPT write Actions

### 9. Authentication model

Initial likely direction: dedicated bearer/API key with narrow MSA GPT scope.

Still decide:

- rotation/revocation process,
- per-client scopes,
- whether high-impact actions use separate credentials or server-side approval.

### 10. Confirmation boundary

Define which GPT operations can execute routinely and which require explicit user confirmation/preview.

Likely higher-risk examples:

- new product identity,
- ambiguous CMS mapping approval,
- stock adjustment,
- historical correction,
- month close.

### 11. Idempotency ownership

Define how operation IDs are generated for GPT Actions, Telegram, Flutter, and Sheet integration so network/model retries cannot duplicate movements.

## Must decide before Google Sheet becomes mirror

### 12. Sheet-originated write policy

Choose whether, after DB promotion:

- day-usage cells remain editable and are converted to typed usage deltas,
- staff enter usage through a helper/input surface instead,
- Flutter/Telegram becomes the preferred write UI while Sheet is mostly read-only.

Do not implement unrestricted last-write-wins synchronization.

### 13. Canonical ID metadata in Sheet

Decide where stable `product_id` / `lot_id` mapping metadata lives:

- protected hidden columns,
- hidden helper sheet,
- external mapping maintained by the sync service.

It must not clutter the normal staff-facing workflow.

## Must decide before canonical promotion

### 14. Backup destination and retention

Choose an off-VPS destination and test restore.

Initial target should include daily backups and multi-period retention. Exact provider/retention can be selected later without changing the domain model.

### 15. Promotion acceptance criteria

Define measurable acceptance thresholds for:

- imported row/lot reconciliation,
- balance parity,
- usage/receipt parity,
- catalogue mapping parity,
- reorder parity,
- shadow-operation success count/duration,
- backup/restore test.

### 16. Rollback/cutback procedure

Document how to revert to the prior safe operational mode if a promoted write path fails.

## Future, not needed for v1

Do not block the first reliable canonical inventory backend on:

- Redis,
- Kafka/message broker,
- microservices,
- advanced event sourcing framework,
- managed paid database,
- multi-region database,
- complex role hierarchy,
- full offline-first Flutter synchronization,
- fixed-asset backend redesign,
- AI automation beyond proven narrow workflows.

Add these only when a concrete requirement justifies them.
