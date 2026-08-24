# Medicine Store Assistant — Project Roadmap

Status: **AI Workspace / D4.8-D4.9 is an accepted supporting foundation. F6B remains test-only; PostgreSQL remains non-canonical. Current bounded target: F6C Workbook Parity Lock, followed by F6D Canonical Inventory Schema Parity + Fresh Shadow Import.**

The live Google workbook/source documents remain operationally authoritative. `migration_baseline_accepted=false`; `database_canonical=false`.

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

## CURRENT — F6C Workbook Parity Lock

Canonical architecture: `docs/architecture/F6C_WORKBOOK_PARITY_LOCK.md`.

Purpose: lock the real workbook structure/functions before modifying the canonical inventory schema or performing a fresh migration candidate.

Source surfaces to inspect and document from authorized current evidence:

1. Main Stock
2. Daily Usage
3. This Month Received
4. Reorder
5. Final Reorder
6. CMS catalogue / price list
7. transfer / receipt intake
8. monthly close / Excel Master compatibility

Deliverables:

- `docs/architecture/WORKBOOK_PARITY_MATRIX.md`
- `docs/architecture/WORKBOOK_FUNCTION_CONTRACT.md`
- explicit schema/domain gap list
- fresh shadow-import plan

Do not invent missing formulas, macros, column behavior, reorder logic, or month-close semantics from memory.

## NEXT — F6D Canonical Inventory Schema Parity + Fresh Shadow Import

After F6C is source-verified:

1. adjust only the schema/domain pieces proven necessary by parity analysis;
2. implement/revise product, lot, CMS catalogue mapping, receipts, usage, adjustments and monthly-state structures as required;
3. take a fresh authorized source snapshot;
4. perform a repeatable non-canonical shadow import;
5. reconcile identities, expiry lots, balances, receipt totals, usage, CMS mapping/price and workbook projections;
6. keep unresolved mismatches explicit and remain non-canonical until accepted.

The existing F6B data is not the F6D migration baseline.

## Subsequent inventory/database path

1. **F6C — CURRENT:** workbook parity lock.
2. **F6D:** schema parity + fresh shadow import.
3. Historical bootstrap from strongest available evidence without fabricating transactions.
4. Shadow calculation parity for balances, receipts, usage, CMS data, month outputs and reorder.
5. Dual verification of real operational events against the live workbook.
6. Selected DB read-path promotion only after repeated parity.
7. Controlled write promotion one operation class at a time with idempotency, authorization, confirmation, audit and read-back.
8. Explicit database canonicality promotion only after migration, backup/restore, month-close/reorder and Sheet-mirror parity are proven.

## Deferred supporting work

Telegram Attention delivery, GROUP, COMPARE, DEBATE, broader vision/OCR and additional AI collaboration features remain later work unless explicitly reprioritized. They must not block the core inventory/database migration path.

## Immediate boundary

Proceed from the live workbook as source truth. The next work is understanding and reproducing the real store workflow, not adding more AI surface area. No production inventory mutation or PostgreSQL canonical promotion is authorized in F6C/F6D until the explicit acceptance gates are met.
