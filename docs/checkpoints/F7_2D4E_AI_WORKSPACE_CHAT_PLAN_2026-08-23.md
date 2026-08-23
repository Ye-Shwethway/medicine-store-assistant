# F7.2D4E — AI Workspace Chat implementation checkpoint

Date: 2026-08-23

Status: IMPLEMENTED + DEPLOYED; manual UI/runtime acceptance pending.

Production merge SHA: `4a71068e81bacb2b97db7d07f2ed592f3be00548`

Production deploy run: `32647208398` — `status=success`

## Locked UX / authority architecture

- `AI Agent Management` remains the Owner-only control plane.
- `AI Workspace` is a separate top-level operational work surface in the Dashboard navigation.
- Single-agent Chat is available to the Owner and to non-Owner users who pass the AI Workspace access policy.
- Multi-Agent execution remains Owner-only. The initial AI Workspace shows an Owner-only Multi-Agent placeholder; no non-Owner execution route exists in this slice.
- The Owner is never blocked by the non-Owner AI Chat switch or per-user entitlement.
- Non-Owner denial happens before any provider request.
- Provider/model assignment remains hidden from ordinary Chat selection; users select a named agent, not a provider model.
- Internal Chat runs through the MCP-independent native `INTERNAL_MODEL` runtime. Public MCP is not in the normal path.

## Implemented scope

1. Durable single-agent conversations/messages owned by the signed-in human user (`0018_ai_workspace_conversations`).
2. Access-gated AI Workspace APIs to list eligible internal agents, list/create/read conversations, and send a message.
3. Persisted conversation history is included as bounded context on later turns.
4. A top-level `AI Workspace` Dashboard navigation item and operational Chat view with agent selector, conversation list, message thread, composer, and runtime provenance.
5. Owner-only Multi-Agent tab/placeholder; orchestration execution remains a later slice.
6. MSA typed tools remain detached; this is conversational inference only.
7. Production inventory writes remain disabled.

## Security invariants

- Every conversation is owned by one authenticated human user; users can read/write only their own conversations.
- Conversation agent must be ACTIVE + `INTERNAL_MODEL` and have an enabled/healthy primary model path.
- AI Chat access policy is checked server-side for workspace agent listing, conversation access/create, and message send.
- Provider invocation occurs only after session, AI Chat policy, conversation ownership, and agent validation succeed.
- Cross-user conversation lookup returns 404 rather than exposing existence.
- Multi-Agent execution endpoints are not added in this slice; future endpoints must use Owner backend authorization.

## Automated verification

PR #90 `Add durable AI Workspace Chat` passed all triggered checks, including:

- Validate AI Workspace Chat
- Validate AI Workspace access policy
- Validate backend changes
- Validate native internal agent runtime
- Validate internal agent model assignments
- Validate MCP agent binding
- Validate MCP audit proof
- Validate broad typed reads
- Validate saved model catalog

Production deployment issue #26 confirms `status=success` for the merge SHA above.

## Manual acceptance still required

- Owner sees `AI Workspace` in primary navigation independently of `AI Agent Management`.
- Owner can select an internal agent, create a conversation, send multiple messages, refresh, and retain history/context.
- Runtime provenance identifies the actual provider/model and native backend path.
- Multi-Agent tab appears only for Owner and remains non-executable placeholder in this slice.
- Later non-Owner acceptance must prove allowed/blocked behavior and ownership isolation with real staff accounts.
