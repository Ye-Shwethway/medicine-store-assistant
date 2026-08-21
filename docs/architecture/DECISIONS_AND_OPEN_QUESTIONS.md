# Architecture Decisions and Open Questions

Status: **F2 schema/auth gates resolved; later-phase questions remain**

This file separates locked decisions from questions that still gate later implementation slices.

## Locked direction

### Repository and infrastructure

- Keep the public `medicine-store-assistant` repository.
- Preserve `skills/medicine-store-assistant/` as the independently installable Git-backed skill.
- Backend/runtime/integration code remains in sibling areas.
- PostgreSQL on the existing VPS is the future canonical datastore only after shadow validation and explicit promotion.
- Cloudflare Free/custom hostname is a transport/front-door layer, not a data store.
- Never commit production credentials or operational/private data.

### Inventory identity and history

- Stable `product_id` and `lot_id` are canonical identities; spreadsheet rows are presentation only.
- CMS code alone is never local identity.
- Normal v1 operational lot boundary is product + expiry date.
- Same-product/same-expiry receipts may share an operational lot while receipt-line provenance stays separate.
- `local_name` may change without changing `product_id` unless the actual medicine/device identity changes.
- Stock movement is ledger/event based; derived balances are deterministic backend calculations.
- One `OPENING_BALANCE` movement is used for migrated pre-existing lots at initial migration/canonicalization, not at every month boundary.
- Monthly opening is snapshot/derived state, not a repeated stock movement.
- Canonical quantities use fixed-point `NUMERIC(18,3)`; discrete-unit operations normally require whole quantities.
- No implicit unit conversion in v1.
- Normal writes must not create negative stock; privileged audited exceptions exist only for explicit reconciliation/correction cases.
- Corrections use reversal/amendment semantics rather than destructive history rewriting.

Canonical decision record: `F2_SCHEMA_DECISION_PROPOSAL.md` (approved/locked despite the historical filename).

### Human access and service identities

- Stable backend `user_id` is canonical human identity.
- v1 roles: `OWNER`, `ADMIN`, `STAFF`, `READ_ONLY`.
- Telegram numeric user ID is an external identity link; Telegram username is metadata only.
- Flutter uses native MSA credentials independent of Telegram, with modern password hashing and revocable token/session design when authentication is implemented.
- Disabled users remain in history; do not hard-delete identities with audit ownership.
- Custom GPT and other non-human clients use service principals with revocable scoped credentials.
- Every protected operation resolves actor + client/channel + operation ID + authorization context as appropriate.

Canonical access design: `USER_ACCESS_AND_AUTHORIZATION.md` and the approved F2 decision record.

### Human operational views

- Main Stock and Daily Usage are primary operational views.
- This Month Received is a generated/display projection, not an independent canonical store.
- Reorder/Final Reorder are workflow/display projections; final approved reorder output may be preserved in monthly history.

## F2 schema authorization

The schema-gating decisions that were previously open are now resolved. Slice F2 may create migration tooling and the initial foundation schema for:

- users/roles/external identities;
- service principals/credential metadata;
- products/product lots;
- operating months;
- CMS catalogue versions/items;
- audit-event foundation.

F2 does **not** authorize stock ledger writes, live inventory import, Sheet mirror conversion, Custom GPT write actions, or database canonical promotion.

## Later gate — reorder implementation

Before backend reorder calculation, inspect/document the exact current formula behavior including reorder level, surplus factor, estimated quantity, shortage date influence, expiry effects, rounding, exclusions, and manual overrides.

The display-only nature of This Month Received is already resolved; only compatibility details needed for exact export parity may remain.

## Later gate — Custom GPT write Actions

Before write Actions:

- finalize credential rotation/revocation process;
- define exact service scopes;
- define which high-impact operations require explicit user confirmation/approval;
- define client-generated/server-issued idempotency strategy.

Read-only GPT access may be tested earlier with a narrowly scoped service credential.

## Later gate — Google Sheet mirror writes

Before DB becomes canonical, decide the final Sheet-originated input policy:

- editable Daily Usage cells converted to typed operations;
- helper/input surface;
- or Flutter/Telegram preferred for writes with Sheet mostly read-only.

Also choose where canonical product/lot mapping metadata lives in the Sheet integration.

## Later gate — canonical promotion

Before promotion:

- choose/test off-VPS backup destination and retention;
- define measurable parity acceptance criteria;
- test restore;
- document rollback/cutback procedure.

## Deferred beyond v1

Do not block the first reliable backend on Redis, Kafka, microservices, advanced event-sourcing frameworks, managed paid databases, multi-region architecture, custom enterprise RBAC editors, SSO, MFA, complex offline synchronization, or fixed-asset redesign unless a concrete requirement emerges.
