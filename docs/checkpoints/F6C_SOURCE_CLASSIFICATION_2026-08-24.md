# F6C Source Classification Checkpoint — 2026-08-24

Status: **SOURCE PASS RECORDED — NO RUNTIME/SCHEMA/INVENTORY MUTATION**

## Evidence used

- authorized live `Medicine Store Cloud` Google Sheet;
- representative `FORMULA` reads of `Main Stock!A:U` and `Daily Usage!A:AM`;
- current CMS price-list and batch staging structures;
- `Audit_Log` structure;
- canonical `skills/medicine-store-assistant/SKILL.md` and task references;
- Owner-confirmed role of This Month Received, Reorder Form, Final Reorder Form and Master archive.

## Important source finding

The live Google Sheet returns materialized values rather than formula strings for representative Main Stock and Daily Usage derived cells. Therefore:

- Google Sheet is strong evidence for current operational structure and values;
- it is not sufficient evidence for exact legacy Excel formula/macro implementation;
- derived business semantics already locked by the MSA skill may be used as the operational contract;
- exact legacy reorder/month-close macro details remain open when they materially affect canonical semantics.

## Locked classifications

### Main Stock

Current A:U operational projection has been classified field-by-field into:

- canonical product/lot/config/mapping evidence;
- receipt/event-backed projections;
- deterministic current-balance/monthly/reorder outputs;
- display/helper fields.

Multiple expiry rows sharing one CMS Serial Code confirm the separation:

`product != lot != CMS catalogue identity`.

### Daily Usage

Locked as a monthly spreadsheet/pivot view over normalized usage events.

Established workflow remains:

`Main Stock base/structure -> Daily Usage A:D/expiry projection -> Day 1-31 actual usage -> monthly usage/current balance -> Main Stock projection`.

The future canonical command is date/lot/store based, not day-column based.

### CMS / batch / audit

- CMS catalogue is versioned external identity/price evidence.
- transfer/batch evidence maps to receipt batch + receipt line + lot resolution.
- repeated historical sources must not double-intake.
- current catalogue price remains separate from historical receipt price.
- significant operations require durable audit/read-back semantics.

### Derived legacy surfaces

Owner-confirmed as lower-priority projection/output concerns:

- This Month Received — filtered receipt projection;
- Reorder Form — filtered calculated-reorder projection;
- Final Reorder — manually adjustable final working/submission output;
- Master Data archive — historical final-output snapshot/archive.

They do not require independent canonical inventory tables.

## Open F6C items

1. Store/location semantics for one Main Store plus unlimited Sub Stores.
2. Exact month rollover/carry-forward behavior that changes canonical state.
3. Exact reorder calculation logic/rounding where backend parity is required.
4. Remark/config ownership and scope where ambiguous.
5. Original Excel macro details only where needed to reproduce business semantics or historical exports.

## Boundary

No schema migration, database promotion, production stock write, Google Sheet mutation, or runtime deploy was performed by this checkpoint.
