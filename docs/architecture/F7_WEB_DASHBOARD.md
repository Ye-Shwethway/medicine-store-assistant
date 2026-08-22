# F7 — Read-only Web Dashboard

Status: **F7.1 verified complete; F7.2 authentication/RBAC design authorized**

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

Design guidance is governed by `design-system/medicine-store-assistant/MASTER.md`, `design-system/medicine-store-assistant/pages/dashboard.md`, `docs/design/F7_2_AUTH_RBAC_DESIGN.md`, and the pinned UI/UX Pro Max reference.

## Stack decision

F7 uses the existing FastAPI service for both the dashboard shell and a server-side browser-facing BFF. Do not introduce React/Next/Vite or another frontend runtime merely for this slice.

Frontend assets remain plain HTML/CSS/vanilla JavaScript and are progressively replaceable later if product requirements justify a framework.

## Browser security boundary

The browser must never receive or persist the raw F3 service credential, plaintext passwords, password hashes, or session signing secrets.

The existing F7.1 bootstrap authentication uses:

- `MSA_DASHBOARD_OWNER_PASSWORD_HASH`: PBKDF2-SHA256 encoded bootstrap Owner password hash;
- `MSA_DASHBOARD_SESSION_SECRET`: high-entropy HMAC signing secret;
- `msa_dashboard_session`: HttpOnly, Secure, SameSite=Strict cookie;
- short-lived signed session payload validated server-side on every BFF read.

If required authentication material is missing, the private dashboard data plane remains fail-closed.

## F7.1 verified route contract

UI shell:

- `GET /` → redirect to `/dashboard`
- `GET /dashboard`
- `GET /dashboard/assets/{asset}`

Session:

- `GET /dashboard/api/session`
- `POST /dashboard/api/session`
- `DELETE /dashboard/api/session`

Authenticated read-only BFF:

- `GET /dashboard/api/overview`
- `GET /dashboard/api/rows`
- `GET /dashboard/api/review-reasons`

All BFF data responses continue to state:

- `database_canonical: false`
- `migration_baseline_accepted: false`

## F7.2 — Authentication & Role-Based Access

F7.2 is no longer defined as credential provisioning only. It is the dashboard authentication and role-based access slice.

### Dedicated sign-in experience

Introduce `/dashboard/login` as the primary user-facing sign-in page. The existing owner modal is transitional and must not remain the final primary login UX.

Requirements:

- reuse Dashboard v2.4 visual language and theme tokens;
- login name + password fields;
- generic inline credential errors;
- no public signup;
- no social/OAuth login in v1;
- no browser secret storage;
- safe return to intended protected page after successful login;
- authenticated users visiting the login page return to `/dashboard`;
- session expiry/sign-out return to login.

### Canonical roles

Use the approved F2 v1 roles:

- `OWNER`
- `ADMIN`
- `STAFF`
- `READ_ONLY`

Backend policy, not hidden UI, is authoritative. Role-aware navigation/control visibility is a UX layer only.

`Audit & Access` becomes the future account/access management surface. Accounts are provisioned by authorized workflows only; public self-registration is prohibited. Canonical human identity is stable backend `user_id`; deactivation/revocation is preferred over deleting users with history.

### Access-denied behavior

Authenticated-but-unauthorized access uses a first-class `403 / Access denied` state with the current role and safe return path. Do not misrepresent authorization failure as invalid credentials.

### Bootstrap Owner bridge

The existing runtime values remain the first deployment bridge:

- `MSA_DASHBOARD_OWNER_PASSWORD_HASH`
- `MSA_DASHBOARD_SESSION_SECRET`

They may be provisioned to verify the protected Owner read path before the canonical multi-user credential store is implemented. They are not the final user database.

## Data authority

Current authority remains:

```text
Google Sheet (authoritative operational source)
        ↓ explicit test snapshot only
PostgreSQL (non-canonical shadow/test)
        ↓ authenticated server-side reads
Dashboard BFF
        ↓ authenticated role-aware session
Browser dashboard
```

Normal backend deploy must not import/read the live Google workbook.

## Security / scope boundary

F7.2 remains read-only and does **not** authorize:

- inventory writes;
- stock receipts/issues/adjustments;
- catalogue mapping edits;
- migration promotion;
- Sheet mutation;
- real migration baseline acceptance;
- Telegram/Flutter/Custom GPT write actions;
- arbitrary permission editing.

No dashboard route may expose arbitrary SQL.

## F7.2 implementation sequence

1. Lock auth/RBAC design and continuity docs.
2. Provision bootstrap Owner runtime secrets securely on the VPS.
3. Verify the existing protected Owner read path.
4. Implement dedicated login UX and role-aware session/account foundation against the approved F2 identity model.
5. Verify OWNER / ADMIN / STAFF / READ_ONLY authorization behavior and access-denied states.
6. Keep all current data-authority and read-only boundaries intact.
