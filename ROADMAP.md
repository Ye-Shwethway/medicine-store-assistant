# Medicine Store Assistant — Project Roadmap

Status: **Phase 2 foundation active; F0/F1/F2/F3 verified complete; F4 synthetic ledger slice authorized**

This roadmap tracks the full Medicine Store Assistant project and must stay synchronized with `NEW_CHAT_BOOTSTRAP.md`.

## Core architecture

```text
MSA Custom GPT ─┐
Telegram ───────┼──> Inventory API on VPS ───> PostgreSQL
Flutter ────────┘              │
                               ├──> Google Sheets operational mirror
                               └──> Excel monthly exports
```

GitHub stores code/docs only. The current Google workbook remains operationally authoritative until shadow/dual validation and explicit database promotion.

## Phase 0 — Existing skill/workbook foundation

Status: **completed / active operational workflow**

The Git-backed `$msa` skill, source hierarchy, lot handling, CMS matching rules, visual marking, tab persistence, Fixed Assets boundary, Daily Usage parity, and Main/Daily synchronization contract remain preserved.

## Phase 1 — Architecture documentation

Status: **sufficient for foundation implementation**

Canonical docs cover inventory architecture/data model, monthly lifecycle, CMS versioning, integrity/audit, Sheet/Excel compatibility, API/client architecture, migration/shadow validation, user/access management, decisions, VPS deployment, backup/recovery, and implementation slices.

F2 schema/access decisions are locked in `docs/architecture/F2_SCHEMA_DECISION_PROPOSAL.md`.

## Phase 2 — Backend foundation

Status: **active**

### F0 — VPS inspection

Status: **verified complete 2026-08-22**

Evidence: `docs/operations/F0_VPS_INSPECTION_2026-08-22.md`.

### F1 — Runtime skeleton

Status: **verified complete 2026-08-22**

Evidence: `docs/operations/F1_VPS_RUNTIME_VERIFICATION_2026-08-22.md`.

### Cloudflare public HTTPS route

Status: **verified complete 2026-08-22**

Canonical evidence: `docs/operations/CLOUDFLARE_ROUTE_2026-08-22.md`.

Verified path:

`https://inventory.drthorne.uk -> Cloudflare HTTPS edge -> existing managed Tunnel -> http://localhost:8088`

User-side browser verification observed the expected public-safe MSA health JSON over HTTPS. VPS port 8088 remains non-public.

### F2 — PostgreSQL schema/migration foundation

Status: **verified complete 2026-08-22**

Evidence: `docs/operations/F2_VPS_MIGRATION_VERIFICATION_2026-08-22.md`.

Verified migration `0001_foundation`, DB readiness, stable user/access/product/lot/month/catalogue/audit foundation, and `database_canonical: false`.

### F3 — Authenticated read-only domain/API

Status: **verified complete 2026-08-22**

Evidence: `docs/operations/F3_READ_API_VERIFICATION_2026-08-22.md`.

Verified runtime:

- deployed commit `dac1a4aa5b218d3c5eda24a636b3c3688979473b`;
- `/health` and `/ready` healthy;
- anonymous `/v1/products` returns HTTP 401;
- authenticated `/v1/products` returns HTTP 200 with expected empty list before import;
- scoped read token stored only in protected VPS runtime secrets and hash stored in DB;
- authenticated read-only product/lot/month/catalogue/access diagnostics available;
- no live inventory import or inventory write endpoint exists.

### F4 — Ledger primitives in isolated synthetic/test mode

Status: **authorized / current implementation slice**

Purpose: prove deterministic inventory-movement semantics before importing or writing real store inventory.

Authorized F4 scope:

- add ledger transaction schema for `OPENING_BALANCE`, `RECEIPT`, `USAGE`, `ADJUSTMENT_POSITIVE`, `ADJUSTMENT_NEGATIVE`;
- fixed-point quantities and explicit transaction type semantics;
- operation/idempotency key uniqueness so retries cannot duplicate movement;
- correction/reversal linkage without destructive history deletion;
- deterministic lot balance calculation from movements;
- explicit negative-balance protection for normal synthetic test operations;
- synthetic/test fixture workflow only;
- automated tests/verification proving idempotency, balance math, reversal semantics, and negative-stock policy;
- no live Google Sheet import;
- no real medicine-store stock writes;
- no Sheet mirror mutation;
- no database canonical promotion.

F4 is not production stock authority. Any write endpoints introduced for verification must be clearly test-only/internal or disabled from the public production API surface.

## Phase 3 — Shadow migration/reconciliation

Status: **not started**

Import current Sheet state into shadow PostgreSQL only after the deterministic ledger foundation is verified. Preserve provenance, compare backend projections against the workbook, and report mismatches without silent repair.

## Phase 4 — Dual validation

Status: **not started**

Run representative real workflows through current Sheet + backend shadow path and compare before promotion.

## Phase 5 — Canonical database promotion

Status: **not started; explicit approval required**

Requires parity acceptance, tested backup/restore, and rollback/cutback plan.

## Phase 6 — Private Custom GPT Action experiment

Status: **possible after stable public HTTPS + verified read-only API; not connected yet**

Start read-only with a revocable scoped service credential. No arbitrary SQL/database credentials.

## Phase 7 — Google Sheets mirror

Status: **future**

## Phase 8 — Telegram staff client

Status: **future multi-user client**

## Phase 9 — Flutter staff application

Status: **future multi-user client**

## Phase 10 — Monthly archive/export

Status: **future**

## Current next work

1. Implement and verify F4 synthetic/test-only ledger primitives.
2. Keep public/domain production surface read-only.
3. Do not import current Sheet inventory or grant production stock-write authority during F4.

## Continuity rule

After every significant architecture decision, implementation slice, deployment change, migration result, or next-work change:

1. update `ROADMAP.md`;
2. update `NEW_CHAT_BOOTSTRAP.md`;
3. update relevant canonical architecture/operations docs.
