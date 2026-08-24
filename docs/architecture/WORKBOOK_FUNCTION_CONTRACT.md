# Workbook Function Contract

Status: **F6C working artifact — source inspection required**

Purpose: capture the exact operational behavior that the future backend must reproduce or intentionally preserve through compatibility projections.

## Main Stock

Pending verification from the current authorized source:

- exact visible column order and headers;
- editable vs formula/lookup/integration-managed cells;
- product/local-name semantics;
- expiry-lot row semantics;
- CMS Serial / CMS Code / CMS Price / Price relationships;
- received, usage, balance, reorder and remark fields;
- row insertion/removal/reorder behavior;
- expiry suffix/display behavior;
- month rollover behavior.

## Daily Usage

Pending verification:

- exact A:D synchronization source and direction;
- Day 1–31 edit semantics;
- multiple issues on the same day/lot;
- monthly total and remaining/current-balance formulas;
- remark and expiry projections;
- month reset/archive sequence;
- literal non-FIFO recording compatibility.

## This Month Received

Pending verification:

- exact columns;
- source/filter rule;
- whether any field is independently editable business data;
- month reset/archive behavior.

## Reorder

Pending verification:

- exact Main Stock inputs;
- formula/threshold/rounding behavior;
- generated working-sheet behavior;
- timing within month-close workflow.

## Final Reorder

Pending verification:

- copy/generation step;
- fields Owner may edit manually;
- submission/export behavior;
- archive behavior;
- distinction between calculated recommendation and final approved result.

## CMS catalogue and transfers

Pending verification:

- current catalogue columns and retention rules;
- serial/code/name/price relationships;
- recycled/retired/new code handling;
- transfer sheet/document layout;
- receipt quantity/unit/expiry/price evidence;
- mapping and new-lot behavior.

## Monthly lifecycle / Excel Master

Pending verification:

- opening-balance carry forward;
- exact close sequence;
- Master/archive file creation;
- copy/reset behavior per sheet;
- macros/formulas with business meaning;
- outputs required for historical re-export.

## Completion rule

Replace `Pending verification` only with source-backed facts. Any ambiguity must remain explicit and be routed to Owner review before F6D schema changes or a fresh shadow import.
