# API and Client Architecture

Status: **design contract — implementation pending**

## Purpose

Provide one stable, typed boundary between canonical inventory data and all clients: MSA Custom GPT, Telegram, Flutter, Google Sheets integration, and future tools.

## API role

The Inventory API is the normal write boundary for canonical data.

It should expose domain operations rather than database tables or arbitrary SQL.

Examples of future operation families:

### Read

- get products and lots
- get current stock
- get a monthly summary
- get receipt history
- get usage history
- get catalogue/version information
- get reconciliation status
- get audit entries subject to authorization

### Write

- record usage
- stage/import receipt batch
- confirm reviewed receipt line mappings
- create authorized product/lot
- record adjustment
- import catalogue version
- approve mapping change
- close month
- request mirror refresh

The exact endpoint list is implementation work and must follow the locked data model and integrity rules.

## Versioning

Use an explicit API version boundary such as `/api/v1`.

Breaking changes should create a new version or a controlled migration path rather than silently changing semantics for existing GPT/Telegram/Flutter clients.

## Stable hostname

Clients should use a domain such as:

`https://inventory.<custom-domain>`

Cloudflare Free may terminate/proxy traffic or provide DNS in front of the VPS.

Do not expose PostgreSQL publicly to clients.

## Authentication and authorization

Each client class should have independent credentials/scopes where practical.

Examples:

- MSA Custom GPT Action credential
- Telegram backend/internal credential
- Flutter user/session authentication
- Google Sheets sync service credential
- administrative maintenance credential

A leaked low-privilege client key should not grant full administrative/database access.

Secrets never belong in the public Git repository or OpenAPI example values.

## MSA Custom GPT Actions

The first planned direct ChatGPT integration is a dedicated private MSA Custom GPT using Actions against the VPS API.

Repository reservation:

`integrations/custom-gpt/`

Future contents may include:

- `openapi.yaml` — public schema without secrets
- setup notes
- operation/scope mapping
- test checklist

The GPT should call narrow operations, never arbitrary SQL or unrestricted generic mutation endpoints.

High-impact actions may require explicit conversational confirmation or server-side approval depending on the final safety design.

The architecture must not depend exclusively on Custom GPT Actions. If the feature becomes unavailable or unsuitable, Telegram, Flutter, Google Sheets, or another authorized API client must still work against the same backend.

## GPT Action reliability pattern

A write-capable action should include or obtain:

- stable target identity,
- operation/idempotency identifier,
- explicit quantity/date/source fields,
- review/approval status where required.

The server responds with structured outcome states such as:

- committed
- already applied
- review required
- conflict
- invalid request
- unauthorized
- failed/rolled back
- committed but mirror refresh pending

The GPT must not reinterpret a failure as success.

## Telegram

Telegram is a future convenience/control client, not a separate inventory engine.

Possible roles:

- stock lookup
- low-stock/expiry alerts
- receipt/usage capture
- image/document submission
- admin review/approval
- quick summaries

Telegram webhook path may live under the same stable host, for example `/webhooks/telegram`, while normal inventory operations remain under `/api/v1`.

The webhook handler must verify Telegram-specific authenticity/security requirements and translate requests into the same backend domain services.

## Flutter

Flutter is the planned richer human operational client.

It should use the same versioned API and canonical identities.

Potential capabilities:

- search/current stock
- usage entry
- receipt intake/review
- monthly history
- reorder view
- catalogue/history view
- reconciliation/admin screens

Do not embed database credentials in the app.

## AI API inside Telegram/Flutter

Future clients may use lower-cost AI APIs for conversational or document-understanding assistance.

Those models should remain orchestration/interpretation layers. They must submit the same validated typed operations to the backend and cannot bypass integrity rules simply because they are less capable than the subscription ChatGPT workflow.

## Google Sheets integration

After database promotion, a sync service or controlled integration translates canonical backend state into the Google workbook.

If Sheet-originated changes are supported, the integration translates only approved editable changes into API/domain commands.

Google Sheets is not a generic raw database synchronization channel.

## OpenAPI publication

The API may expose a sanitized OpenAPI schema at a stable URL for Custom GPT Action import, such as:

`https://inventory.<custom-domain>/openapi.yaml`

The schema may be public even when every operational endpoint requires authentication.

Never place API keys, example production IDs, live inventory data, or private URLs/tokens in the schema.

## Deployment independence

The API contract should remain stable if:

- VPS provider changes,
- reverse proxy changes,
- Cloudflare is removed or upgraded,
- application language/framework changes,
- PostgreSQL moves to another host later.

Clients depend on the domain contract, not implementation topology.

## Public repository safety

The repository may contain:

- API schemas,
- database migration source code,
- deterministic business logic,
- deployment templates with placeholders,
- architecture documentation.

It must not contain:

- production `.env`,
- DB passwords,
- bearer tokens,
- Telegram bot tokens,
- AI API keys,
- Google credentials,
- real operational exports or private evidence.
