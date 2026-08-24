# Reorder Baseline and AI Enhancement

Status: **LOCKED ARCHITECTURE DIRECTION — implementation later than F6D foundation**

## Purpose

Keep reorder useful even when every AI provider is unavailable, while still allowing AI and richer analytics to improve recommendations when available.

Core rule:

> **Reorder must have a deterministic baseline fallback. AI improves the recommendation; AI is not the only way to obtain one.**

The legacy Excel `Estimated Reorder Qty` proves the operational value of a baseline calculation, but the future system is not locked to that exact historical formula.

## Two-layer model

### Layer 1 — deterministic baseline

The backend can produce a baseline reorder recommendation without any external AI service.

The baseline uses only structured local data and configuration available in PostgreSQL, for example:

- current location balance;
- recent usage totals/history;
- configured reorder level/minimum stock;
- safety-stock factor or target coverage;
- expected/incoming stock where known;
- lead-time setting where configured;
- store scope;
- simple deterministic trend windows where implemented.

The exact baseline algorithm is versioned/configurable implementation policy, not immutable database identity.

### Layer 2 — AI / advanced enhancement

When AI is available, it may review or improve the baseline using wider context such as:

- unusual usage spikes;
- multi-month trend interpretation;
- seasonality;
- expiry risk;
- cross-store demand;
- anticipated transfers;
- contextual operational notes;
- alternative scenarios;
- agent review/debate;
- explanation of uncertainty.

AI output remains a proposal/review artifact until authorized workflow accepts it.

## Availability behavior

### AI available

`canonical stock/history -> deterministic baseline -> AI enhancement/review -> human/authorized workflow -> final reorder`

### AI unavailable

`canonical stock/history -> deterministic baseline -> human review/adjustment -> final reorder`

The user must never be forced to manually calculate every item merely because AI providers are unavailable.

## Configuration philosophy

Do not hard-code one forever formula into the canonical inventory schema.

Store only the durable inputs/configuration required to run deterministic strategies, such as store/product policy values or versioned reorder-policy settings when the feature is implemented.

A reorder engine should identify which deterministic strategy/version produced a proposal so historical results remain explainable.

## Final business result

Keep separate:

1. deterministic baseline recommendation;
2. AI-enhanced proposal if one exists;
3. reviewer comments/agent reviews;
4. final authorized reorder quantity.

This preserves the established real-world behavior where an estimated quantity is only a starting point and final quantities may be manually adjusted.

## F6D boundary

F6D does **not** need to implement the full reorder engine.

It must preserve the data needed later:

- accurate store/lot balances;
- dated usage history;
- receipt/incoming history;
- transfers;
- expiry;
- durable Product identity;
- location identity;
- actor/audit provenance;
- a clean path for store/product reorder configuration.

A minimal deterministic fallback engine may be implemented in a later bounded slice once the canonical inventory foundation is proven.

## Failure rule

AI outage may reduce recommendation sophistication, but it must not remove reorder capability or stop ordinary inventory operation.
