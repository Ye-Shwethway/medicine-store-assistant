# F6B Live Shadow Import Verification — 2026-08-22

Status: **verified test-only staging exercise; not an accepted migration baseline**

## Scope

F6B proved that the `Medicine Store Cloud` workbook could be read through a Viewer-only service account and staged into shadow PostgreSQL without mutating the workbook.

Project clarification after verification: the staged F6B batch is **test data for workflow/read-path validation only**. It is **not** the real migration dataset to be reconciled or promoted later. A fresh real migration dataset will be imported only after the operational workflow and user-facing management UI are ready and explicitly approved.

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

## Test snapshot evidence

The read-only test snapshot staged:

- total rows: **1,646**
- `SAFE`: **1,417**
- `REVIEW`: **222**
- `NEW_UNMAPPED`: **7**
- `CONFLICT`: **0**
- snapshot source hash: `cfe4c24201bbe9f519189572f0c4c1988a9785e6fb0ca3e8f9630f5ca0417192`

The batch retained source-sheet/source-row provenance. Real medicine-store row payloads are intentionally not published in this public repository.

## Verified controls

- dedicated Google service account used read-only workbook access;
- workbook shared to service account as Viewer;
- credential remained on VPS outside GitHub;
- runtime preflight confirmed credential readability without logging private key material;
- rows staged only in shadow migration tables;
- deterministic classification/reporting executed without silent repair;
- no canonical inventory mutation occurred;
- API restarted successfully;
- `/health` returned healthy with deployed build SHA and `database_canonical:false`;
- `/ready` returned database reachable with migration/expected migration `0004_shadow`.

Transient connection resets during API recreation were followed by successful retry and healthy final probes.

## Correct interpretation

F6B proves only that the live workbook can be read safely and staged reproducibly into the shadow migration domain.

The current 1,646-row batch must be treated as **test-only**:

- `migration_baseline_accepted = false`;
- it should not drive real migration reconciliation decisions;
- its 222 `REVIEW` and 7 `NEW_UNMAPPED` rows are useful for exercising read-only inspection/reporting only;
- a fresh migration snapshot will be taken later after the workflow and management UI are ready.

Normal backend deployment must not rerun the live importer. The importer remains an explicit test/migration operation only.

## Next slice

F6C is limited to authenticated read-only inspection of the existing test-only shadow batch: batch summaries, staged-row queries, filters, and review-reason summaries. It must expose no write/correction/promotion endpoint and must explicitly report that no migration baseline is accepted.
