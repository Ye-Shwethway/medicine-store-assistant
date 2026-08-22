# Medicine Store Assistant — Project Roadmap

Status: **F0/F1/F2/F3/F4/F5/F5.1/F6A/F6C verified complete; F6B remains test-only; PostgreSQL remains non-canonical**

The live Google workbook/source documents remain operationally authoritative. The current staged F6B snapshot is **test-only** and is **not an accepted migration baseline**. A fresh real migration dataset will be imported later only after the operational workflow and user-facing management UI are ready and explicitly approved.

## Delivery policy

Canonical flow: `test -> pull request -> main -> automatic VPS deploy for relevant runtime changes`.

Validation is path-aware and lightweight. Docs-only changes do not run the backend suite or deploy the VPS. Normal continuation does not require manual VPS commands or a manual Actions deploy button. Runtime secrets remain only on the VPS.

Normal backend deployment must **not** read/import the live workbook. Live snapshot import is an explicit test/migration operation only.

## Verified foundation

- F0 VPS inspection — verified complete 2026-08-22
- F1 runtime skeleton — verified complete 2026-08-22
- Cloudflare public HTTPS route — verified complete 2026-08-22
- F2 PostgreSQL foundation — verified complete 2026-08-22
- F3 authenticated read-only API — verified complete 2026-08-22
- F4 synthetic ledger foundation — verified complete 2026-08-22
- F5 synthetic CMS catalogue versioning — verified complete 2026-08-22
- F5.1 authenticated catalogue read API — verified complete 2026-08-22
- F6A synthetic shadow migration adapter foundation — verified complete 2026-08-22
- F6B read-only live-workbook test snapshot — verified staging exercise only; not a migration baseline
- F6C authenticated shadow read API — verified complete 2026-08-22

Canonical evidence:

- `docs/operations/F4_SYNTHETIC_LEDGER_VERIFICATION_2026-08-22.md`
- `docs/operations/F5_F5_1_CATALOGUE_VERIFICATION_2026-08-22.md`
- `docs/operations/F6A_SHADOW_MIGRATION_VERIFICATION_2026-08-22.md`
- `docs/operations/F6B_LIVE_SHADOW_IMPORT_VERIFICATION_2026-08-22.md`
- `docs/operations/F6C_SHADOW_READ_API_VERIFICATION_2026-08-22.md`

## Test-only F6B snapshot

Verified source commit `34b169c56422454b9a919936689c3088a9c4ebfc` via GitHub Actions run `32549738838` staged one read-only snapshot from `Medicine Store Cloud` into shadow PostgreSQL.

Test snapshot summary:

- rows: **1,646**
- `SAFE`: **1,417**
- `REVIEW`: **222**
- `NEW_UNMAPPED`: **7**
- `CONFLICT`: **0**
- source hash: `cfe4c24201bbe9f519189572f0c4c1988a9785e6fb0ca3e8f9630f5ca0417192`

This batch is for read-path testing only. It must not drive canonical reconciliation or promotion decisions.

## F6C verified read-only inspection

Verified deployed source commit: `9f706da4832c08f10b1a8d694273f8f48412570a` via GitHub Actions run `32550437296`.

Verified behavior:

- normal backend deploy executed with **no live workbook import**;
- existing test-only batch provenance/classification summary verified;
- `GET /v1/shadow/batches` registered;
- `GET /v1/shadow/batches/{migration_batch_id}` registered;
- `GET /v1/shadow/rows` registered;
- `GET /v1/shadow/review-reasons` registered;
- anonymous shadow access returns HTTP 401;
- API responses are designed to state `migration_baseline_accepted:false` and `database_canonical:false`;
- `/health` and `/ready` green at migration `0004_shadow`.

## Next product slice — proposal only

The next meaningful product work should be **user-facing management UI architecture/foundation**, not real migration reconciliation.

The UI should eventually let the owner safely browse/manage inventory, lots, catalogue mappings, shadow/import review state, and later authorized operations without relying on raw API calls or database access. Google Sheets remains the practical human-facing source today until this UI is ready.

Do not import/accept a real migration baseline merely to continue backend development.

## Safety boundary

Do not treat the current F6B test batch as real migration truth. Do not begin production stock writes, database promotion, Telegram writes, Flutter rollout, Sheet mirror conversion, or Custom GPT write Actions without explicit authorization for those slices.

## Continuity rule

After every significant architecture decision, implementation slice, deployment/migration result, or next-work change, update `ROADMAP.md`, `NEW_CHAT_BOOTSTRAP.md`, and relevant canonical architecture/operations docs.
