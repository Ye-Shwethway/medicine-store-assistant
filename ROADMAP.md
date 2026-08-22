# Medicine Store Assistant — Project Roadmap

Status: **F0/F1/F2/F3/F4/F5/F5.1/F6A verified complete; PostgreSQL remains non-canonical**

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

F6A did not read or import the live Google workbook.

## Next gated slice — F6B

**F6B — first read-only live-workbook snapshot import into shadow PostgreSQL** is the next logical slice, but it crosses the live-source boundary and therefore requires explicit authorization before implementation.

If authorized, F6B should:

1. read a controlled snapshot of the authoritative Main Stock and Daily Usage workbook data;
2. preserve workbook/sheet/row provenance and source hash;
3. stage data only in the shadow migration domain first;
4. classify SAFE / REVIEW / CONFLICT / NEW-UNMAPPED cases;
5. produce counts and mismatch reports without silent repair;
6. avoid production stock-write endpoints and keep PostgreSQL non-canonical;
7. make reruns idempotent and traceable to the exact snapshot.

## Safety boundary

Do not begin F6B live Sheet import, production stock writes, database promotion, Telegram writes, Flutter rollout, Google Sheet mirror conversion, or Custom GPT write Actions without explicit authorization for that slice.

## Continuity rule

After every significant architecture decision, implementation slice, deployment/migration result, or next-work change, update `ROADMAP.md`, `NEW_CHAT_BOOTSTRAP.md`, and relevant canonical architecture/operations docs.
