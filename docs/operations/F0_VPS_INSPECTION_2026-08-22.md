# F0 VPS Foundation Inspection — 2026-08-22

Status: **completed via one-time VPS setup agent relay; no application implementation performed**

This document records the verified host-preparation evidence reported for Medicine Store Assistant Slice F0. It is infrastructure evidence, not proof that the future API/database is deployed.

## Host baseline

- Ubuntu 24.04.4 LTS (Noble), x86_64, kernel 6.8.0-106
- 2 vCPU Intel Xeon E5-2690 v2 @ 3.0 GHz
- RAM: 3.3 GiB total, about 1.4 GiB available at inspection time
- Swap: 1.5 GiB total, about 1.1 GiB already used at inspection time
- Root disk: 63 GiB total, about 17 GiB free / 72% used
- Inodes healthy at about 22% used
- Docker Engine 29.3.0 active/enabled
- Docker Compose plugin 5.1.1 available; legacy 5.1.0 also present
- Git 2.43.0 available
- curl/wget available

## Existing runtime/public-edge model

- No host-side nginx/Caddy/Traefik reverse proxy was found.
- `cloudflared` runs as a systemd service using a managed tunnel token.
- Local `~/.cloudflared/` has no ingress configuration; hostname routing is controlled in Cloudflare dashboard/Zero Trust.
- Tunnel identifier reported during F0: `c15e7358-9276-4876-a14d-259b71fd8474`.
- `127.0.0.1:20241` is the tunnel metrics/diagnostic endpoint, not an application endpoint.

Existing publicly bound services reported during inspection include SSH and several unrelated services. Medicine Store Assistant must not copy those public-binding patterns by default.

## Prepared MSA host area

The following host paths were created without cloning application code or creating credentials:

- `/opt/medicine-store-assistant/`
- `/opt/medicine-store-assistant/app/`
- `/opt/medicine-store-assistant/deploy/`
- `/opt/medicine-store-assistant/secrets/`
- `/opt/medicine-store-assistant/.notes/`

A system user `medstore` was created with UID 995 and `/usr/sbin/nologin`.

No application code was cloned. No database credentials were generated. No new public port was opened.

## Existing PostgreSQL evidence

- A host PostgreSQL service already listens on `127.0.0.1:5432`; it is unrelated to MSA and must not be reused.
- Another Docker PostgreSQL/pgvector service was reported on host port `5433`; it is unrelated to MSA and must not be modified.
- MSA PostgreSQL remains planned as an isolated project container on a private Docker network. Normal architecture does not require publishing the database port to the host at all.

## Binding rule locked from F0

The future Inventory API must bind to localhost only when exposed to the host, for example:

```text
127.0.0.1:8088:8080
```

Do not publish the Inventory API on `0.0.0.0` merely to make Cloudflare routing easier. `cloudflared` can target the localhost service.

Preferred first API host port: `8088`, subject to read-back conflict check immediately before deployment.

The database should normally be reachable only on the internal Docker network. A host PostgreSQL port such as `5434` is not required for normal production operation and should be omitted unless a specific maintenance workflow justifies a localhost-only bind.

## Resource constraints

The VPS is usable but resource-constrained.

Initial runtime should remain small:

- API target memory envelope: roughly 256–384 MiB
- PostgreSQL target memory envelope: roughly 384–512 MiB, tuned conservatively
- avoid Redis, brokers, sidecars, duplicate reverse proxies, or other memory-consuming infrastructure without a concrete requirement
- monitor disk growth, PostgreSQL volume growth, logs, and Docker layers

These are starting constraints, not guaranteed final tuning values. Measure after deployment before increasing limits.

## Security observations

- No active UFW/nftables host firewall was reported.
- Therefore localhost-only Docker publishes are a hard MSA deployment requirement unless a later explicitly reviewed network design says otherwise.
- Existing unrelated public bindings are not precedent for MSA.
- Secrets belong in protected VPS runtime configuration, never in the public Git repository.

## F0 conclusion

F0 exit criteria are satisfied:

- host baseline inspected;
- conflicts identified;
- Docker/Compose/Git available;
- dedicated project path prepared;
- no existing production service disturbed;
- no MSA public service/database was deployed.

## Authorized next slice

The next slice is **F1 — Repository Runtime Skeleton**.

F1 must not define the canonical inventory schema yet. It should create the minimal backend/container/runtime skeleton and deterministic `/health` endpoint while preserving the published skill tree.
