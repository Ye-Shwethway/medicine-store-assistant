# Medicine Store Assistant

Public, Git-backed plugin source for the `medicine-store-assistant` workflow (`$msa`). It reconciles medical-store inventory through authorized Google Sheets while preserving the existing Excel/macro contract, source-document truth, expiry-separated lots, and cautious CMS identity matching.

## Current scope

- CMS batch and supply intake
- Daily Usage entry from paper forms or images
- CMS price-list and missing-code reconciliation
- Exact-cell visual marking for writes, reviews, and conflicts
- Read-back verification and significant-operation audit guidance

The repository currently contains the workflow layer only. The planned Telegram/runtime implementation will be added separately without weakening the spreadsheet safety contract.

## Install as a Git-backed plugin

Register this public repository as a marketplace source:

```bash
codex plugin marketplace add Ye-Shwethway/medicine-store-assistant --ref main
```

Then refresh the supported ChatGPT or Codex surface, open the Plugins Directory, choose **Medicine Store Assistant**, and install the plugin. Start a new chat before invoking `$msa`.

To pull later releases:

```bash
codex plugin marketplace upgrade medicine-store-assistant-marketplace
```

Plugin availability and marketplace controls depend on the ChatGPT/Codex surface and account. The plugin supplies the MSA workflow; the active chat must also have authorized Google Drive/Google Sheets access.

## Direct Normal Chat fallback

If plugin installation is unavailable, enable GitHub and Google Drive for the chat, give ChatGPT this repository URL, and ask it to read and follow [`NORMAL_CHAT_BOOTSTRAP.md`](NORMAL_CHAT_BOOTSTRAP.md).

Reading this repository does not itself grant spreadsheet access. Confirm access before authorizing writes.

## Security

This public repository must never contain Google credentials, service-account JSON, API keys, access tokens, inventory exports, audit exports, supply/usage photos, patient-related data, or the live spreadsheet ID. Runtime identifiers and credentials belong in connector authorization or protected secrets.

## Layout

- `skills/medicine-store-assistant/` — canonical bundled skill
- `.codex-plugin/plugin.json` — plugin manifest
- `.agents/plugins/marketplace.json` — Git-backed marketplace entry
- `.github/workflows/validate-skill.yml` — quota-independent structural validation
- `scripts/validate_repository.py` — local and CI validator
