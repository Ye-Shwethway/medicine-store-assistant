# F6D Main Materialization + Live CMS Catalogue Checkpoint — 2026-08-25

Status: **VERIFIED SHADOW MILESTONE — PostgreSQL remains non-canonical**

Authority flags remain:

- `database_canonical=false`
- `migration_baseline_accepted=false`
- live Google workbook/source evidence remains operationally authoritative

## Fresh Main Store source

Fresh source batch:

- migration batch `7ecf9a2b-0521-400d-8990-caaea20d3a57`
- source hash `c212d7da6192e7e20f340e7b302436f588dfb0fa191459fd572dfdb46f23ba76`
- Main Stock source rows `823`
- Daily Usage source rows `823`
- total staged source records `1646`

`1646` is source evidence count, not canonical inventory count. Main Stock is migration-primary; Daily Usage is joined evidence only.

## Source-safe Main-primary materialization

Runtime materialization completed successfully from the guarded Main Stock subset:

- Products persisted: `670`
- Lots persisted: `799`
- positive-balance migration `OPENING_BALANCE` transactions: `679`
- opening quantity sum: `72009`
- zero-balance identity-only Lots: `120`
- balance readback mismatches: `0`

Immediate replay created:

- Products: `0`
- Lots: `0`
- inventory transactions: `0`

Replay therefore proved idempotency for the exact fresh source batch.

### Explicit HOLDs

No source ambiguity was guessed or silently corrected.

Held outside materialization:

- 14 inventory-semantic review rows;
- duplicate Product+Expiry rows `41,42,156,157`;
- missing/conflicting Unit rows `237,245,459,460,461,601`.

The Unit conflict for normalized `O' Coamoxiclav 625` is preserved as source ambiguity rather than collapsed across `Tab/Cap/Tab` evidence.

No Product-CMS mappings were created by materialization.

## First live CMS catalogue version

The live `CMS_Price_List_202608` source was first preflighted read-only, then imported using an exact source-hash guard.

Source/version evidence:

- title: `August 2026 Updated Price List (Yuan) - 02.08.2026`
- effective date: `2026-08-02`
- source hash: `6f221152024c9a06b73f7f7115097abfb688a37a6ba6bf0be78345f3b70dd116`
- catalogue version ID: `34947c29-6427-4b7c-9fb8-ba8ffe3278b0`
- parsed/persisted rows: `6891`
- unique codes: `6891`
- duplicate codes: `0`
- blank codes: `0`
- invalid prices: `0`
- blank source selling-price rows: `6442` only

Source row `6442`, CMS code `S10105035`, has a blank Selling Price. The shadow catalogue preserves this as `NULL`; no price is inferred.

Immediate replay returned the same catalogue version with `created=false`, proving source-hash idempotency.

## Catalogue isolation proof

Protected local-domain counts before and after catalogue import were identical:

- Products `670`
- Lots `799`
- inventory transactions `679`
- Product-CMS mappings `0`

The catalogue import therefore changed catalogue reference data only. It did not:

- remap local Products;
- update local operational prices;
- rewrite inventory balances or movements;
- promote PostgreSQL authority.

## Next bounded slice

Build a **read-only CMS assisted-reconciliation planner** using:

- materialized local Product identity;
- fresh Main Stock source evidence (`serial_code`, `cs_name`, local name, remark, mapping hint, source price evidence);
- imported catalogue version `34947c29-6427-4b7c-9fb8-ba8ffe3278b0`.

Deterministic screening must precede AI reasoning. Code equality is evidence, not identity proof. Preserve uncertainty for recycled/discontinued/history/local-error cases. Keep `product_cms_mappings=0` until a later separately reviewed mapping-acceptance slice.