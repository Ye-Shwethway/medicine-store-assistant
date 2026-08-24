# F7.2D4.8 Live Export Hang Root Cause

Date: 2026-08-24
Status: root cause confirmed; hotfix in progress

## Symptom

Opening AI Workspace after the live Review/export deployment caused the browser UI to hang.

## Confirmed root cause

`dashboard_multi_agent_live_export.js` installed a subtree `MutationObserver`. Every observer callback called `syncSingleChatExport()`, and that function unconditionally rewrote `actions.innerHTML` whenever an active conversation existed. That rewrite itself generated another child-list mutation, which immediately retriggered the observer. The result was a self-sustaining DOM mutation loop on the browser main thread.

This was a frontend event-loop bug, not a provider, database, Review runtime, export backend, or network failure.

## Hotfix contract

- Export reconciliation must be idempotent.
- The Single Chat export DOM must mutate only when the active conversation ID actually changes.
- Observer callbacks must be coalesced through one scheduled animation-frame reconciliation rather than synchronously rewriting DOM for every mutation.
- Existing live Review polling, Copy controls, formatting normalization, DOCX/JSON endpoints, and inventory write boundaries must remain unchanged.
- Production inventory mutation remains disabled and PostgreSQL remains non-canonical.

## Acceptance

1. Opening AI Workspace does not hang or lock the browser main thread.
2. Single Chat export controls appear for the active conversation.
3. Switching conversations updates export targets once without observer feedback.
4. Multi-Agent Review remains usable.
5. Existing backend and AI Workspace validation suites remain green.
