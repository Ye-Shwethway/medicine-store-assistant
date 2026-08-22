# Medicine Store Assistant — Master Design System

Status: **active design source of truth for Web Dashboard v2**

Basis: UI/UX Pro Max design-system-first workflow, pinned in `docs/design/UI_UX_PRO_MAX_INTEGRATION.md`.

## Product character

Medicine Store Assistant is an internal inventory operations product. The interface should feel trustworthy, calm, precise, modern, and operational rather than decorative or consumer-marketing oriented.

Design keywords: **clinical, professional, data-first, calm, efficient, trustworthy, responsive, accessible**.

Avoid: gratuitous glassmorphism, excessive gradients, oversized marketing typography, decorative dashboards with low information density, hover-only controls, emoji UI icons, color-only statuses, and dense tables that require page-level horizontal scrolling.

## Layout

Desktop reference width: 1440 px.

- Persistent left navigation for primary desktop workflows.
- Main content uses a responsive max-width/grid with generous edge padding.
- 8 px spacing base.
- Dense dashboard spacing range: 8 / 12 / 16 / 20 / 24 / 32 px.
- Cards use consistent internal padding, usually 16–20 px.
- Primary interactive targets are at least 44 px high.
- Sections must align to the same content grid.
- No overlapping text, badges, pills, or controls.
- Text containers must be allowed to shrink/wrap intentionally; status pills must not overlap adjacent cells.

## Typography

Primary family: Inter or an equivalently legible neutral sans-serif.

- Page title: 24–28 px, semibold.
- Section title: 17–20 px, semibold.
- Standard body: 16 px preferred for primary user content.
- Compact table body: 13–14 px only when density is required and contrast/legibility remain strong.
- Secondary metadata: 12–13 px.
- Line height approximately 1.4–1.6 for body copy.
- Never use placeholder text as the only form label.

## Color semantics

Use semantic tokens rather than arbitrary raw component colors.

- Surface / canvas: near-white cool neutral.
- Primary text: dark slate.
- Secondary text: medium slate with accessible contrast.
- Primary operational accent: deep teal/green.
- Success: teal/green + explicit text label.
- Review / warning: amber + explicit text label.
- Error / conflict: red + explicit text label.
- Information / unmapped: blue + explicit text label.

Status meaning must never depend on color alone.

## Navigation

Desktop primary sections:

1. Overview
2. Inventory
3. Expiry & Alerts
4. Shadow Inspection
5. Catalogue
6. Audit & Access

Future write workflows may add Receive Stock, Record Usage, Adjust Stock, and Reconciliation, but these must not appear as active production controls until those backend write slices are explicitly authorized.

## Core components

### Status pill

- Single line; no wrap.
- Includes readable text label.
- Compact but not cramped.
- Must not collide with table content.

### Metric card

- One primary value.
- One concise descriptor.
- Optional semantic context line.
- Avoid multiple competing actions inside a metric card.

### Data table

- Fixed semantic column model, not manually positioned text.
- Header and row cells share the same grid widths.
- Long names truncate or wrap intentionally.
- Rows have consistent minimum height.
- Selected/hover state is supplemental; all actions remain tap/click accessible.
- On small screens, switch to a card/detail pattern or local scroll region rather than forcing page-level horizontal scroll.

### Filters/search

- Search has a visible accessible label or associated programmatic label.
- Filters expose active state clearly.
- Clearing filters is easy and deterministic.
- Loading/filtering changes provide feedback.

### Drawer / detail panel

Use for row details, provenance, expiry information, and future controlled actions. Preserve the user's table context when the panel opens/closes.

## Motion

Motion level: moderate-subtle.

- 150–250 ms for ordinary UI transitions.
- Motion communicates state change or spatial relationship.
- Avoid animating layout width/height when transform/opacity can be used.
- Respect `prefers-reduced-motion`.
- Do not use continuous decorative motion in operational screens.

## Accessibility

- Target WCAG AA contrast; ordinary text 4.5:1 or better.
- Full keyboard navigation.
- Visible focus states.
- Accessible names for icon buttons.
- Minimum ~44×44 px primary touch targets.
- Do not hide essential actions behind hover.
- Errors appear near the affected field and are announced where appropriate.
- Tables and status changes require semantic structure, not visual-only grouping.

## Current data-authority messaging

Until explicit database promotion:

- Show `TEST DATA` where appropriate.
- Show `DB NON-CANONICAL` where database state may otherwise be misunderstood.
- Explain that Google Sheet remains the operational source of truth.
- Never label the current F6B/F6C snapshot as a migration baseline.

## Definition of design-ready

A page is ready for implementation only when:

- desktop hierarchy is clean;
- no overlap/clipping/alignment defects remain;
- mobile/tablet adaptation is defined;
- loading, empty, error, and disabled states are defined;
- keyboard/touch interaction paths are known;
- every visible action has a real intended behavior;
- data authority is represented accurately;
- the design can map cleanly to API contracts without browser-direct database access.
