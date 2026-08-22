# Medicine Store Assistant — Project Roadmap

Status: **F0/F1/F2/F3/F4/F5/F5.1/F6A/F6C/F7.1 verified complete; F6B remains test-only; F7.2 Authentication & RBAC next; PostgreSQL remains non-canonical**

The live Google workbook/source documents remain operationally authoritative. The current staged F6B snapshot is **test-only** and is **not an accepted migration baseline**. A fresh real migration dataset will be imported later only after the operational workflow and user-facing management UI are ready and explicitly approved.

## Delivery policy

Canonical flow: `test -> pull request -> main -> automatic VPS deploy for relevant runtime changes`.

Validation is path-aware and lightweight. Docs-only changes do not deploy the VPS. Normal continuation does not require manual VPS commands or a manual Actions deploy button. Runtime secrets remain only on the VPS. Normal backend deployment must **not** read/import the live workbook.

Owner-interaction policy is now explicit:

- Bamboo/Bamboo Claw is **not part of the normal MSA implementation, deployment, verification, or continuity workflow** unless the owner explicitly re-authorizes it.
- Do not require the owner to use Termux, SSH, tmux, shell commands, or manual GitHub Actions for normal project continuation.
- Prefer connected tools, repository automation, the existing self-hosted runner, and durable application-native/browser admin flows.
- If privileged runtime setup cannot be completed through the automated path, build a safe browser/admin mechanism instead of repeated ad-hoc terminal steps.

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
- F6B read-only live-workbook test snapshot — verified staging exercise only; not a migration baseline
- F6C authenticated shadow read API — verified complete 2026-08-22
- **F7.1 read-only Web Dashboard foundation — verified complete 2026-08-22**

Canonical evidence:

- `docs/operations/F4_SYNTHETIC_LEDGER_VERIFICATION_2026-08-22.md`
- `docs/operations/F5_F5_1_CATALOGUE_VERIFICATION_2026-08-22.md`
- `docs/operations/F6A_SHADOW_MIGRATION_VERIFICATION_2026-08-22.md`
- `docs/operations/F6B_LIVE_SHADOW_IMPORT_VERIFICATION_2026-08-22.md`
- `docs/operations/F6C_SHADOW_READ_API_VERIFICATION_2026-08-22.md`
- `docs/operations/F7_1_WEB_DASHBOARD_FOUNDATION_VERIFICATION_2026-08-22.md`

## Test-only F6B snapshot

Current test dataset remains unchanged:

- batch ID `be13d127-5045-4284-a088-0a0b9b024d76`
- rows **1,646**
- SAFE **1,417**
- REVIEW **222**
- NEW_UNMAPPED **7**
- CONFLICT **0**
- `migration_baseline_accepted=false`
- `database_canonical=false`

This batch is for read-path/UI testing only. It must not drive canonical reconciliation or promotion decisions.

## F7 — Web Dashboard

UI/UX Pro Max remains the design-intelligence reference, pinned for this design cycle to upstream `bc826e2267a36d98a2dcf5231e16c30ff546770f`.

Canonical dashboard docs:

- `docs/architecture/F7_WEB_DASHBOARD.md`
- `docs/design/UI_UX_PRO_MAX_INTEGRATION.md`
- `docs/design/F7_2_AUTH_RBAC_DESIGN.md`
- `design-system/medicine-store-assistant/MASTER.md`
- `design-system/medicine-store-assistant/pages/dashboard.md`

Dashboard v2.4 remains the locked implementation baseline: responsive sidebar/mobile drawer, visual sun/moon Light-Dark toggle, spreadsheet gridlines, Inventory→Overview return path, item detail drawer, full-table focus mode, TEST DATA / DB NON-CANONICAL indicators, and no write affordances.

### F7.1 — verified complete

Implementation PR #14 merged at `99b41c32c55d59e4acaafd44be77b78d93ed5889`; automatic deploy run `32568177813` succeeded.

Public verification PR #15 merged at `e114ce9abcde30f727315eea0c4314a5047f1c29`; automatic deploy run `32568305770` succeeded. Deployment marker: `0f9401baed9f950b1fb6abd507cc285f150f1c8b`.

Verified:

- FastAPI dashboard shell at `/dashboard` and `/` redirect;
- server-side BFF routes for overview, rows, review reasons;
- fail-closed owner session architecture;
- no browser exposure of the F3 Bearer credential;
- dashboard auth primitive/tamper checks PASS;
- local dashboard/session/private gate PASS;
- public Cloudflare route `https://inventory.drthorne.uk` dashboard/session checks PASS;
- unauthenticated public private-data read returns fail-closed HTTP 503 while owner credentials are unprovisioned;
- F6C test-only data remained unchanged;
- no live Google workbook import executed.

### F7.2 — next authorized slice: Authentication & Role-Based Access

F7.2 is explicitly broader than owner-password provisioning.

Design decisions are locked in `docs/design/F7_2_AUTH_RBAC_DESIGN.md`:

- dedicated `/dashboard/login` page as the primary login UX;
- no public self-registration;
- roles `OWNER`, `ADMIN`, `STAFF`, `READ_ONLY` from the approved F2 model;
- role-aware navigation/control visibility with backend authorization as the source of truth;
- explicit authenticated `403 / Access denied` state;
- session expiry and sign-out return to login;
- `Audit & Access` becomes the future account/access-management surface;
- stable backend `user_id` remains canonical human identity;
- deactivate/revoke accounts rather than delete historical actors.

The bootstrap Owner runtime credentials have now been provisioned successfully on the protected VPS runtime. The temporary setup mechanism completed and was removed. Application restart and owner-login verification were then initiated; canonical completion evidence must still come from the normal repository/runtime verification path before marking the whole F7.2 bootstrap verification complete.

The existing runtime values remain a **bootstrap Owner bridge**:

- `MSA_DASHBOARD_OWNER_PASSWORD_HASH`
- `MSA_DASHBOARD_SESSION_SECRET`

They are not the final multi-user credential store.

Implementation sequence:

1. auth/RBAC design and continuity docs;
2. bootstrap Owner runtime secret provisioning — completed;
3. authenticated Owner public dashboard read verification — in verification;
4. implement dedicated login UX and canonical user/session/RBAC foundation;
5. verify role behavior and access-denied states.

F7.2 remains **read-only** and does not authorize inventory writes, Sheet mutation, database promotion, or arbitrary permission editing.

## Safety boundary

Do not treat F6B test data as production migration truth. Do not begin production stock writes, database promotion, Telegram writes, Flutter rollout, Sheet mirror conversion, or Custom GPT write Actions without explicit authorization for those slices.

## Continuity rule

After every significant architecture decision, implementation slice, deployment/migration result, or next-work change, update `ROADMAP.md`, `NEW_CHAT_BOOTSTRAP.md`, and relevant canonical architecture/operations docs.
