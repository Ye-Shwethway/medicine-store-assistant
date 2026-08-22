# User Access and Authorization Architecture

Status: **F7.2A canonical human identity/session foundation verified; F7.2B User Management next**

## Purpose

Medicine Store Assistant will be used by the owner and authorized staff through future Telegram and Flutter clients. User identity, authentication, authorization, service identities, and audit attribution therefore belong in the backend foundation rather than being retrofitted after operational history exists.

This domain remains separate from inventory identity. Products, lots, receipts, usage, catalogue records, and monthly snapshots must not contain Telegram- or Flutter-specific login fields as their identity source.

## Canonical human identity

Use one stable internal `user_id` for each human staff member regardless of client.

The deployed F7.2A implementation reuses the F2 `users`, `roles`, and `user_roles` tables. Human identity now includes stable UUID `user_id`, display name, username, password hash where applicable, canonical state, credential version, timestamps, and exactly one current v1 role from the approved static role set.

Users with historical operational records are disabled/revoked rather than hard-deleted.

Canonical states are:

- `PENDING`
- `ACTIVE`
- `DISABLED`

## External identities

Provider-specific identities live separately from `users`.

For Telegram:

- numeric Telegram user ID is the stable external subject;
- Telegram username/display name is mutable metadata only;
- unknown/unlinked Telegram identities receive no operational access by default.

A user may later link multiple approved identity providers without changing canonical `user_id`.

## Authentication vs authorization

Authentication proves caller identity. Authorization determines allowed operations. The backend API is always the enforcement boundary; client buttons, hidden screens, GPT instructions, or UI state are not authorization controls.

F7.2A establishes backend role dependencies that resolve the current session to canonical human identity and reject insufficient authenticated authority with HTTP `403` / `Access denied`.

## Approved minimal v1 roles

- `OWNER` — full system authority, user/admin management, high-risk approvals, month-close/canonical-promotion authority.
- `ADMIN` — operational administration and approved inventory management; cannot implicitly become Owner.
- `STAFF` — routine reads and approved day-to-day operational entry; no privileged historical correction, role management, or system configuration.
- `READ_ONLY` — inventory/history/report reads only.

Use a small static permission matrix initially. Do not build an arbitrary enterprise permission editor in v1.

## Web/native account baseline

The canonical MSA account is client-independent and may later be used by Web, Flutter, and other approved clients:

- user-chosen/assigned username;
- password stored only as a one-way secure hash;
- durable revocable session bound to canonical `user_id`;
- server-side account-state and role checks on every protected operation.

F7.2A specifically preserved the already-deployed Owner PBKDF2 hash so the temporary password-only bridge could migrate into the canonical account model without obtaining or logging plaintext credentials. This is a compatibility migration, not the final credential-lifecycle decision. Password change/reset and any deliberate future hash upgrade belong to F7.2C.

Email/phone remain optional profile/recovery metadata rather than mandatory v1 identity.

## Durable session model — F7.2A verified

The deployed `user_sessions` model stores server-side session metadata rather than trusting a self-contained Owner token:

- stable `session_id`;
- canonical `user_id`;
- keyed digest of an opaque browser token rather than the raw token;
- credential-version binding;
- creation/expiry/revocation timestamps;
- last-seen metadata.

Protected session resolution requires:

- session exists and is not revoked;
- session has not expired;
- session credential version matches the current user credential version;
- user state is `ACTIVE`;
- current canonical role is resolved from backend role state.

Therefore a `DISABLED` user loses protected access immediately even if an old browser token still exists.

Verified anchor: PR #36, merge `c3aa75d65e0bc6d1836227fe8450b0b3de5b2651`, deploy run `32586385336` / job `97063270146`.

## Service principals

Non-human clients use separate service principals rather than human accounts.

Examples:

- private MSA Custom GPT;
- Google Sheets synchronization service;
- future internal adapters/jobs.

Service credentials are revocable and scoped. Store verifier-safe/hash material where feasible; never plaintext API keys in Git, audit logs, or canonical operational exports.

The private Custom GPT begins with narrow read-only scopes when that integration is implemented; it is not automatically equivalent to `OWNER`.

AI Agent Management remains the later F7.2D Owner-only slice and is not implemented by F7.2A.

## Audit attribution

Every protected domain operation resolves actor context containing at least:

- human `user_id` or service-principal ID;
- client/channel such as Flutter, Telegram, Custom GPT, Sheet sync, or internal/admin;
- operation/idempotency ID;
- timestamp;
- authorization role/scope context where useful;
- reason/approval information for privileged actions.

When a service acts on behalf of a known human, later audit design should retain both authenticated service/client context and initiating/approving human context where applicable.

Disabling or renaming an account never breaks historical attribution.

F7.3 remains the later operational Actor-aware Audit / Operation Ledger slice. F7.2B may add only the minimum security/account-event prerequisite required for User Management.

## Access lifecycle

1. F7.2B creates or receives a pending staff account/access request.
2. Owner or narrowly authorized Admin reviews according to backend policy.
3. Allowed role is assigned and account becomes `ACTIVE`, or request is rejected/disabled.
4. Backend authenticates and authorizes every protected request through the F7.2A session/RBAC foundation.
5. Access can be disabled/revoked without deleting historical identity.

Self-registration never automatically grants store access in v1.

## F7.2B next boundary

F7.2B User Management is the exact next authorized slice. It should add the human account-management surface and typed backend operations for:

- pending access requests;
- Owner approval/rejection;
- assignment of `ADMIN`, `STAFF`, or `READ_ONLY` within policy;
- disable/reactivate/revoke flows;
- backend escalation prevention, especially ADMIN -> OWNER prohibition;
- minimum security/account events and reusable notification-event contract needed by the slice.

F7.2B must not implement password-change/reset lifecycle, AI Agent Management, global Settings, operational Audit UI, inventory writes, or PostgreSQL canonical promotion.

## High-impact operations

Elevated permission and/or explicit approval is expected for operations such as:

- user/role administration;
- stock adjustments or negative-stock override;
- historical correction/amendment;
- ambiguous identity/mapping approval;
- month close/reopen;
- canonical migration/promotion controls.

Exact route-level permission mapping is implemented only when those operations are introduced.

## Security boundaries

- no database credential is exposed to Telegram, Flutter, GPT, or Sheets;
- no client-side UI state is trusted as authorization;
- credentials/tokens are revocable and rotatable;
- raw session tokens are not stored in the database;
- public API authentication/rate limiting is added as protected endpoints are exposed;
- credential material and production identity exports never enter the public repository;
- historical audit remains after account/credential revocation;
- disabled/PENDING accounts receive no protected inventory access.

## F2 schema relationship and F7.2A evolution

The F2 foundation created:

- `users`;
- `roles` and `user_roles`;
- `external_identities`;
- `service_principals`;
- service credential metadata;
- audit-event actor references.

F7.2A intentionally evolved that same canonical identity foundation rather than replacing it. Alembic `0005_identity` canonicalized username/state metadata, added credential version and one-role-per-user enforcement for the current v1 human RBAC model, and added `user_sessions`.

This identity/session schema does not make PostgreSQL canonical for inventory. The live Google workbook remains operationally authoritative and F6B remains test-only.

## Deferred beyond F7.2A

F7.2B User Management, F7.2C credential lifecycle, F7.2D AI Agent Management, F7.3 operational Audit, OAuth/social login, MFA, password-reset email, SSO, custom role editors, complex departments/teams, biometrics, multi-organization tenancy, and offline-auth synchronization remain deferred until their authorized slices.
