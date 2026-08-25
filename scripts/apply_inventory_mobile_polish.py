from pathlib import Path


def replace_once(path: str, old: str, new: str) -> None:
    p = Path(path)
    text = p.read_text()
    if old not in text:
        raise SystemExit(f"expected snippet not found in {path}: {old[:100]!r}")
    p.write_text(text.replace(old, new, 1))


js = "backend/app/dashboard_assets/dashboard_inventory_views.js"
replace_once(
    js,
    "const dialog=document.createElement('section');dialog.setAttribute('role','dialog');",
    "const dialog=document.createElement('section');dialog.className='inventory-table-builder';dialog.setAttribute('role','dialog');",
)
replace_once(
    js,
    "    .inventory-saved-view-actions{display:inline-flex;align-items:center;gap:5px;padding:3px;border:1px solid color-mix(in srgb,var(--accent,#2f6fed) 16%,var(--border,#d9dde7));border-radius:9px;background:color-mix(in srgb,var(--accent,#2f6fed) 3%,var(--card,#fff))}.inventory-saved-view-actions button{min-height:36px;padding:6px 9px;font-size:.7rem}.inventory-saved-view-actions #inventorySaveView{font-weight:800}.inventory-saved-view-actions #inventoryDeleteView:not(:disabled){color:#a52d43}.inventory-view-toolbar option[data-custom-view]{font-weight:700}\n",
    "    .inventory-saved-view-actions{display:inline-flex;align-items:center;gap:5px;padding:3px;border:1px solid color-mix(in srgb,var(--accent,#2f6fed) 16%,var(--border,#d9dde7));border-radius:9px;background:color-mix(in srgb,var(--accent,#2f6fed) 3%,var(--card,#fff))}.inventory-saved-view-actions button{min-height:36px;padding:6px 9px;font-size:.7rem}.inventory-saved-view-actions #inventorySaveView{font-weight:800}.inventory-saved-view-actions #inventoryDeleteView:not(:disabled){color:#a52d43}.inventory-view-toolbar option[data-custom-view]{font-weight:700}\n    .inventory-table-builder button,.inventory-table-builder input,.inventory-table-builder select{font:inherit}.inventory-table-builder input,.inventory-table-builder select{box-sizing:border-box;width:100%;min-height:44px;padding:9px 11px;border:1px solid var(--border,#d9dde7);border-radius:10px;background:var(--card,#fff);color:inherit}.inventory-table-builder button{min-height:44px;padding:9px 14px;border:1px solid var(--border,#d9dde7);border-radius:10px;background:var(--card,#fff);color:inherit;font-weight:750;cursor:pointer}.inventory-table-builder [data-inventory-builder-save]{background:var(--accent,#2f6fed);border-color:var(--accent,#2f6fed);color:#fff}.inventory-table-builder [data-builder-close]{display:grid;place-items:center;width:44px;padding:0;flex:0 0 44px}.inventory-table-builder [data-builder-move]{display:grid;place-items:center;width:44px;min-width:44px;padding:0;font-size:1rem}.inventory-table-builder button:disabled{opacity:.42;cursor:not-allowed}\n",
)
replace_once(
    js,
    ".inventory-saved-view-actions{width:100%;display:grid;grid-template-columns:repeat(3,minmax(0,1fr))}",
    ".inventory-saved-view-actions{grid-column:1/-1;width:100%;display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:7px;padding:7px}.inventory-saved-view-actions button{min-height:44px;font-size:.74rem}.inventory-saved-view-actions #inventoryDeleteView{grid-column:1/-1}.inventory-table-builder-backdrop{padding:0!important;place-items:end center!important}.inventory-table-builder{width:100%!important;max-height:92dvh!important;padding:16px!important;border-radius:20px 20px 0 0!important}.inventory-table-builder>div:nth-of-type(2){grid-template-columns:1fr!important}.inventory-table-builder [data-inventory-builder-fields]{gap:10px!important}.inventory-table-builder [data-builder-field]{grid-template-columns:auto minmax(0,1fr) auto auto!important;gap:8px!important;align-items:start!important;padding:12px!important}.inventory-table-builder [data-builder-field]>div{grid-column:2/-1}.inventory-table-builder [data-builder-label]{grid-column:2/3!important}.inventory-table-builder [data-builder-move]{grid-row:2}.inventory-table-builder [data-builder-move=up]{grid-column:3}.inventory-table-builder [data-builder-move=down]{grid-column:4}",
)

export_js = "backend/app/dashboard_assets/dashboard_inventory_export.js"
replace_once(
    export_js,
    "    const params=new URLSearchParams({preset});\n",
    "    const params=new URLSearchParams({preset});\n    const displayName=(select?.selectedOptions?.[0]?.textContent||'Main Stock').replace(/^Custom\\s*·\\s*/,'').trim();\n    if(displayName)params.set('export_name',displayName);\n",
)

py = "backend/app/inventory_view_export.py"
replace_once(py, "import json\n", "import json\nimport re\n")
replace_once(
    py,
    "def _response_headers(filename: str) -> dict[str, str]:\n",
    "def _safe_export_stem(value: str | None, fallback: str) -> str:\n    source = (value or fallback).strip().lower()\n    stem = re.sub(r'[^a-z0-9]+', '-', source).strip('-')\n    return stem[:80] or 'inventory'\n\n\ndef _response_headers(filename: str) -> dict[str, str]:\n",
)
replace_once(
    py,
    "    column_labels: str | None = Query(default=None, max_length=MAX_COLUMN_LABELS_QUERY, description=\"Optional JSON object of presentation-only header labels keyed by selected registered field.\"),\n    q: str | None = None,\n",
    "    column_labels: str | None = Query(default=None, max_length=MAX_COLUMN_LABELS_QUERY, description=\"Optional JSON object of presentation-only header labels keyed by selected registered field.\"),\n    export_name: str | None = Query(default=None, max_length=120, description=\"Optional presentation-only export filename label.\"),\n    q: str | None = None,\n",
)
replace_once(
    py,
    "        headers=_response_headers(f\"msa-{view.view_id}.xlsx\"),\n",
    "        headers=_response_headers(f\"msa-{_safe_export_stem(export_name, view.name)}.xlsx\"),\n",
)
# second endpoint parameter
marker = "def inventory_view_export_csv(\n"
text = Path(py).read_text()
pos = text.index(marker)
head, tail = text[:pos], text[pos:]
old = "    column_labels: str | None = Query(default=None, max_length=MAX_COLUMN_LABELS_QUERY, description=\"Optional JSON object of presentation-only header labels keyed by selected registered field.\"),\n    q: str | None = None,\n"
if old not in tail:
    raise SystemExit("CSV parameter snippet not found")
tail = tail.replace(old, "    column_labels: str | None = Query(default=None, max_length=MAX_COLUMN_LABELS_QUERY, description=\"Optional JSON object of presentation-only header labels keyed by selected registered field.\"),\n    export_name: str | None = Query(default=None, max_length=120, description=\"Optional presentation-only export filename label.\"),\n    q: str | None = None,\n", 1)
tail = tail.replace('headers=_response_headers(f"msa-{view.view_id}.csv"),', 'headers=_response_headers(f"msa-{_safe_export_stem(export_name, view.name)}.csv"),', 1)
Path(py).write_text(head + tail)

verify = "backend/app/inventory_view_export_verify.py"
replace_once(verify, '        "column_labels": None,\n', '        "column_labels": None,\n        "export_name": None,\n')
replace_once(
    verify,
    "        custom_xlsx = export.inventory_view_export_xlsx(**_kwargs(column_labels=custom_labels))\n",
    "        custom_xlsx = export.inventory_view_export_xlsx(**_kwargs(column_labels=custom_labels, export_name='TEST STOCK'))\n        assert custom_xlsx.headers['content-disposition'] == 'attachment; filename=\"msa-test-stock.xlsx\"'\n",
)
replace_once(
    verify,
    '        csv_response = export.inventory_view_export_csv(**_kwargs(column_labels=custom_labels))\n',
    '        csv_response = export.inventory_view_export_csv(**_kwargs(column_labels=custom_labels, export_name="TEST STOCK"))\n        assert csv_response.headers["content-disposition"] == \'attachment; filename="msa-test-stock.csv"\'\n',
)

print("inventory_mobile_polish_patch=applied")
