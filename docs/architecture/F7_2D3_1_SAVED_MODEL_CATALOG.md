# F7.2D3.1 — Saved Provider Model Catalog

Status: implementation contract

## Purpose

Separate provider discovery from the durable set of models that Medicine Store Assistant is allowed to use.

The required workflow is:

`Fetch provider catalog -> search/filter -> select candidate -> test model -> save approved model -> bind agent from saved models`

A fetched/discovered model is not automatically an approved MSA model.

## Data roles

### Discovered provider models

`ai_provider_models` remains the refreshable snapshot returned by provider model-list APIs. Refresh may add, remove, rename, or change metadata. It is discovery evidence, not assignment authority.

### Saved provider models

A new durable saved-model catalog records Owner-approved provider/model choices. A saved record retains the provider-local model ID, approval/test provenance and status. Refreshing the discovered catalog must never silently delete saved records.

If an already-saved model disappears from the latest provider discovery snapshot, keep the saved record and mark its discovery/availability state stale or unavailable. Agent runtime must fail closed rather than silently substitute another model.

## Model test

Before a discovered model can be saved, the Owner runs a narrow server-side model ping using the configured provider credential.

For OpenAI-compatible text providers, use a minimal non-streaming chat-completion request with a tiny response limit. For NanoGPT this is `POST /api/v1/chat/completions` with the selected model ID. This is an availability/authorization test only; it is not a quality benchmark.

The browser never receives the provider credential. Test responses must be bounded and only safe status/latency/error metadata is retained; do not persist full model output as secret-bearing evidence.

Test states: `UNTESTED`, `HEALTHY`, `ERROR`.

## Save gate

A model may be saved only when:

- the provider exists and has a configured credential;
- the model exists in the current discovered provider catalog;
- the latest model test for that provider/model is `HEALTHY`;
- the Owner explicitly chooses Save/Add to catalog.

Saved catalog actions are Owner-only.

## Agent assignment contract

Only `INTERNAL_MODEL` agents may bind to provider models.

Agent create/edit must expose:

1. Provider selector containing enabled providers;
2. Model selector populated only from that provider's saved catalog;
3. only saved models whose latest model-test status is healthy and not revoked/removed may be newly assigned.

Provider/model assignment never changes stable `agent_id`, call name, human/agent authority, location scope, or the system write gate.

## UI

Provider model browser:

- type-ahead search/filter;
- detailed capability, pricing and billing metadata where provided;
- per-model `Test model` action;
- test state/last-tested result;
- `Save to catalog` enabled only after a healthy test;
- saved badge/action state.

Provider card:

- discovered model count;
- saved model count;
- `View models` for discovered catalog;
- `Saved models` view showing durable approved models and test/availability state.

Agent editor:

- for `INTERNAL_MODEL` runtime only, Provider + Saved model fields;
- changing provider clears incompatible model selection;
- no arbitrary free-text model IDs.

## Security and authority

- Provider API keys remain server-side write-only credentials.
- Model testing is an outbound provider call, not inventory authority.
- Saving a model authorizes model availability for assignment only; it grants no inventory read/write/control capability.
- Production inventory writes remain disabled.
- No raw provider response or arbitrary HTTP proxy is exposed to browser/agent clients.
