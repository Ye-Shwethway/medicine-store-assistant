# Medicine Store Assistant

Portable, public-safe source for the `medicine-store-assistant` workflow (`$msa`). It reconciles medical-store inventory through an authorized Google Sheet while preserving the existing Excel/macro contract, source-document truth, expiry-separated lots, and cautious CMS identity matching.

## Current scope

- CMS batch and supply intake
- Daily Usage entry from paper forms or images
- CMS price-list and missing-code reconciliation
- Exact-cell visual marking for writes, reviews, and conflicts
- Read-back verification and significant-operation audit guidance

The repository currently contains the workflow layer only. The planned Telegram/runtime implementation will be added separately without weakening the spreadsheet safety contract.

## Use from a normal ChatGPT chat

1. Enable the GitHub and Google Drive plugins for the chat.
2. Give ChatGPT this repository URL.
3. Ask it to read and follow [`NORMAL_CHAT_BOOTSTRAP.md`](NORMAL_CHAT_BOOTSTRAP.md).
4. Confirm that the target Google Sheet is accessible before authorizing writes.

Reading this repository does not itself grant spreadsheet access. The active chat or runtime must provide an authorized Google Sheets capability.

## Security

This public repository must never contain Google credentials, service-account JSON, API keys, access tokens, inventory exports, audit exports, supply/usage photos, or patient-related data. Runtime identifiers and credentials belong in connector authorization or protected secrets.

## Layout

- `.agents/skills/medicine-store-assistant/` — canonical repo-scoped skill
- `.codex-plugin/plugin.json` — plugin-ready package manifest
- `.agents/plugins/marketplace.json` — repository marketplace entry
- `.github/workflows/validate-skill.yml` — quota-independent structural validation
- `scripts/validate_repository.py` — local and CI validator

