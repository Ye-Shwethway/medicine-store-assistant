# F6C Shadow Read API Verification — 2026-08-22

Status: **verified complete**

## Scope

F6C added authenticated read-only inspection over the existing F6B **test-only** shadow batch. It did not import a new workbook snapshot, mutate Google Sheets, alter canonical inventory, or accept a migration baseline.

## Deployment evidence

- deployed source commit: `9f706da4832c08f10b1a8d694273f8f48412570a`
- GitHub Actions run: `32550437296`
- runner: `msa-vps-runner-01`
- deployment result: `success`
- migration/expected migration: `0004_shadow`
- `database_canonical`: `false`
- `migration_baseline_accepted`: `false`

## Verified read-only surfaces

- `GET /v1/shadow/batches`
- `GET /v1/shadow/batches/{migration_batch_id}`
- `GET /v1/shadow/rows`
- `GET /v1/shadow/review-reasons`

The routes are protected by the existing read-scope authentication boundary. Anonymous access returned HTTP 401.

## Test-only batch verification

Existing test batch:

- rows: `1646`
- SAFE: `1417`
- REVIEW: `222`
- CONFLICT: `0`
- NEW_UNMAPPED: `7`

The verifier confirmed provenance and classification-summary consistency without modifying the batch.

## Deployment-policy correction

Normal backend deployment now uses `deploy/apply_backend.sh` and **does not execute the live Google workbook importer**. `deploy/apply_f6b_live_shadow_snapshot.sh` remains an explicit test/migration command only.

Runtime output explicitly confirmed:

`MSA backend deployed ...; no live workbook import executed.`

## Boundary

F6C is backend read-path foundation only. It is not the user-facing management UI, not a real migration baseline, and not authorization for production writes or database promotion.
