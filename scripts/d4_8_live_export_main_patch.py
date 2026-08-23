from pathlib import Path

path = Path('backend/app/main.py')
text = path.read_text()

def replace_once(old: str, new: str, label: str) -> None:
    global text
    count = text.count(old)
    if count != 1:
        raise SystemExit(f'{label}: expected one anchor, found {count}')
    text = text.replace(old, new, 1)

replace_once(
    'MULTI_AGENT_REVIEW_ASSET_VERSION = "f72d48-review-ui-2"\n',
    'MULTI_AGENT_REVIEW_ASSET_VERSION = "f72d48-review-ui-2"\nMULTI_AGENT_LIVE_EXPORT_ASSET_VERSION = "f72d48-live-export-1"\n',
    'asset constant',
)
replace_once(
    "        f'<link rel=\"stylesheet\" href=\"/dashboard/assets/dashboard_multi_agent_review.css?v={MULTI_AGENT_REVIEW_ASSET_VERSION}\">\\n'\n",
    "        f'<link rel=\"stylesheet\" href=\"/dashboard/assets/dashboard_multi_agent_review.css?v={MULTI_AGENT_REVIEW_ASSET_VERSION}\">\\n'\n        f'<link rel=\"stylesheet\" href=\"/dashboard/assets/dashboard_multi_agent_live_export.css?v={MULTI_AGENT_LIVE_EXPORT_ASSET_VERSION}\">\\n'\n",
    'review css loader',
)
replace_once(
    "        f'<script src=\"/dashboard/assets/dashboard_multi_agent_review.js?v={MULTI_AGENT_REVIEW_ASSET_VERSION}\" defer></script>\\n'\n",
    "        f'<script src=\"/dashboard/assets/dashboard_multi_agent_review.js?v={MULTI_AGENT_REVIEW_ASSET_VERSION}\" defer></script>\\n'\n        f'<script src=\"/dashboard/assets/dashboard_multi_agent_live_export.js?v={MULTI_AGENT_LIVE_EXPORT_ASSET_VERSION}\" defer></script>\\n'\n",
    'review js loader',
)
replace_once(
    '''@app.get("/dashboard/assets/dashboard_multi_agent_review.css", include_in_schema=False)\ndef multi_agent_review_css() -> FileResponse:\n    return _asset_file("dashboard_multi_agent_review.css", "text/css")\n\n\n''',
    '''@app.get("/dashboard/assets/dashboard_multi_agent_review.css", include_in_schema=False)\ndef multi_agent_review_css() -> FileResponse:\n    return _asset_file("dashboard_multi_agent_review.css", "text/css")\n\n\n@app.get("/dashboard/assets/dashboard_multi_agent_live_export.css", include_in_schema=False)\ndef multi_agent_live_export_css() -> FileResponse:\n    return _asset_file("dashboard_multi_agent_live_export.css", "text/css")\n\n\n''',
    'review css route',
)
replace_once(
    '''@app.get("/dashboard/assets/dashboard_multi_agent_review.js", include_in_schema=False)\ndef multi_agent_review_js() -> FileResponse:\n    return _asset_file("dashboard_multi_agent_review.js", "text/javascript")\n\n\n''',
    '''@app.get("/dashboard/assets/dashboard_multi_agent_review.js", include_in_schema=False)\ndef multi_agent_review_js() -> FileResponse:\n    return _asset_file("dashboard_multi_agent_review.js", "text/javascript")\n\n\n@app.get("/dashboard/assets/dashboard_multi_agent_live_export.js", include_in_schema=False)\ndef multi_agent_live_export_js() -> FileResponse:\n    return _asset_file("dashboard_multi_agent_live_export.js", "text/javascript")\n\n\n''',
    'review js route',
)
path.write_text(text)
trigger = Path('docs/checkpoints/d4-8-live-export-trigger.txt')
if trigger.exists():
    trigger.unlink()
print('d4_8_live_export_main_patch=pass')
