# F2 VPS Migration Verification — 2026-08-22

Status: **verified complete**

## Final deployed revision

The hardened F2 verification run deployed repository revision:

`a9cd98e4af6fd20aee07a783f82daf46d557ac7a`

## Final verified results

- repository validator passed for `medicine-store-assistant` plugin 1.1.0;
- API image rebuilt successfully with Alembic, SQLAlchemy and psycopg v3;
- isolated MSA PostgreSQL container remained healthy;
- Alembic confirmed the database at migration `0001_foundation`;
- long-lived API container was recreated and started successfully;
- `GET http://127.0.0.1:8088/health` returned HTTP 200 with:
  - `ok: true`;
  - service `medicine-store-assistant-api`;
  - environment `foundation`;
  - version `0.1.0-dev`;
  - build SHA `a9cd98e4af6fd20aee07a783f82daf46d557ac7a`;
  - `database_canonical: false`;
- `GET http://127.0.0.1:8088/ready` returned HTTP 200 with:
  - `ok: true`;
  - `database: reachable`;
  - `migration: 0001_foundation`;
  - `expected_migration: 0001_foundation`;
  - service `medicine-store-assistant-api`;
  - `database_canonical: false`.

These results satisfy the F2 runtime exit criteria.

## Driver issue resolved during F2

The first F2 apply attempt failed before migration because SQLAlchemy interpreted a plain `postgresql://` runtime URL using the default psycopg2 dialect while the backend intentionally installs psycopg v3.

The repository was corrected to normalize PostgreSQL URLs to `postgresql+psycopg://` in both Alembic and application database-readiness paths. No VPS-local source patch and no psycopg2 dependency were added.

## Deploy verification race resolved

The initial successful migration run exposed a brief container-recreate race where an immediate curl could receive `Recv failure: Connection reset by peer` before Uvicorn had bound the new listener.

`deploy/apply_f2_foundation.sh` was hardened with retry/polling behavior. During the final verification run, early polling probes still observed two transient connection resets, but the script remained in its intended retry loop and subsequently obtained successful `/health` and `/ready` responses before printing its success result.

The transient probe failures are therefore not steady-state service failures.

## Safety boundary preserved

F2 did **not**:

- import live inventory data;
- enable stock ledger/write APIs;
- mutate the Google workbook;
- enable Custom GPT write Actions;
- deploy Telegram or Flutter clients;
- promote PostgreSQL to canonical operational authority.

The live workbook/source-document workflow remains authoritative until later shadow/dual validation and explicit promotion.
