# CMS Catalogue Versioning

Status: **design contract — implementation pending**

## Purpose

Preserve complete CMS catalogue history without forcing the live Google workbook to carry every old price-list version forever.

The catalogue domain is separate from local inventory identity because CMS codes and descriptions may change, disappear, or be reused.

## Full-version archive

The planned database should store each imported CMS catalogue version in full.

This is preferred over keeping only rows currently matched to store items because historical full versions support:

- later forensic reconciliation,
- code-reuse investigation,
- price-history analysis,
- re-evaluation of old ambiguous mappings,
- detection of description/form/class changes,
- reconstruction of what catalogue evidence was available at a historical point.

The expected catalogue size is small for PostgreSQL even when many monthly versions are retained.

## Catalogue version entity

Candidate fields:

- `catalogue_version_id`
- source/effective date or catalogue period
- imported timestamp
- source filename or logical source label
- source file/content hash
- row count
- import status
- parser/importer version if needed
- optional note

A source hash should help detect accidental re-import of an identical catalogue file.

## Catalogue row entity

Store the source fields without destructive normalization.

Initial fields should mirror the verified catalogue columns, for example:

- CMS code
- brand name
- description
- form
- type
- class
- selling price
- source row number
- catalogue version identifier

Any normalized/search fields should be additional derived fields, not replacements for source text.

## Version uniqueness and idempotency

The import path must prevent accidental duplicate version creation when the same source file is submitted repeatedly.

Use source hash and explicit version metadata together; do not assume filename alone proves uniqueness.

A repeated identical import should return an idempotent `already imported` result unless the user explicitly requests a separate archival copy for a documented reason.

## Deterministic version diff

When a new catalogue version is imported, backend code should compute structured changes such as:

- new codes,
- codes no longer present,
- price changes,
- description changes,
- form/type/class changes,
- potential code-reuse or identity-shift candidates.

AI should review ambiguous semantic changes, not manually compare thousands of rows that code can compare exactly.

## Local inventory mapping

Keep mappings separate from catalogue rows.

A mapping should be able to record:

- local product or lot identity,
- catalogue version/row used as evidence,
- CMS code,
- mapping decision/status,
- confidence/review class where useful,
- evidence/operation/audit reference,
- validity dates or supersession relationship if needed.

Never make `cms_code` the local product primary key.

## Code reuse

When the same CMS code has materially incompatible identity across catalogue versions:

- preserve both historical catalogue rows,
- do not silently propagate the newest identity backward,
- flag linked local mappings for deterministic/AI review according to the MSA SAFE/REVIEW/CONFLICT model,
- preserve historical receipt identity snapshots and transaction history.

## Current catalogue projection

The operational Google workbook may continue to show only the latest active `CMS_Price_List_YYYYMM` tab.

Older full catalogue versions may be removed from the live workbook only under the workbook lifecycle policy, because the database will provide durable catalogue history after migration.

Until database archival is verified and promoted, the current skill's existing tab-retention rules remain authoritative.

## Current-price synchronization

A new catalogue version does not automatically authorize every local price/mapping change.

The backend should:

1. import the full catalogue version,
2. calculate exact structural diffs,
3. identify store-linked products/lots affected by changed catalogue evidence,
4. auto-apply only changes that meet explicit SAFE rules,
5. send ambiguous identity changes to review,
6. preserve receipt/historical prices separately from current catalogue price.

Historical transaction prices must never be overwritten merely because the current catalogue price changed.

## Historical price queries

The versioned catalogue should support questions such as:

- what was the catalogue selling price for code X in a given version,
- when did a price first change,
- how did the description/form/class change over time,
- which current store items are linked to a changed code,
- which historical receipt mapping used a prior catalogue identity.

## Google Sheet role

Google Sheets remains useful for human inspection of the current catalogue and for transitional reconciliation.

The full historical catalogue archive belongs in PostgreSQL once the database is promoted; the live workbook does not need to become a large historical catalogue warehouse.
