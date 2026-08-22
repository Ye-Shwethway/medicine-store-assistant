# F6A — Synthetic Shadow Migration Adapter Foundation

Status: **authorized and authored; VPS verification pending**

F6A introduces migration provenance/staging only. It does not read the live Google workbook and does not create canonical inventory movements.

Included:

- `migration_batches` with source hash/idempotency metadata;
- `migration_source_rows` with sheet/row provenance, row hash, payload, classification, and review reason;
- deterministic synthetic Main Stock and Daily Usage fixture adapters;
- classification into `LOT_OPENING_CANDIDATE`, `USAGE_CANDIDATE`, or `REVIEW`;
- explicit reasons for review rows;
- repeat-snapshot idempotency;
- synthetic verifier proving no product or inventory-transaction rows are created by staging;
- migration readiness target `0004_shadow`.

Excluded:

- live Google workbook reads/imports;
- production stock writes;
- local identity auto-approval;
- database canonical promotion;
- Sheet mutation;
- Telegram, Flutter, or Custom GPT writes.
