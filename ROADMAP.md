# Medicine Store Assistant — Project Roadmap

Status: **AI Workspace / D4.8-D4.9 is an accepted supporting foundation. F6B remains test-only; PostgreSQL remains non-canonical. F6C core field semantics and Store/Location model are now locked; remaining blockers are month rollover semantics and exact legacy reorder calculation. F6D follows after those gates are resolved or explicitly bounded.**

The live Google workbook/source documents remain operationally authoritative. `migration_baseline_accepted=false`; `database_canonical=false`.

## Product direction — LOCKED

MSA is not a fixed spreadsheet clone and not an AI-only application.

Target product:

- one Main Store plus unlimited Sub Stores;
- durable PostgreSQL-backed inventory truth;
- human staff and AI agents working through the same typed operation layer;
- Web, Flutter, Telegram, ChatGPT and automation clients over the same backend;
- persistent operation with or without ChatGPT/Google Sheets;
- spreadsheet-like operational tables that may use presets or user-defined column layouts.

Core rule:

> **Spreadsheet layout is configurable; inventory semantics are not arbitrary.**

Architecture:

`canonical inventory domain -> field/computation registry -> configurable operational views -> draft/confirm/save -> typed domain commands -> audit/read-back`

Human UI edits and AI-agent MSA actions converge on the same authorized typed backend command layer. Neither receives raw SQL authority.

Canonical companion architecture: `docs/architecture/CONFIGURABLE_OPERATIONAL_VIEW_ENGINE.md`.

## Delivery policy

`branch -> PR -> main -> automatic VPS deploy for relevant runtime changes -> issue #26 runtime evidence -> continuity docs`

## Canonicality / authority boundary

- Google Sheet/source documents = current operational source of truth.
- PostgreSQL = deployed shadow/test database, **not canonical**.
- Existing F6B snapshot is test evidence only and must not be silently promoted.
- No production inventory writes, transfers, Calculator deductions, Telegram/Flutter stock mutations, automatic OCR/vision commit, arbitrary agent SQL/DB mutation, or DB canonical promotion are authorized.
- Provider/model selection never grants authority; participant privileges never union.

## Accepted AI Workspace foundation

D4.8/D4.9, external MCP federation, Review thread discussion, Owner Decisions, export/delete UX and Web Production Reliability Hardening are accepted foundations.

PR #129 added ordinary Review-thread `Talk to -> All agents` broadcast while keeping full `Send review` separate. Production deploy evidence:

- source SHA `75bfb89eb83b5cedfffa9148db454b1245269593`
- workflow run `32736647711`
- issue #26 `status=success`

Small Review UI polish may be folded into later touched Web work. Do not keep extending AI collaboration as the immediate product focus.

## CURRENT — F6C Workbook / Domain Parity Lock

Canonical architecture:

- `docs/architecture/F6C_WORKBOOK_PARITY_LOCK.md`
- `docs/architecture/CONFIGURABLE_OPERATIONAL_VIEW_ENGINE.md`
- `docs/architecture/STORE_LOCATION_MODEL.md`
- `docs/architecture/WORKBOOK_PARITY_MATRIX.md`
- `docs/architecture/WORKBOOK_FUNCTION_CONTRACT.md`

### Locked during F6C

- Main Stock field semantics and product/lot identity.
- Daily Usage Day 1–31 as a monthly pivot/edit surface over normalized usage events.
- CMS catalogue identity/mapping/current price vs historical receipt-price separation.
- Batch intake, idempotency, new expiry-lot and fixed-asset-routing semantics.
- `This Month Received` / Reorder Form / Final Reorder / Master archive treatment as projection, working output, or snapshot rather than canonical inventory tables.
- configurable operational-view boundary.
- one Main Store plus unlimited Sub Stores with shared Product/Lot identity and location-scoped stock.
- internal transfer as one atomic typed operation with linked source and destination ledger effects.

### Store/Location schema gap proven

Current shadow migrations have no canonical store/location entity and `inventory_transactions` is lot-only. Therefore F6D must add location-aware inventory state before multi-store canonicality.

The current live `Medicine Store Cloud` contains no populated Store/Location/Sub Store field in Main Stock/Daily Usage. Treat it as the configured legacy Main Store context during migration rather than changing its production columns.

### Remaining F6C blockers

1. Month rollover/carry-forward semantics that affect canonical monthly state.
2. Exact legacy reorder calculation/threshold/rounding needed for parity.

Exact cosmetic workbook formatting and report-only macro behavior do not block F6D unless they change inventory meaning or historical reconstruction requirements.

## NEXT — F6D Canonical Inventory Schema Parity + Fresh Shadow Import

After F6C acceptance:

1. add canonical Store/Location identity and bind the legacy workbook source to the configured Main Store;
2. make balance-changing movements location-aware;
3. add receipt destination location and explicit internal transfer representation;
4. make monthly snapshot rows store+lot scoped while keeping the shared calendar month concept where appropriate;
5. preserve a path for store-scoped reorder configuration;
6. adjust only other schema/domain pieces proven necessary by parity analysis;
7. take a fresh authorized source snapshot;
8. perform a repeatable non-canonical shadow import;
9. reconcile identities, expiry lots, opening/base stock, receipt totals, usage, CMS mapping/price and balances;
10. prove Main Stock and Daily Usage projections can be generated from the DB for the Main Store context;
11. keep unresolved mismatches explicit and remain non-canonical until accepted.

The existing F6B data is not the F6D migration baseline.

## Subsequent inventory/database path

1. **F6C — CURRENT:** close month/reorder parity gates.
2. **F6D:** location-aware canonical schema parity + fresh shadow import.
3. Historical bootstrap from strongest available evidence without fabricating transactions.
4. Shadow calculation parity for balances, receipts, usage, CMS data, month outputs and reorder.
5. Minimal field/computation registry + saved view-definition substrate.
6. Main Stock/Daily Usage DB-backed preset views.
7. Spreadsheet-like draft/confirm/save editing over typed commands.
8. Dual verification of real operational events against the live workbook.
9. Selected DB read-path promotion only after repeated parity.
10. Controlled write promotion one operation class at a time with idempotency, authorization, confirmation, audit and read-back.
11. Explicit database canonicality promotion only after migration, backup/restore, month-close/reorder and Sheet-mirror parity are proven.

## Deferred supporting work

Telegram Attention delivery, GROUP, COMPARE, DEBATE, broader vision/OCR and additional AI collaboration features remain later work unless explicitly reprioritized. They must not block the core inventory/database migration path.

## Immediate boundary

Continue using the live workbook plus the established MSA skill as source-backed operational evidence. Do not infer exact reorder or month-close behavior from materialized Google Sheet values alone. No production inventory mutation or PostgreSQL canonical promotion is authorized in F6C/F6D until the explicit acceptance gates are met.
