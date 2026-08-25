# Medicine Store Assistant — Implementation Plan

Status: **F6C architecture is locked. F6D shadow foundation is runtime-verified. F6E Slice A/B/C/D are complete and runtime-verified through the configurable read-only Inventory View Engine, generic Web renderer, source/CMS review workspace, bounded Ask AI context and Deep Review handoff. Inventory Spreadsheet Focus Mode v1 is production-runtime verified. Current bounded target: Spreadsheet Workbench v2 read/review ergonomics. PostgreSQL remains non-canonical.**

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

## 5. F6E — Inventory View Engine + Workbench

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
- [x] Human-friendly presentation of structured CMS review reasons while preserving raw evidence.
- [x] Mobile full-width drawer and responsive review controls.
- [x] Production runtime evidence recorded in issue #171; mutation false and canonical flags remain false.

Slice C introduced **no** accepted CMS mapping, price mutation, inventory mutation, migration-baseline acceptance or DB canonical promotion.

### 5.4 Slice D — bounded AI copilot — COMPLETE + RUNTIME VERIFIED

- [x] Define bounded `Inventory Review Context` containing view metadata, active filters, pagination coordinates, selected row indices and server-rehydrated allowed review evidence.
- [x] Browser sends selection coordinates rather than treating DOM row facts as canonical context.
- [x] Add `Ask AI` entry point for selected Migration Review / CMS Mapping Review evidence.
- [x] Reuse existing native AI Workspace/internal-agent runtime rather than creating a second inference stack.
- [x] Ask AI explicitly opens Chat and creates a **fresh** conversation only after the user selects an agent.
- [x] Selected review prompt is prefilled but never auto-sent; model execution still requires explicit Send.
- [x] Add focused modal with selected-row summary, reliable agent loading/retry, Cancel and explicit Start new chat.
- [x] Add Deep Review handoff into the existing Owner Multi-Agent REVIEW workspace.
- [x] Deep Review prefills durable work title/task and exposes quick REVIEW preset / role / explicit-run controls without auto-running.
- [x] Preserve read-only context: AI cannot accept mappings, prices or inventory changes.
- [x] Durable Owner/authorized typed acceptance remains a later mutation gate.
- [x] Browser/runtime proof verifies bounded context and false canonical flags.

Evidence chain includes PRs #175, #177, #179, #180, #181, #183, #184 and runtime checkpoints #176/#178. Deployment issue #26 confirmed deployed descendants.

### 5.5 Inventory Spreadsheet Focus Mode v1 — COMPLETE + RUNTIME VERIFIED

- [x] Near-fullscreen Focus mode for the Inventory workbench.
- [x] Explicit Exit focus and `Escape` exit behavior.
- [x] Preserve View/Search/Filters/Columns controls in focused mode.
- [x] Comfortable/Compact table density toggle.
- [x] Header checkbox for Select visible rows with checked/indeterminate synchronization.
- [x] Rename ambiguous `Clear` action to explicit `Clear selection`.
- [x] Freeze selection column and first visible data column during horizontal scrolling.
- [x] Preserve existing Ask AI / Deep Review interactions.
- [x] 390x844 Playwright proof for focus viewport, select-visible, clear-selection, density and frozen columns.
- [x] PR #185 merged at `af461f2f4ddd329c81fd983955c26e905970e0af`.
- [x] Deployment issue #26 confirmed `status=success` for that SHA via run `32811537864`.
- [x] Runtime checkpoint issue #186 records the evidence.

### 5.6 Spreadsheet Workbench v2 — CURRENT

Keep v2 read/review-only. Do not add direct cell mutation yet.

- [ ] Add server-side validated sort parameters and visible sort indicators.
- [ ] Add active filter chips with per-chip removal and `Clear all` behavior.
- [ ] Add column resize/reorder controls over registered fields only.
- [ ] Add Auto-fit and Reset layout actions.
- [ ] Add Copy selected as TSV for direct paste into Excel/Google Sheets.
- [ ] Add CSV export for the current validated projection/filter/sort state.
- [ ] Add keyboard navigation/copy shortcuts after sort/layout interactions are stable.
- [ ] Add optional desktop split-pane review detail after core table ergonomics are proven.
- [ ] Keep all operations read-only/non-canonical.

### 5.7 Slice E — saved custom views

- [ ] Persist user-defined view definitions.
- [ ] View Builder: row grain, Store scope, field selection/order, labels, widths, filter/sort/group/formatting.
- [ ] Persist user-owned layout preferences such as column order/width/density/sort where appropriate.
- [ ] Duplicate a system preset into a user-owned view without mutating the system preset.
- [ ] Never permit arbitrary SQL/raw DB expressions.

### 5.8 Slice F — Daily Usage + editing

- [ ] Daily Usage monthly-pivot system preset over normalized dated usage events.
- [ ] spreadsheet-like `draft -> validation -> preview -> Confirm & Save -> typed command -> audit -> read-back` editing.
- [ ] direct current-balance overwrite blocked/translated to explicit adjustment workflow.
- [ ] only after this typed editing substrate exists may Excel-like inline editing/paste workflows gain mutation semantics.

## 6. Later sequence

1. Complete Spreadsheet Workbench v2 read/review ergonomics.
2. Persist saved user-defined views / View Builder.
3. Resolve HOLD inventory rows and reviewed CMS mapping exceptions through typed reviewed actions when explicitly authorized.
4. Daily Usage monthly-pivot preset + typed editing flow.
5. Deterministic reorder baseline engine and reorder presets.
6. Dual verification of real operational events.
7. Migration baseline acceptance after source/recovery/reconciliation gates.
8. Selected DB read-path promotion.
9. Controlled write promotion per operation class.
10. Explicit DB canonicality promotion.
11. Sheet mirror/rebuild, exports, Flutter/Telegram and further automation.

## 7. Immediate boundary

The immediate target is **Spreadsheet Workbench v2 read/review ergonomics**, not inventory mutation. Sorting/filtering/layout/copy/export features must operate over validated registered projections. Do not create accepted CMS mappings, push prices, mutate inventory, accept the migration baseline, or promote PostgreSQL as part of this workbench slice.