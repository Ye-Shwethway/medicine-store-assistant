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

## Project boundary and authority

Same-repository monorepo remains active. The live Google workbook/source evidence remains authoritative until PostgreSQL is explicitly promoted after shadow/dual validation.

## Verified checkpoints

### F0 — VPS inspection

**Verified complete 2026-08-22.**

### F1 — Runtime skeleton

**Verified complete 2026-08-22.** API localhost-only on `127.0.0.1:8088`; MSA PostgreSQL has no host-published port.

### Cloudflare public HTTPS route

**Verified complete 2026-08-22.**

Canonical route:

`https://inventory.drthorne.uk -> Cloudflare HTTPS -> existing managed Tunnel -> http://localhost:8088`

User-side browser verification observed the expected public-safe `/health` JSON over HTTPS. VPS port 8088 remains non-public.

### F2 — PostgreSQL schema/migration foundation

**Verified complete 2026-08-22.**

Canonical evidence: `docs/operations/F2_VPS_MIGRATION_VERIFICATION_2026-08-22.md`.

Migration `0001_foundation` established users/roles/external identities, service principals/credential metadata, products/lots, operating months, CMS catalogue versions/items, and audit-event foundation. PostgreSQL remains non-canonical.

### F3 — Authenticated read-only API

**Verified complete 2026-08-22.**

Canonical evidence: `docs/operations/F3_READ_API_VERIFICATION_2026-08-22.md`.

Verified deployed commit: `dac1a4aa5b218d3c5eda24a636b3c3688979473b`.

- `/health` and `/ready` healthy;
- anonymous `/v1/products` -> HTTP 401;
- authenticated `/v1/products` -> HTTP 200 with empty list before import;
- scoped read credential stored runtime-only with plaintext token protected on VPS and hash in DB;
- product/lot/month/catalogue/access diagnostics are authenticated and read-only;
- no live inventory import and no production stock-write endpoint exists.

### F4 — Synthetic ledger foundation

**Verified complete 2026-08-22.**

Canonical evidence: `docs/operations/F4_SYNTHETIC_LEDGER_VERIFICATION_2026-08-22.md`.

Verified deployed commit: `184f964a86cfb00696f4f2622e41289ab53f165a`.

Verified implementation/runtime:

- migration `0002_ledger` adds `inventory_transactions`;
- permitted transaction types: `OPENING_BALANCE`, `RECEIPT`, `USAGE`, `ADJUSTMENT_POSITIVE`, `ADJUSTMENT_NEGATIVE`;
- fixed-point positive quantity constraint;
- unique `operation_id` idempotency key;
- optional unique `reversal_of_transaction_id` linkage;
- actor linkage to user or service principal;
- deterministic lot balance calculation;
- normal negative-stock guard in the ledger service;
- synthetic verifier passed balance math, duplicate-operation blocking, negative-stock blocking, and linked reversal semantics;
- synthetic fixture data is rolled back and not retained;
- `/health` is healthy with build SHA `184f964a86cfb00696f4f2622e41289ab53f165a` and `database_canonical: false`;
- `/ready` is healthy with database reachable and migration/expected migration both `0002_ledger`;
- transient connection resets during API recreation were followed by successful retry-loop verification and do not represent an unresolved failure.

F4 does **not** expose production inventory write endpoints. It does not import the live Google Sheet, mutate the Sheet, connect Custom GPT writes, or promote PostgreSQL.

## Recommended next minimum safe slice

**F5 — CMS catalogue versioning using synthetic/non-sensitive sample data only.**

This is recommendation-only and is **not yet authorized**.

If authorized, keep F5 limited to deterministic catalogue version/hash storage, idempotent sample import, new/removed/changed diff behavior, current/historical catalogue reads needed for verification, and proof that CMS code changes cannot automatically remap local product/lot identity.

Do not begin live Sheet import, production stock writes, database promotion, Telegram writes, Flutter rollout, Google Sheet mirror conversion, or Custom GPT write Actions without explicit authorization.

## Safety boundary

PostgreSQL is **not canonical yet**. The live Google workbook/source documents remain authoritative. Public/domain API remains read-only for real inventory.

## Continuity rule

After every significant architecture decision, implementation slice, deployment/migration result, or next-work change:

- update `ROADMAP.md`;
- update this file;
- update relevant architecture/operations docs.

A fresh chat must recover current truth from repository evidence without relying on remembered conversation history.
