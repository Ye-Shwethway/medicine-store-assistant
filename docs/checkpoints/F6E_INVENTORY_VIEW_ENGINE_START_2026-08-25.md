# F6E Inventory View Engine Start — 2026-08-25

Status: **STARTED — read-only substrate; no canonical promotion**

## Owner-confirmed direction

The Web Inventory section must not be rebuilt as a fixed Main Stock/Daily Usage display. Main Stock, Daily Usage, Migration Review and CMS Mapping Review are system presets over one configurable sheet-style View Engine.

Users must later be able to create their own table layouts by binding columns to registered domain fields, computations and typed-command edit semantics. No custom view may expose arbitrary SQL or arbitrary raw database mutation.

## Current verified shadow state entering this slice

- PostgreSQL remains non-canonical.
- `database_canonical=false`.
- `migration_baseline_accepted=false`.
- shadow Products: 670.
- shadow Lots: 799.
- opening movements: 679, quantity sum 72,009.
- CMS catalogue: 1 version / 6,891 items.
- CMS mapping review-state rows: 670.
- accepted `ACTIVE_MATCH`: 0.
- accepted operational prices: 0.
- Google Sheet/source documents remain operationally authoritative.

## First implementation slice

Add a registry-driven read-only View Engine substrate:

1. typed field registry;
2. system view definitions;
3. Main Stock preset at Product-Lot grain;
4. Migration Review preset at source-Main-row grain;
5. generic projection renderer with validated caller-selected registry fields;
6. explicit read-only/non-canonical response state;
7. no editing, mapping acceptance, price update or inventory mutation.

## Transition model

The same Inventory UI is intended to serve both migration review and future production operation:

`shadow projection -> source comparison/review -> baseline acceptance -> promoted DB read paths -> typed write promotion`

The migration-review UI is therefore a system preset within the reusable engine, not a disposable one-off screen.

## AI boundary

Inventory becomes the primary visual review/work surface. Embedded AI assistance will later receive selected-row/view/filter evidence and may propose actions. Difficult cases may escalate to AI Workspace/multi-agent review. AI does not own acceptance authority and does not bypass typed command confirmation.

## Next proof after this checkpoint

- wire the engine into the authenticated dashboard API;
- render the Main Stock system preset in Web without worksheet-shaped hard-coding;
- render Migration Review through the same table component;
- expose preset/field selection in the UI;
- keep old shadow diagnostic data under an Admin/Shadow inspection surface rather than using it as the product-facing Inventory table;
- add browser behavior verification before considering the read-only Inventory rewrite accepted.
