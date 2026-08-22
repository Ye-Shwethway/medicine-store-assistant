# Medicine Store Assistant — Project Roadmap

Status: **F0/F1/F2/F3/F4/F5/F5.1/F6A/F6C/F7.1/F7.2A verified complete; F6B remains test-only; F7.2B User Management is next; PostgreSQL remains non-canonical**

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
- `docs/architecture/F7_2D_AI_AGENT_MANAGEMENT.md`
- `docs/architecture/F7_3_ACTOR_AUDIT_AND_OPERATION_LEDGER.md`
- `docs/architecture/F7_4_F7_8_STORE_AND_INTELLIGENCE_ARCHITECTURE.md`
- `design-system/medicine-store-assistant/MASTER.md`
- `design-system/medicine-store-assistant/pages/dashboard.md`

## F7 — Application and control-plane foundation

### F7.2A — Canonical multi-user identity — **VERIFIED COMPLETE**

Stable `user_id`, username + password, roles `OWNER` / `ADMIN` / `STAFF` / `READ_ONLY`, states `PENDING` / `ACTIVE` / `DISABLED`, durable revocable user sessions, Owner migration from the bootstrap bridge, backend authorization, and explicit 403 behavior are deployed and runtime-verified. Inventory remains read-only.

### F7.2B — User Management — **NEXT**

Dedicated human-account surface with access requests, Owner approval/rejection, role assignment, disable/reactivate/revoke, escalation boundaries, security events, and reusable notification events. ADMIN cannot grant/promote OWNER.

### F7.2C — Credential lifecycle

Change password, Owner-assisted forgotten-password reset, short-lived one-time reset, and session revocation after reset/disable.

### F7.2D — AI Agent Management & delegated authority

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

## Recommended execution order

1. F7.2A — Canonical multi-user identity — verified complete
2. F7.2B — User Management — next
3. F7.2C — Credential lifecycle
4. F7.2D — AI Agent Management & delegated authority
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

The next authorized implementation slice is **F7.2B User Management**. Do not implement F7.2C credential lifecycle, F7.2D AI Agent Management, F7.3 Audit, production inventory writes, AI writes, store transfers, Smart Calculator deduction, Telegram/Flutter stock mutation, or canonical promotion as part of F7.2B unless a strict prerequisite is separately authorized.

## Continuity rule

After every significant architecture decision, implementation slice, deployment/migration result, or next-work change, update `ROADMAP.md`, `NEW_CHAT_BOOTSTRAP.md`, `IMPLEMENTATION_PLAN.md`, and relevant canonical docs.
