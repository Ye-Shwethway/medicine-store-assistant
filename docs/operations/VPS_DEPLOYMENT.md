# VPS Deployment Baseline

Status: **design baseline — deployment not yet authorized**

## Goal

Run Medicine Store Assistant backend on the existing VPS at minimal additional recurring cost while isolating it from other services.

## Baseline topology

```text
Cloudflare Free / custom DNS
        ↓ HTTPS
reverse proxy on VPS
        ↓ private app port
inventory API container
        ↓ private Docker network
PostgreSQL container
```

## Required boundaries

- PostgreSQL must not expose a public internet port.
- Public traffic reaches only the reverse proxy/API HTTPS endpoint.
- Runtime secrets live on the VPS in protected environment/secret files, never in Git.
- Use a dedicated project directory and preferably a dedicated least-privilege service user.
- Do not modify unrelated VPS services, ports, firewall rules, or reverse-proxy sites without explicit need and verification.
- Health endpoint must not disclose secrets or sensitive inventory data.

## Initial deployment profile

Prefer a small Docker Compose deployment:

- `api`
- `postgres`

Do not add Redis, message brokers, workers, or additional databases until a concrete requirement exists.

## Repository/deployment relationship

GitHub remains code/docs distribution only.

Because GitHub Actions quota is not assumed, deployment must not depend on Actions. Supported low-cost approaches include:

1. controlled manual `git pull` + `docker compose up -d --build` during early development;
2. later VPS pull-based deploy using a restricted script/service;
3. later webhook-triggered pull/deploy only after authentication and rollback behavior are designed.

For the first implementation slices, prefer explicit controlled deployment over autonomous webhook deployment.

## Suggested host layout

Example only; inspect the live VPS first:

```text
/opt/medicine-store-assistant/
  repo/
  runtime/
  backups/
```

Exact paths must be chosen after checking existing conventions and permissions.

## Reverse proxy / hostname

Use a stable custom hostname such as a dedicated inventory/MSA subdomain. Do not hard-code the VPS IP into GPT, Telegram, or Flutter clients.

Configure the hostname only after the API has a verified local health endpoint. Cloudflare is the DNS/TLS/public-front-door layer, not the canonical database.

## Health checks

Minimum health model:

- process/container health;
- API `/health` response;
- separate readiness status for PostgreSQL connectivity where needed.

The public health endpoint should remain safe and minimal.

## Deployment verification

After each deployment:

1. verify containers/services are healthy;
2. verify local API health on VPS;
3. verify HTTPS health through the public hostname when configured;
4. verify PostgreSQL is not publicly reachable;
5. verify unrelated services remain healthy;
6. record deployed commit/version.

## Rollback baseline

Before production write authority exists, rollback can normally mean redeploying the prior known-good application commit while preserving database volume.

After schema/data writes begin, application rollback and database rollback must be treated separately. Never destroy or downgrade canonical data casually.

## Security baseline

- firewall/host rules should expose only required public services;
- database credentials must be unique to MSA;
- use a revocable API credential per client/integration when write clients are introduced;
- logs must avoid secrets and sensitive raw documents;
- public repository contains templates/examples only.
