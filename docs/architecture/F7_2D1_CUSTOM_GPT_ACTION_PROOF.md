# F7.2D1 — Custom GPT Action Read-Only Connectivity Proof

Status: **FIRST IMPLEMENTATION STEP OF F7.2D**

## Goal

Prove as early as possible that a Custom GPT can securely reach the public Medicine Store Assistant backend through a GPT Action and receive real, authorized MSA data.

This is a connectivity/authority proof, not an AI write slice and not direct database access.

## Architecture

`Custom GPT -> HTTPS Action -> inventory.drthorne.uk -> MSA typed API -> scoped external-client credential -> capability check -> read-only service -> response`

The Custom GPT must never receive PostgreSQL credentials, Google Sheet credentials, VPS shell access, or a generic SQL endpoint.

## Why this comes first

The project intends to use Custom GPT as one durable external access path for ChatGPT/IANEO-style interaction with MSA. If GPT Actions cannot reliably authenticate to or call the deployed MSA API in the real product environment, that constraint should be discovered before significant Agent Management/provider work is built around the assumption that the path works.

## Current OpenAI Action assumptions

At implementation time, re-check current OpenAI documentation before configuring the GPT.

As of the architecture update, Custom GPT Actions support:

- external HTTPS APIs;
- OpenAPI JSON/YAML schemas;
- API-key authentication including Bearer/custom-header forms;
- OAuth for account-based user authorization;
- Preview testing in the GPT editor.

For the first single-Owner proof, prefer a scoped revocable API/service credential. Do not implement OAuth unless the proof or current product requirements require per-human delegated identity.

## Minimal server contract

Create a dedicated external-action API namespace rather than exposing arbitrary internal endpoints.

Suggested first contract:

- `GET /actions/v1/whoami`
  - returns external client/agent identity, active state, and granted read capability names;
  - reveals no secret/token material.

- `GET /actions/v1/inventory/summary`
  - returns an existing bounded read-only summary from the current test/shadow dataset;
  - must preserve `database_canonical=false` and `migration_baseline_accepted=false` metadata.

- optional bounded lookup such as `GET /actions/v1/inventory/search?q=...&limit=...`
  - only if necessary to prove parameterized tool invocation;
  - no mutation.

Do not expose raw SQL, arbitrary table selection, generic database query execution, or unrestricted internal admin routes.

## External client identity

The proof should register one named external client/agent, for example a Custom GPT Action client, with:

- stable identifier;
- runtime type `EXTERNAL_ACTION_CLIENT`;
- `ACTIVE`/`REVOKED` state;
- credential digest or equivalent safe verifier material;
- explicit read capability allowlist;
- created/revoked timestamps/provenance.

Plaintext service credential is shown/provisioned only at issuance and must not be persisted in ordinary database fields, Git, logs, docs, or browser storage.

## Authentication

First proof preference:

`Authorization: Bearer <scoped-service-token>`

Requirements:

- high-entropy revocable token;
- server stores only keyed digest/verifier material;
- token scope is limited to this external client/agent;
- disabling/revoking the client immediately blocks future requests;
- invalid/missing token returns 401;
- valid token without a requested capability returns 403.

## OpenAPI schema

Provide the smallest valid schema needed for the proof.

Requirements:

- server URL uses `https://inventory.drthorne.uk`;
- stable descriptive `operationId` values;
- clear natural-language descriptions so ChatGPT selects the intended action;
- bounded parameters/response shapes;
- no write endpoints;
- no secret-bearing schema examples;
- schema should be exportable/copyable for Custom GPT configuration.

A public schema endpoint may be added later if useful, but the first proof may use a checked-in schema file copied into the GPT editor.

## Acceptance test

The slice passes only when all of the following are proven end-to-end:

1. MSA external Action client/credential is created without exposing secrets in Git/logs.
2. Local/API-level test with the credential succeeds.
3. Missing/invalid credential returns 401.
4. A deliberately ungranted operation returns 403.
5. OpenAPI schema validates in the Custom GPT editor.
6. GPT Preview can invoke `whoami` successfully.
7. GPT Preview can invoke a real read-only inventory summary and receive current MSA backend data.
8. The response explicitly preserves test/non-canonical boundaries where relevant.
9. Revoking the Action client causes a subsequent GPT Action request to fail.
10. Re-enabling/reissuing a new credential restores only the intended read access.
11. No inventory mutation, workbook import, DB canonical promotion, or provider/model call occurs as part of the proof.

## Failure decision

If the GPT editor or runtime cannot execute the Action because of current OpenAI product/workspace/domain/authentication restrictions, record the exact failure and stop treating Custom GPT Actions as a proven primary path.

Do not weaken MSA security, expose DB credentials, or open unauthenticated data merely to make the proof pass.

The architecture can still continue through internal provider-backed agents and other typed clients, but the limitation must be documented early.

## Non-scope

- provider API keys;
- OpenAI/Gemini/OpenRouter/NanoGPT model calls;
- Provider Registry UI;
- internal AI Chat;
- OAuth unless required to prove connectivity;
- production inventory writes;
- AI writes;
- Telegram/Flutter integration;
- F7.3 full operational Audit;
- PostgreSQL canonical promotion.

## Next after success

Proceed to F7.2D2 AI-agent principal/control-plane foundation, then Provider Registry/model catalog and internal model assignment.
