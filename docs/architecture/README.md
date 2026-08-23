# Medicine Store Assistant — Architecture Index

Status: **F7.2A/B/C, F7.2D0 custom MCP connectivity, and F7.2D2 named Agent Management/multi-agent sessions are verified; F7.2D3 Provider Registry + model catalog is next; PostgreSQL remains non-canonical**

This directory defines the canonical architecture for Medicine Store Assistant beyond the current spreadsheet-operating skill.

The Git-backed `$msa` skill remains canonical at:

`skills/medicine-store-assistant/`

## Core decision

MSA evolves toward a ledger-backed multi-client inventory system in which:

- PostgreSQL is planned future canonical operational storage but is **not canonical yet**;
- Google Sheets remains operationally authoritative until explicit promotion;
- Web, custom MCP, Telegram, Flutter, optional Custom GPT Actions, internal AI and other clients use typed application contracts rather than direct DB writes;
- human identities, AI agents, external clients, provider connections, and model resources are separate concepts;
- deterministic backend code owns authorization/delegation, validation, idempotency, transactions, and read-back verification;
- AI interprets/reconciles/proposes and may later execute only Owner-authorized typed capabilities;
- actor-aware Audit records who/what acted, under whose authority, through which client/location, and with what outcome.

## Verified MCP-first external access

F7.2D0 is verified complete.

Live path:

`ChatGPT Developer Mode -> OAuth/PKCE -> custom MSA MCP -> typed MSA backend -> deterministic read services`

Verified runtime anchor:

- source SHA `611918572717058882849ede7a4cc2a39dd2e3ac`;
- deploy run `32618376291`;
- Alembic `0010_mcp_oauth`;
- public authorization-server and protected-resource metadata pass;
- ChatGPT Developer Mode OAuth connection succeeds;
- fresh ChatGPT chat can execute authorized MSA identity/system reads;
- scopes `mcp:connect`, `mcp:read`, `offline_access`;
- propose/write/control disabled;
- anonymous `/mcp` returns 401.

The MCP server remains **full-schema/policy-gated**. Discoverability is not authorization. Future capabilities are enabled through backend policy/project gates without rebuilding the connector.

Explicitly forbidden generic access remains:

- arbitrary SQL/table editing;
- DB credentials;
- VPS shell/filesystem;
- plaintext secrets;
- Google Sheet credentials;
- generic unrestricted HTTP proxying.

Custom GPT Actions are optional/fallback only because custom MCP already proves ChatGPT access.

## F7.2D2 — verified Agent Management foundation

F7.2D2 is now verified complete.

Runtime anchor:

- PR #58;
- merge SHA `3b385a37b95c1ff79f76883381d8268fa6c49db2`;
- deploy run `32620386876` / job `97147568336`;
- Alembic `0010_mcp_oauth -> 0011_ai_agents`;
- issue #26 `status=success`.

Verified model:

- durable named `AI_AGENT` principal with immutable `agent_id`;
- editable `display_name`;
- case-insensitive unique `call_name` for human-friendly addressing/selection;
- server-generated self-identity context from canonical name + stable ID;
- `ACTIVE` / `DISABLED` / `REVOKED` lifecycle;
- capability/location/authority/execution/confirmation metadata;
- Owner-only management and non-Owner 403;
- persistent multi-agent sessions;
- modes `GROUP`, `COMPARE`, `REVIEW`, `DEBATE`;
- ordered participants + optional role labels;
- provider/model inference disabled;
- production system write gate closed.

Canonical detailed design:

`F7_2D2_AGENT_MANAGEMENT_AND_MULTI_AGENT_SESSIONS.md`

Canonical verified checkpoint:

`../checkpoints/F7_2D2_AGENT_MANAGEMENT_2026-08-23.md`

## Agent/provider/model/client separation

Canonical distinction:

- **Human user** — canonical person/account and human role.
- **AI agent** — named identity + capability/location/execution policy.
- **External client** — transport/runtime such as custom MCP connection.
- **Provider connection** — outbound model API configuration + secret reference.
- **Model** — provider-local model resource/capability metadata.
- **Assignment** — which provider/model an internal agent currently uses.
- **Multi-agent session** — reusable topology of selected named agents.

Changing provider/model never changes agent identity or authority.

## F7.2D3 — next architecture slice

Provider Registry is Owner-only and remains separate from MCP/Agent Management.

Built-in presets:

- OpenAI
- Google Gemini
- OpenRouter
- NanoGPT

Generic adapter:

- `OPENAI_COMPATIBLE`

Canonical Owner workflow:

`Add provider -> provision credential -> Test connection -> Fetch models -> inspect capabilities -> Save/enable`

Provider credentials remain write-only protected runtime secrets/secret references. Model lists are fetched dynamically; unknown capability metadata remains unknown rather than guessed. Custom provider URLs require production SSRF protections.

## Immediate F7.2D order

1. **F7.2D0 — custom MCP full-schema/OAuth connectivity — VERIFIED COMPLETE**
2. **F7.2D2 — named Agent Management + multi-agent sessions — VERIFIED COMPLETE**
3. **F7.2D3 — Provider Registry + model catalog — NEXT**
4. **F7.2D4 — internal model assignment/fallbacks + runtime identity injection**
5. optional **F7.2D1 — Custom GPT Action proof** only for a concrete standalone-GPT need
6. **F7.3 — actor-aware operational Audit**

No production inventory write becomes authorized merely because capability metadata or write-capable MCP tools exist.

## Web design/implementation rule

Default Web workflow:

`UI/UX Pro Max -> repo design system -> authenticated API contract -> direct implementation -> responsive/accessibility/runtime verification`

Figma is optional and used only when explicitly requested by the Owner or genuinely required by a specific task.

Canonical UI sources:

- `../design/UI_UX_PRO_MAX_INTEGRATION.md`
- `../../design-system/medicine-store-assistant/MASTER.md`
- `../../design-system/medicine-store-assistant/pages/dashboard.md`

## Documents

1. [CANONICAL_INVENTORY_ARCHITECTURE.md](CANONICAL_INVENTORY_ARCHITECTURE.md) — system boundaries and SOT model.
2. [INVENTORY_DATA_MODEL.md](INVENTORY_DATA_MODEL.md) — products/lots/transactions/identity/lifecycle.
3. [MONTHLY_LIFECYCLE.md](MONTHLY_LIFECYCLE.md) — monthly lifecycle and Excel compatibility.
4. [CMS_CATALOGUE_VERSIONING.md](CMS_CATALOGUE_VERSIONING.md) — catalogue history/mapping.
5. [INVENTORY_INTEGRITY_AND_AUDIT.md](INVENTORY_INTEGRITY_AND_AUDIT.md) — integrity/idempotency/reconciliation.
6. [SHEET_MIRROR_AND_COMPATIBILITY.md](SHEET_MIRROR_AND_COMPATIBILITY.md) — Sheet mirror direction.
7. [API_AND_CLIENT_ARCHITECTURE.md](API_AND_CLIENT_ARCHITECTURE.md) — API/client boundaries.
8. [USER_ACCESS_AND_AUTHORIZATION.md](USER_ACCESS_AND_AUTHORIZATION.md) — identity/access foundation.
9. [MIGRATION_AND_SHADOW_VALIDATION.md](MIGRATION_AND_SHADOW_VALIDATION.md) — migration/promotion safety.
10. [DECISIONS_AND_OPEN_QUESTIONS.md](DECISIONS_AND_OPEN_QUESTIONS.md) — locked/open decisions.
11. [F7_WEB_DASHBOARD.md](F7_WEB_DASHBOARD.md) — Dashboard v2.4 foundation.
12. `../design/F7_2_AUTH_RBAC_DESIGN.md` — human identity/RBAC.
13. `../design/F7_2C_CREDENTIAL_LIFECYCLE_DESIGN.md` — credential/recovery lifecycle.
14. [F7_2D_AI_AGENT_MANAGEMENT.md](F7_2D_AI_AGENT_MANAGEMENT.md) — agent/provider/MCP delegated-authority architecture.
15. [F7_2D0_MCP_FULL_CAPABILITY_SCHEMA.md](F7_2D0_MCP_FULL_CAPABILITY_SCHEMA.md) — MCP tool/policy schema.
16. [F7_2D0_CUSTOM_MCP_CONNECTIVITY_PROOF.md](F7_2D0_CUSTOM_MCP_CONNECTIVITY_PROOF.md) — MCP proof contract.
17. [F7_2D2_AGENT_MANAGEMENT_AND_MULTI_AGENT_SESSIONS.md](F7_2D2_AGENT_MANAGEMENT_AND_MULTI_AGENT_SESSIONS.md) — named identity/session contract.
18. [F7_2D1_CUSTOM_GPT_ACTION_PROOF.md](F7_2D1_CUSTOM_GPT_ACTION_PROOF.md) — optional secondary Action path.
19. [F7_3_ACTOR_AUDIT_AND_OPERATION_LEDGER.md](F7_3_ACTOR_AUDIT_AND_OPERATION_LEDGER.md) — operation provenance/audit.
20. [F7_4_F7_8_STORE_AND_INTELLIGENCE_ARCHITECTURE.md](F7_4_F7_8_STORE_AND_INTELLIGENCE_ARCHITECTURE.md) — locations/settings/calculator/analysis/AI/alerts.

Relevant checkpoints:

- `../checkpoints/F7_2D_MCP_FIRST_DECISION_2026-08-23.md`
- `../checkpoints/F7_2D_MCP_FULL_CAPABILITY_DECISION_2026-08-23.md`
- `../checkpoints/F7_2D0_MCP_CONNECTIVITY_VERIFIED_2026-08-23.md`
- `../checkpoints/F7_2D2_AGENT_MANAGEMENT_2026-08-23.md`

## Design rule

Do not implement from one document in isolation. `AGENTS.md`, `NEW_CHAT_BOOTSTRAP.md`, `ROADMAP.md`, `IMPLEMENTATION_PLAN.md`, active architecture/design docs, and current repository/runtime evidence together form the implementation contract.
