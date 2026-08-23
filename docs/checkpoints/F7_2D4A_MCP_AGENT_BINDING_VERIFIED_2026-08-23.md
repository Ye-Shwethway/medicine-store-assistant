# F7.2D4A — External MCP Named-Agent Binding — Verified 2026-08-23

## Runtime anchor

- binding implementation PR #70
- merge SHA `5f00458b55e85cfe4e3a78f5fb7b2f8517e159e2`
- binding deploy run `32631778542`
- issue #26 `status=success`
- binding migration `0014_mcp_agent_bindings`
- replacement OAuth cleanup PR #80
- current production merge/deploy SHA `a669890d4cf34c061f28296f64c306d95d4ee012`
- cleanup deploy run `32639464966` — success
- current production migration head `0016_revoke_stale_chatgpt_oauth`

## Verified implementation

- Owner-only active MCP OAuth grant listing without token/secret readback.
- Durable one-to-one active binding between an OAuth grant and a named `EXTERNAL_MCP_CLIENT` agent.
- Bind/rebind/unbind is controlled from Agent Management and does not require reconnecting ChatGPT.
- MCP `msa_identity_whoami` resolves the bound stable `agent_id`, display name, call name, runtime mode, state, authority ceiling, execution/confirmation policy, client name, and effective scopes.
- Bound MCP authority is computed from the live OAuth grant and live named-agent capability/authority ceiling; provider/model identity is not part of that authority calculation.
- Disabled/revoked/non-external agents contribute no named-agent capability authority.
- Unbound OAuth transport remains authenticated but reports `agent_binding_status=UNBOUND`; no agent identity is invented.
- Production inventory writes and control-plane writes remain system-gated off.
- Agent Management has explicit MCP connection binding UI for external MCP agents.
- Destructive `Revoke` styling is normalized through the MSA danger-action design rather than browser-default styling.
- MCP binding overlay observes direct list replacement only (`subtree:false`) to avoid the prior MutationObserver self-trigger freeze failure mode.

## Replacement registration cleanup — VERIFIED

When the ChatGPT MCP app was replaced, duplicate same-name OAuth registrations/grants were visible in the binding selector. PR #80 added a one-time migration to reconcile that stale server-side state without changing the newest replacement connection.

Cleanup behavior:

- rank ACTIVE `ChatGPT` grants per user/client-name by newest creation;
- keep the newest ACTIVE grant;
- remove stale bindings attached to older duplicates;
- revoke tokens for older duplicate grants;
- mark older duplicate grants `REVOKED`;
- revoke an old client registration when no ACTIVE grant remains for it;
- leave the newest replacement grant untouched.

PR #80 validation runs for backend, saved-model catalog, MCP audit, and MCP agent binding all passed. Production deploy run `32639464966` also passed backend verification and the public MCP OAuth boundary checks.

## Live named-agent acceptance — VERIFIED

The replacement client now passes the full named-agent acceptance path:

`ChatGPT replacement MCP -> newest ACTIVE OAuth grant -> IANEO binding -> mcp:read typed operation -> append-only Audit evidence`

Verified results:

- schema `2026-08-23.v2.1`;
- 106 scanned MCP actions;
- named agent `IANEO`;
- binding `BOUND`;
- read enabled;
- write/control disabled;
- `msa_shadow_read_rows` successfully returned live `NEW_UNMAPPED` detail;
- Dashboard Audit recorded `IANEO -> msa_shadow_read_rows -> SUCCESS`, transport `EXTERNAL_MCP`, runtime `EXTERNAL_MCP_CLIENT`, capability `mcp:read`, timestamp 2026-08-23 19:02:38 local.

No additional connector recreation is required for the current v2.1 schema contract.

## Direction boundary

`ChatGPT/custom MCP client -> MSA MCP -> named external agent -> authority engine -> typed operation`

MSA does not call back into ChatGPT through this binding. Internal/outbound AI execution remains provider-backed and is handled separately.

## Audit hand-off

The external actor path now has both durable named-agent resolution and minimal append-only read evidence. Full F7.3 still expands the Audit product surface and operation ledger.

F7.3 Audit should expose/filter by at least:

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

Continue F7.2D4 with internal provider/model assignment, fallback policy, canonical runtime identity injection, and a narrow real provider-backed inference proof. The replacement external-MCP acceptance prerequisite is complete. F7.3 actor-aware Audit/operation ledger follows after the Agent/Provider control-plane foundation is complete.