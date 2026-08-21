# F1 VPS Runtime Verification — 2026-08-22

Status: **verified complete**

## Deployed revision

- Repository: `Ye-Shwethway/medicine-store-assistant`
- Branch: `main`
- Commit: `408dcbbdba6c579f446d303197c9071340188619`
- Repository validator: PASS — `Validated Git-backed medicine-store-assistant plugin 1.1.0`

## Runtime deployment

The F1 runtime skeleton was deployed from the canonical repository without local code changes.

- API container: `deploy-api-1`
- PostgreSQL container: `deploy-db-1`
- Docker network: `deploy_msa_internal`
- PostgreSQL volume: `deploy_msa_postgres_data`
- API host bind: `127.0.0.1:8088 -> 8080`
- PostgreSQL: container-internal `5432/tcp` only; no host-published port
- API memory limit: 384 MiB
- PostgreSQL memory limit: 512 MiB

All previously running unrelated VPS containers were reported intact and unchanged.

## Health verification

`GET http://127.0.0.1:8088/health` returned HTTP 200:

```json
{
  "ok": true,
  "service": "medicine-store-assistant-api",
  "environment": "foundation",
  "version": "0.1.0-dev",
  "build_sha": "408dcbbdba6c579f446d303197c9071340188619",
  "database_canonical": false
}
```

The response confirms that deployment does **not** promote PostgreSQL to canonical operational authority.

## Exposure verification

- API port 8088 listened on `127.0.0.1` only.
- No `0.0.0.0:8088` or `[::]:8088` listener was present.
- MSA PostgreSQL had no host port mapping.
- Existing unrelated host PostgreSQL on `127.0.0.1:5432` remained untouched and is not part of MSA.

## Runtime resource use at verification

- API: ~34.73 MiB / 384 MiB
- PostgreSQL: ~51.4 MiB / 512 MiB

No blocking resource issue was observed at F1 runtime start.

## Secret-handling observation

A real `docker compose ... config` invocation with the runtime env file interpolated the PostgreSQL password into rendered stdout via environment/DATABASE_URL expansion.

Operational rule going forward:

- do not print rendered Compose config with production/runtime secrets in shared terminals, logs, CI output, chat, or tickets;
- prefer `docker compose ... config --quiet` when only validation is required;
- never copy rendered secret-bearing Compose output into repository documentation;
- runtime secret files remain outside Git with restrictive permissions.

No secret value is recorded in this document.

## F1 closure

F1 is complete. No inventory schema/migrations, live inventory import, Cloudflare public hostname route, Custom GPT Action, Google Sheets mirror, Telegram client, Flutter client, or canonical database promotion was performed as part of F1.
