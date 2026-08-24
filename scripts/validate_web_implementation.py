from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(message)


agents = read("AGENTS.md")
standard = read("docs/design/WEB_IMPLEMENTATION_STANDARD.md")
ownership = read("docs/design/WEB_SURFACE_OWNERSHIP.md")
main = read("backend/app/main.py")
base_review = read("backend/app/dashboard_assets/dashboard_multi_agent_review.js")
live_review = read("backend/app/dashboard_assets/dashboard_multi_agent_live_export.js")

require("WEB_IMPLEMENTATION_STANDARD.md" in agents, "AGENTS.md must reference WEB_IMPLEMENTATION_STANDARD.md")
require("WEB_SURFACE_OWNERSHIP.md" in agents, "AGENTS.md must reference WEB_SURFACE_OWNERSHIP.md")
require("One interactive DOM subtree" in agents, "AGENTS.md must enforce single interactive renderer ownership")
require("fresh-load, same-tab, refresh, and reopen" in agents, "AGENTS.md must require lifecycle acceptance")
require("Interaction tests, not presence tests" in standard, "Web standard must require behavior-level tests")
require("Multi-Agent — active Review chat" in ownership, "Surface ownership registry must include Multi-Agent active Review chat")

# Asset identity must follow source content, not manually remembered release tags.
require("asset_bundle_version" in main, "Dashboard entrypoint must use content-derived asset identity")
for legacy in ("f72d48-review-ui-2", "f72d48-live-export-3", "f72d47b-attachments-1"):
    require(legacy not in main, f"stale manual Dashboard asset marker remains: {legacy}")

# Dynamic Review actions use one stable delegated owner. Direct binding on replaceable feedback buttons is banned.
require("event.target.id==='reviewReturnRevision'" in base_review, "Review feedback action must be delegated from stable host")
require("querySelector('#reviewReturnRevision')?.addEventListener" not in base_review, "Replaceable Review feedback button must not also bind a direct click listener")

# When both Review scripts are loaded, base detail rendering delegates to the one active chat renderer.
require("window.MSAReviewChatRenderer?.render" in base_review, "Base Review UI must delegate active chat rendering to authoritative renderer")
require("window.MSAReviewChatRenderer={render:renderLive" in live_review, "Live Review module must expose the authoritative chat renderer bridge")

# MutationObserver remains a known transitional mechanism; require RAF coalescing and idempotent scheduling while it exists.
if "new MutationObserver" in live_review:
    require("requestAnimationFrame(reconcileDom)" in live_review, "Review MutationObserver work must be requestAnimationFrame-coalesced")
    require("if(reconcileFrame!==null)return" in live_review, "Review MutationObserver scheduling must be idempotent per frame")

print("web_implementation_reliability=pass")
