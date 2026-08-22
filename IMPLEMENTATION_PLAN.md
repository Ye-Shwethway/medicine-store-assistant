# Medicine Store Assistant — Implementation Plan

Status: **F7.2A canonical identity/sessions, F7.2B User Management, and F7.2C Credential + Recovery Lifecycle verified complete; F7.2D AI Agent Management is the next implementation slice; production inventory write authority remains unauthorized**

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
- Normal continuation uses connected tools, repository automation, and the self-hosted runner. Do not require the Owner to use Termux, SSH, Bamboo/Bamboo Claw, tmux, or manual GitHub Actions for normal development.
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

Canonical reconciliation classes retain the established skill semantics:

- `SAFE` — strong evidence compatibility; routine operation may proceed when its operation class is pre-authorized;
- `REVIEW` — likely match but meaningful uncertainty; require human review before identity-sensitive mutation;
- `CONFLICT` — contradictory/recycled/incompatible evidence; block automatic propagation;
- `NEW_UNMAPPED` — no acceptable existing match; require the appropriate create/mapping review workflow.

UI may use semantic visual treatment, but stored workflow state must be explicit and not depend on color alone.

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
- F7.2C — Credential + Recovery Lifecycle and self-service Account security

F6B remains a verified **test-only** live-workbook staging exercise, not an accepted migration baseline.

### F7.2A verification evidence

- PR #36 merged as `c3aa75d65e0bc6d1836227fe8450b0b3de5b2651`;
- automatic VPS deploy run `32586385336`, job `97063270146`, success;
- Alembic `0004_shadow -> 0005_identity`;
- existing F2 `users` / `roles` / `user_roles` evolved as canonical human identity;
- canonical Owner bootstrap reused the existing password hash without plaintext exposure;
- username/password auth, durable revocable DB session, Owner RBAC, authenticated 403, and disabled-user denial passed;
- F6B stayed row_count 1646 / SAFE 1417 / REVIEW 222 / CONFLICT 0 / NEW_UNMAPPED 7;
- `database_canonical=false` and `migration_baseline_accepted=false` remained enforced;
- no live workbook import and no inventory mutation.

### F7.2B verification evidence

- PR #38 merged as `e4671c75ab2ece2a6f5065a78779413ef3e9f38b`;
- automatic VPS deploy run `32588170791`, job `97067607202`, success;
- Alembic `0005_identity -> 0006_user_management`;
- public pending-only access request, pending-user denial, Owner list, approval, role assignment, rejection, non-Owner 403, OWNER ordinary-flow escalation guard, role-change session revocation, disable/reactivate, explicit session revocation, account-security events, and notification events passed;
- Dashboard profile UI contract passed;
- public anonymous User Management access remained 401;
- no live workbook import and no inventory mutation.

### F7.2C verification evidence

Base lifecycle:

- PR #40 merged as `a910658efc3cbc214b30a1f5ed946fdd34ffe4a2`;
- automatic VPS deploy run `32589571152`, job `97071112514`, success;
- Alembic `0006_user_management -> 0007_credential_lifecycle`;
- self-service username/password change, current-password re-authentication, credential/session invalidation, enumeration-safe reset request, Owner reset review/issuance, digest-only token persistence, single-use reset, and security/notification events passed.

Final recovery/account refinements:

- PR #43 — Recovery email integrated into Account security;
- PR #44 — recovery token cleanup/schema compatibility fixed provider-failure masking as HTTP 500;
- PR #45 — Resend helper transport compatibility fixed Cloudflare error 1010 by using explicit API-client headers;
- PR #46 — Forgot password accepts username or verified recovery email; password confirmation backend/UI added;
- PR #47 — Account-security JS cache-bust for Android Chrome;
- PR #48 — Request Access captures recovery email and sends pending-access verification;
- PR #49 — runtime-contract compatibility hotfix;
- final production source SHA `371936e0c7088c76f692292d31318cfd972a1a46`;
- issue #26 reported `status=success`, deploy run `32596093790`;
- verified recovery email and automated Resend reset delivery tested successfully;
- `database_canonical=false`, `migration_baseline_accepted=false`, F6B test-only status, and read-only inventory boundary preserved;
- no production inventory mutation.

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

All clients reuse the same backend identity, authority, store-location, preference, inventory, analytics, calculator, recovery, and operation contracts.

---

# F7 — Application and control-plane foundation before production writes

## F7.2A — Canonical multi-user identity and sessions — VERIFIED COMPLETE

Purpose: replace the bootstrap password-only Owner bridge with durable human accounts.

### Implemented

- stable canonical UUID `user_id` using existing F2 `users`;
- username + password authentication;
- roles `OWNER`, `ADMIN`, `STAFF`, `READ_ONLY`;
- states `PENDING`, `ACTIVE`, `DISABLED`;
- one current static role per human user;
- durable user-bound `user_sessions` with opaque client token, server-side digest, expiry, revocation, last-seen, and credential-version binding;
- Owner migration without plaintext password exposure;
- backend role-policy helpers and explicit 403 behavior;
- disabled users fail protected-session resolution;
- inventory/dashboard remains read-only.

### Exit criteria — pass

- Owner canonical login/session;
- stable `user_id` + OWNER role;
- disabled-user denial;
- authenticated 403 role denial;
- anonymous dashboard denial;
- non-canonical/test-only authority flags;
- no inventory mutation.

## F7.2B — User Management — VERIFIED COMPLETE

Purpose: durable human account/access workflow, separate from Audit and AI Agent Management.

### Implemented

- dedicated Owner-only User Management;
- Request Access creates pending account/request only;
- pending users receive no role/private access;
- Owner approve/reject/assign `ADMIN`, `STAFF`, `READ_ONLY`;
- current F7.2B does not delegate User Management to ADMIN;
- ordinary User Management cannot create/promote/mutate `OWNER`;
- role change revokes sessions;
- disable/reactivate/session revoke;
- account-security events;
- reusable notification-event contract;
- explicit Access Denied state;
- account/security history separate from operational F7.3 Audit.

### UI/UX

Follows pinned UI/UX Pro Max + locked Dashboard v2.4 design system.

- login Request Access progressive disclosure;
- drawer/sidebar signed-in profile box;
- circular avatar area with deterministic initials fallback;
- canonical username + role from authenticated backend session;
- textual account states, no color-only meaning;
- responsive touch/keyboard behavior;
- read-only inventory boundary preserved.

Profile-image upload/edit remains deferred.

### Exit criteria — pass

- pending/rejected protected-access denial;
- Owner list/review;
- exact role assignment;
- non-Owner User Management 403;
- OWNER mutation guard;
- role/session revocation;
- disable/reactivate;
- explicit session revoke;
- account-security/notification events;
- separate User Management/Audit;
- profile UI contract;
- no inventory mutation.

## F7.2C — Credential + Recovery Lifecycle — VERIFIED COMPLETE

Purpose: product-native username/password/recovery maintenance without routine VPS/terminal intervention.

Canonical design: `docs/design/F7_2C_CREDENTIAL_LIFECYCLE_DESIGN.md`.

Final checkpoint: `docs/checkpoints/F7_2C_FINAL_RECOVERY_2026-08-23.md`.

### Username maintenance

- authenticated current-password re-authentication;
- existing 3–64 username contract;
- case-insensitive uniqueness;
- stable `user_id`, role, state preserved;
- `credential_version` increment;
- prior-session invalidation;
- `USERNAME_CHANGED` security event;
- initial bootstrap username `owner` can be replaced through Account without changing `OWNER` role.

### Password maintenance

- authenticated current-password re-authentication;
- New password + Confirm new password;
- mismatch rejected in UI and backend;
- one-way password hash only;
- credential-version increment;
- prior-session invalidation;
- outstanding reset cancellation;
- `PASSWORD_CHANGED` security event.

### Recovery email

- Account has Recovery email card with `Not set` / `Unverified` / `Verified` state;
- adding/changing address requires current-password re-authentication;
- verification token is cryptographically random, short-lived, single-use, digest-only at rest;
- current verified address remains active until replacement is verified;
- verification completion records security events;
- recovery email never changes role/account authority.

### Resend adapter — deployed

Dedicated domain:

`msamail.drthorne.uk`

Sender:

`no-reply@msamail.drthorne.uk`

Runtime variables:

- `RESEND_API_KEY`
- `MSA_RECOVERY_EMAIL_FROM`

Secrets remain in protected VPS runtime environment and are mapped through canonical `deploy/docker-compose.yml`.

The Resend domain is verified. DKIM/SPF/Return-Path records are deployed under the dedicated mail namespace. Parent-domain DMARC was not added merely for this slice because the suggested `_dmarc` entry would affect the parent-domain policy boundary.

The helper sends explicit `Accept: application/json` and an application User-Agent because Cloudflare in front of Resend rejected the default Python urllib fingerprint with error 1010.

### Forgot password — deployed automated recovery

Public UI offers:

- Username
- Verified recovery email

Public responses remain enumeration-safe.

Email mode resolves only a unique eligible active account with that verified address. Ambiguous matches do not select a user.

Eligible automated flow:

1. request recovery;
2. create/issue short-lived single-use reset token;
3. persist only token digest/verifier material;
4. send reset link through Resend;
5. user opens `/dashboard/login#reset=<token>`;
6. backend validates state/expiry/one-use;
7. replace password hash;
8. increment credential version;
9. revoke prior sessions;
10. consume/reset verifier state;
11. record security/notification events.

Owner-assisted reset issuance remains an **operational fallback**, not the normal recovery path, for exceptional cases/no usable verified channel/delivery failure.

### Request Access email verification

Request Access now collects:

- Display name
- Username
- Recovery email
- Password
- Confirm password

A new request remains `PENDING` and unassigned until Owner approval.

The email may be verified while account is `PENDING`. Verification only activates recovery-email proof; it never grants a role or protected access.

If Owner approval occurs first, the same valid verification link may still complete for the active account. If the account is rejected/disabled before verification, the pending verification is not eligible to activate access.

If initial delivery fails, the access request may remain pending with unverified email; after approval the user can verify/change email from Account security.

### Security rules

- public forgot responses enumeration-safe;
- recovery email requires proof of control;
- reset/verification tokens short-lived, single-use, digest-only at rest;
- provider credentials never enter Git/browser storage;
- provider failure never grants/reduces account authority;
- email provider is transport only, not account authority;
- account-security history remains separate from operational Audit;
- no inventory authority changes.

### Verified exit criteria — pass

- username change current-password gate;
- old username/session invalid after change;
- new username login;
- password change current-password + confirmation gate;
- old password/session invalid after change;
- verified recovery email activation;
- automated Resend delivery;
- username-mode Forgot password;
- recovery-email-mode Forgot password;
- generic public response;
- digest-only reset token storage;
- single-use reset/reuse denial;
- old-session denial after reset;
- Owner fallback reset review/issuance;
- Request Access recovery email deployed without bypassing `PENDING`/Owner approval;
- runtime health/readiness green;
- no inventory mutation;
- authority flags unchanged.

### Explicit non-scope

- profile-image upload/editing;
- Owner creation/promotion flow;
- F7.2D AI Agent Management;
- global Settings;
- operational/store Audit implementation;
- inventory writes or AI inventory writes;
- transfers or Smart Calculator deductions;
- Telegram/Flutter stock mutation;
- Sheet mirror conversion;
- PostgreSQL canonical promotion.

Telegram recovery is future work after secure Telegram identity linking. It must reuse canonical `user_id`, recovery policy, token lifecycle, and notification events rather than becoming a second credential authority.

## F7.2D — AI Agent Management & delegated authority — NEXT

Purpose: create the Owner-only control plane for named AI/service principals while preserving the low-friction `$msa` workflow.

Canonical design: `docs/architecture/F7_2D_AI_AGENT_MANAGEMENT.md`.

### Principal model

AI agents are distinct `AI_AGENT` principals, not human users with copied staff roles.

Each agent may have:

- stable `agent_id`;
- active/disabled state;
- typed capability allowlist;
- location scope: Main Store, selected Sub Stores, all active stores, or read-only analytical scope;
- authority ceiling;
- delegated vs autonomous execution policy;
- confirmation policy: read-only, propose-only, confirm-before-write, or autonomous-within-preauthorized-scope;
- revocable service/client credential where applicable.

### Owner-only control plane

Only `OWNER` may create, configure, enable/disable, revoke, or change AI-agent capability/location/authority policy.

`AI Agent Management` and global `Settings` are Owner-only surfaces.

An agent can never change its own grant, authority ceiling, Agent Management policy, Owner/security controls, or global Settings.

### Effective authority

For a human-delegated AI action:

`effective_authority = human_authority ∩ agent_capability_scope ∩ location_scope ∩ operation_policy`

Consequences:

- Owner may grant Main Store reads and, only in later separately authorized write phases, Main Store typed writes;
- agents are **not** Sub-Store-only;
- Staff/Admin may use AI Chat only if Owner enables it;
- AI Chat cannot expand a user's normal role/location authority;
- even Owner-invoked agent cannot execute capabilities not granted to that agent.

### MSA workflow parity

- SAFE operations inside a pre-authorized workflow may later execute without per-row confirmation once corresponding production writes are separately authorized;
- REVIEW/CONFLICT/NEW_UNMAPPED and material/high-risk cases require human review;
- writes require deterministic validation, idempotency where applicable, atomic commit, actor-aware audit, and read-back verification;
- future Main Store CMS price/reconciliation workflows may be delegated only when Owner capability policy and later write authorization both allow them.

### Exit criteria

- Owner can manage agent principals/scopes from product control plane;
- non-Owner users cannot access Agent Management/global Settings;
- agent cannot self-escalate;
- capability/location intersection deterministic/testable;
- no inventory write tool enabled merely by creating agent.

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
- autonomous policy reference;
- client/source: Web, Telegram, Flutter, Internal AI, Custom GPT, system job, integration;
- typed action name;
- location/target references;
- reconciliation class where relevant;
- validation/approval result;
- timestamp/outcome;
- before/after or stock-ledger references;
- reversal/correction linkage;
- sync/mirror result linkage.

Rules:

- Audit is operational history, not User Management or Agent Management;
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

Owner may switch backend policy from Settings without code/formula changes.

### Preferences

Backend user preferences may include default location/Calculator Sub Store, allowed Calculator-location switching, card/table/list view, visible columns/order/density, saved filters, analysis defaults, calculator defaults, fee presets, and receipt defaults.

### Exit criteria

- deterministic one-Main constraint;
- unlimited Sub Store representation without duplicating product identity;
- deterministic location balance reads;
- reorder basis controlled through one Owner setting;
- reusable cross-client preference contract;
- no stock mutation enabled yet.

## F7.5 — Smart Calculator & Receipts — calculation-only first

Purpose: backend-backed calculator workflow without Excel re-upload or stock mutation.

### Normal data source

Calculator searches backend product/lot/location records directly. Normal use does not ask for Excel column mapping. Owner batch-intake/import mapping remains separate.

### Capabilities

- item search and same-name disambiguation;
- quantity/effective price;
- multiple items;
- fee presets/ad-hoc allowed fees;
- receiver/customer, issuer, note;
- subtotal/fees/total;
- saved calculation sessions;
- receipt identity/history;
- print-friendly Web receipt;
- PDF/export/share reusable by Flutter later.

Modes:

- `CALCULATE_ONLY` — no stock mutation;
- future `DISPENSE_FROM_SUB_STORE` — later controlled-write slice only.

AI/photo scan may build a calculation draft after typed candidate matching; ambiguity requires human selection and OCR/LLM interpretation alone never commits stock.

### Exit criteria

- DB/API-backed Calculator without Excel remapping;
- explicit similar-item disambiguation;
- deterministic calculations/fees/receipts;
- Web save/print/export;
- stock unchanged.

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
- Owner may enable AI Chat for Staff/Admin;
- no arbitrary SQL;
- no write tools yet.

Future write tools reuse F7.2D policy and F7.3 audit rather than inventing separate AI authority.

## F7.8 — Alerts & Notifications

Deterministic event generation first; optional AI explanation/prioritization second.

Initial candidates include low stock/days-of-stock, Sub Store refill pressure, expiry, unusual transfer/dispense patterns, data-quality issues, sync failures, access/reset requests, scheduled analysis results, and credential-recovery delivery events.

One backend event contract is reusable across Web, Telegram, Flutter, email, and future clients. Channel adapters remain transport-only and never become account/inventory authority.

Resend email delivery is already proven for credential recovery and may be reused for broader email notifications later. Telegram delivery requires secure account linking/pairing before it can be a recovery or notification destination.

---

# F8 — External / Custom GPT read-only integration

Reuse approved typed read/analytics interfaces with scoped/revocable service or delegated auth. External AI principals must be Owner-registered in Agent Management where applicable. No DB/Sheet credentials and no writes.

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
- validate existing `$msa` reconciliation/approval/read-back behavior against typed DB operations;
- define backend-owned Google Sheet mirror/sync;
- clients/AI never bypass backend to mutate Sheets in canonical architecture;
- retry/idempotency/reconciliation failures observable;
- mismatches reported rather than silently repaired.

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

Only after approved promotion may PostgreSQL become operational source of truth for promoted scope.

# Later client rollout

Telegram and Flutter are clients over the same backend contracts, not separate inventory truths.

Telegram account linking must bind a verified/pairing-confirmed Telegram identity to canonical `user_id`; once implemented, linked bot channel may deliver recovery links/notifications without becoming account authority.

Flutter may provide mobile-optimized card/table views, Smart Calculator, receipt/share/print, preferences, alerts, and offline-tolerant caching; local cache never becomes a second canonical inventory store.

## Recommended execution order

1. **F7.2A — Canonical multi-user identity** — verified complete
2. **F7.2B — User Management** — verified complete
3. **F7.2C — Credential + Recovery Lifecycle** — verified complete
4. **F7.2D — AI Agent Management & delegated authority** — next
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

The next authorized slice is **F7.2D AI Agent Management & delegated authority**.

Reuse the verified F7.2A human identity/session/RBAC foundation, F7.2B User Management/security-event foundation, and final F7.2C username/password/recovery-email lifecycle.

Do not implement F7.3 operational Audit, production inventory writes, AI inventory writes, store transfers, Calculator deduction, Telegram/Flutter mutation, Sheet mirror conversion, or canonical promotion as part of F7.2D unless a strict prerequisite is separately authorized.
