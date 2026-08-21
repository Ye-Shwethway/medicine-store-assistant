# Medicine Store Assistant — New Chat Bootstrap

Use this file for **project-development continuity and memory reconciliation** in a fresh chat.

This is distinct from `NORMAL_CHAT_BOOTSTRAP.md`, which teaches normal chats how to use the published `$msa` skill.

## Canonical repository

`https://github.com/Ye-Shwethway/medicine-store-assistant`

## Required reconciliation order

1. `AGENTS.md`
2. `NEW_CHAT_BOOTSTRAP.md`
3. `ROADMAP.md`
4. `IMPLEMENTATION_PLAN.md`
5. `docs/architecture/README.md`
6. task-relevant architecture/operations docs
7. `skills/medicine-store-assistant/SKILL.md` and task-relevant references for spreadsheet work
8. current repository/runtime evidence

Treat newer verified repository/runtime evidence as authoritative over remembered chat context. Do not mutate live operational state during reconciliation unless the user explicitly authorizes that slice.

## Project boundary

Same-repository monorepo:

- `skills/medicine-store-assistant/` — canonical published `$msa` skill; must remain independently installable
- `docs/architecture/` — canonical design
- `docs/operations/` — runtime/deployment evidence
- `backend/` — deterministic FastAPI/PostgreSQL backend
- `integrations/` — Custom GPT / Sheets / Telegram / Flutter adapters
- `deploy/` — VPS deployment assets

## Current operational authority

The live Google workbook remains authoritative until PostgreSQL is explicitly promoted after shadow/dual validation.

Primary human views:

- Main Stock
- Daily Usage

Generated/workflow views:

- This Month Received — display-only filtered projection
- Reorder / Final Reorder — working/final workflow projections; final approved reorder may be snapshotted historically

## Target architecture

```text
MSA Custom GPT ─┐
Telegram ───────┼──> Inventory API on VPS ───> PostgreSQL
Flutter ────────┘              │
                               ├──> Google Sheets operational mirror
                               └──> Excel monthly exports
```

## Locked F2 domain/access decisions

Approved 2026-08-22:

- initial migration/canonicalization uses one `OPENING_BALANCE` movement per pre-existing lot; month boundaries do not create repeated opening movements;
- normal lot boundary = product + expiry, with receipt lines preserved separately;
- `product_id` remains stable across harmless local-name changes;
- quantities use fixed-point PostgreSQL `NUMERIC(18,3)`; discrete units normally require whole-number values;
- no implicit unit conversion in v1;
- normal writes cannot silently create negative stock; privileged audited reconciliation exceptions require explicit reason;
- historical corrections use reversals/amendments, not destructive rewriting;
- roles = `OWNER`, `ADMIN`, `STAFF`, `READ_ONLY`;
- canonical human identity = backend `user_id`;
- Telegram numeric user ID = external identity link, username = metadata only;
- Flutter will use native MSA credentials/session design independent of Telegram;
- non-human clients use scoped service principals;
- protected operations preserve actor/client/operation attribution.

Canonical record: `docs/architecture/F2_SCHEMA_DECISION_PROPOSAL.md` (approved/locked content despite historical filename).

## Implementation checkpoint

### F0 — VPS inspection

**Verified complete 2026-08-22.**

### F1 — Runtime skeleton

**Verified complete 2026-08-22.**

Verified runtime:

- FastAPI + PostgreSQL containers on VPS;
- API localhost-only at `127.0.0.1:8088`;
- PostgreSQL has no host-published port;
- `/health` HTTP 200 with `database_canonical: false`;
- unrelated VPS services unchanged.

Bamboo/one-time VPS executor role is closed and is not part of ongoing implementation.

### Cloudflare edge

**Configured; end-to-end public health verification pending.**

Configured route:

`inventory.drthorne.uk -> existing managed Cloudflare Tunnel -> http://localhost:8088`

Cloudflare-side route/DNS read-back succeeded and VPS port 8088 remains non-public. Independent HTTPS `/health` verification has not yet succeeded because resolver/cache propagation was still pending. Do not claim full public-route completion until external HTTP 200 + expected JSON are observed.

### F2 — PostgreSQL schema/migration foundation

**Approved and authored; VPS runtime apply/verification pending.**

Repository now contains:

- SQLAlchemy + psycopg + Alembic dependencies;
- `backend/alembic.ini` and Alembic environment;
- migration `0001_foundation`;
- foundation tables for users/roles/external identities, service principals/credential metadata, products/lots, operating months, CMS catalogue versions/items, and audit events;
- `/ready` endpoint that requires PostgreSQL reachability and expected migration `0001_foundation`;
- `deploy/apply_f2_foundation.sh` for secret-safe one-command migration/rebuild/readiness verification.

F2 deliberately does not include stock ledger tables/write APIs, live Sheet import, canonical promotion, Custom GPT writes, Telegram/Flutter rollout, or Sheet mirror mutation.

## Immediate next work

1. Apply/verify F2 on the VPS using the existing sealed runtime environment.
2. Re-test public `https://inventory.drthorne.uk/health` after propagation.
3. If F2 passes, record canonical runtime evidence and move to F3 read-only domain/API.

## F2 expected verification

After deployment:

- repository validator passes;
- migration applies cleanly;
- `/health` remains HTTP 200 and `database_canonical: false`;
- `/ready` returns HTTP 200 with:
  - `ok: true`
  - `database: reachable`
  - `migration: 0001_foundation`
  - `expected_migration: 0001_foundation`
  - `database_canonical: false`
- API remains localhost-only;
- DB has no host-published port;
- unrelated services remain healthy.

## Safety boundary

PostgreSQL is **not canonical yet**. The live Google workbook/source documents remain authoritative. No production inventory data should be imported or written as part of F2.

## Continuity rule

After every significant architecture decision, implementation slice, deployment/migration result, or next-work change:

- update `ROADMAP.md`;
- update this file;
- update relevant architecture/operations docs.

A fresh chat must recover current truth from repository evidence without relying on remembered conversation history.
