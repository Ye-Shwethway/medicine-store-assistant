# F7.2D0 — Custom MCP Full-Capability Connectivity Proof

Status: **FIRST IMPLEMENTATION STEP OF F7.2D**

Canonical companion: `F7_2D0_MCP_FULL_CAPABILITY_SCHEMA.md`

## Goal

Prove as early as possible that ChatGPT Developer Mode can securely connect to a custom remote Medicine Store Assistant MCP service hosted on the VPS, discover the durable full tool catalog, and execute only the operations currently granted by backend policy.

This is no longer a read-only server design. The **server/schema is full-capability from the start** so the connector does not need to be rebuilt later merely to add write/admin tool classes. The first runtime grant remains read-only because current production inventory writes are not authorized.

Canonical rule:

`full MCP schema + narrow current authority`

## Why MCP comes first

The project wants ChatGPT/IANEO-style access to MSA with typed-tool freedom and reuse. A working custom MCP path may remove the need for a separate Custom GPT Action path for the main ChatGPT workflow.

Because custom MCP configuration can be relatively expensive to repeat, the first durable setup should already expose the stable long-term tool namespaces for read, propose, write, control-plane, provider, audit and settings operations. Future activation should occur through MSA policy rather than connector reconstruction.

If the real ChatGPT Developer Mode connection cannot authenticate to or invoke the deployed MSA MCP service because of current product, protocol, network, authentication or plan/workspace constraints, discover that limitation before building the rest of F7.2D around an unproven assumption.

## Architecture

`ChatGPT Developer Mode`
`  -> HTTPS remote MCP`
`msa-mcp adapter`
`  -> authenticated external-client/agent context`
`  -> capability + location + operation-policy + write/canonicality gates`
`  -> typed deterministic MSA services`
`  -> current backend/data boundary`

The MCP adapter is not a raw database gateway and does not duplicate inventory business logic.

## Hosting direction

MSA hosts its own remote MCP service on the existing VPS.

Preferred shape:

- separate small `msa-mcp` service/container;
- stable public HTTPS endpoint through existing reverse-proxy/TLS infrastructure;
- dedicated subdomain or stable path chosen during implementation;
- protocol logic isolated from core inventory business logic;
- typed backend service reuse;
- no direct public PostgreSQL exposure.

Use the then-current stable MCP specification and a maintained Tier-1 SDK where practical. As of the 2026-08-23 research checkpoint, the current MCP direction includes a stateless core, remote HTTPS/Streamable-HTTP-compatible deployment, JSON Schema 2020-12 tool schemas, structured outputs and tool annotations.

## Full catalog, narrow initial grant

The server should publish the durable tool catalog defined in `F7_2D0_MCP_FULL_CAPABILITY_SCHEMA.md` where practical.

The initial ChatGPT/MCP principal is granted only the minimum current read capabilities needed for proof, for example:

- `msa_identity_whoami`
- `msa_system_status`
- `msa_system_capabilities`
- `msa_inventory_read_summary`
- bounded inventory search/item reads if useful

The catalog may also contain policy-disabled future tools such as inventory writes, transfers, User Management, Agent Management, Provider Registry and Settings.

A visible tool is not an authorized tool. A discoverable write operation must fail deterministically while its capability/system gate is disabled.

## Tool annotations

Use current MCP annotations accurately where supported:

- read-only tools: `readOnlyHint=true`;
- additive/non-destructive mutations: `destructiveHint=false`;
- destructive/high-impact mutations: `destructiveHint=true`;
- `idempotentHint=true` only when repeat execution is actually idempotent;
- closed MSA-internal operations normally use `openWorldHint=false`.

These are hints for clients. MSA backend authorization remains authoritative.

## Authentication

Re-check current ChatGPT Developer Mode/MCP authentication requirements immediately before implementation.

The long-term server should be OAuth-capable where the ChatGPT connection path uses MCP-standard authorization, including protected-resource discovery, token audience/resource binding, scope validation and durable authorization behavior.

For development/bootstrap or a supported direct bearer flow, MSA may use a high-entropy revocable scoped service credential.

In all cases:

- plaintext secrets are never stored in Git/docs/logs;
- server stores safe verifier/digest/secret references only;
- invalid/missing credentials are denied;
- revoked clients are denied immediately;
- valid authentication without a required capability is denied;
- no unauthenticated inventory access is opened to make the connector work.

## Policy model

The MCP transport grants no authority.

For a non-human external MCP call:

`effective_authority = registered_client_scope ∩ agent_capability_scope ∩ location_scope ∩ operation_policy ∩ system_write_gate`

When a human delegation context exists, human authority is also intersected.

Current `system_write_gate` remains closed for production inventory mutation.

## Explicitly forbidden generic tools

Even the full-capability schema must never expose:

- raw SQL;
- arbitrary table/column selection;
- PostgreSQL credentials;
- Google Sheet credentials;
- generic SSH/VPS shell;
- arbitrary filesystem access;
- arbitrary outbound HTTP proxying;
- plaintext provider/API secrets;
- unrestricted environment-variable editing.

Full capability means full **typed MSA capability**, not unrestricted infrastructure access.

## Transport/security requirements

- public HTTPS/TLS;
- explicit allowed Host configuration;
- Origin validation and DNS-rebinding protections consistent with current MCP guidance;
- bounded request/response sizes;
- sensible timeouts;
- secret-redacted logs;
- rate/abuse controls;
- health diagnostics separate from tool data;
- stable endpoint and stable tool names.

## ChatGPT product capability boundary

Current OpenAI documentation indicates that modify/write support for custom MCP apps can depend on plan/workspace/product rollout, and some environments may expose only read/fetch behavior.

Therefore the proof must distinguish:

1. **server capability** — MSA publishes the full typed schema;
2. **MSA policy** — current principal is only granted currently authorized operations;
3. **ChatGPT client capability** — the active ChatGPT plan/workspace may or may not permit write/modify actions.

A client limitation does not require redesigning the MCP server.

## Acceptance test

F7.2D0 passes only when all of the following are proven end-to-end:

1. The full-capability remote MSA MCP service is deployed on the VPS and reachable through public HTTPS.
2. ChatGPT can scan/discover the stable MCP catalog.
3. Authentication succeeds without exposing plaintext credentials in Git/logs/docs.
4. Server-level tool discovery works after restart/redeploy.
5. ChatGPT invokes `msa_identity_whoami` successfully.
6. ChatGPT invokes `msa_system_status` successfully.
7. ChatGPT invokes `msa_inventory_read_summary` and receives current real MSA backend data.
8. Relevant results preserve `database_canonical=false`, `migration_baseline_accepted=false`, and F6B test-only status.
9. At least one discoverable but currently ungranted write/control-plane tool is rejected by MSA policy.
10. Missing/invalid credentials are rejected.
11. Revoking the MCP client/credential causes a later ChatGPT invocation to fail.
12. Reissuing/reactivating restores only the intended granted scope.
13. No production inventory mutation, workbook import, DB canonical promotion or provider-model call occurs during the proof.
14. Any ChatGPT plan/workspace limitation on write actions is recorded separately from server/policy behavior.

## Success decision

If the MCP proof passes and ChatGPT can reliably use the typed MSA tools with the required flexibility, MCP becomes the primary ChatGPT access path.

The Custom GPT Action path remains optional and should be implemented only for a concrete standalone-GPT/distribution need or if MCP cannot satisfy a required product capability.

## Failure decision

If ChatGPT cannot connect or invoke tools:

- identify whether the failure is protocol, TLS/network, Host/Origin validation, authentication/OAuth, workspace policy, tool scan, or plan/product limitation;
- correct legitimate implementation defects only;
- do not weaken MSA security or expose raw DB access;
- record any real platform limitation;
- evaluate the optional Custom GPT Action path only if the MCP path cannot meet the intended use.

## Next after connectivity success

Proceed without rebuilding the connector:

1. canonical external-client/AI-agent principal management;
2. Provider Registry and model catalog;
3. internal model assignment;
4. F7.3 actor-aware operation/audit foundation;
5. later location/calculator/analysis capabilities;
6. progressively enable write tools only when their explicit implementation/authorization slices are complete.
