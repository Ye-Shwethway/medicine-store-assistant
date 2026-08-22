# Medicine Store Assistant — New Chat Bootstrap

Use this file for project-development continuity and memory reconciliation in a fresh chat.

## Canonical repository

`https://github.com/Ye-Shwethway/medicine-store-assistant`

## Reconciliation order

1. `AGENTS.md`
2. `NEW_CHAT_BOOTSTRAP.md`
3. `ROADMAP.md`
4. `IMPLEMENTATION_PLAN.md`
5. `docs/architecture/README.md`
6. task-relevant architecture/operations docs
7. skill references when spreadsheet work is involved
8. current repository/runtime evidence

Treat newer verified repository/runtime evidence as authoritative over remembered chat context.

## Authority boundary

The live Google workbook/source documents remain authoritative. PostgreSQL is deployed but **not canonical**.

## Deployment workflow

Canonical flow: `test -> pull request -> main -> automatic VPS deployment for relevant runtime changes`.

- No normal manual VPS deployment command is required from the user.
- No normal manual GitHub Actions deploy button is required.
- Backend validation is path-aware and lightweight.
- Docs-only/unrelated changes do not deploy the VPS.
- Relevant runtime changes use repository-scoped self-hosted runner `msa-vps-runner-01`.
- Runtime secrets stay on the VPS.
- `.github/backend-deploy-result` records deployment status, source SHA, and workflow run ID.

## Verified checkpoints

F0, F1, Cloudflare HTTPS route, F2, F3, F4, F5, F5.1, and **F6A** are verified complete as of 2026-08-22.

F6A canonical evidence: `docs/operations/F6A_SHADOW_MIGRATION_VERIFICATION_2026-08-22.md`.

Verified F6A deployment:

- source commit `bab03f1f5ad14e0707cbde51217c6d951b05d66f`;
- GitHub Actions run `32546294049`;
- Alembic migration `0004_shadow`;
- batch idempotency, provenance, classification, review reporting, and no-canonical-mutation all pass;
- synthetic staging fixtures rolled back;
- `/health` healthy with `database_canonical: false`;
- `/ready` database reachable with migration/expected migration both `0004_shadow`.

F6A did **not** read or import the live Google workbook.

## Next gated slice

**F6B — first read-only live-workbook snapshot import into shadow PostgreSQL.**

F6B crosses the live-source boundary and must not begin without explicit authorization. If authorized, it must preserve exact snapshot provenance, stage/classify before any promotion, surface SAFE/REVIEW/CONFLICT/NEW-UNMAPPED results, remain idempotent, and keep PostgreSQL non-canonical.

## Safety boundary

Do not begin live Sheet import, production stock writes, database promotion, Telegram writes, Flutter rollout, Google Sheet mirror conversion, or Custom GPT write Actions without explicit authorization for that slice.

## Continuity rule

After significant architecture, implementation, deployment, migration, or next-work changes, update `ROADMAP.md`, this file, and relevant canonical docs.
