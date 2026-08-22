# F6B Live Shadow Import Verification — 2026-08-22

Status: **verified complete**

## Scope

F6B performed the first read-only live-workbook snapshot import from the authoritative `Medicine Store Cloud` Google workbook into shadow PostgreSQL staging. The workbook remained authoritative and PostgreSQL remained non-canonical.

No Google Sheet mutation, production stock write, canonical product/lot creation, canonical ledger transaction, database promotion, Telegram write, Flutter rollout, Sheet mirror conversion, or Custom GPT write Action occurred.

## Deployment evidence

- deployed source commit: `34b169c56422454b9a919936689c3088a9c4ebfc`
- GitHub Actions run: `32549738838`
- runner: `msa-vps-runner-01`
- deployment result: `success`
- database migration: `0004_shadow`
- expected migration: `0004_shadow`
- `database_canonical`: `false`
- source authority: `google_workbook`

## Live snapshot evidence

The live read-only snapshot staged:

- total rows: **1,646**
- `SAFE`: **1,417**
- `REVIEW`: **222**
- `NEW_UNMAPPED`: **7**
- `CONFLICT`: **0**
- snapshot source hash: `cfe4c24201bbe9f519189572f0c4c1988a9785e6fb0ca3e8f9630f5ca0417192`

The migration batch was created successfully and retained source-sheet/source-row provenance. Real medicine-store row payloads are intentionally not published in this public repository.

## Verified controls

- dedicated Google service account used read-only workbook access;
- workbook shared to service account as Viewer;
- credential remained on VPS outside GitHub;
- runtime preflight confirmed credential readability without logging private key material;
- live rows staged only in shadow migration tables;
- deterministic classification/reporting executed without silent repair;
- no canonical inventory mutation occurred;
- API restarted successfully;
- `/health` returned healthy with deployed build SHA and `database_canonical:false`;
- `/ready` returned database reachable with migration/expected migration `0004_shadow`.

Transient connection resets during API recreation were followed by successful retry and healthy final probes.

## Interpretation

F6B proves that the live workbook can be read safely and staged reproducibly into the shadow migration domain. It does **not** prove that all staged rows are ready for canonical promotion. The 222 `REVIEW` rows and 7 `NEW_UNMAPPED` rows require reconciliation before any promotion decision.

`CONFLICT=0` is encouraging but is not sufficient by itself for database canonicality.

## Next recommended slice

F6C should reconcile and explain the staged `REVIEW` and `NEW_UNMAPPED` populations using read-only analysis and non-sensitive summary evidence. It should not silently repair source data, create canonical inventory transactions, or promote PostgreSQL.
