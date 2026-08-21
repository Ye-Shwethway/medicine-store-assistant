# User Access and Authorization Architecture

Status: **approved v1 foundation — implementation staged by slice**

## Purpose

Medicine Store Assistant will be used by the owner and authorized staff through future Telegram and Flutter clients. User identity, authentication, authorization, service identities, and audit attribution therefore belong in the backend foundation rather than being retrofitted after operational history exists.

This domain remains separate from inventory identity. Products, lots, receipts, usage, catalogue records, and monthly snapshots must not contain Telegram- or Flutter-specific login fields as their identity source.

## Canonical human identity

Use one stable internal `user_id` for each human staff member regardless of client.

Foundation user fields include stable ID, display name, optional login name, status, timestamps, and credential metadata only when required. Users with historical operational records are disabled/revoked rather than hard-deleted.

## External identities

Provider-specific identities live separately from `users`.

For Telegram:

- numeric Telegram user ID is the stable external subject;
- Telegram username/display name is mutable metadata only;
- unknown/unlinked Telegram identities receive no operational access by default.

A user may later link multiple approved identity providers without changing canonical `user_id`.

## Authentication vs authorization

Authentication proves caller identity. Authorization determines allowed operations. The backend API is always the enforcement boundary; client buttons, hidden screens, GPT instructions, or UI state are not authorization controls.

## Approved minimal v1 roles

- `OWNER` — full system authority, user/admin management, high-risk approvals, month-close/canonical-promotion authority.
- `ADMIN` — operational administration and approved inventory management; cannot implicitly become Owner.
- `STAFF` — routine reads and approved day-to-day operational entry; no privileged historical correction, role management, or system configuration.
- `READ_ONLY` — inventory/history/report reads only.

Use a small static permission matrix initially. Do not build an arbitrary enterprise permission editor in v1.

## Flutter authentication baseline

Flutter uses a native MSA account independent of Telegram:

- user-chosen login name;
- password stored only as a modern secure hash, with Argon2id preferred when credential implementation begins;
- short-lived access token plus revocable refresh/session token;
- server-side account status and role checks on protected operations.

Email/phone are optional profile/recovery metadata rather than mandatory v1 identity.

## Service principals

Non-human clients use separate service principals rather than human accounts.

Examples:

- private MSA Custom GPT;
- Google Sheets synchronization service;
- future internal adapters/jobs.

Service credentials are revocable and scoped. Store verifier-safe/hash material where feasible; never plaintext API keys in Git, audit logs, or canonical operational exports.

The private Custom GPT begins with narrow read-only scopes when that integration is implemented; it is not automatically equivalent to `OWNER`.

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

## Access lifecycle

1. Owner/Admin creates or approves a staff account according to policy.
2. Required login/external identities are linked and verified.
3. Role is assigned.
4. Backend authenticates and authorizes every protected request.
5. Access can be disabled/revoked without deleting history.

Self-registration never automatically grants store access in v1.

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
- public API authentication/rate limiting is added as protected endpoints are exposed;
- credential material and production identity exports never enter the public repository;
- historical audit remains after account/credential revocation.

## F2 schema relationship

The approved F2 foundation may create:

- `users`;
- `roles` and `user_roles`;
- `external_identities`;
- `service_principals`;
- service credential metadata;
- audit-event actor references.

This does not require enabling staff login yet. Credential/session endpoints, Telegram onboarding, and Flutter login UI remain later implementation slices.

## Deferred beyond F2

OAuth/social login, MFA, password-reset email, SSO, custom role editors, complex departments/teams, biometrics, multi-organization tenancy, and offline-auth synchronization are explicitly deferred until a concrete requirement justifies them.
