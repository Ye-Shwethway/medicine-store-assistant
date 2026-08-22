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

The F6B staged batch is **test-only**. It is not an accepted migration baseline and must not be treated as the real dataset to promote later. A fresh real migration dataset will be imported only after the operational workflow and user-facing management UI are ready and explicitly approved.

## Deployment workflow

Canonical flow: `test -> pull request -> main -> automatic VPS deployment for relevant runtime changes`.

- No normal manual VPS deployment command is required from the user.
- No normal manual GitHub Actions deploy button is required.
- Backend validation is path-aware and lightweight.
- Docs-only/unrelated changes do not deploy the VPS.
- Relevant runtime changes use repository-scoped self-hosted runner `msa-vps-runner-01`.
- Runtime secrets stay on the VPS.
- `.github/backend-deploy-result` records deployment status, source SHA, and workflow run ID.
- Normal backend deploy does **not** read/import the live Google workbook.
- The F6B importer is retained only as an explicit test/migration tool.

## Verified checkpoints

F0, F1, Cloudflare HTTPS route, F2, F3, F4, F5, F5.1, F6A, and **F6C** are verified foundation/read-path checkpoints.

F6B is a verified **test-only** snapshot/staging exercise, not a migration baseline.

F6C verification:

- source commit `9f706da4832c08f10b1a8d694273f8f48412570a`;
- GitHub Actions run `32550437296`;
- existing test batch verified at `1646` rows (`SAFE=1417`, `REVIEW=222`, `CONFLICT=0`, `NEW_UNMAPPED=7`);
- `migration_baseline_accepted=false`;
- `database_canonical=false`;
- shadow read routes registered for batches, one-batch summary, rows, and review reasons;
- anonymous shadow read returns HTTP 401;
- `/health` and `/ready` green at `0004_shadow`;
- deployment log explicitly confirmed that **no live workbook import executed**.

Canonical evidence: `docs/operations/F6C_SHADOW_READ_API_VERIFICATION_2026-08-22.md`.

## Next product direction — proposal only

The next meaningful product slice should be the **user-facing management UI architecture/foundation**. Google Sheets remains the current practical human-facing interface until that UI exists.

The future UI should safely surface inventory/lot/catalogue/shadow-review information and later explicitly authorized operations through the MSA API. Do not import/accept a real migration baseline just to continue backend work.

## Safety boundary

Do not treat F6B test data as production migration truth. Do not begin production stock writes, database promotion, Telegram writes, Flutter rollout, Sheet mirror conversion, or Custom GPT write Actions without explicit authorization for those slices.

## Continuity rule

After significant architecture, implementation, deployment, migration, or next-work changes, update `ROADMAP.md`, this file, and relevant canonical docs.
