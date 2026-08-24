# Medicine Store Assistant — Implementation Plan

Status: **AI Workspace / D4.8-D4.9 is accepted. F6B remains test-only; PostgreSQL remains non-canonical. F6C core field semantics and Store/Location model are locked. Remaining F6C blockers: month rollover/carry-forward semantics and exact legacy reorder calculation. Next: F6D Canonical Inventory Schema Parity + Fresh Shadow Import.**

## 1. Global rules

- Google Sheets/source documents remain operationally authoritative until explicit canonical DB promotion.
- PostgreSQL being deployed does **not** make it canonical.
- F6B is test-only and must never be silently promoted.
- All humans, AI agents, integrations, and jobs use typed backend operations.
- Never expose arbitrary SQL, DB credentials, VPS shell/filesystem, Sheet credentials, plaintext provider keys, passwords/tokens/recovery secrets, or unrestricted HTTP proxying to AI/client runtimes.
- Deterministic backend code owns identity, authorization, constraints, idempotency, transactions, confirmation, read-back and audit semantics.
- Provider/model choice never grants authority; participant privileges never union.
- Significant implementation/deploy/next-work changes update `ROADMAP.md`, `NEW_CHAT_BOOTSTRAP.md`, this file, and relevant canonical docs.

## 2. Accepted supporting foundation

Accepted work includes Provider Registry, named agents, native inference, Single Chat, bounded read tools, D4.8 Work/Artifact/Review/Event/Attention substrate, external MCP federation, feedback passes, Review export/delete/navigation, Web Production Reliability Hardening, D4.9 discussion/Owner Decisions, and PR #129 `Talk to -> All agents` ordinary discussion broadcast.

PR #129 production evidence:

- source SHA `75bfb89eb83b5cedfffa9148db454b1245269593`
- deploy run `32736647711`
- issue #26 `status=success`

Small AI/Review cosmetic fixes may be folded into future Web touches; do not create another AI-only implementation branch unless required for correctness.

## 3. Product architecture direction — LOCKED

MSA is a canonical inventory domain with configurable spreadsheet-like operational views.

Core rule:

> **Spreadsheet layout is configurable; inventory semantics are not arbitrary.**

Canonical path:

`domain data/events -> typed field/computation registry -> preset/custom view -> draft edits -> validation/change preview -> Confirm & Save -> typed domain commands -> transaction -> audit/read-back`

Human Web/Flutter edits and AI-agent MSA actions converge on the same authorized typed backend command layer.

Canonical architecture:

- `docs/architecture/CONFIGURABLE_OPERATIONAL_VIEW_ENGINE.md`
- `docs/architecture/STORE_LOCATION_MODEL.md`

## 4. Canonicality / write boundary

- `database_canonical=false`.
- `migration_baseline_accepted=false`.
- Existing F6B shadow data is test evidence only.
- No production inventory write, transfer, Calculator deduction, Telegram/Flutter stock mutation, automatic OCR/vision commit, arbitrary agent DB/SQL mutation, or DB canonical promotion is authorized.

## 5. CURRENT — F6C Workbook / Domain Parity Lock

### 5.1 Locked core semantics

- Product is stable local identity.
- Lot is normally Product + expiry in v1.
- CMS catalogue identity is external/versioned and CMS code alone is never canonical identity.
- Main Stock is a stock/lot operational projection, not the DB table design.
- Daily Usage is a monthly Day 1–31 pivot/edit surface over normalized usage events.
- Receipt, usage and adjustment are typed canonical movements.
- `This Month Received`, Reorder Form and Final Reorder are projection/working/snapshot concerns rather than independent stock truth tables.
- Human UI and AI actions use the same typed backend command layer.

### 5.2 Store / Location — LOCKED CORE

Rule:

> **Stock belongs to a location; product and catalogue identity do not.**

Required semantics:

- exactly one configured Main Store and unlimited Sub Stores in v1;
- Product and normal Lot identities are shared across stores;
- balance is derived per `(store_id, lot_id)`;
- every balance-changing movement resolves a location;
- usage belongs to the actual issuing store;
- external receipt resolves a destination store;
- internal transfer is one atomic typed operation with linked source decrease + destination increase;
- internal transfer must not be represented as unrelated adjustments;
- month snapshots become store+lot scoped;
- operational view definitions are reusable with a store context/filter.

Current schema gap proven from migrations:

- no canonical stores/location table;
- `inventory_transactions` is lot-only;
- current movement types do not represent internal transfer.

The current `Medicine Store Cloud` has no populated Store/Location/Sub Store field in Main Stock/Daily Usage. F6D migration binds that workbook to the configured Main Store rather than changing its production columns.

### 5.3 Remaining F6C work

Only behavior that can change canonical meaning remains blocking:

1. **Month rollover/carry-forward**
   - prior closing balance -> next opening/base state;
   - reset semantics for monthly receipts/usage/day-grid projections;
   - snapshot timing and close authority;
   - store-scoped month behavior.
2. **Exact reorder calculation**
   - approved inputs;
   - formula/threshold/rounding;
   - store scope;
   - deterministic recommendation vs manual final adjustment.

Do not reconstruct either from materialized Google Sheet values alone.

Exact report formatting/macros that do not alter inventory meaning can be handled later as export/compatibility work.

### 5.4 F6C completion gate

F6C is complete when Product/Lot/Store/Catalogue/Receipt/Usage/Adjustment/Ledger/Reorder/Audit/month semantics are explicit enough to reproduce Main Stock and Daily Usage from DB state without guessing canonical inventory meaning.

No schema migration, fresh real import, production write, or canonical promotion is authorized merely by completing documentation.

## 6. NEXT — F6D Canonical Inventory Schema Parity + Fresh Shadow Import

Sequence:

1. add canonical Store/Location entity;
2. seed/configure one Main Store identity for the legacy-source migration context;
3. make balance-changing movements location-aware;
4. add location-aware indexes/queries;
5. add receipt destination location;
6. add explicit transfer header/lines or equivalent typed transfer representation with paired atomic ledger effects;
7. make monthly snapshot rows store+lot scoped;
8. preserve a path for per-store reorder configuration/overrides;
9. apply only other schema changes proven by F6C;
10. create versioned migrations and repeatable import tooling;
11. take a fresh authorized source snapshot;
12. import non-canonically with provenance bound to Main Store;
13. reconcile product/lot identity, expiry separation, opening/base stock, receipts, usage, CMS mapping/price and current balances;
14. prove Main Stock and Daily Usage projections from shadow DB;
15. classify every mismatch instead of forcing either side to match;
16. keep PostgreSQL non-canonical until explicit acceptance.

The full custom table-builder/editor is intentionally **not** part of F6D.

## 7. Subsequent implementation sequence

1. finish F6C month/reorder gates;
2. F6D location-aware schema parity + fresh shadow import;
3. historical bootstrap from strongest available evidence;
4. shadow calculation parity;
5. minimal field/computation registry and saved view-definition substrate;
6. DB-backed Main Stock and Daily Usage preset views;
7. spreadsheet-like draft/confirm/save editing over typed commands;
8. dual verification of real operational events;
9. read-path promotion;
10. controlled write promotion per operation class;
11. explicit database canonicality promotion;
12. Sheet mirror/rebuild and multi-client expansion;
13. resume deferred Telegram/AI collaboration expansions as useful.

## 8. Immediate boundary

Continue source-first analysis. Re-read the live Google Sheet whenever field/value behavior matters. Do not infer exact legacy formulas/macros from materialized cloud values. Do not spend the next slices expanding AI collaboration unless explicitly reprioritized.
