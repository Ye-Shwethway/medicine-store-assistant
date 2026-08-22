# Medicine Store Assistant — Project Roadmap

Status: **F0/F1/F2/F3/F4/F5/F5.1/F6A verified complete; F6B authorized and authored on test; PostgreSQL remains non-canonical**

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

Canonical evidence:

- `docs/operations/F4_SYNTHETIC_LEDGER_VERIFICATION_2026-08-22.md`
- `docs/operations/F5_F5_1_CATALOGUE_VERIFICATION_2026-08-22.md`
- `docs/operations/F6A_SHADOW_MIGRATION_VERIFICATION_2026-08-22.md`

F6A verified source commit `bab03f1f5ad14e0707cbde51217c6d951b05d66f` through GitHub Actions run `32546294049`.

Verified F6A runtime:

- Alembic `0003_catalogue -> 0004_shadow`;
- batch idempotency pass;
- provenance pass;
- deterministic classification pass;
- explicit review reporting pass;
- no canonical product/ledger mutation pass;
- synthetic fixtures rolled back;
- `/health` healthy with `database_canonical: false`;
- `/ready` database reachable with migration/expected migration both `0004_shadow`.

## F6B — read-only live-workbook shadow snapshot

Status: **authorized; implementation authored on `test`; runtime credential bootstrap pending before merge**.

The authoritative workbook was identified as `Medicine Store Cloud`. Read-only inspection confirmed the live `Main Stock` and `Daily Usage` column contracts.

F6B authored behavior:

1. use Google Sheets read-only OAuth scope only;
2. read `Main Stock` and `Daily Usage` without mutating the workbook;
3. preserve exact source sheet/row provenance and deterministic source hashes;
4. stage live rows only in F6A shadow migration tables;
5. classify `SAFE`, `REVIEW`, `CONFLICT`, and `NEW_UNMAPPED` cases;
6. validate Main Stock and Daily Usage balance formulas and cross-sheet monthly usage/current balance consistency;
7. perform no automatic identity repair/remapping;
8. create no canonical products/lots/ledger transactions;
9. keep PostgreSQL non-canonical and the Google workbook authoritative;
10. keep all live workbook rows and Google credentials out of the public repository.

Canonical plan: `docs/operations/F6B_LIVE_SHADOW_IMPORT_PLAN.md`.

### Current gate

The self-hosted VPS runner does not yet have a dedicated Google service-account credential. Do not merge the F6B runtime path to `main` until:

- a dedicated service account exists;
- its email is shared to `Medicine Store Cloud` as Viewer only;
- its JSON key is stored outside the repository at `/opt/medicine-store-assistant/secrets/google-service-account.json`;
- `runtime.env` contains `MSA_GOOGLE_SPREADSHEET_ID` and `MSA_GOOGLE_SERVICE_ACCOUNT_FILE`;
- `msa-runner` can read the credential through the existing `medstore` group boundary without printing it.

After that one-time credential bootstrap, F6B promotion remains automatic: `test -> PR -> main -> self-hosted deploy/import/verify`.

## Safety boundary

F6B is authorized only for read-only source access and shadow staging. It does not authorize production stock writes, database promotion, Telegram writes, Flutter rollout, Google Sheet mirror conversion, or Custom GPT write Actions.

## Continuity rule

After every significant architecture decision, implementation slice, deployment/migration result, or next-work change, update `ROADMAP.md`, `NEW_CHAT_BOOTSTRAP.md`, and relevant canonical architecture/operations docs.
