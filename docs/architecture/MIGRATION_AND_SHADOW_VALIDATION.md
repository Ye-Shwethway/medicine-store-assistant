# Migration and Shadow Validation

Status: **design contract — implementation pending**

## Goal

Move from the current spreadsheet-first system to a PostgreSQL-backed canonical inventory system without a big-bang cutover and without losing the ability to detect migration mistakes before they affect live operations.

## Non-negotiable rule

Creating a database does **not** make it canonical.

The database becomes source of truth only after the migration data, derived calculations, transaction reconstruction, backups, and client/mirror behavior have been validated against trusted live/source evidence and explicitly promoted.

## Phase 0 — Documentation and evidence lock

Before implementation:

- lock architecture documents,
- document the current Main Stock and Daily Usage contracts,
- inspect/document This Month Received and Final Reorder behavior from the Excel source before reproducing them,
- document the reorder algorithm rather than inventing a replacement,
- define identity rules for product vs lot,
- define month-close semantics,
- define integrity/idempotency rules,
- define backup/restore minimum,
- decide unresolved policies such as negative stock and closed-month amendment.

No production database promotion occurs in this phase.

## Phase 1 — Backend foundation

Implement a minimal VPS runtime:

- PostgreSQL,
- versioned migrations,
- Inventory API/internal domain services,
- authentication boundary,
- audit/idempotency foundation,
- health/readiness endpoints,
- backup automation.

At this point the database may be empty or test-only.

Do not connect write-capable production clients yet.

## Phase 2 — Initial shadow import

Import the current authorized inventory into shadow tables/domain records.

Import must preserve:

- local product names,
- distinct expiry lots,
- current structured expiry,
- opening/base stock evidence needed to reconstruct current state,
- received/current-month usage values and their historical source where available,
- CMS mappings and current catalogue evidence,
- current display order only as presentation metadata.

Every imported row should retain a migration provenance reference so it can be traced back to the source workbook snapshot used for migration.

## Phase 3 — Historical bootstrap

Historical data should be added in the strongest available order rather than invented.

Possible sources include:

- existing Excel Master month archives,
- original transfer documents,
- preserved usage sheets/forms,
- historical catalogue files,
- current Google workbook staging/audit evidence.

Where full historical transactions cannot be reconstructed safely, preserve an explicit historical snapshot/opening-balance record rather than fabricating detailed events.

The system must distinguish reconstructed transaction history from imported snapshot/brought-forward history.

## Phase 4 — Shadow calculation

Run PostgreSQL/backend calculations without changing the live workbook.

Compare at minimum:

- lot identities and expiry separation,
- current balances,
- current-month receipt totals,
- Daily Usage day/month totals where source history exists,
- current-month remaining values,
- CMS mappings/current prices,
- month snapshot outputs,
- reorder results after the reorder algorithm is implemented.

Any mismatch is classified and investigated; it is not silently forced to match by changing whichever side is easier.

## Phase 5 — Dual verification

For new operational events, run the existing approved spreadsheet workflow and a parallel shadow database operation.

Examples:

- batch receipt intake,
- usage entry,
- new expiry lot,
- catalogue update.

Compare results after each event.

During this phase, database writes are shadow/test truth only unless a specific operation has been explicitly promoted.

Repeated agreement across realistic operations is stronger evidence than a one-time import match.

## Phase 6 — Read-path promotion

Before canonical write promotion, begin using the backend for selected read-only queries such as:

- current stock lookup,
- month summaries,
- receipt lookup,
- catalogue history.

Compare responses with trusted workbook views.

Custom GPT Actions may first be connected read-only in this phase to validate authentication/schema/tool behavior safely.

## Phase 7 — Controlled write promotion

Promote narrow operation classes one at a time.

Suggested order:

1. low-risk/read-heavy operations,
2. routine usage entry,
3. receipt intake after idempotency/mapping parity is proven,
4. adjustments with stronger authorization,
5. catalogue mapping/price updates,
6. month close only after full monthly/reorder parity.

For a promoted operation, PostgreSQL becomes canonical and Google Sheets becomes a mirror for that operation.

Avoid a mixed state in which no one knows which side is authoritative for a particular operation. Document promotion status explicitly.

## Phase 8 — Database canonicality

Promote the database as canonical only when all required conditions are met:

- migration reconciliation accepted,
- realistic shadow operations repeatedly pass,
- identity/lot behavior is correct,
- idempotency and transaction rollback are tested,
- audit records are complete,
- off-host backup and restore are tested,
- Google Sheet mirror can be rebuilt/refreshed from DB,
- current monthly views are reproducible,
- month close and reorder parity are proven before those functions become canonical,
- rollback/cutback procedure is documented.

Promotion is an explicit project decision, not an incidental consequence of deploying code.

## Phase 9 — Sheet mirror mode

After promotion:

- canonical writes enter through backend/domain APIs,
- Google Sheet is refreshed from canonical state,
- direct human Sheet edits to canonical fields are either blocked, detected, or converted into controlled API commands,
- mirror divergence is monitored,
- the workbook remains useful for humans and Excel compatibility.

## Rollback strategy

Before each promotion step, define how to return to the prior safe mode.

Rollback must distinguish:

- application rollback,
- database schema rollback/forward-fix,
- canonical transaction reversal,
- mirror resynchronization,
- full database restore.

Do not use destructive database restore merely to undo one valid but mistaken inventory transaction when an explicit correction/reversal is sufficient.

## Migration safety for public GitHub repository

No migration snapshot, inventory export, audit export, credential, or operational source file may be committed to the public repository.

Migration tooling may live in the repository with synthetic fixtures/placeholders, while real migration inputs remain in authorized runtime storage.

## Validation artifacts

Keep non-sensitive validation evidence such as:

- counts,
- schema versions,
- reconciliation summary statistics,
- synthetic/test cases,
- migration tool versions,
- anonymized invariant results where safe.

Do not publish real medicine-store operational rows merely to prove migration success.

## Stop conditions

Pause promotion if:

- product/lot identity cannot be reconciled safely,
- duplicate receipt behavior is uncertain,
- derived balance mismatches remain unexplained,
- backup/restore has not been tested,
- mirror behavior can create duplicate canonical writes,
- reorder/month-close parity is unverified,
- authentication/authorization is incomplete for the target client.

The correct response to an unresolved canonicality question is to remain in the prior safer phase.
