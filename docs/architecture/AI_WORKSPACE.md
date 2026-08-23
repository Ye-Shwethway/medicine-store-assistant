# AI Workspace

AI Workspace is the operational AI work surface for Medicine Store Assistant. It is intentionally separate from the Owner-only AI Agent Management control plane.

## Surfaces

### AI Agent Management — control plane
Owner-only. Manages named agents, provider/model assignments, capability ceilings, reusable multi-agent session definitions, and the global non-Owner AI Chat switch.

### AI Workspace — work plane
Top-level Dashboard destination.

- `Chat`: single selected internal agent; Owner plus authorized non-Owner users.
- `Multi-Agent`: Owner-only execution surface. Initial UI may be a bounded placeholder until orchestration execution is implemented.

## Native execution path

Normal Web Chat path:

`Signed-in human -> AI Workspace backend -> access/ownership checks -> native INTERNAL_MODEL runtime -> configured provider/model -> response`

Public MCP is not part of this normal path.

## Access policy

Owner always passes AI Chat access.

For a non-Owner:

1. global non-Owner AI Chat must be enabled;
2. per-user entitlement must not be `BLOCK`;
3. later agent/location/tool permissions further restrict what can be used.

A denied request stops before any provider API request.

## Conversation ownership

Single-agent conversations are durable server-side records owned by one human user and linked to one named internal agent. A non-Owner may not read or mutate another user's conversation. Provider/model identity is runtime provenance, not conversation identity.

## Future tool authority

When MSA typed tools are attached, effective authority must be bounded by the intersection of system gate, human-user scope, selected agent scope/ceiling, location scope, and operation class. Agent authority must never elevate the signed-in human user's authority.
