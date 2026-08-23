# F7.2D4A — External MCP Named-Agent Binding — Verified 2026-08-23

## Runtime anchor

- PR #70
- merge SHA `5f00458b55e85cfe4e3a78f5fb7b2f8517e159e2`
- deploy run `32631778542`
- issue #26 `status=success`
- migration head `0014_mcp_agent_bindings`

## Verified implementation

- Owner-only active MCP OAuth grant listing without token/secret readback.
- Durable one-to-one active binding between an OAuth grant and a named `EXTERNAL_MCP_CLIENT` agent.
- Bind/rebind/unbind is controlled from Agent Management and does not require reconnecting ChatGPT.
- MCP `msa_identity_whoami` resolves the bound stable `agent_id`, display name, call name, runtime mode, state, authority ceiling, execution/confirmation policy, client name, and effective scopes.
- Bound MCP authority is computed from the live OAuth grant and live named-agent capability/authority ceiling; provider/model identity is not part of that authority calculation.
- Disabled/revoked/non-external agents contribute no named-agent capability authority.
- Unbound OAuth transport remains authenticated but reports `agent_binding_status=UNBOUND`; no agent identity is invented.
- Production inventory writes and control-plane writes remain system-gated off.
- Agent Management now has explicit MCP connection binding UI for external MCP agents.
- Destructive `Revoke` styling is normalized through the MSA danger-action design rather than browser-default styling.
- MCP binding overlay observes direct list replacement only (`subtree:false`) to avoid the prior MutationObserver self-trigger freeze failure mode.

## Direction boundary

`ChatGPT/custom MCP client -> MSA MCP -> named external agent -> authority engine -> typed operation`

MSA does not call back into ChatGPT through this binding. Internal/outbound AI execution remains provider-backed and is handled separately.

## Audit hand-off

This slice resolves the durable named actor identity required by F7.3 but does not yet persist the full actor-aware operation ledger.

F7.3 Audit should later expose/filter by at least:

- date/time and month;
- human/delegating user;
- named AI agent;
- transport/client/runtime;
- provider/model when relevant;
- operation type;
- result/state;
- store/location and target references.

Historical month navigation/archive must preserve audit records rather than silently deleting or rewriting them.

## Current next work

Continue F7.2D4 with internal provider/model assignment, fallback policy, canonical runtime identity injection, and a narrow real provider-backed inference proof. F7.3 actor-aware Audit/operation ledger follows after the Agent/Provider control-plane foundation is complete.
