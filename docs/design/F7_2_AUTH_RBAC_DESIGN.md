# F7.2 — Authentication, RBAC & User Management Design

Status: **authorized design slice; canonical planning updated before implementation**

## Goal

Replace the temporary Owner-only password bridge with a durable multi-user authentication and role model while preserving the locked Dashboard v2.4 visual system and the read-only data-authority boundary.

F7.2 answers two questions only:

1. **Who is this user?**
2. **What is this user allowed to access?**

Inventory write authority remains deferred to later slices.

## Canonical role model

Use the locked v1 roles from F2:

- `OWNER` — full system authority, user-management authority, high-risk approvals, later canonical promotion/month-close authority.
- `ADMIN` — operational administration and approved inventory management; cannot implicitly become or create an Owner.
- `STAFF` — routine inventory reads and approved normal operational entry once write slices are separately authorized.
- `READ_ONLY` — inventory/history/report reads only.

No arbitrary permission editor in v1. Backend authorization policy is the source of truth.

## F7.2A — Canonical multi-user identity and sessions

Introduce the durable human-account model:

- stable backend `user_id` is the canonical identity;
- username is unique credential metadata and may be changed without changing historical identity;
- password is stored only as a one-way password hash;
- account status includes at least `PENDING`, `ACTIVE`, `DISABLED`;
- role is one of `OWNER`, `ADMIN`, `STAFF`, `READ_ONLY`;
- authenticated sessions resolve to `user_id`, role, account status, and session metadata;
- disabling an account invalidates future authorization and should revoke active sessions;
- historical actors are never deleted merely because an account is disabled.

### Owner bootstrap migration

The current runtime-only bridge:

- `MSA_DASHBOARD_OWNER_PASSWORD_HASH`
- `MSA_DASHBOARD_SESSION_SECRET`

is temporary bootstrap infrastructure, not the final credential store.

F7.2A must migrate the bootstrap Owner into the canonical user model and then move normal Owner login to **username + password**. The password-only bridge may remain only long enough to perform a controlled migration/verification, then should be retired from normal login flow.

## Authentication UX

### Dedicated sign-in page

`/dashboard/login` remains the primary login experience.

Required fields:

- Username
- Password

Rules:

- reuse Dashboard v2.4 visual language;
- inline generic login errors that do not reveal whether a username exists;
- accessible password visibility control if included;
- no social/OAuth login in v1;
- authenticated users visiting `/dashboard/login` redirect to `/dashboard`;
- unauthenticated access to protected pages redirects to `/dashboard/login`;
- session expiry and sign-out return to login;
- passwords, service credentials, and session signing secrets never enter browser storage.

## F7.2B — User Management

`User Management` is a standalone navigation/surface. It is **not combined with Audit**.

Primary responsibilities:

- list users and account status;
- review access requests;
- approve or reject requests;
- assign allowed roles;
- change role within authorized boundaries;
- disable/reactivate accounts;
- inspect basic security/account state;
- initiate or approve credential-recovery workflows.

### Access-request model

Do not expose unrestricted public self-registration that immediately creates an active account.

Instead expose **Request access**:

1. applicant submits requested username, password, and minimal identity/display information;
2. backend creates a `PENDING` account/access request;
3. pending account has no private inventory access;
4. Owner receives an in-product notification in User Management;
5. later Telegram integration may mirror the same pending notification;
6. authorized approver chooses an allowed role or rejects the request;
7. approval activates the account;
8. approval, rejection, role changes, and account-status changes are recorded as security/account events.

### Grant boundaries

- `OWNER` can approve `ADMIN`, `STAFF`, and `READ_ONLY` accounts.
- `ADMIN` may only manage account operations explicitly delegated by backend policy and can never grant or promote to `OWNER`.
- OWNER creation/promotion is a separate high-risk operation and must not be an ordinary role dropdown action.
- No client-side visibility rule is treated as authorization.

User-facing terminology should use **Approve access**, **Assign role**, **Promote**, **Disable account**, etc.; do not use Unix `sudo` terminology in the product UI.

## F7.2C — Credential lifecycle

Initial durable credential lifecycle:

- logged-in user can change their password after re-authentication;
- forgotten-password recovery does not depend on email infrastructure in v1;
- user may create a password-reset request;
- authorized Owner workflow issues or approves a short-lived one-time reset flow;
- reset token is single-use, expires, and is never stored in plaintext after issuance if avoidable;
- successful password reset invalidates old sessions;
- password change/reset events are security/account events.

A verified-email reset flow may be added later only when real email delivery/verification infrastructure is intentionally introduced.

## Role-aware dashboard behavior

### OWNER

- full navigation visibility;
- User Management visible;
- future high-risk/canonical actions remain separately gated and are not authorized by F7.2 alone.

### ADMIN

- operational/admin surfaces appropriate to backend capabilities;
- no Owner escalation;
- no canonical promotion/month-close authority unless separately authorized later.

### STAFF

- inventory and approved routine operational surfaces only;
- no User Management authority unless a later explicit policy adds a narrow capability;
- no privileged historical correction, migration promotion, or system configuration.

### READ_ONLY

- read surfaces only;
- no write/edit/save/approve controls;
- protected management screens return an explicit access-denied state.

## Access-denied state

Use a first-class `403 / Access denied` page/state that:

- states that the signed-in user lacks permission;
- may identify the current role without exposing internal policy detail;
- offers a safe return to Overview;
- never suggests retrying credentials for an authenticated-but-unauthorized user.

## Audit separation

`Audit` and `User Management` are separate product surfaces.

`Audit` is reserved for store/database operational history: inventory movements, corrections/reversals, imports/syncs, typed API operations, actor/client provenance, before/after references where appropriate, operation IDs, timestamps, and outcomes.

User-account administration belongs in `User Management`. Security/account events may be retained in backend security history, but the primary user-facing `Audit` area is not an account-management screen.

## Telegram and future clients

Web, Telegram, Flutter, ChatGPT, and Custom GPT must attach actions to canonical backend identities rather than create separate user stores.

A future Telegram approval message may provide buttons such as Approve / Reject, but Telegram is only a client of the backend approval operation. The backend remains authoritative for identity, role, state, and authorization.

## F7.2 acceptance criteria

F7.2 is complete only when:

1. canonical multi-user `user_id` model exists;
2. Owner uses username + password through the canonical account model;
3. `OWNER / ADMIN / STAFF / READ_ONLY` authorization is backend-enforced;
4. User Management exists as a separate surface;
5. access requests can remain pending and be approved/rejected safely;
6. role and account-status changes obey escalation boundaries;
7. explicit 403 behavior is verified;
8. change-password and initial reset lifecycle are verified;
9. session revocation works for disable/reset cases;
10. the bootstrap Owner bridge is no longer the normal multi-user credential store.

## Safety boundary

F7.2 does **not** authorize inventory writes, Google Sheet mutation, PostgreSQL canonical promotion, Telegram inventory writes, Flutter rollout, Custom GPT write Actions, arbitrary SQL, or arbitrary permission editing.
