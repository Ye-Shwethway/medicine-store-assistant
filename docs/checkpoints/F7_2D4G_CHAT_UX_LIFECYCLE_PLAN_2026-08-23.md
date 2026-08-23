# F7.2D4G — AI Workspace Chat UX + Lifecycle

Date: 2026-08-23
Status: IMPLEMENTATION

## Acceptance evidence entering this slice

F7.2D4F native bounded reads are production-live and manually accepted from AI Workspace. Bamboo Leaf successfully returned the real F6B shadow summary and real NEW_UNMAPPED rows through the native MSA backend without public MCP.

Observed UX defects from mobile acceptance:

- long native-read answers can end mid-response because AI Workspace still uses the native runtime's 1024-token default output limit;
- stored messages can appear out of user/assistant order because both rows in one transaction can share the same `now()` timestamp and the secondary UUID ordering is random;
- Markdown markers such as `#`, `**`, backticks and pipe-table syntax are shown literally;
- conversation cards lack a useful first-message preview and human-friendly last-interaction time;
- conversations cannot be deleted;
- message copying/long-press selection is not intentionally supported.

## Implementation

1. Increase AI Workspace output budget for complete answers, especially native tool results, while keeping the global hard model/runtime limit bounded.
2. Make message ordering deterministic: timestamp, USER before ASSISTANT for equal timestamps, then stable ID.
3. Request clean plain-text replies from the native Workspace prompt and sanitize legacy Markdown-like display without executing HTML.
4. Make message text selectable and add an explicit Copy action for each message.
5. Add first USER-message preview and human-friendly `updated_at` to conversation cards.
6. Add authenticated owner-of-conversation DELETE endpoint; deleting a conversation cascades its messages and cannot target another user's conversation.
7. Add conversation-card delete control with confirmation and safe selection fallback.
8. Keep native tools read-only; do not widen authority or enable production writes.

## Security / data boundaries

- AI Workspace access policy remains the first request gate.
- Conversation ownership remains backend-enforced for read/send/delete.
- Deletion is limited to the authenticated conversation owner.
- Display cleanup is text-only; no model HTML is injected into the DOM.
- Public MCP is not used by the native Chat path.
- PostgreSQL remains non-canonical and F6B remains test/shadow evidence.

## Acceptance

Pass when mobile verification shows:

- long 7-row NEW_UNMAPPED answer reaches a natural end rather than token truncation;
- every turn renders USER then ASSISTANT in deterministic sequence;
- no raw Markdown heading/bold/table markers clutter normal display;
- each message can be copied and text can be long-pressed/selected;
- conversation cards show first-message preview + human-friendly last interaction;
- delete removes the selected owned conversation and its card/history;
- refresh preserves remaining conversations and sequence;
- production inventory writes remain disabled.
