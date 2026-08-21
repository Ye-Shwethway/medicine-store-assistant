# Medicine Store Assistant — New Chat Bootstrap

Use this file for **project-development continuity and memory reconciliation** in a fresh chat.

This file is not the same as `NORMAL_CHAT_BOOTSTRAP.md`:

- `NORMAL_CHAT_BOOTSTRAP.md` teaches a normal chat how to load and operate the published `$msa` skill against the authorized workbook.
- `NEW_CHAT_BOOTSTRAP.md` restores the **project-development checkpoint**: architecture, implementation status, locked decisions, current risks, and next authorized slice.

## Canonical repository

`https://github.com/Ye-Shwethway/medicine-store-assistant`

## Required reconciliation order

At the start of a development chat, read and reconcile in this order:

1. `AGENTS.md`
2. `NEW_CHAT_BOOTSTRAP.md`
3. `ROADMAP.md`
4. `IMPLEMENTATION_PLAN.md`
5. `docs/architecture/README.md`
6. the task-relevant architecture/operations documents
7. `skills/medicine-store-assistant/SKILL.md` and task-relevant references when spreadsheet operations are involved
8. current repository code/config/runtime evidence once implementation exists

Treat newer verified repository/runtime evidence as authoritative over remembered chat context.

Do not modify production, the live workbook, backend state, deployment, schema, or integrations during reconciliation unless the user explicitly authorizes that slice.

## Project identity and repository boundary

Medicine Store Assistant is now a broader medicine-store information-system project while preserving its original Git-backed workflow skill.

Same-repository monorepo direction:

- `skills/medicine-store-assistant/` — canonical published Git-backed skill; alias `$msa`
- `docs/architecture/` — canonical domain/system design
- `docs/operations/` — deployment/backup/runtime evidence
- `backend/` — deterministic Inventory API/runtime when implemented
- `integrations/` — Custom GPT, Google Sheets, Telegram, Flutter adapters
- `deploy/` — VPS deployment assets

The published skill folder must remain independently installable and must not be moved, renamed, or buried by backend work.

## Current operational authority

The live Google workbook remains authoritative under the existing MSA skill until PostgreSQL is explicitly promoted after shadow/dual validation.

Human-facing operational model:

- `Main Stock` — primary lot-level inventory view
- `Daily Usage` — primary monthly usage view
- `This Month Received` — display-only/filtered projection, not an independent canonical store
- `Reorder` / `Final Reorder` — workflow/display projections; final user-approved reorder may be preserved in monthly history

Daily Usage contract remains:

- Main `A/B/F/G/C` → Daily `A/B/C/D/AM`
- Daily `E:AI` = day 1–31 usage inputs
- Daily `AJ = SUM(E:AI)`
- Daily `AK = C + D - AJ`
- Daily `AJ` → Main `J This Month Usage`
- Daily `AK` → Main `H Stock Status Today`
- never write calculated current balance back to Main `F Remaining Stock`

## Locked target architecture

```text
MSA Custom GPT ─┐
Telegram ───────┼──> Inventory API on VPS ───> PostgreSQL
Flutter ────────┘              │
                               ├──> Google Sheets operational mirror
                               └──> Excel monthly exports
```

Infrastructure direction:

- reuse the existing VPS;
- PostgreSQL on VPS becomes canonical only after migration validation and explicit promotion;
- Cloudflare Free/custom domain may provide stable public HTTPS entry routing;
- GitHub stores code/docs only, never live credentials/private operational data;
- AI clients use typed API operations, never arbitrary SQL/database credentials.

## Canonical data principles

- stable `product_id` identifies a local product;
- stable `lot_id` identifies a stock/expiry lot;
- spreadsheet row order is presentation metadata;
- CMS code is versioned external identity, never sufficient local primary identity by itself;
- stock movement is ledger/event based: opening, receipts, usage, approved adjustments;
- deterministic backend code owns calculations, idempotency, constraints, transactions, and audit;
- historical operational records are correction-safe and are not silently hard-deleted.

## Current documentation checkpoint

Architecture/docs foundation exists for:

- canonical inventory architecture;
- inventory data model;
- monthly lifecycle;
- CMS catalogue versioning;
- integrity/audit;
- Sheet/Excel compatibility;
- API/client architecture;
- migration/shadow validation;
- decisions/open questions;
- implementation slices;
- VPS deployment baseline;
- backup/recovery baseline.

Schema-gating decisions remain open in `docs/architecture/DECISIONS_AND_OPEN_QUESTIONS.md`; therefore canonical inventory migrations/tables are not yet authorized.

## Implementation checkpoint

### F0 — VPS inspection and safe host preparation

Status: **completed 2026-08-22**.

Canonical evidence: `docs/operations/F0_VPS_INSPECTION_2026-08-22.md`.

Verified F0 facts:

- Ubuntu 24.04.4 LTS x86_64;
- 2 vCPU;
- 3.3 GiB RAM with limited headroom and substantial swap already in use;
- 63 GiB root disk with about 17 GiB free at inspection time;
- Docker Engine 29.3.0 and Compose plugin 5.1.1 available;
- managed-token `cloudflared` tunnel active; hostname routing is controlled in Cloudflare dashboard/Zero Trust;
- no host nginx/Caddy/Traefik reverse proxy;
- dedicated `/opt/medicine-store-assistant/` host area prepared with `medstore` non-login system user;
- no MSA code cloned, credentials created, public app port opened, or database deployed;
- unrelated host/Docker PostgreSQL services already exist and must not be reused;
- no active host firewall was reported, so MSA host publishes must remain localhost-only by default;
- preferred first API host port is `8088`, subject to a fresh conflict check;
- PostgreSQL should normally stay private on the Docker network and does not need a host port.

Resource posture requires conservative API/PostgreSQL memory limits and no unnecessary Redis/broker/proxy sidecars.

### F1 — Repository Runtime Skeleton

Status: **explicitly authorized / next slice**.

Authorized scope:

- create sibling runtime folders without altering `skills/medicine-store-assistant/`;
- minimal API with deterministic `/health` and build/version metadata;
- Dockerfile + Compose;
- isolated PostgreSQL service definition with private Docker networking and secret-driven configuration;
- no canonical inventory schema/migrations/tables yet;
- localhost-only API bind, initially `127.0.0.1:8088` after conflict check;
- no public DB port;
- `.env.example` / `.gitignore`, no real secrets in Git;
- build/start/health verification and repository validation.

Explicitly out of F1:

- Cloudflare hostname routing;
- Custom GPT creation/action connection;
- Google Sheet mutation/mirror service;
- inventory schema/migrations;
- live inventory import;
- canonical DB promotion;
- Telegram/Flutter implementation.

## Next sequence after F1

1. Resolve schema-gating decisions in `DECISIONS_AND_OPEN_QUESTIONS.md`.
2. Authorize F2 PostgreSQL schema/migration foundation.
3. Implement read-only domain/API foundation.
4. When read-only API health/contract is stable, configure Cloudflare custom hostname.
5. Then create the private MSA Custom GPT and test read-only Actions.
6. Ledger writes/shadow migration come later under separate authorization.

## Continuity maintenance rule

After every significant architecture decision, implementation slice, migration result, deployment change, or next-work change:

- update `ROADMAP.md`;
- update this `NEW_CHAT_BOOTSTRAP.md`;
- update relevant architecture/operations docs.

A fresh chat must recover current truth from repository evidence without relying on remembered conversation history.
