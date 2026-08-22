# F7 — Read-only Web Dashboard

Status: **authorized implementation; F7.1 foundation in progress**

## Goal

Provide a professional browser-based management surface for Medicine Store Assistant while PostgreSQL remains non-canonical and Google Sheets remains operationally authoritative.

## Locked visual baseline

The current approved dashboard design is **v2.4**. Preserve these behaviors unless the owner explicitly requests a redesign:

- professional clinical/operations visual language;
- responsive left navigation with mobile slide-out drawer;
- Overview, Inventory, Expiry & Alerts, Shadow Inspection, Catalogue, Audit & Access navigation;
- permanent `TEST DATA` and `DB NON-CANONICAL` state indicators while those facts remain true;
- light/dark theme controlled by a visual sun/moon toggle, not a text-only theme button;
- spreadsheet-style inventory table with horizontal and vertical gridlines;
- search and classification/source-sheet filters;
- item-detail side drawer;
- explicit `← Overview` return path from Inventory;
- expanded/full-table focus mode with a visible exit path;
- no edit/save/write affordances in the read-only phase.

Design guidance is governed by `design-system/medicine-store-assistant/MASTER.md` and the pinned UI/UX Pro Max reference documented in `docs/architecture/UI_UX_PRO_MAX_INTEGRATION.md`.

## Stack decision

F7 uses the existing FastAPI service for both the dashboard shell and a server-side browser-facing BFF. Do not introduce React/Next/Vite or another frontend runtime merely for this slice.

Reasons:

- the repository currently has no frontend framework;
- FastAPI is already the deployed HTTPS origin;
- the dashboard is an owner-facing operational tool, not a public marketing app;
- minimizing runtime/dependency surface keeps deployment and debugging simple;
- server-side BFF endpoints prevent the existing F3 Bearer service credential from being exposed to browser JavaScript or storage.

Frontend assets are plain HTML/CSS/vanilla JavaScript and remain progressively replaceable later if product requirements justify a framework.

## Browser auth boundary

The browser must never receive or persist the raw F3 service credential.

F7 owner authentication uses:

- `MSA_DASHBOARD_OWNER_PASSWORD_HASH`: PBKDF2-SHA256 encoded owner password hash;
- `MSA_DASHBOARD_SESSION_SECRET`: high-entropy HMAC signing secret;
- `msa_dashboard_session`: HttpOnly, Secure, SameSite=Strict cookie;
- short-lived signed session payload validated server-side on every BFF read.

If either required dashboard secret is missing, the dashboard data plane is **disabled fail-closed**. The public shell may render, but no private inventory rows are returned.

The owner password itself must never be committed to the repository or logged by the application.

## F7.1 route contract

UI shell:

- `GET /` → redirect to `/dashboard`
- `GET /dashboard`
- `GET /dashboard/assets/{asset}`

Session:

- `GET /dashboard/api/session` — configuration/authentication state only
- `POST /dashboard/api/session` — owner login; returns no secret material
- `DELETE /dashboard/api/session` — logout

Authenticated read-only BFF:

- `GET /dashboard/api/overview`
- `GET /dashboard/api/rows`
- `GET /dashboard/api/review-reasons`

All BFF data responses must state:

- `database_canonical: false`
- `migration_baseline_accepted: false`

## Data authority

Current authority remains:

```text
Google Sheet (authoritative operational source)
        ↓ explicit test snapshot only
PostgreSQL (non-canonical shadow/test)
        ↓ authenticated server-side reads
Dashboard BFF
        ↓ secure owner session
Browser dashboard
```

Normal backend deploy must not import/read the live Google workbook.

## Security / scope boundary

F7 does **not** authorize:

- inventory writes;
- stock receipts/issues/adjustments;
- catalogue mapping edits;
- migration promotion;
- Sheet mutation;
- real migration baseline acceptance;
- Telegram/Flutter/Custom GPT write actions.

No dashboard route may expose arbitrary SQL.

## F7.1 completion criteria

F7.1 is complete only when:

1. locked v2.4 dashboard shell is served by the deployed FastAPI service;
2. theme, navigation, mobile drawer, Inventory→Overview path, item detail drawer and full-table mode work;
3. unauthenticated/private BFF reads fail closed;
4. dashboard is visibly non-canonical/test-only;
5. health/readiness remain green;
6. deployment performs no live workbook import;
7. repository validation and automatic deployment are green.

## F7.2 follow-up

Provision owner dashboard credentials on the VPS without exposing them in Git or browser code, then live-verify authenticated BFF reads against the existing F6C test-only shadow dataset.
