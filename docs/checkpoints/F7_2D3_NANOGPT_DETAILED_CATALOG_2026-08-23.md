# F7.2D3 NanoGPT Detailed Catalog — 2026-08-23

Status: implementation branch; runtime verification pending.

Owner operational evidence before this refinement:

- NanoGPT provider credential was configured through the Owner Web UI;
- provider connection/model fetch succeeded;
- model catalog was viewable in the dashboard;
- the basic OpenAI-compatible fetch left Text/Vision/Tools/Structured largely unknown.

Implementation refinement:

- use NanoGPT documented `?detailed=true` text catalog;
- use official subscription-only and paid-only endpoint membership rather than guessing billing coverage;
- persist detailed capabilities/pricing/billing membership in the existing normalized provider-model catalog;
- add local type-ahead search in the model dialog;
- show input/output USD per 1M tokens plus subscription/paid-only state;
- retain unknown when NanoGPT does not publish a capability or billing classification.

No inventory authority, database canonicality, agent authority, or production write boundary changes.

Runtime evidence must be added only after PR merge/deploy and an Owner-triggered real NanoGPT detailed model fetch.