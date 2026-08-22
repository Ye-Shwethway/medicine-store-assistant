# Medicine Store Assistant — UI/UX Pro Max Integration

Status: **adopted for the Web Dashboard design workflow**

## Upstream

- Project: `nextlevelbuilder/ui-ux-pro-max-skill`
- Upstream commit pinned for this design cycle: `bc826e2267a36d98a2dcf5231e16c30ff546770f`
- License: MIT
- Purpose: local design intelligence for UI structure, visual design, responsive layout, accessibility, interaction, typography, color, charts, animation, and stack-specific implementation guidance.

The upstream repository is a development/design dependency only. It is not part of the MSA production runtime and must not gain access to medicine-store secrets, credentials, private workbook rows, or production database credentials.

## Adoption policy

Use UI/UX Pro Max for user-facing UI design, review, and implementation decisions. Do not apply it to backend data authority, inventory integrity, database promotion, authentication policy, or deployment decisions.

For a new page or product-wide direction, follow its design-system-first workflow. For focused bugs, query the smallest relevant domain. Do not treat design guidance as authorization for data writes.

## MSA Web Dashboard target

Product type: internal inventory operations dashboard / productivity tool.

Audience: medicine-store operator and authorized staff. The interface must work for users who are not web-design specialists and should privilege clarity, scanning speed, confidence, and low-error operation over visual novelty.

Current design direction:

- professional clinical / operational appearance;
- dense-but-calm dashboard information density;
- light-first interface with dark-mode compatibility planned;
- strong table and status hierarchy;
- semantic status colors plus text labels, never color alone;
- 44 px minimum primary interaction targets;
- keyboard-accessible navigation and focus states;
- no hover-only essential interactions;
- no page-level horizontal scrolling on mobile;
- responsive tables should progressively collapse or switch to row-detail patterns;
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
3. Design/review in Figma before production implementation for major screens.
4. Use an interactive prototype for navigation, filters, search, selection, drawers/modals, loading/empty/error states, and responsive behavior before enabling production writes.
5. Implement the dashboard against authenticated API contracts; never query PostgreSQL directly from the browser.
6. Test accessibility, keyboard behavior, narrow screens, touch targets, loading states, and failure states before calling a UI slice complete.

## Upstream update policy

Do not silently float to the latest upstream revision. When upgrading UI/UX Pro Max, record the new upstream commit here, review release changes, and verify that MSA design decisions remain compatible.
