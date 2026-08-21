# Repository Rules

Treat `skills/medicine-store-assistant/` as the canonical Git-backed plugin skill source.

- Preserve the skill name `medicine-store-assistant` and invocation alias `$msa`.
- Keep `SKILL.md` concise: global rules and links only. Put workflow detail in its `references/` directory.
- Preserve exact source-document truth, expiry-separated lots, and the existing Excel/Google Sheets compatibility contract.
- Never commit credentials, access tokens, service-account JSON, live spreadsheet IDs, inventory exports, audit exports, or operational photos.
- Use runtime configuration or authorized live discovery for spreadsheet identity.
- Validate every change with `python scripts/validate_repository.py`.
- Bump `VERSION` and `.codex-plugin/plugin.json` together for release changes.
- Keep `.agents/plugins/marketplace.json` installable from the public Git repository.
- Update `NORMAL_CHAT_BOOTSTRAP.md` whenever the canonical skill path or startup contract changes.
- Do not add Telegram or autonomous write behavior until its authentication, dry-run, approval, idempotency, audit, and read-back design is explicit.
