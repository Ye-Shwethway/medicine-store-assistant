# Repository Rules

Treat `skills/medicine-store-assistant/` as the canonical Git-backed plugin skill source.

- Preserve the skill name `medicine-store-assistant` and invocation alias `$msa`.
- **Do not move, rename, repurpose, or bury `skills/medicine-store-assistant/` when adding backend/runtime code.** The published Git-backed skill must remain independently installable from this repository.
- Keep `SKILL.md` concise: global rules and links only. Put workflow detail in its `references/` directory.
- Preserve exact source-document truth, expiry-separated lots, and the existing Excel/Google Sheets compatibility contract.
- Treat `docs/architecture/` as the canonical design contract for the planned database/API system. Keep architecture, data model, integrity, monthly lifecycle, client API, mirror, and migration documents mutually consistent.
- **Docs first, implementation second.** Do not create production database migrations, backend write paths, Custom GPT write Actions, Telegram write behavior, or database-canonical promotion until the relevant architecture is explicitly reviewed/authorized.
- Future implementation belongs in sibling areas such as `backend/`, `integrations/`, and `deploy/`; it must not replace the skill structure.
- PostgreSQL/VPS implementation must use typed domain operations and deterministic integrity controls. Never expose arbitrary SQL or database credentials to GPT, Telegram, Flutter, or Google Sheets clients.
- The current Google-Sheets-first workflow remains authoritative until the migration plan explicitly promotes the database after shadow validation.
- Never commit credentials, access tokens, service-account JSON, live spreadsheet IDs, inventory exports, audit exports, migration snapshots, operational photos, production database dumps, or other private operational data.
- Use runtime configuration or authorized live discovery for spreadsheet/database identity.
- Validate every change with `python scripts/validate_repository.py` when the validator is available in the execution environment.
- Bump `VERSION` and `.codex-plugin/plugin.json` together for release changes. Architecture documentation drafts alone do not automatically require a plugin release bump unless they change the published skill contract.
- Keep `.agents/plugins/marketplace.json` installable from the public Git repository.
- Update `NORMAL_CHAT_BOOTSTRAP.md` whenever the canonical skill path or startup contract changes.
- Do not add Telegram or autonomous write behavior until its authentication, dry-run/preview where appropriate, approval, idempotency, audit, rollback, and read-back design is explicit.
- Do not declare PostgreSQL the canonical source of truth merely because it is deployed. Canonical promotion requires the staged reconciliation and shadow-validation process in `docs/architecture/MIGRATION_AND_SHADOW_VALIDATION.md`.
