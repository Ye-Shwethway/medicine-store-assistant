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

The F7.2 bootstrap Owner flow is now live-verified: dedicated login works, authenticated dashboard data reads work, logout returns to login, and the test snapshot remains intact. The temporary password-only Owner bridge is therefore proven but is **not** the final multi-user credential model.

## F7 Web Dashboard and identity

Read before auth/user-management work:

- `docs/architecture/F7_WEB_DASHBOARD.md`
- `docs/design/UI_UX_PRO_MAX_INTEGRATION.md`
- `docs/design/F7_2_AUTH_RBAC_DESIGN.md`
- `design-system/medicine-store-assistant/MASTER.md`
- `design-system/medicine-store-assistant/pages/dashboard.md`
- `docs/architecture/F2_SCHEMA_DECISION_PROPOSAL.md`

Dashboard v2.4 remains the locked visual/interaction baseline.

## Next authorized slice — F7.2A canonical multi-user identity

Implement the durable identity/session foundation before any production write capability:

- stable backend `user_id`;
- username + password;
- roles `OWNER`, `ADMIN`, `STAFF`, `READ_ONLY`;
- states `PENDING`, `ACTIVE`, `DISABLED`;
- user-bound revocable sessions;
- migrate/bootstrap the existing Owner into the canonical user model;
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

### F7.3 — Audit

`Audit` is separate from User Management and is reserved for store/database operational history: stock operations, corrections/reversals, imports/syncs, operation IDs, actor/client provenance, timestamps, outcomes, and relevant before/after references.

## Future write/sync sequence

- **F8**: Custom GPT/private API read-only experiment.
- **F9**: first controlled typed write experiment after RBAC/ledger/idempotency/audit are verified.
- **F10**: dual real-workflow + Google Sheet sync/mirror validation.
- **F11**: explicit canonical promotion only after fresh migration, parity, backup/restore, audit, sync, and rollback proof.

Clients such as Web, Telegram, ChatGPT/Custom GPT, and Flutter must use typed Inventory API operations. No arbitrary SQL, no direct LLM-to-DB credentials, and no direct LLM-to-Sheet mutation.

## Safety boundary

Do not treat F6B test data as production migration truth. Do not begin production inventory writes, DB promotion, Telegram inventory writes, Flutter rollout, Sheet mirror conversion, or Custom GPT write Actions without explicit authorization for the corresponding slice.

## Continuity rule

After significant architecture, implementation, deployment, migration, design-system, or next-work changes, update `ROADMAP.md`, this file, `IMPLEMENTATION_PLAN.md`, and relevant canonical docs.
