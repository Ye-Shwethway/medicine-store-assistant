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

F0, F1, Cloudflare HTTPS route, F2, F3, F4, F5, F5.1, F6A, and **F6B** are verified complete as of 2026-08-22.

Canonical F6B evidence: `docs/operations/F6B_LIVE_SHADOW_IMPORT_VERIFICATION_2026-08-22.md`.

Verified F6B deployment:

- source commit `34b169c56422454b9a919936689c3088a9c4ebfc`;
- GitHub Actions run `32549738838`;
- dedicated Google service account shared to `Medicine Store Cloud` as Viewer only;
- live read-only snapshot staged into shadow PostgreSQL;
- total rows `1646`;
- `SAFE=1417`, `REVIEW=222`, `NEW_UNMAPPED=7`, `CONFLICT=0`;
- snapshot hash `cfe4c24201bbe9f519189572f0c4c1988a9785e6fb0ca3e8f9630f5ca0417192`;
- no Google Sheet mutation;
- no canonical product/lot/ledger mutation;
- `/health` healthy with `database_canonical:false`;
- `/ready` database reachable with migration/expected migration `0004_shadow`.

Real medicine-store rows and credentials are not published in the public repository.

## Next gated slice

**F6C — shadow reconciliation analysis.**

F6C should explain and group the 222 `REVIEW` rows and 7 `NEW_UNMAPPED` rows using read-only analysis. It may compare staged provenance against current workbook/CMS/local identity evidence, but must not silently repair source data, create canonical inventory transactions, mutate mappings, or promote PostgreSQL.

F6C requires explicit authorization before implementation.

## Safety boundary

Do not begin production stock writes, database promotion, Telegram writes, Flutter rollout, Google Sheet mirror conversion, or Custom GPT write Actions without explicit authorization for that slice.

## Continuity rule

After significant architecture, implementation, deployment, migration, or next-work changes, update `ROADMAP.md`, this file, and relevant canonical docs.
