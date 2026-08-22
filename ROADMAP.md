# Medicine Store Assistant — Project Roadmap

Status: **F0/F1/F2/F3/F4/F5/F5.1/F6A/F6C/F7.1/F7.2A/F7.2B/F7.2C verified complete; F6B remains test-only; F7.2D AI Agent Management is next; PostgreSQL remains non-canonical**

The live Google workbook/source documents remain operationally authoritative. The current F6B snapshot is test-only and is not an accepted migration baseline. A fresh real migration dataset will be imported only after the redesigned operational workflow, location model, management surfaces, and shadow-validation path are ready and explicitly approved.

## Delivery policy

Canonical flow: `test -> pull request -> main -> automatic VPS deploy for relevant runtime changes`.

Normal continuation does not require manual VPS commands, Termux/SSH/tmux, Bamboo/Bamboo Claw, or a manual Actions deploy button. Prefer connected tools, repository automation, the repo-scoped self-hosted runner, and durable browser/admin mechanisms.

Runtime secrets remain only on the VPS. Normal backend deployment must not read/import the live workbook. Deployment status is published to GitHub issue #26 (`MSA deployment status`) so connected tooling can inspect deployment evidence directly.

## Product direction

MSA is a multi-client intelligent store-operations platform, not merely a database-backed spreadsheet replacement.

Future clients/actors include Web, Telegram, Flutter, internal MSA AI Assistant, Custom GPT/ChatGPT integrations, scheduled jobs, and external integrations.

All clients use the same typed backend contracts, canonical identities, role/delegation rules, store-location scope, preferences, audit, analytics, calculator/receipt flows, and later controlled inventory operations. No client or AI agent receives arbitrary SQL or raw database credentials.

The new architecture preserves the useful `$msa` workflow: source evidence is reconciled against current truth, classified as `SAFE` / `REVIEW` / `CONFLICT` / `NEW_UNMAPPED`, routine SAFE operations may run inside an Owner-preauthorized workflow, ambiguous/high-risk cases return for human review, successful writes require read-back verification, and significant operations remain auditable.

## Verified foundation

- F0 VPS inspection — verified complete 2026-08-22
- F1 runtime skeleton — verified complete 2026-08-22
- Cloudflare public HTTPS route — verified complete 2026-08-22
- F2 PostgreSQL foundation — verified complete 2026-08-22
- F3 authenticated read-only API — verified complete 2026-08-22
- F4 synthetic ledger foundation — verified complete 2026-08-22
- F5 synthetic CMS catalogue versioning — verified complete 2026-08-22
- F5.1 authenticated catalogue read API — verified complete 2026-08-22
- F6A synthetic shadow migration adapter — verified complete 2026-08-22
- F6B live-workbook snapshot — test-only staging exercise
- F6C authenticated shadow read API — verified complete 2026-08-22
- F7.1 read-only Web Dashboard — verified complete 2026-08-22
- F7.2 temporary bootstrap Owner credential bridge — superseded by F7.2A
- F7.2A canonical multi-user identity and sessions — verified complete 2026-08-22 via PR #36, merge `c3aa75d65e0bc6d1836227fe8450b0b3de5b2651`, deploy run `32586385336`
- F7.2B User Management and signed-in drawer profile — verified complete 2026-08-22 via PR #38, merge `e4671c75ab2ece2a6f5065a78779413ef3e9f38b`, deploy run `32588170791`, job `97067607202`
- F7.2C Credential Lifecycle and self-service account/recovery security — verified complete 2026-08-23; base PR #40 plus final recovery refinements through PR #49; final verified runtime SHA `371936e0c7088c76f692292d31318cfd972a1a46`

## F7.2A verified result

- existing F2 `users`, `roles`, and `user_roles` remain the canonical human-identity foundation;
- stable UUID `user_id` is preserved across clients/sessions;
- normal login is username + password;
- canonical roles are `OWNER`, `ADMIN`, `STAFF`, `READ_ONLY`;
- canonical states are `PENDING`, `ACTIVE`, `DISABLED`;
- browser sessions are durable DB-bound opaque sessions with server-side token digests, expiry, revocation, and credential-version binding;
- the existing Owner password hash was materialized into the canonical user model without exposing plaintext credentials;
- backend `require_roles(...)` authorization returns explicit authenticated `403 / Access denied` for insufficient role;
- disabled users immediately lose protected access even if a previously issued session token still exists;
- public dashboard private gate remains authenticated and read-only;
- `database_canonical=false` and `migration_baseline_accepted=false` remain enforced;
- deployment performed no live workbook import and introduced no inventory mutation.

## F7.2B verified result

- Alembic upgraded `0005_identity -> 0006_user_management`;
- public `Request access` creates a `PENDING` canonical user/request only and does not grant a role or protected access;
- pending users cannot authenticate to protected inventory;
- Owner-only User Management lists human users and pending requests;
- Owner can approve as `ADMIN`, `STAFF`, or `READ_ONLY`, or reject a request;
- approved users receive the exact assigned role;
- non-Owner User Management access returns authenticated `403 / Access denied`;
- ordinary User Management cannot mutate/demote the existing `OWNER` account; Owner creation/promotion remains a separate high-risk future flow;
- active non-Owner role changes revoke existing sessions;
- account disable removes protected access and approved disabled accounts can be reactivated;
- explicit per-user session revocation works;
- account/security events are stored separately from operational Audit;
- reusable notification events exist for future Web/Telegram/Flutter delivery;
- Dashboard drawer/sidebar top section now shows a signed-in profile box with circular avatar area, canonical username, and current role;
- deterministic initials are used as the avatar fallback until profile-image management is separately authorized;
- User Management is a standalone surface separate from operational Audit;
- UI work follows the pinned UI/UX Pro Max skill and locked Dashboard v2.4 design system;
- public anonymous User Management gate returns 401;
- `database_canonical=false`, `migration_baseline_accepted=false`, and the read-only inventory boundary remain enforced;
- deployment performed no live workbook import and introduced no inventory mutation.

## F7.2C verified result

- Alembic upgraded `0006_user_management -> 0007_credential_lifecycle`, with later recovery-email schema refinements preserving the same human identity model;
- all active human roles have an authenticated `Account` surface for self-service username, password, and recovery-email maintenance;
- username is mutable while stable canonical `user_id`, role, and account state remain unchanged;
- the bootstrap username `owner` is not a permanent visible identity requirement and the existing Owner can replace it through the Account page while retaining the `OWNER` role;
- username change requires current-password re-authentication, case-insensitive uniqueness, credential-version increment, session revocation, and a `USERNAME_CHANGED` security event;
- password change requires current-password re-authentication, explicit Confirm new password, one-way hash replacement, credential-version increment, session revocation, outstanding reset cancellation, and a `PASSWORD_CHANGED` security event;
- recovery email can be added/changed from Account and becomes active only after inbox verification;
- current verified recovery email remains active until a replacement email is successfully verified;
- Resend is configured as the transactional recovery-mail adapter using verified sending domain `msamail.drthorne.uk` and sender `no-reply@msamail.drthorne.uk`;
- runtime Resend secrets stay on the VPS and are mapped by canonical `deploy/docker-compose.yml`;
- the Resend helper uses explicit API-client headers after Cloudflare error 1010 blocked the default Python urllib fingerprint;
- public forgotten-password recovery supports either username or verified recovery email while preserving enumeration-safe generic responses;
- eligible verified-email recovery automatically issues/sends the existing short-lived single-use reset link;
- email-mode recovery requires a unique eligible verified-address match and never chooses an arbitrary account when ambiguous;
- Owner-only User Management assisted reset issuance remains a fallback path;
- persistent reset/verification storage retains only keyed token digest/verifier material; plaintext token material is not stored after issuance boundaries;
- reset links use `/dashboard/login#reset=<token>` so plaintext token material is not sent in ordinary HTTP request URLs;
- successful reset changes only the password credential, increments credential version, revokes sessions, consumes the reset, and records security/notification events;
- `Request access` now collects Display name, Username, Recovery email, Password, and Confirm password;
- a new access request remains `PENDING` and unassigned until Owner approval, even when its recovery email has already been verified;
- pending-access email verification does not grant protected access or a role;
- Account recovery-email placement, recovery cleanup error handling, password confirmation, username-or-email reset, Android asset cache behavior, and Request Access email verification were all finalized through PRs #43–#49;
- final deployment issue #26 reported `status=success` for source SHA `371936e0c7088c76f692292d31318cfd972a1a46`;
- UI work follows Dashboard v2.4 and the pinned UI/UX Pro Max skill;
- profile-image upload/editing remains separately deferred;
- public anonymous private/User Management gates remain 401;
- `database_canonical=false`, `migration_baseline_accepted=false`, F6B test-only status, and the read-only inventory boundary remain enforced;
- deployment performed no live workbook import and introduced no inventory mutation.

## Test-only F6B snapshot

- batch ID `be13d127-5045-4284-a088-0a0b9b024d76`
- rows **1,646**
- SAFE **1,417**
- REVIEW **222**
- NEW_UNMAPPED **7**
- CONFLICT **0**
- `migration_baseline_accepted=false`
- `database_canonical=false`

## Canonical current architecture docs

- `IMPLEMENTATION_PLAN.md`
- `docs/architecture/F7_WEB_DASHBOARD.md`
- `docs/design/F7_2_AUTH_RBAC_DESIGN.md`
- `docs/design/F7_2C_CREDENTIAL_LIFECYCLE_DESIGN.md`
- `docs/checkpoints/F7_2C_FINAL_RECOVERY_2026-08-23.md`
- `docs/architecture/F7_2D_AI_AGENT_MANAGEMENT.md`
- `docs/architecture/F7_3_ACTOR_AUDIT_AND_OPERATION_LEDGER.md`
- `docs/architecture/F7_4_F7_8_STORE_AND_INTELLIGENCE_ARCHITECTURE.md`
- `design-system/medicine-store-assistant/MASTER.md`
- `design-system/medicine-store-assistant/pages/dashboard.md`

## F7 — Application and control-plane foundation

### F7.2A — Canonical multi-user identity — **VERIFIED COMPLETE**

Stable `user_id`, username + password, roles `OWNER` / `ADMIN` / `STAFF` / `READ_ONLY`, states `PENDING` / `ACTIVE` / `DISABLED`, durable revocable user sessions, Owner migration from the bootstrap bridge, backend authorization, and explicit 403 behavior are deployed and runtime-verified. Inventory remains read-only.

### F7.2B — User Management — **VERIFIED COMPLETE**

Dedicated human-account surface with pending access requests, Owner approval/rejection, role assignment, disable/reactivate/session revoke, escalation boundaries, security/account events, reusable notification events, explicit Access Denied handling, and the signed-in drawer profile box are deployed and runtime-verified. Ordinary User Management does not grant/promote `OWNER`.

### F7.2C — Credential lifecycle — **VERIFIED COMPLETE**

Self-service username/password/recovery-email maintenance, password confirmation, verified-email recovery, automated Resend reset delivery, username-or-email Forgot password, Owner-assisted fallback reset, pending-access email verification, digest-only token persistence, credential/session invalidation, security/notification events, and Web product UI are deployed and verified.

The Owner may replace the initial bootstrap username `owner` through Account without changing the canonical `OWNER` role or stable `user_id`. Profile-image upload/edit remains separately deferred.

### F7.2D — AI Agent Management & delegated authority — **NEXT**

A dedicated **Owner-only** control plane for named `AI_AGENT` principals.

AI agents are not ordinary human users with copied roles. Owner configures:

- typed capability scope;
- Main Store / selected Sub Stores / all-store location scope;
- authority ceiling;
- delegated vs autonomous policy;
- read-only / propose-only / confirm-before-write / autonomous-within-preauthorized-scope behavior;
- revocation/disable state;
- which human users/roles may use shared features such as AI Chat.

`AI Agent Management` and global `Settings` are Owner-only. Agents cannot self-escalate or change security/control-plane policy.

For delegated action:

`effective_authority = human_authority ∩ agent_capability_scope ∩ location_scope ∩ operation_policy`

Agents are **not Sub-Store-only**. After the appropriate write/canonicality slices are authorized, Owner may grant an agent typed Main Store operations such as approved CMS reconciliation/price or batch workflows.

### F7.3 — Actor-aware Audit & Operation Ledger

Operational/database Audit is separate from User Management and Agent Management.

Actor classes: `HUMAN`, `AI_AGENT`, `SYSTEM`, `INTEGRATION`.

Meaningful operations retain actor/source/authority/location/outcome/affected-record provenance. Delegated AI actions retain the authorizing `user_id`; autonomous agent/system jobs retain their configured policy authority source. Committed historical operations use reversal/correction instead of silent destructive editing.

### F7.4 — Inventory Locations, Store Policy & Preferences

- exactly one Main Store;
- Owner may create any number of Sub Stores;
- product/lot balances are location-aware;
- initial transfer direction Main -> selected Sub Store;
- current `Daily Usage` source becomes future Stock Transfer evidence where source truth supports it;
- no invented historical Sub Store destinations;
- Owner-only reorder setting: `MAIN_STORE_ONLY` initially/default or `TOTAL_ACTIVE_STOCK`;
- durable cross-client preferences include default Calculator Sub Store, view mode, columns, filters, and calculator/receipt defaults.

### F7.5 — Smart Calculator & Receipts — calculation-only first

DB/API-backed item/lot/location search with same-name disambiguation, quantity/price, multiple items, extra fees, receiver/issuer/note, saved calculations, receipt history, print/PDF/export/share.

Normal Calculator use does not require a new Excel upload or column mapping. Owner batch-intake/import mapping remains a separate ingestion workflow.

`CALCULATE_ONLY` is first. Future `DISPENSE_FROM_SUB_STORE` becomes write-capable only after controlled-write authorization.

### F7.6 — Smart Analysis

Deterministic KPI/charts and drill-down for Stock Health, Transfer/Usage Trends, Expiry Risk, Reorder Outlook, Price Movement, and Data Quality. Main/Sub/Total views remain available and active reorder basis is explicit.

### F7.7 — Internal AI Assistant

Read-only first-party AI Chat grounded in typed backend tools. The Owner may enable this feature for Staff/Admin users. The assistant remains an identifiable `AI_AGENT`, and user role/location scope still limits effective authority. Future write tools reuse F7.2D/F7.3 rather than inventing a second authority path.

### F7.8 — Alerts & Notifications

Deterministic event generation first, optional AI explanation second. Examples: low stock, Sub Store refill pressure, expiry, unusual transfer/dispense patterns, data-quality problems, sync failures, and access/reset requests. One backend event is reusable across Web/Telegram/Flutter.

Resend email delivery is already proven for credential recovery. F7.8 may reuse the same event/delivery foundation for broader alerts, while Telegram delivery remains future work after secure account linking.

## F8 — External / Custom GPT read-only integration

Reuse approved typed reads/analytics with scoped/revocable agent/service identity. No raw DB/Sheet credentials and no writes.

## F9 — Controlled typed writes

Only after human identity, Agent Management, actor-aware Audit, location model, ledger/idempotency, and typed validation are stable.

Required path:

`Client/Agent -> typed API -> auth/RBAC/delegation -> agent capability + location scope -> validation/reconciliation policy -> idempotency -> atomic transaction -> actor-aware audit -> readback`

Candidate operations include approved Main Store CMS/metadata reconciliation, receipts/batch operations, Main->Sub transfer, reversal/correction, Smart Calculator Sub Store dispense, and later adjustments.

For AI writes, preserve the `$msa` low-friction policy: pre-authorized SAFE workflow classes may proceed; REVIEW/CONFLICT/NEW_UNMAPPED and high-risk cases require human review.

## F10 — Real workflow, fresh migration & Sheet sync validation

Validate the redesigned DB operations against the real Owner workflow before cutover. Keep batch-intake mapping separate from Smart Calculator, import a fresh migration candidate only when authorized, preserve historical ambiguity instead of guessing, compare Sheet workflow against backend shadow operations, and make the backend own Sheet mirror/sync orchestration.

## F11 — Canonical promotion

Requires explicit Owner approval plus fresh migration baseline, parity acceptance, backup/restore proof, location-aware workflow validation, actor/AI audit completeness, Sheet mirror/reconciliation confidence, and rollback/cutback procedure.

Only after promotion may PostgreSQL become operational SOT for the approved scope.

## Later client rollout

Telegram and Flutter reuse the same backend contracts and never become separate inventory truths. Flutter may use offline-tolerant caching for usability only.

Telegram account linking may later add recovery/notification delivery, but Telegram does not become account authority merely by carrying a message.

## Recommended execution order

1. F7.2A — Canonical multi-user identity — verified complete
2. F7.2B — User Management — verified complete
3. F7.2C — Credential lifecycle — verified complete
4. F7.2D — AI Agent Management & delegated authority — next
5. F7.3 — Actor-aware Audit / operation ledger
6. F7.4 — Inventory Locations, Store Policy & Preferences
7. F7.5 — Smart Calculator / receipts, calculation-only
8. F7.6 — Smart Analysis
9. F7.7 — Internal read-only AI Assistant
10. F7.8 — Alerts & Notifications
11. F8 — External/Custom GPT read-only integration
12. F9 — Controlled typed writes
13. F10 — Real workflow + fresh migration + Sheet sync validation
14. F11 — Canonical promotion
15. Telegram/Flutter rollout over proven contracts

## Immediate boundary

The next authorized implementation slice is **F7.2D AI Agent Management & delegated authority**. Do not implement F7.3 Audit, production inventory writes, AI inventory writes, store transfers, Smart Calculator deduction, Telegram/Flutter stock mutation, Sheet mirror conversion, or canonical promotion as part of F7.2D unless a strict prerequisite is separately authorized.

## Continuity rule

After every significant architecture decision, implementation slice, deployment/migration result, or next-work change, update `ROADMAP.md`, `NEW_CHAT_BOOTSTRAP.md`, `IMPLEMENTATION_PLAN.md`, and relevant canonical docs.
