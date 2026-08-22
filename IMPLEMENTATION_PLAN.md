# Medicine Store Assistant — Implementation Plan

Status: **foundation and read-only dashboard verified; F7.2A canonical multi-user identity is the next implementation slice; production inventory write authority remains unauthorized**

This plan is the execution contract for the current Medicine Store Assistant architecture. It converts the approved product direction into small, reversible slices with explicit exit criteria.

`ROADMAP.md` remains the high-level project roadmap. This file defines implementation order, dependencies, and the boundaries that must be preserved while moving from the current Sheet-led workflow toward a multi-client intelligent store operations platform.

## 1. Global implementation rules

- Google Sheets remains operationally authoritative until an explicit canonical-promotion slice is approved and verified.
- PostgreSQL being deployed does **not** make it canonical.
- The current F6B dataset remains test-only and must never be silently promoted into migration truth.
- No browser, Telegram bot, Flutter client, Custom GPT, internal AI agent, or integration receives arbitrary SQL or database credentials.
- Human users, AI agents, integrations, and system jobs operate through typed backend APIs/commands.
- AI interpretation never replaces deterministic database facts, formulas, business rules, or auditable transaction results.
- Every meaningful state-changing operation must eventually carry stable actor/client provenance.
- Historical stock/ledger records are corrected through reversal/correction semantics rather than destructive history editing where auditability matters.
- Secrets never enter Git, browser storage, application logs, or documentation evidence.
- Prefer the smallest runnable slice and avoid unnecessary infrastructure.
- Normal continuation uses connected tools, repository automation, and the self-hosted runner. Do not require the Owner to use Termux, SSH, Bamboo/Bamboo Claw, tmux, or manual GitHub Actions.
- Significant architecture, implementation, deployment, migration, or next-work changes must update `ROADMAP.md`, `NEW_CHAT_BOOTSTRAP.md`, this file, and relevant canonical docs.

## 2. Verified foundation

Verified complete:

- F0 — VPS inspection / host preparation
- F1 — runtime skeleton
- Cloudflare HTTPS route
- F2 — PostgreSQL foundation
- F3 — authenticated read-only API
- F4 — synthetic ledger primitives
- F5 — CMS catalogue versioning
- F5.1 — catalogue read API
- F6A — synthetic shadow migration adapter
- F6C — authenticated shadow read API
- F7.1 — read-only Web Dashboard foundation
- bootstrap Owner login/data/logout path for F7.2

F6B remains a verified **test-only** live-workbook staging exercise, not an accepted migration baseline.

## 3. Product architecture direction

MSA is not intended to be only a spreadsheet replacement. The target system is a multi-client store operations platform with:

- Web dashboard;
- future Telegram client;
- future Flutter client;
- internal AI Assistant;
- Custom GPT / ChatGPT integrations;
- scheduled/system jobs;
- deterministic analytics;
- alerts and notifications;
- receipts/calculation workflow;
- one Main Store plus expandable Sub Stores;
- complete actor-aware operational audit.

All clients reuse the same backend identity, role, store-location, inventory, analytics, calculator, and operation contracts.

---

# F7 — Application foundation before production writes

## F7.2A — Canonical multi-user identity and sessions — **NEXT**

Purpose: replace the bootstrap password-only Owner bridge with durable human accounts before expanding privileged application features.

### Tasks

- add canonical human-account schema with stable `user_id`;
- unique mutable username;
- password hash + credential metadata;
- roles: `OWNER`, `ADMIN`, `STAFF`, `READ_ONLY`;
- account states: `PENDING`, `ACTIVE`, `DISABLED`;
- user-bound revocable sessions;
- migrate/bootstrap the existing Owner into the canonical account model without exposing plaintext credentials;
- normal Owner login becomes username + password;
- backend authorization helpers and role policy tests;
- explicit authenticated `403 / Access denied` state;
- session revocation on disable/security events;
- keep inventory read-only.

### Exit criteria

- Owner authenticates with username + password;
- session resolves to stable `user_id` + `OWNER` role;
- disabled users lose protected access;
- role checks are server-side and deterministic;
- no inventory mutation is introduced.

## F7.2B — User Management

Purpose: create a durable account/access workflow independent of store Audit.

### Tasks

- dedicated `User Management` navigation/screen;
- `Request access` creates pending account/request only;
- pending users receive no private inventory access;
- Owner sees pending requests;
- Owner may approve/reject and assign `ADMIN`, `STAFF`, or `READ_ONLY`;
- ADMIN may not grant/promote `OWNER`;
- Owner creation/promotion uses a separate high-risk flow;
- disable/reactivate/revoke flows;
- security events for account/role/status changes;
- notification-event contract so Telegram can later mirror approval requests without becoming the authorization source.

### Exit criteria

- pending/rejected users cannot access protected inventory;
- approved users receive the exact assigned role;
- escalation boundaries are enforced by backend tests;
- User Management remains separate from operational Audit.

## F7.2C — Credential lifecycle

Purpose: make credentials maintainable without VPS/terminal intervention.

### Tasks

- authenticated password change with re-authentication;
- forgotten-password reset request;
- Owner-assisted v1 reset approval/issuance;
- short-lived single-use reset token/link;
- revoke old sessions after reset;
- security-event recording;
- verified-email recovery only if separate email infrastructure is deliberately introduced later.

### Exit criteria

- password change works through product UI;
- reset flow is durable and one-use;
- expired reset tokens fail;
- old sessions fail after reset/disable.

## F7.3 — Actor-aware Audit & Operation Ledger Foundation

Purpose: establish the traceability layer required before humans and AI agents begin collaborating on write-capable workflows.

### Canonical actor classes

- `HUMAN`
- `AI_AGENT`
- `SYSTEM`
- `INTEGRATION`

### Operation provenance

Support, as applicable:

- stable `operation_id`;
- idempotency key;
- actor type/id;
- `authorized_by_user_id` when an AI/service acts under human authority;
- client/source: Web, Telegram, Flutter, internal AI, Custom GPT, system job, integration;
- typed action name;
- target/affected-record references;
- timestamp and outcome;
- before/after or stock-ledger references;
- reversal/correction linkage;
- sync/mirror result linkage.

### Rules

- Audit is store/database operational history, not User Management;
- AI agents are never invisible superusers;
- secrets, passwords, tokens, and unrestricted prompt transcripts are never operational-audit payloads;
- historical committed operations are not silently edited/deleted.

### Exit criteria

- representative test operations distinguish human, AI, system, and integration origin;
- delegated AI actions preserve authorizing human identity;
- Audit can answer what happened, who/what initiated it, under whose authority, through which client, what changed, and the result.

## F7.4 — Inventory Locations, Store Policy & Preference Foundation

Purpose: move from a single implicit stock pool to an expandable location-aware model without yet enabling live stock mutation.

### Store-location rules

- exactly **one** `MAIN` store exists for the system;
- Owner may create any number of `SUB` stores;
- Sub Stores can be renamed, activated, disabled/archived according to policy without destroying history;
- inventory balance is modeled per product/lot/location;
- current operational `Daily Usage` semantics are treated as a future migration source for **Main Store -> Sub Store transfer history**, not assumed to be true end-customer consumption;
- migration provenance retains the original source sheet/document name.

### Transfer-domain direction

Initial stock movement concepts:

- `RECEIPT`: external source -> Main Store;
- `TRANSFER`: Main Store -> selected Sub Store;
- `DISPENSE/USAGE`: selected Sub Store -> customer/consumption;
- `ADJUSTMENT`: controlled balance correction;
- `REVERSAL/CORRECTION`: linked correction of a previously committed operation.

Whether Sub-to-Sub transfer is supported is deferred until there is a real workflow need.

### Reorder policy

Owner-configurable setting:

- `MAIN_STORE_ONLY` — **initial/default production policy**;
- `TOTAL_ACTIVE_STOCK` — Main Store + all active Sub Stores.

The Owner can switch this policy from Settings without changing formulas/code. Analytics and reorder calculations read the policy from the backend.

Regardless of active reorder policy, analysis may display Main, Sub, and Total stock separately.

### User/location preferences

Support durable user preferences such as:

- default store/location;
- default Smart Calculator dispense Sub Store;
- whether a role/user may change Calculator store;
- card/table/list view preference;
- visible columns, column order, table density;
- saved filters and analysis defaults;
- receipt/calculator defaults.

Cross-device preferences belong in backend user preferences. Ephemeral device-only display state may use local client storage.

### Exit criteria

- schema/policy guarantees only one Main Store;
- multiple Sub Stores can be represented without duplicating product identity;
- product/lot/location balances can be read deterministically;
- reorder policy can switch between Main-only and Total-active-stock using one Owner setting;
- preference contract is client-independent;
- no live stock mutation is enabled yet.

## F7.5 — Smart Calculator & Receipt Foundation — calculation-only first

Purpose: restore the valuable Flutter calculator workflow as a first-class backend-backed product capability without requiring Excel uploads or inventory writes.

### Data source

- Calculator searches the canonical backend product/lot rows;
- normal Calculator use **does not** ask users to map Excel columns;
- item identity is `product_id`/`lot_id`, not display name alone;
- same/similar names must be disambiguated using relevant brand/strength/lot/expiry/code/location details;
- owner batch-intake/import mapping remains a separate data-ingestion workflow and is not part of Calculator UX.

### Calculation workflow

- item search and selection;
- quantity;
- effective/reference price;
- multiple added items;
- extra-fee presets and ad-hoc allowed fee lines;
- receiver/customer;
- issuer;
- note;
- subtotal/fee/total calculation;
- saved calculation session;
- receipt identity and history;
- print-friendly Web receipt;
- PDF/export/share contract reusable by Flutter later.

### Modes

1. `CALCULATE_ONLY`
   - does not mutate stock;
   - may save receipt/calculation history.

2. `DISPENSE_FROM_SUB_STORE`
   - designed now, but **write capability remains disabled until the later controlled-write slice**;
   - selected Sub Store is explicit;
   - user preference can provide default Sub Store;
   - stock availability must be validated at commit time once writes are authorized.

### AI/photo upgrade contract

Future scan/photo-to-calculation flow may:

- extract candidate item/quantity text;
- resolve candidate products through typed search;
- surface ambiguous same-name matches for human selection;
- create a draft calculation only;
- never auto-commit inventory based solely on AI/OCR interpretation.

### Exit criteria

- Calculator works from backend data with no Excel re-upload/mapping requirement;
- same-name candidates are explicitly distinguishable;
- calculations, fees, totals, saved sessions, and receipts are deterministic;
- Web can save/print/export a calculation receipt;
- no stock quantity changes occur in this slice.

## F7.6 — Smart Analysis Foundation

Purpose: provide professional read-only operational intelligence independent of LLM availability.

### Initial modules

1. Stock Health
2. Transfer / Usage Trends
3. Expiry Risk
4. Reorder Outlook
5. Price Movement
6. Data Quality

### Requirements

- deterministic SQL/domain formulas/business rules;
- professional KPI cards and charts;
- date/category/product/store filters;
- Main/Sub/Total stock visibility where relevant;
- active reorder policy clearly identified;
- drill-down from charts/metrics to supporting rows/lots/operations;
- test/non-canonical dataset labeling when applicable;
- AI commentary may explain results but never becomes the numeric source of truth.

### Exit criteria

- metrics are reproducible without AI;
- supporting data is inspectable;
- Main-vs-Sub-vs-Total analysis is available where useful;
- Smart Analysis remains usable if the AI provider is offline.

## F7.7 — Internal AI Assistant

Purpose: add a first-party read-only conversational analysis workspace grounded in typed backend truth.

### Tasks

- register the Assistant as an identifiable `AI_AGENT` principal;
- typed tools for stock health, transfer/usage trends, period comparison, expiry risk, reorder candidates, price movement, data quality, calculator/reference lookup, and audit summaries;
- preserve the signed-in user's RBAC and location scope;
- allow chart/table/drill-down requests;
- log appropriate tool/agent provenance;
- no arbitrary SQL;
- no inventory write tools yet.

### Exit criteria

- Assistant answers representative operational questions from structured backend facts;
- responses can expose supporting tables/charts;
- role/location boundaries are respected;
- no write capability exists.

## F7.8 — Alerts & Notifications

Purpose: convert deterministic rules/events into reusable attention signals across clients.

### Initial candidates

- low stock / low days-of-stock;
- approaching expiry;
- transfer/usage anomalies;
- data-quality/mapping issues;
- reconciliation/sync failure;
- pending access/password-reset requests;
- later store-specific refill pressure and saved/scheduled analysis results.

### Requirements

- deterministic alert generation first;
- Web notification center;
- one reusable backend notification event contract;
- Telegram and Flutter delivery later;
- optional AI explanation/prioritization layered on the same event;
- observable delivery/read state.

### Exit criteria

- one backend event can surface in multiple clients;
- trigger facts are reproducible without AI;
- AI explanation cannot replace the underlying alert fact.

---

# F8 — External / Custom GPT read-only integration

Only after identity/RBAC and core audit/read/analysis contracts are stable.

### Tasks

- version-control Custom GPT OpenAPI contract;
- expose scoped typed read APIs;
- reuse internal read/analytics interfaces;
- revocable service/client credential or delegated auth;
- health, stock/lot/location lookup, audit summary, analysis reads, and permitted Calculator reference reads;
- no writes.

### Exit criteria

- Custom GPT can reliably call allowed reads;
- actor/source provenance is available;
- no DB/Sheet credentials are exposed.

# F9 — Controlled typed write foundation

Purpose: prove safe state mutation after identity, audit, location, and ledger foundations are stable.

No arbitrary CRUD/SQL writes are introduced.

Required pipeline:

`Client/Agent -> typed API -> auth/RBAC/location scope/delegation -> validation -> idempotency -> atomic DB transaction -> actor-aware audit -> committed-state readback -> result`

### Initial write sequence

Start with a deliberately narrow synthetic/test operation, then expand only after verification.

Candidate operational commands include:

- Main Store -> Sub Store transfer;
- reversal/correction of a committed transfer;
- Sub Store dispense operation generated from Smart Calculator;
- controlled receipt/adjustment operations later.

Smart Calculator `DISPENSE_FROM_SUB_STORE` becomes write-capable only here or a specifically authorized descendant slice.

### Exit criteria

- duplicate replay cannot duplicate a movement;
- failed operation rolls back;
- successful operation records actor/source/authority/location/result;
- committed-state readback matches transaction state;
- production authority is still not implied merely by technical success.

# F10 — Real workflow, migration, and Sheet sync validation

Purpose: reconcile the redesigned Main/Sub Store model with the real operational workflow before any canonical cutover.

### Tasks

- define Owner batch-intake workflow separately from Smart Calculator;
- import a fresh migration candidate when authorized;
- reinterpret/transform historical `Daily Usage` records as Stock Transfer source data where supported by source truth;
- do not silently invent Sub Store destinations when historical source data lacks them;
- run representative Sheet workflow and backend shadow operations in parallel;
- compare Main balances, Sub balances where available, transfers, lots, and history;
- define Google Sheet mirror/sync contract behind the backend;
- clients/AI never write directly to the workbook;
- retry/idempotency/reconciliation for sync failures;
- mismatch reports instead of silent repair.

### Exit criteria

- representative workflows reconcile measurably;
- historical ambiguity is surfaced rather than guessed;
- sync failure is observable/recoverable;
- no automatic canonical cutover.

# F11 — Canonical promotion

Requires explicit Owner approval.

Before promotion:

- fresh migration baseline;
- measurable parity acceptance;
- backup/restore proof;
- location-aware inventory validation;
- actor-aware audit completeness;
- realistic transfer/dispense/receipt workflow validation;
- Sheet mirror/rebuild/reconciliation proof;
- rollback/cutback procedure.

Promotion may be operation-scope based instead of all-at-once if deliberately designed and approved.

# Later client rollout tracks

Telegram and Flutter are not separate sources of inventory truth. They are additional clients over the same backend contracts.

Future client rollout should reuse:

- canonical users/RBAC;
- store/location scope;
- user preferences;
- Smart Calculator and receipts;
- Smart Analysis;
- Alerts/Notifications;
- AI Assistant tools;
- typed inventory operations;
- actor-aware Audit.

Flutter should eventually support mobile-optimized card/table views, Smart Calculator, receipt/share/print workflows, and optional offline-tolerant caching without creating a second canonical database.

# Recommended implementation order

1. **F7.2A — Canonical multi-user identity**
2. **F7.2B — User Management**
3. **F7.2C — Credential lifecycle**
4. **F7.3 — Actor-aware Audit / operation ledger foundation**
5. **F7.4 — Inventory Locations, Store Policy & Preferences**
6. **F7.5 — Smart Calculator / receipts, calculation-only**
7. **F7.6 — Smart Analysis**
8. **F7.7 — Internal read-only AI Assistant**
9. **F7.8 — Alerts & Notifications**
10. **F8 — External/Custom GPT read-only integration**
11. **F9 — Controlled typed writes**
12. **F10 — Real workflow + migration + Sheet sync validation**
13. **F11 — Canonical promotion**
14. Telegram/Flutter expansion over the proven backend contracts

The immediate authorized continuation remains **F7.2A**, followed by User Management and credential lifecycle. Store-location, Calculator, analytics, AI, alerts, and write capabilities must not jump ahead of the identity/audit foundation.