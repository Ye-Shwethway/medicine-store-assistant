# Medicine Store Assistant — Architecture Index

Status: **documentation-first / implementation not yet authorized**

This directory defines the future canonical architecture for Medicine Store Assistant (MSA) beyond the current spreadsheet-operating skill.

The existing Git-backed skill remains canonical at:

`skills/medicine-store-assistant/`

The architecture described here must not move, rename, replace, or weaken that published skill structure.

## Core decision

MSA will evolve toward a ledger-backed inventory system in which:

- PostgreSQL on the existing VPS is the planned canonical operational datastore.
- The inventory API is the only normal write boundary to canonical data.
- Google Sheets remains a human-facing operational mirror and migration/reconciliation surface.
- Excel remains a compatible export/archive/report surface rather than the only historical store.
- Telegram, Flutter, the MSA Custom GPT, and other future clients use typed API operations rather than direct database writes.
- AI interprets evidence and orchestrates workflows; deterministic backend code owns arithmetic, constraints, idempotency, transactions, and derived state.
- The current Google-Sheets-first workflow remains authoritative until the migration plan explicitly promotes the database after shadow validation.

## Documents

1. [CANONICAL_INVENTORY_ARCHITECTURE.md](CANONICAL_INVENTORY_ARCHITECTURE.md) — system boundaries, source-of-truth model, client roles, and AI/code separation.
2. [INVENTORY_DATA_MODEL.md](INVENTORY_DATA_MODEL.md) — products, lots, transactions, receipts, usage, stable identity, lifecycle, and ordering.
3. [MONTHLY_LIFECYCLE.md](MONTHLY_LIFECYCLE.md) — monthly open/close, snapshots, archive semantics, next-month preparation, and Excel Master compatibility.
4. [CMS_CATALOGUE_VERSIONING.md](CMS_CATALOGUE_VERSIONING.md) — full catalogue version history, diffs, mappings, and current-price projection.
5. [INVENTORY_INTEGRITY_AND_AUDIT.md](INVENTORY_INTEGRITY_AND_AUDIT.md) — constraints, idempotency, transactions, audit, verification, reconciliation, and recovery.
6. [SHEET_MIRROR_AND_COMPATIBILITY.md](SHEET_MIRROR_AND_COMPATIBILITY.md) — Google Sheets mirror contract and Excel compatibility.
7. [API_AND_CLIENT_ARCHITECTURE.md](API_AND_CLIENT_ARCHITECTURE.md) — VPS API, Custom GPT Actions, Telegram, Flutter, and future access paths.
8. [MIGRATION_AND_SHADOW_VALIDATION.md](MIGRATION_AND_SHADOW_VALIDATION.md) — safe migration from the current spreadsheet-first system to database canonicality.

## Repository boundary

The intended same-repository layout is:

```text
medicine-store-assistant/
├── skills/medicine-store-assistant/   # published Git-backed skill; preserve
├── docs/architecture/                 # canonical system design
├── backend/                           # future deterministic API + DB runtime
├── integrations/                     # future GPT/Sheets/Telegram/Flutter adapters
├── deploy/                            # future VPS deployment assets
├── AGENTS.md
├── NORMAL_CHAT_BOOTSTRAP.md
└── README.md
```

Folders shown as `future` are architectural reservations only until implementation is explicitly authorized.

## Design rule

Do not implement from one document in isolation. The data model, integrity rules, monthly lifecycle, mirror contract, and migration plan form one system contract and must remain mutually consistent.
