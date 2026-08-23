# F7.2D4.8 REVIEW UI 500 + chatbox hotfix

Status: planned/implementation in progress

Date: 2026-08-24

## Observed production behavior

The Owner Multi-Agent REVIEW UI loads preset/session data, but initial workspace load still reports `Request failed: 500` after the first work-list hotfix deployment. This narrows the remaining failure to the Review work/history read path rather than the preset/session/role surface.

## Hotfix contract

1. A failure to load recent Review history must not block preset selection, role configuration, or running a new Review.
2. The work-list endpoint should fail soft with a bounded degraded response instead of returning HTTP 500 for SQL/database read failures.
3. The response must not expose SQL, credentials, stack traces, DB internals, or arbitrary exception text.
4. Work Item detail remains a separate read when the Owner opens a persisted item.
5. No inventory mutation, MCP schema/action, migration, or canonicality change is part of this hotfix.
6. Multi-Agent REVIEW should present outputs in a dedicated chatbox-style conversation surface: Owner task, Analyst/Reviewer/Synthesizer turns, status/provenance, and Owner revision interaction.
7. The chatbox is a presentation layer over the same Work Item/Artifact/Review/Event substrate; it does not create a second workflow or message store.

## Acceptance

- Initial Multi-Agent tab load no longer shows a blocking 500 if recent-work history cannot be read.
- A degraded history warning is shown only in the history area.
- Preset + role controls remain usable.
- Review Work Item details render participant artifacts as chat-style turns.
- Review verdict and provider/model provenance remain visible.
- `Production mutation: NO` and DB non-canonical boundaries remain visible.
- Existing reload-safe history behavior remains when the read path is healthy.
