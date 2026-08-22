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

The F6B staged batch is **test-only** and not an accepted migration baseline.

## Deployment and owner-interaction workflow

Canonical flow: `test -> pull request -> main -> automatic VPS deployment for relevant runtime changes`.

- Do not require the owner to use Termux, SSH, tmux, shell commands, Bamboo/Bamboo Claw, or manual GitHub Actions for normal continuation.
- Prefer connected tools, repository automation, repo-scoped self-hosted runner `msa-vps-runner-01`, and durable browser/admin mechanisms.
- Runtime secrets stay on the VPS.
- Normal backend deploy does not read/import the live workbook.
- Deployment status is published to GitHub issue #26 (`MSA deployment status`) with source SHA/run ID/status so connected tooling can inspect the run and job logs directly.
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

The F7.2 bootstrap Owner flow is live-verified: dedicated login works, authenticated dashboard data reads work, logout returns to login, and the test snapshot remains intact. The temporary password-only Owner bridge is proven but is **not** the final multi-user credential model.

## Product direction

MSA is being developed as a multi-client intelligent operations system rather than only a database-backed spreadsheet replacement.

Humans, AI agents, integrations, and system jobs will eventually collaborate through the same typed backend across Web, Telegram, Flutter, internal AI, and Custom GPT clients.

The architecture must always preserve:

- canonical actor identity;
- server-side authorization/delegation;
- deterministic database truth;
- actor-aware operation provenance;
- no arbitrary SQL/client DB credentials;
- clear separation between calculated facts and AI interpretation.

## F7 Web Application roadmap

Read before current/future work:

- `docs/architecture/F7_WEB_DASHBOARD.md`
- `docs/design/UI_UX_PRO_MAX_INTEGRATION.md`
- `docs/design/F7_2_AUTH_RBAC_DESIGN.md`
- `docs/architecture/F7_3_ACTOR_AUDIT_AND_OPERATION_LEDGER.md`
- `docs/architecture/F7_4_F7_6_INTELLIGENCE_ARCHITECTURE.md`
- `design-system/medicine-store-assistant/MASTER.md`
- `design-system/medicine-store-assistant/pages/dashboard.md`
- `docs/architecture/F2_SCHEMA_DECISION_PROPOSAL.md`

Dashboard v2.4 remains the locked visual/interaction baseline.

## Next authorized slice — F7.2A canonical multi-user identity

Implement durable identity/session foundation before production writes:

- stable backend `user_id`;
- username + password;
- roles `OWNER`, `ADMIN`, `STAFF`, `READ_ONLY`;
- states `PENDING`, `ACTIVE`, `DISABLED`;
- user-bound revocable sessions;
- migrate/bootstrap existing Owner into canonical user model;
- normal Owner login becomes username + password;
- backend-enforced role authorization;
- explicit authenticated `403 / Access denied` state;
- disabled users lose protected access;
- inventory remains read-only.

Then continue:

### F7.2B — User Management

- separate `User Management` surface;
- Request access -> pending only;
- Owner approval/rejection and allowed role assignment;
- ADMIN cannot grant/promote OWNER;
- disable/reactivate/revoke behavior;
- in-product pending notifications;
- future Telegram approval notification mirrors backend operations.

### F7.2C — Credential lifecycle

- change password;
- owner-assisted forgotten-password/reset flow in v1;
- short-lived single-use reset;
- revoke old sessions after reset/disable.

### F7.3 — Actor-aware Audit / Operation Ledger

`Audit` is separate from User Management and reserved for store/database operational history.

Canonical actor classes are `HUMAN`, `AI_AGENT`, `SYSTEM`, and `INTEGRATION`.

Every meaningful operation should eventually carry stable operation identity plus actor/source provenance. When an AI agent acts for a human, the delegated/authorizing `user_id` must be retained so Audit can distinguish human actions from AI-assisted or autonomous actions.

Audit covers stock operations, corrections/reversals, imports/syncs, operation IDs, actor/client provenance, timestamps, outcomes, affected records, and relevant before/after or ledger references.

### F7.4 — Smart Analysis

Read-only deterministic analytics plus professional dashboard charts/KPIs.

Initial v1 modules:

- Stock Health
- Usage Trends
- Expiry Risk
- Reorder Outlook
- Price Movement
- Data Quality

Metrics must be reproducible from SQL/domain formulas/business rules and remain useful if AI is unavailable.

### F7.5 — Internal AI Assistant

Read-only conversational analysis grounded in typed backend analytics/tools.

The Assistant is an identifiable `AI_AGENT`, respects current-user RBAC scope, may explain/drill down/chart database facts, and never receives arbitrary SQL or raw DB credentials.

### F7.6 — Alerts & Notifications

Deterministic alert/event generation first, optional AI explanation second.

Initial direction includes low stock, expiry, unusual usage, data-quality/mapping problems, reconciliation/sync failures, and User Management access/reset notifications.

One backend event should later be reusable across Web, Telegram, Flutter, and other notification channels.

## Future integration/write sequence

- **F8**: external/Custom GPT read-only integration reusing approved read/analytics APIs.
- **F9**: first controlled typed write experiment after identity/RBAC/ledger/idempotency/actor-audit are verified.
- **F10**: dual real-workflow + Google Sheet sync/mirror validation.
- **F11**: explicit canonical promotion only after fresh migration, parity, backup/restore, audit, sync, and rollback proof.

Clients and AI agents must use typed Inventory API operations. No arbitrary SQL, no direct LLM-to-DB credentials, and no direct LLM-to-Sheet mutation.

## Safety boundary

Do not treat F6B test data as production migration truth. Do not begin production inventory writes, DB promotion, Telegram inventory writes, Flutter rollout, Sheet mirror conversion, or Custom GPT write Actions without explicit authorization for the corresponding slice.

## Continuity rule

After significant architecture, implementation, deployment, migration, design-system, or next-work changes, update `ROADMAP.md`, this file, `IMPLEMENTATION_PLAN.md`, and relevant canonical docs.
