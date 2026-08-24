# CMS Catalogue Versioning

Status: **F6D live shadow catalogue ingestion is runtime-verified for versioned reference data. Local Product-CMS mapping, operational-price propagation, and production DB authority remain separately gated and are not authorized by catalogue import.**

## Purpose

Preserve complete CMS catalogue history without making CMS Code the local Product identity or silently synchronizing local inventory state.

The catalogue domain is separate from local inventory because CMS codes/descriptions may change, disappear, retire, be reused, or conflict with historical/local mapping evidence.

Canonical mapping lifecycle companion: `CMS_MAPPING_LIFECYCLE.md`.

## Full-version archive

Each imported catalogue version is stored in full. Historical versions support forensic reconciliation, code-reuse investigation, price history, re-evaluation of ambiguous mappings, detection of identity-field changes, and reconstruction of the catalogue evidence available at a historical point.

## Catalogue version entity

Fields include:

- `catalogue_version_id`;
- `effective_date`;
- `source_hash`;
- `source_label`;
- `imported_at`;
- `row_count`;
- `import_status`;
- `parser_version`;
- optional `note`.

`source_hash` is unique so identical source content cannot create duplicate catalogue history.

## Catalogue row entity

Source-preserving fields include CMS code, brand name, description, form, type, class, selling price, source row number and catalogue version ID. Normalized/search fields may be added later as derived fields; they must not replace source text.

## Version uniqueness and idempotency

A deterministic SHA-256 hash is computed over source-preserving catalogue rows. Re-importing identical content returns the existing catalogue version rather than creating another version.

### First real live shadow version — VERIFIED

The current live catalogue was imported into shadow PostgreSQL as reference data:

- sheet: `CMS_Price_List_202608`;
- source title: `August 2026 Updated Price List (Yuan) - 02.08.2026`;
- effective date: `2026-08-02`;
- source hash: `6f221152024c9a06b73f7f7115097abfb688a37a6ba6bf0be78345f3b70dd116`;
- catalogue version: `34947c29-6427-4b7c-9fb8-ba8ffe3278b0`;
- row count: **6,891**;
- unique CMS codes: **6,891**;
- duplicate codes: **0**;
- blank codes: **0**;
- invalid prices: **0**;
- one blank selling-price source row: row `6442`, code `S10105035`, preserved as database `NULL` rather than inferred.

Immediate replay returned the same catalogue version with `created=false` and the same 6,891 rows.

The import used an exact expected-source-hash guard and post-import readback.

## Local-domain isolation proof

The live catalogue import did not change local inventory or mapping counts. Before and after import:

- Products: **670**;
- Lots: **799**;
- inventory transactions: **679**;
- Product-CMS mappings: **0**.

Therefore catalogue ingestion is proven to be a **reference-data operation**, not a local mapping/price/inventory mutation.

## Deterministic version diff

Version comparison may report:

- new codes;
- codes no longer present;
- price changes;
- brand/description/form/type/class changes;
- potential identity-shift/code-reuse candidates.

Identity-sensitive differences are review evidence only. They do not automatically mutate local Product identity or accepted Product-CMS mapping.

## Local inventory mapping

Mappings remain separate from catalogue rows.

**A catalogue import never creates or accepts a Product-CMS mapping.**

Never make `cms_code` the local Product primary key and never interpret code equality alone as proof of local identity.

The next F6D step is assisted reconciliation: deterministic screening first, optional AI reasoning later, human acceptance in a separately authorized persistence slice.

## Code reuse and ambiguous local state

When a CMS code appears incompatible with local/historical identity evidence:

- preserve catalogue evidence;
- preserve prior accepted/local mapping history;
- flag the relation for review;
- do not silently propagate current identity backward;
- do not automatically remap a Product/Lot;
- preserve historical receipt identity and transaction history.

The live workbook contains `Recycled ID` evidence and same-code local states that may reflect historical mapping, catalogue change, or local staff error. The system must preserve that uncertainty rather than asserting reuse solely from a mismatch.

## CMS discontinued while local stock remains

Catalogue lifecycle and local inventory lifecycle are independent. A disappeared/discontinued CMS item does not delete or invalidate a local Product/Lot. Historical mapping evidence remains, replacement is not forced, and local stock may remain usable under store policy.

## Current-price synchronization

A new catalogue version does not authorize local price or mapping changes.

Any future local price update must separately prove accepted mapping compatibility and follow review/confirmation/audit rules. Code equality alone is insufficient, and historical receipt/source prices must never be overwritten merely because a current catalogue selling price changed.

## Last accepted state / AI outage behavior

If a newer catalogue remains unreconciled, including during AI outage:

- ordinary inventory operation continues;
- accepted mappings remain available;
- last accepted operational prices remain available;
- unresolved new mappings remain review-required/unmapped;
- manual reconciliation remains possible;
- no working mapping is erased merely because a newer catalogue version exists.

AI is preferred assistance for ambiguous matching, not an operational dependency.

## Authority boundary

The live workbook/source evidence remains operationally authoritative until explicit database promotion after shadow/dual validation.

The verified shadow catalogue version changes neither `database_canonical=false` nor `migration_baseline_accepted=false`. It authorizes neither accepted mapping writes nor production price propagation.