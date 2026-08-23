# Medicine Store Assistant — New Chat Bootstrap

Use this file for project-development continuity and reconciliation in a fresh chat.

## Canonical repository

`https://github.com/Ye-Shwethway/medicine-store-assistant`

## Mandatory reconciliation order

Before changing code/config/schema/runtime, read:

1. `AGENTS.md`
2. `NEW_CHAT_BOOTSTRAP.md`
3. `ROADMAP.md`
4. `IMPLEMENTATION_PLAN.md`
5. `docs/architecture/README.md`
6. `docs/architecture/F7_2D_AI_AGENT_MANAGEMENT.md`
7. `docs/architecture/F7_2D_EXECUTION_PATH_SEPARATION.md`
8. `docs/architecture/F7_2D4_AI_WORKSPACE_AND_ACCESS.md`
9. `docs/architecture/F7_2D2_AGENT_MANAGEMENT_AND_MULTI_AGENT_SESSIONS.md`
10. `docs/checkpoints/F7_2D4F_GROUNDED_NATIVE_READS_PLAN_2026-08-23.md`
11. `docs/checkpoints/F7_2D4G_CHAT_UX_LIFECYCLE_PLAN_2026-08-23.md`
12. `docs/checkpoints/F7_2D47_FALLBACK_MANAGEMENT_PLAN_2026-08-23.md`
13. `docs/checkpoints/F7_2D47A_NATIVE_TOOL_CALLING_PLAN_2026-08-23.md`
14. `docs/checkpoints/F7_2D47B_RESPONSE_AND_ATTACHMENTS_PLAN_2026-08-24.md`
15. current runtime/deployment evidence, especially issue #26
16. `docs/design/UI_UX_PRO_MAX_INTEGRATION.md` and `docs/design/WEB_ASSET_RELEASE_INTEGRITY.md` for Web work

Treat newer verified repository/runtime evidence as authoritative over remembered chat context.

## Current canonicality boundary

- Google Sheet/source documents remain operationally authoritative.
- PostgreSQL is deployed but **not canonical**.
- F6B is test-only and not an accepted migration baseline.
- `database_canonical=false`.
- `migration_baseline_accepted=false`.
- No production inventory write, AI inventory write, transfer, Calculator deduction, Telegram/Flutter stock mutation, Sheet mirror conversion, automatic OCR/vision commit, or DB canonical promotion is authorized.

## Delivery policy

`branch -> PR -> main -> automatic VPS deploy for runtime changes -> issue #26 evidence -> continuity-doc refresh`

## Durable execution-path invariant

External MCP:

`ChatGPT model -> MCP action -> MCP authority gate -> typed MSA backend operation -> result`

Native internal agent:

`MSA Web / future Telegram / Flutter / automation -> INTERNAL_MODEL runtime -> assigned provider/model -> internal typed-tool adapter -> typed MSA backend operation -> response`

They are peer paths. Internal agents do not depend on public MCP for ordinary work. Direct authorized MCP actions do not require an internal-agent hop. `msa_agent_invoke` is optional delegation/orchestration only.

## Verified internal-agent truth

Production/manual accepted:

- named AI Agent Management and persisted authority/policy;
- Provider Registry + tested Owner-saved models;
- backend PRIMARY + ordered FALLBACK chain for `INTERNAL_MODEL` agents;
- Owner fallback configuration UI exists; live failover proof still pending;
- server rejection of model assignment for non-internal agents;
- MCP-independent native provider inference;
- provider/model/fallback/latency attempt provenance;
- backend-first AI Workspace access policy;
- durable top-level AI Workspace Chat;
- bounded grounded native reads over F6B test/shadow evidence;
- long response handling, deterministic USER -> ASSISTANT ordering, clean display, Copy/select, richer conversation cards, and owner-scoped conversation deletion;
- D4.7A deterministic fast path + model-driven native tool calling; contextual follow-up manual acceptance passed with MiniMax M3;
- D4.7B attachment transport/persistence/manual behavior accepted: photo/file upload, remove-before-send, persisted message binding, and explicit no-vision/OCR claim when bytes are not supplied to the model;
- external MCP direct read/audit remains independent;
- production inventory writes remain disabled.

## AI Workspace architecture — LOCKED

### AI Agent Management — Owner-only control plane

Contains agent lifecycle/policy, provider/model/fallback assignments, reusable multi-agent session definitions, and global non-owner AI Workspace access setting.

Owner-only requires backend authorization plus UI restriction.

### AI Workspace — work plane

- `Chat` — one selected internal agent; Owner + authorized users.
- `Multi-Agent` — GROUP/COMPARE/REVIEW/DEBATE execution; Owner-only for this phase and not yet wired.
- Both composer contracts use the same photo/file attachment architecture. Single-agent upload is the first implementation; Multi-Agent reuses it when D4.8 execution lands.

## Access + authority

Owner always has AI Workspace access. Global OFF hard-blocks all non-owner Chat before provider calls. Per-user entitlement foundation is `INHERIT | ALLOW | BLOCK`.

Native tool authority intersects system gate, authenticated human authority, selected-agent capability/ceiling, location scope, operation class, and confirmation policy. Never union privileges. Provider/model assignment never grants authority.

Native store-tool execution is currently backend-restricted to Owner sessions plus selected-agent READ authority. Non-owner Chat is reasoning-only for store tools until explicit human/location tool authority is implemented.

Uploaded attachment evidence is ownership-scoped. Attachment byte/preview endpoints must independently enforce authenticated AI Workspace access plus conversation/attachment ownership. An attachment never grants tool/write authority.

## D4.7A native tool calling — VERIFIED

Canonical checkpoint: `docs/checkpoints/F7_2D47A_NATIVE_TOOL_CALLING_PLAN_2026-08-23.md`.

Accepted hybrid behavior:

1. Explicit supported request -> deterministic backend fast-path prefetch -> grounded model answer.
2. If no fast-path evidence exists and the assigned tool-capable OpenAI-compatible model supports tools -> expose all currently authorized native read tools -> model may request tools -> backend allowlist/authority validation -> typed result -> final answer.
3. Tool loop is bounded to four rounds.
4. Unsupported providers/models fall back to grounded reasoning and must not claim tool execution.
5. Public MCP is not used.

Current native tool registry:

- `inventory_summary`
- `new_unmapped_rows`
- `review_reasons`

The public MCP schema has 106 actions, but those are not automatically internal-agent tools. Only implemented native typed adapters that are backend-authorized are exposed.

## Current work — D4.7B UX completion

Canonical checkpoint: `docs/checkpoints/F7_2D47B_RESPONSE_AND_ATTACHMENTS_PLAN_2026-08-24.md`.

Current implementation/acceptance target:

- native read tools expose a human-friendly presentation layer while retaining raw evidence/provenance;
- deterministic spreadsheet serial-date conversion may be shown as a derived value while preserving the raw serial;
- agents answer the user's question first and do not lead with UUIDs, raw JSON keys, batch/source IDs, or repeated canonicality boilerplate unless requested/needed;
- facts, deterministic derived values, and inference must remain distinct;
- identifying one blocker does not prove a state transition; revalidation/reclassification must run and pass;
- single-agent Chat has Photo and File buttons, selected attachment remove-before-send, bounded persistence, and message binding;
- max 4 pending attachments, max 8 MB each, MIME allowlist, authenticated conversation ownership;
- bound attachment metadata survives conversation reload; conversation deletion cascades attachments;
- JPEG/PNG/WebP should render as small thumbnails before send and as visible image evidence inside bound USER chat messages; HEIC/HEIF may remain metadata-only when browser preview is unreliable;
- image preview/content serving is owner/conversation scoped and is display-only: it does not mean provider vision/OCR has received or processed the bytes;
- conversation cards now target the latest USER/ASSISTANT message preview with `You:` or agent-name prefix plus human-friendly last-interaction time, rather than the first USER message;
- attachment bytes are NOT yet supplied to provider models, OCR, or vision processing; model receives metadata only and must not claim inspection;
- Multi-Agent UI reserves the same attachment contract but remains disabled until D4.8 execution is wired.

Future typed workflows using this attachment evidence include issue-paper photo batch intake, Daily Usage extraction, and stock-transfer evidence/proposals. Extraction must produce a draft/review stage before any controlled write.

## Next authorized order

1. Finish/deploy D4.7B image-preview + latest-message-card refinement and manually verify it.
2. Run D4.7 live PRIMARY -> FALLBACK proof when a stable secondary model/provider is available.
3. D4.8 Owner-only Multi-Agent execution using the shared attachment contract.
4. Per-user Chat entitlement/allowed-agent UI plus human/location tool-authority intersection before staff tool rollout.
5. Expand native typed tools and vision/OCR attachment processors only through bounded typed workflows.
6. D4.9 optional MCP -> native-agent delegation.

## D4.7B manual acceptance

In Owner AI Workspace Chat:

1. attach JPEG/PNG/WebP and confirm a small preview is visible before Send;
2. send/reload and confirm the image remains visibly rendered inside the USER message;
3. confirm preview/content access is unavailable outside the owning authenticated conversation;
4. send another USER/ASSISTANT turn and confirm the conversation card preview updates to the newest message, with `You:` or agent prefix and human-friendly timestamp;
5. ask the agent about image contents and confirm it still explicitly says vision/OCR content processing is not wired yet rather than pretending it inspected the file;
6. confirm no inventory write occurs.

## Survival proof

`MSA Web -> selected INTERNAL_MODEL agent -> assigned provider/model -> authorized typed MSA read -> response + provenance`

This proof is already live and must remain independent of public MCP.
