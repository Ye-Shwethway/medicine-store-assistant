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

Cloudflare-side route/DNS read-back succeeded and VPS port 8088 remains non-public. Independent external fetch has still not produced a confirmed public HTTP 200 response, so keep this slice open until verified.

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
- runtime PostgreSQL URLs are normalized to the intended `postgresql+psycopg://` driver.

F2 did not enable stock ledger writes, import live inventory, mutate the Sheet, connect Custom GPT Actions, deploy Telegram/Flutter, or promote PostgreSQL to canonical authority.

## Immediate next work

F3 — Core read-only domain/API — is the next implementation slice but is **not yet started**.

Target F3 scope:

- read-only product and lot lookup/listing;
- operating-month read diagnostics;
- CMS catalogue/version read diagnostics;
- safe user/account diagnostics with no credential exposure;
- typed response models and stable API conventions;
- no inventory mutations and no live Sheet import.

Separately, continue independent external checks of `https://inventory.drthorne.uk/health` until public HTTP 200 + expected JSON are observed.

## Safety boundary

PostgreSQL is **not canonical yet**. The live Google workbook/source documents remain authoritative. No live inventory import, stock-write authority, Custom GPT Action connection, Telegram/Flutter rollout, Sheet mirror mutation, or database promotion is active.

## Continuity rule

After every significant architecture decision, implementation slice, deployment/migration result, or next-work change:

- update `ROADMAP.md`;
- update this file;
- update relevant architecture/operations docs.

A fresh chat must recover current truth from repository evidence without relying on remembered conversation history.
