# Medicine Store Assistant — Project Roadmap

Status: **Phase 2 foundation active; F0/F1/F2/F3 verified complete; F4 authored and VPS verification pending**

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

Status: **authorized and authored; VPS verification pending**

Purpose: prove deterministic inventory-movement semantics before importing or writing real store inventory.

Repository implementation includes:

- migration `0002_ledger` adding `inventory_transactions`;
- transaction types `OPENING_BALANCE`, `RECEIPT`, `USAGE`, `ADJUSTMENT_POSITIVE`, `ADJUSTMENT_NEGATIVE`;
- fixed-point positive quantity constraint;
- unique `operation_id` idempotency protection;
- correction/reversal linkage without destructive deletion;
- stable user/service-principal actor linkage;
- deterministic lot-balance calculation;
- normal negative-stock blocking;
- synthetic verifier covering balance math, duplicate-operation rejection, negative-stock rejection, and linked reversal semantics;
- verifier transaction rollback so synthetic fixture data does not remain in PostgreSQL;
- `deploy/apply_f4_ledger_foundation.sh` to apply migration, run synthetic verification, and confirm `/health` + `/ready`;
- `/ready` expects migration `0002_ledger` once F4 is applied.

F4 does **not** expose production inventory write endpoints, import live Sheet data, mutate Google Sheets, enable Custom GPT writes, or promote PostgreSQL to canonical authority.

Current VPS verification command:

```bash
cd /opt/medicine-store-assistant/app/repo && git pull --ff-only && bash deploy/apply_f4_ledger_foundation.sh
```

Expected success evidence includes:

- repository validator PASS;
- Alembic upgrade to `0002_ledger`;
- synthetic ledger verifier PASS for balance math, idempotency, negative-stock guard, and reversal linkage;
- `/health` HTTP 200 with `database_canonical: false`;
- `/ready` HTTP 200 with migration and expected migration both `0002_ledger`.

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

1. Run the F4 VPS verification command above and inspect its exact output.
2. If verification passes, record F4 canonical runtime evidence and mark F4 verified complete.
3. Do not begin live shadow import or production stock-write authority without a later explicit slice.

## Continuity rule

After every significant architecture decision, implementation slice, deployment change, migration result, or next-work change:

1. update `ROADMAP.md`;
2. update `NEW_CHAT_BOOTSTRAP.md`;
3. update relevant canonical architecture/operations docs.
