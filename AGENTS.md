# Repository Rules

Treat `skills/medicine-store-assistant/` as the canonical Git-backed plugin skill source.

- Preserve the skill name `medicine-store-assistant` and invocation alias `$msa`.
- **Do not move, rename, repurpose, or bury `skills/medicine-store-assistant/` when adding backend/runtime code.** The published Git-backed skill must remain independently installable from this repository.
- Keep `SKILL.md` concise: global rules and links only. Put workflow detail in its `references/` directory.
- Preserve exact source-document truth, expiry-separated lots, and the existing Excel/Google Sheets compatibility contract.
- Preserve the useful `$msa` evidence workflow when moving operations into the database architecture: inspect evidence, reconcile against current truth, classify `SAFE` / `REVIEW` / `CONFLICT` / `NEW_UNMAPPED`, execute only Owner-authorized workflow classes, surface ambiguity, commit through typed operations, read back affected state, audit the operation, and never claim success before verification.
- Owner preauthorization may allow low-friction SAFE routine execution after the corresponding write slice is authorized; REVIEW/CONFLICT/NEW_UNMAPPED and material/high-risk cases remain review boundaries.
- Treat `docs/architecture/` as the canonical design contract for the planned database/API system. Keep architecture, data model, integrity, monthly lifecycle, client API, mirror, migration, actor-audit, agent-management, location, and intelligence documents mutually consistent.
- **Use `NEW_CHAT_BOOTSTRAP.md` + `ROADMAP.md` as mandatory project-continuity documents.** After every significant architecture decision, implementation slice, deployment change, migration/reconciliation result, or change to the next authorized work, update both files so a fresh chat can recover the current checkpoint without remembered conversation context.
- `NORMAL_CHAT_BOOTSTRAP.md` has a different role: it teaches an ordinary chat how to load and operate the published `$msa` skill. Do not turn it into the project-development continuity file.
- **Docs first, implementation second.** Do not create production database migrations, backend write paths, Custom GPT write Actions, Telegram write behavior, or database-canonical promotion until the relevant architecture is explicitly reviewed/authorized.
- Future implementation belongs in sibling areas such as `backend/`, `integrations/`, and `deploy/`; it must not replace the skill structure.
- PostgreSQL/VPS implementation must use typed domain operations and deterministic integrity controls. Never expose arbitrary SQL or database credentials to GPT, AI agents, Telegram, Flutter, or Google Sheets clients.
- Canonical human accounts and AI/service principals are separate identity types. AI agents use Owner-managed capability/delegation/location policy rather than human roles copied onto service accounts.
- **`AI Agent Management` and global `Settings` are Owner-only control planes.** AI agents may never self-escalate, change their own grants, alter Owner/security controls, or modify global Settings.
- AI agents are not inherently Sub-Store-only. Later Main Store or Sub Store typed operations may be granted by Owner only after the corresponding controlled-write and canonicality boundaries are explicitly authorized.
- Shared AI Chat may be made available to Staff/Admin users, but effective authority must remain the intersection of human authority, agent capability scope, location scope, and operation policy.
- The current Google-Sheets-first workflow remains authoritative until the migration plan explicitly promotes the database after shadow validation.
- Never commit credentials, access tokens, service-account JSON, live spreadsheet IDs, inventory exports, audit exports, migration snapshots, operational photos, production database dumps, or other private operational data.
- Use runtime configuration or authorized live discovery for spreadsheet/database identity.
- Validate every change with `python scripts/validate_repository.py` when the validator is available in the execution environment.
- Bump `VERSION` and `.codex-plugin/plugin.json` together for release changes. Architecture documentation drafts alone do not automatically require a plugin release bump unless they change the published skill contract.
- Keep `.agents/plugins/marketplace.json` installable from the public Git repository.
- Update `NORMAL_CHAT_BOOTSTRAP.md` whenever the canonical skill path or startup contract changes.
- Do not add Telegram or autonomous write behavior until authentication, capability/location scope, dry-run/preview where appropriate, approval/policy, idempotency, audit, rollback/correction, and read-back design are explicit.
- Do not declare PostgreSQL the canonical source of truth merely because it is deployed. Canonical promotion requires the staged reconciliation and shadow-validation process in `docs/architecture/MIGRATION_AND_SHADOW_VALIDATION.md`.
- **For every Dashboard CSS/JS change, verify the full browser delivery chain.** Update the HTML entrypoint asset version/cache identity, ensure CI checks the intended current asset reference, wait for issue #26 deployment evidence, and do not call a UI slice verified merely because backend/API/standalone JS checks passed. Follow `docs/design/WEB_ASSET_RELEASE_INTEGRITY.md`.
- **Do not reuse a stale Dashboard asset version marker for changed content.** While manually versioned static assets are used, CSS/JS responses must remain no-store/no-cache and live HTML must reference the current release asset key.
- **Do not use Bamboo/Bamboo Claw as part of the normal MSA implementation, deployment, verification, or continuity workflow.** It may be used only if the owner explicitly asks for it again.
- **Do not require the owner to run Termux, SSH, tmux, shell commands, or manual GitHub Actions as part of normal implementation.** Prefer connected tools, repository automation, self-hosted runner automation, application-native setup/admin UI, and safe server-side workflows that require at most ordinary browser interaction from the owner.
- If a future runtime-secret or privileged VPS task cannot be completed through the normal automated path, design a durable product/admin mechanism first rather than falling back to repeated ad-hoc terminal instructions.
