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

Canonical record: `docs/architecture/F2_SCHEMA_DECISION_PROPOSAL.md`.

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

Cloudflare-side route/DNS read-back succeeded and VPS port 8088 remains non-public. Independent HTTPS `/health` verification is still pending.

### F2 — PostgreSQL schema/migration foundation

**Migration applied; final readiness verification pending.**

Canonical evidence: `docs/operations/F2_VPS_MIGRATION_VERIFICATION_2026-08-22.md`.

Implemented foundation:

- SQLAlchemy + psycopg v3 + Alembic;
- migration `0001_foundation`;
- users/roles/external identities;
- service principals/credential metadata;
- products/product lots;
- operating months;
- CMS catalogue versions/items;
- audit-event attribution foundation;
- `/ready` endpoint for database reachability + expected migration revision.

Verified runtime so far:

- repository validator passed;
- migration `0001_foundation` applied successfully;
- API restarted successfully and subsequently served `/health` HTTP 200;
- deployed runtime health response reported build SHA `2fff4408666723159543af900c3df8b8e3dd14fb` and `database_canonical: false`.

First F2 attempt failed before migration because a plain `postgresql://` URL caused SQLAlchemy to choose psycopg2 while the project intentionally uses psycopg v3. Repo code was fixed to normalize to `postgresql+psycopg://`; no VPS-local patch or psycopg2 package was added.

The successful migration run then exited on an immediate post-container-recreate curl race. Subsequent `/health` was healthy, confirming this was a verification timing race rather than a steady-state service failure. `deploy/apply_f2_foundation.sh` now retries `/health` and `/ready` after recreation.

F2 final completion requires one clean hardened apply/verification run showing:

- `/health` HTTP 200 and `database_canonical: false`;
- `/ready` HTTP 200;
- `database: reachable`;
- `migration: 0001_foundation`;
- `expected_migration: 0001_foundation`.

Re-running `alembic upgrade head` is expected to be idempotent when already at `0001_foundation`.

## Immediate next work

1. Pull current `main` and run the hardened F2 apply script once.
2. If `/ready` passes, mark F2 verified complete and begin F3 read-only API work.
3. Independently re-test public `https://inventory.drthorne.uk/health` when DNS propagation permits.

## Safety boundary

PostgreSQL is **not canonical yet**. The live Google workbook/source documents remain authoritative. No live inventory import, stock-write authority, Custom GPT Action connection, Telegram/Flutter rollout, Sheet mirror mutation, or database promotion is active.

## Continuity rule

After every significant architecture decision, implementation slice, deployment/migration result, or next-work change:

- update `ROADMAP.md`;
- update this file;
- update relevant architecture/operations docs.

A fresh chat must recover current truth from repository evidence without relying on remembered conversation history.
