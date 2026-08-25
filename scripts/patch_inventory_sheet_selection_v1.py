from pathlib import Path
import re

js_path = Path('backend/app/dashboard_assets/dashboard_inventory_views.js')
source = js_path.read_text(encoding='utf-8')

old_state = "const state={preset:'main-stock',offset:0,limit:100,q:'',mappingStatus:'',sourceClassification:'',reviewReason:'',sortField:'',sortDir:'',presets:[],registry:[],columns:null,columnWidths:{},loading:false,items:[],columnsRendered:[],selected:new Set(),drawerIndex:null,focusMode:false,density:'comfortable',dateFormat:storedDateFormat};"
new_state = "const state={preset:'main-stock',offset:0,limit:100,q:'',mappingStatus:'',sourceClassification:'',reviewReason:'',sortField:'',sortDir:'',presets:[],registry:[],columns:null,columnWidths:{},loading:false,items:[],columnsRendered:[],selected:new Set(),activeCell:null,anchorCell:null,cellRange:null,rowAnchor:null,dragging:false,drawerIndex:null,focusMode:false,density:'comfortable',dateFormat:storedDateFormat};"
assert old_state in source
source = source.replace(old_state, new_state, 1)

style_anchor = "    .inventory-sort-button{display:inline-flex;align-items:center;gap:6px;width:100%;min-height:28px;padding:0;border:0;background:transparent;color:inherit;font:inherit;font-weight:inherit;text-align:left;cursor:pointer}.inventory-sort-button:hover .inventory-sort-label{text-decoration:underline;text-decoration-thickness:1px;text-underline-offset:3px}.inventory-sort-indicator{display:inline-grid;place-items:center;min-width:14px;font-size:.68rem;opacity:.55}.inventory-sort-button.is-active .inventory-sort-indicator{opacity:1;color:var(--accent,#2f6fed)}.inventory-sort-button:focus-visible{outline:2px solid color-mix(in srgb,var(--accent,#2f6fed) 38%,transparent);outline-offset:2px;border-radius:4px}\n"
style_add = "    .inventory-row-header{width:48px!important;min-width:48px!important;max-width:48px!important;padding:0!important;text-align:center!important}.inventory-row-selector,#inventorySelectVisible{display:grid;place-items:center;width:100%;min-width:44px;min-height:44px;padding:0;border:0;border-radius:0;background:transparent;color:var(--muted,#667085);font:inherit;font-size:.72rem;font-weight:800;cursor:pointer}.inventory-row-selector:hover,#inventorySelectVisible:hover{background:color-mix(in srgb,var(--accent,#2f6fed) 8%,transparent)}.inventory-row-selector[aria-pressed=\"true\"],#inventorySelectVisible[aria-pressed=\"true\"]{background:color-mix(in srgb,var(--accent,#2f6fed) 14%,transparent);color:var(--accent,#2f6fed)}.inventory-row-selector:focus-visible,#inventorySelectVisible:focus-visible{outline:2px solid var(--accent,#2f6fed);outline-offset:-3px}.inventory-view-table td[data-col-index]{position:relative;cursor:cell;user-select:none;touch-action:pan-x pan-y}.inventory-view-table td.inventory-cell-selected{box-shadow:inset 0 0 0 1px color-mix(in srgb,var(--accent,#2f6fed) 68%,transparent);background:color-mix(in srgb,var(--accent,#2f6fed) 8%,transparent)}.inventory-view-table td.inventory-cell-active{box-shadow:inset 0 0 0 2px var(--accent,#2f6fed);z-index:3}.inventory-view-table td[data-col-index]:focus{outline:none}.inventory-view-table td[data-col-index]:focus-visible{box-shadow:inset 0 0 0 2px var(--accent,#2f6fed),0 0 0 2px color-mix(in srgb,var(--accent,#2f6fed) 20%,transparent);z-index:4}.inventory-selection-copy span{max-width:680px}.inventory-selection-actions #inventoryDetails{min-width:88px}\n"
assert style_anchor in source
source = source.replace(style_anchor, style_anchor + style_add, 1)

old_bar = '<div class="inventory-selection-actions"><button class="secondary" id="inventoryAskAI" type="button">Ask AI</button><button class="secondary" id="inventoryDeepReview" type="button">Deep Review</button><button class="secondary" id="inventoryCopySelected" type="button">Copy TSV</button><button class="secondary" id="inventoryClearSelection" type="button">Clear selection</button></div>'
new_bar = '<div class="inventory-selection-actions"><button class="secondary" id="inventoryDetails" type="button">Details</button><button class="secondary" id="inventoryAskAI" type="button">Ask AI</button><button class="secondary" id="inventoryDeepReview" type="button">Deep Review</button><button class="secondary" id="inventoryCopySelected" type="button">Copy TSV</button><button class="secondary" id="inventoryClearSelection" type="button">Clear selection</button></div>'
assert old_bar in source
source = source.replace(old_bar, new_bar, 1)

old_refs = "selectionBar=$('#inventorySelectionBar'),drawer=$('#inventoryReviewDrawer'),askAI=$('#inventoryAskAI'),deepReview=$('#inventoryDeepReview'),copySelected=$('#inventoryCopySelected'),focusToggle=$('#inventoryFocusToggle')"
new_refs = "selectionBar=$('#inventorySelectionBar'),drawer=$('#inventoryReviewDrawer'),detailsButton=$('#inventoryDetails'),askAI=$('#inventoryAskAI'),deepReview=$('#inventoryDeepReview'),copySelected=$('#inventoryCopySelected'),focusToggle=$('#inventoryFocusToggle')"
assert old_refs in source
source = source.replace(old_refs, new_refs, 1)

source, count = re.subn(
    r"  function renderColumns\(columns\)\{.*?\n  function selectedIndices",
    '''  function renderColumns(columns){thead.innerHTML=`<tr><th class="inventory-row-header inventory-frozen-select"><button id="inventorySelectVisible" type="button" aria-label="Select visible rows" title="Select visible rows" aria-pressed="false"><svg aria-hidden="true" width="18" height="18" viewBox="0 0 18 18" fill="none"><rect x="3" y="3" width="12" height="12" rx="1.5" stroke="currentColor" stroke-width="1.5"/><path d="M6 6h6v6H6z" fill="currentColor" opacity=".28"/></svg></button></th>${columns.map((col,index)=>{const width=columnWidth(col),active=state.sortField===col.field,ariaSort=active?(state.sortDir==='desc'?'descending':'ascending'):'none',indicator=active?(state.sortDir==='desc'?'▼':'▲'):'↕',label=esc(col.label);const content=col.sortable?`<button class="inventory-sort-button ${active?'is-active':''}" type="button" data-sort-field="${esc(col.field)}" aria-label="Sort by ${label}${active?` ${ariaSort}`:''}"><span class="inventory-sort-label">${label}</span><span class="inventory-sort-indicator" aria-hidden="true">${indicator}</span></button>`:label;return `<th data-field="${esc(col.field)}" class="${index===0?'inventory-frozen-first':''}" aria-sort="${ariaSort}" style="${width?`width:${width}px;min-width:${width}px;max-width:${width}px`:''}">${content}</th>`}).join('')}</tr>`}
  function selectedIndices''',
    source,
    count=1,
    flags=re.S,
)
assert count == 1

source, count = re.subn(
    r"  function updateSelection\(\)\{.*?\n  function renderRows",
    '''  function normalizedRange(a,b){if(!a||!b)return null;return {r1:Math.min(a.row,b.row),r2:Math.max(a.row,b.row),c1:Math.min(a.col,b.col),c2:Math.max(a.col,b.col)}}
  function cellSelectionCount(){const r=state.cellRange;return r?(r.r2-r.r1+1)*(r.c2-r.c1+1):0}
  function isCellSelected(row,col){const r=state.cellRange;return Boolean(r&&row>=r.r1&&row<=r.r2&&col>=r.c1&&col<=r.c2)}
  function clearCellSelection(){state.activeCell=null;state.anchorCell=null;state.cellRange=null;state.dragging=false}
  function clearSheetSelection(){state.selected.clear();state.rowAnchor=null;clearCellSelection();updateSelection()}
  function focusCell(row,col){const cell=tbody.querySelector(`td[data-row-index="${row}"][data-col-index="${col}"]`);if(cell){tbody.querySelectorAll('td[data-col-index][tabindex="0"]').forEach(item=>{if(item!==cell)item.tabIndex=-1});cell.tabIndex=0;cell.focus({preventScroll:true})}}
  function setCellSelection(row,col,{extend=false,focus=true}={}){if(row<0||col<0||row>=state.items.length||col>=state.columnsRendered.length)return;state.selected.clear();state.rowAnchor=null;const target={row,col};if(!extend||!state.anchorCell)state.anchorCell=target;state.activeCell=target;state.cellRange=normalizedRange(state.anchorCell,target);updateSelection();if(focus)requestAnimationFrame(()=>focusCell(row,col))}
  function selectRow(index,{extend=false}={}){if(index<0||index>=state.items.length)return;clearCellSelection();if(!extend||state.rowAnchor===null){state.selected.clear();state.rowAnchor=index;state.selected.add(rowKey(state.items[index],index))}else{state.selected.clear();const start=Math.min(state.rowAnchor,index),end=Math.max(state.rowAnchor,index);for(let i=start;i<=end;i++)state.selected.add(rowKey(state.items[i],i))}updateSelection()}
  function detailRowIndex(){if(state.activeCell)return state.activeCell.row;const indices=selectedIndices();return indices.length===1?indices[0]:null}
  function selectionSummary(){if(state.selected.size)return `${state.selected.size.toLocaleString()} row${state.selected.size===1?'':'s'} selected`;const r=state.cellRange,count=cellSelectionCount();if(!r||!count)return '0 selected';if(count===1)return '1 cell selected';return `${r.r2-r.r1+1}×${r.c2-r.c1+1} range · ${count.toLocaleString()} cells`}
  function updateSelection(){const rowCount=state.selected.size,cellCount=cellSelectionCount(),hasSelection=rowCount>0||cellCount>0,tooMany=rowCount>20;selectionBar.hidden=!hasSelection;$('#inventorySelectionCount').textContent=selectionSummary();const helper=selectionBar.querySelector('.inventory-selection-copy span');if(helper)helper.textContent=rowCount?'Whole-row selection · Review actions use server-rehydrated row evidence.':'Cell/range selection · read-only sheet workspace.';askAI.hidden=!(isReviewPreset()&&rowCount>0);deepReview.hidden=!(isReviewPreset()&&rowCount>0);askAI.disabled=tooMany;deepReview.disabled=tooMany;copySelected.disabled=!hasSelection;detailsButton.disabled=detailRowIndex()===null;askAI.title=tooMany?'Select at most 20 rows for AI review.':'Build a read-only server-rehydrated review context.';deepReview.title=tooMany?'Select at most 20 rows for Deep Review.':'Prefill the existing Owner Multi-Agent REVIEW workspace without running it.';tbody.querySelectorAll('tr[data-row-key]').forEach(tr=>{const selected=state.selected.has(tr.dataset.rowKey);tr.classList.toggle('inventory-row-selected',selected);tr.setAttribute('aria-selected',String(selected));const button=tr.querySelector('[data-row-selector]');if(button)button.setAttribute('aria-pressed',String(selected))});tbody.querySelectorAll('td[data-col-index]').forEach(cell=>{const row=Number(cell.dataset.rowIndex),col=Number(cell.dataset.colIndex),selected=isCellSelected(row,col),active=Boolean(state.activeCell&&state.activeCell.row===row&&state.activeCell.col===col);cell.classList.toggle('inventory-cell-selected',selected);cell.classList.toggle('inventory-cell-active',active);cell.setAttribute('aria-selected',String(selected));cell.tabIndex=active?0:-1});const header=thead.querySelector('#inventorySelectVisible');if(header){const keys=state.items.map((item,index)=>rowKey(item,index)),selectedCount=keys.filter(key=>state.selected.has(key)).length;const all=keys.length>0&&selectedCount===keys.length;header.setAttribute('aria-pressed',String(all));header.disabled=!keys.length;header.title=all?'Clear visible row selection':'Select visible rows'}}
  function renderRows''',
    source,
    count=1,
    flags=re.S,
)
assert count == 1

source, count = re.subn(
    r"  function renderRows\(columns,items\)\{.*?\n  function estimateColumnWidth",
    '''  function renderRows(columns,items){tbody.innerHTML='';state.items=items;state.columnsRendered=columns;if(!items.length){empty.textContent='No rows match this view and filters.';empty.hidden=false;table.hidden=true;updateSelection();return}empty.hidden=true;table.hidden=false;const fragment=document.createDocumentFragment();items.forEach((item,index)=>{const key=rowKey(item,index),tr=document.createElement('tr');tr.dataset.rowKey=key;tr.dataset.rowIndex=String(index);tr.className=rowClass(item);tr.setAttribute('aria-selected',String(state.selected.has(key)));tr.innerHTML=`<td class="inventory-row-header inventory-frozen-select"><button type="button" class="inventory-row-selector" data-row-selector aria-label="Select row ${state.offset+index+1}" aria-pressed="${state.selected.has(key)?'true':'false'}">${state.offset+index+1}</button></td>`+columns.map((col,colIndex)=>{const value=item[col.field],text=format(value,col.field_definition,col.field),width=state.columnWidths[col.field]?clampedWidth(state.columnWidths[col.field]):null,selected=isCellSelected(index,colIndex),active=Boolean(state.activeCell&&state.activeCell.row===index&&state.activeCell.col===colIndex);return `<td data-row-index="${index}" data-col-index="${colIndex}" data-field="${esc(col.field)}" tabindex="${active?'0':'-1'}" aria-selected="${selected?'true':'false'}" class="${colIndex===0?'inventory-frozen-first ':''}${cellClass(col.field,value)}${selected?' inventory-cell-selected':''}${active?' inventory-cell-active':''}" style="${width?`width:${width}px;min-width:${width}px;max-width:${width}px`:''}" title="${esc(text)}">${esc(text)}</td>`}).join('');fragment.appendChild(tr)});tbody.appendChild(fragment);updateSelection()}
  function estimateColumnWidth''',
    source,
    count=1,
    flags=re.S,
)
assert count == 1

source, count = re.subn(
    r"  function selectVisible\(checked\)\{.*?\n  function tsvValue",
    '''  function selectVisible(force){clearCellSelection();const keys=state.items.map((item,index)=>rowKey(item,index)),all=keys.length>0&&keys.every(key=>state.selected.has(key)),select=typeof force==='boolean'?force:!all;state.selected.clear();if(select)keys.forEach(key=>state.selected.add(key));state.rowAnchor=select&&state.items.length?0:null;updateSelection()}
  function tsvValue''',
    source,
    count=1,
    flags=re.S,
)
assert count == 1

source, count = re.subn(
    r"  async function copySelectedRows\(\)\{.*?\n\n  function drawerPair",
    '''  async function copySelection(){let text='',count=0;if(state.cellRange){const r=state.cellRange;const rows=[];for(let row=r.r1;row<=r.r2;row++){const values=[];for(let col=r.c1;col<=r.c2;col++){const column=state.columnsRendered[col];values.push(tsvValue(format(state.items[row]?.[column.field],column.field_definition,column.field)))}rows.push(values.join('\\t'))}text=rows.join('\\n');count=cellSelectionCount()}else{const indices=selectedIndices();if(!indices.length)return;const headers=state.columnsRendered.map(col=>col.label);const rows=indices.map(index=>state.columnsRendered.map(col=>tsvValue(format(state.items[index]?.[col.field],col.field_definition,col.field))));text=[headers,...rows].map(row=>row.map?row.map(tsvValue).join('\\t'):row).join('\\n');count=indices.length}const original=copySelected.textContent;copySelected.disabled=true;try{await writeClipboard(text);copySelected.textContent=`Copied ${count}`;copySelected.classList.add('inventory-copy-feedback');setTimeout(()=>{copySelected.textContent=original;copySelected.classList.remove('inventory-copy-feedback');copySelected.disabled=false},1200)}catch(err){copySelected.textContent=original;copySelected.disabled=false;window.alert(err.message)}}

  function drawerPair''',
    source,
    count=1,
    flags=re.S,
)
assert count == 1

source, count = re.subn(
    r"  function changeSort\(field\)\{.*?\n  function syncWorkspaceMode",
    '''  function changeSort(field){if(!field)return;if(state.sortField===field){state.sortDir=state.sortDir==='asc'?'desc':'asc'}else{state.sortField=field;state.sortDir='asc'}state.offset=0;clearSheetSelection();drawer.hidden=true;renderActiveFilters();load()}
  function syncWorkspaceMode''',
    source,
    count=1,
    flags=re.S,
)
assert count == 1

old_clear = "$('#inventoryClearSelection').addEventListener('click',()=>{state.selected.clear();tbody.querySelectorAll('.inventory-row-check').forEach(input=>{input.checked=false});updateSelection()});\n  copySelected.addEventListener('click',copySelectedRows);"
new_clear = "$('#inventoryClearSelection').addEventListener('click',clearSheetSelection);\n  copySelected.addEventListener('click',copySelection);\n  detailsButton.addEventListener('click',()=>{const index=detailRowIndex();if(index!==null)openDrawer(index)});"
assert old_clear in source
source = source.replace(old_clear, new_clear, 1)

old_head = "thead.addEventListener('change',event=>{if(event.target.matches('#inventorySelectVisible'))selectVisible(event.target.checked)});\n  thead.addEventListener('click',event=>{const button=event.target.closest('[data-sort-field]');if(button)changeSort(button.dataset.sortField)});"
new_head = "thead.addEventListener('click',event=>{const corner=event.target.closest('#inventorySelectVisible');if(corner){selectVisible();return}const button=event.target.closest('[data-sort-field]');if(button)changeSort(button.dataset.sortField)});"
assert old_head in source
source = source.replace(old_head, new_head, 1)

old_tail = "tbody.addEventListener('click',event=>{const tr=event.target.closest('tr[data-row-index]');if(!tr)return;const index=Number(tr.dataset.rowIndex),key=tr.dataset.rowKey;if(event.target.matches('.inventory-row-check')){event.stopPropagation();event.target.checked?state.selected.add(key):state.selected.delete(key);updateSelection();return}openDrawer(index)});\n  document.addEventListener('keydown',event=>{if(event.key==='Escape'&&state.focusMode&&!root.querySelector('.inventory-ai-dialog-backdrop'))toggleFocus(false)});"
new_tail = '''tbody.addEventListener('pointerdown',event=>{const rowButton=event.target.closest('[data-row-selector]');if(rowButton){if(event.button!==0)return;const tr=rowButton.closest('tr[data-row-index]');selectRow(Number(tr.dataset.rowIndex),{extend:event.shiftKey});event.preventDefault();rowButton.focus();return}const cell=event.target.closest('td[data-row-index][data-col-index]');if(!cell||event.button!==0)return;const row=Number(cell.dataset.rowIndex),col=Number(cell.dataset.colIndex);setCellSelection(row,col,{extend:event.shiftKey,focus:true});state.dragging=event.pointerType==='mouse';if(event.pointerType==='mouse')event.preventDefault()});
  tbody.addEventListener('pointerover',event=>{if(!state.dragging||!(event.buttons&1))return;const cell=event.target.closest('td[data-row-index][data-col-index]');if(!cell)return;setCellSelection(Number(cell.dataset.rowIndex),Number(cell.dataset.colIndex),{extend:true,focus:false})});
  document.addEventListener('pointerup',()=>{state.dragging=false});
  table.addEventListener('keydown',event=>{const cell=event.target.closest('td[data-row-index][data-col-index]');if(!cell)return;const row=Number(cell.dataset.rowIndex),col=Number(cell.dataset.colIndex);if(event.key==='Enter'){event.preventDefault();openDrawer(row);return}if(event.key===' '&&event.shiftKey){event.preventDefault();selectRow(row,{extend:false});return}if((event.ctrlKey||event.metaKey)&&event.key.toLowerCase()==='c'&&(state.cellRange||state.selected.size)){event.preventDefault();copySelection();return}const delta={ArrowUp:[-1,0],ArrowDown:[1,0],ArrowLeft:[0,-1],ArrowRight:[0,1]}[event.key];if(!delta)return;event.preventDefault();const nextRow=Math.max(0,Math.min(state.items.length-1,row+delta[0])),nextCol=Math.max(0,Math.min(state.columnsRendered.length-1,col+delta[1]));setCellSelection(nextRow,nextCol,{extend:event.shiftKey,focus:true})});
  document.addEventListener('keydown',event=>{if(event.key==='Escape'&&state.focusMode&&!root.querySelector('.inventory-ai-dialog-backdrop'))toggleFocus(false)});'''
assert old_tail in source
source = source.replace(old_tail, new_tail, 1)

replacements = {
    "state.preset=presetSelect.value;state.offset=0;state.columns=null;state.columnWidths={};state.sortField='';state.sortDir='';state.selected.clear();drawer.hidden=true": "state.preset=presetSelect.value;state.offset=0;state.columns=null;state.columnWidths={};state.sortField='';state.sortDir='';clearSheetSelection();drawer.hidden=true",
    "state.q=search.value.trim();state.offset=0;renderActiveFilters();load()": "state.q=search.value.trim();state.offset=0;clearSheetSelection();renderActiveFilters();load()",
    "state.mappingStatus=mappingStatus.value;state.offset=0;renderActiveFilters();load()": "state.mappingStatus=mappingStatus.value;state.offset=0;clearSheetSelection();renderActiveFilters();load()",
    "state.sourceClassification=sourceClassification.value;state.offset=0;renderActiveFilters();load()": "state.sourceClassification=sourceClassification.value;state.offset=0;clearSheetSelection();renderActiveFilters();load()",
    "state.reviewReason=reviewReason.value.trim();state.offset=0;renderActiveFilters();load()": "state.reviewReason=reviewReason.value.trim();state.offset=0;clearSheetSelection();renderActiveFilters();load()",
    "state.offset=Math.max(0,state.offset-state.limit);drawer.hidden=true;load()": "state.offset=Math.max(0,state.offset-state.limit);clearSheetSelection();drawer.hidden=true;load()",
    "state.offset+=state.limit;drawer.hidden=true;load()": "state.offset+=state.limit;clearSheetSelection();drawer.hidden=true;load()",
}
for old, new in replacements.items():
    assert old in source, old
    source = source.replace(old, new, 1)

js_path.write_text(source, encoding='utf-8')

# Dashboard override.
dash = Path('design-system/medicine-store-assistant/pages/dashboard.md')
text = dash.read_text(encoding='utf-8')
old = """Primary workflow:\n\n1. search;\n2. filter;\n3. scan spreadsheet-style rows;\n4. open detail drawer;\n5. inspect provenance/status;\n6. optionally expand the table into focus mode;\n7. return to Inventory or Overview without losing navigation context.\n\nCurrent inventory phase is read-only. Do not show fake inventory edit/save buttons."""
new = """Primary workflow:\n\n1. search/filter and scan spreadsheet-style rows;\n2. click/tap a data cell to make it the active sheet cell;\n3. extend rectangular ranges with desktop drag / Shift and keyboard arrows;\n4. use the dedicated row-selector gutter for one or more whole rows;\n5. open item provenance/status through explicit `Details` or the keyboard Enter shortcut rather than row-wide click;\n6. optionally expand the table into focus mode;\n7. return to Inventory or Overview without losing navigation context.\n\nCell/range selection is presentation-only. Whole-row selection remains the bounded source for existing server-rehydrated Ask AI / Deep Review context. Current inventory phase is read-only. Do not show fake inventory edit/save buttons."""
assert old in text
dash.write_text(text.replace(old, new, 1), encoding='utf-8')

# Surface ownership registry.
ownership = Path('docs/design/WEB_SURFACE_OWNERSHIP.md')
text = ownership.read_text(encoding='utf-8')
marker = "| MCP Agent binding/settings | Agent Management MCP connection section | `dashboard_mcp_binding.js` | `dashboard_mcp_binding.js` | `dashboard_mcp_binding.js` | MCP binding/grant APIs | none |\n"
row = "| Inventory Workbench / sheet selection | `.view[data-panel=\"inventory\"]` / `#inventoryViewTable` | `dashboard_inventory_views.js` | `dashboard_inventory_views.js` | `dashboard_inventory_views.js` | Inventory View APIs for rows; selection/layout are session-only in v1 | none |\n"
assert marker in text
ownership.write_text(text.replace(marker, marker + row, 1), encoding='utf-8')

# Continuity checkpoints.
additions = {
    'ROADMAP.md': """\n\n## Inventory Sheet Interaction Foundation v1 — ACTIVE\n\nCurrent bounded target after formatted Excel export: convert the Inventory Workbench from row-click inspection to a sheet-selection model before Saved Custom Views / View Builder. Contract: `docs/design/INVENTORY_SHEET_INTERACTION_V1.md`.\n\nAuthorized v1 scope: active cell, rectangular cell range, desktop drag / Shift range, Arrow + Shift+Arrow keyboard movement, dedicated whole-row selector gutter, explicit Details action, selection-aware TSV copy, and preservation of whole-row Ask AI / Deep Review semantics. Cell click must no longer open details. Selection remains session-only/read-only. Fill colors and persistent formatting are the next Sheet Formatting slice, not part of this v1.\n""",
    'IMPLEMENTATION_PLAN.md': """\n\n### 5.6A Inventory Sheet Interaction Foundation v1 — ACTIVE\n\n- [ ] Single click/tap selects a data cell without opening details.\n- [ ] Desktop pointer drag and Shift+click create a rectangular range.\n- [ ] Arrow keys move the active cell; Shift+Arrow extends the range.\n- [ ] Dedicated row-selector gutter selects one/contiguous whole rows.\n- [ ] Explicit Details / Enter opens the selected row drawer.\n- [ ] Copy TSV supports selected cell rectangles and whole rows.\n- [ ] Ask AI / Deep Review remain whole-row-only and server-rehydrated.\n- [ ] Mobile 390x844 tap/scroll behavior is proven.\n- [ ] No mutation/canonicality change.\n\nContract: `docs/design/INVENTORY_SHEET_INTERACTION_V1.md`. Sheet Formatting (fill/clear fill) follows only after this selection foundation is stable. Saved Custom Views / View Builder follows the sheet interaction/formatting foundation.\n""",
    'NEW_CHAT_BOOTSTRAP.md': """\n\n## Current bounded target — Inventory Sheet Interaction Foundation v1\n\nFormatted Excel export is complete and production-runtime verified. The active Inventory work is now `docs/design/INVENTORY_SHEET_INTERACTION_V1.md`: cell-first selection, rectangular ranges, keyboard navigation, whole-row selector gutter, explicit Details, and selection-aware copy. Do not restore row-wide click-to-open behavior. Whole-row selection remains the only source for Ask AI / Deep Review row context. Fill colors/persistent formatting follow after this v1; Saved Custom Views / View Builder follows the sheet interaction/formatting foundation. All current work remains read-only and PostgreSQL remains non-canonical.\n""",
}
for name, addition in additions.items():
    path = Path(name)
    current = path.read_text(encoding='utf-8')
    heading = addition.strip().splitlines()[0]
    if heading not in current:
        path.write_text(current.rstrip() + addition + '\n', encoding='utf-8')

smoke = r'''import assert from 'node:assert/strict';
import path from 'node:path';
import { chromium } from 'playwright';

const script=path.join(process.cwd(),'backend/app/dashboard_assets/dashboard_inventory_views.js');
const browser=await chromium.launch({headless:true});
const page=await browser.newPage({viewport:{width:1280,height:800}});
await page.setContent('<main id="msa"><section class="view" data-panel="inventory"></section></main>');
await page.evaluate(()=>{
  window.__copied='';
  Object.defineProperty(navigator,'clipboard',{configurable:true,value:{writeText:async text=>{window.__copied=text}}});
  const items=[
    {lot_id:'l1',local_item_name:'Alpha',current_qty:10,cms_code:'C1',mapping_status:'REVIEW_REQUIRED'},
    {lot_id:'l2',local_item_name:'Beta',current_qty:20,cms_code:'C2',mapping_status:'REVIEW_REQUIRED'},
    {lot_id:'l3',local_item_name:'Gamma',current_qty:30,cms_code:'C3',mapping_status:'REVIEW_REQUIRED'},
  ];
  window.fetch=async url=>{
    const requestPath=String(url);
    const json=value=>Promise.resolve({ok:true,status:200,json:async()=>value});
    if(requestPath.includes('/presets'))return json({items:[{view_id:'main-stock',name:'Main Stock'},{view_id:'migration-review',name:'Migration Review'}]});
    if(requestPath.includes('/registry'))return json({fields:[{key:'local_item_name',label:'Items',data_type:'string',kind:'ENTITY_FIELD'},{key:'current_qty',label:'Current Qty',data_type:'decimal',kind:'COMPUTED_FIELD'},{key:'cms_code',label:'CMS Code',data_type:'string',kind:'ENTITY_FIELD'}]});
    if(requestPath.includes('/rows'))return json({view:{view_id:'main-stock',name:'Main Stock',description:'Test view',row_grain:'PRODUCT_LOT',store_scope:'MAIN',columns:[{field:'local_item_name',label:'Items',width:180},{field:'current_qty',label:'Current Qty',width:120},{field:'cms_code',label:'CMS Code',width:120}]},columns:[{field:'local_item_name',label:'Items',sortable:true,width:180,field_definition:{key:'local_item_name',data_type:'string'}},{field:'current_qty',label:'Current Qty',sortable:true,width:120,field_definition:{key:'current_qty',data_type:'decimal'}},{field:'cms_code',label:'CMS Code',sortable:true,width:120,field_definition:{key:'cms_code',data_type:'string'}}],items,sort:{field:null,direction:null}});
    throw new Error('Unexpected '+requestPath);
  };
});
await page.addScriptTag({path:script});
await page.getByText('Alpha',{exact:true}).waitFor();

const cell=(row,col)=>page.locator(`tbody tr:nth-child(${row+1}) td[data-col-index="${col}"]`);
await cell(0,0).click();
assert.equal(await page.locator('#inventorySelectionCount').textContent(),'1 cell selected');
assert.equal(await page.locator('#inventoryReviewDrawer').isHidden(),true,'cell click must not open details');
assert.equal(await cell(0,0).getAttribute('aria-selected'),'true');

await cell(1,1).click({modifiers:['Shift']});
assert.match(await page.locator('#inventorySelectionCount').textContent(),/2×2 range · 4 cells/);
assert.equal(await cell(1,1).getAttribute('aria-selected'),'true');

await cell(1,1).focus();
await page.keyboard.press('ArrowRight');
assert.equal(await cell(1,2).getAttribute('aria-selected'),'true');
assert.equal(await page.locator('#inventorySelectionCount').textContent(),'1 cell selected');
await page.keyboard.press('Shift+ArrowDown');
assert.match(await page.locator('#inventorySelectionCount').textContent(),/2×1 range · 2 cells/);

const box1=await cell(0,0).boundingBox(),box3=await cell(2,2).boundingBox();
assert.ok(box1&&box3);
await page.mouse.move(box1.x+8,box1.y+8);
await page.mouse.down();
await page.mouse.move(box3.x+8,box3.y+8,{steps:5});
await page.mouse.up();
assert.match(await page.locator('#inventorySelectionCount').textContent(),/3×3 range · 9 cells/);

await cell(0,0).click();
await page.getByRole('button',{name:'Copy TSV'}).click();
assert.equal(await page.evaluate(()=>window.__copied),'Alpha');

const row1=page.getByRole('button',{name:'Select row 1'}),row3=page.getByRole('button',{name:'Select row 3'});
await row1.click();
assert.equal(await page.locator('#inventorySelectionCount').textContent(),'1 row selected');
assert.equal(await page.getByRole('button',{name:'Details'}).isEnabled(),true);
await page.getByRole('button',{name:'Details'}).click();
assert.equal(await page.locator('#inventoryReviewDrawer').isVisible(),true);
assert.match(await page.locator('#inventoryDrawerTitle').textContent(),/Alpha/);
await page.getByRole('button',{name:'Close review detail'}).click();
await row3.click({modifiers:['Shift']});
assert.equal(await page.locator('#inventorySelectionCount').textContent(),'3 rows selected');

await page.getByRole('button',{name:'Select visible rows'}).click();
assert.equal(await page.locator('#inventorySelectionCount').textContent(),'0 selected');
assert.equal(await page.locator('#inventorySelectionBar').isHidden(),true);

await page.setViewportSize({width:390,height:844});
await cell(0,1).click();
assert.equal(await page.locator('#inventoryReviewDrawer').isHidden(),true);
assert.equal(await page.locator('#inventorySelectionCount').textContent(),'1 cell selected');
const touchTarget=await row1.boundingBox();
assert.ok(touchTarget&&touchTarget.height>=40,'row selector remains a practical touch target');

await browser.close();
console.log('inventory_sheet_selection=pass cell_click=pass range=pass drag=pass keyboard=pass rows=pass details=explicit copy=pass mobile=pass');
'''
Path('tests/web/inventory_sheet_selection_smoke.mjs').write_text(smoke, encoding='utf-8')

wf = Path('.github/workflows/validate-inventory-view-engine.yml')
text = wf.read_text(encoding='utf-8')
path_line = "      - 'tests/web/inventory_sorting_smoke.mjs'\n"
if "inventory_sheet_selection_smoke.mjs" not in text:
    assert path_line in text
    text = text.replace(path_line, path_line + "      - 'tests/web/inventory_sheet_selection_smoke.mjs'\n", 1)
    step = "      - name: Run Inventory server sorting smoke\n        run: node tests/web/inventory_sorting_smoke.mjs\n"
    assert step in text
    text = text.replace(step, step + "      - name: Run Inventory Sheet Interaction smoke\n        run: node tests/web/inventory_sheet_selection_smoke.mjs\n", 1)
wf.write_text(text, encoding='utf-8')
