# Medicine Store Assistant — UI/UX Pro Max Integration

Status: **adopted as the default Web Dashboard design-and-implementation workflow**

## Upstream

- Project: `nextlevelbuilder/ui-ux-pro-max-skill`
- Upstream commit pinned for this design cycle: `bc826e2267a36d98a2dcf5231e16c30ff546770f`
- License: MIT
- Purpose: local design intelligence for UI structure, visual design, responsive layout, accessibility, interaction, typography, color, charts, animation, and stack-specific implementation guidance.

The upstream repository is a development/design dependency only. It is not part of the MSA production runtime and must not gain access to medicine-store secrets, credentials, private workbook rows, or production database credentials.

## Adoption policy

Use UI/UX Pro Max for user-facing UI design, review, and implementation decisions. Do not apply it to backend data authority, inventory integrity, database promotion, authentication policy, or deployment decisions.

For a new page or product-wide direction, follow the UI/UX Pro Max design-system-first workflow and the locked MSA design system. For focused bugs, use the smallest relevant UI/UX guidance. Do not treat design guidance as authorization for data writes.

### Canonical direct-code rule

The default MSA Web workflow is:

`UI/UX Pro Max guidance -> MSA MASTER/page design contract -> Web implementation standard -> authenticated API contract -> direct web implementation -> behavior/lifecycle verification -> browser delivery verification`

Figma is **not a mandatory implementation gate**. Do not stop normal MSA Web work to create or update Figma artifacts unless the Owner explicitly asks for a Figma design/prototype or a task genuinely requires one.

For ordinary new screens and refinements, implement directly from:

- `design-system/medicine-store-assistant/MASTER.md`;
- the relevant page override under `design-system/medicine-store-assistant/pages/`;
- `docs/design/WEB_IMPLEMENTATION_STANDARD.md`;
- `docs/design/WEB_SURFACE_OWNERSHIP.md`;
- current UI/UX Pro Max guidance;
- the task-specific backend/API contract.

Interactive behavior may be validated in the running Web product itself. A separate design prototype is optional, not required.

### Web implementation reliability rule

Visual correctness is only one part of Web quality. Interactive implementation must also satisfy the canonical reliability standard:

- one authoritative renderer/state owner per interactive subtree;
- delegated/rebound events that survive DOM replacement;
- frontend + backend + persistence verified as one paired contract;
- persisted rehydration after fresh load, refresh, and reopen;
- one async/polling owner with deterministic start/resume/stop behavior;
- behavior-level browser tests for critical controls where practical;
- mobile return/back paths that do not trap the user.

Canonical details: `docs/design/WEB_IMPLEMENTATION_STANDARD.md`.

### Browser-delivery integrity rule

A Web feature is not verified merely because backend routes, CSS/JS source, or CI checks are green. The deployed browser entrypoint must load the intended current asset content.

Dashboard bundles now prefer **content-derived asset identity**: the `?v=` value is calculated from the actual served bundle files, so content changes produce a new URL identity automatically. Manual release strings must not be reintroduced for migrated bundles.

Keep authenticated Dashboard HTML/assets under the current explicit no-store/no-cache delivery contract, wait for issue #26 deployment evidence, and verify the browser delivery chain when accepting a release.

Canonical detailed checklist: `docs/design/WEB_ASSET_RELEASE_INTEGRITY.md`.

## MSA Web Dashboard target

Product type: internal inventory operations dashboard / productivity tool.

Audience: medicine-store operator and authorized staff. The interface must work for users who are not web-design specialists and should privilege clarity, scanning speed, confidence, and low-error operation over visual novelty.

Current design direction:

- professional clinical / operational appearance;
- dense-but-calm dashboard information density;
- light-first interface with dark-mode compatibility;
- strong table and status hierarchy;
- semantic status colors plus text labels, never color alone;
- 44 px minimum primary interaction targets;
- keyboard-accessible navigation and focus states;
- no hover-only essential interactions;
- no page-level horizontal scrolling on mobile;
- responsive tables progressively collapse or use local scrolling/detail patterns;
- subtle meaningful motion only, with reduced-motion support;
- SVG/icon-system icons rather than emoji as interface icons;
- body text at least 16 px in normal user-facing views except compact secondary metadata where accessibility remains acceptable.

## Data-state boundary

The current F6B/F6C dataset is test-only. UI text must clearly distinguish:

- Google Sheet = current operational source of truth;
- PostgreSQL = non-canonical test/shadow database;
- current staged snapshot = test dataset, not an accepted migration baseline.

The dashboard must not imply that PostgreSQL is canonical until explicit promotion occurs.

## Workflow

1. Maintain `design-system/medicine-store-assistant/MASTER.md` as the product-wide design source of truth.
2. Maintain page overrides under `design-system/medicine-store-assistant/pages/` only where a page genuinely differs from the master system.
3. Use UI/UX Pro Max plus those repo design contracts to design and implement Web screens directly in code by default.
4. Before implementation, identify/update the surface owner in `WEB_SURFACE_OWNERSHIP.md`; do not add a second renderer/state owner for the same interactive subtree.
5. Implement the dashboard against authenticated API contracts; never query PostgreSQL directly from the browser.
6. Verify the paired interaction path: user action -> frontend event -> API payload -> backend persistence -> read-back -> rehydrated UI.
7. Validate navigation, filters, selection, drawers/modals, loading/empty/error/disabled states and responsive behavior.
8. For persistent features, verify fresh load, same-tab update, refresh, and reopen. For async features, also verify intermediate and settled states plus polling resume/stop.
9. Test accessibility, keyboard behavior, narrow screens, touch targets, visible labels/focus, reduced motion, failure states, and an obvious mobile return path.
10. Run behavior-level browser tests for critical changed controls where practical; string/route presence checks are supporting evidence only.
11. Validate asset/browser delivery integrity under `WEB_ASSET_RELEASE_INTEGRITY.md` and wait for the exact deployed SHA in issue #26 before calling a UI release live.
12. Never expose a fake action. A disabled future operation must explain why it is unavailable.

## Upstream update policy

Do not silently float to the latest upstream revision. When upgrading UI/UX Pro Max, record the new upstream commit here, review release changes, and verify that MSA design decisions remain compatible.
