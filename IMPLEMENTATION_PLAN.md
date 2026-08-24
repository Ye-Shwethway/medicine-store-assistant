# Medicine Store Assistant — Implementation Plan

Status: **AI Workspace / D4.8-D4.9 is accepted. F6B remains test-only; PostgreSQL remains non-canonical. Current bounded slice: F6C Workbook Parity Lock. Next: F6D Canonical Inventory Schema Parity + Fresh Shadow Import.**

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

## 3. Canonicality / write boundary

- `database_canonical=false`.
- `migration_baseline_accepted=false`.
- Existing F6B shadow data is test evidence only.
- No production inventory write, transfer, Calculator deduction, Telegram/Flutter stock mutation, automatic OCR/vision commit, arbitrary agent DB/SQL mutation, or DB canonical promotion is authorized.

## 4. CURRENT — F6C Workbook Parity Lock

Canonical docs:

- `docs/architecture/F6C_WORKBOOK_PARITY_LOCK.md`
- `docs/architecture/WORKBOOK_PARITY_MATRIX.md`
- `docs/architecture/WORKBOOK_FUNCTION_CONTRACT.md`

### 4.1 Source inspection order

1. Main Stock exact structure and formulas/functions.
2. Daily Usage exact structure and month behavior.
3. This Month Received projection/filter behavior.
4. Reorder exact calculation algorithm.
5. Final Reorder copy/edit/submission/archive behavior.
6. CMS catalogue/price-list identity and retention behavior.
7. Transfer/receipt intake structure and mapping flow.
8. Monthly close / Excel Master copy-reset-archive behavior.

### 4.2 Required output for each source surface

- exact source fields/columns;
- editable vs formula/lookup/integration-managed fields;
- business meaning;
- identity implications;
- formula/macro/workflow behavior;
- future domain entity or projection mapping;
- unresolved gaps requiring Owner review.

### 4.3 F6C completion gate

Do not mark F6C complete until every operational workbook surface is accounted for and no required formula/macro/business behavior is silently omitted or guessed.

No schema migration, fresh real import, production write, or canonical promotion is authorized merely by starting F6C.

## 5. NEXT — F6D Canonical Inventory Schema Parity + Fresh Shadow Import

After F6C acceptance:

1. compare the locked workbook contract with `INVENTORY_DATA_MODEL.md`, `F2_SCHEMA_DECISION_PROPOSAL.md`, `MONTHLY_LIFECYCLE.md`, `CMS_CATALOGUE_VERSIONING.md`, and `SHEET_MIRROR_AND_COMPATIBILITY.md`;
2. change only domain/schema elements that parity evidence requires;
3. create versioned migrations and repeatable import tooling;
4. use a fresh authorized current source snapshot;
5. import non-canonically with provenance;
6. reconcile product/lot identity, expiry separation, balances, receipts, usage, CMS mapping/price and relevant workbook projections;
7. classify every mismatch instead of forcing either side to match;
8. keep PostgreSQL non-canonical until explicit acceptance.

## 6. Subsequent implementation sequence

1. F6C workbook parity lock.
2. F6D schema parity + fresh shadow import.
3. Historical bootstrap from strongest available evidence.
4. Shadow calculation parity.
5. Dual verification of real operational events.
6. Read-path promotion.
7. Controlled write promotion per operation class.
8. Explicit database canonicality promotion.
9. Sheet mirror mode and rebuild/recovery proof.
10. Resume deferred Telegram/AI collaboration expansions as useful.

## 7. Immediate boundary

The project focus is now the real inventory/workbook/database path. Do not spend the next slices expanding AI collaboration, Telegram delivery, GROUP/COMPARE/DEBATE, or speculative intelligence features unless explicitly reprioritized.
