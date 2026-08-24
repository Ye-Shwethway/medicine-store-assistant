# Medicine Store Assistant — Project Roadmap

Status: **AI Workspace is an accepted supporting foundation. PostgreSQL remains non-canonical. F6C has been realigned around the Canonical Inventory Foundation; exact reorder/monthly Excel formula parity is no longer an F6D blocker. Next bounded implementation target: F6D Canonical Inventory Schema Parity + Fresh Shadow Import.**

The live Google workbook/source documents remain operationally authoritative. `migration_baseline_accepted=false`; `database_canonical=false`.

## Product direction — LOCKED

MSA is not a fixed spreadsheet clone and not an AI-only application.

Target product:

- one Main Store plus unlimited Sub Stores;
- durable PostgreSQL-backed inventory truth;
- human staff and AI agents working through the same typed operation layer;
- Web, Flutter, Telegram, ChatGPT and automation clients over the same backend;
- persistent operation with or without ChatGPT/Google Sheets;
- spreadsheet-like operational tables that may use presets or user-defined layouts;
- dynamic AI/rule-based inventory intelligence layered on top of canonical stock history.

Core rules:

> **Spreadsheet layout is configurable; inventory semantics are not arbitrary.**

> **Stock belongs to a location; product and catalogue identity do not.**

> **Store quantity truth comes from movements; totals and operational quantity columns are projections of that truth.**

Canonical foundation:

`Product -> Lot -> Store -> Movement -> Balance -> Transfer -> CMS Mapping -> Actor/Audit`

Canonical architecture docs:

- `docs/architecture/CANONICAL_INVENTORY_FOUNDATION.md`
- `docs/architecture/STORE_LOCATION_MODEL.md`
- `docs/architecture/CONFIGURABLE_OPERATIONAL_VIEW_ENGINE.md`

## Delivery policy

`branch -> PR -> main -> automatic VPS deploy for relevant runtime changes -> runtime evidence -> continuity docs`

## Canonicality / authority boundary

- Google Sheet/source documents = current operational source of truth.
- PostgreSQL = deployed shadow/test database, **not canonical**.
- Existing F6B snapshot is test evidence only and must not be silently promoted.
- No production inventory writes, transfers, Calculator deductions, Telegram/Flutter stock mutations, automatic OCR/vision commit, arbitrary agent SQL/DB mutation, or DB canonical promotion are authorized.
- Provider/model selection never grants authority; participant privileges never union.

## Accepted AI Workspace foundation

D4.8/D4.9, external MCP federation, Review discussion, Owner Decisions, Web Production Reliability Hardening and `Talk to -> All agents` remain accepted supporting foundations.

Small Review UI polish may be folded into later touched Web work. Do not keep extending AI collaboration as the immediate product focus.

## CURRENT — F6C Canonical Inventory Foundation / Workbook Semantics Lock

### Locked core

- Product = stable local operational identity.
- Lot = normal v1 Product + expiry operational identity.
- Store/Location = one Main Store plus unlimited Sub Stores.
- Balance = derived per `(store_id, lot_id)` from canonical movements.
- Total Store Stock = sum of location balances, not an independent editable truth.
- External receipt and internal transfer are distinct event classes.
- Internal transfer preserves Product/Lot identity and atomically creates source-out + destination-in effects.
- Usage/deduction belongs to the actual issuing store.
- CMS catalogue is global/versioned and separate from local Product identity.
- Product-to-CMS mapping is auditable/version-aware; CMS code alone is never canonical identity.
- current catalogue price is distinct from historical receipt/source price.
- human/AI operations resolve stable actor identity, operation/idempotency ID, audit and read-back.
- Main Stock and Daily Usage are operational projections/edit surfaces over canonical data.

### Operational inventory view direction

Useful inventory columns may include:

`Local Item Name | CMS Name | Type | Unit | CMS Code | Expiry Date | Original/Opening Qty | Received Qty | Deducted/Used Qty | Current Qty | CMS Price | Store/Location`

`No.` is view/order metadata only.

Opening, received, deducted and current quantities are not separate mutable inventory truths. They are source fields or movement aggregates according to their semantics.

### Reorder / calculation realignment

Exact legacy `Estimated Reorder Qty` formula, threshold and rounding parity is **deprioritized and does not block F6D**.

Future reorder is a dynamic workflow/intelligence layer that may combine usage history, trends, expiry risk, safety stock, lead time, incoming stock, store-specific demand, deterministic rules, AI proposals, agent review and human approval/adjustment.

F6D only needs to preserve the canonical stock/history/configuration data required for those workflows.

### Monthly Excel compatibility realignment

Exact reset formulas/macros and archive formatting are later compatibility work unless a specific behavior changes canonical stock identity, quantity, provenance, transfer semantics or audit truth.

Opening/migration balance provenance remains foundational.

## NEXT — F6D Canonical Inventory Schema Parity + Fresh Shadow Import

Implement the minimum schema foundation proven by F6C:

1. canonical `stores` identity and one configured Main Store;
2. location-aware stock movements;
3. Product/Lot identity preserved independently of location;
4. receipt provenance and destination location;
5. explicit internal transfer header/lines or equivalent paired atomic semantics;
6. Universal CMS Catalogue versioning + auditable Product mapping;
7. location-aware balance queries/aggregation;
8. actor/audit/idempotency coverage for inventory operations;
9. only the minimum additional snapshot/config structures required for the fresh import and projection proof;
10. fresh authorized source snapshot bound to Main Store;
11. repeatable non-canonical import with provenance;
12. reconciliation of Product/Lot identity, opening stock, receipts, usage, CMS mapping/price and current balances;
13. proof that Main Stock and Daily Usage views can be generated from DB state;
14. explicit mismatch classification with PostgreSQL still non-canonical.

The existing F6B data is not the F6D migration baseline.

## Subsequent inventory/database path

1. **F6C — CURRENT:** complete documentation alignment and any remaining genuinely foundational Owner decisions.
2. **F6D:** canonical inventory schema parity + fresh shadow import.
3. Historical bootstrap from strongest available evidence without fabricating movements.
4. Shadow balance/projection parity and transfer tests.
5. Minimal field/computation registry + saved view-definition substrate.
6. Main Stock/Daily Usage DB-backed preset views.
7. Spreadsheet-like draft/confirm/save editing over typed commands.
8. Dynamic reorder / trend / AI proposal-review workflows.
9. Dual verification of real operational events against the live workbook.
10. Selected DB read-path promotion after repeated parity.
11. Controlled write promotion one operation class at a time.
12. Explicit database canonicality promotion only after migration, recovery, reconciliation and controlled-write gates pass.
13. Sheet mirror/rebuild, monthly exports, Flutter/Telegram expansion and further AI workflows.

## Deferred supporting work

Exact legacy reorder formula reconstruction, cosmetic Excel macro parity, broader AI collaboration modes, Telegram Attention delivery, GROUP/COMPARE/DEBATE and speculative intelligence features do not block the canonical inventory foundation.

## Immediate boundary

Continue re-reading the live Google Sheet whenever source structure/value behavior matters, but do not let legacy spreadsheet calculation mechanics dictate the new database architecture.

The immediate implementation target is the canonical inventory foundation, not formula replication and not additional AI surface area.
