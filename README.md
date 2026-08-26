# Medicine Store Assistant

Public, Git-backed source for the current `medicine-store-assistant` workflow (`$msa`) **and** the separately implemented standalone Medicine Store Assistant product.

## Two related layers, one repository

This repository intentionally contains two sibling tracks that share business semantics but do not share automatic runtime authority.

### 1. Current direct-use `$msa` skill

The canonical published skill lives under `skills/medicine-store-assistant/`.

Today, when `$msa` is invoked in an authorized ChatGPT/Codex session, it operates the live Google workbook directly through the tools/capabilities available to that session. Its operational contract is defined by the skill and its references.

The skill currently handles, among other things:

- CMS batch and supply intake;
- Daily Usage entry and Main Stock synchronization;
- CMS price-list and identity reconciliation;
- expiry-lot handling;
- fixed-asset routing;
- `Item_Mapping` mapping memory;
- reorder/usage evidence and review rules;
- exact-cell visual marking;
- pre-mutation restore checkpoints, read-back verification, and audit logging.

The live authorized Google workbook and exact source documents remain the operational authority for this direct-use workflow unless an explicit later migration decision says otherwise.

### 2. Standalone MSA product implementation

The same repository also contains a separate product implementation track: VPS backend, Web frontend, PostgreSQL/shadow inventory foundation, LLM API integration, MCP/internal-agent workflows, and future client integrations.

These areas are siblings of the skill. Code existing in `backend/`, Web/client areas, deployment assets, or MCP workflows does **not** mean the current `$msa` skill automatically uses or has authority over them.

PostgreSQL remains non-canonical until explicit migration/reconciliation gates are passed. Shadow/runtime values must not be substituted for current live-store truth.

## Legacy Excel workbook role

The original macro-enabled Excel workbook is treated as a **behavioral specification and historical design source**, not something the modern system must copy literally.

Useful business behavior can be preserved or improved—for example expiry-aware local pricing, reorder baselines, early-depletion signals, received-stock reconciliation, monthly history, and usage analysis—while long formulas, VBA orchestration, hidden helper mechanics, old cloud-sync macros, and workbook-specific UI complexity may be replaced by simpler explicit rules, typed backend logic, and human/AI-assisted review.

The goal is behavioral continuity with a simpler and more refined system, not hard copy-cat implementation.

## Current operational scope

- CMS batch and supply intake
- Daily Usage entry from paper forms or images
- Main Stock ↔ Daily Usage synchronization and calculation workflow
- CMS price-list and missing-code reconciliation
- clinically aware local-to-CMS identity matching
- durable `Item_Mapping` evidence registry and explicit exclusions
- fixed-asset routing
- expiry-aware operational review
- reorder baseline plus human/AI reasoned adjustment guidance
- actual early-depletion/stock-out signal interpretation
- exact-cell visual marking for writes, reviews, and conflicts
- full-workbook pre-mutation checkpoints, read-back verification, and audit guidance

## Architecture direction

The standalone target system separates AI interpretation from deterministic inventory integrity:

```text
MSA Web / Chat / Clients ─┐
Telegram / MCP agents ────┼──► Inventory API on VPS ───► PostgreSQL
Other clients ────────────┘              │
                                         ├──► Google Sheets operational bridge
                                         └──► Excel exports / backups
```

Key principles:

- PostgreSQL is the planned/future canonical transaction datastore only after explicit promotion; it is currently shadow/non-canonical.
- Google Sheets remains the present operational source for the direct `$msa` workflow and a human-facing compatibility surface.
- Excel remains a supported legacy/reference/export representation where useful.
- CMS catalogue versions should be retained historically while active operational views can focus on the current catalogue.
- deterministic code owns arithmetic, balances, idempotency, transactions, and typed derived state;
- AI interprets documents, clinical/product semantics, seasonality, anomalies, trade-offs, and review context;
- reorder and request quantities should use a reproducible baseline plus explainable human/AI adjustment rather than one rigid universal formula;
- no client or agent receives arbitrary SQL access.

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

Reading this repository does not itself grant spreadsheet, VPS, database, MCP, or other operational access.

## Repository layout

Canonical skill/current direct workflow:

- `skills/medicine-store-assistant/` — canonical published `$msa` skill and operational references
- `.codex-plugin/plugin.json` — plugin manifest
- `.agents/plugins/marketplace.json` — Git-backed marketplace entry
- `.github/workflows/validate-skill.yml` — structural validation workflow
- `scripts/validate_repository.py` — repository validator

Standalone product/design/implementation siblings:

- `docs/architecture/` — canonical design for the future/candidate database/API system
- `backend/` — deterministic Inventory API, domain logic, PostgreSQL migrations and shadow/runtime implementation
- `integrations/custom-gpt/` — Custom GPT Action/OpenAPI contract where applicable
- `integrations/google-sheets/` — operational bridge/mirror integration
- `integrations/telegram/` — Telegram adapter
- `integrations/flutter/` — Flutter client integration
- `deploy/` — VPS deployment assets

The implementation areas must not move, weaken, or silently redefine the Git-backed skill path.

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

## Implementation and canonicality gate

Do not infer production backend authority from implemented code alone. Review the full architecture bundle and runtime evidence before promoting any operation class.

The direct `$msa` Google-Sheets-first workflow remains operationally authoritative until an explicit later migration checkpoint says otherwise. Database/shadow/runtime functionality may be implemented and verified without becoming canonical.
