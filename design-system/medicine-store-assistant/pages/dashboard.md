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
- no inventory write/edit/save affordance in the read-only phase.

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

1. search/filter and scan spreadsheet-style rows;
2. click/tap a data cell to make it the active sheet cell;
3. extend rectangular ranges with desktop drag / Shift and keyboard arrows;
4. use the dedicated row-selector gutter for one or more whole rows;
5. open item provenance/status through explicit `Details` or the keyboard Enter shortcut rather than row-wide click;
6. optionally expand the table into focus mode;
7. return to Inventory or Overview without losing navigation context.

Cell/range selection is presentation-only. Whole-row selection remains the bounded source for existing server-rehydrated Ask AI / Deep Review context. Current inventory phase is read-only. Do not show fake inventory edit/save buttons.

Desktop columns must remain aligned through a shared table grid. Use visible vertical and horizontal borders similar to the working Google Sheet. Mobile may use local horizontal table scrolling rather than crushing columns until the later mobile inventory redesign is authorized.

## Shadow inspection

Audience: operator/technical reviewer, not general staff.

Show batch identity, source/test status, classification counts, reason summaries, API/read status, and explicit no-write boundary. Avoid exposing internal secrets or raw credential paths.

## Authentication & access UX — F7.2

Primary authentication is a dedicated `/dashboard/login` page. Reuse v2.4 visual language. Request access is pending-only; Forgot password is enumeration-safe; authenticated private access stays behind backend authorization. Never store service credentials, plaintext passwords, signing secrets, password hashes, reset verifiers, or provider keys in browser storage.

### Drawer signed-in profile — F7.2B

The top section of the desktop sidebar / narrow-screen drawer shows a compact signed-in identity box below product branding and above navigation. It includes circular avatar/initials fallback, canonical username, role metadata, safe truncation, and server-derived session data. It is informational; profile-image management remains deferred.

### Account security — F7.2C — **VERIFIED**

All active human roles receive an `Account` navigation surface for self-service username/password/recovery-email maintenance. Credential changes require current-password re-authentication, use visible labels/helper/error states, maintain ~44 px controls, and invalidate old sessions as documented.

### Forgot password / reset — F7.2C — **VERIFIED**

Forgot-password UI is enumeration-safe. Owner-issued reset links use a dedicated new-password state; reset tokens are temporary secret material and are not persisted in browser storage.

### Role-aware states

Use canonical human roles `OWNER`, `ADMIN`, `STAFF`, `READ_ONLY`. UI visibility is convenience only; backend authorization remains authoritative.

### User Management — F7.2B/F7.2C

`User Management` is standalone and Owner-only. Show pending/active/disabled metrics, identity/role/state, approval/rejection, allowed role assignment, session revoke, disable/reactivate, and reset-request actions. Ordinary User Management cannot create/promote/modify `OWNER`. Destructive actions require confirmation. States always have text labels.

### Access denied

Provide explicit authenticated `403 / Access denied` states with concise explanation and safe return path.

Detailed design contracts:

- `docs/design/F7_2_AUTH_RBAC_DESIGN.md`
- `docs/design/F7_2C_CREDENTIAL_LIFECYCLE_DESIGN.md`

## AI Agent Management & Provider Registry — F7.2D2/F7.2D3 — **VERIFIED**

This is one Owner-only AI control-plane surface. It must visually reuse Dashboard v2.4 and the UI/UX Pro Max direct-code workflow rather than inventing a separate product style.

### Control consistency

Toolbar/header controls in the same semantic class must use the same visual family. In particular:

- `Refresh`, `Create agent`, and `New session` use the dashboard secondary-control family;
- Provider Registry actions such as `Add provider`, `Test connection`, `Fetch models`, `View models`, `Enable`, and `Disable` use existing button families according to action risk/priority;
- all principal controls retain ~44 px touch targets and visible keyboard focus;
- browser-default button chrome is not acceptable when an equivalent MSA control pattern exists.

### Agent-origin grouping

Do not present all AI principals as one visually undifferentiated list. Separate/labeled groups are required:

1. **External / MCP agents** — ChatGPT/custom MCP and other externally hosted agent runtimes.
2. **Internal / provider-backed agents** — MSA-managed agents that receive provider/model assignments.

System automation may use an explicit system-origin label while remaining distinct from an externally hosted MCP runtime.

The grouping is explanatory UX only; backend runtime mode/identity remains authoritative.

### Agent card primary metadata

Every agent card must make these three fields quickly scannable:

- **Agent name** — canonical configured display name;
- **Origin** — e.g. Custom MCP, Custom Action, MSA provider, or MSA system;
- **Model** — actual assigned model where known.

Rules for model display:

- internal provider-backed agent without assignment: `Not assigned`;
- externally hosted runtime without canonical model metadata: `Client-managed`;
- never infer/guess a model from client brand, runtime name, or chat behavior;
- after F7.2D4 assignment, internal cards show the actual provider/model relationship while stable agent identity remains unchanged.

Secondary metadata may include call name, runtime mode, state, authority ceiling, execution/confirmation policy, capabilities, purpose, and self-identity preview.

### Multi-agent sessions

Keep session creation visually adjacent to named agents but separate from provider configuration. Session UI must support participant selection/order/role labels and make origin differences readable when selecting participants. Existing modes are `GROUP`, `COMPARE`, `REVIEW`, `DEBATE`.

### Provider Registry

Provider Registry belongs in the same Owner-only AI control-plane page because it configures runtime implementation for internal agents, but provider cards remain visually distinct from agent cards.

Show at minimum:

- provider display name/kind;
- enabled/disabled state;
- connection status;
- credential configured/missing status without key read-back;
- model count/model-fetch status;
- base URL where relevant;
- Test connection / Fetch models / View models / Enable/Disable controls.

Saved provider API credentials are write-only. The UI must never show or imply that a saved key can be read/reconstructed. A custom provider URL must be clearly identified as an outbound server connection subject to backend security validation.

Model-catalog views must explicitly represent unknown capability values rather than converting unknown to yes/no.

## Interaction regression checklist

Every implementation/refinement must preserve and verify:

- dedicated sign-in flow and unauthenticated redirect;
- Request access remains pending-only;
- Forgot password remains enumeration-safe;
- one-time reset surface works without exposing reset verifier material;
- authenticated redirect away from sign-in;
- drawer/sidebar signed-in profile card;
- Account surface and re-authentication behavior;
- role-aware navigation/control visibility;
- Owner-only User Management;
- Owner-only AI Agent Management and Provider Registry;
- explicit Access denied state;
- Overview ↔ Inventory navigation;
- sidebar/drawer navigation;
- light ↔ dark theme switching;
- inventory search/filter/detail/focus flows;
- AI Agent `Refresh` / `Create agent` / `New session` control-style consistency;
- External/MCP vs Internal/provider-backed agent grouping;
- Agent name / Origin / Model card fields;
- provider credential no-readback messaging/state;
- loading, empty and auth-error states;
- keyboard-focus affordances;
- touch targets around 44 px;
- no accidental inventory write controls;
- reduced-motion-safe transitions.

All controls shown in the product must have defined behavior. Disabled future actions must explain why they are disabled.