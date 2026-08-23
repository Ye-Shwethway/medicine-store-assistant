# F7.2D4 Preflight — Agent Assignment Guard

Status: **implementation candidate — pending PR/runtime verification**

Date: 2026-08-23

## Purpose

Close the Agent Management presentation-state flaw observed before native internal-agent runtime work: Provider and Saved model controls must be usable only for `INTERNAL_MODEL` agents.

## Verified pre-existing backend facts

- Agent create/update persists `capability_scopes`, `authority_ceiling`, `execution_policy`, and `confirmation_policy`.
- External MCP effective authority is already evaluated from live OAuth/client grant capability intersected with the bound external agent capability scope and authority ceiling.
- Primary provider/model assignment already rejects agents whose `runtime_mode != INTERNAL_MODEL`.
- Primary assignment already requires an enabled provider plus an active, healthy Owner-saved model.
- Internal-agent permission persistence exists, but native internal-agent runtime/tool enforcement remains pending F7.2D4 because that runtime does not yet exist.

## UI defect

The saved-model enhancement already intended to hide Provider/Saved model fields when runtime mode is not `INTERNAL_MODEL`, but modal state could leak from a previously opened internal-agent editor. An external agent editor could therefore visually expose selectable Provider/Saved model fields even though the backend would reject assignment.

## Candidate correction

- add a dedicated dashboard assignment guard asset;
- on modal open and runtime-mode changes, Provider/Saved model fields are enabled only for `INTERNAL_MODEL`;
- for every other runtime mode, both fields are disabled, cleared, and hidden;
- keep the existing backend runtime-mode rejection as the authoritative server guard;
- validate the UI guard and backend rejection in the saved-model CI workflow;
- preserve no-store/versioned browser delivery.

## Non-goals

This preflight does not implement native model invocation, internal typed tools, fallback execution, AI inventory writes, or canonical DB promotion.

## Next after verification

Proceed with F7.2D4 D4.1 assignment/fallback contract and D4.2 MCP-independent native invocation service.
