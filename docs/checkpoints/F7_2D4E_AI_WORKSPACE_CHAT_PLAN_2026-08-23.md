# F7.2D4E — AI Workspace Chat implementation checkpoint

Date: 2026-08-23

## Locked UX / authority architecture

- `AI Agent Management` remains the Owner-only control plane.
- `AI Workspace` is a separate top-level operational work surface in the Dashboard navigation.
- Single-agent Chat is available to the Owner and to non-Owner users who pass the AI Workspace access policy.
- Multi-Agent execution remains Owner-only. The initial AI Workspace may show an Owner-only Multi-Agent tab/placeholder, but no non-Owner execution route is permitted.
- The Owner is never blocked by the non-Owner AI Chat switch or per-user entitlement.
- Non-Owner denial must happen before any provider request.
- Provider/model assignment remains hidden from ordinary Chat selection; users select a named agent, not a provider model.
- Internal Chat runs through the MCP-independent native `INTERNAL_MODEL` runtime. Public MCP is not in the normal path.

## Slice scope

1. Add durable single-agent conversations/messages owned by the signed-in human user.
2. Add access-gated AI Workspace APIs to list eligible internal agents, list/create/read conversations, and send a message.
3. Preserve conversation context in provider calls rather than treating each message as an isolated ping.
4. Add a top-level `AI Workspace` Dashboard navigation item and operational Chat view with agent selector, conversation list, message thread, and composer.
5. Show Multi-Agent as Owner-only and explicitly not yet executable in this slice.
6. Keep MSA typed tools detached; this remains conversational inference only.
7. Keep production inventory writes disabled.

## Security invariants

- Every conversation is owned by one authenticated human user; non-Owners may read/write only their own conversations.
- Conversation agent must be ACTIVE + `INTERNAL_MODEL` and have an enabled valid model chain.
- AI Chat access policy is checked server-side for every workspace read/create/send operation that can expose or invoke AI Chat.
- Provider invocation occurs only after session, AI Chat policy, conversation ownership, and agent validation succeed.
- Multi-Agent execution endpoints are not added in this slice; future endpoints must use Owner backend authorization.

## Acceptance

- Owner sees `AI Workspace` in primary navigation independently of `AI Agent Management`.
- Owner can create a conversation with a named internal agent, send multiple messages, refresh, and retain history/context.
- A permitted non-Owner can use single-agent Chat.
- A blocked non-Owner receives a backend 403 and no provider request is made.
- Non-Owner cannot access another user's conversation by ID.
- Multi-Agent UI is Owner-only and marked as a later execution slice.
