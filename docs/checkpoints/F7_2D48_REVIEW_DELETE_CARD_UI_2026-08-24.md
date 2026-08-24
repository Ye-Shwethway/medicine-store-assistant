# F7.2D4.8 Review Delete Card UI Polish — 2026-08-24

## Change

Owner feedback showed that Multi-Agent Review Delete was visually grouped with DOCX/JSON export actions in the opened Review detail header.

The UI now follows the established Single-Agent Chat hierarchy:

- Recent Review card = open/select surface
- top-right `×` on each Recent Review card = Delete
- opened Review detail = DOCX/JSON export actions only

The existing audit-preserving DELETE backend semantics are unchanged: the Work Item becomes `CANCELLED`, disappears from Recent Review work, open Attention is resolved, and immutable audit evidence remains preserved.

## Mobile behavior

The delete control is a sibling of the card open button rather than a nested button. It has an independent touch target and stops propagation so Delete does not also open the Review.

## Boundaries

No inventory mutation, database canonical promotion, MCP change, native-tool change, or workflow lifecycle change is introduced by this UI polish.
