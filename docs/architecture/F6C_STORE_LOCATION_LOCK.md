# F6C — Store / Location Lock

Status: **LOCKED FOR F6D SCHEMA PARITY**

This short lock file points to the canonical store/location architecture in `STORE_LOCATION_MODEL.md`.

Core rule:

> **Stock belongs to a location; product and catalogue identity do not.**

F6D must make stock movements, balances, receipts, monthly snapshots and future reorder scope location-aware while preserving shared Product/Lot/CMS identities across one Main Store and unlimited Sub Stores.

Current live `Medicine Store Cloud` remains a single implicit Main Store compatibility source because its populated Main Stock / Daily Usage contracts contain no store/location field.

The current PostgreSQL foundation is not yet multi-store capable because `inventory_transactions` is lot-only and there is no canonical stores/location entity.

Internal transfer must be a typed atomic business operation with linked source-decrease and destination-increase effects. It must not be represented as unrelated manual adjustments.

See:

- `docs/architecture/STORE_LOCATION_MODEL.md`
- `docs/checkpoints/F6C_STORE_LOCATION_2026-08-24.md`
- `docs/architecture/INVENTORY_DATA_MODEL.md`
- `docs/architecture/F2_SCHEMA_DECISION_PROPOSAL.md`

No production mutation or canonical promotion is authorized by this lock.
