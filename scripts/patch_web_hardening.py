from pathlib import Path


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"{label}: expected 1 match, found {count}")
    return text.replace(old, new, 1)

# 1) Content-derived asset identity in main.py.
main_path = Path('backend/app/main.py')
main = main_path.read_text(encoding='utf-8')
main = replace_once(
    main,
    'from app.dashboard import ASSET_DIR, DASHBOARD_CSP, router as dashboard_router\n',
    'from app.dashboard import ASSET_DIR, DASHBOARD_CSP, router as dashboard_router\nfrom app.dashboard_asset_version import asset_bundle_version\n',
    'asset helper import',
)
old_constants = '''SAVED_MODEL_ASSET_VERSION = "f72d31-2"\nAGENT_ASSIGNMENT_GUARD_ASSET_VERSION = "f72d4-preflight-1"\nNATIVE_AGENT_TEST_ASSET_VERSION = "f72d4d-native-test-1"\nAI_WORKSPACE_ACCESS_ASSET_VERSION = "f72d4-access-1"\nAI_WORKSPACE_ASSET_VERSION = "f72d47b-attachments-1"\nMULTI_AGENT_REVIEW_ASSET_VERSION = "f72d48-review-ui-2"\nMULTI_AGENT_LIVE_EXPORT_ASSET_VERSION = "f72d48-live-export-3"\nAGENT_POLISH_ASSET_VERSION = "f72d31-agentui-1"\nMCP_BINDING_ASSET_VERSION = "f72d4a-mcpbind-1"\nAUDIT_ASSET_VERSION = "f73a-mcpaudit-1"\n'''
new_constants = '''SAVED_MODEL_ASSET_VERSION = asset_bundle_version(ASSET_DIR, "dashboard_saved_models.js", "dashboard_saved_models.css")\nAGENT_ASSIGNMENT_GUARD_ASSET_VERSION = asset_bundle_version(ASSET_DIR, "dashboard_agent_assignment_guard.js")\nNATIVE_AGENT_TEST_ASSET_VERSION = asset_bundle_version(ASSET_DIR, "dashboard_native_agent_test.js")\nAI_WORKSPACE_ACCESS_ASSET_VERSION = asset_bundle_version(ASSET_DIR, "dashboard_ai_workspace_access.js")\nAI_WORKSPACE_ASSET_VERSION = asset_bundle_version(ASSET_DIR, "dashboard_ai_workspace.js", "dashboard_ai_workspace.css")\nMULTI_AGENT_REVIEW_ASSET_VERSION = asset_bundle_version(ASSET_DIR, "dashboard_multi_agent_review.js", "dashboard_multi_agent_review.css")\nMULTI_AGENT_LIVE_EXPORT_ASSET_VERSION = asset_bundle_version(ASSET_DIR, "dashboard_multi_agent_live_export.js", "dashboard_multi_agent_live_export.css")\nAGENT_POLISH_ASSET_VERSION = asset_bundle_version(ASSET_DIR, "dashboard_agent_polish.css")\nMCP_BINDING_ASSET_VERSION = asset_bundle_version(ASSET_DIR, "dashboard_mcp_binding.js", "dashboard_mcp_binding.css")\nAUDIT_ASSET_VERSION = asset_bundle_version(ASSET_DIR, "dashboard_audit.js", "dashboard_audit.css")\n'''
main = replace_once(main, old_constants, new_constants, 'asset version constants')
main_path.write_text(main, encoding='utf-8')

# 2) Make the live Review renderer the authoritative active-chat renderer when loaded.
base_path = Path('backend/app/dashboard_assets/dashboard_multi_agent_review.js')
base = base_path.read_text(encoding='utf-8')
base = replace_once(
    base,
    '  function renderWorkDetail(item){\n    const detail=host.querySelector(\'#reviewWorkDetail\');\n',
    "  function renderWorkDetail(item){\n    if(window.MSAReviewChatRenderer?.render){window.MSAReviewChatRenderer.render(item);return}\n    const detail=host.querySelector('#reviewWorkDetail');\n",
    'authoritative renderer delegation',
)
base = replace_once(
    base,
    "    host.querySelector('#reviewReturnRevision')?.addEventListener('click',returnForRevision);\n",
    '',
    'duplicate direct feedback binding',
)
base_path.write_text(base, encoding='utf-8')

live_path = Path('backend/app/dashboard_assets/dashboard_multi_agent_live_export.js')
live = live_path.read_text(encoding='utf-8')
anchor = '  function signature(item){return[item.status,(item.artifacts||[]).length,(item.reviews||[]).length,(item.events||[]).length].join(\':\')}\n'
expose = "  window.MSAReviewChatRenderer={render:renderLive,enter:enterReviewChatView,exit:exitReviewChatView};\n\n"
if expose not in live:
    live = replace_once(live, anchor, expose + anchor, 'renderer bridge export')
live_path.write_text(live, encoding='utf-8')

print('web_hardening_patch=pass')
