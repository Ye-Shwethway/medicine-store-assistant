# Medicine Store Assistant — Project Roadmap

Status: **Phase 2 foundation active; F0 and F1 verified complete; Cloudflare route configured, public health verification pending**

This roadmap tracks the full Medicine Store Assistant project, not only the published `$msa` skill. Keep it synchronized with `NEW_CHAT_BOOTSTRAP.md` after significant changes.

## Project goals

Build a reliable medicine-store information system that preserves the familiar spreadsheet workflow while moving canonical data integrity into deterministic backend infrastructure.

Primary goals:

- preserve the published Git-backed `$msa` skill;
- preserve source-document truth, lot separation, local naming, and Excel/Google Sheets compatibility;
- introduce stable product/lot identity independent of spreadsheet row number;
- preserve complete monthly history and full CMS catalogue history;
- move arithmetic, idempotency, constraints, transactions, audit, authentication and authorization into deterministic backend code;
- expose a safe typed API for Custom GPT, Telegram, Flutter, staff users and Sheet integration;
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

Staff access is a first-class backend concern. Human users, external identities (such as Telegram), service clients and audit attribution must resolve to stable backend identities rather than being embedded ad hoc in inventory rows.

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

Status: **foundation design sufficient for reversible runtime work; schema/auth gates remain open**

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
- `docs/architecture/USER_ACCESS_AND_AUTHORIZATION.md`
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
- Future staff use through Telegram/Flutter requires a backend user/access domain with stable user identities, roles, external-identity links, revocation/deactivation and audit attribution.

Schema implementation still requires decisions in `docs/architecture/DECISIONS_AND_OPEN_QUESTIONS.md`, including opening-balance representation, lot granularity, quantity precision, negative-stock policy, historical-correction semantics, and v1 auth/access choices.

## Phase 2 — Backend foundation

Status: **active**

### Slice F0 — VPS inspection and safe host preparation

Status: **completed 2026-08-22**

Verified evidence: `docs/operations/F0_VPS_INSPECTION_2026-08-22.md`.

### Slice F1 — Repository Runtime Skeleton

Status: **verified complete 2026-08-22**

Canonical evidence: `docs/operations/F1_VPS_RUNTIME_VERIFICATION_2026-08-22.md`.

Verified results:

- deployed canonical commit `408dcbbdba6c579f446d303197c9071340188619`;
- repository validator PASS (`medicine-store-assistant` plugin 1.1.0);
- FastAPI runtime skeleton deployed in Docker;
- PostgreSQL 16 Alpine container deployed privately on the project Docker network;
- API bound only to `127.0.0.1:8088`;
- PostgreSQL has no host-published port;
- `/health` returned HTTP 200 with expected build/environment metadata and `database_canonical: false`;
- API/PostgreSQL memory usage remained well below configured caps at verification;
- unrelated VPS containers/services remained unchanged.

Operational hardening learned in F1:

- rendered `docker compose config` output can expose interpolated runtime secrets; use secret-safe validation such as `config --quiet` when appropriate and never copy rendered secret-bearing configuration into logs/docs/chat.

### Cloudflare public route

Status: **configured 2026-08-22; public end-to-end health verification pending**

Evidence: `docs/operations/CLOUDFLARE_ROUTE_2026-08-22.md`.

Configured route:

`https://inventory.drthorne.uk` → existing managed Cloudflare Tunnel → `http://localhost:8088`

Verified Cloudflare-side facts:

- hostname was unused before assignment;
- existing managed tunnel was reused;
- proxied CNAME/tunnel hostname route was created additively;
- unrelated existing tunnel routes were preserved;
- no Worker, D1, KV, R2, Pages, Load Balancer, Access policy, paid Cloudflare service, or host reverse proxy was added;
- VPS port `8088` remains non-public and localhost-bound.

Immediately after creation, available execution environments could not resolve the new hostname, so HTTP 200 + expected public `/health` JSON has **not yet been independently verified**. Do not mark this slice fully complete until that succeeds.

### Next gate — architecture decisions before F2 schema

Status: **current planning work**

Before canonical inventory/auth tables or migrations, resolve the F2-gating decisions in `docs/architecture/DECISIONS_AND_OPEN_QUESTIONS.md` and `USER_ACCESS_AND_AUTHORIZATION.md`.

Key decisions include:

- opening-balance representation;
- lot granularity;
- product rename/identity semantics;
- quantity precision;
- negative-stock policy;
- historical correction semantics;
- minimal v1 user/role model;
- external identity linkage for Telegram;
- Flutter authentication/session approach;
- service identity/scopes for Custom GPT and other integrations.

### Slice F2 — PostgreSQL schema foundation

Status: **not yet authorized**

After gating decisions are locked, introduce migration tooling, stable user/product/lot/month/catalogue entities, database readiness and least-privilege application credentials. No live inventory import yet.

### Slice F3 — Core read-only domain/API

Status: **not started**

Implement stable identities and read-only APIs before real stock writes.

### Slice F4 — Ledger primitives in isolated test mode

Status: **not started**

Implement typed opening/receipt/usage/adjustment operations with idempotency, atomic transactions, reversal/correction support, audit and deterministic balance calculation using synthetic data only.

## Phase 3 — Shadow migration and reconciliation

Status: **not started**

Import current live Sheet state into shadow PostgreSQL, preserve provenance, compare backend projections against the workbook, and surface mismatches without silent repair.

## Phase 4 — Dual validation

Status: **not started**

Run representative real operations through current Sheet workflow plus backend shadow path and compare results before promotion.

## Phase 5 — Canonical database promotion

Status: **not started; explicit approval required**

Requires successful parity validation, tested backups/restores, measurable acceptance criteria and rollback/cutback plan.

## Phase 6 — Private Custom GPT Action experiment

Status: **planned after public HTTPS + stable read-only API**

Start with read-only Actions only. Version-control OpenAPI under `integrations/custom-gpt/`, use a revocable scoped service credential, and expose no arbitrary SQL/database credentials.

## Phase 7 — Google Sheets backend mirror

Status: **future**

After database promotion, make DB-to-Sheet projection the normal direction and translate approved Sheet-originated edits into typed operations.

## Phase 8 — Telegram client

Status: **future multi-user client**

Use stable backend user identities and role-based authorization. Telegram numeric user ID is an external identity link, not the canonical user primary key. Authentication, authorization, idempotency, audit and read-back are required before writes.

## Phase 9 — Flutter application

Status: **future multi-user client**

Use the same backend users/roles and typed API. Flutter authentication must not create a second user or inventory model.

## Phase 10 — Mature monthly archive/export

Status: **future**

Regenerate familiar Main Stock, Daily Usage, This Month Received and Final Reorder outputs from canonical history.

## Current checkpoint

F0 and F1 are verified complete. Bamboo/one-time VPS executor is no longer part of the implementation workflow.

Cloudflare route is configured but public `/health` verification is still pending DNS/edge propagation.

Current next work:

1. independently re-check `https://inventory.drthorne.uk/health` after propagation and close the Cloudflare route slice when it returns the expected HTTP 200 payload;
2. resolve F2 schema + v1 user/auth gating decisions;
3. authorize and implement F2 only after those decisions are documented.

No canonical inventory schema, live import, Custom GPT Action or production write authority is enabled yet.

## Continuity rule

After every significant architecture decision, implementation slice, deployment change, migration/reconciliation result or next-work change:

1. update `ROADMAP.md`;
2. update `NEW_CHAT_BOOTSTRAP.md`;
3. update relevant architecture/operations docs.

A new chat must be able to determine completed work, current truth and the next authorized slice from repository documents alone.
