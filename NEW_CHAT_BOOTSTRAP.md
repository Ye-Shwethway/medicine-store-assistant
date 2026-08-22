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
7. skill references when spreadsheet/UI work is involved
8. current repository/runtime evidence

Treat newer verified repository/runtime evidence as authoritative over remembered chat context.

## Authority boundary

The live Google workbook/source documents remain authoritative. PostgreSQL is deployed but **not canonical**.

The F6B staged batch is **test-only**. It is not an accepted migration baseline and must not be treated as the real dataset to promote later. A fresh real migration dataset will be imported only after the operational workflow and user-facing management UI are ready and explicitly approved.

## Deployment and owner-interaction workflow

Canonical flow: `test -> pull request -> main -> automatic VPS deployment for relevant runtime changes`.

- No normal manual VPS deployment command is required from the owner.
- No normal manual GitHub Actions deploy button is required.
- Do not require the owner to use Termux, SSH, tmux, shell commands, or other terminal steps for normal continuation.
- Bamboo/Bamboo Claw is not part of the normal MSA implementation, deployment, verification, or continuity workflow unless the owner explicitly re-authorizes it.
- Prefer connected tools, repository automation, repo-scoped self-hosted runner `msa-vps-runner-01`, and durable application-native/browser admin mechanisms.
- If a privileged VPS/runtime task cannot be completed through the normal automated path, design a safe product/admin/browser flow rather than falling back to repeated ad-hoc terminal instructions.
- Backend validation is path-aware and lightweight.
- Docs-only/unrelated changes do not deploy the VPS.
- Runtime secrets stay on the VPS.
- `.github/backend-deploy-result` records deployment status, source SHA, and workflow run ID.
- Normal backend deploy does **not** read/import the live Google workbook.
- Dashboard deploy verification checks both localhost and `https://inventory.drthorne.uk` public HTTPS paths.

## Verified checkpoints

F0, F1, Cloudflare HTTPS route, F2, F3, F4, F5, F5.1, F6A, F6C, and **F7.1** are verified complete.

F6B remains a verified **test-only** snapshot/staging exercise, not a migration baseline.

Current test batch:

- batch ID `be13d127-5045-4284-a088-0a0b9b024d76`
- rows 1646
- SAFE 1417
- REVIEW 222
- CONFLICT 0
- NEW_UNMAPPED 7
- `migration_baseline_accepted=false`
- `database_canonical=false`

Canonical F7.1 evidence:

`docs/operations/F7_1_WEB_DASHBOARD_FOUNDATION_VERIFICATION_2026-08-22.md`

## F7 Web Dashboard

Read before dashboard/auth work:

- `docs/architecture/F7_WEB_DASHBOARD.md`
- `docs/design/UI_UX_PRO_MAX_INTEGRATION.md`
- `docs/design/F7_2_AUTH_RBAC_DESIGN.md`
- `design-system/medicine-store-assistant/MASTER.md`
- `design-system/medicine-store-assistant/pages/dashboard.md`
- `docs/architecture/F2_SCHEMA_DECISION_PROPOSAL.md`

UI/UX Pro Max is pinned for this design cycle to upstream `nextlevelbuilder/ui-ux-pro-max-skill` commit `bc826e2267a36d98a2dcf5231e16c30ff546770f`.

Dashboard v2.4 remains the locked visual/interaction baseline. Preserve responsive sidebar/mobile drawer, visual sun/moon Light-Dark toggle, spreadsheet gridlines, Inventory→Overview path, row detail drawer, full-table focus mode, TEST DATA / DB NON-CANONICAL badges, and the read-only boundary.

### F7.1 verified deployment

Implementation PR #14:

- merge SHA `99b41c32c55d59e4acaafd44be77b78d93ed5889`
- deploy run `32568177813`

Public-route verification PR #15:

- merge SHA `e114ce9abcde30f727315eea0c4314a5047f1c29`
- deploy run `32568305770`
- deploy job `97020051556`
- evidence marker `0f9401baed9f950b1fb6abd507cc285f150f1c8b`

Verified runtime facts:

- `/dashboard` is deployed;
- dashboard session route is deployed;
- private dashboard BFF is fail-closed;
- public `https://inventory.drthorne.uk/dashboard` path verified by the VPS runner;
- dashboard auth password/session/tamper verifier passed;
- F6C shadow verifier passed;
- no live workbook import executed;
- no inventory write routes were added.

## Next authorized slice — F7.2 Authentication & Role-Based Access

F7.2 is explicitly an authentication/RBAC slice, not credential provisioning alone.

Locked design direction:

- dedicated `/dashboard/login` primary sign-in page;
- no public signup;
- roles `OWNER`, `ADMIN`, `STAFF`, `READ_ONLY`;
- backend policy is authoritative; hidden UI is not security;
- role-aware navigation/control visibility;
- explicit authenticated `403 / Access denied` state;
- `Audit & Access` becomes the future account/access-management surface;
- stable backend `user_id` is canonical human identity;
- disable/revoke accounts rather than delete historical actors;
- session expiry/sign-out return to login without exposing private data.

Bootstrap Owner secrets are now provisioned successfully on the protected VPS runtime. The temporary setup server and temporary files were removed after success. API restart completed and `/dashboard/api/session` reported `configured=true`; unauthenticated private dashboard reads returned HTTP 401. Owner login submission was captured for final verification. Do not mark the bootstrap public read path complete until normal runtime evidence confirms authenticated overview/rows/review reads, logout, and post-logout 401.

Runtime-only bootstrap values:

- `MSA_DASHBOARD_OWNER_PASSWORD_HASH`
- `MSA_DASHBOARD_SESSION_SECRET`

They are not the final multi-user credential store. Do not put them, the plaintext Owner password, or session material in Git/browser code/logs.

Authorized implementation order:

1. auth/RBAC canonical design + continuity docs;
2. secure bootstrap Owner secret provisioning — completed;
3. authenticated Owner public dashboard read verification — final verification pending;
4. dedicated login + canonical user/session/RBAC implementation;
5. OWNER / ADMIN / STAFF / READ_ONLY authorization verification.

F7.2 remains read-only. Google Sheets remains the operational source of truth.

## Safety boundary

Do not treat F6B test data as production migration truth. Do not begin production stock writes, database promotion, Telegram writes, Flutter rollout, Sheet mirror conversion, Custom GPT write Actions, or arbitrary permission editing without explicit authorization for those slices.

## Continuity rule

After significant architecture, implementation, deployment, migration, design-system, or next-work changes, update `ROADMAP.md`, this file, and relevant canonical docs.
