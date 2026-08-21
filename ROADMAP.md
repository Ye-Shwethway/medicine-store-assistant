# Medicine Store Assistant — Project Roadmap

Status: **Phase 2 foundation active; F0/F1 complete, F2 migration applied and final readiness verification pending**

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

Locked v1 decisions:

- initial migration uses one `OPENING_BALANCE` movement per migrated pre-existing lot; month boundaries do not create repeated opening movements;
- normal lot boundary is product + expiry, while receipt-line provenance stays separate;
- `product_id` is stable; harmless local-name changes do not create a new product;
- quantities use fixed-point `NUMERIC(18,3)` with unit-level whole-number validation for discrete units;
- normal writes may not create negative stock; privileged explicit reconciliation exceptions require audit/reason;
- corrections use reversal/amendment rather than destructive history rewrite;
- roles are `OWNER`, `ADMIN`, `STAFF`, `READ_ONLY`;
- stable backend `user_id` is canonical human identity;
- Telegram numeric user ID is an external identity link;
- Flutter uses native MSA credentials/session design independent of Telegram;
- non-human clients use scoped service principals;
- protected operations preserve actor/client/operation attribution.

Canonical record: `docs/architecture/F2_SCHEMA_DECISION_PROPOSAL.md` (historical filename, approved/locked content).

## Phase 2 — Backend foundation

Status: **active**

### F0 — VPS inspection

Status: **verified complete 2026-08-22**

Evidence: `docs/operations/F0_VPS_INSPECTION_2026-08-22.md`.

### F1 — Runtime skeleton

Status: **verified complete 2026-08-22**

Evidence: `docs/operations/F1_VPS_RUNTIME_VERIFICATION_2026-08-22.md`.

Verified runtime:

- FastAPI + PostgreSQL containers;
- API localhost-only on `127.0.0.1:8088`;
- DB has no host-published port;
- `/health` HTTP 200;
- `database_canonical: false`;
- unrelated VPS services unchanged.

Bamboo/one-time executor is closed and no longer part of the implementation workflow.

### Cloudflare public route

Status: **configured; external health verification pending**

Configured hostname:

`inventory.drthorne.uk -> existing managed Cloudflare Tunnel -> http://localhost:8088`

Route/DNS read-back succeeded. Direct public exposure of VPS port 8088 was not present. Independent public `/health` verification is still pending due resolver/cache propagation; do not claim the HTTPS slice fully complete until HTTP 200 + expected JSON are observed externally.

### F2 — PostgreSQL schema/migration foundation

Status: **migration applied; final readiness verification pending**

Canonical runtime evidence: `docs/operations/F2_VPS_MIGRATION_VERIFICATION_2026-08-22.md`.

Repository/runtime implementation includes:

- Alembic migration tooling;
- SQLAlchemy + psycopg v3 runtime dependencies;
- initial migration `0001_foundation`;
- user/role/external-identity foundation;
- service-principal/credential metadata foundation;
- product/product-lot stable identity tables;
- operating-month table;
- CMS catalogue version/item tables;
- audit-event attribution foundation;
- `/ready` endpoint for DB connectivity + expected migration revision;
- one-command `deploy/apply_f2_foundation.sh` deployment helper using secret-safe Compose validation.

Verified F2 runtime evidence so far:

- repository validator passed;
- API image rebuilt successfully;
- migration `0001_foundation` applied successfully to isolated MSA PostgreSQL;
- API restarted and subsequently returned HTTP 200 on `/health`;
- runtime served build SHA `2fff4408666723159543af900c3df8b8e3dd14fb`;
- `database_canonical: false` remains preserved.

The first apply attempt exposed a SQLAlchemy driver mismatch: plain `postgresql://` selected psycopg2 while the project installs psycopg v3. Repository code now normalizes URLs to `postgresql+psycopg://`; no psycopg2 dependency or VPS-local source patch was introduced.

The successful migration run then hit a transient curl race immediately after API container recreation. Subsequent `/health` was healthy, so `deploy/apply_f2_foundation.sh` is now hardened with retry/backoff for `/health` and `/ready`.

F2 final exit criteria still require one clean hardened verification run showing:

- `/health` HTTP 200 and `database_canonical: false`;
- `/ready` HTTP 200;
- `/ready` reports `database: reachable`;
- migration and expected migration both equal `0001_foundation`.

F2 explicitly does **not** contain stock ledger write APIs, live inventory import, Sheet mirror writes, or database canonical promotion.

### F3 — Core read-only domain/API

Status: **not started**

After F2 final readiness verification, implement read-only product/lot/month/catalogue/user-safe diagnostics before real inventory writes.

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

1. Pull the hardened F2 apply script and run one clean verification pass; migration rerun is idempotent at `0001_foundation`.
2. Recheck external `https://inventory.drthorne.uk/health` when DNS propagation permits.
3. If `/ready` passes, record F2 verified complete and authorize F3 read-only domain/API.

No live inventory import, production stock write authority, Custom GPT Action connection, Telegram/Flutter rollout, Sheet mirror conversion, or DB canonical promotion is enabled yet.

## Continuity rule

After every significant architecture decision, implementation slice, deployment change, migration result, or next-work change:

1. update `ROADMAP.md`;
2. update `NEW_CHAT_BOOTSTRAP.md`;
3. update relevant canonical architecture/operations docs.
