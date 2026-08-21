# Canonical Inventory Architecture

Status: **design contract — implementation pending**

## Purpose

The current MSA skill safely operates a live Google workbook. The long-term system must reduce the amount of correctness that depends on manual spreadsheet mutation or LLM arithmetic while preserving the human workflow that already works.

The target architecture therefore separates:

- evidence and human interfaces,
- canonical transaction truth,
- deterministic inventory state,
- synchronized spreadsheet/report views,
- AI interpretation and orchestration.

## Canonical truth hierarchy

Once migration is complete, apply this hierarchy:

1. Original source evidence: transfer documents, usage forms, physical counts, approved catalogue files, explicit authorized corrections.
2. Canonical database transactions and approved master identities.
3. Deterministically derived inventory state and closed monthly snapshots.
4. Google Sheets operational mirrors and generated Excel exports.
5. Conversational summaries, caches, model memory, or other convenience representations.

Before database promotion, the current live workbook and source documents remain authoritative according to the existing skill contract.

## Target topology

```text
                         MSA Custom GPT
                              │
                              │ typed Action calls
                              ▼
Telegram ───────────────► Inventory API ◄────────────── Flutter
                              │
                              ▼
                    PostgreSQL on VPS
                    CANONICAL DATA LAYER
                              │
             ┌────────────────┼────────────────┐
             ▼                ▼                ▼
       Google Sheets      Excel exports     Backups
      operational mirror  archive/report    off-host
```

Cloudflare Free may provide DNS, TLS/proxying, and a stable custom subdomain in front of the VPS. Canonical business logic and canonical data do not depend on a paid Cloudflare database product.

## Stable public boundary

External clients should target a stable hostname such as:

`https://inventory.<custom-domain>`

The hostname is an infrastructure indirection boundary. Clients must not hard-code a VPS IP address. Moving the VPS or changing deployment providers should not require changing the domain contract or client business logic.

## Canonical database principle

The canonical database stores domain identities and transactions, not spreadsheet row positions.

A product or lot has a stable identifier even if its spreadsheet row changes, the visible sort order changes, or the item becomes inactive.

Spreadsheet row numbers are projections of the current operational view, not canonical identity.

## Ledger principle

Do not make a mutable `current_stock` cell the only canonical truth.

Canonical movement is represented as validated transactions such as:

- opening/brought-forward balance,
- receipt,
- usage/issue,
- positive or negative approved adjustment,
- other explicitly modeled movement types introduced later.

Current balance is derived deterministically from those movements under the applicable monthly/lot rules.

Materialized current-balance fields may exist for performance, but they must remain reproducible and verifiable from canonical transactions.

## Primary operational views

The following four concepts remain first-class because they match the established store workflow:

1. **Main Stock** — current lot-level inventory state.
2. **Daily Usage** — day-by-day monthly usage projection.
3. **This Month Received** — current-month receipt projection.
4. **Final Reorder** — current-month reorder calculation/output.

They are views/projections of canonical data rather than four independent sources of truth.

## AI boundary

AI is appropriate for:

- understanding photos and source documents,
- normalizing harmless wording differences,
- proposing product/CMS/lot matches,
- classifying SAFE / REVIEW / CONFLICT / NEW,
- explaining anomalies,
- orchestrating typed operations,
- assisting human review.

AI must not be trusted as the only mechanism for:

- arithmetic totals,
- balance derivation,
- duplicate prevention,
- transaction atomicity,
- database constraints,
- stable identifiers,
- authorization,
- audit persistence,
- month-close invariants.

Those responsibilities belong to deterministic backend code and PostgreSQL constraints/transactions.

## Write boundary

Normal canonical writes must enter through the Inventory API or an internal backend service using the same domain rules.

Never expose arbitrary SQL to the Custom GPT, Telegram bot, Flutter app, or Google Sheet integration.

Clients request narrow domain operations such as:

- record usage,
- import/confirm a receipt batch,
- create a new product or expiry lot,
- record an approved adjustment,
- close a month,
- request reconciliation.

The backend validates and either commits the complete operation or rejects it.

## Read/write separation during migration

The system will not immediately declare the new database canonical.

Migration progresses through shadow and verification phases defined in `MIGRATION_AND_SHADOW_VALIDATION.md`.

Until explicit promotion:

- existing Google Sheet procedures remain live,
- database results are compared against live workbook truth,
- automatic reverse writes are constrained,
- promotion requires reproducible agreement and rollback readiness.

## Repository architecture

Keep the existing Git-backed Personal Skill intact in the same repository.

Future implementation areas are siblings, not replacements:

- `skills/medicine-store-assistant/` — published workflow skill.
- `backend/` — deterministic API/application/database migrations.
- `integrations/custom-gpt/` — OpenAPI Action contract and GPT-specific integration notes.
- `integrations/google-sheets/` — mirror/sync integration.
- `integrations/telegram/` — Telegram adapter.
- `integrations/flutter/` — Flutter client integration notes/contracts.
- `deploy/` — VPS deployment configuration.

## Cost principle

Prefer existing paid infrastructure and free tiers before adding recurring services.

Initial target:

- existing VPS,
- PostgreSQL on that VPS,
- Cloudflare Free for public domain edge/DNS where useful,
- existing Google Sheets,
- existing GitHub repository,
- AI/API use only where its value justifies the cost.

Do not introduce Redis, Kafka, microservices, managed databases, or other paid infrastructure without a concrete demonstrated need.

## Portability principle

PostgreSQL is canonical because it is portable. Cloudflare, VPS provider, Custom GPT Actions, Telegram, Flutter, and Google Sheets are adapters around the domain model.

If any one client or platform becomes unavailable, the inventory truth must remain intact and accessible through another authorized path.
