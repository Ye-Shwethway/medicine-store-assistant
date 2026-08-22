# Medicine Store Assistant — Implementation Plan

Status: **F7.2A canonical identity/sessions and F7.2B User Management verified complete; F7.2C Credential Lifecycle is the next implementation slice; production inventory write authority remains unauthorized**

This file is the execution contract for the current Medicine Store Assistant architecture. `ROADMAP.md` remains the high-level roadmap; this plan defines implementation order, dependencies, and exit criteria.

## 1. Global implementation rules

- Google Sheets remains operationally authoritative until an explicit F11 canonical-promotion decision is approved and verified.
- PostgreSQL being deployed does **not** make it canonical.
- The current F6B dataset is test-only and must never be silently promoted into migration truth.
- No Web, Telegram, Flutter, Custom GPT, internal AI agent, integration, or system job receives arbitrary SQL or raw database credentials.
- Humans, AI agents, integrations, and system jobs operate through typed backend APIs/commands.
- Deterministic backend code owns identity resolution, arithmetic, constraints, authorization, location scope, idempotency, transactions, derived state, and committed read-back.
- AI may interpret evidence, reconcile candidates, prepare proposals, explain results, and execute explicitly allowed typed operations; AI interpretation never replaces source evidence or deterministic database truth.
- Every meaningful mutation must carry actor/client/authority provenance and must not be reported as successful until committed-state read-back succeeds.
- Historical committed stock/ledger facts are corrected through reversal/correction semantics rather than silent destructive rewriting.
- Secrets never enter Git, browser storage, application logs, prompt/audit payloads, or documentation evidence.
- Prefer the smallest runnable slice and avoid unnecessary infrastructure.
- Normal continuation uses connected tools, repository automation, and the self-hosted runner. Do not require the Owner to use Termux, SSH, Bamboo/Bamboo Claw, tmux, or manual GitHub Actions.
- Significant architecture, implementation, deployment, migration, or next-work changes must update `ROADMAP.md`, `NEW_CHAT_BOOTSTRAP.md`, this file, and relevant canonical docs.

## 2. Existing MSA workflow that the new architecture must preserve

The database system is an evolution of the existing `$msa` operating model, not a replacement for its useful behavior.

For evidence-driven workflows such as CMS issue/supply papers, price updates, and paper-form reconciliation, preserve this conceptual sequence:

1. inspect source evidence;
2. reconcile against the current authoritative inventory data;
3. classify identity/confidence;
4. perform only the operation classes already authorized by Owner policy;
5. surface material ambiguity instead of guessing;
6. commit through a typed backend operation;
7. read the affected state back;
8. record actor/operation/audit provenance;
9. report success only after verification.

Canonical reconciliation classes may retain the established skill semantics:

- `SAFE` — strong evidence compatibility; routine operation may proceed when its operation class is pre-authorized;
- `REVIEW` — likely match but meaningful uncertainty; require human review before identity-sensitive mutation;
- `CONFLICT` — contradictory/recycled/incompatible evidence; block automatic propagation;
- `NEW_UNMAPPED` — no acceptable existing match; require the appropriate create/mapping review workflow.

UI may use green/yellow/red-style visual treatment, but stored workflow state must be explicit and not depend on color alone.

Owner authorization is policy-based as well as per-operation. A narrow SAFE workflow may run without asking for confirmation on every obvious row when the Owner has already granted that workflow scope. REVIEW/CONFLICT/NEW_UNMAPPED and high-risk operations remain review/approval boundaries.

## 3. Verified foundation

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
- F7.2A — canonical multi-user identity and sessions
- F7.2B — User Management and signed-in drawer profile

F6B remains a verified **test-only** live-workbook staging exercise, not an accepted migration baseline.

F7.2A verification evidence:

- PR #36 merged as `c3aa75d65e0bc6d1836227fe8450b0b3de5b2651`;
- automatic VPS deploy run `32586385336`, job `97063270146`, completed successfully;
- Alembic `0004_shadow -> 0005_identity` succeeded;
- existing F2 `users` / `roles` / `user_roles` were evolved as the canonical human identity model rather than replaced;
- canonical Owner bootstrap used the existing password hash without plaintext exposure;
- username/password auth, durable revocable DB session, Owner RBAC, authenticated 403, and disabled-user denial all passed runtime acceptance;
- F6B remained row_count 1646 / SAFE 1417 / REVIEW 222 / CONFLICT 0 / NEW_UNMAPPED 7;
- `database_canonical=false` and `migration_baseline_accepted=false` remained true boundaries;
- deployment executed no live workbook import and no inventory mutation.

F7.2B verification evidence:

- PR #38 merged as `e4671c75ab2ece2a6f5065a78779413ef3e9f38b`;
- automatic VPS deploy run `32588170791`, job `97067607202`, completed successfully;
- Alembic `0005_identity -> 0006_user_management` succeeded;
- public pending-only access request, pending-user denial, Owner list, approval, role assignment, rejection, non-Owner 403, OWNER ordinary-flow escalation guard, role-change session revocation, disable/reactivate, explicit session revocation, account-security events, and notification events all passed runtime acceptance;
- Dashboard profile UI contract passed: drawer/sidebar profile box with circular avatar area, initials fallback, canonical username, and role;
- public anonymous User Management access remained 401;
- F6B counts remained unchanged and `database_canonical=false` / `migration_baseline_accepted=false` remained enforced;
- deployment executed no live workbook import and no inventory mutation.

## 4. Product architecture direction

MSA is a multi-client intelligent store-operations platform with:

- Web dashboard;
- future Telegram client;
- future Flutter client;
- canonical human users;
- Owner-managed AI/service agents;
- internal AI Assistant;
- Custom GPT / ChatGPT integrations;
- scheduled/system jobs;
- actor-aware operational audit;
- one Main Store plus expandable Sub Stores;
- Smart Calculator and receipts;
- deterministic Smart Analysis;
- Alerts & Notifications.

All clients reuse the same backend identity, authority, store-location, preference, inventory, analytics, calculator, and operation contracts.

---

# F7 — Application and control-plane foundation before production writes

## F7.2A — Canonical multi-user identity and sessions — **VERIFIED COMPLETE**

Purpose: replace the bootstrap password-only Owner bridge with durable human accounts.

### Implemented

- stable canonical UUID `user_id` using the existing F2 `users` table;
- username login field and username + password authentication;
- approved roles `OWNER`, `ADMIN`, `STAFF`, `READ_ONLY` through the existing `roles` / `user_roles` model;
- account states `PENDING`, `ACTIVE`, `DISABLED`;
- one role per canonical human user for the current static RBAC model;
- durable user-bound `user_sessions` with opaque client token, server-side keyed digest, expiry, revocation, last-seen tracking, and credential-version binding;
- bootstrap of the existing Owner password hash into the canonical user model without plaintext exposure;
- normal Owner login changed from password-only to username + password;
- backend `require_roles(...)` helper and `require_owner_session` specialization;
- explicit authenticated `403 / Access denied` result for role denial;
- protected-session resolution rejects disabled users immediately;
- deployment acceptance exercises a temporary auth-only READ_ONLY user and removes it afterward;
- inventory/dashboard data access remains read-only.

### Verified exit criteria

- Owner authenticates through the canonical username/password model — pass;
- session resolves to stable `user_id` + `OWNER` role — pass;
- disabled user loses protected access with an existing session — pass;
- server-side role denial returns authenticated 403 / `Access denied` — pass;
- anonymous private dashboard access remains 401 — pass;
- PostgreSQL remains non-canonical and F6B remains test-only — pass;
- no inventory mutation was introduced — pass.

Compatibility note: F7.2A preserved the already-deployed bootstrap PBKDF2 password hash specifically so the Owner could migrate without plaintext access. New credential creation/upgrade policy belongs to F7.2C.

## F7.2B — User Management — **VERIFIED COMPLETE**

Purpose: durable human account/access workflow, separate from Audit and AI Agent Management.

### Implemented

- dedicated Owner-only `User Management` surface;
- `Request access` creates a pending account/request only;
- pending users receive no role/private inventory access and cannot authenticate to protected inventory;
- Owner sees pending requests and may approve/reject/assign `ADMIN`, `STAFF`, or `READ_ONLY`;
- current deployed F7.2B does not delegate User Management to ADMIN;
- ordinary User Management cannot assign/promote/mutate an existing `OWNER`; Owner creation/promotion remains a separate high-risk future flow;
- active non-Owner role changes revoke existing sessions;
- disable/reactivate and explicit session-revoke flows;
- account-security events for request/approval/rejection/role/state/session changes;
- reusable notification-event contract for future Telegram/Flutter approval mirrors;
- explicit authenticated Access Denied state;
- account/security history remains separate from operational F7.3 Audit.

### UI/UX implementation

The Web implementation follows the pinned UI/UX Pro Max skill together with the locked Dashboard v2.4 design system.

- login page has a progressively disclosed `Request access` flow;
- drawer/sidebar top section below product branding and above navigation has a signed-in profile box;
- profile box shows circular avatar area, deterministic initials fallback, canonical username, and current role;
- profile identity comes from the authenticated backend session rather than browser-side profile storage;
- User Management shows textual `PENDING` / `ACTIVE` / `DISABLED` states and does not rely on color alone;
- controls are responsive and preserve the read-only inventory UI boundary.

Profile-image upload/editing is intentionally deferred and is not automatically part of F7.2C.

### Verified exit criteria

- pending/rejected users cannot access protected inventory — pass;
- Owner can list/review pending users — pass;
- approved users receive the exact assigned role — pass;
- non-Owner User Management access returns 403 — pass;
- ordinary OWNER mutation/escalation is backend-blocked — pass;
- role changes revoke prior sessions — pass;
- disabled users lose protected sessions — pass;
- reactivation works for approved non-Owner accounts — pass;
- explicit session revocation works — pass;
- account-security and notification events persist — pass;
- User Management remains separate from operational Audit and AI Agent Management — pass;
- drawer profile UI contract — pass;
- no credential-reset lifecycle or inventory mutation was introduced — pass.

## F7.2C — Credential lifecycle — **NEXT**

Purpose: credential maintenance without VPS/terminal intervention.

### Tasks

- authenticated password change with current-password re-authentication;
- forgotten-password reset request that does not reveal whether a username exists;
- Owner-assisted v1 reset approval/issuance;
- short-lived single-use reset token/link;
- store only reset-token digest/verifier material after issuance boundary;
- successful password change/reset increments credential version and invalidates old sessions;
- security/account event recording;
- product UI for user change-password and Owner-assisted reset workflow;
- verified-email recovery only if separate email infrastructure is deliberately added later.

### Exit criteria

- password change works through product UI and requires the correct current password;
- reset request is enumeration-safe;
- reset flow is durable, short-lived, and one-use;
- expired/consumed tokens fail;
- old sessions fail after change/reset;
- successful reset permits login only with the new credential;
- security/account and reusable notification events are verified;
- normal credential maintenance requires no VPS/terminal intervention;
- inventory authority flags/read-only boundary remain unchanged.

F7.2C must not silently include profile-image upload/editing, F7.2D Agent Management, F7.3 operational Audit, or inventory writes unless separately authorized.

## F7.2D — AI Agent Management & delegated authority

Purpose: create the Owner-only control plane for named AI/service principals while preserving the low-friction `$msa` workflow.

Canonical design: `docs/architecture/F7_2D_AI_AGENT_MANAGEMENT.md`.

### Principal model

AI agents are distinct `AI_AGENT` principals, not human users with copied staff roles.

Each agent may have:

- stable `agent_id`;
- active/disabled state;
- typed capability allowlist;
- location scope: Main Store, selected Sub Stores, all active stores, or read-only analytical scope as configured;
- authority ceiling;
- delegated vs autonomous execution policy;
- confirmation policy such as read-only, propose-only, confirm-before-write, or autonomous-within-preauthorized-scope;
- revocable service/client credential where applicable.

### Owner-only control plane

Only `OWNER` may create, configure, enable/disable, revoke, or change AI-agent capability/location/authority policy.

`AI Agent Management` and global `Settings` are Owner-only surfaces.

An agent can never change its own grant, authority ceiling, Agent Management policy, Owner/security controls, or global Settings.

### Effective authority

For a human-delegated AI action:

`effective_authority = human_authority ∩ agent_capability_scope ∩ location_scope ∩ operation_policy`

This means:

- the Owner may explicitly grant an agent Main Store reads and, in later authorized write phases, Main Store typed writes;
- agents are **not** Sub-Store-only;
- Staff/Admin users may use AI Chat only when the Owner enables that feature for them;
- AI Chat cannot expand a user's normal role/location authority;
- an Owner-invoked agent still cannot execute capabilities that the Owner did not grant to that agent.

### MSA workflow parity

- SAFE operations inside a pre-authorized workflow may execute without per-row confirmation once production writes for that operation are separately authorized;
- REVIEW/CONFLICT/NEW_UNMAPPED and material/high-risk cases require human review/approval;
- all writes require deterministic validation, idempotency where applicable, atomic commit, actor-aware audit, and read-back verification;
- Main Store workflows such as future CMS price reconciliation/batch operations may be delegated to AI if Owner capability policy allows them.

### Exit criteria

- Owner can manage agent principals and scopes from product UI/control plane;
- non-Owner users cannot access Agent Management or global Settings;
- an agent cannot self-escalate;
- capability/location intersection is testable and deterministic;
- no inventory write tool is enabled merely by creating an agent.

## F7.3 — Actor-aware Audit & Operation Ledger

Purpose: establish traceability before humans and AI agents collaborate on write-capable operations.

Actor classes:

- `HUMAN`
- `AI_AGENT`
- `SYSTEM`
- `INTEGRATION`

Required provenance, as applicable:

- stable `operation_id`;
- idempotency key;
- actor type/id;
- `authorized_by_user_id` for delegated AI/service action;
- autonomous policy reference where there is no live human delegate;
- client/source: Web, Telegram, Flutter, Internal AI, Custom GPT, system job, integration;
- typed action name;
- location/target references;
- reconciliation class where operationally relevant;
- validation/approval result;
- timestamp/outcome;
- before/after or stock-ledger references;
- reversal/correction linkage;
- sync/mirror result linkage.

Rules:

- Audit is store/database operational history, not User Management or Agent Management;
- AI agents are never invisible superusers;
- secrets, credentials, tokens, and unrestricted prompt transcripts are not stored in operational audit;
- committed history is not silently edited/deleted.

### Exit criteria

Audit can answer what happened, who/what initiated it, under whose authority, through which client, at which location, what changed, and whether it succeeded/failed/reversed.

## F7.4 — Inventory Locations, Store Policy & Preferences

Purpose: create location-aware inventory and persistent cross-client operational preferences without live stock mutation.

### Store model

- exactly one `MAIN` Store;
- Owner may create any number of `SUB` Stores;
- Sub Stores may be renamed/activated/disabled while history is preserved;
- product/lot balances are location-aware;
- initial transfer direction is Main Store -> selected Sub Store;
- current `Daily Usage` data is future Main->Sub Stock Transfer evidence where source truth supports it; never invent historical destinations.

### Reorder policy — Owner-only Settings

- `MAIN_STORE_ONLY` — initial/default;
- `TOTAL_ACTIVE_STOCK` — Main Store + all active Sub Stores.

The Owner may switch the backend policy from Settings without code/formula changes.

### Preferences

Backend user preferences may include default location/Calculator Sub Store, allowed Calculator-location switching, card/table/list view, visible columns/order/density, saved filters, analysis defaults, calculator defaults, fee presets, and receipt defaults.

### Exit criteria

- one-Main constraint is deterministic;
- unlimited Sub Store representation works without duplicating product identity;
- location balances read deterministically;
- reorder basis switches through one Owner setting;
- preference contract is reusable across Web/Flutter/other clients;
- no stock mutation is enabled yet.

## F7.5 — Smart Calculator & Receipts — calculation-only first

Purpose: restore the useful local Flutter calculator workflow as a backend-backed feature without Excel re-upload or stock mutation.

### Normal data source

Calculator searches backend product/lot/location records directly. Normal use does not ask for Excel column mapping. Owner batch-intake/import mapping remains a separate ingestion workflow.

### Capabilities

- item search and same-name disambiguation;
- quantity and effective/reference price;
- multiple items;
- extra-fee presets/ad-hoc allowed fees;
- receiver/customer, issuer, note;
- subtotal/fees/total;
- saved calculation sessions;
- receipt identity/history;
- print-friendly Web receipt;
- PDF/export/share contract reusable by Flutter later.

Modes:

- `CALCULATE_ONLY` — no stock mutation;
- future `DISPENSE_FROM_SUB_STORE` — selected/default Sub Store, activated only in a later controlled-write slice.

AI/photo scan may build a calculation draft after typed candidate matching; ambiguity requires human selection and OCR/LLM interpretation alone never commits stock.

### Exit criteria

- DB/API-backed Calculator works without Excel remapping;
- similar items are explicitly distinguishable;
- calculations/fees/receipts are deterministic;
- Web can save/print/export;
- stock quantity remains unchanged.

## F7.6 — Smart Analysis

Deterministic first, AI-assisted second.

Initial modules:

1. Stock Health
2. Transfer / Usage Trends
3. Expiry Risk
4. Reorder Outlook
5. Price Movement
6. Data Quality

Requirements include professional KPI/charts, product/category/date/store filters, Main/Sub/Total visibility, active reorder-policy labeling, and drill-down to supporting rows/lots/operations.

## F7.7 — Internal AI Assistant

Purpose: first-party conversational workspace grounded in typed backend tools.

Initial mode remains read-only.

- identifiable `AI_AGENT` principal;
- tools for stock/lot/location lookup, analytics, comparison, expiry/reorder risk, data quality, Calculator draft/reference lookup, and audit summaries;
- signed-in user role/location scope remains part of effective authority;
- Owner may enable AI Chat for Staff/Admin users;
- no arbitrary SQL;
- no write tools yet.

Future write tools reuse F7.2D policy and F7.3 audit rather than inventing a separate AI authority path.

## F7.8 — Alerts & Notifications

Deterministic event generation first; optional AI explanation/prioritization second.

Initial candidates include low stock/days-of-stock, Sub Store refill pressure, expiry, unusual transfer/dispense patterns, data-quality issues, sync failures, access/reset requests, and scheduled analysis results.

One backend event contract is reusable across Web, Telegram, Flutter, and future clients.

---

# F8 — External / Custom GPT read-only integration

Reuse approved typed read/analytics interfaces with scoped/revocable service or delegated auth. External AI principals must be Owner-registered in the Agent Management model where applicable. No DB/Sheet credentials and no writes.

# F9 — Controlled typed write foundation

Purpose: prove safe typed mutation after identity, Agent Management, audit, location, and idempotency foundations are stable.

Required path:

`Client/Agent -> typed API -> auth/RBAC/delegation -> agent capability + location scope -> validation/reconciliation policy -> idempotency -> atomic DB transaction -> actor-aware audit -> committed-state readback -> result`

Potential typed operations include:

- approved Main Store CMS price/metadata reconciliation;
- approved batch/receipt operation;
- Main Store -> Sub Store transfer;
- reversal/correction;
- Smart Calculator Sub Store dispense;
- later controlled adjustments.

Start with a narrow synthetic/test operation. Technical write success does not make PostgreSQL canonical or authorize broad production writes.

For AI-agent writes, preserve `$msa` semantics: pre-authorized SAFE workflow classes may proceed with low friction; REVIEW/CONFLICT/NEW_UNMAPPED and high-risk operations require human review.

# F10 — Real workflow, fresh migration & Sheet sync validation

- keep Owner batch-intake workflow separate from Smart Calculator;
- import a fresh migration candidate only when authorized;
- reinterpret supported historical `Daily Usage` as Stock Transfer evidence without inventing unknown destinations;
- compare real Sheet workflow against backend shadow operations;
- validate the existing `$msa` reconciliation/approval/read-back behavior against typed DB operations;
- define backend-owned Google Sheet mirror/sync;
- clients/AI never bypass the backend to mutate Sheets in the canonical architecture;
- retry/idempotency/reconciliation failures are observable;
- mismatches are reported rather than silently repaired.

No automatic cutover.

# F11 — Canonical promotion

Requires explicit Owner approval plus:

- fresh migration baseline;
- measurable parity acceptance;
- backup/restore proof;
- location-aware workflow validation;
- actor-aware audit completeness;
- AI/delegated workflow validation;
- Sheet mirror/rebuild/reconciliation confidence;
- rollback/cutback procedure.

Only after approved promotion may PostgreSQL become the operational source of truth for the promoted scope.

# Later client rollout

Telegram and Flutter are clients over the same backend contracts, not separate inventory truths.

Flutter may provide mobile-optimized card/table views, Smart Calculator, receipt/share/print, preferences, alerts, and offline-tolerant caching; local cache never becomes a second canonical inventory store.

## Recommended execution order

1. **F7.2A — Canonical multi-user identity** — verified complete
2. **F7.2B — User Management** — verified complete
3. **F7.2C — Credential lifecycle** — next
4. **F7.2D — AI Agent Management & delegated authority**
5. **F7.3 — Actor-aware Audit / operation ledger**
6. **F7.4 — Inventory Locations, Store Policy & Preferences**
7. **F7.5 — Smart Calculator / receipts, calculation-only**
8. **F7.6 — Smart Analysis**
9. **F7.7 — Internal read-only AI Assistant**
10. **F7.8 — Alerts & Notifications**
11. **F8 — External/Custom GPT read-only integration**
12. **F9 — Controlled typed writes**
13. **F10 — Real workflow + fresh migration + Sheet sync validation**
14. **F11 — Canonical promotion**
15. Telegram/Flutter rollout over proven contracts

## Immediate work boundary

The next authorized slice is **F7.2C Credential Lifecycle**. Reuse the verified F7.2A canonical human identity/session/RBAC foundation and F7.2B User Management/security-event foundation. Do not implement F7.2D AI Agent Management, F7.3 operational Audit, production inventory writes, AI writes, store transfers, Calculator deduction, Telegram/Flutter mutation, Sheet mirror conversion, or canonical promotion as part of this slice unless a strict prerequisite is separately authorized.
