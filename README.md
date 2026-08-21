# Medicine Store Assistant

Public, Git-backed source for the `medicine-store-assistant` workflow (`$msa`) and its planned deterministic inventory backend.

The existing skill reconciles medical-store inventory through authorized Google Sheets while preserving the Excel/macro contract, source-document truth, expiry-separated lots, and cautious CMS identity matching.

The repository is now intentionally evolving as a **same-repository, separated-layer system**: the published skill remains stable under `skills/medicine-store-assistant/`, while future backend/runtime and client integrations are added as sibling areas rather than replacing the skill.

## Current operational scope

- CMS batch and supply intake
- Daily Usage entry from paper forms or images
- Main Stock ↔ Daily Usage synchronization and calculation workflow
- CMS price-list and missing-code reconciliation
- fixed-asset routing
- exact-cell visual marking for writes, reviews, and conflicts
- read-back verification and significant-operation audit guidance

The current live workflow is still Google-Sheets-first. The planned PostgreSQL/VPS system is **documentation/design only until implementation is explicitly authorized and shadow validation succeeds**.

## Architecture direction

The target system separates AI interpretation from deterministic inventory integrity:

```text
MSA Custom GPT ─┐
Telegram ───────┼──► Inventory API on VPS ───► PostgreSQL
Flutter ────────┘              │
                               ├──► Google Sheets operational mirror
                               └──► Excel monthly exports / backups
```

Key principles:

- PostgreSQL is the planned future canonical transaction datastore, but is not canonical until explicit promotion after shadow validation.
- Google Sheets remains a human-facing operational surface and compatibility bridge.
- Excel remains a supported monthly export/archive/report representation.
- CMS catalogue versions are planned to be retained historically in the database while the live workbook may show only the current active catalogue.
- AI may interpret documents and orchestrate typed actions; backend code/database constraints own arithmetic, idempotency, transactions, and derived state.
- No client receives arbitrary SQL access.
- The existing VPS and Cloudflare Free/custom-domain edge are preferred before adding recurring infrastructure cost.

Read the architecture bundle at [`docs/architecture/README.md`](docs/architecture/README.md).

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

Plugin availability and marketplace controls depend on the ChatGPT/Codex surface and account. The plugin supplies the MSA workflow; the active chat must also have the authorized capabilities required by the requested operation.

## Direct Normal Chat fallback

If plugin installation is unavailable, enable the required connected tools for the chat, give ChatGPT this repository URL, and ask it to read and follow [`NORMAL_CHAT_BOOTSTRAP.md`](NORMAL_CHAT_BOOTSTRAP.md).

Reading this repository does not itself grant spreadsheet, VPS, database, or other operational access.

## Repository layout

Current/canonical:

- `skills/medicine-store-assistant/` — canonical published skill
- `docs/architecture/` — canonical design for the future database/API system
- `.codex-plugin/plugin.json` — plugin manifest
- `.agents/plugins/marketplace.json` — Git-backed marketplace entry
- `.github/workflows/validate-skill.yml` — structural validation workflow
- `scripts/validate_repository.py` — repository validator

Reserved for future implementation after approval:

- `backend/` — deterministic Inventory API, domain logic, PostgreSQL migrations
- `integrations/custom-gpt/` — Custom GPT Action/OpenAPI contract
- `integrations/google-sheets/` — operational mirror integration
- `integrations/telegram/` — Telegram adapter
- `integrations/flutter/` — Flutter client integration
- `deploy/` — VPS deployment assets

The implementation areas are siblings of the skill. They must not move or weaken the Git-backed skill path.

## Security

This is a public repository. Never commit:

- Google credentials or service-account JSON
- API keys, bearer tokens, Telegram tokens, database passwords, or deployment secrets
- live spreadsheet IDs or production database connection strings
- inventory/audit exports or migration snapshots
- operational supply/usage photos
- patient-related or other private operational data
- production database dumps

Runtime identifiers and credentials belong in authorized connectors, VPS environment configuration, or another protected secret mechanism.

## Implementation gate

Do not begin production backend/database implementation from a single sketch. Review the full architecture bundle first, especially:

- canonical architecture
- inventory data model
- monthly lifecycle
- CMS catalogue versioning
- integrity/audit
- Sheet/Excel compatibility
- API/client boundaries
- migration and shadow validation

The current Google-Sheets-first workflow remains authoritative until an explicit later migration checkpoint says otherwise.
