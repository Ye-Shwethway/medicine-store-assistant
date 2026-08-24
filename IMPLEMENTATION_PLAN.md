# Medicine Store Assistant — Implementation Plan

Status: **AI Workspace / D4.8-D4.9 is accepted. F6B remains test-only; PostgreSQL remains non-canonical. Current bounded slice: F6C Workbook Parity Lock with canonical-domain/configurable-view separation. Next: F6D Canonical Inventory Schema Parity + Fresh Shadow Import.**

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

Canonical architecture: `docs/architecture/CONFIGURABLE_OPERATIONAL_VIEW_ENGINE.md`.

## 4. Canonicality / write boundary

- `database_canonical=false`.
- `migration_baseline_accepted=false`.
- Existing F6B shadow data is test evidence only.
- No production inventory write, transfer, Calculator deduction, Telegram/Flutter stock mutation, automatic OCR/vision commit, arbitrary agent DB/SQL mutation, or DB canonical promotion is authorized.

## 5. CURRENT — F6C Workbook Parity Lock

Canonical docs:

- `docs/architecture/F6C_WORKBOOK_PARITY_LOCK.md`
- `docs/architecture/CONFIGURABLE_OPERATIONAL_VIEW_ENGINE.md`
- `docs/architecture/WORKBOOK_PARITY_MATRIX.md`
- `docs/architecture/WORKBOOK_FUNCTION_CONTRACT.md`

### 5.1 Priority inspection order

1. Main Stock field semantics and product/lot identity.
2. Daily Usage movement semantics and monthly pivot behavior.
3. CMS catalogue/mapping/current-price behavior.
4. Batch intake, idempotency, new expiry lots and fixed-asset routing.
5. Reorder inputs/configuration and calculated recommendation.
6. Month rollover/opening carry-forward/audit behavior.
7. Store/location model needed for one Main Store plus unlimited Sub Stores.
8. Projection/archive surfaces only to the degree needed to preserve business meaning.

`This Month Received`, `Reorder Form`, `Final Reorder Form` and Master/archive formatting are primarily views/working outputs/snapshots and must not drive the canonical schema.

### 5.2 Required output for each important field/workflow

Classify as one of:

- canonical entity/domain field;
- canonical event/transaction;
- deterministic computed field;
- command-backed editable field;
- display/helper/projection-only field;
- approved snapshot/archive output;
- unresolved Owner decision.

Also record:

- source evidence;
- editable/write semantics;
- identity implications;
- authority/idempotency needs;
- future canonical or view mapping.

### 5.3 F6C completion gate

F6C is complete when:

- Product/Lot/Store/Catalogue/Receipt/Usage/Adjustment/Ledger/Audit semantics are explicit;
- Main Stock and Daily Usage can be reproduced as views over those semantics;
- current important columns are semantically classified;
- lower-priority projection/archive tabs are accounted for without over-modeling;
- unresolved issues are explicit rather than guessed.

No schema migration, fresh real import, production write, or canonical promotion is authorized merely by starting F6C.

## 6. NEXT — F6D Canonical Inventory Schema Parity + Fresh Shadow Import

After F6C acceptance:

1. compare the locked contract with `INVENTORY_DATA_MODEL.md`, `F2_SCHEMA_DECISION_PROPOSAL.md`, `MONTHLY_LIFECYCLE.md`, `CMS_CATALOGUE_VERSIONING.md`, `SHEET_MIRROR_AND_COMPATIBILITY.md`, and the configurable-view architecture;
2. lock Store/Location, Product, Lot, Catalogue Mapping, Receipt, Usage, Adjustment, Ledger and Audit identities;
3. change only domain/schema elements that parity evidence requires;
4. create versioned migrations and repeatable import tooling;
5. use a fresh authorized current source snapshot;
6. import non-canonically with provenance;
7. reconcile product/lot identity, expiry separation, opening/base stock, receipts, usage, CMS mapping/price and current balances;
8. prove Main Stock and Daily Usage projections from the shadow DB;
9. classify every mismatch instead of forcing either side to match;
10. keep PostgreSQL non-canonical until explicit acceptance.

The full custom table-builder/editor is intentionally **not** part of F6D.

## 7. Subsequent implementation sequence

1. F6C domain/workbook parity lock.
2. F6D schema parity + fresh shadow import.
3. Historical bootstrap from strongest available evidence.
4. Shadow calculation parity.
5. Minimal field/computation registry and saved view-definition substrate.
6. DB-backed Main Stock and Daily Usage preset views.
7. Spreadsheet-like draft/confirm/save editing over typed commands.
8. Dual verification of real operational events.
9. Read-path promotion.
10. Controlled write promotion per operation class.
11. Explicit database canonicality promotion.
12. Sheet mirror/rebuild and multi-client expansion.
13. Resume deferred Telegram/AI collaboration expansions as useful.

## 8. Immediate boundary

The project focus is now the real inventory/workbook/database path. Do not spend the next slices expanding AI collaboration, Telegram delivery, GROUP/COMPARE/DEBATE, or speculative intelligence features unless explicitly reprioritized.