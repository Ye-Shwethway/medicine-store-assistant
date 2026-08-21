# Medicine Store Assistant — Project Roadmap

Status: **Phase 2 foundation active; F0/F1/F2/F3/F4 verified complete**

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

Status: **verified complete 2026-08-22**

Evidence: `docs/operations/F4_SYNTHETIC_LEDGER_VERIFICATION_2026-08-22.md`.

Verified deployed commit: `184f964a86cfb00696f4f2622e41289ab53f165a`.

Verified runtime and invariants:

- repository validator passed;
- Alembic upgraded `0001_foundation -> 0002_ledger`;
- `inventory_transactions` ledger foundation is deployed;
- movement types are `OPENING_BALANCE`, `RECEIPT`, `USAGE`, `ADJUSTMENT_POSITIVE`, and `ADJUSTMENT_NEGATIVE`;
- fixed-point positive quantities and unique `operation_id` protection are enforced;
- deterministic lot-balance calculation passed;
- duplicate-operation/idempotency protection passed;
- normal negative-stock guard passed;
- linked reversal/correction semantics passed;
- synthetic verifier fixture data is rolled back and not retained;
- `/health` returned healthy metadata with `database_canonical: false` and build SHA `184f964a86cfb00696f4f2622e41289ab53f165a`;
- `/ready` returned database reachable with migration and expected migration both `0002_ledger`;
- transient connection resets during API recreation were tolerated by the deployment helper retry loop and were followed by successful health/readiness verification.

F4 exposes no production inventory write endpoint, imports no live Sheet inventory, mutates no Google Sheet, connects no Custom GPT write Action, and does not promote PostgreSQL.

## Phase 3 — Shadow migration/reconciliation

Status: **not started**

Import current Sheet state into shadow PostgreSQL only after an explicitly authorized migration slice. Preserve provenance, compare backend projections against the workbook, and report mismatches without silent repair.

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

## Recommended next minimum safe slice

**F5 — CMS catalogue versioning with synthetic/non-sensitive sample data only.**

Why this is the preferred next slice:

- it is already the next ordered slice in `IMPLEMENTATION_PLAN.md`;
- it exercises deterministic import/version/diff/idempotency behavior without touching live stock quantities;
- it preserves the critical rule that CMS code alone cannot remap local product identity;
- it creates useful foundation for later reconciliation while staying below the risk boundary of live Sheet shadow import.

Proposed F5 scope, if explicitly authorized:

1. define/import a non-sensitive synthetic CMS catalogue fixture;
2. store catalogue version/hash metadata;
3. implement deterministic same-version idempotency;
4. implement new/removed/changed-row diff output;
5. expose current/historical catalogue reads only as needed for verification;
6. prove that catalogue-code changes do not automatically mutate local product/lot identity;
7. verify on VPS with synthetic/sample data and record canonical runtime evidence.

Do **not** begin F5 implementation, live Sheet import, production inventory writes, database promotion, Telegram writes, Flutter rollout, or Custom GPT write Actions without explicit authorization.

## Continuity rule

After every significant architecture decision, implementation slice, deployment change, migration result, or next-work change:

1. update `ROADMAP.md`;
2. update `NEW_CHAT_BOOTSTRAP.md`;
3. update relevant canonical architecture/operations docs.
