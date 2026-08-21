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

Primary human views are Main Stock and Daily Usage. This Month Received and Reorder/Final Reorder are generated/workflow projections; final approved reorder may be snapshotted historically.

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
- Flutter uses native MSA credentials/session design independent of Telegram;
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

Cloudflare-side route/DNS read-back succeeded and VPS port 8088 remains non-public. User may verify externally with a browser or `curl -i https://inventory.drthorne.uk/health`. Close the Cloudflare slice only after HTTP 200 + expected public-safe health JSON are observed.

### F2 — PostgreSQL schema/migration foundation

**Verified complete 2026-08-22.**

Canonical evidence: `docs/operations/F2_VPS_MIGRATION_VERIFICATION_2026-08-22.md`.

Final verified runtime:

- repository validator passed;
- SQLAlchemy + psycopg v3 + Alembic foundation deployed;
- migration `0001_foundation` applied successfully;
- users/roles/external identities, service principals/credential metadata, products/lots, operating months, CMS catalogue versions/items, and audit-event foundation exist;
- `/health` returned HTTP 200 with build SHA `a9cd98e4af6fd20aee07a783f82daf46d557ac7a` and `database_canonical: false`;
- `/ready` returned HTTP 200 with `database: reachable`, migration `0001_foundation`, expected migration `0001_foundation`, and `database_canonical: false`;
- deploy helper retries through transient container-recreate connection resets until stable readiness;
- runtime PostgreSQL URLs use the intended psycopg v3 dialect.

### F3 — Authenticated read-only domain/API

**Authorized and authored; VPS verification pending.**

Repository implementation now includes authenticated read-only endpoints for:

- products;
- lots;
- operating months;
- CMS catalogue versions/items;
- safe access-control counts/summary.

Security model:

- domain reads require a bearer credential with `inventory:read` (or `*`) scope;
- token is SHA-256 hashed before lookup against active `service_credentials` joined to active `service_principals`;
- anonymous domain reads return 401;
- no password hashes, service-key hashes, Telegram IDs, or credential material are returned by the safe access summary;
- `/health` remains intentionally public-safe;
- no inventory write endpoints exist in F3.

Operational tooling:

- `python -m app.service_key_cli` creates a high-entropy service token, stores only its hash/scopes in PostgreSQL, and can print raw token only for controlled bootstrap use;
- `deploy/apply_f3_read_api.sh` updates runtime build SHA, validates/builds/starts the API, waits for `/health` and `/ready`, verifies anonymous `/v1/products` is 401, generates a scoped verification credential, stores its plaintext token only in `/opt/medicine-store-assistant/secrets/f3_read_api.token` with mode 0600, verifies authenticated `/v1/products` HTTP 200, and does not print the token.

Current DB contains no live inventory import, so authenticated product reads are expected to return an empty list until the later shadow-migration slice.

## Immediate next work

1. Deploy/verify F3 on the VPS with `deploy/apply_f3_read_api.sh`.
2. Accept user-side public `/health` evidence and close the Cloudflare slice if it returns HTTP 200 + expected JSON.
3. After F3 verification, decide the next minimum slice; do not jump directly to live stock writes or database promotion.

## Safety boundary

PostgreSQL is **not canonical yet**. The live Google workbook/source documents remain authoritative. No live inventory import, stock-write authority, Custom GPT Action connection, Telegram/Flutter rollout, Sheet mirror mutation, or database promotion is active.

## Continuity rule

After every significant architecture decision, implementation slice, deployment/migration result, or next-work change:

- update `ROADMAP.md`;
- update this file;
- update relevant architecture/operations docs.

A fresh chat must recover current truth from repository evidence without relying on remembered conversation history.
