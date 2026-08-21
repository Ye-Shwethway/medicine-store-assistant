# Medicine Store Assistant — Implementation Plan

Status: **planning complete enough for foundation work; production write authority not yet authorized**

This plan translates the approved architecture into small, reversible implementation slices. It does not replace `ROADMAP.md`; it defines execution order and exit criteria.

## Global rules

- Preserve `skills/medicine-store-assistant/` unchanged as the canonical Git-backed skill source.
- No production database canonicality until shadow validation and explicit promotion.
- No client receives arbitrary SQL or database credentials.
- Secrets never enter the public repository.
- Every slice must leave `NEW_CHAT_BOOTSTRAP.md`, `ROADMAP.md`, and relevant canonical docs current.
- Prefer the smallest runnable slice; avoid Redis, queues, microservices, managed paid databases, or other infrastructure without a concrete need.

## Slice F0 — Infrastructure inspection and safe host preparation

Purpose: prepare the existing VPS without deploying inventory logic.

Tasks:
- inspect OS, CPU/RAM/disk, Docker/Compose, reverse proxy, firewall, existing services, free ports, backup storage, and Git access;
- choose a dedicated host path and service user;
- install only missing baseline packages required for Docker/Compose/PostgreSQL deployment;
- do not expose a public inventory port yet;
- do not create production data or credentials in Git.

Exit criteria:
- documented VPS inventory and conflicts;
- reserved service path;
- Docker/Compose usable;
- no existing production service disturbed.

## Slice F1 — Repository runtime skeleton

Purpose: establish sibling implementation areas while preserving the skill.

Create minimal structure:
- `backend/`
- `deploy/`
- `integrations/custom-gpt/`
- `integrations/google-sheets/`
- `docs/operations/`

Add a minimal API service with:
- `/health`
- build/version metadata
- no canonical inventory writes
- no production database dependency required for the health endpoint.

Exit criteria:
- local build passes;
- container starts;
- health endpoint returns deterministic response.

## Slice F2 — PostgreSQL foundation

Purpose: create an isolated database foundation without importing live inventory yet.

Tasks:
- PostgreSQL container/service on private Docker network;
- database/user created through runtime secrets;
- migration mechanism;
- connection health/readiness;
- initial schema only after gated domain decisions are locked;
- no public database port.

Exit criteria:
- migrations can apply from empty database;
- clean reset works in non-production environment;
- API can connect with least-privilege application credentials.

## Slice F3 — Core read-only domain model

Purpose: encode stable identity and deterministic reads before real writes.

Initial entities:
- products;
- product lots;
- operating months;
- CMS catalogue versions/items;
- audit metadata foundation.

Add read-only API endpoints for diagnostics and empty/test fixtures only.

Exit criteria:
- constraints enforce stable identity rules;
- no spreadsheet row number is a primary identity;
- no CMS code is a local primary key.

## Slice F4 — Ledger primitives in isolated test mode

Purpose: implement receipt, usage, opening, and adjustment mechanics with synthetic data only.

Requirements:
- typed domain operations;
- idempotency keys;
- atomic transactions;
- reversal/correction links;
- deterministic balance calculation;
- audit event for every committed operation.

Exit criteria:
- duplicate replay cannot duplicate stock movement;
- failed multi-step operation rolls back;
- derived balance exactly reconciles with ledger.

## Slice F5 — CMS catalogue versioning

Purpose: prove full catalogue import/version/diff capability.

Tasks:
- import a non-sensitive sample catalogue first;
- hash/version metadata;
- deterministic diff for new/removed/changed rows;
- current-version projection;
- no automatic local product remapping from code alone.

Exit criteria:
- repeated same import is idempotent;
- historical versions remain queryable.

## Slice F6 — Shadow migration adapter

Purpose: import a verified snapshot of current Main Stock/Daily Usage into a shadow database.

Rules:
- Google Sheet remains authoritative;
- migration is repeatable/idempotent;
- no Sheet mutation required for import;
- preserve provenance and migration batch ID;
- produce mismatch report rather than silently repairing.

Exit criteria:
- all rows/lots classified;
- unexplained parity differences are surfaced;
- rerun does not duplicate entities or movements.

## Slice F7 — Shadow projection parity

Generate backend projections equivalent to:
- Main Stock;
- Daily Usage;
- This Month Received;
- Reorder working projection once its formula contract is encoded.

Compare backend output against the live workbook while the workbook remains canonical.

## Slice F8 — Private Custom GPT Action experiment

Only after the read-only API is stable:
- expose a private HTTPS API through the chosen custom subdomain;
- version-control `integrations/custom-gpt/openapi.yaml`;
- start with read-only Actions (`health`, stock lookup, lot lookup, audit/summary reads);
- use a revocable scoped bearer key;
- do not enable stock writes in the first GPT experiment.

Exit criteria:
- Custom GPT can call the VPS API reliably;
- authentication, timeout, and response behavior are verified.

## Slice F9 — Controlled write Action experiment

Only after ledger/idempotency/audit tests pass:
- add one low-risk typed write operation first;
- require server-side validation and operation ID;
- read back committed state;
- do not make the DB canonical yet.

## Slice F10 — Dual real-workflow validation

Run representative live operations through current Sheet workflow plus backend shadow path and compare results. No automatic cutover.

## Slice F11 — Canonical promotion

Requires explicit approval, tested backups/restores, measurable parity acceptance, and rollback/cutback procedure.

## Recommended immediate order

1. Finish architecture gates that affect schema.
2. Run Slice F0 via a one-time VPS setup assistant/agent relay.
3. Implement F1 in this repository.
4. Implement F2/F3 after schema decisions are locked.
5. Configure Cloudflare/custom subdomain only when an API health endpoint exists to target.
6. Create the dedicated MSA Custom GPT only when the read-only OpenAPI contract is ready; creating it earlier adds no useful capability and creates manual rework.
