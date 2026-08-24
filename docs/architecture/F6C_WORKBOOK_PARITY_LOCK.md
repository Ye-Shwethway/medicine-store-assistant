# F6C — Workbook Parity Lock

Status: **CURRENT BOUNDED SLICE**

## Purpose

Close the gap between the existing Medicine Store Cloud / Excel workflow and the future canonical PostgreSQL inventory domain before any production database promotion.

The existing Google Sheet/source documents remain operationally authoritative throughout this slice. F6B remains test-only and must not be promoted.

## Why this slice exists

The current shadow database proves infrastructure and selected migration mechanics, but it does not yet prove full parity with the real workbook structure and functions.

The database design already assumes that Main Stock, Daily Usage, This Month Received, Reorder / Final Reorder, CMS catalogue history, month-close behavior, and legacy Excel compatibility are projections or workflows over canonical domain data. Before implementation can safely continue, those source behaviors must be captured exactly enough that the backend can reproduce them without inventing replacements.

## Source contract to lock

### Main Stock

Document from the real workbook/source evidence:

- exact production columns and their meanings;
- which cells/columns are human input, formula-derived, lookup-derived, or integration-managed;
- local product identity vs expiry-lot presentation;
- CMS Code / Serial / CMS Price / Price behavior and current formula dependencies;
- received/current stock/monthly usage/reorder-related fields;
- row insertion, removal, reorder, naming and expiry-suffix behavior;
- formatting or helper metadata that has workflow meaning.

### Daily Usage

Lock:

- exact A:D/base-field synchronization behavior;
- Day 1–31 structure and editing semantics;
- monthly total and remaining/current balance formulas;
- remark and expiry behavior;
- how multiple physical issues on the same day/lot are represented;
- month rollover/reset/archive behavior;
- non-FIFO literal recording compatibility.

### This Month Received

Lock:

- exact source columns;
- filter/inclusion rule from Main Stock / receipt evidence;
- whether any user-authored information exists beyond projection;
- month reset/archive behavior.

### Reorder / Final Reorder

Lock the actual current algorithm rather than designing a new one:

- source inputs from Main Stock;
- exact formulas/thresholds/rounding;
- working Reorder generation;
- Final Reorder copy/edit/submission behavior;
- approved manual edits and how they differ from calculated recommendation;
- monthly archive behavior.

### CMS catalogue / transfer intake

Lock:

- active catalogue sheet structure and retention behavior;
- code/serial/name/price identity rules;
- recycled/retired/new CMS code handling;
- transfer/batch input structure;
- mapping, new expiry-lot and NEW_UNMAPPED behavior.

### Monthly lifecycle / Excel compatibility

Lock:

- opening balance carry-forward;
- month close sequence;
- Master/archive workbook behavior;
- sheet reset/copy operations;
- formulas/macros that still represent required business behavior;
- outputs that must be reproducible from a future canonical database.

## Deliverables

1. `WORKBOOK_PARITY_MATRIX.md` — source surface -> exact fields/formulas/actions -> future domain entity/projection mapping.
2. `WORKBOOK_FUNCTION_CONTRACT.md` — behavioral rules for Main Stock, Daily Usage, This Month Received, Reorder/Final Reorder and month close.
3. Gap list classified as:
   - already represented correctly in current schema;
   - schema/domain adjustment required;
   - projection/export only;
   - unresolved and Owner review required.
4. Fresh real-source shadow-import plan derived from the locked contract.

## Acceptance

F6C is complete only when:

- every operational workbook surface above is accounted for;
- no current formula/macro/business behavior required for operations is silently omitted;
- identity mapping distinguishes product, lot and CMS catalogue identity;
- the future database can explain how each workbook input/output is represented or generated;
- unresolved gaps are explicit rather than guessed;
- no production store mutation or canonical DB promotion occurred.

## Next slice after F6C

**F6D — Canonical Inventory Schema Parity + Fresh Shadow Import**

Implement only the schema/domain changes proven necessary by F6C, then perform a fresh non-canonical shadow import against an authorized current source snapshot with reconciliation and read-back evidence.

Do not reuse F6B as an accepted migration baseline merely because it already contains data.
