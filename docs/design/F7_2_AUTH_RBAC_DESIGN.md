# F7.2 — Authentication, RBAC & User Management Design

Status: **F7.2A and F7.2B verified complete; F7.2C Credential Lifecycle is next; F7.2D remains later**

## Goal

Replace the temporary Owner-only password bridge with durable multi-user authentication and role-based access while preserving the locked Dashboard v2.4 visual system and the current read-only inventory boundary.

F7.2A/B/C answers human identity and account-management questions. AI/service principals are handled by the companion F7.2D design:

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

F7.2A materialized the existing Owner password hash into the canonical F2 `users` model and assigned the canonical `OWNER` role without exposing plaintext credentials. Normal Owner sign-in is now **username + password**; the deployed bootstrap username is `owner` unless explicitly overridden by protected runtime configuration.

Compatibility boundary: the already-deployed Owner PBKDF2 hash was preserved specifically to permit plaintext-free migration. New password-change/reset/hash-upgrade policy belongs to F7.2C.

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

Current F7.2B does not delegate User Management to ADMIN. Future ADMIN delegation, if desired, must be explicitly designed and can never grant/promote OWNER.

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

F7.2B introduces minimum durable `account_security_events` and reusable `notification_events` required for human-account administration. These do **not** replace or implement the later F7.3 actor-aware operational/store Audit ledger.

## Signed-in drawer profile — **VERIFIED F7.2B**

Dashboard v2.4 now shows a signed-in identity box below product branding and above primary navigation in the sidebar/drawer.

Required/deployed representation:

- circular profile avatar area;
- deterministic initials fallback while no managed profile image exists;
- canonical username as primary identity label;
- current role as secondary metadata;
- safe truncation/responsive drawer behavior;
- identity sourced from authenticated backend session, not a browser-side profile store.

The F7.2B profile card is informational. Actual profile-image upload/change is deferred until separately authorized and must not be silently mixed into F7.2C.

Web UI implementation follows the pinned UI/UX Pro Max skill and the existing MSA `MASTER.md` / Dashboard v2.4 design system: semantic surfaces, keyboard/focus affordances, responsive behavior, readable textual state, and no color-only meaning.

## Role-aware dashboard behavior

### OWNER

- full ordinary navigation visibility;
- User Management visible;
- AI Agent Management visible only when F7.2D is implemented;
- global Settings visible only when its authorized slice is implemented;
- later high-risk/canonical actions remain separately gated.

### ADMIN

- operational/admin surfaces allowed by backend policy;
- no current F7.2B User Management access;
- no Owner escalation;
- no AI Agent Management/global Settings.

### STAFF

- inventory and approved routine operational surfaces;
- no User Management, Agent Management, global Settings, migration promotion, or privileged historical correction.

### READ_ONLY

- read surfaces only;
- no write/edit/save/approve controls;
- management routes return access-denied behavior.

## Access denied

Use a first-class `403 / Access denied` state that:

- states signed-in user lacks permission;
- may identify current role without exposing internal policy detail;
- provides a safe return to Overview;
- does not suggest credential retry for authenticated-but-unauthorized users.

Backend 403 and the User Management visual denied state are verified.

## F7.2C — Credential lifecycle — **NEXT**

- logged-in user changes password only after current-password re-authentication;
- forgotten-password request must not reveal whether username exists;
- reset request grants no access;
- Owner-assisted workflow approves/issues a cryptographically random short-lived one-time reset;
- store only reset-token digest/verifier material after issuance boundary;
- reset token expires and is single-use;
- successful password change/reset increments credential version and invalidates old sessions;
- password change/reset become account-security events;
- reusable notification events support Owner review/delivery;
- normal credential maintenance is accessible through product UI without VPS/terminal intervention.

Verified-email recovery may be added later only if real email infrastructure is deliberately introduced.

Profile-image upload/edit remains outside F7.2C unless separately authorized.

## F7.2D companion — AI Agent Management

AI agents are **not** human accounts assigned `OWNER/ADMIN/STAFF/READ_ONLY` roles. They are separately registered `AI_AGENT` principals with capability-based authority.

Only `OWNER` may access `AI Agent Management` and global `Settings`.

For human-delegated AI actions:

`effective_authority = human_authority ∩ agent_capability_scope ∩ location_scope ∩ operation_policy`

AI Chat never becomes a permission bypass. An Owner may later grant an AI agent explicit typed Main Store/Sub Store operations only when those writes are separately authorized. An agent cannot self-escalate or change security/control-plane policy.

## Surface separation

- `User Management` — human accounts, roles, state, session administration.
- credential lifecycle — F7.2C password/change/reset workflow.
- `AI Agent Management` — later Owner-only F7.2D control plane.
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

### Remaining human-account work

F7.2C must separately verify change-password/reset lifecycle, token expiry/single use, and credential/session invalidation. F7.2D remains a subsequent companion slice and must not be conflated with human-account implementation.

## Safety boundary

F7.2 does **not** authorize inventory writes, Google Sheet mutation, PostgreSQL canonical promotion, Telegram/Flutter inventory writes, Custom GPT write Actions, arbitrary SQL, AI self-escalation, or arbitrary permission editing.
