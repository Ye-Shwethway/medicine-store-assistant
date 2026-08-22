# Medicine Store Assistant — Architecture Index

Status: **F7.2A canonical human identity/sessions verified; F7.2B User Management next; PostgreSQL remains non-canonical**

This directory defines the future canonical architecture for Medicine Store Assistant beyond the current spreadsheet-operating skill.

The existing Git-backed skill remains canonical at:

`skills/medicine-store-assistant/`

The architecture here must preserve the useful skill workflow while moving authority into durable typed backend contracts.

## Core decision

MSA evolves toward a ledger-backed multi-client inventory system in which:

- PostgreSQL on the VPS is the planned future canonical operational datastore, but is **not canonical yet**;
- the Inventory API is the only normal mutation boundary once DB writes are authorized;
- Google Sheets remains operationally authoritative until explicit promotion, then becomes a human-facing mirror/reconciliation surface for the promoted scope;
- Excel remains a compatible export/archive/report surface;
- Web, Telegram, Flutter, Custom GPT, internal AI, and other clients use typed API/BFF operations rather than direct DB writes;
- canonical human identities and separately managed AI/service principals provide durable actor attribution;
- AI interprets evidence, reconciles candidates, prepares proposals, and may later execute only Owner-authorized typed capabilities;
- deterministic backend code owns arithmetic, constraints, authorization/delegation, idempotency, transactions, derived state, and read-back verification;
- actor-aware Audit records who/what acted, under whose authority, through which client/location, and with what outcome;
- the current Google-Sheets-first workflow remains authoritative until migration/shadow-validation explicitly promotes the database.

## Current F7 architecture

F7.2A is deployed and runtime-verified. Human accounts now use the existing F2 canonical `users` / `roles` / `user_roles` foundation with stable UUID `user_id`, username + password, `PENDING` / `ACTIVE` / `DISABLED` state, durable DB-bound revocable sessions, backend role helpers, explicit authenticated 403 behavior, and disabled-user enforcement. This changed authentication/control-plane identity only; inventory remains read-only.

Current direction continues with:

- F7.2B User Management next;
- exactly one Main Store plus Owner-created Sub Stores later in F7.4;
- Owner-only global Settings in its later authorized slice;
- Owner-configurable reorder basis (`MAIN_STORE_ONLY` initially, later optional `TOTAL_ACTIVE_STOCK`);
- human User Management separate from Owner-only AI Agent Management;
- AI agents may be granted Main Store and/or Sub Store capabilities; they are not inherently Sub-Store-only;
- shared AI Chat may be enabled for Staff/Admin users, but effective authority remains the intersection of human authority, agent capability, location scope, and operation policy;
- Smart Calculator is DB-backed and calculation-only first;
- Smart Analysis is deterministic first, AI-assisted second;
- Alerts/Notifications reuse backend events across clients.

Verified F7.2A anchor: PR #36, merge `c3aa75d65e0bc6d1836227fe8450b0b3de5b2651`, deploy run `32586385336`. Deployment preserved `database_canonical=false`, `migration_baseline_accepted=false`, and performed no live workbook import or inventory mutation.

## Documents

1. [CANONICAL_INVENTORY_ARCHITECTURE.md](CANONICAL_INVENTORY_ARCHITECTURE.md) — system boundaries, SOT model, client roles, AI/code separation.
2. [INVENTORY_DATA_MODEL.md](INVENTORY_DATA_MODEL.md) — products, lots, transactions, receipts, usage, identity, lifecycle.
3. [MONTHLY_LIFECYCLE.md](MONTHLY_LIFECYCLE.md) — monthly lifecycle and Excel compatibility.
4. [CMS_CATALOGUE_VERSIONING.md](CMS_CATALOGUE_VERSIONING.md) — catalogue history, diffs, mappings, current-price projection.
5. [INVENTORY_INTEGRITY_AND_AUDIT.md](INVENTORY_INTEGRITY_AND_AUDIT.md) — constraints, idempotency, transactions, audit, verification, reconciliation, recovery.
6. [SHEET_MIRROR_AND_COMPATIBILITY.md](SHEET_MIRROR_AND_COMPATIBILITY.md) — Google Sheets mirror and Excel compatibility.
7. [API_AND_CLIENT_ARCHITECTURE.md](API_AND_CLIENT_ARCHITECTURE.md) — VPS API and client access paths.
8. [USER_ACCESS_AND_AUTHORIZATION.md](USER_ACCESS_AND_AUTHORIZATION.md) — canonical identity/access foundation.
9. [MIGRATION_AND_SHADOW_VALIDATION.md](MIGRATION_AND_SHADOW_VALIDATION.md) — migration and canonical-promotion safety.
10. [DECISIONS_AND_OPEN_QUESTIONS.md](DECISIONS_AND_OPEN_QUESTIONS.md) — locked direction and unresolved gates.
11. [F7_WEB_DASHBOARD.md](F7_WEB_DASHBOARD.md) — locked Dashboard v2.4 read-only foundation.
12. [F7_2D_AI_AGENT_MANAGEMENT.md](F7_2D_AI_AGENT_MANAGEMENT.md) — Owner-only AI/service principal management, capabilities, delegation, Main/Sub scope, and `$msa` workflow parity.
13. [F7_3_ACTOR_AUDIT_AND_OPERATION_LEDGER.md](F7_3_ACTOR_AUDIT_AND_OPERATION_LEDGER.md) — human/AI/system/integration provenance and operation ledger.
14. [F7_4_F7_8_STORE_AND_INTELLIGENCE_ARCHITECTURE.md](F7_4_F7_8_STORE_AND_INTELLIGENCE_ARCHITECTURE.md) — Main/Sub locations, Settings/preferences, Smart Calculator, Smart Analysis, AI Chat, Alerts.

`F7_4_F7_6_INTELLIGENCE_ARCHITECTURE.md` is superseded and retained only as a historical pointer.

## Repository boundary

```text
medicine-store-assistant/
├── skills/medicine-store-assistant/   # published Git-backed skill; preserve
├── docs/architecture/                 # canonical system design
├── backend/                           # deterministic API + DB + dashboard runtime
├── integrations/                      # GPT/Sheets/Telegram/Flutter adapters
├── deploy/                            # VPS deployment assets
├── AGENTS.md
├── NEW_CHAT_BOOTSTRAP.md
├── NORMAL_CHAT_BOOTSTRAP.md
└── ROADMAP.md
```

## Design rule

Do not implement from one document in isolation. `AGENTS.md`, `NEW_CHAT_BOOTSTRAP.md`, `ROADMAP.md`, `IMPLEMENTATION_PLAN.md`, the active F7 architecture/design docs, and current repository/runtime evidence form the current implementation contract.

Before implementing a slice, resolve only the questions that actually gate that slice. Do not block safe current work on later-phase choices.
