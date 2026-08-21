# CMS Catalogue Versioning

Status: **F5 implementation active; synthetic/non-sensitive verification only; live catalogue ingestion not authorized**

## Purpose

Preserve complete CMS catalogue history without forcing the live Google workbook to carry every old price-list version forever.

The catalogue domain is separate from local inventory identity because CMS codes and descriptions may change, disappear, or be reused.

## Full-version archive

The database stores each imported CMS catalogue version in full. F5 proves this behavior with synthetic/non-sensitive fixtures only.

Historical full versions support:

- later forensic reconciliation,
- code-reuse investigation,
- price-history analysis,
- re-evaluation of old ambiguous mappings,
- detection of description/form/class changes,
- reconstruction of what catalogue evidence was available at a historical point.

## Catalogue version entity

Current F5 fields include:

- `catalogue_version_id`
- `effective_date`
- `source_hash`
- `source_label`
- `imported_at`
- `row_count`
- `import_status`
- `parser_version`
- optional `note`

`source_hash` is unique in F5 so an identical source cannot accidentally create duplicate catalogue history.

## Catalogue row entity

Current source-preserving fields include:

- CMS code
- brand name
- description
- form
- type
- class
- selling price
- source row number
- catalogue version identifier

Normalized/search fields, if later needed, must be additional derived fields rather than replacements for source text.

## Version uniqueness and idempotency

F5 computes a deterministic SHA-256 hash over the source-preserving catalogue row payload.

A repeated identical import returns the already-existing catalogue version rather than creating a duplicate. Filename/source label alone is not identity.

Live-file byte hashing/parsing policy may be refined only when a real catalogue-ingestion slice is separately authorized.

## Deterministic version diff

F5 computes structured differences for:

- new codes,
- codes no longer present,
- price changes,
- brand/description/form/type/class changes,
- potential code-reuse or identity-shift candidates.

Identity-sensitive changes are flagged for review; they do not automatically mutate local inventory identity.

## Local inventory mapping

Mappings remain separate from catalogue rows.

**F5 does not create or modify local product/lot mappings.**

Never make `cms_code` the local product primary key and never interpret code equality alone as proof of local identity.

## Code reuse

When the same CMS code has materially incompatible identity across versions:

- preserve both historical catalogue rows,
- flag the new row as an identity-shift candidate,
- do not silently propagate the newest identity backward,
- do not automatically remap a local product/lot,
- preserve historical receipt identity and transaction history.

The F5 synthetic verifier explicitly exercises this invariant.

## Current catalogue projection

The operational Google workbook may continue to show its existing CMS price-list tabs under the current skill/workbook rules.

F5 does not remove, import, rewrite, or synchronize any live Google Sheet catalogue tab.

## Current-price synchronization

A new catalogue version does not automatically authorize local price or mapping changes.

Future live synchronization must separately prove identity compatibility and honor SAFE/REVIEW/CONFLICT rules before any production update.

Historical transaction prices must never be overwritten merely because a current catalogue price changed.

## Historical price queries

The versioned catalogue is designed to support questions such as:

- what was the catalogue selling price for code X in a given version,
- when did a price first change,
- how did description/form/class change over time,
- which current store items are linked to a changed code,
- which historical receipt mapping used prior catalogue evidence.

F5 verifies version persistence and deterministic diff internally with synthetic data; it does not yet authorize or require a public production catalogue-write endpoint.

## Google Sheet role and authority

Google Sheets remains useful for human inspection and transitional reconciliation.

Until explicit database promotion after shadow/dual validation, the live Google workbook/source evidence remains authoritative. F5 catalogue versioning does not change that authority boundary.
