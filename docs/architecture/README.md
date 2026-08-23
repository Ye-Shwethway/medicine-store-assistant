# Medicine Store Assistant — Architecture Index

Status: **F7.2A canonical human identity/sessions, F7.2B User Management, F7.2C Credential Lifecycle, and F7.2D0 custom MCP connectivity are verified; F7.2D2 AI Agent/external-client principal control plane is next; PostgreSQL remains non-canonical**

This directory defines the future canonical architecture for Medicine Store Assistant beyond the current spreadsheet-operating skill.

The existing Git-backed skill remains canonical at:

`skills/medicine-store-assistant/`

## Core decision

MSA evolves toward a ledger-backed multi-client inventory system in which:

- PostgreSQL is planned future canonical operational storage but is **not canonical yet**;
- Google Sheets remains operationally authoritative until explicit promotion;
- Web, custom MCP, Telegram, Flutter, optional Custom GPT Actions, internal AI and other clients use typed application contracts rather than direct DB writes;
- human identities and AI/service/external-client principals are separate;
- deterministic backend code owns authorization/delegation, validation, idempotency, transactions and read-back verification;
- AI interprets/reconciles/proposes and may later execute only Owner-authorized typed capabilities;
- actor-aware Audit records who/what acted, under whose authority, through which client/location and with what outcome.

## Current F7 architecture

F7.2A/B/C are deployed and runtime-verified. F7.2C includes self-service username/password/recovery-email maintenance, password confirmation, verified-email recovery, automated Resend delivery, username-or-email Forgot password, Owner-assisted fallback reset and pending-access email verification. PostgreSQL remains non-canonical and inventory remains read-only.

F7.2D uses an **MCP-first external-access strategy**. F7.2D0 is now verified complete for the external ChatGPT read-access proof.

The live path is:

`ChatGPT Developer Mode -> OAuth -> custom MSA MCP -> typed MSA backend -> deterministic read services`

Verified F7.2D0 runtime:

- production source SHA `611918572717058882849ede7a4cc2a39dd2e3ac`;
- deploy run `32618376291` / issue #26 `status=success`;
- Alembic `0010_mcp_oauth` deployed;
- public OAuth authorization-server metadata verified;
- public MCP protected-resource metadata verified;
- OAuth authorization-code + PKCE S256, dynamic client registration, rotating refresh tokens and `offline_access` deployed;
- anonymous `/mcp` access returns 401;
- ChatGPT Developer Mode successfully connected using OAuth;
- a fresh ChatGPT chat successfully executed the MSA identity/system-status read through the custom MCP path;
- current connected scope is `mcp:connect`, `mcp:read`, `offline_access`;
- proposal/write/control capabilities remain disabled;
- `database_canonical=false`, `migration_baseline_accepted=false`, F6B test-only status and production inventory-write denial remain preserved.

The MCP direction remains **full-capability schema first** rather than read-only-server-first:

- the durable server/tool catalog is designed once for read, proposal, future typed write, User Management, Agent Management, Provider Registry, Audit and typed Settings capabilities;
- the initial external MCP principal receives only currently authorized read grants;
- discoverable tools do not imply execution permission;
- future capabilities are enabled through backend policy and project-slice gates rather than reconnecting/rebuilding the MCP app;
- raw SQL, arbitrary table/column mutation, SSH, filesystem, plaintext secrets and generic HTTP proxying remain forbidden.

Current researched MCP/OpenAI direction as of 2026-08-23 includes stateless MCP core, remote HTTPS/Streamable-HTTP-compatible deployment, JSON Schema 2020-12 tool definitions, tool annotations and standards-based authorization/protected-resource discovery where OAuth is used. ChatGPT write/modify availability may still depend on plan/workspace/product rollout; client limitations do not change the server architecture.

Provider Registry remains separate from MCP. Built-in provider presets are OpenAI, Google Gemini, OpenRouter and NanoGPT, plus generic `OPENAI_COMPATIBLE` custom providers. Provider/model work follows the agent/external-client principal control plane.

The optional Custom GPT Action path is no longer required to prove ChatGPT access. It remains a secondary/fallback integration only if a standalone Custom GPT surface is later useful.

## Immediate F7.2D order

1. **F7.2D0 — full-capability MCP transport/schema + initial read-grant connectivity proof — VERIFIED COMPLETE**.
2. **F7.2D2 — AI agent/external-client principal control plane — NEXT**.
3. F7.2D3 — Provider Registry + model catalog.
4. F7.2D4 — internal model assignment/fallbacks.
5. Optional F7.2D1 — Custom GPT Action proof only if MCP is insufficient or a standalone GPT is needed.
6. F7.3 — actor-aware operational Audit.

No production inventory write becomes authorized merely because write-capable MCP tools exist in the schema.

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
11. [F7_WEB_DASHBOARD.md](F7_WEB_DASHBOARD.md) — locked Dashboard v2.4 foundation.
12. `../design/F7_2_AUTH_RBAC_DESIGN.md` — human identity/RBAC design.
13. `../design/F7_2C_CREDENTIAL_LIFECYCLE_DESIGN.md` — verified credential/recovery lifecycle.
14. [F7_2D_AI_AGENT_MANAGEMENT.md](F7_2D_AI_AGENT_MANAGEMENT.md) — AI/service/external-client principals, MCP access, Provider Registry and delegated authority.
15. [F7_2D0_MCP_FULL_CAPABILITY_SCHEMA.md](F7_2D0_MCP_FULL_CAPABILITY_SCHEMA.md) — durable full MCP tool namespaces, auth, policy gates, tool annotations, write contract and activation model.
16. [F7_2D0_CUSTOM_MCP_CONNECTIVITY_PROOF.md](F7_2D0_CUSTOM_MCP_CONNECTIVITY_PROOF.md) — first implementation proof using the full schema but only current read grants.
17. [F7_2D1_CUSTOM_GPT_ACTION_PROOF.md](F7_2D1_CUSTOM_GPT_ACTION_PROOF.md) — optional secondary Action path.
18. [F7_3_ACTOR_AUDIT_AND_OPERATION_LEDGER.md](F7_3_ACTOR_AUDIT_AND_OPERATION_LEDGER.md) — operation provenance/audit.
19. [F7_4_F7_8_STORE_AND_INTELLIGENCE_ARCHITECTURE.md](F7_4_F7_8_STORE_AND_INTELLIGENCE_ARCHITECTURE.md) — locations/settings/calculator/analysis/AI/alerts.

Relevant checkpoints:

- `../checkpoints/F7_2D_MCP_FIRST_DECISION_2026-08-23.md`
- `../checkpoints/F7_2D_MCP_FULL_CAPABILITY_DECISION_2026-08-23.md`
- `../checkpoints/F7_2D0_MCP_CONNECTIVITY_VERIFIED_2026-08-23.md`

## Repository boundary

```text
medicine-store-assistant/
├── skills/medicine-store-assistant/
├── docs/architecture/
├── backend/
├── integrations/
├── deploy/
├── AGENTS.md
├── NEW_CHAT_BOOTSTRAP.md
├── NORMAL_CHAT_BOOTSTRAP.md
└── ROADMAP.md
```

## Design rule

Do not implement from one document in isolation. `AGENTS.md`, `NEW_CHAT_BOOTSTRAP.md`, `ROADMAP.md`, `IMPLEMENTATION_PLAN.md`, the active F7 architecture/design docs and current repository/runtime evidence together form the implementation contract.
