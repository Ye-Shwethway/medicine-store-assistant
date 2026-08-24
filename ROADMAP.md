# Medicine Store Assistant — Project Roadmap

Status: **AI Workspace is an accepted supporting foundation. PostgreSQL remains non-canonical. F6C Canonical Inventory Foundation is aligned; reorder resilience and CMS assisted-mapping lifecycle are now part of the locked architecture. Next bounded implementation target: F6D Canonical Inventory Schema Parity + Fresh Shadow Import.**

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
- deterministic fallback workflows where AI unavailability would otherwise block essential store work;
- AI-assisted reconciliation/analysis layered on top of durable accepted state.

Core rules:

> **Spreadsheet layout is configurable; inventory semantics are not arbitrary.**

> **Stock belongs to a location; product and catalogue identity do not.**

> **Store quantity truth comes from movements; totals and operational quantity columns are projections of that truth.**

> **AI enhances store operation but must not become a single point of operational failure.**

Canonical foundation:

`Product -> Lot -> Store -> Movement -> Balance -> Transfer -> CMS Mapping -> Actor/Audit`

Canonical architecture docs:

- `docs/architecture/CANONICAL_INVENTORY_FOUNDATION.md`
- `docs/architecture/STORE_LOCATION_MODEL.md`
- `docs/architecture/CMS_MAPPING_LIFECYCLE.md`
- `docs/architecture/REORDER_BASELINE_AND_AI_ENHANCEMENT.md`
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

### Reorder resilience — LOCKED

Exact legacy `Estimated Reorder Qty` formula, threshold and rounding parity is **not an F6D blocker**, but reorder must not depend entirely on AI.

The future reorder subsystem has two layers:

1. deterministic baseline calculation available entirely from local/backend structured data;
2. optional AI/advanced analysis that enhances/reviews the baseline.

If all AI providers are unavailable, users still receive a baseline recommendation and may manually review/adjust it rather than recalculating every item from scratch.

The deterministic strategy can evolve/version independently of canonical inventory identity. AI may later add usage-trend interpretation, expiry risk, seasonality, cross-store context and multi-agent review.

Canonical contract: `docs/architecture/REORDER_BASELINE_AND_AI_ENHANCEMENT.md`.

### CMS assisted mapping — LOCKED

CMS mapping is not direct code synchronization.

The local store uses a small operational subset of a much larger CMS catalogue, names often differ, CMS codes may retire/reuse, and live workbook evidence contains recycled/discontinued/ambiguous mapping states.

Core rule:

> **CMS mapping is never blindly auto-synced. Last accepted mapping and price state remain usable until a newer mapping is reviewed and accepted.**

New catalogue versions are diffed and screened deterministically. Ambiguous/new/recycled/discontinued mappings enter review. AI is the preferred assistance layer for difficult matching, but when AI is unavailable the user can manually map/review while existing accepted mappings and last accepted prices continue to operate.

A newer unresolved catalogue must not erase a working prior mapping or force a zero/new price.

Canonical contract: `docs/architecture/CMS_MAPPING_LIFECYCLE.md`.

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
6. Universal CMS Catalogue versioning + historical/auditable Product mapping lifecycle;
7. retention of last accepted CMS mapping/price state across unresolved newer catalogue versions;
8. location-aware balance queries/aggregation;
9. actor/audit/idempotency coverage for inventory and mapping operations;
10. only the minimum additional snapshot/config structures required for the fresh import and projection proof;
11. fresh authorized source snapshot bound to Main Store;
12. repeatable non-canonical import with provenance;
13. reconciliation of Product/Lot identity, opening stock, receipts, usage, CMS mapping/price and current balances;
14. proof that Main Stock and Daily Usage views can be generated from DB state;
15. explicit mismatch classification with PostgreSQL still non-canonical.

F6D does not need the final semantic/AI CMS matcher or full reorder engine. It must persist the state those later workflows require without redesign.

The existing F6B data is not the F6D migration baseline.

## Subsequent inventory/database path

1. **F6C — CURRENT:** documentation aligned around durable inventory, reorder fallback and assisted CMS mapping.
2. **F6D:** canonical inventory schema parity + fresh shadow import.
3. Historical bootstrap from strongest available evidence without fabricating movements.
4. Shadow balance/projection parity and transfer tests.
5. Minimal field/computation registry + saved view-definition substrate.
6. Main Stock/Daily Usage DB-backed preset views.
7. Spreadsheet-like draft/confirm/save editing over typed commands.
8. Deterministic reorder baseline engine + configuration/version attribution.
9. CMS assisted reconciliation workflow + optional AI candidate reasoning.
10. AI-enhanced reorder/trend proposal-review workflows.
11. Dual verification of real operational events against the live workbook.
12. Selected DB read-path promotion after repeated parity.
13. Controlled write promotion one operation class at a time.
14. Explicit database canonicality promotion only after migration, recovery, reconciliation and controlled-write gates pass.
15. Sheet mirror/rebuild, monthly exports, Flutter/Telegram expansion and further AI workflows.

## Deferred supporting work

Exact legacy reorder formula reconstruction, cosmetic Excel macro parity, broader AI collaboration modes, Telegram Attention delivery, GROUP/COMPARE/DEBATE and speculative intelligence features do not block the canonical inventory foundation.

## Immediate boundary

Continue re-reading the live Google Sheet whenever source structure/value behavior matters, but do not let legacy spreadsheet calculation mechanics dictate the new database architecture.

The immediate implementation target is the canonical inventory foundation, with CMS mapping lifecycle persisted safely enough for later manual/AI-assisted reconciliation.
