# F7.2D4.8 Live Review + Conversation Export Plan

Status: approved implementation plan

Date: 2026-08-24

## Goal

Polish the accepted native REVIEW workflow into a practical Owner work surface, then add one shared point-in-time export subsystem for Single-Agent Chat and Multi-Agent Review.

## Review polish

1. Keep REVIEW presets flexible: two-agent REVIEWER -> SYNTHESIZER is valid; ANALYST is optional unless assigned by the Owner.
2. Do not invent unconfigured roles in orchestration context. Every participant receives the actual configured role sequence and only persisted prior participant outputs.
3. Replace all-at-once UI completion with persisted turn-by-turn progress: create the Work Item immediately, execute native participants in backend background work, persist each artifact/event as the participant completes, poll the durable Work Item from the browser at a short bounded interval, render each completed turn as soon as it is persisted, and stop polling at WAITING_OWNER or FAILED.
4. This slice is turn streaming, not token streaming. No WebSocket/SSE is required yet.
5. Reuse Single-Agent Chat display normalization for Review bubbles so raw Markdown markers/tables are not shown as UI noise.
6. Add per-message Copy controls to Owner and agent Review turns, matching Single-Agent Chat behavior.
7. Preserve provider/model/fallback/latency provenance under agent turns.
8. Preserve production mutation and database-canonicality boundaries.

## Unified Conversation Export

One shared backend export service covers both work surfaces. First formats are DOCX for human-readable snapshots and JSON for machine-readable audit/automation/future federation. PDF and Markdown are later follow-ups.

Single-Agent snapshots include conversation metadata, ordered messages, selected agent, assistant provenance, attachments, timestamps and export metadata. Multi-Agent snapshots include Work Item lifecycle state, Owner task/evidence, ordered participant artifacts and roles, artifact-bound Review records/verdicts, Owner revisions, provenance, Attention state, immutable events, production_mutation/database_canonical flags, timestamps and snapshot schema version.

## Snapshot invariant

Export is immutable point-in-time output, not a live-linked document. Later revisions do not modify earlier downloaded files; re-exporting creates a newer snapshot.

## Authorization

Single-Agent export uses the same authenticated access and conversation ownership as Chat readback. Multi-Agent Review export remains Owner-only. Export never grants inventory authority or performs store mutation.

## UI

Single-Agent Chat header and Multi-Agent Review Work Item header each expose Export -> DOCX / JSON, using authenticated same-origin browser downloads and a mobile-first layout.

## Acceptance

Review polish passes when a two-agent REVIEWER -> SYNTHESIZER preset runs without implying a configured ANALYST, each persisted participant turn appears while later participants are still running, Copy works, Markdown display noise is normalized, and final state remains WAITING_OWNER with no store mutation.

Export passes when an authorized user can download complete Single-Agent DOCX/JSON snapshots, Owner can download complete Multi-Agent DOCX/JSON snapshots, ordered content and provenance are present, cross-user/unauthorized export is denied, and file generation does not mutate source records.
