# Multi-Agent single-surface UI

Owner feedback established that the Multi-Agent workspace should not stack a Recent Review layer and a separate detail layer in the same page flow.

Target interaction:

- setup/list state shows Review setup plus Recent Review cards
- opening a Review or starting a new Review switches the same Multi-Agent surface into one full-width chatbox state
- the chatbox contains Owner task, internal-agent turns, external MCP review turns, Owner feedback, and later internal-agent passes in durable chronological order
- a visible `Back to reviews` control returns to setup/list state
- external review is a normal persisted chat turn, not a transient secondary detail
- production mutation remains disabled
