# Medicine Store Assistant — New Chat Bootstrap

Use this file for **project-development continuity and memory reconciliation** in a fresh chat.

This file is not the same as `NORMAL_CHAT_BOOTSTRAP.md`:

- `NORMAL_CHAT_BOOTSTRAP.md` teaches a normal chat how to load and operate the published `$msa` skill against the authorized workbook.
- `NEW_CHAT_BOOTSTRAP.md` restores the **project-development checkpoint**: architecture, implementation status, locked decisions, current risks, and next authorized slice.

## Canonical repository

`https://github.com/Ye-Shwethway/medicine-store-assistant`

## Required reconciliation order

At the start of a development chat, read and reconcile in this order:

1. `AGENTS.md`
2. `NEW_CHAT_BOOTSTRAP.md`
3. `ROADMAP.md`
4. `docs/architecture/README.md`
5. the task-relevant architecture documents referenced there
6. `skills/medicine-store-assistant/SKILL.md` and only the task-relevant skill references when spreadsheet operations are involved
7. current repository code/config/runtime evidence once implementation exists

Treat newer verified repository/runtime evidence as authoritative over remembered chat context.

Do not modify production, the live workbook, backend state, deployment, schema, or integrations during reconciliation unless the user explicitly authorizes implementation.

## Project identity

Medicine Store Assistant has evolved from a Git-backed Google-Sheets workflow skill into a broader medicine-store information system while preserving the published skill as a first-class component.

The same repository is intentionally used as a monorepo-style project:

- `skills/medicine-store-assistant/` — canonical published Git-backed skill; invocation alias `$msa`
- `docs/architecture/` — canonical database/API/system design contract
- future `backend/` — deterministic inventory API and domain logic
- future `integrations/` — Custom GPT, Google Sheets, Telegram, Flutter adapters
- future `deploy/` — VPS deployment/runtime configuration templates

The skill folder must remain independently installable and must not be moved, renamed, or buried by backend work.

## Current authoritative operational state

The live Google workbook remains authoritative under the existing MSA skill until database promotion is explicitly completed after shadow validation.

Current operational model:

- `Main Stock` — primary lot-level inventory operational view
- `Daily Usage` — primary monthly usage operational view
- `This Month Received` — display-only/filtered projection of received activity, not an independent source of truth
- `Reorder` / `Final Reorder` — workflow/display projections; the working reorder result can be manually reviewed/edited before final submission
- `Final Reorder` becomes a historical business record only when the approved final result is saved as part of the month archive/snapshot

Daily Usage synchronization contract already established in the live workbook:

- Main `A/B/F/G/C` → Daily `A/B/C/D/AM`
- Daily `E:AI` = day 1–31 usage inputs
- Daily `AJ = SUM(E:AI)`
- Daily `AK = C + D - AJ`
- Daily `AJ` → Main `J This Month Usage`
- Daily `AK` → Main `H Stock Status Today`
- never write calculated current balance back to Main `F Remaining Stock`

The live Daily Usage parity repair and full calculation/reverse-sync pass were completed before the architecture phase. Future work must not assume remembered row numbers; inspect live state when spreadsheet work resumes.

## Locked architecture direction

Architecture is docs-first. Implementation has **not yet been authorized**.

Planned target architecture:

```text
MSA Custom GPT ─┐
Telegram ───────┼──> Inventory API on VPS ───> PostgreSQL
Flutter ────────┘              │
                               ├──> Google Sheets operational mirror
                               └──> Excel monthly exports/archive representations
```

Infrastructure direction:

- reuse existing VPS rather than requiring paid Cloudflare data services
- PostgreSQL on VPS is the planned canonical database after successful migration
- Cloudflare Free + custom subdomain may provide stable DNS/TLS/public entry routing
- repository remains public; never commit secrets or operational/private data
- GitHub is code/docs distribution, not canonical operational data storage

AI-access direction:

- primary experiment: dedicated private Custom GPT using **GPT Actions → VPS API**
- expose only typed domain operations through an OpenAPI schema
- never expose arbitrary SQL or database credentials to an LLM/client
- if Custom GPT Actions prove unsuitable, Google Sheets can remain a controlled bridge/fallback while the backend stays API-first

## Canonical data principles

The planned database must not copy spreadsheet row identity directly.

- stable `product_id` identifies a local product
- stable `lot_id` identifies an expiry/stock lot
- spreadsheet row order is presentation metadata only
- CMS code is external/versioned catalogue identity and is never a permanent local primary key by itself
- stock movement is ledger/event based: opening, receipts, usage, approved adjustments
- derived balances must be reproducible deterministically from canonical movements
- historical operational records are not hard-deleted merely because a row disappears from a current sheet

## Monthly-history direction

The existing Excel Master concept remains important but is translated into database history rather than duplicated spreadsheet tables.

The database should preserve enough canonical history and immutable closed-month snapshots to regenerate familiar monthly outputs:

- Main Stock
- Daily Usage
- This Month Received
- Final Reorder

`This Month Received` and working reorder views remain projections. The final user-approved reorder output may be snapshotted at month close.

Month close must preserve effective dates, receipts, usage, closing stock, relevant configuration, and approved reorder output without destructive reset of historical transactions.

## CMS catalogue direction

Full CMS catalogue versions should be retained in the database after migration rather than storing only currently matched store rows.

Each catalogue import should be versioned with source metadata/hash where appropriate and support deterministic diffs for:

- new/removed catalogue rows
- price changes
- description/identity changes
- store-linked mapping changes

The operational Google workbook may continue showing only the latest active catalogue.

## Integrity model

The backend, not the LLM, must own deterministic data integrity.

Required design principles include:

- typed domain operations
- authentication and authorization
- idempotency keys for replay/duplicate safety
- database constraints and foreign keys
- atomic transactions
- append-only or correction-safe audit events
- explicit adjustment/reversal patterns instead of silent history edits
- read-back/verification
- reconciliation invariants
- backup and recovery
- no canonical promotion merely because PostgreSQL is deployed

## Migration direction

Use staged migration; no big-bang cutover.

1. architecture approval
2. backend/database foundation
3. import current Sheet state into a shadow database
4. reconcile DB projections against the live workbook
5. run dual/shadow validation for representative receipts, usage, month logic, catalogue history, and reorder outputs
6. promote PostgreSQL to canonical only after explicit user approval and verified parity
7. convert Google Sheets to synchronized operational mirror
8. add/expand Custom GPT, Telegram, Flutter clients against the typed API

Until step 6, current Sheet/source-document authority remains unchanged.

## Current documentation checkpoint

Canonical architecture documents exist under `docs/architecture/` covering:

- canonical inventory architecture
- inventory data model
- monthly lifecycle
- CMS catalogue versioning
- inventory integrity and audit
- Sheet/Excel mirror compatibility
- API/client architecture
- migration and shadow validation
- architecture decisions/open questions

Recent clarification already incorporated:

- `This Month Received` is display-only projection: No., Items, Sub Store Qty, Received Qty, Unit, Expiry Date, Remark
- it simply presents relevant received rows from Main Stock/current receipt state
- `Final Reorder` is also a workflow/display output
- Main Stock already contains the estimated reorder calculation; a working Reorder sheet synchronizes it, then the user may copy/edit the final submission
- do not create unnecessary independent canonical tables for these UI sheets

## Current implementation status

**Architecture/documentation phase only.**

Not yet implemented:

- PostgreSQL schema/migrations
- inventory backend API
- VPS deployment
- production subdomain/API routing
- Custom GPT Action schema/runtime connection
- Google Sheets backend mirror service
- Telegram inventory client
- Flutter inventory client
- database canonical promotion

Do not describe any of these as live.

## Next planning gate

Before implementation, review the architecture bundle for remaining domain gaps and explicitly approve the first minimal implementation slice.

The expected first implementation slice should be small and reversible, likely a local/VPS-safe backend foundation with no production canonical write authority yet. Exact scope must come from `ROADMAP.md` plus explicit user approval.

## Continuity maintenance rule

After every significant architecture decision, completed implementation slice, migration result, deployment change, or change to the next authorized work:

- update `ROADMAP.md`
- update this `NEW_CHAT_BOOTSTRAP.md`
- update task-specific canonical docs when the underlying contract changed

A fresh chat must be able to recover the current project checkpoint from repository documents without relying on remembered conversation history.
