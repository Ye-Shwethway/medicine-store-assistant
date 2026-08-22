# F7.2 — Authentication & Role-Based Access Design

Status: **authorized design slice; implementation not yet promoted**

## Goal

Extend the locked Dashboard v2.4 experience with a dedicated sign-in experience and role-aware access without redesigning the existing Medicine Store Assistant dashboard.

This slice preserves the current clinical/operations visual system and read-only data authority boundary while replacing the temporary owner-only modal concept with a durable user/account model aligned to the approved F2 identity decisions.

## Canonical role model

Use the locked v1 roles from F2:

- `OWNER` — full system authority, user/admin management, high-risk approvals, canonical promotion/month-close authority.
- `ADMIN` — operational administration and approved inventory management; cannot implicitly become Owner.
- `STAFF` — routine inventory reads and approved normal operational entry; no privileged historical correction, role management, or system configuration.
- `READ_ONLY` — inventory/history/report reads only.

No arbitrary permission editor in v1. Backend policy remains the source of truth for authorization.

## Authentication UX

### Dedicated sign-in page

Add a dedicated `/dashboard/login` experience rather than relying on an in-dashboard modal as the primary entry path.

Visual rules:

- reuse Dashboard v2.4 typography, spacing, controls, surface treatment, light/dark tokens, and clinical/operations tone;
- Medicine Store Assistant identity is prominent but restrained;
- no marketing content or decorative complexity;
- username and password fields are explicit and accessible;
- password visibility toggle is optional but must be keyboard/touch accessible;
- primary action is `Sign in`;
- login errors remain inline next to the form and never reveal whether a username exists;
- no public `Sign up` action;
- no social/OAuth login in v1;
- no password-reset email workflow in this slice;
- if authentication is not provisioned, show a clear unavailable/configuration state rather than a broken form.

### Session behavior

- unauthenticated navigation to protected dashboard pages redirects to `/dashboard/login`;
- successful sign-in returns the user to the intended dashboard view when safe;
- authenticated users visiting `/dashboard/login` redirect to `/dashboard`;
- sign out clears only the browser session and returns to the sign-in page;
- session expiry returns to sign-in without exposing private data;
- never store passwords, F3 Bearer credentials, or session signing secrets in browser storage.

## Role-aware dashboard behavior

The interface may hide or disable controls the current role cannot use, but backend authorization is mandatory for every protected operation.

### OWNER

- full navigation visibility;
- `Audit & Access` includes user/access management entry points once implemented;
- future high-risk/canonical actions remain separately gated and are not authorized by this design slice alone.

### ADMIN

- operational/admin navigation appropriate to current backend capabilities;
- user-role escalation to OWNER is never available;
- no canonical promotion/month-close authority unless separately authorized by backend policy.

### STAFF

- inventory and approved routine operational surfaces only;
- no user management, system configuration, privileged historical correction, or migration promotion UI.

### READ_ONLY

- read surfaces only;
- no write/edit/save/approve controls;
- protected admin/access screens are hidden or replaced with an explicit access-denied state.

## Access-denied state

Use a first-class `403 / Access denied` page/state that:

- states the user lacks permission for the requested area;
- identifies the current signed-in role without exposing internal policy detail;
- offers a safe return to Overview;
- never suggests retrying credentials for a valid authenticated-but-unauthorized user.

## Account management direction

`Audit & Access` becomes the future role-aware account surface.

For v1:

- accounts are created/provisioned by authorized Owner/Admin workflow only;
- public self-registration is prohibited;
- canonical identity is stable backend `user_id`;
- login name is mutable credential metadata, not historical identity;
- disable/revoke accounts rather than delete users with audit history;
- role changes and account status changes must be audited;
- future Telegram identity linkage and Flutter authentication attach to canonical user identity rather than creating separate user records.

## Credential/runtime bootstrap boundary

The existing owner-only runtime values remain valid as a temporary bootstrap bridge for the first authenticated deployment verification:

- `MSA_DASHBOARD_OWNER_PASSWORD_HASH`
- `MSA_DASHBOARD_SESSION_SECRET`

They are not the final multi-user credential store. The first bootstrap Owner session may be used to prove the protected dashboard path while the canonical `users` / roles / sessions implementation is added in a later implementation step.

Do not put either runtime value, the plaintext Owner password, or generated session material in Git, browser code, CI logs, or documentation evidence.

## F7.2 design acceptance criteria

The design slice is complete when canonical docs cover:

1. dedicated sign-in page;
2. no public signup;
3. OWNER / ADMIN / STAFF / READ_ONLY roles;
4. role-aware navigation and control visibility;
5. explicit access-denied state;
6. session expiry/sign-out behavior;
7. bootstrap-owner runtime secret boundary;
8. backend-enforced authorization requirement;
9. continuity docs identify F7.2 as authentication/RBAC rather than owner-password provisioning only.

## Safety boundary

This design does not authorize inventory writes, Google Sheet mutation, database canonical promotion, Telegram/Flutter rollout, Custom GPT write Actions, or arbitrary role/permission editing.
