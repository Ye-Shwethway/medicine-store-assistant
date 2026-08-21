# Medicine Store Assistant — Project Roadmap

Status: **architecture/documentation phase**

This roadmap tracks the full Medicine Store Assistant project, not only the published `$msa` skill. It must stay synchronized with `NEW_CHAT_BOOTSTRAP.md` after significant changes.

## Project goals

Build a reliable medicine-store information system that preserves the familiar spreadsheet workflow while moving canonical data integrity into deterministic backend infrastructure.

Primary goals:

- preserve the published Git-backed `$msa` skill
- preserve source-document truth, lot separation, local naming, and Excel/Google Sheets compatibility
- make Main Stock and Daily Usage operational data reliable enough to support downstream workflows
- introduce stable product/lot identity independent of spreadsheet row number
- preserve complete monthly history
- preserve full CMS catalogue history/versioning
- replace fragile manual calculations/synchronization with deterministic backend logic
- expose a safe typed API for Custom GPT, Telegram, Flutter, and Sheet integration
- keep infrastructure cost low by reusing the existing VPS and Cloudflare Free/custom domain where useful
- avoid a big-bang migration

## Architecture baseline

Planned long-term topology:

```text
MSA Custom GPT ─┐
Telegram ───────┼──> Inventory API on VPS ───> PostgreSQL
Flutter ────────┘              │
                               ├──> Google Sheets operational mirror
                               └──> Excel monthly exports
```

GitHub remains code/docs distribution. Operational/private data and secrets must never be committed to the public repository.

## Phase 0 — Existing skill and workbook foundation

Status: **completed / active production workflow**

Established:

- canonical Git-backed skill at `skills/medicine-store-assistant/`
- `$msa` invocation alias
- source-authority hierarchy and cautious CMS identity matching
- fixed-asset boundary
- visual marking and read-back verification
- tab sequencing/persistence policy
- Main Stock new-lot insertion rules
- Daily Usage structural parity and bidirectional synchronization contract
- live Daily Usage parity repair completed
- live AJ/AK recalculation and Main H/J reverse synchronization completed

The Google workbook remains authoritative until database promotion is explicitly approved after shadow validation.

## Phase 1 — Canonical architecture documentation

Status: **in progress**

Completed design documents:

- `docs/architecture/CANONICAL_INVENTORY_ARCHITECTURE.md`
- `docs/architecture/INVENTORY_DATA_MODEL.md`
- `docs/architecture/MONTHLY_LIFECYCLE.md`
- `docs/architecture/CMS_CATALOGUE_VERSIONING.md`
- `docs/architecture/INVENTORY_INTEGRITY_AND_AUDIT.md`
- `docs/architecture/SHEET_MIRROR_AND_COMPATIBILITY.md`
- `docs/architecture/API_AND_CLIENT_ARCHITECTURE.md`
- `docs/architecture/MIGRATION_AND_SHADOW_VALIDATION.md`
- `docs/architecture/ARCHITECTURE_DECISIONS_AND_OPEN_QUESTIONS.md`

Clarifications locked:

- Main Stock and Daily Usage are primary operational views
- This Month Received is a display-only filtered projection, not an independent canonical data store
- working Reorder/Final Reorder sheets are workflow/display projections
- final user-approved reorder output may be preserved in the monthly snapshot/business history
- spreadsheet row numbers are not canonical identities
- full CMS catalogue versions should be retained in the database
- backend calculations and integrity must be deterministic rather than LLM-authored arithmetic
- same repository remains a monorepo-style project; published skill path stays stable
- Custom GPT Actions → VPS API is the preferred first direct AI-access experiment

Remaining Phase 1 work:

- review the architecture bundle for contradictions/gaps
- lock minimal v1 backend technology choices and API conventions
- define exact authentication model for the first private Custom GPT Action experiment
- define backup/restore baseline for the VPS database
- define first implementation slice before any production write authority is introduced

Exit criteria:

- architecture reviewed and explicitly approved
- first implementation slice explicitly authorized

## Phase 2 — Backend foundation

Status: **not started / not yet authorized**

Target minimal scope:

- create `backend/` sibling area without modifying the skill publishing path
- PostgreSQL schema/migration foundation
- stable product/lot IDs
- core receipt/usage/adjustment ledger primitives
- month entity and minimal monthly projection support
- catalogue-version persistence foundation
- audit/event infrastructure
- typed API skeleton
- health/read-only diagnostics

Safety boundary:

- no production canonical promotion
- no autonomous Sheet overwrite
- no arbitrary SQL exposure
- secrets only in runtime/VPS secret configuration

## Phase 3 — Shadow migration and reconciliation

Status: **not started**

Goals:

- import current live Sheet state into shadow PostgreSQL
- preserve source provenance and migration metadata
- reconcile product/lot identities
- compare backend-derived current stock against Main Stock
- compare usage projections against Daily Usage
- verify received projections
- validate current reorder calculations against existing workbook behavior
- import/retain catalogue versions as available

Exit criteria:

- material differences explained or resolved
- no unexplained silent divergence
- migration can be repeated idempotently

## Phase 4 — Dual validation

Status: **not started**

Run representative real operations through both the current workflow and backend shadow path:

- batch receipt intake
- new expiry lot
- daily usage
- adjustment/correction
- monthly received projection
- reorder projection
- month-close/archive dry run
- catalogue update/version diff

Backend must prove deterministic parity and auditability before promotion.

## Phase 5 — Canonical database promotion

Status: **not started; explicit approval required**

Only after successful shadow/dual validation:

- promote PostgreSQL to canonical operational source of truth
- preserve ledger and monthly history
- make Google Sheets a synchronized operational mirror
- keep Excel as export/archive/compatibility representation
- enable divergence detection and controlled Sheet-originated operations

Promotion must be a deliberate project event with rollback/recovery plan.

## Phase 6 — Custom GPT Action integration

Status: **planned experiment**

Preferred direct AI path:

```text
Private MSA Custom GPT
        ↓ typed Actions
Inventory API
        ↓
PostgreSQL
```

Requirements:

- OpenAPI schema version controlled under future `integrations/custom-gpt/`
- API-key or other approved authentication
- no arbitrary SQL
- narrow domain actions such as read stock, record usage, submit receipt, reconcile, query audit
- backend validation/idempotency/transaction/audit on every write
- clear read-back result to the GPT

If this path proves unavailable or unsuitable, retain Google Sheets as a controlled AI bridge/fallback without changing backend domain architecture.

## Phase 7 — Google Sheets backend mirror

Status: **not started**

After database promotion:

- database-to-Sheet projection becomes normal direction
- Main Stock and Daily Usage remain familiar human views
- This Month Received and reorder views are generated projections
- Sheet-originated edits require typed controlled ingestion rather than unrestricted last-write-wins sync
- mirror failures must not replay canonical stock movements

## Phase 8 — Telegram client

Status: **future**

Potential capabilities:

- current stock lookup
- low/reorder alerts
- expiry alerts
- controlled usage/receipt operations
- reconciliation/status messages
- optional AI assistance through API-backed domain commands

Authentication, authorization, approval, idempotency, audit, and read-back must be designed before write behavior.

## Phase 9 — Flutter application

Status: **future**

Potential role:

- full operational UI
- product/lot browsing
- usage/receipt entry
- monthly views/history
- reorder review
- catalogue/history inspection
- audit/reconciliation UI

Flutter must consume the same typed API rather than introducing a second data model.

## Phase 10 — Mature monthly archive/export

Status: **future**

Provide historical month selection and reproducible exports including familiar outputs:

- Main Stock
- Daily Usage
- This Month Received
- Final Reorder

Potential compatibility target:

- clean `.xlsx` export
- optional established workbook-template compatibility
- historical re-export from canonical database at any time

## Cross-cutting reliability work

Required throughout the project:

- idempotency
- foreign-key/uniqueness constraints
- atomic transactions
- append-only/correction-safe audit
- explicit adjustments/reversals
- source provenance
- deterministic calculation functions
- backup and restore testing
- divergence detection
- secrets management
- least-privilege client permissions
- no silent data repair by AI

## Current checkpoint

Current phase: **Phase 1 — architecture documentation**.

No backend/database implementation has started.

Immediate next step after documentation review:

> Define and approve the smallest Phase 2 backend-foundation slice. It should establish local/VPS-safe infrastructure and read-only/isolated primitives first, without declaring PostgreSQL canonical or giving any external client production write authority.

## Continuity rule

After every significant architecture decision, implementation slice, deployment change, migration/reconciliation result, or change in the next authorized work:

1. update this `ROADMAP.md`
2. update `NEW_CHAT_BOOTSTRAP.md`
3. update the relevant canonical architecture/skill reference document

A new chat must be able to determine completed work, current truth, and the next authorized slice from these documents alone.
