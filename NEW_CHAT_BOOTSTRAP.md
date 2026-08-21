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
8. current repository code/config/runtime evidence

Treat newer verified repository/runtime evidence as authoritative over remembered chat context.

Do not modify production, the live workbook, backend schema/state, deployment, or integrations during reconciliation unless the user explicitly authorizes that slice.

## Project identity and repository boundary

Medicine Store Assistant is a broader medicine-store information-system project while preserving its original Git-backed workflow skill.

Same-repository monorepo:

- `skills/medicine-store-assistant/` — canonical published Git-backed skill; alias `$msa`
- `docs/architecture/` — canonical domain/system design
- `docs/operations/` — deployment/backup/runtime evidence
- `backend/` — deterministic Inventory API/runtime
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
- PostgreSQL becomes canonical only after migration validation and explicit promotion;
- Cloudflare Free/custom domain provides stable public HTTPS entry;
- GitHub stores code/docs only, never live credentials/private operational data;
- AI/human clients use typed API operations, never arbitrary SQL/database credentials.

## User/access direction

Future Telegram and Flutter clients are multi-user staff surfaces.

- maintain stable backend `user_id` identities;
- link external identities such as Telegram numeric user IDs separately;
- do not use Telegram username as canonical identity;
- use a small v1 role model such as Owner/Admin/Staff/Read-only unless the final access design chooses otherwise;
- service clients such as the MSA Custom GPT use separate service identities/scoped credentials rather than pretending to be human users;
- disabling/revoking an account must preserve historical audit attribution;
- transaction/audit records must be attributable to actor + client/channel + operation ID.

Canonical design: `docs/architecture/USER_ACCESS_AND_AUTHORIZATION.md`.

## Canonical data principles

- stable `product_id` identifies a local product;
- stable `lot_id` identifies a stock/expiry lot;
- spreadsheet row order is presentation metadata;
- CMS code is versioned external identity, never sufficient local primary identity by itself;
- stock movement is ledger/event based: opening, receipts, usage, approved adjustments;
- deterministic backend code owns calculations, idempotency, constraints, transactions and audit;
- historical operational records are correction-safe and not silently hard-deleted.

## Documentation checkpoint

Architecture/docs foundation exists for inventory architecture, data model, monthly lifecycle, CMS versioning, integrity/audit, Sheet/Excel compatibility, API/client architecture, migration, user/access management, decisions/open questions, implementation slices, VPS deployment and backup/recovery.

Schema/auth gating decisions remain open in `docs/architecture/DECISIONS_AND_OPEN_QUESTIONS.md` and `USER_ACCESS_AND_AUTHORIZATION.md`; therefore canonical inventory/user migrations are not yet authorized.

## Implementation checkpoint

### F0 — VPS inspection and safe host preparation

Status: **completed 2026-08-22**.

Evidence: `docs/operations/F0_VPS_INSPECTION_2026-08-22.md`.

### F1 — Repository Runtime Skeleton

Status: **verified complete 2026-08-22**.

Evidence: `docs/operations/F1_VPS_RUNTIME_VERIFICATION_2026-08-22.md`.

Verified F1 facts:

- deployed canonical commit `408dcbbdba6c579f446d303197c9071340188619`;
- repository validator PASS for plugin version 1.1.0;
- API and PostgreSQL containers started successfully;
- API listens only on `127.0.0.1:8088`;
- MSA PostgreSQL has no host-published port;
- local `/health` returns HTTP 200 with service `medicine-store-assistant-api`, environment `foundation`, version `0.1.0-dev`, matching build SHA and `database_canonical: false`;
- API/PostgreSQL memory use remained far below configured caps at verification;
- unrelated VPS services/containers remained unchanged.

Important ops note: `docker compose config` with real runtime env can render interpolated secrets to stdout. Use secret-safe validation such as `config --quiet` and never copy secret-bearing rendered config into logs/chat/docs.

The one-time Bamboo/VPS executor role is closed and is not part of the ongoing implementation workflow.

## Current public-edge state

Cloudflare route configured 2026-08-22.

Evidence: `docs/operations/CLOUDFLARE_ROUTE_2026-08-22.md`.

Configured path:

`https://inventory.drthorne.uk` → existing managed Cloudflare Tunnel → `http://localhost:8088`

Verified Cloudflare-side state:

- hostname was free before assignment;
- existing managed tunnel reused;
- proxied tunnel CNAME/hostname route created additively;
- existing unrelated routes preserved;
- no Worker/D1/KV/R2/Pages/Load Balancer/Access policy/paid service added;
- host port `8088` remains non-public.

**Public end-to-end verification is still pending.** Immediately after route creation, available resolvers could not yet resolve the new hostname. Do not claim public HTTP 200/TLS health until an independent request to `https://inventory.drthorne.uk/health` returns the expected health JSON.

## Current next work

1. Re-check public `https://inventory.drthorne.uk/health` after DNS/edge propagation and close the Cloudflare route slice when verified.
2. Resolve F2 schema-gating domain decisions.
3. Resolve minimal v1 user/auth/access decisions for staff Telegram/Flutter and service clients.
4. Authorize F2 PostgreSQL schema/migration foundation.
5. Implement read-only domain/API before any real stock writes.
6. Create/test the private MSA Custom GPT only after stable public HTTPS + read-only OpenAPI operations exist.

Explicitly not yet implemented/authorized:

- canonical inventory/user migrations;
- live inventory import;
- Google Sheets backend mirror;
- Custom GPT Action connection;
- Telegram staff client;
- Flutter staff client;
- database canonical promotion;
- production stock write authority.

## Continuity maintenance rule

After every significant architecture decision, implementation slice, migration result, deployment change or next-work change:

- update `ROADMAP.md`;
- update this `NEW_CHAT_BOOTSTRAP.md`;
- update relevant architecture/operations docs.

A fresh chat must recover current truth from repository evidence without relying on remembered conversation history.
