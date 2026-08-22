# F7.2 — Authentication, RBAC & User Management Design

Status: **F7.2A, F7.2B, and F7.2C verified complete; F7.2D AI Agent Management is next**

## Goal

Replace the temporary Owner-only password bridge with durable multi-user authentication and role-based access while preserving the locked Dashboard v2.4 visual system and the current read-only inventory boundary.

F7.2A/B/C answer human identity, account-management, and credential-lifecycle questions. AI/service principals are handled by the companion F7.2D design:

`docs/architecture/F7_2D_AI_AGENT_MANAGEMENT.md`

Inventory write authority remains deferred to later slices.

## Canonical human role model

- `OWNER` — full human system authority, User Management authority, AI Agent Management authority, global Settings authority, high-risk approvals, and later canonical-promotion authority.
- `ADMIN` — operational administration and approved inventory management according to backend policy; cannot implicitly become/create an Owner and cannot administer AI-agent/global security policy.
- `STAFF` — routine reads and approved normal operational workflows once later write slices are authorized.
- `READ_ONLY` — inventory/history/report reads only.

No arbitrary human permission editor in v1. Backend authorization policy is authoritative.

## F7.2A — Canonical multi-user identity and sessions — **VERIFIED COMPLETE**

The deployed implementation reuses and evolves the existing F2 human-identity foundation rather than creating a parallel user store:

- `users.user_id` UUID remains stable canonical human identity;
- existing `roles` and `user_roles` carry `OWNER`, `ADMIN`, `STAFF`, `READ_ONLY`;
- current v1 policy enforces one role per canonical human user;
- username credential metadata does not change stable `user_id`;
- account state is canonicalized as `PENDING`, `ACTIVE`, `DISABLED`;
- password is stored only as a one-way hash;
- `credential_version` supports session invalidation boundaries;
- durable `user_sessions` bind an opaque browser token to `user_id` through a server-side keyed token digest, expiry, revocation state, credential version, and last-seen metadata;
- every protected session resolution re-checks current user state and role;
- disabling an account immediately blocks protected access even when an issued browser token still exists;
- historical actors are not deleted merely because access is disabled.

### Owner bootstrap migration — verified

The former runtime-only password bridge has been superseded for normal login.

F7.2A materialized the existing Owner password hash into the canonical F2 `users` model and assigned the canonical `OWNER` role without exposing plaintext credentials. Normal Owner sign-in is username + password. The initial deployed bootstrap username was `owner`.

F7.2C supersedes the assumption that `owner` is a permanent product identity: username is now a mutable credential/display label while stable `user_id` and `OWNER` role remain authoritative. The Owner can replace `owner` through the signed-in Account page after current-password re-authentication.

Verified implementation evidence:

- PR #36;
- merge `c3aa75d65e0bc6d1836227fe8450b0b3de5b2651`;
- deploy run `32586385336`, job `97063270146` — success;
- Alembic migration `0004_shadow -> 0005_identity` — pass;
- canonical Owner bootstrap — pass;
- username/password auth — pass;
- durable revocable session — pass;
- Owner RBAC — pass;
- authenticated 403 / `Access denied` — pass;
- disabled-user denial — pass;
- inventory authority flags unchanged.

## Authentication UX

`/dashboard/login` remains the primary sign-in page.

Required fields:

- Username
- Password

Rules:

- reuse Dashboard v2.4 language;
- generic login errors do not reveal whether username exists;
- accessible password visibility control if included;
- no social/OAuth login in v1;
- authenticated users visiting login redirect to dashboard;
- unauthenticated protected routes redirect to login;
- session expiry/sign-out return to login;
- passwords, service credentials, and signing secrets never enter browser storage.

F7.2B adds a progressively disclosed `Request access` flow. Submitting it creates only a pending canonical account/request; it does not grant private inventory access.

F7.2C adds `Forgot password?` with an enumeration-safe acknowledgement and a one-time reset-completion surface activated by an Owner-issued `#reset=<token>` link.

## Backend authorization contract

- authenticated session resolution returns stable `user_id`, username, role, state, and session identity;
- `require_roles(...)` accepts only canonical human roles;
- insufficient authenticated role returns HTTP `403` with `Access denied`;
- missing/invalid/disabled session returns unauthenticated denial rather than a client-side role decision;
- UI visibility is convenience only and never substitutes for backend enforcement.

## F7.2B — User Management — **VERIFIED COMPLETE**

Deployed via PR #38, merge `e4671c75ab2ece2a6f5065a78779413ef3e9f38b`, deploy run `32588170791`, job `97067607202`.

Alembic upgraded `0005_identity -> 0006_user_management`.

`User Management` is a standalone human-account surface. It is not combined with operational Audit or AI Agent Management.

### Request-access lifecycle

1. applicant submits display name, requested username, and password;
2. password is stored only as a one-way hash;
3. backend creates a canonical `PENDING` account and pending access request;
4. pending account receives no role/private inventory access and cannot authenticate to protected inventory;
5. Owner sees the pending request in User Management;
6. Owner may assign `ADMIN`, `STAFF`, or `READ_ONLY`, or reject;
7. approval activates the account with the exact assigned role;
8. request/approval/rejection and later role/state/session changes create account-security events;
9. reusable notification events are generated independently of delivery channel.

The public request response is designed not to reveal whether a username already exists.

### Deployed management operations

Owner-only F7.2B supports:

- list human users/account state;
- review pending requests;
- approve/reject;
- assign/change allowed non-Owner roles;
- disable/reactivate approved non-Owner accounts;
- revoke sessions;
- inspect basic active-session state.

F7.2C adds Owner review/issuance of password-reset requests inside the same User Management product area without turning credential recovery into an ordinary role mutation.

Current User Management does not delegate to ADMIN. Future ADMIN delegation, if desired, must be explicitly designed and can never grant/promote OWNER.

### Grant/escalation boundaries

- ordinary assignable roles are `ADMIN`, `STAFF`, `READ_ONLY`;
- `OWNER` is not an ordinary dropdown role;
- ordinary User Management refuses mutation of an existing OWNER account;
- OWNER creation/promotion remains a separate future high-risk flow;
- backend enforcement is authoritative.

### Session/state behavior

- role change revokes the target user's existing sessions;
- disable removes protected access;
- approved disabled users can be reactivated;
- explicit session revocation is available;
- stable `user_id` survives role/state changes;
- rejected users remain non-authenticating.

### Account/security history vs operational Audit

F7.2B/F7.2C maintain minimum durable `account_security_events` and reusable `notification_events` required for human-account administration and credential recovery. These do **not** replace or implement the later F7.3 actor-aware operational/store Audit ledger.

## Signed-in drawer profile — **VERIFIED F7.2B**

Dashboard v2.4 shows a signed-in identity box below product branding and above primary navigation in the sidebar/drawer.

Required/deployed representation:

- circular profile avatar area;
- deterministic initials fallback while no managed profile image exists;
- current canonical username as primary identity label;
- current role as secondary metadata;
- safe truncation/responsive drawer behavior;
- identity sourced from authenticated backend session, not a browser-side profile store.

The profile card remains informational. Profile-image upload/change is deferred until separately authorized.

Username itself is managed through F7.2C `Account`, not by editing the drawer card. After username change and re-login, the profile card reflects the new canonical username.

Web UI implementation follows the pinned UI/UX Pro Max skill and the existing MSA `MASTER.md` / Dashboard v2.4 design system: semantic surfaces, keyboard/focus affordances, responsive behavior, readable textual state, and no color-only meaning.

## Role-aware dashboard behavior

### OWNER

- full ordinary navigation visibility;
- User Management visible;
- Account credential management visible;
- AI Agent Management visible only when F7.2D is implemented;
- global Settings visible only when its authorized slice is implemented;
- later high-risk/canonical actions remain separately gated.

### ADMIN

- operational/admin surfaces allowed by backend policy;
- Account credential management visible for own username/password;
- no current User Management access;
- no Owner escalation;
- no AI Agent Management/global Settings.

### STAFF

- inventory and approved routine operational surfaces;
- Account credential management visible for own username/password;
- no User Management, Agent Management, global Settings, migration promotion, or privileged historical correction.

### READ_ONLY

- read surfaces only for inventory/business data;
- Account credential management remains available for the user's own sign-in credential;
- no inventory write/edit/save/approve controls;
- management routes return access-denied behavior.

## Access denied

Use a first-class `403 / Access denied` state that:

- states signed-in user lacks permission;
- may identify current role without exposing internal policy detail;
- provides a safe return to Overview;
- does not suggest credential retry for authenticated-but-unauthorized users.

Backend 403 and the User Management visual denied state are verified.

## F7.2C — Credential lifecycle — **VERIFIED COMPLETE**

Deployed via PR #40, merge `a910658efc3cbc214b30a1f5ed946fdd34ffe4a2`, deploy run `32589571152`, job `97071112514`.

Alembic upgraded `0006_user_management -> 0007_credential_lifecycle`.

### Self-service username change

- available to every active signed-in human role through `Account`;
- requires current-password re-authentication;
- enforces the existing 3–64 character username format and case-insensitive uniqueness;
- changes username only, not stable `user_id`, role, or state;
- increments credential version and revokes prior sessions;
- records `USERNAME_CHANGED` account-security event;
- requires sign-in again with the new username;
- initial bootstrap username `owner` is therefore not a permanent visible identity requirement.

### Self-service password change

- requires current-password re-authentication;
- validates the new password and rejects reusing the current password;
- stores only a one-way hash;
- increments credential version and revokes prior sessions;
- cancels outstanding reset requests/tokens;
- records `PASSWORD_CHANGED` account-security event;
- requires sign-in again with the new password.

### Forgotten-password / Owner-assisted reset

- public request accepts username but returns the same generic accepted response for unknown and eligible users;
- a durable pending reset grants no access;
- eligible reset requests are Owner-reviewable in User Management;
- only Owner may issue a cryptographically random short-lived one-time reset;
- reset lifetime defaults to 30 minutes with bounded runtime configuration;
- persistent storage contains only a keyed reset-token digest/verifier;
- plaintext token is returned only at issuance;
- link uses `/dashboard/login#reset=<token>` so plaintext token is not transmitted in ordinary HTTP request URLs;
- completion checks issued state, expiry, active target state, token verifier, and new-password policy;
- success increments credential version, revokes sessions, consumes the reset, removes verifier material, and records `PASSWORD_RESET_COMPLETED`;
- request/issuance also create reusable notification events.

### Verified acceptance

- username current-password re-authentication — pass;
- username change / old-session revoke / old-username denial / new-username login — pass;
- password current-password re-authentication — pass;
- password change / old-session revoke / old-password denial / new-password login — pass;
- enumeration-safe reset request — pass;
- non-Owner reset-list 403 — pass;
- Owner reset review/issuance — pass;
- digest-only token persistence — pass;
- reset single use — pass;
- reset session revoke — pass;
- credential/security events — pass;
- reset notifications — pass;
- Account/Forgot/Owner-reset UI contract — pass;
- inventory authority flags and read-only boundary — unchanged.

Verified-email recovery may be added later only if real email infrastructure is deliberately introduced.

Profile-image upload/edit remains outside F7.2C and separately deferred.

## F7.2D companion — AI Agent Management — **NEXT**

AI agents are **not** human accounts assigned `OWNER/ADMIN/STAFF/READ_ONLY` roles. They are separately registered `AI_AGENT` principals with capability-based authority.

Only `OWNER` may access `AI Agent Management` and global `Settings`.

For human-delegated AI actions:

`effective_authority = human_authority ∩ agent_capability_scope ∩ location_scope ∩ operation_policy`

AI Chat never becomes a permission bypass. An Owner may later grant an AI agent explicit typed Main Store/Sub Store operations only when those writes are separately authorized. An agent cannot self-escalate or change security/control-plane policy.

## Surface separation

- `User Management` — human accounts, roles, state, session administration, and Owner-assisted reset review.
- `Account` — self-service F7.2C username/password maintenance.
- credential recovery — public forgot request plus Owner-issued reset link.
- `AI Agent Management` — Owner-only F7.2D control plane.
- `Settings` — Owner-only global policy in later authorized slices.
- `Audit` — F7.3 store/database operational history, not account/agent management.

## F7.2 acceptance state

### F7.2A — complete

1. canonical stable `user_id` — pass;
2. Owner username + password — pass;
3. backend human role authorization — pass;
4. explicit authenticated 403 — pass;
5. durable revocable session — pass;
6. disabled-user denial — pass;
7. bootstrap password-only normal login retired — pass;
8. no inventory write authority — pass.

### F7.2B — complete

1. pending request remains non-authenticating — pass;
2. Owner lists/reviews pending requests — pass;
3. approval/rejection — pass;
4. exact role assignment — pass;
5. non-Owner User Management 403 — pass;
6. ordinary OWNER-account escalation/mutation guard — pass;
7. role-change session revocation — pass;
8. disable/reactivate — pass;
9. explicit session revocation — pass;
10. account-security + notification events — pass;
11. signed-in drawer profile UI — pass;
12. User Management separate from operational Audit — pass;
13. no inventory mutation — pass.

### F7.2C — complete

1. authenticated username change with current-password re-authentication — pass;
2. username change preserves stable identity/role/state and revokes old sessions — pass;
3. authenticated password change with current-password re-authentication — pass;
4. forgotten-password request is enumeration-safe — pass;
5. Owner-assisted reset issuance — pass;
6. digest-only persistent reset verifier — pass;
7. reset expiry/one-use contract — pass;
8. credential/session invalidation after change/reset — pass;
9. account-security + notification events — pass;
10. product UI requires no VPS/terminal intervention — pass;
11. no inventory mutation — pass.

Human identity/User Management/credential lifecycle are now verified. F7.2D is the next separate companion slice and must not be conflated with human-account implementation.

## Safety boundary

F7.2 does **not** authorize inventory writes, Google Sheet mutation, PostgreSQL canonical promotion, Telegram/Flutter inventory writes, Custom GPT write Actions, arbitrary SQL, AI self-escalation, or arbitrary permission editing.