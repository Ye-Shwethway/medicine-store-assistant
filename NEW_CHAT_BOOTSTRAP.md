# Medicine Store Assistant — New Chat Bootstrap

Use this file for project-development continuity and memory reconciliation in a fresh chat.

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

Treat newer verified repository/runtime evidence as authoritative over remembered chat context.

## Authority boundary

The live Google workbook/source documents remain authoritative. PostgreSQL is deployed but **not canonical**.

## Deployment workflow

Canonical development/deployment flow:

`test -> pull request -> main -> automatic VPS deployment for relevant runtime changes`

- Do not require the user to run normal VPS deployment commands or press a manual Actions deploy button.
- Backend/deploy validation is path-aware and lightweight.
- Skill validation runs only for skill/plugin/package-contract changes.
- Docs-only/unrelated changes do not deploy the VPS.
- Relevant `main` runtime changes run on repository-scoped self-hosted runner `msa-vps-runner-01` (`self-hosted`, `linux`, `msa-vps`).
- Runtime secrets stay at `/opt/medicine-store-assistant/secrets/runtime.env` on the VPS.
- Deployment evidence is written back to `.github/backend-deploy-result` with status/source SHA/workflow run ID.

## Verified checkpoints

- F0 VPS inspection — **verified complete 2026-08-22**
- F1 runtime skeleton — **verified complete 2026-08-22**
- Cloudflare public HTTPS route — **verified complete 2026-08-22**
- F2 PostgreSQL foundation — **verified complete 2026-08-22**
- F3 authenticated read-only API — **verified complete 2026-08-22**
- F4 synthetic ledger foundation — **verified complete 2026-08-22**
- F5 synthetic CMS catalogue versioning — **verified complete 2026-08-22**
- F5.1 authenticated catalogue read API — **verified complete 2026-08-22**

Canonical F5/F5.1 evidence: `docs/operations/F5_F5_1_CATALOGUE_VERIFICATION_2026-08-22.md`.

Verified deployed source commit: `3a49c8edb63c4c3f38da8508ebf3187962224bb7`, GitHub Actions run `32546107503`.

Runtime proof includes:

- F5 hash idempotency, version history, add/remove diff, price diff, identity-shift guard all pass;
- F5.1 versions/current/items/diff GET surfaces pass;
- no catalogue write surface exists;
- `/health` healthy with `database_canonical: false`;
- `/ready` database reachable with migration and expected migration both `0003_catalogue`.

## Current next slice

**F6A — Shadow migration adapter foundation using synthetic/non-sensitive fixtures only.**

F6A may build provenance schema, deterministic adapters, classification/reporting, and idempotent synthetic migration verification. It must not read or import the live Google workbook.

A later separately authorized **F6B** would be the first read-only live-workbook snapshot import into shadow PostgreSQL.

## Safety boundary

Do not begin live CMS ingestion, live Sheet import, production stock writes, database promotion, Telegram writes, Flutter rollout, Google Sheet mirror conversion, or Custom GPT write Actions without explicit authorization for that slice.

## Continuity rule

After every significant architecture decision, implementation slice, deployment/migration result, or next-work change, update `ROADMAP.md`, this file, and relevant canonical architecture/operations docs.
