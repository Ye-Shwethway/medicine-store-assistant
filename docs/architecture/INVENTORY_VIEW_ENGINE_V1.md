# Inventory View Engine v1

Status: **IMPLEMENTATION CONTRACT — read-only projection, review, bounded AI context and spreadsheet-workbench substrate**

## Decision

The Web Inventory section is not a fixed Main Stock screen and must not become a worksheet-shaped database client.

`Main Stock`, `Daily Usage`, `Migration Review`, `CMS Mapping Review`, and later operational layouts are **view definitions/presets over canonical domain semantics**.

The same engine must later support user-created sheet-style views.

> **Presets are examples and compatibility surfaces, not the limit of the view model.**

> **A user-defined column maps to a registered semantic field/computation/command, not arbitrary SQL or a raw database column.**

## v1 layers

### Field/computation registry

Every projectable column has a stable field key and semantic class:

- `ENTITY_FIELD`
- `COMPUTED_FIELD`
- `COMMAND_EDITABLE_FIELD`
- `DISPLAY_HELPER`

The registry is the contract shared by presets, the future View Builder, Web/Flutter renderers and AI context.

### View definition

A view definition carries at least:

- stable view ID;
- name/preset type;
- row grain;
- Store/location scope;
- ordered columns;
- display labels/width hints;
- field bindings;
- provider/query family;
- system-preset versus user-defined status.

Changing a view definition never mutates inventory history.

### Generic renderer

The renderer receives a validated view definition (or validated registry field selection), obtains rows at the declared domain grain, and returns ordered columns plus row values.

It must never expose arbitrary SQL/column expressions supplied by a client.

## First system presets

### Main Stock

Row grain: `PRODUCT_LOT`, scoped to `MAIN` initially.

It projects familiar columns from Product/Lot/Store/Ledger/CMS mapping state. Current quantity is ledger-derived; Main Stock is not a canonical table.

### Migration Review

Row grain: source Main Stock row joined to materialized shadow state where resolvable.

It is a review preset, not a second inventory truth. It exists so source-versus-shadow review can use the same table/view architecture that later serves production inventory.

### CMS Mapping Review

Row grain: current local Product mapped to its current non-accepted CMS review-state row.

This preset is a read-only review projection over `products`, current `product_cms_mappings`, and the current referenced catalogue item. It must expose mapping status, CMS evidence, current catalogue price and accepted operational price without accepting a mapping or changing a price.

The initial review-state dataset is intentionally dominated by `REVIEW_REQUIRED`; `CMS_DISCONTINUED`, `RECYCLED_CODE`, and `UNMAPPED` remain directly filterable and visible rather than being collapsed into one warning state.

## Review filter contract

The generic rows endpoint may accept validated provider-aware review filters in addition to text search:

- `mapping_status` — exact current mapping status such as `REVIEW_REQUIRED`, `CMS_DISCONTINUED`, `RECYCLED_CODE`, or `UNMAPPED`;
- `source_classification` — exact staged source classification for Migration Review;
- `review_reason` — case-insensitive substring match against the staged review reason.

The API constructs SQL only from server-owned clauses and typed parameter values. Clients never supply raw predicates, column names, joins, SQL fragments, or database expressions.

Changing filters changes only the read projection.

## Source-vs-shadow review contract

Migration Review remains source-row-grain. The review workspace preserves these boundaries:

- source values are visually distinguished from shadow projections;
- HOLD/review reason remains explicit;
- missing or ambiguous source values are never filled from shadow state merely to make comparison look complete;
- row selection never implies acceptance;
- selection is context for human review / AI review until separately authorized typed acceptance commands exist;
- structured review evidence may be rendered as human-friendly summaries, but raw source/review evidence is not rewritten.

## Bounded Inventory AI context contract

The Inventory AI path reuses the existing AI Workspace/internal-agent runtime rather than creating a parallel inference stack.

`Inventory Review Context` is server-owned and server-rehydrated. The browser provides only validated review coordinates such as:

- preset/view ID;
- active validated filters;
- pagination offset/limit;
- selected row indices within that rehydrated page.

The browser does **not** establish current store facts merely by sending row text from the DOM. The server re-runs the same validated view provider and constructs the selected bounded evidence.

### Ask AI

- available for review presets;
- explicitly opens AI Workspace Chat;
- displays the selected Inventory context in a focused chooser;
- requires explicit agent choice / Start new chat;
- creates a fresh conversation rather than reusing the previous chat;
- prefills a review prompt from the server-rehydrated context;
- never auto-sends the prompt or auto-executes the model.

### Deep Review

- explicitly opens the existing Owner Multi-Agent REVIEW workspace;
- prefills the durable Work Item title/task from the server-rehydrated context;
- may expose a nearby quick REVIEW-preset selector and role navigation;
- may invoke the existing canonical `Run native review` control only after explicit user action;
- must not silently select or run a review.

Neither AI path accepts mappings/prices, mutates inventory, accepts the migration baseline, or promotes database canonicality.

## Spreadsheet workbench contract

The generic renderer may provide spreadsheet-like **interaction ergonomics** without becoming a raw spreadsheet database editor.

### Focus Mode v1 — implemented

The first workbench layer includes:

- near-fullscreen Focus mode;
- explicit Exit and `Escape` exit behavior;
- current View/Search/Filters/Columns remain available;
- Comfortable/Compact density modes;
- select-visible header checkbox + explicit `Clear selection`;
- sticky/frozen selection column and first visible data column;
- existing review drawer / Ask AI / Deep Review remain compatible.

Focus Mode v1 is a presentation/read-context feature. It does not change data semantics or authority.

### Workbench v2 target

The next bounded read/review layer may add:

- server-side validated sorting and visual sort state;
- active filter chips;
- registered-column resize/reorder/auto-fit/reset-layout controls;
- Copy selected as TSV;
- CSV export of the current validated projection/filter/sort state;
- keyboard navigation/copy shortcuts;
- optional desktop split-pane review detail.

These features must operate over registry-owned fields and server-owned query semantics. Client-provided arbitrary SQL or expressions remain forbidden.

## Shadow/canonical boundary

During migration/review work:

- PostgreSQL remains `database_canonical=false`;
- `migration_baseline_accepted=false`;
- Google Sheet/source documents remain operationally authoritative;
- Inventory views may read shadow domain tables for review/projection proof;
- view selection, sorting, filtering, layout, copy/export or AI handoff is not an authorized production inventory mutation.

The Web Inventory UI must visibly label this state rather than presenting shadow data as canonical.

## Custom view target

A later user can create a view by selecting a row grain and Store scope, adding/reordering registered fields, renaming display labels, setting widths/filters/sorts/groups/formatting, and saving the definition.

Persistence of user-owned layout/view definitions belongs to Slice E. Workbench v2 may prove interactions before they are persisted.

## Editing boundary

Later spreadsheet-like editing follows:

`cell/table edits -> local draft -> semantic validation -> preview -> Confirm & Save -> typed domain command -> transaction -> audit -> read-back -> refresh`

No direct current-balance overwrite and no arbitrary DB mutation are introduced by the View Engine or read-only workbench.

Excel/Sheets-like mutation features such as multi-cell paste, inline editing, fill behavior or undo/redo must wait for this typed editing substrate rather than writing directly to shadow tables.

## v1 acceptance and evidence

The View Engine substrate is accepted because:

1. a typed registry exists;
2. Main Stock, Migration Review and CMS Mapping Review exist as system view definitions;
3. one generic authenticated read API renders validated presets;
4. caller-selected registered field subset/order is validated and unknown fields are rejected;
5. output remains explicitly read-only/non-canonical;
6. source-vs-shadow/CMS review uses the same renderer;
7. bounded Ask AI / Deep Review reuse existing AI Workspace runtimes without mutation authority;
8. Spreadsheet Focus Mode v1 improves table ergonomics without changing semantics;
9. no inventory, mapping-acceptance or price mutation is introduced.

Runtime checkpoints include issues #166, #171, #176, #178 and #186. Focus Mode v1 was merged in PR #185 at `af461f2f4ddd329c81fd983955c26e905970e0af` and deployment issue #26 confirmed production `status=success` for that SHA via run `32811537864`.