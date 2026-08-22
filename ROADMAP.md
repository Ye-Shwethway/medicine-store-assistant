# Medicine Store Assistant — Project Roadmap

Status: **F0/F1/F2/F3/F4/F5/F5.1/F6A/F6B verified complete; PostgreSQL remains non-canonical**

The live Google workbook/source documents remain operationally authoritative until shadow/dual validation and explicit database promotion.

## Delivery policy

Canonical flow: `test -> pull request -> main -> automatic VPS deploy for relevant runtime changes`.

Validation is path-aware and lightweight. Docs-only changes do not run the backend suite or deploy the VPS. Normal continuation does not require manual VPS commands or a manual Actions deploy button. Runtime secrets remain only on the VPS.

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
- F6B first read-only live-workbook shadow snapshot — verified complete 2026-08-22

Canonical evidence:

- `docs/operations/F4_SYNTHETIC_LEDGER_VERIFICATION_2026-08-22.md`
- `docs/operations/F5_F5_1_CATALOGUE_VERIFICATION_2026-08-22.md`
- `docs/operations/F6A_SHADOW_MIGRATION_VERIFICATION_2026-08-22.md`
- `docs/operations/F6B_LIVE_SHADOW_IMPORT_VERIFICATION_2026-08-22.md`

## F6B verified runtime

Verified deployed source commit: `34b169c56422454b9a919936689c3088a9c4ebfc` via GitHub Actions run `32549738838`.

The authoritative `Medicine Store Cloud` workbook was read through a dedicated Viewer-only service account and staged into shadow PostgreSQL without mutating the workbook.

Live snapshot summary:

- total staged rows: **1,646**
- `SAFE`: **1,417**
- `REVIEW`: **222**
- `NEW_UNMAPPED`: **7**
- `CONFLICT`: **0**
- source snapshot hash: `cfe4c24201bbe9f519189572f0c4c1988a9785e6fb0ca3e8f9630f5ca0417192`
- `/health`: healthy, `database_canonical:false`
- `/ready`: database reachable, migration/expected migration `0004_shadow`

Real workbook rows and credentials remain outside the public repository. F6B created no canonical product/lot/ledger records and performed no automatic repair or mapping mutation.

## Next recommended slice — F6C

**F6C — shadow reconciliation analysis** should explain the 222 `REVIEW` rows and 7 `NEW_UNMAPPED` rows before any canonical promotion discussion.

Recommended scope:

1. group review cases by deterministic reason/category;
2. identify whether mismatches originate from source formulas, missing identifiers, expiry/name normalization, or cross-sheet differences;
3. analyze the 7 unmapped rows against available CMS/local identity evidence without automatic remapping;
4. produce non-sensitive counts and reconciliation summaries;
5. preserve all source rows unchanged;
6. keep Google workbook authoritative and PostgreSQL non-canonical;
7. make no production stock writes.

F6C is a new reconciliation slice and should be explicitly authorized before implementation.

## Safety boundary

Do not begin production stock writes, database promotion, Telegram writes, Flutter rollout, Google Sheet mirror conversion, or Custom GPT write Actions without explicit authorization for that slice.

## Continuity rule

After every significant architecture decision, implementation slice, deployment/migration result, or next-work change, update `ROADMAP.md`, `NEW_CHAT_BOOTSTRAP.md`, and relevant canonical architecture/operations docs.
