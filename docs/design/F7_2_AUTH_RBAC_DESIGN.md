# F7.2 — Authentication, RBAC & User Management Design

Status: **authorized design slice; canonical planning aligned before implementation**

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

## F7.2A — Canonical multi-user identity and sessions

Introduce the durable human-account model:

- stable backend `user_id` is canonical human identity;
- username is unique credential metadata and may change without changing historical identity;
- password stored only as a one-way hash;
- account state includes `PENDING`, `ACTIVE`, `DISABLED`;
- role is `OWNER`, `ADMIN`, `STAFF`, or `READ_ONLY`;
- authenticated sessions resolve to `user_id`, role, status, and session metadata;
- disabling an account revokes protected authorization/sessions;
- historical actors are not deleted when accounts are disabled.

### Owner bootstrap migration

Current runtime-only bridge values are temporary bootstrap infrastructure, not the final credential store.

F7.2A migrates the bootstrap Owner into the canonical user model and moves normal Owner login to **username + password**. The password-only bridge remains only long enough for controlled migration/verification and is then retired from normal login.

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

## F7.2B — User Management

`User Management` is a standalone human-account surface. It is not combined with Audit or AI Agent Management.

Responsibilities:

- list human users/account status;
- review access requests;
- approve/reject requests;
- assign allowed roles;
- change role within authorized boundaries;
- disable/reactivate accounts;
- inspect basic account/security state;
- initiate/approve credential recovery.

### Access request

1. applicant submits requested username, password, and minimal identity/display information;
2. backend creates `PENDING` account/request;
3. pending account has no private inventory access;
4. Owner sees pending request in product UI;
5. later Telegram/Flutter may mirror the same backend notification;
6. authorized approver chooses allowed role or rejects;
7. approval activates account;
8. approval/rejection/role/status changes become security/account events.

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
- AI Agent Management visible;
- global Settings visible;
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
- AI Chat may be visible only if Owner enables it;
- AI Chat remains bounded by Staff role/location authority;
- no User Management, Agent Management, global Settings, migration promotion, or privileged historical correction.

### READ_ONLY

- read surfaces only;
- AI Chat may only be exposed if Owner policy allows read-only assistant use;
- no write/edit/save/approve controls;
- management screens return explicit access-denied state.

## Access denied

Use a first-class `403 / Access denied` state that:

- states signed-in user lacks permission;
- may identify current role without exposing internal policy detail;
- provides a safe return to Overview;
- does not suggest credential retry for authenticated-but-unauthorized users.

## Surface separation

- `User Management` — human accounts, roles, status, credential recovery.
- `AI Agent Management` — Owner-only agent capabilities/delegation/control plane.
- `Settings` — Owner-only global policy, including later reorder/store/agent policy.
- `Audit` — store/database operational history, not account/agent management.

Security/account/control-plane events may be retained in backend security history while the primary `Audit` product surface remains operational/store focused.

## Telegram and future clients

Web, Telegram, Flutter, ChatGPT, and Custom GPT attach actions to canonical backend human/agent identities rather than creating separate user stores.

Future Telegram approval controls remain clients of backend approval operations; backend identity/state/authorization is authoritative.

## F7.2 acceptance criteria

F7.2A/B/C human-account work is complete only when:

1. canonical `user_id` model exists;
2. Owner uses username + password through canonical account model;
3. human role authorization is backend-enforced;
4. User Management is separate;
5. access requests remain pending until approved/rejected;
6. role/status changes obey escalation boundaries;
7. explicit 403 behavior is verified;
8. change-password/reset lifecycle is verified;
9. session revocation works;
10. bootstrap bridge is no longer normal credential store.

F7.2D is a subsequent companion slice and must not be conflated with the human-account implementation.

## Safety boundary

F7.2 does **not** authorize inventory writes, Google Sheet mutation, PostgreSQL canonical promotion, Telegram/Flutter inventory writes, Custom GPT write Actions, arbitrary SQL, or arbitrary permission editing.
