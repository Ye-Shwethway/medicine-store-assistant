# F2 VPS Migration Verification — 2026-08-22

Status: **migration applied; final `/ready` verification pending after deploy-script retry hardening**

## Deployed revision

Runtime repository was fast-forwarded from the F1 deployment to:

`2fff4408666723159543af900c3df8b8e3dd14fb`

## Verified results

- repository validator passed for `medicine-store-assistant` plugin 1.1.0;
- API image rebuilt successfully with Alembic, SQLAlchemy and psycopg v3;
- isolated MSA PostgreSQL container remained healthy;
- Alembic successfully applied migration `0001_foundation` using PostgreSQL transactional DDL;
- long-lived API container was recreated and started successfully;
- post-start `GET http://127.0.0.1:8088/health` returned HTTP 200;
- health response reported service `medicine-store-assistant-api`, environment `foundation`, version `0.1.0-dev`, build SHA `2fff4408666723159543af900c3df8b8e3dd14fb`, and `database_canonical: false`.

## Initial driver issue and fix

The first F2 apply attempt failed before migration because SQLAlchemy interpreted a plain `postgresql://` runtime URL using the default psycopg2 dialect while the backend intentionally installs psycopg v3.

The repository was corrected to normalize PostgreSQL URLs to `postgresql+psycopg://` in both Alembic and application database-readiness paths. No VPS-local source patch or psycopg2 dependency was added.

## Transient post-deploy verification race

The successful migration run exited during the script's immediate `/health` curl with:

`curl: (56) Recv failure: Connection reset by peer`

Evidence showed this occurred in the brief container-recreate window after the new API container was marked starting but before Uvicorn had bound its listener. A subsequent health request returned HTTP 200. This was a deploy verification timing race, not a migration or steady-state API failure.

`deploy/apply_f2_foundation.sh` has therefore been hardened to retry `/health` and `/ready` after container recreation instead of assuming immediate socket readiness.

## Remaining F2 exit check

Before declaring F2 verified complete, run the hardened apply script at the current repository head and verify:

- `/health` HTTP 200;
- `/ready` HTTP 200;
- `/ready` reports `database: reachable`;
- `/ready` reports migration `0001_foundation` and expected migration `0001_foundation`;
- `database_canonical: false` remains true.

Re-running `alembic upgrade head` is expected to be idempotent when the database is already at `0001_foundation`.

No live inventory import, stock write authority, Sheet mutation, or database canonical promotion was performed during F2.
