# F6C — Workbook Parity Lock

Status: **CURRENT BOUNDED SLICE**

## Purpose

Close the gap between the existing Medicine Store Cloud / Excel workflow and the future canonical PostgreSQL inventory domain before any production database promotion.

The existing Google Sheet/source documents remain operationally authoritative throughout this slice. F6B remains test-only and must not be promoted.

Canonical companion architecture: `CONFIGURABLE_OPERATIONAL_VIEW_ENGINE.md`.

## Locked architectural direction

MSA will not reproduce every worksheet as a canonical database table.

The target is:

`canonical inventory domain -> typed field/computation registry -> configurable operational views -> draft/confirm/save -> typed domain commands`

Guiding rule:

> **Spreadsheet layout is configurable; inventory semantics are not arbitrary.**

This allows familiar Main Stock / Daily Usage workflows, custom spreadsheet-like tables, one Main Store plus unlimited Sub Stores, human staff and AI agents, and multiple clients without making any one UI or spreadsheet the source of truth.

## F6C priority

F6C should spend most effort on source behavior that determines canonical inventory semantics.

### Priority A — canonical/domain behavior

Lock from live source evidence and the existing MSA skill:

- local product identity vs expiry-specific lot identity;
- store/location scope and future Main Store/Sub Store behavior;
- Main Stock opening/base stock semantics;
- received stock / batch intake semantics;
- Daily Usage day-by-day movement semantics;
- current balance derivation;
- adjustments/corrections and actual-movement preservation;
- CMS catalogue identity, mapping, current price and historical-price separation;
- new expiry-lot insertion and sibling-lot behavior;
- fixed-asset boundary;
- reorder inputs/configuration and calculated recommendation semantics;
- month rollover/opening-balance carry-forward;
- audit/idempotency/read-back requirements.

### Priority B — operational view compatibility

Document enough layout behavior to reproduce the familiar human workflow without treating the layout itself as canonical data.

#### Main Stock

Classify each production column as one of:

- entity/domain field;
- computed field;
- command-backed editable field;
- display/helper field.

Preserve the existing view as a future preset.

#### Daily Usage

Treat the existing Day 1–31 layout as a monthly pivot/preset over normalized usage events.

Lock:

- structural/base synchronization meaning;
- day-cell editing semantics;
- monthly usage aggregation;
- current remaining calculation;
- expiry/remark compatibility;
- actual non-FIFO movement preservation.

### Priority C — projection/archive surfaces

`This Month Received`, `Reorder Form`, `Final Reorder Form` and Master/archive formatting are lower-priority schema concerns.

Current Owner-confirmed semantics:

- **This Month Received** — filtered/derived rows from Main Stock received-stock activity for convenient display/archive.
- **Reorder Form** — filtered/derived projection of Main Stock calculated `Estimated Reorder Qty`.
- **Final Reorder Form** — copied working output that the Owner may manually adjust before submission.
- **Master Data archive** — preserves the approved/final monthly output through the legacy macro workflow.

These should normally be modeled as views, generated working documents and approved snapshots/archives rather than independent canonical inventory tables.

F6C needs to preserve their business meaning, but it must not let their legacy worksheet structure drive the canonical schema.

## Current Google Sheet evidence

The live `Medicine Store Cloud` is an operational subset of the fuller local Excel workflow.

Observed user-facing/support surfaces include:

- `Main Stock`
- `Daily Usage`
- `Fixed Assets`
- versioned `CMS_Price_List_YYYYMM`
- `Audit_Log`
- preserved `CMS_Batch_<TRANSFER>_<DATE>` tabs

The existing MSA skill already encodes important compatibility behavior for Main Stock, Daily Usage, batch intake, CMS matching/pricing, fixed assets, visual marking and tab lifecycle. F6C must treat that skill as source-backed operational knowledge rather than re-inventing those rules.

## Deliverables

1. `WORKBOOK_PARITY_MATRIX.md` — source surface/field -> domain meaning -> field class -> future canonical/projection mapping.
2. `WORKBOOK_FUNCTION_CONTRACT.md` — behavioral rules for Main Stock, Daily Usage, intake, price/mapping, reorder/month rollover and relevant archive outputs.
3. `CONFIGURABLE_OPERATIONAL_VIEW_ENGINE.md` — canonical domain/view/edit boundary.
4. Gap list classified as:
   - already represented correctly in current schema;
   - schema/domain adjustment required;
   - configurable view/projection only;
   - approved snapshot/archive output;
   - unresolved and Owner review required.
5. Fresh real-source shadow-import plan derived from the locked contract.

## Acceptance

F6C is complete only when:

- canonical product, lot, store/location, receipt, usage, catalogue, adjustment and audit semantics are explicit;
- Main Stock and Daily Usage can be explained as projections/edit surfaces over canonical data;
- every current operational column is classified by semantic field type;
- derived/archive tabs are accounted for without being over-modeled;
- the future database can explain how each important workbook input/output is represented or generated;
- unresolved gaps are explicit rather than guessed;
- no production store mutation or canonical DB promotion occurred.

## Next slice after F6C

**F6D — Canonical Inventory Schema Parity + Fresh Shadow Import**

Implement only the schema/domain changes proven necessary by F6C, then perform a fresh non-canonical shadow import against an authorized current source snapshot with reconciliation and read-back evidence.

Do not reuse F6B as an accepted migration baseline merely because it already contains data.

The full configurable table-builder UI is not part of F6D. First prove canonical domain correctness and Main Stock/Daily Usage projections, then add the reusable view-definition substrate and later spreadsheet-like editing.