# Medicine Store Assistant — Project Roadmap

Status: **Phase 2 foundation active; F0/F1/F2/F3/F4/F5/F5.1 verified complete**

This roadmap tracks the full Medicine Store Assistant project and must stay synchronized with `NEW_CHAT_BOOTSTRAP.md`.

## Core authority

The live Google workbook/source documents remain operationally authoritative until shadow/dual validation and explicit database promotion. PostgreSQL is deployed but remains non-canonical.

## Delivery / deployment policy

Canonical development flow:

`test -> pull request -> main -> automatic VPS deploy for relevant runtime changes`

Rules:

- `test` is the staging/integration branch;
- promotion to `main` occurs through PR/merge;
- backend/deploy validation is path-aware and lightweight;
- Git-backed skill validation runs only for skill/plugin/package-contract changes;
- docs-only/unrelated changes do not run the backend suite and do not deploy the VPS;
- relevant `main` changes under `backend/**`, `deploy/**`, or the deployment workflow auto-run on the repository-scoped self-hosted runner labelled `self-hosted`, `linux`, `msa-vps`;
- normal continuation does not require the user to run VPS commands or press a manual Actions deploy button;
- runtime secrets stay on the VPS at `/opt/medicine-store-assistant/secrets/runtime.env` and are not copied into GitHub.

## Verified foundation

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

### F4 — Synthetic ledger foundation
Status: **verified complete 2026-08-22**

Evidence: `docs/operations/F4_SYNTHETIC_LEDGER_VERIFICATION_2026-08-22.md`.

Verified ledger invariants: deterministic balance, operation-id idempotency, normal negative-stock guard, correction/reversal linkage, rollback of synthetic fixtures, and readiness at `0002_ledger`.

### F5 — Synthetic CMS catalogue versioning
Status: **verified complete 2026-08-22**

### F5.1 — Authenticated catalogue read API
Status: **verified complete 2026-08-22**

Canonical evidence for both: `docs/operations/F5_F5_1_CATALOGUE_VERIFICATION_2026-08-22.md`.

Verified deployed source commit: `3a49c8edb63c4c3f38da8508ebf3187962224bb7` via GitHub Actions run `32546107503`.

Verified F5/F5.1 behavior:

- migration/expected migration `0003_catalogue`;
- deterministic catalogue hash/idempotency and historical-version storage;
- new/removed/changed and price-only diff behavior;
- same-code incompatible identity is flagged rather than silently remapped;
- authenticated GET surfaces for catalogue versions, current diagnostics, historical items, and version diff;
- no catalogue write surface;
- `/health` and `/ready` healthy;
- `database_canonical: false`.

No live CMS catalogue or live inventory was imported.

## Phase 3 — Shadow migration/reconciliation

Status: **not started**

### Recommended next minimum safe slice — F6A: Shadow migration adapter foundation

Recommendation: author and verify the **adapter/tooling with synthetic fixtures only first**, before reading the live workbook.

Proposed F6A scope:

1. define migration batch/provenance schema needed to trace imported source rows;
2. build deterministic parsers/adapters for normalized Main Stock + Daily Usage fixture shapes;
3. classify source rows into product/lot/opening/usage candidates without making the database canonical;
4. make reruns idempotent by migration batch/source identity;
5. generate a mismatch/classification report rather than silently repairing ambiguity;
6. prove the adapter against synthetic/non-sensitive fixtures on the VPS;
7. expose no production stock-write endpoint.

A later separately authorized **F6B** would be the first read-only snapshot import from the live workbook into shadow PostgreSQL. F6A does not authorize that live read/import.

## Later phases

- Phase 4 — Dual validation: **not started**
- Phase 5 — Canonical database promotion: **not started; explicit approval required**
- Phase 6 — Private Custom GPT Action experiment: **read-only possible later; not connected**
- Phase 7 — Google Sheets mirror: **future**
- Phase 8 — Telegram staff client: **future**
- Phase 9 — Flutter staff application: **future**
- Phase 10 — Monthly archive/export: **future**

## Safety boundary

Do not begin live CMS ingestion, live Sheet shadow import, production stock writes, database promotion, Telegram writes, Flutter rollout, Google Sheet mirror conversion, or Custom GPT write Actions without explicit authorization for that slice.

## Continuity rule

After every significant architecture decision, implementation slice, deployment/migration result, or next-work change:

1. update `ROADMAP.md`;
2. update `NEW_CHAT_BOOTSTRAP.md`;
3. update relevant canonical architecture/operations docs.
