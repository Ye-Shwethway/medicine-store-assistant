# F7.2D3 Provider Registry — Verified Checkpoint

Date: 2026-08-23

Status: **VERIFIED COMPLETE**

## Runtime anchor

- PR #60 — `Implement F7.2D3 Provider Registry and refine agent origin UI`
- main source SHA: `882c67b0134edb59156c17e948128de0ca8c3365`
- deployment run: `32621925138`
- deployment job: `97151213410`
- issue #26: `status=success`
- migration: `0011_ai_agents -> 0012_providers`

## Verified Provider Registry foundation

Owner-only Provider Registry supports:

- OpenAI
- Google Gemini
- OpenRouter
- NanoGPT
- generic public-HTTPS `OPENAI_COMPATIBLE`

Persistent provider state includes stable provider ID, display name/kind/base URL/compatibility mode, opaque credential reference, enabled/disabled state, connection/model-fetch status/timestamps, sanitized error code, and provenance.

## Secret boundary

Provider credentials are write-only from the Owner Web UI.

- dedicated server-side Docker volume: `msa_provider_secrets`;
- PostgreSQL stores only opaque `credential_ref`;
- saved API keys are never returned to the browser;
- runtime verifier used a dummy secret and verified the DB did not contain the plaintext value;
- credential removal deletes the corresponding secret file;
- provider secrets are distinct from MCP OAuth/client credentials.

No real provider secret appears in Git, logs, checkpoint docs, or chat.

## Provider/model workflow

Implemented typed operations support:

`Add provider -> provision credential -> Test connection -> Fetch models -> inspect normalized catalog -> Enable/Disable`

Provider enablement fails closed until a credential exists, connection status is healthy, and model fetch has succeeded.

Deployment verification intentionally made **no real provider API call**. The first real provider connection/model fetch must be initiated from the Owner Web UI after the Owner supplies a credential there.

## Dynamic model catalog

Model discovery stores normalized provider-local model ID/name, availability, nullable capability flags, context/output limits where supplied, bounded provider metadata, and fetch timestamps.

Capability values may be `true`, `false`, or unknown/null. Unknown is not silently promoted to supported.

Provider health, model catalog state, and AI-agent health remain separate.

## Custom provider security

Custom provider base URLs must use public HTTPS. The implementation rejects embedded URL credentials, query/fragment, private/loopback/link-local/multicast/reserved/unspecified destinations, and redirects. Destination resolution is rechecked before an outbound call. Response body/model-count/provider-metadata size is bounded/sanitized.

## Agent Management UI refinement delivered in same runtime

Owner-requested visual/organizational changes are live:

- `Create agent` and `New session` use the same secondary control family as `Refresh`;
- agent list is grouped into `External / MCP agents` and `Internal / provider-backed agents`;
- agent cards expose `Agent name`, `Origin`, and `Model` fields;
- internal agents without assignment show `Not assigned`;
- externally hosted runtime models show `Client-managed` rather than guessed model identity;
- Provider Registry appears in the same Owner-only AI control-plane page.

## Verified runtime output

Deployment verifier reported:

`F7.2D3 provider_registry_runtime=pass credential_write_only=pass db_plaintext_secret=absent enable_gate=pass model_normalization=pass`

Public unauthenticated Provider Registry access returned 401. Existing Agent Management, User Management, MCP OAuth metadata, and unauthenticated `/mcp`=401 boundaries remained green.

## Preserved boundaries

- Google Sheets remains operationally authoritative.
- PostgreSQL remains non-canonical.
- F6B remains test-only.
- No live workbook import occurred.
- No production inventory write occurred.
- No AI inventory write became authorized.
- Provider/model configuration does not expand agent authority.

## Next authorized slice

**F7.2D4 — internal model assignment/fallback/runtime identity.**

The next slice should assign enabled provider/model resources to named internal agents, preserve stable agent identity and authority, support ordered fallbacks/capability validation, inject canonical self-identity for real invocation, and prove a narrow real inference only after the Owner configures a provider credential through the Web UI.

The existing ChatGPT MCP connection remains an external client/runtime. Do not silently invent or bind its named AI-agent identity; any such binding must be explicit and Owner-controlled.