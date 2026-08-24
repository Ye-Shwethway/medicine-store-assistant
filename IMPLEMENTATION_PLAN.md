# Medicine Store Assistant — Implementation Plan

Status: **F6C architecture is locked. F6D schema, fresh Main Store staging, source-safe Main-primary shadow materialization, and the first live CMS catalogue version import are implemented and runtime-verified. PostgreSQL remains non-canonical. Current bounded work: CMS assisted-reconciliation planning, read-only first.**

## 1. Global rules

- Google Sheets/source documents remain operationally authoritative until explicit canonical DB promotion.
- `database_canonical=false`; `migration_baseline_accepted=false`.
- PostgreSQL deployment, shadow materialization, or catalogue import does **not** make PostgreSQL canonical.
- All humans, AI agents, integrations and jobs use typed backend operations.
- Never expose arbitrary SQL, DB credentials, VPS shell/filesystem, Sheet credentials, plaintext provider keys, passwords/tokens/recovery secrets, or unrestricted HTTP proxying to AI/client runtimes.
- Deterministic backend code owns identity, authorization, constraints, idempotency, transactionality, confirmation, read-back and audit semantics.
- Essential store workflows degrade safely when AI providers are unavailable.
- Significant implementation/deploy/next-work changes update `ROADMAP.md`, `NEW_CHAT_BOOTSTRAP.md`, this file, relevant architecture docs and a bounded checkpoint.

## 2. Locked product architecture

`Product -> Lot -> Store -> Movement -> Balance -> Transfer -> CMS Mapping -> Actor/Audit`

- spreadsheet layout is configurable; inventory semantics are not arbitrary;
- stock belongs to a location; Product/CMS identity does not;
- quantity truth comes from movements;
- Total Stock is aggregate truth, never a second editable balance;
- Main Stock/Daily Usage are projections, not canonical worksheet-shaped tables;
- AI enhances workflows but is not an availability dependency;
- CMS code equality alone never proves local Product identity.

## 3. Canonicality / write boundary

- no production inventory write/transfer/usage deduction or DB canonical promotion is authorized;
- no accepted Product-CMS mapping or operational-price mutation is authorized by catalogue import alone;
- no arbitrary AI SQL/DB mutation;
- current live workbook remains operational authority.

## 4. F6C — COMPLETE

Locked semantics include stable Product identity, Product+structured-expiry Lot identity, one Main Store plus unlimited Sub Stores, movement-derived Store balances, atomic internal transfers, global/versioned CMS Catalogue, auditable Product-CMS mapping lifecycle, last-accepted mapping/price fallback, deterministic reorder baseline, and shared human/AI typed-operation provenance.

## 5. F6D — ACTIVE

### 5.1 Schema foundation — DONE

Migration `0022_inventory_foundation` implements Store-aware ledger semantics, transfer/receipt structures, Product-CMS mapping lifecycle, accepted operational price retention, and location/total balance projections. PostgreSQL CI verifies migration, transfer conservation/linkage, mapping fallback, and schema integrity.

### 5.2 Fresh live source staging — DONE + RUNTIME VERIFIED

- fresh migration batch: `7ecf9a2b-0521-400d-8990-caaea20d3a57`;
- source hash: `c212d7da6192e7e20f340e7b302436f588dfb0fa191459fd572dfdb46f23ba76`;
- Main Stock rows: **823**;
- Daily Usage rows: **823**;
- staged source records: **1,646 = 823 + 823**;
- replay idempotency: PASS.

Main Stock owns migration Product/Lot/current-balance evidence. Daily Usage is joined usage evidence only.

### 5.3 Main-primary materialization — DONE + RUNTIME VERIFIED

The source-safe subset was materialized into shadow PostgreSQL:

- persisted Products: **670**;
- persisted Lots: **799**;
- migration `OPENING_BALANCE` movements: **679**;
- opening quantity: **72,009**;
- zero-balance identity-only Lots: **120**;
- balance readback mismatches: **0**;
- immediate replay created Product/Lot/transaction counts: **0 / 0 / 0**.

Explicit HOLDs remain unmaterialized rather than guessed:

- 14 inventory-semantic review rows;
- 4 duplicate Product+Expiry rows: `41,42,156,157`;
- 6 Unit-review rows: `237,245,459,460,461,601`.

No Product-CMS mapping was created by this step.

### 5.4 Live CMS catalogue version import — DONE + RUNTIME VERIFIED

The current catalogue was imported as versioned **reference data only**:

- sheet `CMS_Price_List_202608`;
- effective date `2026-08-02`;
- source hash `6f221152024c9a06b73f7f7115097abfb688a37a6ba6bf0be78345f3b70dd116`;
- catalogue version `34947c29-6427-4b7c-9fb8-ba8ffe3278b0`;
- rows **6,891**;
- unique codes **6,891**;
- duplicate codes **0**;
- blank codes **0**;
- invalid prices **0**;
- one blank source price at row `6442`, code `S10105035`, preserved as `NULL`;
- replay returned `created=false` for the same catalogue version.

Protected local-domain counts stayed unchanged before/after import:

- Products **670**;
- Lots **799**;
- inventory transactions **679**;
- Product-CMS mappings **0**.

Catalogue import therefore does not imply mapping acceptance or current-price propagation.

### 5.5 CURRENT — CMS assisted-reconciliation read-only planner

Implement deterministic screening before any mapping write:

1. resolve each materialized Product back to fresh Main Stock evidence using the same normalized local Product identity;
2. read source `serial_code`, `cs_name`, `mapping_hint`, local name, remark and price evidence;
3. compare those fields against catalogue version `34947c29-6427-4b7c-9fb8-ba8ffe3278b0`;
4. report deterministic categories such as continuity candidate, unmapped, discontinued, recycled-code/review, code-not-in-current-catalogue, code-name conflict and ambiguous local Product evidence;
5. treat code equality as evidence, never identity proof by itself;
6. preserve historical/local-error uncertainty instead of automatically asserting code reuse;
7. keep `product_cms_mappings` count unchanged during the planner;
8. produce representative review rows and counts for Owner review;
9. add AI candidate reasoning only after deterministic screening, and keep AI optional;
10. authorize mapping persistence only in a later explicit acceptance slice.

### 5.6 Import / migration constraints

- Never identify Product solely from CMS Code.
- Do not infer Product identity solely from item-name expiry suffix.
- Structured Expiry Date is the primary Lot-expiry source unless stronger evidence overrides it.
- Preserve local names and suspicious/recycled/discontinued CMS states.
- Do not fabricate receipt/usage history from aggregate cells without provenance.
- Migration opening balances remain one explicit provenance-bearing movement per accepted pre-existing positive-balance Lot.
- Every generated movement requires deterministic operation/idempotency identity and source provenance.
- A catalogue version is reference evidence; it cannot silently rewrite historical transaction price, local mapping, or operational price.

## 6. Later sequence

1. CMS assisted-reconciliation read-only planner.
2. Reviewed mapping-candidate workflow and explicit human acceptance.
3. Historical bootstrap from strongest available evidence.
4. Shadow Main Stock/Daily Usage projection parity + transfer tests.
5. Field/computation registry + saved views.
6. DB-backed Main Stock/Daily Usage presets.
7. Spreadsheet-like draft/confirm/save editing over typed commands.
8. Deterministic reorder baseline engine.
9. Optional AI mapping/reorder/trend proposal-review.
10. Dual verification of real operations.
11. Selected read-path promotion.
12. Controlled write promotion per operation class.
13. Explicit DB canonicality promotion.
14. Sheet mirror/rebuild, exports and multi-client expansion.

## 7. Immediate boundary

The next action is a **read-only CMS assisted-reconciliation planner**. Do not create accepted Product-CMS mappings, push catalogue prices into local operational state, or promote PostgreSQL merely because the catalogue is imported.