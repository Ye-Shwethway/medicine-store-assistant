# F7.2 — Authentication, RBAC & User Management Design

Status: **F7.2A verified complete; F7.2B User Management is next; F7.2C/F7.2D remain later slices**

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
- `login_name` evolved to username credential metadata without changing `user_id`;
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

Compatibility boundary: the already-deployed Owner PBKDF2 hash was preserved specifically to permit plaintext-free migration. This is not authorization to expand credential lifecycle work. New password-change/reset/hash-upgrade policy belongs to F7.2C.

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

## Backend authorization contract

F7.2A establishes backend authorization helpers as the enforcement boundary.

- authenticated session resolution returns stable `user_id`, username, role, state, and session identity;
- `require_roles(...)` accepts only canonical human roles;
- insufficient authenticated role returns HTTP `403` with `Access denied`;
- missing/invalid/disabled session returns unauthenticated denial rather than a client-side role decision;
- UI visibility is convenience only and never substitutes for backend enforcement.

## F7.2B — User Management — **NEXT**

`User Management` is a standalone human-account surface. It is not combined with Audit or AI Agent Management.

Responsibilities:

- list human users/account status;
- review access requests;
- approve/reject requests;
- assign allowed roles;
- change role within authorized boundaries;
- disable/reactivate accounts;
- inspect basic account/security state.

Credential recovery belongs to F7.2C and must not be implemented as part of the F7.2B minimum runnable slice.

### Access request

1. applicant submits requested username, password, and minimal identity/display information;
2. backend creates `PENDING` account/request;
3. pending account has no private inventory access;
4. Owner sees pending request in product UI;
5. later Telegram/Flutter may mirror the same backend notification;
6. authorized approver chooses allowed role or rejects;
7. approval activates account;
8. approval/rejection/role/status changes become security/account events using only the minimum prerequisite interface needed for this slice.

### Grant boundaries

- `OWNER` can approve `ADMIN`, `STAFF`, `READ_ONLY` accounts;
- `ADMIN` may perform only account operations explicitly delegated by backend policy and can never grant/promote `OWNER`;
- OWNER creation/promotion is separate high-risk flow, not an ordinary dropdown;
- no client-side visibility rule is treated as authorization.

Use product terminology such as **Approve access**, **Assign role**, **Promote**, and **Disable account**.

## F7.2C — Credential lifecycle

- logged-in user can change password after re-authentication;
- forgotten-password recovery does not depend on email in v1;
- user can create reset request;
- Owner-assisted workflow approves/issues a short-lived one-time reset;
- reset token expires and is single-use;
- successful reset invalidates old sessions;
- password change/reset become security/account events.

Verified-email recovery may be added later only if real email infrastructure is deliberately introduced.

## F7.2D companion — AI Agent Management

AI agents are **not** human accounts assigned `OWNER/ADMIN/STAFF/READ_ONLY` roles. They are separately registered `AI_AGENT` principals with capability-based authority.

Only `OWNER` may access `AI Agent Management` and global `Settings`.

Owner may configure an agent's:

- typed capability scope;
- Main Store / selected Sub Store / all-store scope;
- authority ceiling;
- delegated/autonomous policy;
- confirmation policy;
- active/disabled/revoked state;
- availability of shared AI Chat to Staff/Admin users.

For human-delegated AI actions:

`effective_authority = human_authority ∩ agent_capability_scope ∩ location_scope ∩ operation_policy`

Therefore AI Chat never becomes a permission bypass. An Owner may later grant an AI agent explicit typed Main Store operations when those writes are separately authorized, while the agent still cannot self-escalate, change Agent Management, alter Owner/security settings, or change global Settings.

## Role-aware dashboard behavior

### OWNER

- full ordinary navigation visibility;
- User Management visible;
- AI Agent Management visible only when F7.2D is implemented;
- global Settings visible only when its authorized slice is implemented;
- later high-risk/canonical actions remain separately gated and are not authorized by F7.2 alone.

### ADMIN

- operational/admin surfaces allowed by backend policy;
- User Management only where a narrow delegated account-management policy allows it;
- no Owner escalation;
- no AI Agent Management;
- no global Settings;
- no canonical promotion authority unless separately authorized later.

### STAFF

- inventory and approved routine operational surfaces;
- AI Chat may be visible only if Owner enables it in its later slice;
- AI Chat remains bounded by Staff role/location authority;
- no User Management, Agent Management, global Settings, migration promotion, or privileged historical correction.

### READ_ONLY

- read surfaces only;
- AI Chat may only be exposed if later Owner policy allows read-only assistant use;
- no write/edit/save/approve controls;
- management screens return explicit access-denied state.

## Access denied

Use a first-class `403 / Access denied` state that:

- states signed-in user lacks permission;
- may identify current role without exposing internal policy detail;
- provides a safe return to Overview;
- does not suggest credential retry for authenticated-but-unauthorized users.

The backend 403 behavior is verified in F7.2A. A polished visual Access Denied management-screen state may be added with the relevant UI slice without changing the backend contract.

## Surface separation

- `User Management` — human accounts, roles, status; credential recovery is F7.2C.
- `AI Agent Management` — Owner-only agent capabilities/delegation/control plane, later F7.2D.
- `Settings` — Owner-only global policy in later authorized slices.
- `Audit` — store/database operational history, not account/agent management.

Security/account/control-plane events may be retained in backend security history while the primary `Audit` product surface remains operational/store focused.

## Telegram and future clients

Web, Telegram, Flutter, ChatGPT, and Custom GPT attach actions to canonical backend human/agent identities rather than creating separate user stores.

Future Telegram approval controls remain clients of backend approval operations; backend identity/state/authorization is authoritative.

## F7.2 acceptance criteria

### F7.2A — complete

1. canonical stable `user_id` model exists — pass;
2. Owner uses username + password through canonical account model — pass;
3. human role authorization is backend-enforced — pass;
4. explicit authenticated 403 behavior is verified — pass;
5. user-bound revocable session exists — pass;
6. disabled users lose protected access — pass;
7. bootstrap bridge is no longer the normal password-only login path — pass;
8. no inventory write authority was introduced — pass.

### Remaining F7.2 human-account work

F7.2B must verify User Management and access-request/approval/escalation boundaries. F7.2C must separately verify change-password/reset lifecycle and related session revocation. F7.2D remains a subsequent companion slice and must not be conflated with human-account implementation.

## Safety boundary

F7.2 does **not** authorize inventory writes, Google Sheet mutation, PostgreSQL canonical promotion, Telegram/Flutter inventory writes, Custom GPT write Actions, arbitrary SQL, or arbitrary permission editing.
