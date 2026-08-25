# Reusable Excel Export

Status: **Authorized F6E implementation contract.**

## Purpose

MSA needs formatted Excel export in many product areas. Inventory is the first consumer, but the workbook renderer must not depend on Inventory providers, presets, database queries, or Dashboard DOM state.

The reusable boundary is:

`validated tabular projection -> generic workbook specification -> styled .xlsx bytes`

Feature areas remain responsible for selecting and validating their own data. The shared Excel module is responsible only for presentation-safe workbook generation.

## Global contract

A caller supplies:

- workbook/sheet identity;
- ordered columns with stable keys, display labels and semantic data types;
- already-authorized row dictionaries;
- optional presentation hints such as preferred widths.

The reusable renderer must:

- create a real `.xlsx` workbook;
- preserve caller column order and row order;
- write strings as literal text and never turn user/source text into formulas;
- preserve numeric/date values as typed Excel cells where practical;
- style the header with blue fill, bold white text, centered/wrapped alignment;
- freeze the header row;
- wrap body text and vertically align cells;
- apply thin borders across the used table range;
- derive bounded readable column widths and practical wrapped row heights;
- create an Excel Table with filter controls when there is at least one data row;
- keep worksheet gridlines visible;
- avoid hidden mutations, persistence, canonicality changes, or domain-specific decisions.

The renderer must not:

- query PostgreSQL/Google Sheets itself;
- interpret arbitrary SQL or client expressions;
- choose authorization scope;
- infer which rows should be exported;
- depend on a specific Inventory preset;
- hard-code future user-created table definitions.

## Inventory adapter

For F6E Inventory, the existing View Engine remains the authority for:

- preset selection;
- registered field validation/order;
- Search/review filters;
- validated sort keys/directions;
- provider query semantics;
- the 5,000-row bounded export cap.

The Inventory adapter converts the resolved `ViewColumn` + `FieldDefinition` metadata into the generic workbook specification and calls the shared renderer.

Current system presets use their existing names and visible structures as the worksheet/export identity. Later user-owned View Builder definitions must be able to call the same renderer without creating a second Excel implementation.

## Presentation baseline

Default workbook styling:

- header fill: professional dark blue;
- header font: bold white;
- freeze pane: `A2`;
- text wrapping: enabled;
- vertical alignment: centered;
- header horizontal alignment: centered;
- cell borders: thin grid borders;
- table filters: enabled through an Excel Table;
- column sizing: content-aware with minimum/maximum bounds;
- row sizing: content-aware approximation for wrapped cells;
- date format: `yyyy-mm-dd`;
- integer format: `0`;
- decimal format: `0.###`.

These are shared defaults, not Inventory-only styling. Future export consumers may provide bounded presentation overrides without bypassing data validation or authorization.

## Security and authority

Excel export is read-only. It must not accept mappings, update catalogue prices, mutate inventory, accept a migration baseline, or promote PostgreSQL.

Source strings beginning with formula-significant characters such as `=`, `+`, `-`, or `@` must remain literal cell text. The generic renderer is the final defense for this workbook-level safety property.
