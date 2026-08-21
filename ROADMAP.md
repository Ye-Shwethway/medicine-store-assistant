# Medicine Store Assistant — Project Roadmap

Status: **Phase 2 foundation active; F0/F1 complete, F2 authored and deployment verification pending**

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

Status: **approved and authored; VPS apply/verification pending**

Repository implementation now includes:

- Alembic migration tooling;
- SQLAlchemy + psycopg runtime dependencies;
- initial migration `0001_foundation`;
- user/role/external-identity foundation;
- service-principal/credential metadata foundation;
- product/product-lot stable identity tables;
- operating-month table;
- CMS catalogue version/item tables;
- audit-event attribution foundation;
- `/ready` endpoint for DB connectivity + expected migration revision;
- one-command `deploy/apply_f2_foundation.sh` deployment helper using secret-safe Compose validation.

F2 explicitly does **not** contain stock ledger movements/receipt/usage/adjustment write APIs, live inventory import, Sheet mirror writes, or database canonical promotion.

F2 exit criteria still pending runtime verification:

- repo validator passes at deployed commit;
- image rebuild succeeds;
- migration applies cleanly to the isolated MSA PostgreSQL database;
- `/health` remains HTTP 200 and `database_canonical: false`;
- `/ready` returns HTTP 200 with migration `0001_foundation`;
- DB remains private/no host port;
- unrelated services remain healthy.

### F3 — Core read-only domain/API

Status: **not started**

After F2 runtime verification, implement read-only product/lot/month/catalogue/user-safe diagnostics before real inventory writes.

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

1. Apply and verify F2 migration foundation on the VPS.
2. Recheck external `https://inventory.drthorne.uk/health` when DNS propagation permits.
3. If F2 verification passes, document it and authorize F3 read-only domain/API.

No live inventory import, production stock write authority, Custom GPT Action connection, Telegram/Flutter rollout, Sheet mirror conversion, or DB canonical promotion is enabled yet.

## Continuity rule

After every significant architecture decision, implementation slice, deployment change, migration result, or next-work change:

1. update `ROADMAP.md`;
2. update `NEW_CHAT_BOOTSTRAP.md`;
3. update relevant canonical architecture/operations docs.
