# Medicine Store Assistant — Project Roadmap

Status: **F0/F1/F2/F3/F4/F5/F5.1/F6A/F6C/F7.1 verified complete; F6B remains test-only; bootstrap Owner login/read/logout verified; F7.2A canonical multi-user identity is next; PostgreSQL remains non-canonical**

The live Google workbook/source documents remain operationally authoritative. The current staged F6B snapshot is **test-only** and is not an accepted migration baseline. A fresh real migration dataset will be imported later only after the operational workflow, location model, and user-facing management surfaces are ready and explicitly approved.

## Delivery policy

Canonical flow: `test -> pull request -> main -> automatic VPS deploy for relevant runtime changes`.

Normal continuation does not require manual VPS commands, Termux/SSH/tmux, Bamboo/Bamboo Claw, or a manual Actions deploy button. Prefer connected tools, repository automation, the repo-scoped self-hosted runner, and durable browser/admin mechanisms.

Runtime secrets remain only on the VPS. Normal backend deployment must not read/import the live workbook.

Deployment status is published to GitHub issue #26 (`MSA deployment status`) so connected tooling can inspect deployment success/failure and descend into run/job logs without manual owner inspection.

## Product direction

MSA is a multi-client intelligent store-operations platform, not merely a database-backed spreadsheet replacement.

Future clients and actors include:

- Web dashboard;
- Telegram;
- Flutter;
- internal MSA AI Assistant;
- Custom GPT / ChatGPT integrations;
- scheduled/system jobs;
- external integrations.

All clients use the same typed backend contracts, identity/RBAC, store-location scope, preferences, audit, analytics, alerts, calculator/receipt flows, and later controlled inventory operations.

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
- F6B read-only live-workbook test snapshot — staging exercise only; not a migration baseline
- F6C authenticated shadow read API — verified complete 2026-08-22
- F7.1 read-only Web Dashboard foundation — verified complete 2026-08-22
- F7.2 bootstrap Owner credential + public login/read/logout flow — verified complete as a temporary bridge

## Test-only F6B snapshot

- batch ID `be13d127-5045-4284-a088-0a0b9b024d76`
- rows **1,646**
- SAFE **1,417**
- REVIEW **222**
- NEW_UNMAPPED **7**
- CONFLICT **0**
- `migration_baseline_accepted=false`
- `database_canonical=false`

This batch is only for read/UI/shadow verification.

## Canonical F7 architecture docs

- `docs/architecture/F7_WEB_DASHBOARD.md`
- `docs/design/UI_UX_PRO_MAX_INTEGRATION.md`
- `docs/design/F7_2_AUTH_RBAC_DESIGN.md`
- `docs/architecture/F7_3_ACTOR_AUDIT_AND_OPERATION_LEDGER.md`
- `docs/architecture/F7_4_F7_8_STORE_AND_INTELLIGENCE_ARCHITECTURE.md`
- `design-system/medicine-store-assistant/MASTER.md`
- `design-system/medicine-store-assistant/pages/dashboard.md`

`docs/architecture/F7_4_F7_6_INTELLIGENCE_ARCHITECTURE.md` is superseded and retained only as a historical pointer.

## F7 — Application foundation before production writes

### F7.1 — Read-only Web Dashboard — verified complete

Public HTTPS dashboard, private BFF, dedicated bootstrap Owner login, authenticated test data reads, logout, and test/non-canonical indicators are verified.

### F7.2A — Canonical multi-user identity — **NEXT**

Implement stable `user_id`, username + password, roles `OWNER` / `ADMIN` / `STAFF` / `READ_ONLY`, states `PENDING` / `ACTIVE` / `DISABLED`, revocable user sessions, Owner migration from the bootstrap bridge, backend authorization, and explicit 403 behavior.

Inventory remains read-only.

### F7.2B — User Management

Dedicated User Management surface with access requests, Owner approval/rejection, role assignment, disable/reactivate/revoke, escalation boundaries, security events, and reusable notification events.

ADMIN cannot grant/promote OWNER.

### F7.2C — Credential lifecycle

Change password, Owner-assisted forgotten-password reset, one-time reset tokens, and session revocation after reset/disable.

### F7.3 — Actor-aware Audit & Operation Ledger

Operational/database audit is separate from User Management.

Canonical actor classes:

- `HUMAN`
- `AI_AGENT`
- `SYSTEM`
- `INTEGRATION`

Meaningful operations retain actor/source/authority/outcome/affected-record provenance. AI actions performed for a human retain the authorizing `user_id`. Committed historical operations use reversal/correction rather than silent destructive edits.

### F7.4 — Inventory Locations, Store Policy & Preferences

Canonical location model:

- exactly **one Main Store**;
- Owner may create any number of Sub Stores;
- product/lot balances are location-aware;
- initial transfer direction is Main Store -> selected Sub Store;
- current `Daily Usage` source is treated as future historical Stock Transfer evidence where supported by source truth;
- no silent invention of historical Sub Store destinations.

Owner-configurable reorder basis:

- `MAIN_STORE_ONLY` — initial/default mode;
- `TOTAL_ACTIVE_STOCK` — Main Store + all active Sub Stores.

Owner can switch the policy through Settings without formula/code changes.

Durable user preferences include default location/Calculator Sub Store, view mode, column visibility/order/density, saved filters, and calculator/receipt defaults.

### F7.5 — Smart Calculator & Receipts — calculation-only first

Restore the useful Flutter calculator concept as a backend-backed first-class surface.

Normal Calculator use reads product/lot/location data directly from the DB/API and **does not require Excel upload or manual column mapping**.

Capabilities:

- item search and same-name disambiguation;
- quantities and prices;
- multiple items;
- extra fees;
- receiver/customer, issuer, note;
- saved calculations;
- receipt history;
- print/PDF/export/share.

Initial mode is `CALCULATE_ONLY` with no stock mutation.

Future `DISPENSE_FROM_SUB_STORE` uses the selected or saved default Sub Store and becomes write-capable only after controlled-write authorization.

Owner batch-intake/import mapping remains a separate ingestion workflow.

### F7.6 — Smart Analysis

Deterministic professional analytics with charts/KPIs and drill-down.

Initial modules:

1. Stock Health
2. Transfer / Usage Trends
3. Expiry Risk
4. Reorder Outlook
5. Price Movement
6. Data Quality

Analysis can show Main Store, individual Sub Stores, and Total active stock. Reorder views clearly identify which Owner policy is active.

### F7.7 — Internal AI Assistant

Read-only first-party conversational analysis grounded in typed backend tools. The Assistant is an identifiable `AI_AGENT`, respects current-user RBAC/location scope, can explain/drill down/chart facts, and receives no arbitrary SQL access.

A future photo/scan-to-calculation flow may build a Smart Calculator draft, but ambiguous item identity requires human confirmation and AI/OCR never auto-commits inventory.

### F7.8 — Alerts & Notifications

Deterministic event generation first, optional AI explanation second.

Examples include low stock, Sub Store refill pressure, expiry, unusual transfer/dispense patterns, data-quality issues, sync failures, and User Management access/reset requests.

One backend event should be reusable across Web, Telegram, and Flutter.

## F8 — External / Custom GPT read-only integration

Reuse approved typed read/analytics interfaces. Read-only first, scoped/revocable auth, no raw DB/Sheet credentials.

## F9 — Controlled typed write foundation

Only after identity, location, ledger/idempotency, and actor-aware audit are verified.

Required path:

`Client/Agent -> typed API -> auth/RBAC/location scope/delegation -> validation -> idempotency -> atomic DB transaction -> actor-aware audit -> readback`

Candidate commands include Main -> Sub transfer, transfer reversal/correction, and Smart Calculator Sub Store dispense. Technical write success does not itself authorize production canonicality.

## F10 — Real workflow, fresh migration & Sheet sync validation

- Owner batch-intake workflow remains separate from Calculator;
- import a fresh migration candidate only when authorized;
- reinterpret supported historical `Daily Usage` as Stock Transfer source evidence;
- surface historical destination ambiguity instead of guessing;
- compare real Sheet workflow against backend shadow operations;
- backend owns Sheet mirror/sync orchestration;
- clients/AI never write directly to Sheets;
- observable retry/idempotency/reconciliation behavior.

No automatic cutover.

## F11 — Canonical promotion

Requires explicit Owner approval plus fresh migration baseline, parity acceptance, backup/restore proof, location-aware workflow validation, actor-aware audit completeness, Sheet mirror/reconciliation confidence, and rollback/cutback procedure.

## Later client rollout

Telegram and Flutter are clients over the same backend, not separate inventory truths.

Flutter may later provide mobile-optimized card/table views, Smart Calculator, receipt/share/print, preferences, alerts, and optional offline-tolerant caching without creating a second canonical inventory database.

## Recommended execution order

1. F7.2A — Canonical multi-user identity
2. F7.2B — User Management
3. F7.2C — Credential lifecycle
4. F7.3 — Actor-aware Audit / operation ledger
5. F7.4 — Inventory Locations, Store Policy & Preferences
6. F7.5 — Smart Calculator / receipts, calculation-only
7. F7.6 — Smart Analysis
8. F7.7 — Internal read-only AI Assistant
9. F7.8 — Alerts & Notifications
10. F8 — External/Custom GPT read-only integration
11. F9 — Controlled typed writes
12. F10 — Real workflow + fresh migration + Sheet sync validation
13. F11 — Canonical promotion
14. Telegram/Flutter rollout over proven contracts

## Safety boundary

Do not treat F6B test data as production migration truth. Do not begin production inventory writes, DB promotion, Telegram/Flutter stock mutation, Sheet mirror conversion, or Custom GPT write Actions until the corresponding slice is explicitly authorized.

## Continuity rule

After every significant architecture decision, implementation slice, deployment/migration result, or next-work change, update `ROADMAP.md`, `NEW_CHAT_BOOTSTRAP.md`, `IMPLEMENTATION_PLAN.md`, and relevant canonical docs.