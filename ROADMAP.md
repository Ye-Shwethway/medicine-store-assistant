# Medicine Store Assistant — Project Roadmap

Status: **F0/F1/F2/F3/F4/F5/F5.1/F6A verified complete; F6B test-only shadow snapshot verified; PostgreSQL remains non-canonical**

The live Google workbook/source documents remain operationally authoritative. The current staged F6B snapshot is **test-only** and is **not an accepted migration baseline**. A real migration dataset will be imported later only after the operational workflow and user-facing management UI are ready and explicitly approved.

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
- F6B read-only live-workbook **test snapshot** — verified as a test-only staging exercise 2026-08-22

Canonical evidence:

- `docs/operations/F4_SYNTHETIC_LEDGER_VERIFICATION_2026-08-22.md`
- `docs/operations/F5_F5_1_CATALOGUE_VERIFICATION_2026-08-22.md`
- `docs/operations/F6A_SHADOW_MIGRATION_VERIFICATION_2026-08-22.md`
- `docs/operations/F6B_LIVE_SHADOW_IMPORT_VERIFICATION_2026-08-22.md`

## F6B test-only snapshot

Verified source commit `34b169c56422454b9a919936689c3088a9c4ebfc` via GitHub Actions run `32549738838` staged one read-only snapshot from `Medicine Store Cloud` into shadow PostgreSQL.

Test snapshot summary:

- total staged rows: **1,646**
- `SAFE`: **1,417**
- `REVIEW`: **222**
- `NEW_UNMAPPED`: **7**
- `CONFLICT`: **0**
- source snapshot hash: `cfe4c24201bbe9f519189572f0c4c1988a9785e6fb0ca3e8f9630f5ca0417192`
- `/health`: healthy, `database_canonical:false`
- `/ready`: database reachable, migration/expected migration `0004_shadow`

This proves read-only acquisition/staging mechanics only. The batch is not approved as migration truth and should not drive canonical reconciliation or promotion decisions.

## Current slice — F6C read-only shadow inspection

Use the existing test-only staged data to prove read-only inspection surfaces needed by future user-facing clients.

Scope:

1. list shadow/test batches and classification counts;
2. inspect one batch summary;
3. query staged rows by batch/sheet/classification/search text;
4. summarize review/unmapped reasons;
5. require the existing authenticated read scope;
6. return `migration_baseline_accepted:false` and `database_canonical:false` explicitly;
7. execute no live workbook import during normal deployment;
8. expose no write/correction/promotion endpoint.

A later product phase must design a user-facing management UI before any real migration baseline is imported/accepted.

## Safety boundary

Do not treat the current F6B test batch as the real migration dataset. Do not begin production stock writes, database promotion, Telegram writes, Flutter rollout, Sheet mirror conversion, or Custom GPT write Actions without explicit authorization for those slices.

## Continuity rule

After every significant architecture decision, implementation slice, deployment/migration result, or next-work change, update `ROADMAP.md`, `NEW_CHAT_BOOTSTRAP.md`, and relevant canonical architecture/operations docs.
