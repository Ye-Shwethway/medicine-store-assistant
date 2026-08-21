# Cloudflare Route — Medicine Store Assistant

Status: **verified complete**

Date: 2026-08-22

## Scope

A narrow Cloudflare infrastructure change exposes the localhost-bound Medicine Store Assistant API through the existing managed Cloudflare Tunnel.

No Worker, D1, KV, R2, Pages, Load Balancer, Access policy, paid Cloudflare service, database schema, Sheet integration, Telegram/Flutter client, or Custom GPT Action was required for the route.

## Verified Cloudflare configuration

- hostname: `inventory.drthorne.uk`
- origin target: `http://localhost:8088`
- existing managed tunnel ID: `c15e7358-9276-4876-a14d-259b71fd8474`
- tunnel configuration source: Cloudflare-managed / remote configuration
- DNS record: proxied CNAME to the tunnel hostname
- existing unrelated tunnel routes were preserved
- VPS port `8088` remains non-public and localhost-bound

Tunnel ingress after the additive change:

```text
messenger.drthorne.uk  -> http://localhost:5001   # pre-existing
inventory.drthorne.uk  -> http://localhost:8088   # MSA
catch-all              -> http_status:404         # pre-existing
```

## End-to-end public verification

User-side mobile-browser verification on 2026-08-22 successfully opened:

`https://inventory.drthorne.uk/health`

The page returned the Medicine Store Assistant health JSON over HTTPS with:

- `ok: true`
- `service: medicine-store-assistant-api`
- `environment: foundation`
- `version: 0.1.0-dev`
- `database_canonical: false`

The screenshot was taken before the later F3 deployment, so the displayed build SHA reflected the then-current F2 runtime. Subsequent VPS verification confirmed the API advanced to F3 commit `dac1a4aa5b218d3c5eda24a636b3c3688979473b`. The browser evidence is sufficient to prove the public HTTPS/Tunnel path itself works end-to-end.

Therefore:

- Cloudflare route/DNS configuration: **verified**
- HTTPS edge/Tunnel/origin path: **verified**
- direct public exposure of VPS `:8088`: **not present**
- database canonicality: **unchanged / false**

## Security/privacy note

Do not store the VPS public IP, Cloudflare API credentials, tokens, connector secrets, operational inventory data, or private source data in this public repository.
