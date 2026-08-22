# F7.2D1 — Custom GPT Action Read-Only Connectivity Proof

Status: **OPTIONAL SECONDARY EXTERNAL PATH — DEFERRED UNTIL AFTER MCP PROOF**

## Goal

Provide a fallback/secondary proof that a standalone Custom GPT can securely reach the public Medicine Store Assistant backend through a GPT Action and receive real, authorized MSA data.

This is a connectivity/authority proof, not direct database access and not an AI write slice.

## Current priority

F7.2D now tries the custom MCP path first through `F7_2D0_CUSTOM_MCP_CONNECTIVITY_PROOF.md`.

If MCP proves reliable and provides the ChatGPT access/freedom needed by the project, this Custom GPT Action path may remain deferred or may never be required for the primary workflow.

Implement this proof only when:

- MCP is blocked by a real platform/product limitation; or
- a standalone packaged Custom GPT is specifically desired; or
- Action-specific distribution/authentication provides a concrete benefit not met by MCP.

## Architecture

`Custom GPT -> HTTPS Action -> inventory.drthorne.uk -> MSA typed API -> scoped external-client credential -> capability check -> read-only service -> response`

The Custom GPT must never receive PostgreSQL credentials, Google Sheet credentials, VPS shell access, or a generic SQL endpoint.

## OpenAI Action assumptions

At implementation time, re-check current OpenAI documentation before configuring the GPT.

The Action proof should use the current supported external HTTPS/OpenAPI/authentication flow. For a single-Owner server-to-server proof, prefer a scoped revocable API/service credential where currently supported. Use OAuth only when per-human delegated identity is actually required.

## Minimal server contract

Use a dedicated external-action API namespace rather than exposing arbitrary internal endpoints.

Suggested first contract:

- `GET /actions/v1/whoami`
  - returns external client/agent identity, active state, and granted read capability names;
  - reveals no secret/token material.

- `GET /actions/v1/inventory/summary`
  - returns an existing bounded read-only summary from the current test/shadow dataset;
  - preserves `database_canonical=false` and `migration_baseline_accepted=false` metadata.

- optional bounded lookup such as `GET /actions/v1/inventory/search?q=...&limit=...`
  - only if necessary to prove parameterized tool invocation;
  - no mutation.

Do not expose raw SQL, arbitrary table selection, generic database query execution, or unrestricted internal admin routes.

## External client identity

Register one named external Action client with:

- stable identifier;
- runtime type `EXTERNAL_ACTION_CLIENT`;
- `ACTIVE` / `REVOKED` state;
- credential digest or equivalent safe verifier material;
- explicit read capability allowlist;
- created/revoked timestamps/provenance.

Plaintext service credential is shown/provisioned only at issuance and must not be persisted in ordinary database fields, Git, logs, docs, or browser storage.

## Authentication

Requirements:

- high-entropy revocable credential;
- server stores only keyed digest/verifier material or a secret reference;
- token scope is limited to the registered external client;
- disabling/revoking the client immediately blocks future requests;
- invalid/missing credential returns an authentication denial;
- valid credential without a requested capability returns an authorization denial.

## OpenAPI schema

Provide the smallest valid schema needed for the proof.

Requirements:

- server URL uses the public MSA HTTPS domain;
- stable descriptive `operationId` values;
- clear natural-language descriptions;
- bounded parameters/response shapes;
- no write endpoints;
- no secret-bearing schema examples.

## Acceptance test

The optional slice passes only when all of the following are proven end-to-end:

1. MSA external Action client/credential is created without exposing secrets in Git/logs.
2. Local/API-level test succeeds.
3. Missing/invalid credential is denied.
4. A deliberately ungranted operation is denied.
5. OpenAPI schema validates in the Custom GPT editor.
6. GPT Preview can invoke `whoami` successfully.
7. GPT Preview can invoke a real read-only inventory summary and receive current MSA backend data.
8. The response explicitly preserves test/non-canonical boundaries where relevant.
9. Revoking the Action client causes a subsequent GPT Action request to fail.
10. No inventory mutation, workbook import, DB canonical promotion, or provider/model call occurs.

## Failure decision

If the GPT editor/runtime cannot execute the Action because of current product/workspace/domain/authentication restrictions, record the exact failure. Do not weaken MSA security or expose DB credentials to make the Action pass.

## Non-scope

- custom MCP implementation, which is owned by F7.2D0;
- provider API keys;
- OpenAI/Gemini/OpenRouter/NanoGPT model calls;
- Provider Registry UI;
- internal AI Chat;
- production inventory writes;
- AI writes;
- Telegram/Flutter integration;
- F7.3 full operational Audit;
- PostgreSQL canonical promotion.

## Next after success

Return to the normal F7.2D sequence: AI-agent/external-client control-plane foundation, Provider Registry/model catalog, and internal model assignment.
