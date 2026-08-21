# Medicine Store Assistant — Project Roadmap

Status: **Phase 2 foundation started; F0 complete, F1 authorized**

This roadmap tracks the full Medicine Store Assistant project, not only the published `$msa` skill. Keep it synchronized with `NEW_CHAT_BOOTSTRAP.md` after significant changes.

## Project goals

Build a reliable medicine-store information system that preserves the familiar spreadsheet workflow while moving canonical data integrity into deterministic backend infrastructure.

Primary goals:

- preserve the published Git-backed `$msa` skill;
- preserve source-document truth, lot separation, local naming, and Excel/Google Sheets compatibility;
- introduce stable product/lot identity independent of spreadsheet row number;
- preserve complete monthly history and full CMS catalogue history;
- move arithmetic, idempotency, constraints, transactions, and audit into deterministic backend code;
- expose a safe typed API for Custom GPT, Telegram, Flutter, and Sheet integration;
- reuse the existing VPS and Cloudflare Free/custom domain where useful;
- avoid big-bang migration and unnecessary paid infrastructure.

## Architecture baseline

```text
MSA Custom GPT ─┐
Telegram ───────┼──> Inventory API on VPS ───> PostgreSQL
Flutter ────────┘              │
                               ├──> Google Sheets operational mirror
                               └──> Excel monthly exports
```

GitHub remains code/docs distribution. Operational/private data and secrets must never be committed to the public repository.

## Phase 0 — Existing skill and workbook foundation

Status: **completed / active production workflow**

Established:

- canonical Git-backed skill at `skills/medicine-store-assistant/`;
- `$msa` invocation alias;
- source-authority hierarchy and cautious CMS identity matching;
- fixed-asset boundary;
- visual marking and read-back verification;
- tab sequencing/persistence policy;
- Main Stock new-lot insertion rules;
- Daily Usage structural parity and bidirectional synchronization contract;
- live Daily Usage parity repair completed;
- full AJ/AK recalculation and Main H/J reverse synchronization completed.

The Google workbook remains authoritative until database promotion is explicitly approved after shadow validation.

## Phase 1 — Canonical architecture documentation

Status: **foundation design sufficient to begin reversible runtime work; schema-gating questions remain open**

Canonical documents include:

- `docs/architecture/CANONICAL_INVENTORY_ARCHITECTURE.md`
- `docs/architecture/INVENTORY_DATA_MODEL.md`
- `docs/architecture/MONTHLY_LIFECYCLE.md`
- `docs/architecture/CMS_CATALOGUE_VERSIONING.md`
- `docs/architecture/INVENTORY_INTEGRITY_AND_AUDIT.md`
- `docs/architecture/SHEET_MIRROR_AND_COMPATIBILITY.md`
- `docs/architecture/API_AND_CLIENT_ARCHITECTURE.md`
- `docs/architecture/MIGRATION_AND_SHADOW_VALIDATION.md`
- `docs/architecture/DECISIONS_AND_OPEN_QUESTIONS.md`
- `IMPLEMENTATION_PLAN.md`
- `docs/operations/VPS_DEPLOYMENT.md`
- `docs/operations/BACKUP_AND_RECOVERY.md`

Locked clarifications:

- Main Stock and Daily Usage are primary operational views.
- This Month Received is a display-only filtered projection, not an independent canonical store.
- Reorder/Final Reorder are workflow/display projections; the final user-approved reorder may be preserved in monthly history.
- Spreadsheet row numbers are not canonical identities.
- Full CMS catalogue versions should be retained historically.
- Backend calculations and integrity are deterministic, not LLM-authored.
- Same repository remains monorepo-style; published skill path stays stable.
- Custom GPT Actions → VPS API is the preferred first direct AI-access experiment.

Schema implementation still requires decisions listed in `docs/architecture/DECISIONS_AND_OPEN_QUESTIONS.md`, including opening-balance representation, lot granularity, quantity precision, negative-stock policy, and historical-correction semantics.

## Phase 2 — Backend foundation

Status: **started**

### Slice F0 — VPS inspection and safe host preparation

Status: **completed 2026-08-22**

Verified evidence is recorded in `docs/operations/F0_VPS_INSPECTION_2026-08-22.md`.

Key results:

- Ubuntu 24.04.4 LTS x86_64, 2 vCPU, 3.3 GiB RAM, 1.5 GiB swap, 63 GiB root disk;
- Docker Engine and Docker Compose already available;
- managed-token `cloudflared` tunnel active; hostname routing lives in Cloudflare dashboard/Zero Trust;
- no host reverse proxy currently used;
- dedicated `/opt/medicine-store-assistant/` host area and non-login `medstore` user prepared;
- no application code cloned, credentials created, or public MSA port exposed;
- unrelated PostgreSQL services already exist and must not be reused;
- MSA API must use localhost-only host binding; DB should remain private to the Docker network;
- RAM/swap headroom is tight, so API/PostgreSQL require conservative memory limits and minimal supporting services.

### Slice F1 — Repository Runtime Skeleton

Status: **authorized / next**

Purpose: establish a runnable backend/container skeleton without choosing irreversible inventory schema semantics.

Authorized F1 scope:

- create sibling `backend/`, `deploy/`, and integration placeholder areas while preserving `skills/medicine-store-assistant/`;
- minimal Inventory API service with deterministic `/health` endpoint and build/version metadata;
- Dockerfile and Compose definition;
- define an isolated PostgreSQL service/container in Compose with private Docker networking and conservative memory limits, but **do not create canonical inventory tables/migrations yet**;
- API host bind must be localhost-only, initially targeting `127.0.0.1:8088` after a fresh conflict check;
- no public database port;
- `.env.example` and `.gitignore` only; no real secrets in Git;
- local/container build and health verification;
- no Cloudflare hostname route yet;
- no Custom GPT yet;
- no Google Sheet mutation or database canonical promotion.

F1 exit criteria:

- repository validator remains valid;
- containerized API builds/starts;
- `/health` returns deterministic service/environment/version/status fields;
- Compose config validates;
- PostgreSQL container definition is isolated and secret-driven;
- published skill path and plugin packaging remain unaffected.

### Slice F2 — PostgreSQL schema foundation

Status: **not yet authorized**

Before F2 migrations/tables, resolve schema-gating domain questions in `DECISIONS_AND_OPEN_QUESTIONS.md`.

Then introduce migration tooling, stable product/lot/month/catalogue entities, connection readiness, and least-privilege application credentials. No live inventory import yet.

### Slice F3 — Core read-only domain/API

Status: **not started**

Implement stable identities and read-only APIs/diagnostics before real stock writes.

### Slice F4 — Ledger primitives in isolated test mode

Status: **not started**

Implement typed opening/receipt/usage/adjustment operations with idempotency, atomic transactions, reversal/correction support, audit, and deterministic balance calculation using synthetic data only.

## Phase 3 — Shadow migration and reconciliation

Status: **not started**

Import current live Sheet state into shadow PostgreSQL, preserve provenance, compare backend projections against Main Stock/Daily Usage/received/reorder behavior, and surface mismatches without silent repair.

## Phase 4 — Dual validation

Status: **not started**

Run representative real operations through current Sheet workflow plus backend shadow path and compare results before promotion.

## Phase 5 — Canonical database promotion

Status: **not started; explicit approval required**

Requires successful parity validation, tested backups/restores, measurable acceptance criteria, and rollback/cutback plan.

## Phase 6 — Private Custom GPT Action experiment

Status: **planned after stable read-only API + HTTPS hostname**

Start with read-only Actions only. Version-control OpenAPI under `integrations/custom-gpt/`, use a revocable scoped credential, and expose no arbitrary SQL/database credentials.

## Phase 7 — Google Sheets backend mirror

Status: **future**

After database promotion, make DB-to-Sheet projection the normal direction and translate approved Sheet-originated edits into typed operations rather than unrestricted last-write-wins sync.

## Phase 8 — Telegram client

Status: **future**

Use the same typed API. Authentication, authorization, idempotency, audit, and read-back are required before writes.

## Phase 9 — Flutter application

Status: **future**

Use the same typed API and domain model; do not create a second source of truth.

## Phase 10 — Mature monthly archive/export

Status: **future**

Regenerate familiar Main Stock, Daily Usage, This Month Received, and Final Reorder historical outputs from canonical history.

## Current checkpoint

Current authorized work: **F1 — Repository Runtime Skeleton**.

Do not begin canonical inventory schema/migrations, Cloudflare public hostname routing, Custom GPT creation, live inventory import, or production write authority as part of F1.

## Continuity rule

After every significant architecture decision, implementation slice, deployment change, migration/reconciliation result, or next-work change:

1. update `ROADMAP.md`;
2. update `NEW_CHAT_BOOTSTRAP.md`;
3. update relevant architecture/operations docs.

A new chat must be able to determine completed work, current truth, and the next authorized slice from repository documents alone.
