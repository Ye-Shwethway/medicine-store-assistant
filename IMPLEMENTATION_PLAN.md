# Medicine Store Assistant — Implementation Plan

Status: **F6C architecture is locked. F6D shadow foundation is runtime-verified. F6E Slice A/B/C are complete and runtime-verified through the configurable read-only Inventory View Engine, generic Web renderer, CMS Mapping Review, source-vs-shadow review workspace, filters, highlighting, selection context and detail drawer. PostgreSQL remains non-canonical. Current bounded target: Slice D embedded Inventory AI copilot context + deep-review handoff.**

## 1. Global rules

- Google Sheets/source documents remain operationally authoritative until explicit canonical DB promotion.
- `database_canonical=false`; `migration_baseline_accepted=false`.
- PostgreSQL deployment, shadow materialization, catalogue import or review-state persistence does **not** make PostgreSQL canonical.
- All humans, AI agents, integrations and jobs use typed backend operations.
- Never expose arbitrary SQL, DB credentials, VPS shell/filesystem, Sheet credentials, plaintext provider keys, passwords/tokens/recovery secrets, or unrestricted HTTP proxying to AI/client runtimes.
- Deterministic backend code owns identity, authorization, constraints, idempotency, transactionality, confirmation, read-back and audit semantics.
- AI may explain/rank/propose; it does not own mutation authority.
- Significant implementation/deploy/next-work changes update `ROADMAP.md`, `NEW_CHAT_BOOTSTRAP.md`, this file, relevant architecture docs and a bounded checkpoint.

## 2. Locked product architecture

`Product -> Lot -> Store -> Movement -> Balance -> Transfer -> CMS Mapping -> Actor/Audit`

- spreadsheet layout is configurable; inventory semantics are not arbitrary;
- stock belongs to a location; Product/CMS identity does not;
- quantity truth comes from movements;
- Total Stock is aggregate truth, never a second editable balance;
- Main Stock/Daily Usage are projections, not canonical worksheet-shaped tables;
- Main Stock, Daily Usage, Migration Review and CMS Mapping Review are system presets over a reusable View Engine;
- users may later build custom sheet-style tables by binding columns to registered semantic fields/computations/typed commands;
- arbitrary SQL/raw DB expressions are not a view-definition feature;
- AI enhances workflows but is not an availability dependency;
- CMS code equality alone never proves local Product identity.

## 3. Canonicality / write boundary

- no production inventory write/transfer/usage deduction or DB canonical promotion is authorized;
- no accepted Product-CMS mapping or operational-price mutation is authorized by catalogue/review staging alone;
- no arbitrary AI SQL/DB mutation;
- current live workbook remains operational authority;
- Inventory View Engine remains read-only and explicitly labels shadow/non-canonical state.

## 4. F6D verified shadow foundation

### Inventory source + materialization

- fresh batch `7ecf9a2b-0521-400d-8990-caaea20d3a57`;
- Main Stock **823** + Daily Usage **823** = **1,646 source evidence rows**;
- Products **670**;
- Lots **799**;
- `OPENING_BALANCE` movements **679**;
- opening quantity **72,009**;
- zero-balance identity-only Lots **120**;
- balance mismatches **0**;
- replay created Product/Lot/transaction rows **0/0/0**.

HOLDs remain unresolved rather than guessed: 14 inventory-semantic review rows, 4 duplicate Product+Expiry rows, 6 Unit-review rows.

### CMS catalogue + review state

- catalogue version `34947c29-6427-4b7c-9fb8-ba8ffe3278b0`, effective `2026-08-02`;
- rows / unique codes **6,891 / 6,891**;
- duplicate codes **0**;
- one blank source price preserved as `NULL`;
- durable non-accepted mapping review rows **670**: `REVIEW_REQUIRED 644`, `CMS_DISCONTINUED 19`, `RECYCLED_CODE 1`, `UNMAPPED 6`, `ACTIVE_MATCH 0`;
- accepted operational prices **0**;
- replay created **0** additional mapping rows.

## 5. F6E — Inventory View Engine

### 5.1 Slice A — registry + generic read projection — COMPLETE + RUNTIME VERIFIED

- [x] Typed field registry and generic view-definition model.
- [x] Main Stock system preset at `PRODUCT_LOT` grain.
- [x] Migration Review system preset at `SOURCE_MAIN_ROW` grain.
- [x] Validated registered-field subset/order; unknown fields rejected.
- [x] Authenticated read-only dashboard API.
- [x] Runtime proof: Main Stock **799**, Migration Review **823**, Main current quantity **72,009.000**, Products/Lots/transactions **670/799/679**, accepted mappings/prices **0/0**.

### 5.2 Slice B — generic Web renderer — COMPLETE + RUNTIME VERIFIED

- [x] One generic table component driven by returned `columns[]` metadata.
- [x] Main Stock / Migration Review preset switching.
- [x] Registry-driven visible columns, search and pagination.
- [x] `Shadow inventory — not canonical` banner.
- [x] Shadow Inspection remains separate diagnostic surface.
- [x] Responsive/mobile table-owned overflow.
- [x] 390x844 Playwright behavior proof.

### 5.3 Slice C — source compare + review — COMPLETE + RUNTIME VERIFIED

- [x] `CMS Mapping Review` third system preset at `PRODUCT_CMS_MAPPING` grain.
- [x] Provider-aware review filters: `mapping_status`, `source_classification`, `review_reason`.
- [x] Contextual Web filter controls.
- [x] REVIEW/HOLD/mapping-state row highlighting.
- [x] Checkbox selection + review-context bar with no acceptance semantics.
- [x] Row-click review detail drawer.
- [x] Migration Review source-vs-shadow quantity comparison.
- [x] CMS mapping/current catalogue/accepted-price evidence detail.
- [x] Mobile full-width drawer and responsive review controls.
- [x] PR #172 merged at `9d030f357a5c3c89e20c4ebba9a702920a227220`.
- [x] Deployment issue #26 confirmed `status=success` for that merge via run `32769124095`.
- [x] Runtime proof recorded in issue #171; mutation false and canonical flags remain false.
- [x] Post-verification polish PR #173 humanizes structured CMS `review_reason` JSON in table/drawer presentation while preserving raw evidence and read-only semantics; CI green, merge `3d7ad88fbd7634571a317cc9b4b5b4c084d77695`.

Slice C introduced **no** accepted CMS mapping, price mutation, inventory mutation, migration-baseline acceptance or DB canonical promotion.

### 5.4 Slice D — AI copilot — CURRENT

- [ ] Define a bounded `Inventory Review Context` payload containing current preset/view metadata, active filters, selected rows and allowed source/review evidence only.
- [ ] Add an embedded Inventory assistant entry point that can explain/rank/summarize selected review evidence.
- [ ] Reuse existing native AI Workspace/internal-agent runtime rather than creating a second inference stack.
- [ ] Add Deep Review handoff that creates/opens durable AI Workspace multi-agent review context from the selected Inventory rows.
- [ ] Preserve read-only context by default; AI cannot accept mappings, prices or inventory changes.
- [ ] Durable Owner/authorized typed acceptance remains a later mutation gate.
- [ ] Add behavior/runtime proof that context handoff contains only the intended selected evidence and canonical flags remain false.

### 5.5 Slice E — saved custom views

- [ ] Persist user-defined view definitions.
- [ ] View Builder: row grain, Store scope, field selection/order, labels, widths, filter/sort/group/formatting.
- [ ] Duplicate a system preset into a user-owned view without mutating the system preset.
- [ ] Never permit arbitrary SQL/raw DB expressions.

### 5.6 Slice F — Daily Usage + editing

- [ ] Daily Usage monthly-pivot system preset over normalized dated usage events.
- [ ] spreadsheet-like `draft -> validation -> preview -> Confirm & Save -> typed command -> audit -> read-back` editing.
- [ ] direct current-balance overwrite blocked/translated to explicit adjustment workflow.

## 6. Later sequence

1. Complete Slice D embedded Inventory AI copilot + deep-review handoff.
2. Resolve HOLD inventory rows and reviewed CMS mapping exceptions through typed reviewed actions.
3. Persist saved user-defined views / View Builder.
4. Daily Usage monthly-pivot preset + typed editing flow.
5. Deterministic reorder baseline engine and reorder presets.
6. Dual verification of real operational events.
7. Migration baseline acceptance after source/recovery/reconciliation gates.
8. Selected DB read-path promotion.
9. Controlled write promotion per operation class.
10. Explicit DB canonicality promotion.
11. Sheet mirror/rebuild, exports, Flutter/Telegram and further automation.

## 7. Immediate boundary

The immediate target is **Slice D Inventory AI copilot context/handoff**, not inventory mutation. The AI receives bounded review context and may explain, summarize, rank or propose only. Do not create accepted CMS mappings, push prices, mutate inventory, accept the migration baseline, or promote PostgreSQL as part of Slice D.
