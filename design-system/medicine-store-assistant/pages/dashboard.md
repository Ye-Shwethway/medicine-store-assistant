# Medicine Store Assistant — Dashboard Page Override

Use together with `../MASTER.md`. These rules refine the master system for the web dashboard only.

## Locked baseline

The owner approved **Dashboard v2.4** as the current visual/interaction baseline on 2026-08-22. Treat this as locked for implementation unless the owner explicitly requests a redesign.

Preserve:

- clean clinical/operations visual language;
- light and dark themes;
- theme control as a visual sun/moon toggle rather than a text-only button;
- persistent test/non-canonical state badges while those states remain true;
- responsive left navigation, with slide-out drawer behavior at narrow widths;
- spreadsheet-style inventory table with visible horizontal and vertical gridlines;
- Inventory `← Overview` return path;
- expanded/full-table focus mode with an obvious exit control;
- item-detail side drawer;
- search and filters;
- no write/edit/save affordance in the read-only phase.

## Dashboard goals

The dashboard should answer, within a few seconds:

1. Is the read path healthy?
2. What test/shadow inventory state needs attention?
3. What is test-only versus operational truth?
4. Where should the operator go next?

## Desktop composition

- Left navigation: 248 px reference width.
- Header: page title + concise subtitle on the left; environment/data-authority badges + visual theme toggle on the right.
- Main canvas: metrics row followed by prioritized operational content.
- Avoid placing more than four top-level metric cards in one row.
- Use one dominant information region and one narrower context/authority region rather than many equal cards.

## Overview

Primary widgets:

- staged/test record summary while PostgreSQL is non-canonical;
- attention queue;
- system/read-path health;
- data-authority flow;
- explicit migration-baseline warning.

Do not present test snapshot counts as live canonical stock KPIs.

## Inventory

Primary workflow:

1. search;
2. filter;
3. scan spreadsheet-style rows;
4. open detail drawer;
5. inspect provenance/status;
6. optionally expand the table into focus mode;
7. return to Inventory or Overview without losing navigation context.

Current phase is read-only. Do not show fake edit/save buttons.

Desktop columns must remain aligned through a shared table grid. Use visible vertical and horizontal borders similar to the working Google Sheet. Mobile may use local horizontal table scrolling rather than crushing columns until the later mobile inventory redesign is authorized.

## Shadow inspection

Audience: operator/technical reviewer, not general staff.

Show:

- batch identity;
- source/test status;
- classification counts;
- reason summaries;
- API/read status;
- explicit no-write boundary.

Avoid exposing internal secrets or raw credential paths.

## Authentication & access UX — F7.2

Primary authentication is a dedicated `/dashboard/login` page, not the temporary in-dashboard owner modal.

Reuse the existing v2.4 visual system. The sign-in page must stay simple and operational: product identity, username, password, `Sign in`, inline generic errors, theme support, and a clear unavailable state when authentication is not provisioned. There is no public sign-up, social login, or password-reset email flow in v1.

Unauthenticated access to protected dashboard pages redirects to sign-in. Successful sign-in returns to the intended protected view when safe. Authenticated visits to the sign-in page redirect to the dashboard. Session expiry and explicit sign-out return to sign-in without revealing private data.

Never ask the browser to store the F3 Bearer service credential, plaintext passwords, session signing secrets, or password hashes.

### Role-aware states

Use the locked F2 roles:

- `OWNER` — full dashboard/access visibility and future user-management entry points.
- `ADMIN` — operational administration without implicit Owner authority.
- `STAFF` — routine inventory/approved operational surfaces; no user management or privileged correction/configuration.
- `READ_ONLY` — read surfaces only; no write/edit/save/approve controls.

UI visibility is convenience only. Backend policy must authorize every protected operation independently.

`Audit & Access` is the future account/role-management surface for authorized roles. Public self-registration is prohibited. Disabled/revoked users with audit history are retained rather than deleted.

### Access denied

Provide an explicit authenticated `403 / Access denied` state for valid users who lack permission. Show the signed-in role, a concise explanation, and a safe return to Overview. Do not treat authorization failure as a bad-password problem.

Detailed design contract: `docs/design/F7_2_AUTH_RBAC_DESIGN.md`.

## Interaction regression checklist

Every implementation/refinement must preserve and verify:

- dedicated sign-in flow and unauthenticated redirect;
- authenticated redirect away from sign-in;
- role-aware navigation/control visibility;
- access-denied state;
- session expiry and sign-out;
- Overview ↔ Inventory navigation;
- sidebar navigation at desktop widths;
- slide-out navigation at narrow widths;
- light ↔ dark theme switching;
- search filtering;
- classification/source-sheet filtering;
- row selection;
- detail drawer open/close and Escape handling;
- expanded table view + exit path;
- loading, empty and auth-error states;
- keyboard-focus affordances;
- touch targets around 44 px;
- no accidental write controls;
- reduced-motion-safe transitions.

All controls shown in the product must have a defined behavior. Disabled future actions must explain why they are disabled.
