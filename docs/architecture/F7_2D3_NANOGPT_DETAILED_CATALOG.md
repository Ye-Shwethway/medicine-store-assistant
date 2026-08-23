# F7.2D3 NanoGPT Detailed Catalog Enrichment

Status: implementation refinement authorized 2026-08-23.

## Goal

Upgrade the verified NanoGPT Provider Registry path from the OpenAI-compatible basic model listing to NanoGPT's documented detailed model catalog so MSA can display useful capabilities, pricing, billing inclusion, and fast client-side search without guessing metadata.

## Official NanoGPT contract used

MSA uses these NanoGPT text-model endpoints:

- `GET /api/v1/models?detailed=true` — canonical detailed text catalog with descriptions, context/output limits, capability flags, and per-million-token pricing.
- `GET /api/subscription/v1/models?detailed=true` — models explicitly included in the current NanoGPT subscription catalog.
- `GET /api/paid/v1/models?detailed=true` — paid/premium/extras catalog that is not subscription-included.

The membership endpoints are authoritative for the display labels `Subscription included` and `Paid only`. MSA must not infer subscription coverage from price, provider, model family, or model name.

## Normalization

For NanoGPT text models, detailed catalog fields map into the existing `ai_provider_models` record:

- `supports_text=true` because this endpoint is the text-chat catalog;
- `capabilities.vision -> supports_vision`;
- `capabilities.tool_calling -> supports_tools`;
- `capabilities.structured_output -> supports_structured_output`;
- `context_length -> context_window`;
- `max_output_tokens -> max_output_tokens`;
- detailed `capabilities`, `pricing`, `description`, `category`, and billing-membership state remain in bounded `provider_metadata`.

Unknown or missing provider fields stay unknown. MSA does not invent support.

## Pricing semantics

NanoGPT detailed text pricing uses USD per million tokens:

- `pricing.prompt` = input rate per 1M tokens;
- `pricing.completion` = output rate per 1M tokens.

Subscription inclusion is separate from price. The displayed price remains useful as pay-as-you-go/overage reference even when a model is subscription-included. Explicit provider selection may have different billing semantics and is not represented as subscription-covered merely because the base model is included.

## UI

The Provider Models dialog must provide:

- type-ahead model search over display name and model ID;
- live result count;
- Text / Vision / Tools / Structured capability state;
- optional Reasoning state when NanoGPT reports it;
- input and output USD-per-1M-token rates when supplied;
- `Subscription included`, `Paid only`, or `Billing unknown` badge derived from official endpoint membership;
- context and max-output limits when supplied.

Search is local over the already-loaded normalized catalog and must not send each keystroke to NanoGPT.

## Security and reliability

- NanoGPT API credentials remain write-only in the Web UI and server-side only.
- Detailed catalog requests are server-to-server.
- Response size/model count remain bounded.
- Redirects are not followed.
- A failure to resolve optional billing membership must never be turned into an invented paid/subscription classification; show unknown instead.
- No inventory write, workbook import, canonical DB promotion, or agent authority change is part of this refinement.

## Release integrity

Because `dashboard_agents.js` changes, the dashboard entrypoint asset version must also be bumped under the Web asset release-integrity contract before this refinement is considered delivered.