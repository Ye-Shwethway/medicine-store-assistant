from pathlib import Path

CHECKPOINT = '''\n### Inventory display/export format polish — COMPLETE + RUNTIME VERIFIED\n\nPR #199 merge `4d407e5d01343deb3da9a8a0f82f6122e989035f` refined presentation without changing inventory semantics:\n\n- Excel quantity fields use whole-number display format `0`;\n- Excel price fields use decimal display format `0.00`;\n- Excel Expiry Date uses `mmm-yy` (for example `Mar-26`);\n- the global `ExcelColumn` contract accepts caller-owned `number_format`, keeping the reusable renderer area-agnostic;\n- Inventory Web date display defaults to `DD-MM-YYYY`;\n- the Web toolbar provides `DD-MM-YYYY`, `MM-DD-YYYY`, `YYYY-MM-DD`, and `DD-MMM-YYYY` display choices;\n- the selected Web date format is display-only and persists locally across reopen; underlying ISO dates/query semantics are unchanged.\n\nRuntime issue #166, run `32821445117`, verified Main Stock **799** rows with Excel formats `expiry=mmm-yy`, `qty=0`, `price=0.00`, `mutation=false`, `database_canonical=false`, `migration_baseline_accepted=false`. Deployment issue #26, run `32821445217`, verified production deployment success at the same SHA.\n'''

for name in ('ROADMAP.md','IMPLEMENTATION_PLAN.md','NEW_CHAT_BOOTSTRAP.md'):
    path=Path(name)
    text=path.read_text(encoding='utf-8')
    if 'Inventory display/export format polish — COMPLETE + RUNTIME VERIFIED' not in text:
        marker='\n## Immediate boundary'
        if marker in text:
            text=text.replace(marker, CHECKPOINT+marker,1)
        else:
            text += CHECKPOINT
    if name=='NEW_CHAT_BOOTSTRAP.md':
        evidence='- PR #199 merge `4d407e5d01343deb3da9a8a0f82f6122e989035f`: Inventory quantity/date display format polish; runtime run `32821445117`; deploy run `32821445217`.\n'
        key='Key recent evidence:\n\n'
        if evidence not in text and key in text:
            text=text.replace(key,key+evidence,1)
    path.write_text(text,encoding='utf-8')

arch=Path('docs/architecture/REUSABLE_EXCEL_EXPORT.md')
text=arch.read_text(encoding='utf-8')
section='''\n## Caller-owned display formats\n\n`ExcelColumn.number_format` is an optional presentation contract owned by the calling area. The global renderer must not infer domain-specific meaning from field names. Inventory currently supplies:\n\n- quantity fields: `0`;\n- price fields: `0.00`;\n- Expiry Date: `mmm-yy`.\n\nThis affects workbook display only; it does not round/rewrite source values or change inventory semantics. Inventory Web date formatting is a separate display-only browser preference, defaulting to `DD-MM-YYYY`; underlying ISO date values remain unchanged.\n'''
if '## Caller-owned display formats' not in text:
    text += section
arch.write_text(text,encoding='utf-8')
print('inventory_format_docs_sync=pass')
