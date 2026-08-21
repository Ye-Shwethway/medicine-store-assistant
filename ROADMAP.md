# Medicine Store Assistant — Project Roadmap

Status: **Phase 2 foundation active; F0/F1/F2 verified complete**

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

### F2 schema decisions — approved 2026-08-22

Locked v1 decisions include:

- one initial `OPENING_BALANCE` movement per migrated pre-existing lot; no repeated monthly opening movement;
- normal lot boundary = product + expiry, with receipt provenance kept separately;
- stable `product_id`; harmless local-name changes do not create new identity;
- fixed-point `NUMERIC(18,3)` quantities with whole-number validation for discrete units;
- normal writes cannot silently create negative stock;
- corrections use reversal/amendment rather than destructive rewriting;
- roles = `OWNER`, `ADMIN`, `STAFF`, `READ_ONLY`;
- stable backend `user_id` is canonical human identity;
- Telegram numeric user ID is an external identity link;
- Flutter uses native MSA credentials/session design;
- non-human clients use scoped service principals;
- protected operations preserve actor/client/operation attribution.

Canonical record: `docs/architecture/F2_SCHEMA_DECISION_PROPOSAL.md`.

## Phase 2 — Backend foundation

Status: **active**

### F0 — VPS inspection

Status: **verified complete 2026-08-22**

Evidence: `docs/operations/F0_VPS_INSPECTION_2026-08-22.md`.

### F1 — Runtime skeleton

Status: **verified complete 2026-08-22**

Evidence: `docs/operations/F1_VPS_RUNTIME_VERIFICATION_2026-08-22.md`.

Verified runtime includes FastAPI + PostgreSQL containers, API localhost-only at `127.0.0.1:8088`, no host-published MSA database port, `/health` HTTP 200, and `database_canonical: false`.

Bamboo/one-time executor is closed and no longer part of the implementation workflow.

### Cloudflare public route

Status: **configured; external health verification still pending**

Configured route:

`inventory.drthorne.uk -> existing managed Cloudflare Tunnel -> http://localhost:8088`

Cloudflare route/DNS read-back succeeded and VPS port 8088 remains non-public. Independent public fetch still has not produced a confirmed HTTP 200 response, so do not claim the HTTPS slice fully complete yet.

### F2 — PostgreSQL schema/migration foundation

Status: **verified complete 2026-08-22**

Canonical evidence: `docs/operations/F2_VPS_MIGRATION_VERIFICATION_2026-08-22.md`.

Verified implementation/runtime:

- SQLAlchemy + psycopg v3 + Alembic migration tooling;
- migration `0001_foundation` applied to isolated MSA PostgreSQL;
- foundation tables for users/roles/external identities, service principals/credential metadata, products/lots, operating months, CMS catalogue versions/items, and audit events;
- `/health` returned HTTP 200 with build SHA `a9cd98e4af6fd20aee07a783f82daf46d557ac7a` and `database_canonical: false`;
- `/ready` returned HTTP 200 with `database: reachable`, migration `0001_foundation`, expected migration `0001_foundation`, and `database_canonical: false`;
- deploy helper now tolerates transient container-recreate connection resets by retrying until stable readiness;
- psycopg v3 is the intended PostgreSQL driver; runtime URLs are normalized to `postgresql+psycopg://`.

F2 did **not** introduce stock ledger write APIs, live inventory import, Sheet mutation, Custom GPT writes, Telegram/Flutter rollout, or database canonical promotion.

### F3 — Core read-only domain/API

Status: **next implementation slice; not yet started**

Target scope:

- read-only product lookup/listing;
- read-only lot lookup/listing;
- operating-month read diagnostics;
- CMS catalogue/version read diagnostics;
- safe user/account diagnostics without exposing credential material;
- typed response models and stable API conventions;
- no inventory mutations and no live Sheet import.

### F4 — Ledger primitives in isolated test mode

Status: **not started**

Later implement opening/receipt/usage/adjustment operations with idempotency, atomic transactions, correction/reversal support, audit, and deterministic balances using synthetic/test data first.

## Phase 3 — Shadow migration/reconciliation

Status: **not started**

Import current Sheet state into shadow PostgreSQL, preserve provenance, compare backend projections against the workbook, and report mismatches without silent repair.

## Phase 4 — Dual validation

Status: **not started**

Run representative real workflows through current Sheet + backend shadow path and compare before promotion.

## Phase 5 — Canonical database promotion

Status: **not started; explicit approval required**

Requires parity acceptance, tested backup/restore, and rollback/cutback plan.

## Phase 6 — Private Custom GPT Action experiment

Status: **planned after stable public HTTPS + read-only API**

Start read-only with a revocable scoped service credential. No arbitrary SQL/database credentials.

## Phase 7 — Google Sheets mirror

Status: **future**

After database promotion, DB-to-Sheet projection becomes normal direction; approved Sheet edits translate into typed backend operations.

## Phase 8 — Telegram staff client

Status: **future multi-user client**

Use canonical users/roles and Telegram numeric external identities.

## Phase 9 — Flutter staff application

Status: **future multi-user client**

Use the same backend identity/domain/API model.

## Phase 10 — Monthly archive/export

Status: **future**

Regenerate Main Stock, Daily Usage, This Month Received, and Final Reorder historical outputs from canonical history.

## Current next work

1. Begin F3 read-only domain/API after explicit authorization.
2. Continue independent rechecks of `https://inventory.drthorne.uk/health` until external HTTP 200 + expected JSON are observed.
3. Keep PostgreSQL non-canonical and do not import live inventory until later shadow-migration authorization.

No live inventory import, production stock write authority, Custom GPT Action connection, Telegram/Flutter rollout, Sheet mirror conversion, or DB canonical promotion is enabled yet.

## Continuity rule

After every significant architecture decision, implementation slice, deployment change, migration result, or next-work change:

1. update `ROADMAP.md`;
2. update `NEW_CHAT_BOOTSTRAP.md`;
3. update relevant canonical architecture/operations docs.
