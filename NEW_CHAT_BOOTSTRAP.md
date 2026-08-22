# Medicine Store Assistant — New Chat Bootstrap

Use this file for project-development continuity and memory reconciliation in a fresh chat.

## Canonical repository

`https://github.com/Ye-Shwethway/medicine-store-assistant`

## Reconciliation order

1. `AGENTS.md`
2. `NEW_CHAT_BOOTSTRAP.md`
3. `ROADMAP.md`
4. `IMPLEMENTATION_PLAN.md`
5. `docs/architecture/README.md`
6. task-relevant architecture/operations/design docs
7. current repository/runtime evidence

Treat newer verified repository/runtime evidence as authoritative over remembered chat context.

## Authority boundary

The live Google workbook/source documents remain authoritative. PostgreSQL is deployed but **not canonical**.

The F6B staged batch remains **test-only** and not an accepted migration baseline.

No production inventory write, DB promotion, Telegram/Flutter stock mutation, Sheet mirror conversion, or Custom GPT write Action is authorized merely by this bootstrap.

## Deployment and owner-interaction workflow

Canonical flow: `test -> pull request -> main -> automatic VPS deployment for relevant runtime changes`.

- Do not require the Owner to use Termux, SSH, tmux, shell commands, Bamboo/Bamboo Claw, or manual GitHub Actions for normal continuation.
- Prefer connected tools, repository automation, repo-scoped self-hosted runner `msa-vps-runner-01`, and durable browser/admin mechanisms.
- Runtime secrets stay on the VPS.
- Normal backend deploy does not read/import the live workbook.
- Deployment status is published to GitHub issue #26 (`MSA deployment status`) with source SHA/run ID/status so connected tooling can inspect runs/jobs directly.
- Dashboard deployment verification checks localhost and `https://inventory.drthorne.uk`.

## Verified checkpoints

F0, F1, Cloudflare HTTPS route, F2, F3, F4, F5, F5.1, F6A, F6C, and F7.1 are verified complete.

F6B remains test-only:

- batch ID `be13d127-5045-4284-a088-0a0b9b024d76`
- rows 1646
- SAFE 1417
- REVIEW 222
- CONFLICT 0
- NEW_UNMAPPED 7
- `migration_baseline_accepted=false`
- `database_canonical=false`

The bootstrap Owner flow is live-verified: dedicated login works, authenticated dashboard data reads work, logout returns to login, and the test snapshot remains intact. The password-only Owner bridge is proven but is **not** the final multi-user credential model.

## Product direction

MSA is a multi-client intelligent store-operations platform rather than only a database-backed spreadsheet replacement.

Humans, AI agents, integrations, and system jobs will eventually collaborate through the same typed backend across Web, Telegram, Flutter, internal AI, Custom GPT, and scheduled jobs.

Preserve:

- canonical actor identity;
- server-side RBAC and location scope;
- explicit AI/service delegation;
- deterministic database truth;
- actor-aware operation provenance;
- no arbitrary SQL/client DB credentials;
- clear separation between calculated facts and AI interpretation.

## Canonical current docs

Read before current/future work:

- `IMPLEMENTATION_PLAN.md`
- `ROADMAP.md`
- `docs/architecture/F7_WEB_DASHBOARD.md`
- `docs/design/UI_UX_PRO_MAX_INTEGRATION.md`
- `docs/design/F7_2_AUTH_RBAC_DESIGN.md`
- `docs/architecture/F7_3_ACTOR_AUDIT_AND_OPERATION_LEDGER.md`
- `docs/architecture/F7_4_F7_8_STORE_AND_INTELLIGENCE_ARCHITECTURE.md`
- `design-system/medicine-store-assistant/MASTER.md`
- `design-system/medicine-store-assistant/pages/dashboard.md`
- `docs/architecture/F2_SCHEMA_DECISION_PROPOSAL.md`

`docs/architecture/F7_4_F7_6_INTELLIGENCE_ARCHITECTURE.md` is superseded.

## Next authorized implementation sequence

### F7.2A — Canonical multi-user identity — **NEXT**

- stable backend `user_id`;
- username + password;
- roles `OWNER`, `ADMIN`, `STAFF`, `READ_ONLY`;
- states `PENDING`, `ACTIVE`, `DISABLED`;
- user-bound revocable sessions;
- migrate/bootstrap current Owner into canonical user model;
- normal Owner login becomes username + password;
- backend-enforced authorization;
- explicit authenticated 403 state;
- inventory stays read-only.

### F7.2B — User Management

- separate `User Management` surface;
- Request access -> pending only;
- Owner approval/rejection and allowed role assignment;
- ADMIN cannot grant/promote OWNER;
- disable/reactivate/revoke;
- security events;
- reusable pending-request notification event for later Telegram/Flutter delivery.

### F7.2C — Credential lifecycle

- change password;
- Owner-assisted forgotten-password/reset v1;
- short-lived single-use reset;
- revoke old sessions after reset/disable.

### F7.3 — Actor-aware Audit / Operation Ledger

Audit is store/database operational history, separate from User Management.

Actor classes: `HUMAN`, `AI_AGENT`, `SYSTEM`, `INTEGRATION`.

Meaningful operations retain stable operation identity plus actor/client/authority/outcome provenance. When AI acts for a human, retain the authorizing `user_id`.

### F7.4 — Inventory Locations, Store Policy & Preferences

- exactly one Main Store;
- Owner may create any number of Sub Stores;
- location-aware product/lot balances;
- Main -> Sub transfer model;
- current `Daily Usage` is future Stock Transfer source evidence, not assumed end-customer usage;
- Owner reorder policy: `MAIN_STORE_ONLY` (initial/default) or `TOTAL_ACTIVE_STOCK`;
- user preferences include default location/Calculator Sub Store, card/table view, columns, filters, and calculator/receipt defaults.

### F7.5 — Smart Calculator / Receipts

Calculation-only first.

- DB-backed item/lot/location search;
- no separate Excel upload or Calculator column mapping;
- same-name disambiguation;
- quantity/price/multiple items/extra fees;
- receiver/issuer/note;
- saved calculations and receipt history;
- print/PDF/export/share;
- `CALCULATE_ONLY` now;
- future `DISPENSE_FROM_SUB_STORE` only after controlled-write authorization;
- selected/default Sub Store comes from backend preference/scope;
- photo/AI scan may create drafts but never auto-commit ambiguous inventory operations.

Owner batch intake/import mapping remains a separate ingestion workflow.

### F7.6 — Smart Analysis

Deterministic charts/KPIs for Stock Health, Transfer/Usage Trends, Expiry Risk, Reorder Outlook, Price Movement, and Data Quality. Support Main/Sub/Total views and clearly show active reorder policy.

### F7.7 — Internal AI Assistant

Read-only typed-tool assistant grounded in backend truth. Identifiable `AI_AGENT`; respects user role/location scope; no arbitrary SQL or stock writes.

### F7.8 — Alerts & Notifications

Deterministic events first, optional AI explanation second. Reusable across Web, Telegram, Flutter.

## Later sequence

- **F8** — external/Custom GPT read-only integration.
- **F9** — controlled typed writes after identity/audit/location/idempotency foundations; candidate commands include Main->Sub transfer and Smart Calculator Sub Store dispense.
- **F10** — real workflow + fresh migration + Google Sheet sync/mirror validation; historical ambiguity must be surfaced, not guessed.
- **F11** — explicit canonical DB promotion after parity, backup/restore, location-aware workflow, audit, sync, and rollback proof.
- later Telegram/Flutter rollout reuses the same backend contracts; Flutter may cache for offline tolerance but does not become a second canonical inventory database.

## Immediate work boundary

Implementation resumes from **F7.2A canonical multi-user identity**. Then F7.2B User Management and F7.2C credential lifecycle. Do not jump ahead to store-location writes, Smart Calculator stock deduction, AI writes, Telegram/Flutter stock mutation, or canonical promotion.

## Continuity rule

After significant architecture, implementation, deployment, migration, design-system, or next-work changes, update `ROADMAP.md`, this file, `IMPLEMENTATION_PLAN.md`, and relevant canonical docs.