# Medicine Store Assistant — Architecture Index

Status: **F7.2A canonical human identity/sessions, F7.2B User Management, and F7.2C Credential Lifecycle verified; F7.2D AI Agent Management next with MCP-first connectivity proof; PostgreSQL remains non-canonical**

This directory defines the future canonical architecture for Medicine Store Assistant beyond the current spreadsheet-operating skill.

The existing Git-backed skill remains canonical at:

`skills/medicine-store-assistant/`

The architecture here must preserve the useful skill workflow while moving authority into durable typed backend contracts.

## Core decision

MSA evolves toward a ledger-backed multi-client inventory system in which:

- PostgreSQL on the VPS is the planned future canonical operational datastore, but is **not canonical yet**;
- the Inventory API/typed backend services are the only normal mutation boundary once DB writes are authorized;
- Google Sheets remains operationally authoritative until explicit promotion, then becomes a human-facing mirror/reconciliation surface for the promoted scope;
- Excel remains a compatible export/archive/report surface;
- Web, custom MCP clients, Telegram, Flutter, optional Custom GPT Actions, internal AI, and other clients use typed application contracts rather than direct DB writes;
- canonical human identities and separately managed AI/service/external-client principals provide durable actor attribution;
- AI interprets evidence, reconciles candidates, prepares proposals, and may later execute only Owner-authorized typed capabilities;
- deterministic backend code owns arithmetic, constraints, authorization/delegation, idempotency, transactions, derived state, and read-back verification;
- actor-aware Audit records who/what acted, under whose authority, through which client/location, and with what outcome;
- the current Google-Sheets-first workflow remains authoritative until migration/shadow-validation explicitly promotes the database.

## Current F7 architecture

F7.2A is deployed and runtime-verified. Human accounts use the existing F2 canonical `users` / `roles` / `user_roles` foundation with stable UUID `user_id`, username + password, `PENDING` / `ACTIVE` / `DISABLED` state, durable DB-bound revocable sessions, backend role helpers, explicit authenticated 403 behavior, and disabled-user enforcement.

F7.2B is deployed and runtime-verified. It adds pending-only access requests, Owner-only human User Management, approval/rejection and `ADMIN` / `STAFF` / `READ_ONLY` assignment, non-Owner role changes with session revocation, disable/reactivate/session revoke, OWNER ordinary-flow escalation protection, account-security events, reusable notification events, and a signed-in drawer/sidebar profile card with circular avatar area, deterministic initials fallback, canonical username, and role. User Management remains separate from operational Audit.

F7.2C is deployed and runtime-verified. Username is a mutable sign-in/display credential while stable `user_id`, role, and state remain authoritative. Active users can change username/password from Account after current-password re-authentication. Password change includes explicit confirmation and revokes prior sessions. Recovery email is product-native: users can verify/change a recovery address through Account, Forgot password accepts either username or verified recovery email, and automated reset links are sent through the verified Resend domain `msamail.drthorne.uk`. Owner-assisted reset issuance remains a fallback. Request Access collects a recovery email and can verify it while the account remains `PENDING`; email verification never grants a role or protected access. The final verified production source SHA is `371936e0c7088c76f692292d31318cfd972a1a46`.

F7.2D is now locked to an **MCP-first external connectivity strategy**. ChatGPT Developer Mode will first be tested against a custom remote MSA MCP service hosted on the VPS. MCP is an external runtime/access path, not a provider. If MCP proves sufficient, Custom GPT Actions may remain optional. Provider Registry still supports built-in OpenAI/Gemini/OpenRouter/NanoGPT adapters plus generic OpenAI-compatible custom providers, but provider/model work follows the MCP connectivity proof rather than preceding it.

Current direction continues with:

- F7.2D0 custom MCP read-only connectivity proof first;
- F7.2D Owner-only AI Agent/external-client control plane after MCP proof;
- Provider Registry/model catalog and internal model assignment after the principal/control-plane foundation;
- optional Custom GPT Action proof only if MCP is insufficient or a standalone GPT is specifically needed;
- F7.3 actor-aware operational Audit after F7.2D;
- exactly one Main Store plus Owner-created Sub Stores later in F7.4;
- Owner-only global Settings in its later authorized slice;
- Owner-configurable reorder basis (`MAIN_STORE_ONLY` initially, later optional `TOTAL_ACTIVE_STOCK`);
- human User Management separate from Owner-only AI Agent Management;
- AI agents may be granted Main Store and/or Sub Store capabilities; they are not inherently Sub-Store-only;
- shared AI Chat may be enabled for Staff/Admin users, but effective authority remains the intersection of human authority, agent capability, location scope, and operation policy;
- Smart Calculator is DB-backed and calculation-only first;
- Smart Analysis is deterministic first, AI-assisted second;
- Alerts/Notifications reuse backend events across clients.

Verified F7.2A anchor: PR #36, merge `c3aa75d65e0bc6d1836227fe8450b0b3de5b2651`, deploy run `32586385336`.

Verified F7.2B anchor: PR #38, merge `e4671c75ab2ece2a6f5065a78779413ef3e9f38b`, deploy run `32588170791`, job `97067607202`.

Verified F7.2C base anchor: PR #40, merge `a910658efc3cbc214b30a1f5ed946fdd34ffe4a2`, deploy run `32589571152`, job `97071112514`. Final recovery/account refinements are recorded in `../design/F7_2C_CREDENTIAL_LIFECYCLE_DESIGN.md`; the final runtime source SHA `371936e0c7088c76f692292d31318cfd972a1a46` deployed successfully through issue #26. The final state includes verified recovery email, Resend delivery, username-or-email reset, password confirmation, pending-access email verification, and the same read-only/non-canonical boundaries.

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
12. `../design/F7_2_AUTH_RBAC_DESIGN.md` — canonical human identity/RBAC design and verified account lifecycle.
13. `../design/F7_2C_CREDENTIAL_LIFECYCLE_DESIGN.md` — verified username/password/recovery-email lifecycle, Resend delivery, automated reset, and access-request email verification.
14. [F7_2D_AI_AGENT_MANAGEMENT.md](F7_2D_AI_AGENT_MANAGEMENT.md) — Owner-only AI/service/external-client principal management, MCP access, Provider Registry, capabilities, delegation, and model assignment.
15. [F7_2D0_CUSTOM_MCP_CONNECTIVITY_PROOF.md](F7_2D0_CUSTOM_MCP_CONNECTIVITY_PROOF.md) — first F7.2D implementation proof: remote MCP on the VPS, ChatGPT Developer Mode connection, typed read tools, capability denial, and revocation.
16. [F7_2D1_CUSTOM_GPT_ACTION_PROOF.md](F7_2D1_CUSTOM_GPT_ACTION_PROOF.md) — optional secondary Custom GPT Action proof if MCP is insufficient or a standalone GPT is later required.
17. [F7_3_ACTOR_AUDIT_AND_OPERATION_LEDGER.md](F7_3_ACTOR_AUDIT_AND_OPERATION_LEDGER.md) — human/AI/system/integration provenance and operation ledger.
18. [F7_4_F7_8_STORE_AND_INTELLIGENCE_ARCHITECTURE.md](F7_4_F7_8_STORE_AND_INTELLIGENCE_ARCHITECTURE.md) — Main/Sub locations, Settings/preferences, Smart Calculator, Smart Analysis, AI Chat, Alerts.

Relevant checkpoint: `../checkpoints/F7_2D_MCP_FIRST_DECISION_2026-08-23.md`.

`F7_4_F7_6_INTELLIGENCE_ARCHITECTURE.md` is superseded and retained only as a historical pointer.

## Repository boundary

```text
medicine-store-assistant/
├── skills/medicine-store-assistant/   # published Git-backed skill; preserve
├── docs/architecture/                 # canonical system design
├── backend/                           # deterministic API + DB + dashboard runtime
├── integrations/                      # MCP/GPT/Sheets/Telegram/Flutter adapters
├── deploy/                            # VPS deployment assets
├── AGENTS.md
├── NEW_CHAT_BOOTSTRAP.md
├── NORMAL_CHAT_BOOTSTRAP.md
└── ROADMAP.md
```

## Design rule

Do not implement from one document in isolation. `AGENTS.md`, `NEW_CHAT_BOOTSTRAP.md`, `ROADMAP.md`, `IMPLEMENTATION_PLAN.md`, the active F7 architecture/design docs, and current repository/runtime evidence form the current implementation contract.

Before implementing a slice, resolve only the questions that actually gate that slice. Do not block safe current work on later-phase choices.
