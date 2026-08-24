# Inventory View Engine v1

Status: **IMPLEMENTATION CONTRACT — first read-only substrate**

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

## Shadow/canonical boundary

During migration review:

- PostgreSQL remains `database_canonical=false`;
- `migration_baseline_accepted=false`;
- Google Sheet/source documents remain operationally authoritative;
- new Inventory views may read shadow domain tables for review/projection proof;
- no view edit is an authorized production inventory mutation.

The Web Inventory UI should visibly label this state rather than presenting shadow data as canonical.

## Custom view target

A later user can create a view by selecting a row grain and Store scope, adding/reordering registered fields, renaming display labels, setting widths/filters/sorts/groups/formatting, and saving the definition.

Persistence of custom definitions is intentionally deferred from the first read-only substrate. The v1 API must nevertheless prove that projection columns are registry-driven rather than hard-coded to one screen.

## Editing boundary

Later spreadsheet-like editing follows:

`cell/table edits -> local draft -> semantic validation -> preview -> Confirm & Save -> typed domain command -> transaction -> audit -> read-back -> refresh`

No direct current-balance overwrite and no arbitrary DB mutation are introduced by the View Engine.

## AI integration

Inventory is the primary operational/review workspace. AI is a context-aware copilot, not the table owner.

The future UI may send selected rows/current view/filter/source evidence to an embedded assistant. Difficult cases may be escalated to AI Workspace/multi-agent review. AI proposals still require the same typed acceptance/authority path.

## v1 acceptance

The first implementation slice is acceptable when:

1. a typed registry exists;
2. at least Main Stock and Migration Review exist as system view definitions;
3. one generic authenticated read API renders either preset;
4. the same API can validate a caller-selected subset/order of registered fields;
5. unknown field keys are rejected;
6. output remains explicitly read-only/non-canonical;
7. no inventory, mapping-acceptance or price mutation is introduced.
