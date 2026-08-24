# Medicine Store Assistant — Implementation Plan

Status: **F6C architecture is locked. F6D shadow foundation is runtime-verified through normalized inventory materialization, catalogue import, deterministic CMS reconciliation and durable non-accepted mapping review state. PostgreSQL remains non-canonical. Current bounded work: configurable read-only Inventory View Engine + migration-review Web surface.**

## 1. Global rules

- Google Sheets/source documents remain operationally authoritative until explicit canonical DB promotion.
- `database_canonical=false`; `migration_baseline_accepted=false`.
- PostgreSQL deployment, shadow materialization, catalogue import or review-state persistence does **not** make PostgreSQL canonical.
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
- Main Stock, Daily Usage, Migration Review and CMS Mapping Review are system presets over a reusable View Engine;
- users may later build custom sheet-style tables by binding columns to registered semantic fields/computations/commands;
- a client never supplies arbitrary SQL/raw DB expressions as a view definition;
- AI enhances workflows but is not an availability dependency;
- CMS code equality alone never proves local Product identity.

## 3. Canonicality / write boundary

- no production inventory write/transfer/usage deduction or DB canonical promotion is authorized;
- no accepted Product-CMS mapping or operational-price mutation is authorized by catalogue/review staging alone;
- no arbitrary AI SQL/DB mutation;
- current live workbook remains operational authority;
- Inventory View Engine v1 is read-only and explicitly labels shadow/non-canonical state.

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

### CMS catalogue

- version `34947c29-6427-4b7c-9fb8-ba8ffe3278b0`;
- effective date `2026-08-02`;
- source hash `6f221152024c9a06b73f7f7115097abfb688a37a6ba6bf0be78345f3b70dd116`;
- rows / unique codes **6,891 / 6,891**;
- duplicate codes **0**;
- one blank source price preserved as `NULL`.

### CMS reconciliation + review state

Deterministic screening categories include 526 exact-name/same-price continuity, 77 exact-name/changed-price continuity, 30 multiple-source-code, 19 discontinued, 9 code/name mismatch, 6 unmapped, 1 missing source CMS name, 1 multiple source CMS names and 1 recycled-code case.

Durable non-accepted mapping review rows: **670**:

- `REVIEW_REQUIRED` **644**;
- `CMS_DISCONTINUED` **19**;
- `RECYCLED_CODE` **1**;
- `UNMAPPED` **6**;
- `ACTIVE_MATCH` **0**;
- accepted operational prices **0**.

Replay created **0** additional rows. Inventory counts remained unchanged.

## 5. F6E — CURRENT: Inventory View Engine

### 5.1 Slice A — registry + generic read projection

- [x] Lock `docs/architecture/INVENTORY_VIEW_ENGINE_V1.md`.
- [x] Add typed field registry contract.
- [x] Add generic view-definition model.
- [x] Add Main Stock system preset at `PRODUCT_LOT` grain.
- [x] Add Migration Review system preset at `SOURCE_MAIN_ROW` grain.
- [x] Add validated caller-selected field subset/order contract.
- [x] Reject unknown/unregistered field keys.
- [x] Keep output read-only/non-canonical.
- [ ] Wire router into authenticated dashboard API.
- [ ] Add runtime readback verification against current shadow counts.

### 5.2 Slice B — generic Web renderer

- [ ] Replace product-facing old staged-row Inventory table with one generic table component.
- [ ] Preset selector: Main Stock / Migration Review first.
- [ ] Render columns from view-definition metadata, not hard-coded `<th>` cells.
- [ ] Keep Shadow Inspection as separate diagnostic surface.
- [ ] Show strong `Shadow inventory — not canonical` banner.
- [ ] Add search/filter/pagination without changing domain truth.
- [ ] Preserve responsive/mobile usability and full-table view.
- [ ] Behavior-level browser verification at desktop and 390x844 mobile.

### 5.3 Slice C — source compare + review

- [ ] Source-vs-shadow compare mode/detail drawer.
- [ ] Highlight unresolved HOLDs and mapping review states.
- [ ] CMS Mapping Review system preset using the same View Engine.
- [ ] Review filters/bulk selection without automatic acceptance.

### 5.4 Slice D — AI copilot

- [ ] Embedded assistant receives current view, selected rows, filters and source evidence.
- [ ] AI may explain/rank/propose; it does not own acceptance.
- [ ] Deep Review handoff to AI Workspace/multi-agent substrate.
- [ ] Durable Owner decision/typed acceptance remains the mutation gate.

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

1. Resolve HOLD inventory rows and reviewed CMS mapping exceptions.
2. Deterministic reorder baseline engine and reorder presets.
3. Dual verification of real operational events.
4. Migration baseline acceptance after source/recovery/reconciliation gates.
5. Selected DB read-path promotion.
6. Controlled write promotion per operation class.
7. Explicit DB canonicality promotion.
8. Sheet mirror/rebuild, exports, Flutter/Telegram and further automation.

## 7. Immediate boundary

The immediate implementation target is **Slice A -> Slice B**: wire the generic authenticated read API, prove Main Stock/Migration Review projections, then render them through one configurable table component. Do not create accepted CMS mappings, push prices, mutate inventory, or promote PostgreSQL during this work.