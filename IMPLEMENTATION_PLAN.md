# Medicine Store Assistant — Implementation Plan

Status: **foundation and read-only dashboard verified; F7.2A canonical multi-user identity is the next implementation slice; production write authority is not yet authorized**

This plan translates the approved architecture into small, reversible implementation slices. It does not replace `ROADMAP.md`; it defines execution order and exit criteria.

## Global rules

- Preserve `skills/medicine-store-assistant/` unchanged as the canonical Git-backed skill source.
- Google Sheets remains operationally authoritative until explicit canonical promotion.
- PostgreSQL deployment alone does not make the database canonical.
- No client receives arbitrary SQL or database credentials.
- Human users, AI agents, integrations, and system jobs call typed backend operations only.
- AI-generated interpretation is never silently substituted for deterministic database truth.
- Secrets never enter the public repository.
- Every significant slice leaves `NEW_CHAT_BOOTSTRAP.md`, `ROADMAP.md`, `IMPLEMENTATION_PLAN.md`, and relevant canonical docs current.
- Prefer the smallest runnable slice; avoid unnecessary infrastructure.
- Normal continuation uses connected tools + repository automation + self-hosted runner; do not require Termux/SSH/Bamboo/manual Actions from the owner.

## Completed foundation — F0 through F6C

F0, F1, F2, F3, F4, F5, F5.1, F6A, and F6C are verified complete.

F6B is a verified **test-only** live-workbook staging exercise. It is not an accepted migration baseline and must not be promoted.

## F7 — Web application, identity, audit, and intelligence

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
- migrate/bootstrap the existing Owner into the user model without exposing plaintext password;
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
- `Request access` creates pending request/account only;
- pending account receives no private inventory access;
- Owner sees pending requests in product UI;
- Owner can approve/reject and assign `ADMIN`, `STAFF`, or `READ_ONLY`;
- ADMIN cannot grant/promote `OWNER`;
- Owner creation/promotion uses separate high-risk flow;
- disable/reactivate behavior;
- account/role/status changes recorded as security events;
- define notification event contract so Telegram can later mirror pending approvals without becoming authorization source.

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
- later verified-email recovery only if deliberately added.

Exit criteria:

- user can change password from browser;
- forgotten password can be recovered through durable product flow;
- reset tokens expire and are one-use;
- old sessions fail after reset.

### F7.3 — Actor-aware Store/Database Audit & Operation Ledger

Purpose: make human + AI collaboration traceable before broad multi-client or AI writes exist.

Canonical actor categories:

- `HUMAN`
- `AI_AGENT`
- `SYSTEM`
- `INTEGRATION`

Audit/operation provenance must support:

- stable `operation_id`;
- idempotency key where applicable;
- actor type/id;
- delegated/authorized human `user_id` when AI acts for a user;
- client/source such as Web, Telegram, Flutter, internal AI, Custom GPT, or system job;
- typed operation/action name;
- target/affected-record references;
- timestamp/outcome;
- before/after or ledger movement references where appropriate;
- reversal/correction linkage;
- sync/mirror result linkage.

Rules:

- Audit is operational/database history, not User Management;
- AI agents are never invisible superusers;
- secrets/passwords/tokens and unrestricted prompt transcripts are not stored in operational audit;
- historical ledger/audit records are not silently edited/deleted; corrections use linked reversal/correction semantics.

Exit criteria:

- representative test operations clearly distinguish human vs AI/service/system origin;
- AI delegated action records the authorizing human where applicable;
- Audit can answer what/who-or-what/source/when/result/affected records;
- User Management remains separate.

### F7.4 — Smart Analysis Foundation

Purpose: create professional read-only operational intelligence that remains useful without an LLM.

Initial v1 modules:

1. Stock Health
2. Usage Trends
3. Expiry Risk
4. Reorder Outlook
5. Price Movement
6. Data Quality

Tasks:

- deterministic SQL/domain formula layer;
- analytics API contracts;
- date/category/item filters;
- KPI cards and professional charts;
- drill-down from metrics/charts to supporting rows/lots/operations;
- dataset/canonicality labeling when operating on shadow/test data;
- optional AI commentary boundary, but deterministic values remain primary.

Exit criteria:

- key metrics are reproducible without AI;
- chart/table values can be inspected and traced to supporting data;
- no opaque AI score is presented as fact;
- Smart Analysis works if AI provider is unavailable.

### F7.5 — Internal AI Assistant

Purpose: add a first-party database-grounded conversational analysis workspace.

Initial mode: read-only.

Tasks:

- register internal Assistant as identifiable `AI_AGENT` principal;
- expose typed analysis tools such as stock health, usage trend, period comparison, expiry risk, reorder candidates, price movement, data-quality issues, and audit summary;
- ground all database-dependent answers in tool/API results;
- allow conversational drill-down and chart/table requests;
- preserve current-user RBAC scope;
- log appropriate agent/tool provenance without storing secrets or unrestricted sensitive prompt transcripts.

Exit criteria:

- Assistant can answer representative operational questions from structured backend truth;
- the same answer can expose supporting chart/table facts;
- role boundaries are respected;
- no arbitrary SQL/DB credential is exposed;
- no inventory write tool exists yet.

### F7.6 — Alerts & Notifications

Purpose: turn analytics/rules into reusable operational attention events across clients.

Initial candidate alert rules:

- low stock / low days-of-stock;
- approaching expiry;
- unusual usage spike/drop;
- data-quality or mapping problems;
- reconciliation/sync failure;
- pending User Management access/password-reset requests.

Tasks:

- deterministic alert/event generation first;
- Web notification center;
- reusable notification event contract;
- Telegram delivery later;
- Flutter delivery later;
- optional AI explanation/prioritization layered on the same backend event;
- later saved/scheduled analysis presets with SYSTEM/AI_AGENT provenance.

Exit criteria:

- one backend event can be surfaced through multiple clients;
- alert facts are reproducible without AI;
- notification delivery state is observable;
- AI explanation does not replace the triggering deterministic fact.

## F8 — External / Custom GPT read-only Action integration

Only after F7.2 identity/RBAC and the core read/audit/analysis contracts are stable.

Tasks:

- version-control `integrations/custom-gpt/openapi.yaml`;
- expose scoped read-only typed APIs;
- reuse approved analytics contracts rather than create a parallel GPT-only data model;
- use revocable service/client credential or delegated authorization;
- start with health, stock lookup, lot lookup, audit/summary and approved analysis reads;
- no writes in first GPT experiment.

Exit criteria:

- Custom GPT can reliably call allowed reads/analysis;
- auth, timeout, and error behavior are verified;
- actor/source provenance is available;
- no DB or Sheet credentials are exposed.

## F9 — Controlled typed write Action experiment

Only after ledger/idempotency/actor-audit + identity/RBAC tests pass.

Purpose: prove one safe end-to-end write before broad inventory mutation is allowed.

First operation should be one low-risk typed domain command, not arbitrary CRUD/SQL.

Required write pipeline:

`Client/Agent -> typed Inventory API -> authentication/RBAC/delegation -> validation -> idempotency -> atomic DB transaction -> actor-aware audit -> committed-state readback -> result`

Requirements:

- operation ID/idempotency key;
- backend validation;
- server-side authorization/delegation;
- explicit human/AI/system actor provenance;
- no arbitrary SQL;
- no direct LLM-to-DB connection;
- no direct LLM-to-Sheet write;
- failure never becomes conversational success;
- PostgreSQL remains non-canonical.

Exit criteria:

- duplicate replay cannot duplicate movement;
- failed operation rolls back;
- successful operation has auditable actor/source/authority/result;
- readback matches committed state.

## F10 — Dual real-workflow and Sheet sync validation

Purpose: prove backend operations against current operational Sheet truth before cutover.

Tasks:

- run representative real operations through existing Sheet workflow and backend shadow path;
- compare balances/lots/history;
- define Google Sheet mirror/sync contract behind backend;
- backend owns sync orchestration; clients/AI never bypass it;
- include retry/idempotency/reconciliation behavior for sync failures;
- produce mismatch reports rather than silent repairs.

Exit criteria:

- representative workflows reconcile measurably;
- sync failure is observable/recoverable;
- no automatic canonical cutover.

## F11 — Canonical promotion

Requires explicit approval.

Before promotion:

- import fresh real migration baseline;
- verify parity acceptance criteria;
- prove backup + restore;
- verify actor-aware audit completeness;
- verify realistic read/write workflows;
- verify Sheet mirror/rebuild/reconciliation;
- document rollback/cutback.

Promotion may be operation-scope based rather than all-at-once if explicitly designed and approved.

## Recommended immediate order

1. Complete and verify **F7.2A** canonical multi-user identity.
2. Implement **F7.2B** User Management/access approval.
3. Implement **F7.2C** credential lifecycle.
4. Implement **F7.3** actor-aware store/database Audit & operation ledger.
5. Implement **F7.4** deterministic Smart Analysis + professional charts.
6. Implement **F7.5** internal read-only AI Assistant.
7. Implement **F7.6** Alerts & Notifications.
8. Begin **F8** external/Custom GPT read-only integration.
9. Only then authorize **F9** first controlled typed write experiment.
10. Continue F10 dual-workflow/sync validation before any F11 promotion.
