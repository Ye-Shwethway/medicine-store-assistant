# F7.2D MCP-First Architecture Decision — 2026-08-23

Status: **APPROVED — docs-first decision before implementation**

## Decision

The first implementation proof inside F7.2D is now the custom remote MCP path, not Custom GPT Actions.

Implementation order begins with:

1. `F7.2D0` — custom MCP read-only connectivity proof;
2. AI-agent/external-client principal and control-plane foundation;
3. Provider Registry/model catalog;
4. internal model assignment;
5. optional Custom GPT Action proof only if MCP is insufficient or a standalone Custom GPT is specifically needed.

## Reason

The Owner already uses custom MCP-style access for other infrastructure and wants to determine as early as possible whether ChatGPT Developer Mode can directly use typed Medicine Store Assistant tools hosted on the VPS.

If the custom MCP path works reliably, it may provide enough flexibility that a separate Custom GPT Action integration is unnecessary for the primary ChatGPT workflow.

## Locked architecture

- MSA hosts its own remote MCP adapter/service on the VPS.
- MCP is an external access/runtime path, not a model provider.
- Custom GPT is also an external client/runtime path, not a provider.
- Built-in model providers remain OpenAI, Gemini, OpenRouter, and NanoGPT.
- Additional model providers may be configured through the generic `OPENAI_COMPATIBLE` provider format.
- MCP and Action clients use typed capabilities and never receive raw PostgreSQL credentials or arbitrary SQL access.
- Provider/model selection never increases agent/client authority.
- Google Sheets remains operationally authoritative; PostgreSQL remains non-canonical.
- F6B remains test-only.
- No production inventory writes or AI writes are authorized by this decision.

## First proof target

ChatGPT Developer Mode must be able to connect to the deployed MSA remote MCP endpoint and invoke at minimum:

- `msa_whoami`;
- `get_system_status`;
- `get_inventory_summary`.

The proof must also demonstrate capability denial and credential/client revocation.

## Failure boundary

If MCP fails because of a real ChatGPT/Developer Mode/MCP product restriction, record the exact blocker and evaluate the existing Custom GPT Action proof next. Do not weaken MSA authentication, expose raw DB access, or bypass typed capability checks.

## Canonical docs

- `docs/architecture/F7_2D_AI_AGENT_MANAGEMENT.md`
- `docs/architecture/F7_2D0_CUSTOM_MCP_CONNECTIVITY_PROOF.md`
- `docs/architecture/F7_2D1_CUSTOM_GPT_ACTION_PROOF.md`

## Next implementation action

Do not begin Provider Registry or full Agent Management UI first. Build and deploy the smallest read-only remote MCP proof, then connect it from ChatGPT Developer Mode and test from an actual chat session.
