# Medicine Store Assistant — Inventory Sheet Interaction Foundation v1

Status: **authorized implementation contract**

## Purpose

Move the read-only Inventory Workbench from a row-inspection-first table toward a true sheet-like interaction model before Saved Custom Views / View Builder and later typed editing.

This contract follows the pinned UI/UX Pro Max workflow, `design-system/medicine-store-assistant/MASTER.md`, the Dashboard page override, and `docs/design/WEB_IMPLEMENTATION_STANDARD.md`.

## Interaction model

The Inventory table remains a semantic data table and read-only shadow projection. Selection is presentation/workbench state only; it does not mutate inventory, mappings, prices, migration state, or canonicality.

### Data cells

- Single click/tap on a data cell selects that cell and makes it the active cell.
- Clicking a different cell replaces the primary cell selection.
- `Shift` + click extends from the anchor cell to a rectangular range.
- Desktop pointer drag extends a rectangular range while the primary pointer is held.
- Arrow keys move the active cell by one visible cell.
- `Shift` + Arrow extends the rectangular range from the anchor.
- `Enter` opens the selected row's detail drawer as a keyboard shortcut.
- Cell click/tap **must not** open the detail drawer.
- Visible focus and selection outlines must remain distinguishable in light and dark themes.

### Whole-row selection

- A dedicated row-selector gutter is UI chrome, separate from registered data fields such as `No.`.
- Click/tap on a row-selector selects that whole visible row.
- `Shift` + row-selector extends a contiguous whole-row selection.
- The top-left selector selects/clears the currently visible rows.
- Whole-row selection is the only selection mode that feeds existing `Ask AI` / `Deep Review` row-context actions.
- AI review continues to send row indices/coordinates for server rehydration; DOM cell text is never treated as canonical evidence.

### Details

- Row-wide click-to-open is removed.
- An explicit `Details` action is available when an active cell or a single whole row provides one unambiguous row context.
- `Enter` may invoke the same detail action from an active cell.
- Closing the drawer preserves sheet selection and focus context.

### Copy

- A rectangular cell selection copies exactly the selected visible cells as TSV, without adding unrelated columns.
- Whole-row selection copies the currently visible registered columns for the selected rows.
- Copy remains read-only and does not persist data.

## Scope intentionally deferred

The following are **not** part of v1:

- Ctrl/Cmd non-contiguous multi-range selection;
- touch drag handles for range resizing;
- persistent cell/range selection across refresh/reopen;
- fill colors or other user formatting;
- inline editing, paste-to-edit, formulas, or inventory mutations.

These belong to follow-up Sheet Formatting / persistence / typed-editing slices after the selection model is proven.

## Mobile behavior

- Tap selects one data cell.
- Row-selector tap selects a whole row.
- Local horizontal table scrolling remains available.
- Touch pointer movement must not hijack normal scrolling to create accidental ranges.
- Essential actions are not hover-only and principal controls retain approximately 44 px touch targets.
- Touch range handles may be added later after the desktop/keyboard model is stable.

## System status vs future user formatting

Existing semantic warning/review states remain authoritative UI signals. Future user fill colors must not erase or replace `REVIEW`, `CONFLICT`, `NEW_UNMAPPED`, mapping-status, or other system semantics. System status should remain visible through text/badges/stripe/border treatment even when presentation fills are later added.

## Ownership

`backend/app/dashboard_assets/dashboard_inventory_views.js` remains the single authoritative renderer/state/event owner for the Inventory Workbench, including sheet selection. Do not add a second overlay renderer, independent table state manager, or MutationObserver-based selection layer.

## Accessibility

- Preserve native table semantics unless a complete, tested ARIA grid pattern is intentionally adopted later.
- Selected cells/rows expose `aria-selected` where applicable.
- Active cell has a deterministic focus target and visible focus state.
- Keyboard navigation does not trap focus inside the table; `Tab` remains available to leave the grid controls.
- Row selectors and Details controls have accessible names.
- Selection is not communicated by color alone; the selection summary provides textual state.

## Acceptance proof

Behavior-level browser tests must prove at minimum:

1. data-cell click selects without opening details;
2. clicking another cell replaces the selection;
3. `Shift` + click creates a rectangular range;
4. desktop pointer drag creates a rectangular range;
5. Arrow and `Shift` + Arrow navigation work;
6. row-selector click and `Shift` + row-selector whole-row selection work;
7. explicit Details / `Enter` opens the correct row drawer;
8. cell-range Copy TSV copies only the selected rectangle;
9. whole-row selection preserves current Ask AI / Deep Review row semantics;
10. 390x844 mobile tap selects a cell without forcing drawer-open or breaking local table scrolling;
11. sorting/filter/preset changes clear stale selection safely;
12. exact merged asset content is deployed and issue #26 confirms the deployed SHA.

## Authority boundary

This slice is UI/read-only only. It must not accept CMS mappings or prices, mutate inventory, accept the migration baseline, or promote PostgreSQL as canonical. `database_canonical=false`; `migration_baseline_accepted=false` remain unchanged.
