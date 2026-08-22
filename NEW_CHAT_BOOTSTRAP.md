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

The F6B staged batch is **test-only**. It is not an accepted migration baseline and must not be treated as the real dataset to be promoted later. A fresh real migration dataset will be imported only after the operational workflow and user-facing management UI are ready and explicitly approved.

## Deployment workflow

Canonical flow: `test -> pull request -> main -> automatic VPS deployment for relevant runtime changes`.

- No normal manual VPS deployment command is required from the user.
- No normal manual GitHub Actions deploy button is required.
- Backend validation is path-aware and lightweight.
- Docs-only/unrelated changes do not deploy the VPS.
- Relevant runtime changes use repository-scoped self-hosted runner `msa-vps-runner-01`.
- Runtime secrets stay on the VPS.
- `.github/backend-deploy-result` records deployment status, source SHA, and workflow run ID.
- Normal backend deploy must not read/import the live Google workbook.
- The F6B live importer is retained only as an explicit test/migration tool.

## Verified checkpoints

F0, F1, Cloudflare HTTPS route, F2, F3, F4, F5, F5.1, and F6A are verified foundation checkpoints.

F6B verified a **test-only** read-only snapshot/staging exercise:

- source commit `34b169c56422454b9a919936689c3088a9c4ebfc`;
- GitHub Actions run `32549738838`;
- total rows `1646`;
- `SAFE=1417`, `REVIEW=222`, `NEW_UNMAPPED=7`, `CONFLICT=0`;
- snapshot hash `cfe4c24201bbe9f519189572f0c4c1988a9785e6fb0ca3e8f9630f5ca0417192`;
- no Google Sheet mutation;
- no canonical product/lot/ledger mutation;
- `/health` healthy with `database_canonical:false`;
- `/ready` database reachable with migration/expected migration `0004_shadow`.

This snapshot is useful for read-path testing only. Do not use its REVIEW/NEW_UNMAPPED population as a real migration reconciliation workload.

## Current slice — F6C read-only shadow inspection

Build and verify authenticated read-only inspection endpoints over the existing test-only shadow batch:

- batch list and classification counts;
- one-batch summary;
- staged-row query/filter/search;
- review/unmapped reason summaries;
- explicit `migration_baseline_accepted:false` and `database_canonical:false` responses;
- no live workbook import during deployment;
- no write/correction/promotion endpoint.

The user-facing management UI remains a required later product slice before a real migration baseline is imported and accepted.

## Safety boundary

Do not treat F6B test data as production migration truth. Do not begin production stock writes, database promotion, Telegram writes, Flutter rollout, Sheet mirror conversion, or Custom GPT write Actions without explicit authorization for those slices.

## Continuity rule

After significant architecture, implementation, deployment, migration, or next-work changes, update `ROADMAP.md`, this file, and relevant canonical docs.
