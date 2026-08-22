# Medicine Store Assistant — Project Roadmap

Status: **F0/F1/F2/F3/F4/F5/F5.1/F6A/F6C/F7.1 verified complete; F6B remains test-only; F7.2 bootstrap Owner read path verified; F7.2A canonical multi-user identity next; PostgreSQL remains non-canonical**

The live Google workbook/source documents remain operationally authoritative. The current staged F6B snapshot is **test-only** and is **not an accepted migration baseline**. A fresh real migration dataset will be imported later only after the operational workflow and user-facing management UI are ready and explicitly approved.

## Delivery policy

Canonical flow: `test -> pull request -> main -> automatic VPS deploy for relevant runtime changes`.

Normal continuation does not require manual VPS commands, Termux/SSH/tmux, Bamboo/Bamboo Claw, or a manual Actions deploy button. Prefer connected tools, repository automation, the repo-scoped self-hosted runner, and durable browser/admin mechanisms.

Runtime secrets remain only on the VPS. Normal backend deployment must **not** read/import the live workbook.

Deployment status is published to GitHub issue #26 (`MSA deployment status`) so connected tooling can inspect push-triggered deployment success/failure and descend into the run/job logs without requiring the owner to manually inspect Actions.

## Verified foundation

- F0 VPS inspection — verified complete 2026-08-22
- F1 runtime skeleton — verified complete 2026-08-22
- Cloudflare public HTTPS route — verified complete 2026-08-22
- F2 PostgreSQL foundation — verified complete 2026-08-22
- F3 authenticated read-only API — verified complete 2026-08-22
- F4 synthetic ledger foundation — verified complete 2026-08-22
- F5 synthetic CMS catalogue versioning — verified complete 2026-08-22
- F5.1 authenticated catalogue read API — verified complete 2026-08-22
- F6A synthetic shadow migration adapter foundation — verified complete 2026-08-22
- F6B read-only live-workbook test snapshot — verified staging exercise only; not a migration baseline
- F6C authenticated shadow read API — verified complete 2026-08-22
- F7.1 read-only Web Dashboard foundation — verified complete 2026-08-22
- F7.2 bootstrap Owner credential + live read path — verified working through dedicated login, authenticated data view, logout, and post-logout login flow

## Test-only F6B snapshot

Current test dataset remains unchanged:

- batch ID `be13d127-5045-4284-a088-0a0b9b024d76`
- rows **1,646**
- SAFE **1,417**
- REVIEW **222**
- NEW_UNMAPPED **7**
- CONFLICT **0**
- `migration_baseline_accepted=false`
- `database_canonical=false`

This batch is for read-path/UI testing only. It must not drive canonical reconciliation or promotion decisions.

## F7 — Web Dashboard, identity, management, and audit

Canonical dashboard/auth docs:

- `docs/architecture/F7_WEB_DASHBOARD.md`
- `docs/design/UI_UX_PRO_MAX_INTEGRATION.md`
- `docs/design/F7_2_AUTH_RBAC_DESIGN.md`
- `design-system/medicine-store-assistant/MASTER.md`
- `design-system/medicine-store-assistant/pages/dashboard.md`

Dashboard v2.4 remains the locked visual/interaction baseline.

### F7.1 — verified complete

Read-only dashboard foundation, public HTTPS route, private BFF, fail-closed session architecture, test/non-canonical indicators, and read-only interaction baseline are verified.

### F7.2 — Authentication, RBAC & User Management

F7.2 is explicitly broader than bootstrap Owner provisioning.

The temporary runtime Owner password bridge successfully proved the protected public dashboard path, but it is not the final credential store.

#### F7.2A — canonical multi-user identity — **next**

Implement:

- stable backend `user_id`;
- username + password accounts;
- roles `OWNER`, `ADMIN`, `STAFF`, `READ_ONLY`;
- `PENDING`, `ACTIVE`, `DISABLED` account states;
- canonical user-bound sessions;
- migrate the bootstrap Owner into the canonical user model;
- normal Owner login becomes username + password;
- backend-enforced role authorization and explicit 403 state.

#### F7.2B — User Management

`User Management` is a dedicated surface, separate from Audit.

Implement:

- access-request queue rather than immediately active public signup;
- Owner approval/rejection;
- allowed role assignment;
- ADMIN cannot grant/promote OWNER;
- disable/reactivate/revoke behavior;
- in-product pending-request notification;
- future Telegram notification mirrors the same backend request/approval operation.

#### F7.2C — credential lifecycle

Implement:

- change password;
- owner-assisted forgotten-password/reset request in v1;
- short-lived single-use reset flow;
- session revocation after reset/disable;
- security/account event recording.

### F7.3 — Store/database Audit UI

`Audit` is reserved for store/database operational history, not user management.

It should expose appropriate read views over:

- stock/inventory operations;
- receipt/usage/adjustment/reversal history;
- imports and sync activity;
- typed API operation IDs;
- actor/client provenance (Web, Telegram, ChatGPT/Custom GPT, Flutter, system job);
- timestamp, outcome, and relevant before/after references.

Historical transactional records are corrected/reversed rather than destructively deleted where auditability matters.

## F8 — Private Custom GPT read experiment

Only after F7.2 identity/RBAC is stable:

- connect Custom GPT through the typed HTTPS API;
- read-only Actions first;
- revocable scoped service/client credential;
- no arbitrary SQL or DB credentials;
- verify health, stock/lot lookup, and audit/summary reads.

## F9 — Controlled typed write experiment

Only after identity/RBAC + ledger/idempotency/audit foundations are verified:

- authorize one low-risk typed write operation first;
- server-side validation + RBAC;
- idempotency/operation ID;
- atomic transaction;
- audit event;
- committed-state readback;
- no direct SQL from LLM/GPT clients;
- database remains non-canonical.

Preferred client architecture:

`Web / Telegram / ChatGPT / Custom GPT / Flutter -> typed Inventory API -> auth/RBAC -> validation -> idempotency -> DB transaction -> audit -> readback`

## F10 — Dual real-workflow + Sheet sync validation

Run representative live operations through the existing Sheet workflow and backend shadow path, then compare results.

Add the operational sync/mirror contract deliberately; do not let LLM clients write directly to Sheets. Backend owns the typed operation and any Sheet mirror/sync behavior.

No automatic canonical cutover.

## F11 — Canonical promotion

Requires explicit approval plus:

- fresh migration baseline;
- measurable parity acceptance;
- backup + restore proof;
- audit completeness;
- real-workflow validation;
- Sheet mirror rebuild/sync confidence;
- rollback/cutback procedure.

Only after promotion may PostgreSQL become the operational source of truth for the approved operation scope.

## Safety boundary

Do not treat F6B test data as production migration truth. Do not begin production inventory writes, DB promotion, Telegram inventory writes, Flutter rollout, Sheet mirror conversion, or Custom GPT write Actions until the corresponding slice is explicitly authorized.

## Continuity rule

After every significant architecture decision, implementation slice, deployment/migration result, or next-work change, update `ROADMAP.md`, `NEW_CHAT_BOOTSTRAP.md`, `IMPLEMENTATION_PLAN.md`, and relevant canonical docs.
