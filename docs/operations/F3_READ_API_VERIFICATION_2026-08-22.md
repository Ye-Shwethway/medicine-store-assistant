# F3 Read API Verification — 2026-08-22

Status: **verified complete**

## Deployed revision

`dac1a4aa5b218d3c5eda24a636b3c3688979473b`

## Verified results

- repository validator passed for `medicine-store-assistant` plugin 1.1.0;
- API image rebuilt and restarted successfully;
- `/health` returned HTTP 200 with service `medicine-store-assistant-api`, environment `foundation`, version `0.1.0-dev`, deployed build SHA, and `database_canonical: false`;
- `/ready` returned HTTP 200 with PostgreSQL reachable and migration `0001_foundation` matching expected migration;
- anonymous `GET /v1/products` returned HTTP 401;
- authenticated `GET /v1/products` returned HTTP 200 with an empty list, which is expected before shadow import;
- a scoped read credential was created for verification;
- the plaintext credential was stored only on the VPS at `/opt/medicine-store-assistant/secrets/f3_read_api.token` with mode 0600 and was not printed;
- PostgreSQL remains non-canonical and contains no live inventory import.

## Security boundary verified

The Cloudflare hostname may expose the API edge publicly, but inventory/domain reads are not anonymous. F3 requires scoped bearer authentication for read-only domain endpoints.

F3 introduces no inventory mutation endpoint and grants no production stock-write authority.

## Current read-only surface

Authenticated read-only endpoints include products, product lots, operating months, CMS catalogue diagnostics, and a credential-safe access summary. Sensitive credential hashes, password hashes, Telegram external identifiers, and raw token material are not exposed by the safe summary.

## Next boundary

The next implementation slice may introduce ledger primitives only in isolated synthetic/test mode. Live Google Sheet inventory, real stock writes, Sheet mirror mutation, and database canonical promotion remain out of scope until later explicit authorization and validation.
