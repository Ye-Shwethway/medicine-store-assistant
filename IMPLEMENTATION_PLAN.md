# Medicine Store Assistant — Implementation Plan

Status: **foundation and read-only dashboard verified; F7.2A canonical multi-user identity is the next implementation slice; production write authority is not yet authorized**

This plan translates the approved architecture into small, reversible implementation slices. It does not replace `ROADMAP.md`; it defines execution order and exit criteria.

## Global rules

- Preserve `skills/medicine-store-assistant/` unchanged as the canonical Git-backed skill source.
- Google Sheets remains operationally authoritative until explicit canonical promotion.
- PostgreSQL deployment alone does not make the database canonical.
- No client receives arbitrary SQL or database credentials.
- LLM/Custom GPT/Telegram/Flutter clients call typed backend operations only.
- Secrets never enter the public repository.
- Every significant slice leaves `NEW_CHAT_BOOTSTRAP.md`, `ROADMAP.md`, `IMPLEMENTATION_PLAN.md`, and relevant canonical docs current.
- Prefer the smallest runnable slice; avoid unnecessary infrastructure.
- Normal continuation uses connected tools + repository automation + self-hosted runner; do not require Termux/SSH/Bamboo/manual Actions from the owner.

## Completed foundation — F0 through F6C

F0, F1, F2, F3, F4, F5, F5.1, F6A, and F6C are verified complete.

F6B is a verified **test-only** live-workbook staging exercise. It is not an accepted migration baseline and must not be promoted.

## F7 — Web Dashboard, identity, management, and audit

### F7.1 — Read-only Web Dashboard — verified complete

Verified public HTTPS dashboard, dedicated Owner login, authenticated test-only data reads, logout flow, and non-canonical/test-data indicators.

### F7.2A — Canonical multi-user identity and sessions — next

Purpose: replace the bootstrap password-only Owner bridge with durable human accounts before any production write capability is considered.

Tasks:

- add canonical human-account schema with stable `user_id`;
- unique mutable username;
- password hash and password metadata;
- role enum/constraint: `OWNER`, `ADMIN`, `STAFF`, `READ_ONLY`;
- status: `PENDING`, `ACTIVE`, `DISABLED`;
- canonical user-bound session model or equivalent revocable session state;
- migrate/bootstrap the existing Owner into the user model without exposing the plaintext password;
- change Owner login to username + password;
- implement backend role authorization helpers;
- explicit `403 / Access denied` UX/state;
- session revocation on disable/security events;
- preserve read-only inventory boundary.

Exit criteria:

- canonical Owner login uses username + password;
- Owner session resolves to stable `user_id` and `OWNER` role;
- role checks are server-side;
- disabled user cannot continue using protected sessions;
- READ_ONLY/STAFF/ADMIN/OWNER policy tests are deterministic;
- no inventory write capability added.

### F7.2B — User Management

Purpose: create durable account provisioning and access approval without unrestricted active self-registration.

Tasks:

- dedicated `User Management` navigation/screen;
- `Request access` flow creates pending request/account only;
- pending account receives no private inventory access;
- Owner sees pending requests in product UI;
- Owner can approve/reject and assign `ADMIN`, `STAFF`, or `READ_ONLY`;
- ADMIN cannot grant or promote `OWNER`;
- Owner creation/promotion uses a separate high-risk flow, not an ordinary dropdown;
- disable/reactivate behavior;
- account/role/status changes recorded as security events;
- define notification event contract so Telegram can later mirror pending approvals without becoming the authorization source.

Exit criteria:

- pending request cannot access inventory;
- Owner approval activates correct role;
- rejection remains denied;
- role escalation boundaries are enforced by backend tests;
- User Management is separate from store Audit.

### F7.2C — Credential lifecycle

Purpose: make credentials maintainable without terminal/VPS intervention.

Tasks:

- authenticated change-password flow with re-authentication;
- forgotten-password reset-request flow;
- Owner-assisted v1 reset approval/issuance;
- short-lived single-use reset token/link;
- revoke old sessions after reset;
- security/account event recording;
- later verified-email recovery only if email delivery infrastructure is deliberately added.

Exit criteria:

- user can change password from browser;
- forgotten password can be recovered through durable product flow;
- reset tokens expire and are one-use;
- old sessions fail after reset.

### F7.3 — Store/database Audit UI

Purpose: provide operational traceability for store/database actions independently of User Management.

Audit covers:

- inventory movements and typed stock operations;
- receipts, usage, adjustments, reversals/corrections;
- imports/migrations/sync jobs;
- operation/idempotency IDs;
- actor `user_id` or service principal;
- client/source such as Web, Telegram, ChatGPT/Custom GPT, Flutter, or system job;
- timestamp, outcome, reason, and relevant before/after references.

Rules:

- do not use Audit as account-management UI;
- do not destructively delete historical ledger/audit records merely to “edit” history;
- use reversal/correction semantics where historical integrity matters.

Exit criteria:

- an authorized read-only audit view can answer who/what/when/source/result for representative synthetic/test operations;
- User Management remains a separate surface.

## F8 — Private Custom GPT read-only Action experiment

Only after F7.2 identity/RBAC is stable.

Tasks:

- version-control `integrations/custom-gpt/openapi.yaml`;
- expose scoped read-only typed API operations;
- use revocable service/client credential or delegated authorization as designed;
- start with health, stock lookup, lot lookup, audit/summary reads;
- no writes in first GPT experiment.

Exit criteria:

- Custom GPT can reliably call allowed read endpoints;
- auth, timeout, and error behavior are verified;
- no DB or Sheet credentials are exposed.

## F9 — Controlled typed write Action experiment

Only after ledger/idempotency/audit + identity/RBAC tests pass.

Purpose: prove one safe end-to-end write before broad inventory mutation is allowed.

First operation should be one low-risk typed domain command, not arbitrary CRUD/SQL.

Required write pipeline:

`Client -> typed Inventory API -> authentication/RBAC -> validation -> idempotency -> atomic DB transaction -> audit event -> committed-state readback -> result`

Requirements:

- operation ID/idempotency key;
- backend validation;
- server-side authorization;
- no arbitrary SQL;
- no direct LLM-to-DB connection;
- no direct LLM-to-Sheet write;
- failure never becomes conversational success;
- PostgreSQL remains non-canonical.

Exit criteria:

- duplicate replay cannot duplicate movement;
- failed operation rolls back;
- successful operation has auditable actor/source/result;
- readback matches committed state.

## F10 — Dual real-workflow and Sheet sync validation

Purpose: prove backend operations against the current operational Sheet truth before cutover.

Tasks:

- run representative real operations through the existing Sheet workflow and backend shadow path;
- compare balances/lots/history;
- define Google Sheet mirror/sync contract behind the backend;
- backend owns sync orchestration; clients never bypass it;
- include retry/idempotency/reconciliation behavior for sync failures;
- produce mismatch reports rather than silent repairs.

Exit criteria:

- representative workflows reconcile measurably;
- sync failure is observable/recoverable;
- no automatic canonical cutover.

## F11 — Canonical promotion

Requires explicit approval.

Before promotion:

- import a fresh real migration baseline;
- verify parity acceptance criteria;
- prove backup + restore;
- verify audit completeness;
- verify realistic read/write workflows;
- verify Sheet mirror/rebuild/reconciliation;
- document rollback/cutback.

Promotion may be operation-scope based rather than all-at-once if explicitly designed and approved.

## Recommended immediate order

1. Complete and verify **F7.2A** canonical multi-user identity.
2. Implement **F7.2B** User Management/access approval.
3. Implement **F7.2C** credential lifecycle.
4. Implement **F7.3** store/database Audit read surface.
5. Stabilize RBAC/audit verification.
6. Begin **F8** Custom GPT read-only integration.
7. Only then authorize **F9** first controlled write experiment.
8. Continue F10 dual-workflow/sync validation before any F11 promotion.
