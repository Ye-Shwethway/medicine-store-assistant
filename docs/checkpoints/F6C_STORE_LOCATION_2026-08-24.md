# F6C Store / Location Checkpoint — 2026-08-24

## Result

The minimum multi-store domain boundary is now clear enough to drive F6D schema parity.

## Source observations

- Product direction is one Main Store plus unlimited Sub Stores.
- The current live `Medicine Store Cloud` Main Stock populated range has no Store/Location/Sub Store field and is therefore a single implicit store context.
- Searching the current Main Stock used grid for `Sub Store` returned no matching rows.
- Existing inventory design already anticipated receipt `from_store` / `to_store` concepts and a legacy `Sub Store Qty` projection field.
- Current PostgreSQL foundation has products/lots and lot-only transactions, but no canonical stores table and no store/location foreign key on stock movements.

## Architecture decision

Lock:

> **Stock belongs to a location; product and catalogue identity do not.**

The same product/expiry lot may exist in Main Store and multiple Sub Stores. Location balance is derived per `(store_id, lot_id)` rather than duplicating product or lot identities per store.

## F6D implications

F6D must add a canonical store/location identity, location-aware movements, receipt destination location, store-scoped monthly snapshots, and explicit atomic internal-transfer semantics.

The existing F2 movement types are not sufficient for a real internal transfer. Transfer support must preserve source and destination effects as one typed business operation rather than unrelated adjustments.

## Still open

The following do not block the core schema model and remain later Owner/workflow decisions:

- Sub Store naming/code convention;
- user-to-store access scoping UX;
- whether Sub Store replenishment normally requests Main Store or can reorder externally;
- per-store versus global default reorder configuration policy.

## Boundary

No live Google Sheet mutation, inventory mutation, database migration, or canonical promotion occurred in this analysis.
