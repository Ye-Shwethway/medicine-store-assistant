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

Canonical route: `https://inventory.drthorne.uk -> Cloudflare HTTPS -> existing managed Tunnel -> http://localhost:8088`.

### F2 — PostgreSQL schema/migration foundation
**Verified complete 2026-08-22.**

Canonical evidence: `docs/operations/F2_VPS_MIGRATION_VERIFICATION_2026-08-22.md`.

### F3 — Authenticated read-only API
**Verified complete 2026-08-22.**

Canonical evidence: `docs/operations/F3_READ_API_VERIFICATION_2026-08-22.md`.

Verified deployed commit: `dac1a4aa5b218d3c5eda24a636b3c3688979473b`.

No live inventory import and no production stock-write endpoint exists.

### F4 — Synthetic ledger foundation
**Verified complete 2026-08-22.**

Canonical evidence: `docs/operations/F4_SYNTHETIC_LEDGER_VERIFICATION_2026-08-22.md`.

Verified deployed commit: `184f964a86cfb00696f4f2622e41289ab53f165a`.

F4 verified migration `0002_ledger`, deterministic balance math, operation-id idempotency, normal negative-stock guard, reversal/correction linkage, rollback of synthetic fixtures, healthy `/health`, healthy `/ready`, and `database_canonical: false`.

## F5 — Synthetic CMS catalogue versioning

**Authorized and authored; VPS verification pending.**

Repository now contains:

- migration `0003_catalogue` adding catalogue row-count/import/parser metadata, source row number, and DB-level unique source-hash protection;
- deterministic SHA-256 catalogue content hashing;
- identical-source idempotent import returning the prior version;
- historical full-version storage in `cms_catalogue_versions` + `cms_catalogue_items`;
- deterministic diff for new/removed codes and changed source fields;
- price-only change classification;
- identity-shift candidate detection when the same CMS code changes brand/description/form/type/class;
- no automatic local product/lot remapping from CMS code;
- synthetic verifier that proves hash idempotency, historical version availability, add/remove diff, price diff, and identity-shift guard;
- verifier transaction rollback so synthetic catalogue data is not retained;
- `deploy/apply_f5_catalogue_versioning.sh` for migration + verifier + health/readiness verification;
- `/ready` now expects `0003_catalogue` after deployment.

F5 does **not** ingest a live CMS catalogue, import live Google Sheet inventory, mutate local item mappings, change production prices, create stock movement, mutate Sheets, enable Telegram/Flutter/GPT writes, or promote PostgreSQL.

## Immediate next work

Run:

```bash
cd /opt/medicine-store-assistant/app/repo && git pull --ff-only && bash deploy/apply_f5_catalogue_versioning.sh
```

Expected F5 evidence:

- repository validator PASS;
- Alembic `0002_ledger -> 0003_catalogue`;
- `F5 synthetic catalogue verification PASS`;
- `hash_idempotency=pass version_history=pass add_remove_diff=pass price_diff=pass identity_shift_guard=pass`;
- `/health` healthy with `database_canonical: false`;
- `/ready` migration and expected migration both `0003_catalogue`.

If the VPS output reveals a repository-side failure, fix the canonical repository rather than applying an ad-hoc VPS patch.

## Safety boundary

PostgreSQL is **not canonical yet**. The live Google workbook/source documents remain authoritative. Public/domain API remains read-only for real inventory.

Do not begin live CMS catalogue ingestion, live Sheet shadow import, production stock writes, database promotion, Telegram writes, Flutter rollout, Google Sheet mirror conversion, or Custom GPT write Actions without explicit authorization.

## Continuity rule

After every significant architecture decision, implementation slice, deployment/migration result, or next-work change:

- update `ROADMAP.md`;
- update this file;
- update relevant canonical architecture/operations docs.

A fresh chat must recover current truth from repository evidence without relying on remembered conversation history.
