# Inventory Integrity and Audit

Status: **design contract — implementation pending**

## Goal

Reduce the chance that a human, AI client, network retry, partial failure, or integration bug can silently corrupt canonical inventory data.

The system cannot guarantee that source evidence itself is always correct, but it should make silent internal inconsistency difficult and detectable.

## Core principle

LLM instructions are not integrity controls.

Integrity must be enforced by deterministic backend validation, PostgreSQL constraints, transaction boundaries, idempotency, audit records, and reconciliation checks.

## API validation

Every write endpoint must validate its request before changing canonical state.

Examples:

- referenced product/lot exists and is in an allowed state,
- quantity is numeric and within the operation's allowed sign/range,
- dates are valid and operationally permitted,
- required source references are present,
- receipt line belongs to the stated batch,
- actor is authorized for the requested operation,
- closed-month policy is respected,
- an operation cannot silently target an ambiguous identity.

Validation failure must produce a structured error and no partial canonical mutation.

## Database constraints

Use PostgreSQL constraints where the database can enforce truth directly.

Candidate constraints include:

- primary keys for stable identities,
- foreign keys between products/lots/transactions/receipt batches and lines,
- uniqueness for source identities such as receipt batch + source line where valid,
- non-null requirements for canonical fields that are truly mandatory,
- check constraints for quantities/statuses/dates where appropriate,
- uniqueness for idempotency keys within their intended scope.

Do not encode uncertain business interpretation as an overly rigid constraint. Keep ambiguous matching logic in the application/review layer.

## Idempotency

Any externally retriable write should support an idempotency key or a deterministic source uniqueness key.

Examples:

- receipt intake: stable operation identifier plus source batch/line uniqueness,
- usage entry submitted by app/bot/GPT: client-generated operation ID,
- month close: one idempotent close operation per month,
- catalogue import: source hash + version metadata.

A network retry or repeated GPT Action call must not duplicate stock movement.

Expected behavior for a repeated successful operation is a stable `already applied` or equivalent response containing the prior result.

## Atomic transactions

Operations that must succeed together belong in one PostgreSQL transaction or an equivalent controlled commit sequence.

For example, committing a receipt may require:

1. validate receipt batch/line,
2. create/link a lot if authorized,
3. create receipt transaction,
4. update any materialized current state,
5. write audit event,
6. commit.

If any required step fails, rollback the canonical mutation.

Do not create workflows where the canonical transaction succeeds but its required audit record silently fails.

## Derived-state invariant

For each lot, materialized/current balance must reconcile to canonical movement.

Conceptually:

```text
current balance
= opening/brought-forward
+ receipts
+ positive adjustments
- usage
- negative adjustments
```

The exact implementation may optimize this, but a reconciliation query must be able to prove equivalence.

## Negative-stock policy

Do not silently decide this during coding.

Before implementation, explicitly choose whether negative current stock is:

- impossible and transaction-blocking,
- allowed only by privileged adjustment,
- temporarily allowed but flagged as a hard reconciliation warning.

The decision should reflect real store operations, including late usage entry and delayed receipt documentation.

## Audit event

Every material canonical operation should have an append-only audit event containing enough information to answer:

- who/what initiated it,
- when it was recorded,
- effective operational date,
- operation type,
- affected identities,
- source reference,
- before/after or resulting domain state where useful,
- idempotency/operation ID,
- reason or review decision,
- outcome.

Audit must distinguish actor classes such as human admin, MSA Custom GPT, Telegram integration, Flutter user, Google Sheet bridge, migration importer, or backend maintenance.

Do not store secrets or raw credentials in audit payloads.

## Correction model

Once a transaction is operational history, prefer explicit reversal/correction rather than destructive overwrite or deletion.

A correction should preserve:

- original transaction,
- correcting/reversal transaction,
- reason,
- actor,
- timestamp,
- source/approval evidence where applicable.

This makes historical balance changes explainable.

## Read-back verification

The current skill requires read-back after spreadsheet writes. Preserve the same philosophy at the API layer.

A successful write response should include canonical identifiers and resulting state sufficient for the client to verify what was committed.

For high-impact operations, the orchestration layer may perform an independent GET/read after POST/commit before claiming success to the user.

## Reconciliation jobs

Provide deterministic reconciliation that can detect at least:

- ledger/current-balance mismatch,
- receipt lines without matching stock transaction,
- stock transactions with invalid/deleted dependencies,
- duplicate source lines that escaped earlier migration logic,
- closed-month snapshot mismatch,
- mirror divergence between PostgreSQL and Google Sheets after database promotion,
- catalogue mapping references to missing versions/rows.

Reconciliation should be safe/read-only by default. Repair actions require a separately authorized command.

## Review states

Preserve the skill's reasoning classes in domain workflows:

- SAFE
- REVIEW
- CONFLICT
- NEW / UNMAPPED

A REVIEW or CONFLICT record must not be silently converted into a canonical identity-sensitive transaction by a weaker client.

Backend permissions/endpoints should make it possible to stage ambiguous work separately from committed stock movement.

## Authorization

Authentication proves who/what is calling. Authorization controls what that actor may do.

Initial design should distinguish at least:

- read-only queries,
- routine usage entry,
- receipt intake,
- identity/mapping approval,
- stock adjustment,
- month close,
- administrative configuration.

The Custom GPT should receive only the minimum action scope needed for its approved workflows.

## Secrets

Never commit production secrets to this public repository.

Use VPS environment configuration or an appropriate secret store for:

- PostgreSQL credentials,
- GPT Action bearer/API keys,
- Telegram bot token,
- future AI API keys,
- Google integration credentials,
- deployment secrets.

## Backup and recovery minimum

Because PostgreSQL becomes canonical only after promotion, promotion requires off-host backup capability.

Initial minimum target:

- automated daily PostgreSQL dump,
- encrypted or appropriately protected off-host copy,
- retention across multiple days/weeks/months,
- tested restore procedure,
- backup failure alert or visible status.

Point-in-time recovery/WAL archiving may be added later if the demonstrated risk justifies the extra operational complexity.

## Failure reporting

Never convert a failed/uncertain write into a conversational success.

Clients should surface:

- validation failure,
- authorization failure,
- conflict/review requirement,
- idempotent prior completion,
- transaction failure/rollback,
- mirror-sync pending or failed,
- successful canonical commit with verification state.
