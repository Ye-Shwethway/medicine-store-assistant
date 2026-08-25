# Inventory Custom Table Builder v1

Status: **Authorized implementation contract for F6E Slice E2**

## Purpose

Allow each authenticated user to create a first-class custom Inventory table/view from registered Inventory data fields instead of only saving presentation changes from an existing system preset.

This slice builds on E1 saved-view persistence. It does not create arbitrary SQL tables and does not change inventory truth.

## Product model

A custom table is a user-owned persisted view definition with:

- a user-visible table name;
- a server-owned row source / row grain selected from an allowlisted Inventory source;
- an ordered list of mapped registered fields;
- a user-editable header label for every mapped field;
- optional per-column width and display metadata;
- the existing density/filter/sort/fill presentation state.

The user may start from a blank table builder and choose fields independently. A system preset is not required as the visible starting layout.

## Column identity and editable headers

Every custom column has two distinct identities:

- `field` — stable registered field key used for backend projection, validation, sorting, filtering and export semantics;
- `label` — user-editable display header shown in the Web table and persisted with the custom table.

Changing a label MUST NOT change the field mapping.

Example:

- field: `local_item_name`
- registry label: `Items`
- user label: `Medicine Name`

The backend still reads `local_item_name`; only the displayed/exported header changes.

Header labels:

- must be non-empty after trimming;
- are bounded to 120 characters;
- may repeat in v1 because mapping identity is the stable field key, not the label;
- are presentation metadata only.

## Row sources v1

The builder exposes only registered server-owned row sources derived from existing system providers:

1. **Main Stock / Product Lot**
   - provider: `lot_balance`
   - row grain: `PRODUCT_LOT`
   - store scope: `MAIN`

2. **Migration Review / Source Main Row**
   - provider: `migration_review`
   - row grain: `SOURCE_MAIN_ROW`
   - store scope: `MAIN`

3. **CMS Mapping Review / Product CMS Mapping**
   - provider: `cms_mapping_review`
   - row grain: `PRODUCT_CMS_MAPPING`
   - store scope: `ALL`

The browser never supplies SQL/provider expressions. It selects a registered row-source ID that resolves server-side.

## Field mapping

The builder may add fields only from `FIELD_REGISTRY` and only when the selected row source can project that field safely.

Each field can appear at most once in v1. The user can:

- add a field;
- remove a field;
- reorder fields;
- edit the header label;
- set/reset width;
- save the custom table;
- reopen/edit/delete it later.

At least one mapped field is required.

## Persistence shape

E2 extends the existing saved-view JSON definition without requiring a new physical table:

- `fields` remains the ordered stable field-key list for compatibility;
- `column_labels` is added as `{field_key: user_label}`;
- `column_widths` continues to be keyed by field key;
- existing density/filters/sort/fills remain unchanged.

`base_preset` remains stored as the server-owned row-source anchor for E2 compatibility, but the UI treats E2 custom tables as independently built tables rather than modified preset layouts.

## Web builder v1

Add a `New table` action to Inventory.

The builder UI must support:

1. table name;
2. row source selection;
3. available field list;
4. add/remove columns;
5. reorder columns;
6. inline editable header names;
7. width controls or reuse existing workbench width behavior;
8. Save / Cancel;
9. reopen an existing custom table in builder mode for structural edits.

The normal Workbench remains the table usage surface after saving.

## Excel/export contract

The reusable Excel renderer continues to own file generation.

For a custom table:

- field mapping determines cell values and number/date formats;
- user `column_labels` determine exported header text;
- persisted column order determines export order;
- no custom-table code forks a second Excel renderer.

## Authority and safety boundary

Custom tables MUST NOT:

- mutate Product, Lot, Store, Movement, Balance, CMS Mapping, catalogue prices or source evidence;
- create arbitrary SQL, raw expressions or executable formulas;
- change PostgreSQL canonicality or migration-baseline acceptance;
- become mutation-capable merely because a header or layout is editable.

The existing typed backend remains the authority for row projection.

## Calculated / derived columns

Calculated and derived columns are explicitly deferred from E2 v1.

Future work must define a typed safe expression model rather than arbitrary SQL or JavaScript formulas. Candidate capabilities include arithmetic over registered numeric fields, date-derived values, and allowlisted conditional expressions, but none are authorized by this slice.

## Acceptance proof

Behavior-level proof must cover:

1. create a new table from the `New table` action;
2. choose a row source;
3. add/remove/reorder mapped fields;
4. rename at least two headers and prove the underlying field mappings remain unchanged;
5. save and reopen the custom table;
6. edit the saved table structure and persist it;
7. verify Web headers use user labels;
8. verify row values still come from the correct registered field keys;
9. verify Excel export uses user labels and the saved order;
10. verify owner scoping and no inventory/CMS/canonical mutation;
11. verify mobile access to create/edit controls.
