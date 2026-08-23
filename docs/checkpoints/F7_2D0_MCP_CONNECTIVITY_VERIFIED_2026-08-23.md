# F7.2D0 — MCP Connectivity Verified — 2026-08-23

## Status

**VERIFIED COMPLETE** for the external ChatGPT read-access proof.

Medicine Store Assistant now has a live custom remote MCP path from ChatGPT Developer Mode to the MSA backend.

## Verified runtime

- Production source SHA: `611918572717058882849ede7a4cc2a39dd2e3ac`
- Deployment workflow run: `32618376291`
- Deployment status issue #26: `status=success`
- Alembic migration: `0009_recovery_token_cleanup -> 0010_mcp_oauth`
- Public MCP resource URL: `https://inventory.drthorne.uk/mcp`
- OAuth issuer: `https://inventory.drthorne.uk/oauth`
- OAuth authorization-code + PKCE S256: deployed
- Dynamic client registration: deployed
- Rotating refresh-token flow with `offline_access`: deployed
- OAuth token material stored digest-only at rest
- Public OAuth metadata: verified
- Public MCP protected-resource metadata: verified
- Anonymous MCP request: verified `401`

## ChatGPT connection proof

The Owner connected the custom MSA MCP app through ChatGPT Developer Mode using OAuth.

A fresh ChatGPT chat with the MSA app selected successfully executed the read-only identity/system-status check through the custom MCP connection.

Observed connected-client truth:

- MSA service: `AVAILABLE`
- runtime: external MCP client
- granted transport/authority scopes: `mcp:connect`, `mcp:read`, `offline_access`
- read capability: enabled
- propose capability: disabled
- write capability: disabled
- control capability: disabled
- environment: `foundation`
- build SHA: `611918572717058882849ede7a4cc2a39dd2e3ac`
- `database_canonical=false`
- `migration_baseline_accepted=false`
- F6B remains test-only
- production inventory writes remain disabled
- control-plane writes remain disabled

This proves the complete path:

`ChatGPT Developer Mode -> OAuth -> custom MSA MCP -> typed MSA backend -> deterministic read services`

## Architectural consequence

Custom MCP is now the primary ChatGPT/MSA external-access path.

The optional Custom GPT Action proof is no longer required for basic ChatGPT access. It remains a secondary/fallback path only if a standalone Custom GPT product surface is later needed.

The MCP server remains **full-schema / policy-gated**. Discoverable future proposal/write/control-plane tools do not grant execution authority. The current OAuth grant is read-only.

Future capability changes should be performed by server-side MSA grants/policy. The MCP connector should not need to be rebuilt or re-authorized merely to expand an already-approved capability scope.

## Security boundary preserved

- no raw SQL tool
- no database credential exposure
- no SSH/filesystem shell tool
- no plaintext provider/API secret exposure
- no generic arbitrary HTTP proxy
- no production inventory mutation
- no canonical PostgreSQL promotion
- no live workbook import

## Next implementation order

1. F7.2D2 — AI Agent / external-client principal control plane
2. F7.2D3 — Provider Registry + model catalog
3. F7.2D4 — model assignment/fallback policy
4. optional F7.2D1 Custom GPT Action only if separately useful
5. F7.3 actor-aware Audit / Operation Ledger
