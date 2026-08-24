# F6E Inventory View Runtime Verified — 2026-08-25

Status: **RUNTIME VERIFIED — read-only configurable Inventory View substrate + first Web renderer**

## Scope

This checkpoint verifies the first F6E Inventory View Engine slice after the Web Inventory section was moved away from the old staged-source-row grid.

The implementation remains shadow/read-only. It does not accept the migration baseline, promote PostgreSQL, accept CMS mappings, write accepted operational prices or enable production inventory mutation.

## Architecture preserved

- Main Stock and Migration Review are system presets over one reusable View Engine.
- Preset columns come from the typed field/computation registry.
- The Web renderer generates headers/cells from returned column metadata instead of one fixed Main Stock table.
- A caller may choose/reorder registered field keys; unknown/unregistered fields are rejected.
- User-defined saved views remain a later slice, but the current substrate proves that the renderer is registry-driven rather than screen-specific.
- Shadow Inspection remains a separate diagnostic surface.

## CI/browser verification

Dedicated Inventory View Engine CI passed:

- registry + preset contract;
- authenticated router binding contract;
- Inventory JavaScript syntax;
- Playwright interaction smoke at 390x844.

The browser smoke proves:

- the old product-facing Inventory subtree is replaced by the new renderer;
- Main Stock and Migration Review use one table component;
- preset switching works;
- registry-driven visible-column projection changes the rendered table and API field selection;
- search stays scoped to the selected preset;
- table overflow is locally owned on mobile;
- a real mobile shadow-banner overflow regression was detected and fixed before merge.

PR #165 merged as `3da90d7e1a26eaee23fc60c4dd9467012610c1ea` and production deployment completed successfully.

## Runtime projection evidence

Read-only self-hosted evidence in issue #166 verifies the live shadow DB through the same View Engine projection providers:

- Products: **670**;
- Lots: **799**;
- inventory transactions: **679**;
- Main Stock projected rows: **799**;
- Migration Review projected rows: **823**;
- Main Stock current quantity sum: **72,009.000**;
- active accepted CMS mappings: **0**;
- accepted operational prices: **0**;
- mutation: **false**;
- `database_canonical=false`;
- `migration_baseline_accepted=false`.

Runtime proof workflow run: `32764015596`.

## Acceptance conclusion

The first configurable read-only Inventory View substrate is accepted for continued F6E work. It is now safe to build review functionality on top of this renderer without converting the presets into fixed database-shaped screens.

## Next bounded slice

1. source-vs-shadow compare detail for Migration Review;
2. HOLD/review filters and clear unresolved-state presentation;
3. CMS Mapping Review as another system preset over the same engine;
4. selection/context substrate for the later embedded AI copilot;
5. no accepted mapping or inventory mutation until typed review/acceptance flows are separately implemented and authorized.
