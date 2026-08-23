# F7.2D4A — External MCP Agent Binding

Status: implementation slice

## Goal
Bind an authenticated external MCP connection to one durable named MSA AI agent so inbound ChatGPT/custom-MCP calls can be attributed to that agent identity without changing the transport connection.

## Direction boundary

`ChatGPT/custom MCP client -> MSA MCP -> named external agent -> MSA authority engine -> typed operation`

MSA does not call back into ChatGPT through this binding. Outbound/internal AI execution remains a separate provider-backed runtime path.

## Identity layers
Keep these distinct:

1. Human user — canonical MSA person/account that authorizes or configures access.
2. AI agent — durable named identity such as IANEO or Bamboo; stable `agent_id` survives rename/provider changes.
3. Transport/client — OAuth MCP grant/client through which an external agent reaches MSA.

The transport does not become the agent. A binding resolves the transport grant to the configured named agent.

## Binding rules
- Owner-only management surface.
- Only `EXTERNAL_MCP_CLIENT` agents may receive MCP OAuth bindings in this slice.
- One active OAuth grant resolves to at most one named agent.
- One named external MCP agent binds to at most one active OAuth grant in this slice.
- Bind/unbind does not require reconnecting or reauthorizing ChatGPT.
- Agent disable/revoke immediately prevents that agent from contributing capability scope.
- Unbound OAuth grants remain transport-authenticated for continuity, but identity reports `UNBOUND`; they are not attributed to a named agent.

## Effective MCP authority after binding
For a bound active external agent:

`effective MCP capability = OAuth grant capability ∩ agent capability_scopes`

Transport scopes such as `mcp:connect` and `offline_access` remain transport metadata and are not agent authority.

System write/control gates still apply after the intersection. Binding can never enable production inventory writes or control-plane writes by itself.

## MCP identity response
`msa_identity_whoami` must return, when bound:
- transport/client identity
- OAuth subject/human authorizer identity reference
- `agent_binding_status = BOUND`
- stable `agent_id`
- `agent_display_name`
- `agent_call_name`
- agent runtime mode
- effective scopes

When no valid named-agent binding exists, it returns `agent_binding_status = UNBOUND` and no invented agent identity.

## Agent Management UI
External/MCP agent cards show an MCP connection block:
- current binding status
- OAuth client display name/client id, without tokens
- bind/rebind control using active OAuth grants
- unbind action

No token value, authorization code, refresh token, or provider secret is ever returned to the browser.

## Audit hand-off
This slice resolves a durable actor identity but does not implement the full Audit UI/operation ledger.

F7.3 will persist and expose the full chain:
`human/grantor -> named agent -> transport/client -> operation -> capability -> resource/location -> result -> correlation id -> timestamp`

Audit UI will later support date/month, human, agent, runtime/transport, provider/model, operation, result, and location filters. Historical/month navigation must preserve records rather than silently deleting them.

## UI consistency rule
All production Agent Management actions must use the MSA button system:
- primary constructive CTA: green filled `.primary`
- neutral/lifecycle action: `.secondary`
- destructive/irreversible action such as Revoke: `.danger-action`
- browser-default unstyled action buttons are not acceptable

## Acceptance
1. Owner can list active MCP OAuth grants without secret material.
2. Owner can bind an `EXTERNAL_MCP_CLIENT` agent to an active grant.
3. Binding another agent/grant that violates one-to-one rules is rejected or explicitly replaces via typed update; no ambiguous identity exists.
4. `msa_identity_whoami` returns the configured named agent after binding.
5. Effective MCP capabilities are the intersection of grant and active agent capabilities.
6. Disabling/revoking the agent immediately removes agent capability contribution.
7. Unbinding returns `UNBOUND` without breaking OAuth transport authentication.
8. No MCP reconnect is required for bind/unbind changes.
9. Production inventory writes/control-plane writes remain disabled.
10. Agent Management destructive buttons use the documented danger style.
