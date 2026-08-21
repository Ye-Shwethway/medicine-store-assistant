# Cloudflare Route — Medicine Store Assistant

Status: **configured; public end-to-end health verification pending**

Date: 2026-08-22

## Scope

A narrow Cloudflare infrastructure change was made to expose the already-verified localhost-bound Medicine Store Assistant API through the existing managed Cloudflare Tunnel.

No application code, database schema, authentication, Custom GPT Action, Google Sheet, Telegram, Flutter, Worker, D1, KV, R2, Pages, Load Balancer, Access policy, or paid Cloudflare service was changed or created.

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

## Local origin already verified

Before Cloudflare routing, the VPS-local endpoint was verified:

`GET http://127.0.0.1:8088/health`

Expected/verified local payload:

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

## Public verification state

Public endpoint target:

`GET https://inventory.drthorne.uk/health`

Immediately after route creation, the available execution environments could not yet resolve the newly created hostname. Independent follow-up also returned DNS/cache resolution failure rather than an HTTP application response.

Therefore:

- Cloudflare route/DNS configuration: **verified created**
- direct public exposure of VPS `:8088`: **not present**
- public HTTPS end-to-end health response: **pending propagation / independent verification**

Do not claim the public endpoint fully verified until an independent request returns HTTP 200 with the expected health JSON.

## Security/privacy note

Do not store the VPS public IP, Cloudflare API credentials, tokens, connector secrets, operational inventory data, or private source data in this public repository.
