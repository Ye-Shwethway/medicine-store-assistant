# F7.2D4.7 — Internal Agent Fallback Management

Status: IMPLEMENTING
Date: 2026-08-23

## Accepted baseline

The native AI Workspace path is production-live and manually accepted for:

- MCP-independent provider-backed internal-agent inference;
- durable conversations/messages;
- grounded bounded native reads over current test/shadow evidence;
- mobile Chat UX, long-answer handling, deterministic USER -> ASSISTANT ordering, message copy/select, conversation preview/time, and owner-scoped delete;
- production inventory writes remain disabled and PostgreSQL remains non-canonical.

## Existing backend truth

The backend already supports an ordered model chain for `INTERNAL_MODEL` agents:

- exactly one `PRIMARY` assignment;
- zero to five ordered `FALLBACK` assignments;
- only ACTIVE/HEALTHY/currently-discovered saved models from ENABLED providers;
- duplicate saved models rejected;
- non-internal agents rejected server-side;
- native runtime attempts PRIMARY first, then FALLBACK in stored order.

The missing product surface is Owner-facing fallback configuration and live failover acceptance.

## This slice

1. Replace the Agent editor's primary-only binding call with the canonical `/model-assignments` chain contract.
2. Add mobile-friendly ordered fallback controls to Owner-only AI Agent Management.
3. Allow up to five fallback models, each selected from tested Owner-saved models.
4. Support add/remove/reorder without changing agent identity or authority.
5. Show fallback count on internal-agent cards.
6. Keep provider/model fields unavailable for non-`INTERNAL_MODEL` agents.
7. Preserve server-side Owner authorization and backend validation as the authority boundary.

## Acceptance

Configuration acceptance:

- Owner can save PRIMARY + ordered FALLBACK chain and reopen the agent editor with the same order;
- duplicate/invalid/unhealthy/stale assignments are rejected by backend;
- non-internal agents cannot receive assignments;
- agent cards show the primary model and fallback count.

Runtime acceptance requires at least two healthy saved models. Once configured:

- force or observe a primary provider/model failure;
- native runtime attempts fallback in order;
- successful response reports `fallback_used=true`;
- attempt provenance records failed primary and successful fallback with provider/model/latency/error evidence;
- public MCP is not used by the native failover path.

If only one healthy saved model exists, configuration UI may ship first and runtime failover acceptance remains pending until another saved model is available.

## Boundaries

No production inventory writes, canonical DB promotion, arbitrary SQL, raw provider credentials, or public-MCP dependency is introduced by this slice.
