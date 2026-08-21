# User Access and Authorization Architecture

Status: **design contract — implementation pending**

## Purpose

Medicine Store Assistant is expected to be used not only by the owner but also by authorized store staff through future Telegram and Flutter clients. User identity, authentication, authorization, and audit attribution therefore belong in the v1 backend architecture rather than being added later as an unrelated patch.

This domain must remain separate from inventory identity. Products, lots, receipts, usage, catalogue records, and monthly snapshots must not carry Telegram-specific or Flutter-specific login fields directly.

## Canonical identity model

Use one stable internal user identity for a human staff member regardless of client.

Candidate `users` fields:

- `user_id` — immutable internal identifier
- `display_name`
- optional staff/reference identifier if the store uses one
- `status` — active, disabled, invited/pending, or another deliberately small approved set
- `created_at`
- `updated_at`
- optional `disabled_at`

Do not hard-delete a user who has operational history. Disable access while retaining audit attribution.

## External identities

A user may authenticate through one or more client-specific identities. Keep these in a separate mapping such as `user_identities` rather than adding every provider to `users`.

Candidate fields:

- `identity_id`
- `user_id`
- `provider` — e.g. `telegram`, `local`, future approved provider
- `provider_subject` — provider-stable identifier such as Telegram numeric user ID
- optional provider-facing username/display metadata
- `verified_at`
- `created_at`
- `revoked_at`

Provider usernames are not canonical identity because they can change. For Telegram, the numeric Telegram user ID is the stable external subject.

## Authentication vs authorization

Authentication proves who the caller is. Authorization determines what that identity may do.

The backend API owns authorization. Telegram buttons, Flutter screens, GPT instructions, or hidden UI controls must never be treated as the enforcement boundary.

## Minimal v1 roles

Start with a deliberately small role model unless a concrete workflow requires more:

- `OWNER` — system ownership, user/role management, high-impact approvals
- `ADMIN` — normal administrative inventory operations, subject to explicitly reserved owner-only actions
- `STAFF` — routine authorized store operations
- `READ_ONLY` — query/report access without inventory mutation

Avoid a complex enterprise RBAC matrix in v1. Store role assignments separately so they can evolve without changing inventory records.

Candidate structures:

- `roles`
- `user_roles`

A single-role-per-user implementation is acceptable initially if the schema can evolve cleanly, but authorization checks must be server-side.

## Service/client identities

Not every caller is a human user.

Custom GPT, Sheet synchronization, scheduled jobs, and future internal integrations may use service credentials. Represent them as service principals or an equivalent actor type rather than pretending they are staff accounts.

Audit should be able to distinguish:

- the authenticated service/client that submitted an operation,
- the human user on whose behalf the operation was requested when known.

Example: a Telegram bot service receives a command from staff user U. The canonical audit event should retain both the Telegram service/client context and U as the initiating human actor.

## Audit attribution

Operational records and audit events should reference stable actor identifiers.

At minimum, committed receipt/usage/adjustment/correction/month-close operations should preserve:

- initiating user/service identity
- authenticated client/channel
- operation ID / idempotency key
- timestamp
- authorization result or relevant approval identity for high-impact actions

Disabling or renaming a user must not break historical attribution.

## Access lifecycle

The backend should support a controlled lifecycle:

1. owner/admin creates or approves a staff account
2. one or more external identities are linked/verified
3. role is assigned
4. authenticated requests are authorized server-side
5. access can be disabled/revoked immediately without deleting history

Self-registration should not automatically grant store access unless explicitly designed later.

## Telegram direction

Telegram should use the sender's numeric Telegram user ID as the external identity key.

A username is useful metadata but must not be trusted as the stable account key.

Unknown Telegram users should default to no operational access. A future onboarding flow may allow an owner/admin to approve and link them to a canonical MSA user.

## Flutter direction

Flutter should authenticate against the backend, not against PostgreSQL directly.

The exact login mechanism remains an implementation decision. Possible v1 approaches include owner-created credentials or a later external identity provider. Password storage, if used, must use a standard secure password-hashing library and never plaintext/reversible storage.

The choice of Flutter login method must not change the canonical `user_id` model.

## Custom GPT direction

The private MSA Custom GPT should initially use a revocable service credential with narrowly scoped API access.

It is not automatically equivalent to the OWNER role. Backend permissions determine what its credential can call.

When a GPT-mediated action represents a human user's instruction, retain an explicit human approval/actor context where the API workflow supports it, especially for high-impact writes.

## High-impact authorization

Actions likely to require elevated permissions and/or explicit approval include:

- user/role management
- stock adjustments
- historical corrections
- ambiguous identity/mapping approval
- month close/reopen/amendment
- canonical promotion/migration controls

Exact role/action mapping is a schema/API implementation gate and should remain small in v1.

## Security boundaries

- never expose database credentials to Telegram, Flutter, GPT, or Sheets
- never authorize from client UI state alone
- use revocable credentials/tokens
- support credential rotation
- rate-limit/authenticate public API paths as appropriate
- preserve audit history after account disablement
- do not commit user credential material or production identity exports to the public repository

## Schema relationship

The inventory schema should reference an actor/user identity where attribution matters, for example `created_by_user_id`, `approved_by_user_id`, or a generalized actor reference.

Do not duplicate staff name, Telegram ID, or role strings into every inventory table as the source of truth. Historical display snapshots may preserve names for reporting, but authorization is based on current canonical identity/role state.

## v1 principle

Design user identity into the schema now; implement only the minimum authentication/role machinery needed by the first real multi-user client. This avoids both extremes: retrofitting identity after operational history exists, and over-engineering a large enterprise IAM system before it is needed.
