# Inventory Saved View Persistence v1

Status: **Authorized implementation contract for F6E Slice E1**

## Purpose

Persist user-owned Inventory view presentation state without changing inventory truth, system presets, CMS mapping state, prices, migration acceptance, or PostgreSQL canonicality.

This slice converts the proven session-only sheet/workbench state into an authenticated server-owned saved-view definition that can survive refresh/reopen and later feed the full View Builder.

## Authority boundary

Saved views are **presentation metadata only**.

They MUST NOT:

- mutate Product, Lot, Store, Movement, Balance, CMS Mapping, catalogue price, source evidence, or migration state;
- create arbitrary SQL, raw DB expressions, provider names, or executable formulas;
- alter system presets;
- become AI review evidence;
- imply `database_canonical=true` or `migration_baseline_accepted=true`.

The live Google/source documents remain operational authority. PostgreSQL remains shadow/noncanonical.

## Ownership model

- Every saved view belongs to one authenticated human `user_id`.
- A user may list/read/update/delete only their own saved views.
- System presets remain global immutable definitions.
- A custom view stores a validated `base_preset` pointing to an existing system preset.
- Provider, row grain and Store scope are inherited from the server-owned base preset in v1; the client cannot invent them.

## Persisted definition v1

A saved view stores:

- `view_id` — UUID owned by the server;
- `owner_user_id` — authenticated human principal;
- `name` — user-visible unique name per owner;
- `base_preset` — one of the registered system preset IDs;
- `fields` — ordered registered field keys only;
- `column_widths` — optional bounded widths keyed by registered field key;
- `density` — `comfortable` or `compact`;
- `filters` — bounded Search / mapping status / source classification / review reason values;
- `sort` — validated registered sortable field + `asc|desc`, or empty;
- `fills` — presentation-only cell fill entries keyed by stable row identity + registered field + bounded fill token;
- timestamps.

Allowed fill tokens remain: `yellow`, `green`, `red`, `blue`, `orange`, `gray`.

## Validation rules

- `base_preset` must exist in `SYSTEM_PRESETS`.
- `fields` must be non-empty, unique, and present in `FIELD_REGISTRY`.
- widths are bounded to practical workbench limits and may only target selected registered fields.
- sort is checked against the base preset provider's server-owned sortable allowlist.
- filters use the existing bounded lengths and are interpreted only by the existing provider query code.
- fill field keys must be registered fields; row keys are opaque presentation identities with bounded length; fill tokens are allowlisted.
- arbitrary JSON keys are rejected/ignored through a typed request model rather than stored as an executable document.

## API contract

Authenticated Inventory API gains:

- `GET /dashboard/api/inventory-view/saved-views`
- `POST /dashboard/api/inventory-view/saved-views`
- `PUT /dashboard/api/inventory-view/saved-views/{view_id}`
- `DELETE /dashboard/api/inventory-view/saved-views/{view_id}`

`GET /presets` remains the immutable system-preset registry. The browser merges those server-owned presets with the authenticated user's `/saved-views` list for one View selector.

When a saved view is selected, the browser rehydrates its validated presentation definition and requests rows through the existing `/rows` endpoint using its server-validated `base_preset`, registered field subset/order, filters and sort. `/rows` continues to validate every field/filter/sort coordinate; a saved definition never supplies SQL/provider expressions.

## Workbench v1 integration

E1 adds minimal persistence controls, not the full View Builder:

- `Save view` from a system preset creates a user-owned custom view after an explicit name prompt;
- `Save view` while an existing custom view is active updates that same user-owned definition;
- `Save as` duplicates the current state under a new user-owned name;
- `Delete view` is enabled only for an active custom view;
- saved views appear in the existing View selector with a clear `Custom ·` marker;
- reopening a saved view rehydrates fields/order/width/density/filter/sort/fill state;
- deleting a saved view returns safely to its base system preset;
- a system preset is never overwritten.

A one-click `Clear all` resets Search + review filters + sort only; it does not delete selection, column layout, fills, or saved-view definitions.

## Persistence proof

Behavior-level proof must cover:

1. save from a system preset;
2. same-tab selection of the new custom view;
3. server read-back of the authenticated saved definition;
4. refresh/reopen rehydration;
5. update existing custom view and `Save as` duplication;
6. owner scoping;
7. delete and fallback to base preset;
8. no inventory/CMS/canonicality mutation;
9. existing Ask AI / Deep Review remains formatting-blind and server-rehydrated;
10. mobile access to saved-view controls.

## Deferred to Slice E2/E3

- full row-grain / Store-scope builder UI;
- arbitrary label editing/grouping UI;
- richer conditional formatting;
- custom-view styled Excel parity beyond the persisted formatting handoff contract;
- sharing views between users;
- mutation-capable cells/paste/formulas.

Those remain separate later slices so E1 stays a small, auditable persistence foundation.