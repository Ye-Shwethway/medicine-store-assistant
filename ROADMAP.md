# Medicine Store Assistant — Project Roadmap

Status: **F0/F1/F2/F3/F4/F5/F5.1/F6A/F6C/F7.1 verified complete; F6B remains test-only; F7.2 bootstrap Owner read path verified; F7.2A canonical multi-user identity next; PostgreSQL remains non-canonical**

The live Google workbook/source documents remain operationally authoritative. The current staged F6B snapshot is **test-only** and is **not an accepted migration baseline**. A fresh real migration dataset will be imported later only after the operational workflow and user-facing management UI are ready and explicitly approved.

## Delivery policy

Canonical flow: `test -> pull request -> main -> automatic VPS deploy for relevant runtime changes`.

Normal continuation does not require manual VPS commands, Termux/SSH/tmux, Bamboo/Bamboo Claw, or a manual Actions deploy button. Prefer connected tools, repository automation, the repo-scoped self-hosted runner, and durable browser/admin mechanisms.

Runtime secrets remain only on the VPS. Normal backend deployment must **not** read/import the live workbook.

Deployment status is published to GitHub issue #26 (`MSA deployment status`) so connected tooling can inspect push-triggered deployment success/failure and descend into run/job logs without requiring the owner to manually inspect Actions.

## Product direction

Medicine Store Assistant is not intended to become only a database-backed spreadsheet replacement. The target product is a multi-client intelligent operations system in which human users, AI agents, integrations, and system jobs collaborate through the same typed backend while preserving clear identity, authorization, auditability, deterministic analytics, and database-grounded AI behavior.

Primary future clients:

- Web dashboard;
- Telegram;
- Flutter;
- internal MSA AI Assistant;
- Custom GPT / ChatGPT integrations;
- scheduled/system jobs.

No client or AI agent receives arbitrary SQL or raw database credentials.

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

## F7 — Web application foundation, identity, audit, and intelligence

Canonical docs include:

- `docs/architecture/F7_WEB_DASHBOARD.md`
- `docs/design/UI_UX_PRO_MAX_INTEGRATION.md`
- `docs/design/F7_2_AUTH_RBAC_DESIGN.md`
- `docs/architecture/F7_3_ACTOR_AUDIT_AND_OPERATION_LEDGER.md`
- `docs/architecture/F7_4_F7_6_INTELLIGENCE_ARCHITECTURE.md`
- `design-system/medicine-store-assistant/MASTER.md`
- `design-system/medicine-store-assistant/pages/dashboard.md`

Dashboard v2.4 remains the locked visual/interaction baseline while new product surfaces are added consistently.

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

### F7.3 — Actor-aware Store/Database Audit & Operation Ledger

`Audit` is reserved for store/database operational history, not user management.

Because humans and AI agents will work together, every meaningful operation must identify both the actor and the client/source. The system must be able to distinguish a human action from an AI-assisted action, autonomous system action, integration action, or scheduled job.

Canonical actor types:

- `HUMAN`
- `AI_AGENT`
- `SYSTEM`
- `INTEGRATION`

Representative provenance:

- stable `operation_id` and idempotency key where applicable;
- `actor_type` and `actor_id`;
- `authorized_by_user_id` when an AI/service actor acts under a human user's authority;
- client/source such as Web, Telegram, Flutter, Custom GPT, internal AI, or system job;
- typed action type;
- timestamp/outcome;
- affected-record references;
- before/after or ledger movement references where appropriate;
- reversal/correction links;
- sync/mirror result references.

Historical transactional records are corrected/reversed rather than destructively deleted where auditability matters.

Before broad AI/multi-client writes are allowed, the Audit foundation must answer: what happened, who/what initiated it, under whose authority, through which client, what changed, and whether it succeeded/failed/reversed.

### F7.4 — Smart Analysis Foundation

Build a read-only deterministic analytics layer plus professional dashboard visualizations.

Initial v1 modules:

1. Stock Health
2. Usage Trends
3. Expiry Risk
4. Reorder Outlook
5. Price Movement
6. Data Quality

Principles:

- SQL/domain formulas/business rules produce reproducible facts;
- charts/KPIs support date/category/item drill-down;
- supporting rows/lots/operations remain inspectable;
- Smart Analysis remains useful even when an AI provider is unavailable;
- no opaque AI-generated metric is treated as database truth.

### F7.5 — Internal AI Assistant

Add a first-party, read-only conversational analysis workspace grounded in authorized backend analytics/tools.

The AI Assistant may explain trends, compare periods, generate chart/table views, identify risk candidates, and drill into supporting facts, but it may not invent database values or receive arbitrary SQL access.

The internal assistant is an identifiable `AI_AGENT` service principal and participates in the same actor/audit model.

Initial tool direction includes typed reads such as stock health, usage trends, expiry risk, reorder candidates, price movement, data-quality issues, and audit summaries.

### F7.6 — Alerts & Notifications

Use deterministic rule/event generation first, with AI optionally explaining or prioritizing results.

Candidate alerts:

- low stock / low days-of-stock;
- approaching expiry;
- unusual usage spike/drop;
- data-quality/mapping problems;
- reconciliation/sync failure;
- pending access/password-reset requests.

One backend event/alert may later surface through Web, Telegram, Flutter, and other notification channels rather than being independently reimplemented per client.

Saved/scheduled analysis may later generate recurring operational summaries and notifications under identifiable SYSTEM/AI_AGENT provenance.

## F8 — External/Custom GPT read-only integration

Only after F7.2 identity/RBAC and the core audit/analysis contracts are stable:

- connect Custom GPT through the typed HTTPS API;
- reuse the same read/analytics interfaces used by internal clients;
- read-only Actions first;
- revocable scoped service/client credential;
- no arbitrary SQL or DB credentials;
- verify health, stock/lot lookup, audit/summary, and approved analysis reads.

## F9 — Controlled typed write experiment

Only after identity/RBAC + ledger/idempotency/actor-audit foundations are verified:

- authorize one low-risk typed write operation first;
- server-side validation + RBAC/delegation;
- idempotency/operation ID;
- atomic transaction;
- complete actor/client provenance;
- audit event;
- committed-state readback;
- no direct SQL from LLM/GPT clients;
- database remains non-canonical.

Preferred client architecture:

`Web / Telegram / Flutter / Internal AI / Custom GPT -> typed Inventory API -> auth/RBAC/delegation -> validation -> idempotency -> DB transaction -> actor-aware audit -> readback`

AI agents are never invisible superusers. When acting on behalf of a human, delegated authority must be explicit and auditable.

## F10 — Dual real-workflow + Sheet sync validation

Run representative live operations through the existing Sheet workflow and backend shadow path, then compare results.

Add the operational sync/mirror contract deliberately; do not let LLM clients write directly to Sheets. Backend owns the typed operation and any Sheet mirror/sync behavior.

No automatic canonical cutover.

## F11 — Canonical promotion

Requires explicit approval plus:

- fresh migration baseline;
- measurable parity acceptance;
- backup + restore proof;
- actor-aware audit completeness;
- real-workflow validation;
- Sheet mirror rebuild/sync confidence;
- rollback/cutback procedure.

Only after promotion may PostgreSQL become the operational source of truth for the approved operation scope.

## Recommended execution order

1. F7.2A canonical multi-user identity.
2. F7.2B User Management.
3. F7.2C credential lifecycle.
4. F7.3 actor-aware Audit / operation ledger.
5. F7.4 deterministic Smart Analysis.
6. F7.5 internal read-only AI Assistant.
7. F7.6 Alerts & Notifications.
8. F8 external/Custom GPT read-only integration.
9. F9 first controlled typed write.
10. F10 dual-workflow + Sheet sync validation.
11. F11 canonical promotion.

## Safety boundary

Do not treat F6B test data as production migration truth. Do not begin production inventory writes, DB promotion, Telegram inventory writes, Flutter rollout, Sheet mirror conversion, or Custom GPT write Actions until the corresponding slice is explicitly authorized.

## Continuity rule

After every significant architecture decision, implementation slice, deployment/migration result, or next-work change, update `ROADMAP.md`, `NEW_CHAT_BOOTSTRAP.md`, `IMPLEMENTATION_PLAN.md`, and relevant canonical docs.
