# Medicine Store Assistant — Inventory Sheet Formatting v1

Status: **authorized implementation contract**

## Purpose

Add spreadsheet-like presentation formatting on top of the proven Inventory Sheet Interaction Foundation without adding inventory mutation semantics or prematurely persisting user layouts.

The Inventory Workbench remains a read-only projection over the current non-canonical shadow dataset. Formatting is workbench presentation metadata only.

## Scope

### Fill formatting

- Apply a fill color to the current rectangular cell selection.
- Apply a fill color to selected whole rows across the currently visible registered columns.
- Clear user fill from the current selection.
- Initial bounded palette: Yellow, Light green, Light red, Light blue, Orange, Gray, plus No fill / Clear fill.
- No arbitrary custom color picker in v1.

### Selection integration

- Formatting actions operate on the existing authoritative sheet-selection state in `dashboard_inventory_views.js`.
- No second renderer, overlay state manager, MutationObserver formatting layer, or DOM-derived authority is permitted.
- Cell/range selection and whole-row selection remain mutually understandable to the selection summary.
- Ask AI / Deep Review remain whole-row-only and server-rehydrated; formatting metadata is never sent as canonical review evidence.

### Presentation layering

User fill must not hide system semantics.

Required visual precedence:

1. system semantic warning remains visible through text/status plus an independent stripe/border signal;
2. user fill supplies the cell background;
3. current selection overlay/active-cell outline remains visible above user fill.

A user-applied green fill must therefore never make REVIEW / CONFLICT / NEW_UNMAPPED or other system states appear resolved.

### Persistence boundary

- v1 formatting is session-only.
- Sorting/filtering/search/pagination may re-render the table, but formatting attached to a stable visible row identity + field key should survive ordinary re-render while the session remains on the same workbench state.
- Formatting is not written to PostgreSQL, Google Sheets, inventory records, CMS mapping rows, source evidence, or a saved View Definition.
- Persistent formatting belongs to Saved Custom Views / View Builder after this interaction contract is proven.

## Data identity

Cell-format metadata is keyed semantically, not by DOM coordinates:

`(rowIdentity, fieldKey) -> fillToken`

Whole-row formatting is expanded to the current visible registered field keys for that row when applied. This keeps formatting deterministic when columns are reordered.

`rowIdentity` continues to use the existing stable workbench identity preference (Lot ID, Product ID, source row identity, then bounded fallback).

## Toolbar behavior

When a cell/range or whole-row selection exists, the selection toolbar exposes a compact `Fill` control and `Clear fill` action.

The Fill control shows the bounded palette as explicit swatches/buttons with accessible names. It must work on desktop and mobile without hover-only behavior.

## Copy/export boundary

- Copy TSV copies values only; user fill metadata is not embedded in clipboard TSV.
- Existing generic Excel export remains unchanged in this v1 slice. Exporting persisted custom-view formatting is deferred until View Builder owns saved formatting metadata.
- No second Excel renderer may be introduced.

## Mobile

- Tap selection remains unchanged.
- Fill palette remains reachable from the selection toolbar at 390x844.
- Applying a fill must not hijack horizontal/vertical sheet scrolling.
- Principal formatting controls keep practical touch targets.

## Accessibility

- Fill choices have text/ARIA labels in addition to color.
- Current selection continues to expose textual selection count/summary; formatting is never communicated by color alone.
- Active-cell outline remains visible over all palette fills in light and dark themes.

## Acceptance proof

Behavior-level browser proof must verify at minimum:

1. one selected cell receives a user fill;
2. rectangular range receives the same fill;
3. whole-row selection fills all currently visible registered cells for selected rows;
4. Clear fill removes only user formatting from the selection;
5. selection outline remains visible over user fill;
6. REVIEW / CONFLICT system signal remains visible after user fill;
7. column reorder does not detach a formatted cell from its semantic field;
8. sorting/re-render does not move a fill to the wrong stable row identity;
9. Copy TSV remains value-only and unchanged;
10. Ask AI / Deep Review semantics remain whole-row-only and do not consume formatting metadata;
11. 390x844 mobile selection + fill controls are usable;
12. no inventory/CMS/baseline/canonicality mutation occurs.

## Authority boundary

This slice is presentation/read-only only. It must not accept CMS mappings or prices, mutate inventory, accept the migration baseline, or promote PostgreSQL as canonical. `database_canonical=false`; `migration_baseline_accepted=false` remain unchanged.
