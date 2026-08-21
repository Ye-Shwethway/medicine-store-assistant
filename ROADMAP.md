# Medicine Store Assistant — Project Roadmap

Status: **Phase 2 foundation active; F0/F1/F2/F3/F4 verified complete; F5 authored and VPS verification pending**

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

## Phase 2 — Backend foundation

Status: **active**

### F0 — VPS inspection
Status: **verified complete 2026-08-22**

### F1 — Runtime skeleton
Status: **verified complete 2026-08-22**

### Cloudflare public HTTPS route
Status: **verified complete 2026-08-22**

Canonical path: `https://inventory.drthorne.uk -> Cloudflare HTTPS edge -> managed Tunnel -> http://localhost:8088`.

### F2 — PostgreSQL schema/migration foundation
Status: **verified complete 2026-08-22**

Evidence: `docs/operations/F2_VPS_MIGRATION_VERIFICATION_2026-08-22.md`.

### F3 — Authenticated read-only domain/API
Status: **verified complete 2026-08-22**

Evidence: `docs/operations/F3_READ_API_VERIFICATION_2026-08-22.md`.

### F4 — Ledger primitives in isolated synthetic/test mode
Status: **verified complete 2026-08-22**

Evidence: `docs/operations/F4_SYNTHETIC_LEDGER_VERIFICATION_2026-08-22.md`.

Verified deployed commit: `184f964a86cfb00696f4f2622e41289ab53f165a`.

F4 proved deterministic balance calculation, duplicate-operation/idempotency protection, normal negative-stock blocking, linked reversal/correction semantics, rollback of synthetic fixtures, and readiness at migration `0002_ledger`. PostgreSQL remains non-canonical and no production inventory-write endpoint exists.

### F5 — CMS catalogue versioning with synthetic/non-sensitive data

Status: **authorized and authored; VPS verification pending**

Purpose: prove deterministic catalogue archival/version/diff behavior without importing or mutating live medicine-store inventory.

Repository implementation includes:

- migration `0003_catalogue` extending catalogue version metadata with row count, import status, parser version, note, source-row number, and DB-level unique source hash;
- deterministic SHA-256 catalogue content hashing over source-preserving row fields;
- idempotent identical-source import returning the existing catalogue version rather than creating a duplicate;
- full per-version catalogue row persistence using existing `cms_catalogue_versions` and `cms_catalogue_items` tables;
- deterministic version diff for new codes, removed codes, changed fields, price-only changes, and identity-shift candidates;
- explicit identity-sensitive fields (`brand_name`, `description`, `form`, `type`, `class_name`) used only to flag possible code reuse/identity shift; no local product or lot mapping is changed automatically;
- synthetic verifier covering hash idempotency, historical version availability, add/remove diff, price-only diff, and same-code incompatible-identity detection;
- synthetic verifier transaction rollback so sample catalogue versions/items are not retained;
- `deploy/apply_f5_catalogue_versioning.sh` to validate the repository, build the API, apply migration, run the synthetic verifier, restart the API, and verify `/health` and `/ready`;
- `/ready` now expects migration `0003_catalogue` after F5 deployment.

F5 does **not** read the live CMS Google Sheet, import a real CMS price list, mutate local inventory mappings, update production prices, create stock movements, mutate Google Sheets, enable client writes, or promote PostgreSQL.

Current VPS verification command:

```bash
cd /opt/medicine-store-assistant/app/repo && git pull --ff-only && bash deploy/apply_f5_catalogue_versioning.sh
```

Expected success evidence includes:

- repository validator PASS;
- Alembic upgrade `0002_ledger -> 0003_catalogue`;
- `F5 synthetic catalogue verification PASS`;
- `hash_idempotency=pass`;
- `version_history=pass`;
- `add_remove_diff=pass`;
- `price_diff=pass`;
- `identity_shift_guard=pass`;
- `/health` with `database_canonical: false`;
- `/ready` with migration and expected migration both `0003_catalogue`.

## Phase 3 — Shadow migration/reconciliation

Status: **not started**

No live Sheet shadow import is authorized by F5. Any future shadow migration requires a separate explicit slice and must preserve provenance and workbook authority.

## Phase 4 — Dual validation
Status: **not started**

## Phase 5 — Canonical database promotion
Status: **not started; explicit approval required**

## Phase 6 — Private Custom GPT Action experiment
Status: **read-only experiment possible later; not connected yet**

## Phase 7 — Google Sheets mirror
Status: **future**

## Phase 8 — Telegram staff client
Status: **future**

## Phase 9 — Flutter staff application
Status: **future**

## Phase 10 — Monthly archive/export
Status: **future**

## Current next work

1. Run the F5 VPS verification command above and inspect its exact output.
2. If verification passes, record F5 canonical runtime evidence and mark F5 verified complete.
3. Do not begin live CMS catalogue ingestion, live Sheet shadow import, production inventory writes, database promotion, Telegram writes, Flutter rollout, Sheet mirror conversion, or Custom GPT write Actions without a later explicit slice.

## Continuity rule

After every significant architecture decision, implementation slice, deployment change, migration result, or next-work change:

1. update `ROADMAP.md`;
2. update `NEW_CHAT_BOOTSTRAP.md`;
3. update relevant canonical architecture/operations docs.
