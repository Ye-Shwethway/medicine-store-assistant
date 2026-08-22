# Medicine Store Assistant — Dashboard Page Override

Use together with `../MASTER.md`. These rules refine the master system for the web dashboard only.

## Dashboard goals

The dashboard should answer, within a few seconds:

1. Is the system healthy?
2. What inventory state needs attention?
3. What is test-only versus operational truth?
4. Where should the operator go next?

## Desktop composition

- Left navigation: 248 px reference width.
- Header: page title + concise subtitle on the left; environment/data-authority badges on the right.
- Main canvas: metrics row followed by prioritized operational content.
- Avoid placing more than four top-level metric cards in one row.
- Use one dominant information region and one narrower context/authority region rather than many equal cards.

## Overview

Primary widgets:

- staged/test record summary while PostgreSQL is non-canonical;
- attention queue;
- system/read-path health;
- data-authority flow;
- explicit migration-baseline warning.

Do not present test snapshot counts as live canonical stock KPIs.

## Inventory

Primary workflow:

1. search;
2. filter;
3. scan rows;
4. open detail drawer;
5. inspect provenance/status.

Current phase is read-only. Do not show fake edit/save buttons.

Desktop columns should remain aligned through a shared grid. Mobile should move secondary fields into the detail view rather than compressing every column.

## Shadow inspection

Audience: operator/technical reviewer, not general staff.

Show:

- batch identity;
- source/test status;
- classification counts;
- reason summaries;
- API/read status;
- explicit no-write boundary.

Avoid exposing internal secrets or raw credential paths.

## Interaction prototype requirements

The prototype must demonstrate:

- navigation selection;
- search filtering;
- classification filter;
- row selection;
- detail drawer/modal;
- loading state;
- empty result state;
- keyboard-focus affordances;
- responsive behavior concept;
- reduced-motion-safe transitions.

All controls shown in the prototype must have a defined behavior. Disabled future actions must explain why they are disabled.
