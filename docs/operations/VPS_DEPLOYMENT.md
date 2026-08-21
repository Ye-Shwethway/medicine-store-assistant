# VPS Deployment Baseline

Status: **F1 runtime foundation deployed and verified; production write authority not enabled**

## Goal

Run Medicine Store Assistant backend on the existing VPS at minimal additional recurring cost while isolating it from other services.

## Verified current topology

```text
Cloudflare edge/tunnel (hostname route not yet configured for MSA)
        ↓ future HTTPS route
127.0.0.1:8088 on VPS
        ↓
MSA API container
        ↓ private Docker network
MSA PostgreSQL container
```

The VPS uses an existing managed-token `cloudflared` tunnel rather than a host nginx/Caddy reverse proxy. MSA hostname routing should therefore be configured through the existing Cloudflare tunnel/Zero Trust routing when authorized.

## Verified F1 runtime

As of 2026-08-22:

- deployed repository commit: `408dcbbdba6c579f446d303197c9071340188619`;
- API container: `deploy-api-1`;
- PostgreSQL container: `deploy-db-1`;
- API bind: `127.0.0.1:8088 -> 8080` only;
- PostgreSQL has no host-published port;
- internal network: `deploy_msa_internal`;
- named PostgreSQL volume: `deploy_msa_postgres_data`;
- API memory cap: 384 MiB;
- PostgreSQL memory cap: 512 MiB;
- `/health` returns HTTP 200 with `database_canonical: false`.

Canonical verification evidence: `F1_VPS_RUNTIME_VERIFICATION_2026-08-22.md`.

## Required boundaries

- PostgreSQL must not expose a public internet port.
- API remains localhost-only at the host layer unless a later architecture decision explicitly changes that model.
- Public traffic should reach MSA through the existing Cloudflare tunnel/custom hostname, not a raw VPS application port.
- Runtime secrets live on the VPS in protected environment/secret files, never in Git.
- Do not modify unrelated VPS services, ports, tunnel routes, or existing databases without explicit need and verification.
- Health endpoints must not disclose secrets or sensitive inventory data.
- PostgreSQL deployment does not make the database canonical; canonical promotion requires shadow/dual validation and explicit approval.

## Initial deployment profile

Keep the deployment minimal:

- `api`
- `postgres`

Do not add Redis, message brokers, extra databases, or host reverse proxies until a concrete requirement exists.

## Repository/deployment relationship

GitHub remains code/docs distribution only. Deployment must not depend on GitHub Actions quota.

Early development may use explicit controlled deployment:

1. fast-forward the canonical public repository checkout;
2. run the repository validator;
3. build/deploy with Docker Compose;
4. verify local health/exposure;
5. record the deployed commit.

Autonomous pull/webhook deployment is deferred until authentication, rollback and operational ownership are designed.

## Current host layout

Prepared host area:

```text
/opt/medicine-store-assistant/
  app/repo/
  deploy/
  secrets/
  .notes/
```

Runtime secrets are outside Git. Do not commit VPS runtime files or operational data.

## Secret-safe Compose validation

Important F1 observation: a normal `docker compose ... config` command with the real runtime env file can interpolate secret values into rendered stdout, including credentials embedded in `DATABASE_URL`.

Therefore:

- use `docker compose ... config --quiet` when only syntax/config validation is needed;
- do not paste rendered Compose output from a secret-bearing runtime env into chat, CI logs, tickets or documentation;
- never store rendered secret-bearing configuration in Git;
- rotate a credential if it is ever exposed to an untrusted destination.

## Cloudflare / hostname

Use a stable custom hostname for the Inventory API. Do not hard-code the VPS IP into GPT, Telegram or Flutter clients.

The MSA route should target the verified local origin:

`http://localhost:8088`

Configure this only through the existing managed Cloudflare tunnel after an explicit route-configuration slice. Cloudflare remains the DNS/TLS/public-front-door layer, not the canonical datastore.

## Health checks

Minimum health model:

- process/container state;
- API `/health`;
- separate database readiness/connectivity endpoint when introduced.

The public `/health` endpoint should stay safe and minimal.

## Deployment verification

After each deployment:

1. verify repository validator if applicable;
2. verify Compose/container state;
3. verify local API health;
4. verify localhost-only host binding;
5. verify PostgreSQL has no host-published port;
6. verify HTTPS health through the public hostname once configured;
7. verify unrelated VPS services remain healthy;
8. record deployed commit/version.

## Rollback baseline

Before production write authority exists, application rollback can normally mean redeploying the prior known-good application commit while preserving the PostgreSQL volume.

After schema/data writes begin, application rollback and database/schema rollback must be treated separately. Never destroy or downgrade canonical data casually.

## Security baseline

- database credentials are unique to MSA;
- clients receive revocable scoped credentials, never DB credentials;
- logs must avoid secrets and sensitive source documents;
- public repository contains templates/examples only;
- staff/user authorization is a backend domain concern and must be designed before multi-user write clients are enabled.
