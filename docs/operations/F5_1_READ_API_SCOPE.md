# F5.1 — Authenticated Catalogue Read API Scope

Status: **authorized and authored; runtime verification pending**

F5.1 extends the existing authenticated read-only API with catalogue diagnostics only.

Included read operations:

- list catalogue versions with F5 version metadata;
- read current catalogue-version diagnostics;
- list items for a selected historical version;
- deterministic diff between two stored catalogue versions.

All `/v1` catalogue endpoints inherit the existing `inventory:read` bearer-authentication boundary.

No catalogue import/write endpoint is exposed. No local product/lot mapping mutation is exposed. No live Google Sheet or real CMS catalogue ingestion is included. PostgreSQL remains non-canonical.

Runtime verification must prove the expected GET surface exists, no POST/PUT/PATCH/DELETE catalogue surface exists, F5 synthetic catalogue invariants still pass, and `/health` + `/ready` remain healthy with `database_canonical: false`.
