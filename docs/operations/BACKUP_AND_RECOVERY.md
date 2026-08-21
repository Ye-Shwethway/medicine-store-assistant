# Backup and Recovery Baseline

Status: **design baseline — implementation pending**

## Goal

Protect the future PostgreSQL canonical datastore from VPS loss, operator error, corruption, and failed deployment without introducing unnecessary paid infrastructure.

## Core rule

A backup stored only on the same VPS is not sufficient once PostgreSQL becomes canonical.

Before canonical promotion, the project must have:

- automated database backup;
- at least one off-VPS copy;
- documented retention;
- a tested restore procedure;
- evidence that the restored database can start and reconcile.

## Initial low-cost backup model

Start simple:

1. scheduled `pg_dump` in a compressed custom/plain format appropriate to the selected restore process;
2. keep a short local staging/retention window on the VPS;
3. copy encrypted/compressed backups to an off-VPS destination already available or chosen later;
4. periodically perform a restore test into an isolated database.

Do not require a paid managed backup service for v1.

## Suggested retention baseline

Initial target, adjustable after storage/cost review:

- daily: 7 copies;
- weekly: 4 copies;
- monthly: 12 copies.

Retention is not canonical business history; PostgreSQL itself retains monthly inventory/catalogue history. Backups exist for disaster recovery.

## What must be backed up

At minimum after DB introduction:

- PostgreSQL application database;
- migration/version metadata;
- configuration templates needed to rebuild the service, but not secrets in Git;
- separately protected runtime-secret recovery material through the user's normal secret-management method.

Raw operational photos/source documents are outside this database backup contract unless a future source-document storage design explicitly adds them.

## Restore test

A backup is not considered proven until restored.

Test procedure should verify:

1. restore into isolated database/container;
2. schema/migration version matches expectation;
3. representative counts and constraints are intact;
4. ledger-derived balances reconcile;
5. catalogue versions/history are queryable;
6. API can connect to the restored copy in isolated mode.

## Recovery scenarios

### Application deployment failure

Prefer application rollback/redeploy without touching the database.

### Accidental bad transaction

Use domain reversal/correction mechanisms when possible rather than restoring the entire database.

### Database corruption or destructive operator action

Stop writes, preserve current evidence, select a verified backup, restore into isolated environment first, compare, then perform controlled recovery.

### Complete VPS loss

Provision replacement host, restore repository/runtime, create new PostgreSQL instance, restore the selected off-VPS backup, validate, then repoint the stable custom hostname.

## Canonical promotion gate

PostgreSQL must not become the canonical source of truth until:

- off-VPS destination is chosen;
- automated backup works;
- restore has been tested successfully;
- recovery ownership and credentials are available;
- the result is recorded in continuity docs.

## Future enhancement

Point-in-time recovery/WAL archiving may be added if transaction volume and recovery objectives justify it. It is not required for the first shadow/foundation slices.
