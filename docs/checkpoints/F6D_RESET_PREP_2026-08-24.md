# F6D Reset Preparation — 2026-08-24

Status: preparation only; no inventory reset executed yet.

## Runtime finding

The target database migration reached `0022_inventory_foundation`, but backend readiness still expected `0021_review_orchestration_roles`. The API therefore returned `/ready` = 503 even though the database migration itself completed.

The readiness guard is being aligned to the Alembic head and a CI drift check is added so future schema-head changes cannot silently leave `/ready` stale.

## Existing shadow state

The target runtime still reports the old F6B test-only batch:

- batch id: `be13d127-5045-4284-a088-0a0b9b024d76`
- row count: 1,646
- SAFE: 1,417
- REVIEW: 222
- CONFLICT: 0
- NEW_UNMAPPED: 7

This data is not an accepted F6D migration baseline and must not be mixed with the fresh real-shadow dataset.

## Reset boundary — OWNER APPROVED

After runtime health is restored, perform a bounded inventory-domain reset only.

Preserve:

- Alembic/schema state;
- `stores` schema and seeded `MAIN` Store identity;
- users, roles and sessions;
- AI agents and provider/model configuration;
- MCP/OAuth identities and credentials;
- AI Workspace conversations/reviews/artifacts/events;
- service principals;
- system/audit infrastructure unrelated to test inventory rows.

Reset test/shadow inventory state after a pre-reset audit confirms scope:

- legacy migration batches/source rows;
- test/synthetic inventory transactions;
- test receipt/transfer rows;
- test Product/Lot rows;
- test Product-CMS mappings;
- test CMS catalogue rows only if the audit confirms they are not the intended retained real catalogue dataset;
- test inventory-month/snapshot state where present.

## Execution gate

1. `/ready` healthy at migration `0022_inventory_foundation`.
2. Read-only database audit records exact row counts and unexpected dependencies.
3. Reset script refuses to run on a migration other than `0022_inventory_foundation`.
4. Reset script preserves `MAIN` Store and non-inventory control-plane data.
5. Post-reset verification proves inventory shadow state is empty/seed-only as intended.
6. Only then stage the fresh live workbook snapshot.
7. PostgreSQL remains non-canonical: `database_canonical=false`, `migration_baseline_accepted=false`.
