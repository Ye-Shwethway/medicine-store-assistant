from pathlib import Path

files = [
    'tests/web/inventory_view_engine_smoke.mjs',
    'tests/web/inventory_sorting_smoke.mjs',
    'tests/web/inventory_excel_export_smoke.mjs',
    'tests/web/inventory_date_format_smoke.mjs',
    'tests/web/inventory_sheet_selection_smoke.mjs',
    'tests/web/inventory_sheet_formatting_smoke.mjs',
]

for name in files:
    p = Path(name)
    s = p.read_text()
    if '/dashboard/api/inventory-view/saved-views' in s:
        continue
    candidates = [
        ("    if(url==='/dashboard/api/inventory-view/presets')", "    if(url==='/dashboard/api/inventory-view/saved-views')return response({items:[],database_canonical:false,migration_baseline_accepted:false});\n    if(url==='/dashboard/api/inventory-view/presets')"),
        ("    if(requestPath.includes('/presets'))", "    if(requestPath.includes('/saved-views'))return json({items:[],database_canonical:false,migration_baseline_accepted:false});\n    if(requestPath.includes('/presets'))"),
        ("    if(requestPath.includes('/registry'))", "    if(requestPath.includes('/saved-views'))return json({items:[],database_canonical:false,migration_baseline_accepted:false});\n    if(requestPath.includes('/registry'))"),
    ]
    for old, new in candidates:
        if old in s:
            s = s.replace(old, new, 1)
            p.write_text(s)
            break
    else:
        raise SystemExit(f'No fetch anchor found for {name}')
