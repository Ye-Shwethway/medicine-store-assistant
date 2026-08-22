# Medicine Store Assistant — Project Roadmap

Status: **F0/F1/F2/F3/F4/F5/F5.1/F6A/F6C verified complete; F6B remains test-only; F7 Web Dashboard implementation active; PostgreSQL remains non-canonical**

The live Google workbook/source documents remain operationally authoritative. The current staged F6B snapshot is **test-only** and is **not an accepted migration baseline**. A fresh real migration dataset will be imported later only after the operational workflow and user-facing management UI are ready and explicitly approved.

## Delivery policy

Canonical flow: `test -> pull request -> main -> automatic VPS deploy for relevant runtime changes`.

Validation is path-aware and lightweight. Docs-only changes do not run the backend suite or deploy the VPS. Normal continuation does not require manual VPS commands or a manual Actions deploy button. Runtime secrets remain only on the VPS.

Normal backend deployment must **not** read/import the live workbook. Live snapshot import is an explicit test/migration operation only.

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

Canonical evidence:

- `docs/operations/F4_SYNTHETIC_LEDGER_VERIFICATION_2026-08-22.md`
- `docs/operations/F5_F5_1_CATALOGUE_VERIFICATION_2026-08-22.md`
- `docs/operations/F6A_SHADOW_MIGRATION_VERIFICATION_2026-08-22.md`
- `docs/operations/F6B_LIVE_SHADOW_IMPORT_VERIFICATION_2026-08-22.md`
- `docs/operations/F6C_SHADOW_READ_API_VERIFICATION_2026-08-22.md`

## Test-only F6B snapshot

Verified source commit `34b169c56422454b9a919936689c3088a9c4ebfc` via GitHub Actions run `32549738838` staged one read-only snapshot from `Medicine Store Cloud` into shadow PostgreSQL.

Test snapshot summary:

- rows: **1,646**
- `SAFE`: **1,417**
- `REVIEW`: **222**
- `NEW_UNMAPPED`: **7**
- `CONFLICT`: **0**
- source hash: `cfe4c24201bbe9f519189572f0c4c1988a9785e6fb0ca3e8f9630f5ca0417192`

This batch is for read-path testing only. It must not drive canonical reconciliation or promotion decisions.

## F6C verified read-only inspection

Verified deployed source commit: `9f706da4832c08f10b1a8d694273f8f48412570a` via GitHub Actions run `32550437296`.

Verified behavior:

- normal backend deploy executed with **no live workbook import**;
- existing test-only batch provenance/classification summary verified;
- `GET /v1/shadow/batches` registered;
- `GET /v1/shadow/batches/{migration_batch_id}` registered;
- `GET /v1/shadow/rows` registered;
- `GET /v1/shadow/review-reasons` registered;
- anonymous shadow access returns HTTP 401;
- API responses state `migration_baseline_accepted:false` and `database_canonical:false`;
- `/health` and `/ready` green at migration `0004_shadow`.

## F7 — Web Dashboard

User-facing web management is now the active implementation direction. The existing F6B/F6C test dataset remains the only dataset used for dashboard workflow development.

UI/UX Pro Max is the design-intelligence reference, pinned for this design cycle to upstream commit `bc826e2267a36d98a2dcf5231e16c30ff546770f` from `nextlevelbuilder/ui-ux-pro-max-skill`.

Canonical dashboard docs:

- `docs/architecture/F7_WEB_DASHBOARD.md`
- `docs/design/UI_UX_PRO_MAX_INTEGRATION.md`
- `design-system/medicine-store-assistant/MASTER.md`
- `design-system/medicine-store-assistant/pages/dashboard.md`

The owner approved **Dashboard v2.4** as the locked implementation baseline. Required behaviors include responsive sidebar/mobile drawer navigation, Light/Dark visual sun-moon toggle, spreadsheet-style table gridlines, Inventory→Overview return path, item detail drawer, full-table focus mode, persistent TEST DATA / DB NON-CANONICAL indicators, and no write affordances.

### F7.1 — Read-only dashboard foundation — implementation active

Current implementation on `test` includes:

- FastAPI-served dashboard shell at `/dashboard` with `/` redirect;
- HTML/CSS/vanilla-JS implementation of the approved v2.4 interaction model;
- server-side dashboard BFF routes for overview, rows, and review reasons;
- fail-closed owner authentication using PBKDF2-SHA256 password hash + HMAC-signed HttpOnly/Secure/SameSite session cookie;
- no browser exposure of the existing F3 Bearer service credential;
- dashboard auth disabled automatically when required runtime secrets are absent;
- deterministic dashboard auth verification in deployment;
- dashboard shell/session/private-gate checks in automatic VPS deployment;
- CI JavaScript syntax validation;
- no live workbook import and no inventory write routes.

F7.1 is **not verified complete until PR validation, main merge, automatic VPS deploy, public HTTPS shell verification, and private data-gate verification are green**.

### F7.2 — Owner credential provisioning + authenticated live read verification

After F7.1 is deployed, provision these values only in the protected VPS runtime environment:

- `MSA_DASHBOARD_OWNER_PASSWORD_HASH`
- `MSA_DASHBOARD_SESSION_SECRET`

Then verify browser owner sign-in, real test-only F6C overview/rows/review data, search/filter, drawer behavior, full-table mode, theme switching, responsive navigation, logout, and private-route rejection without a valid session.

Do not import/accept a real migration baseline merely to continue UI development.

## Safety boundary

Do not treat the current F6B test batch as real migration truth. Do not begin production stock writes, database promotion, Telegram writes, Flutter rollout, Sheet mirror conversion, or Custom GPT write Actions without explicit authorization for those slices.

## Continuity rule

After every significant architecture decision, implementation slice, deployment/migration result, or next-work change, update `ROADMAP.md`, `NEW_CHAT_BOOTSTRAP.md`, and relevant canonical architecture/operations docs.
