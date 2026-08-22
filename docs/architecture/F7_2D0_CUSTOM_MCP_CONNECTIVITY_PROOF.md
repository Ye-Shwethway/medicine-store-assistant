# F7.2D0 — Custom MCP Read-Only Connectivity Proof

Status: **FIRST IMPLEMENTATION STEP OF F7.2D**

## Goal

Prove as early as possible that ChatGPT Developer Mode can securely connect to a custom remote Medicine Store Assistant MCP service hosted on the VPS and receive real, authorized MSA backend data.

This is a connectivity/authority proof. It is not direct database access, not an AI write slice, and not a provider/model integration slice.

## Why MCP comes first

The project wants ChatGPT/IANEO-style access to MSA with as much typed-tool freedom and reuse as practical. A working custom MCP connection may remove the need for a separate Custom GPT Action path for the main ChatGPT workflow.

If the real ChatGPT Developer Mode connection cannot authenticate to or invoke the deployed MSA MCP service because of current product, protocol, network, or authentication constraints, that limitation should be discovered before significant Agent Management/provider work assumes the MCP path works.

## Architecture

`ChatGPT Developer Mode -> HTTPS remote MCP -> MSA MCP adapter -> scoped external-client identity -> capability check -> existing deterministic read service -> response`

The MCP service may read from the current PostgreSQL-backed test/shadow services only through bounded application contracts. It must not become an unrestricted DB gateway.

## Hosting direction

MSA must host its own remote MCP server/service on the existing VPS because there is no provider-hosted MSA MCP endpoint to reuse.

Preferred deployment shape:

- a small separate `msa-mcp` service/container;
- public TLS endpoint through the existing MSA domain/reverse-proxy stack;
- either a dedicated subdomain or stable path chosen during implementation;
- protocol adapter isolated from core inventory business logic;
- reuse existing typed/read service functions or API contracts rather than duplicating inventory logic.

The exact framework/library and endpoint path must be selected against the current MCP specification and current ChatGPT Developer Mode requirements at implementation time.

## Initial MCP tools

Start with the smallest useful read-only tool set.

### `msa_whoami`

Returns:

- external MCP client identifier/name;
- client state;
- runtime type `EXTERNAL_MCP_CLIENT`;
- granted capability names;
- no credential/token material.

### `get_system_status`

Returns bounded application status such as:

- service/environment;
- `database_canonical`;
- `migration_baseline_accepted`;
- current read-only/test boundary metadata.

### `get_inventory_summary`

Returns the existing bounded current test/shadow inventory summary and explicitly preserves:

- F6B test-only state;
- `database_canonical=false`;
- `migration_baseline_accepted=false`.

### Later optional bounded reads

Only after the basic proof passes:

- `search_inventory` with bounded query/limit;
- `get_inventory_item` by stable typed identifier;
- selected catalogue/shadow diagnostics already authorized for read access.

Do not begin with a large tool catalog.

## Explicitly forbidden MCP tools

The first proof must not expose:

- raw SQL;
- arbitrary query/table/column selection;
- database credentials;
- Google Sheet credentials;
- VPS shell/SSH commands;
- arbitrary file-system access;
- provider API keys;
- User Management mutation;
- Agent Management mutation;
- stock/price/lot/transfer mutation;
- generic arbitrary HTTP proxying.

## External client identity

Register one named MCP external client with at least:

- stable client identifier;
- runtime type `EXTERNAL_MCP_CLIENT`;
- `ACTIVE` / `REVOKED` state;
- credential digest/verifier or secret reference;
- explicit read capability allowlist;
- created/revoked timestamps and provenance.

This proof may use the minimum schema needed before the full F7.2D Agent Management UI exists, but it must be compatible with the later canonical external-client/agent policy model rather than creating a disposable security bypass.

## Authentication

At implementation time, re-check current OpenAI/ChatGPT Developer Mode and MCP authentication requirements first.

Preferred first proof, where supported:

- one high-entropy, scoped, revocable service credential;
- plaintext shown/provisioned only at issuance;
- server stores only digest/verifier or secret reference;
- missing/invalid credential denied;
- valid credential with missing capability denied;
- revocation immediately blocks subsequent calls.

If the current ChatGPT MCP connection flow requires another supported authentication mechanism, use the minimum secure supported method and document the deviation. Do not open unauthenticated inventory access merely to make MCP connect.

## Capability policy

The MCP transport itself grants no authority.

For the first proof:

`effective_authority = registered_client_scope ∩ granted_tool_capability ∩ operation_policy`

The first client should receive only narrowly named read capabilities needed for the proof.

Future human-delegated or AI-agent execution will reuse the broader F7.2D authority engine; MCP does not create a second permission system.

## Transport and protocol requirements

Implementation must use the current remote MCP transport expected by ChatGPT Developer Mode at that time.

Requirements:

- HTTPS/TLS public endpoint;
- stable MCP endpoint URL;
- protocol-compliant initialization/tool discovery/invocation;
- bounded request/response sizes;
- sensible timeouts;
- no secret logging;
- clear 401/403-equivalent authorization failure behavior where applicable;
- health/diagnostic visibility separate from MCP tool data.

Do not assume an older SSE-only or newer transport shape without re-checking the current MCP/OpenAI documentation immediately before coding.

## Acceptance test

F7.2D0 passes only when all of the following are proven end-to-end:

1. The remote MSA MCP service is deployed on the VPS and reachable through public HTTPS.
2. One scoped external MCP client/credential exists without exposing plaintext secrets in Git/logs/docs.
3. Local/server-level MCP initialization and tool listing work.
4. ChatGPT Developer Mode accepts/connects to the custom MCP endpoint.
5. ChatGPT can invoke `msa_whoami` and receives the registered MSA external-client identity.
6. ChatGPT can invoke `get_system_status` or equivalent bounded status read.
7. ChatGPT can invoke `get_inventory_summary` and receives current real MSA backend data.
8. Relevant responses preserve `database_canonical=false`, `migration_baseline_accepted=false`, and F6B test-only status.
9. A deliberately ungranted tool/capability is denied.
10. Revoking the MCP client/credential causes a later ChatGPT call to fail.
11. Reissuing/reactivating only the intended scoped credential restores only intended read access.
12. No inventory mutation, workbook import, canonical DB promotion, provider/model call, or Custom GPT Action is required for the proof.

## Success decision

If the MCP proof passes and ChatGPT can reliably use the typed MSA tools with the needed flexibility, **MCP becomes the primary ChatGPT access path**.

The separate Custom GPT Action path becomes optional and should be implemented only if there is a concrete need such as a standalone packaged Custom GPT, Action-specific distribution, or a capability that MCP does not satisfy.

## Failure decision

If ChatGPT cannot connect or invoke tools because of current Developer Mode/MCP restrictions:

- capture the exact failing stage and error;
- determine whether the blocker is server protocol, TLS/network, authentication, account/workspace policy, or ChatGPT product support;
- fix only legitimate implementation defects;
- do not weaken authentication or expose raw DB access;
- if the platform restriction is real, record MCP as unproven/blocked and evaluate the existing Custom GPT Action proof as the next external path.

## Non-scope

- provider API keys/model calls;
- Provider Registry UI;
- internal AI Chat;
- production inventory writes;
- AI writes;
- store transfers;
- Smart Calculator deductions;
- Telegram/Flutter integration;
- full F7.3 operational Audit;
- Sheet mirror conversion;
- PostgreSQL canonical promotion.

## Next after success

Proceed to the F7.2D AI-agent/external-client principal control-plane foundation and Provider Registry/model catalog. Defer the Custom GPT Action proof unless a concrete need remains.
