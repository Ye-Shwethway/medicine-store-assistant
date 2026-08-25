from pathlib import Path


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"{label}: expected one anchor, found {count}")
    return text.replace(old, new, 1)


p = Path("backend/app/main.py")
s = p.read_text()
s = replace_once(
    s,
    "from app.inventory_view_engine import router as inventory_view_router\nfrom app.inventory_view_export import router as inventory_view_export_router",
    "from app.inventory_view_engine import router as inventory_view_router\nfrom app.inventory_saved_views import router as inventory_saved_views_router\nfrom app.inventory_view_export import router as inventory_view_export_router",
    "main import",
)
s = replace_once(
    s,
    "app.include_router(inventory_view_router)\napp.include_router(inventory_view_export_router)",
    "app.include_router(inventory_view_router)\napp.include_router(inventory_saved_views_router)\napp.include_router(inventory_view_export_router)",
    "main router",
)
p.write_text(s)

p = Path("backend/app/dashboard_assets/dashboard_inventory_views.js")
s = p.read_text()
s = replace_once(
    s,
    "  const DATE_FORMATS=new Set(['dd-mm-yyyy','mm-dd-yyyy','yyyy-mm-dd','dd-mmm-yyyy']);\n  const storedDateFormat=(()=>{try{const value=localStorage.getItem(DATE_FORMAT_KEY);return DATE_FORMATS.has(value)?value:'dd-mm-yyyy'}catch{return 'dd-mm-yyyy'}})();\n  const state={preset:'main-stock',offset:0,limit:100,q:'',mappingStatus:'',sourceClassification:'',reviewReason:'',sortField:'',sortDir:'',presets:[],registry:[],columns:null,columnWidths:{},loading:false,items:[],columnsRendered:[],selected:new Set(),activeCell:null,anchorCell:null,cellRange:null,rowAnchor:null,dragging:false,drawerIndex:null,focusMode:false,density:'comfortable',dateFormat:storedDateFormat,formatFills:new Map()};",
    "  const DATE_FORMATS=new Set(['dd-mm-yyyy','mm-dd-yyyy','yyyy-mm-dd','dd-mmm-yyyy']);\n  const ACTIVE_SAVED_VIEW_KEY='msa.inventory.activeSavedViewId';\n  const storedDateFormat=(()=>{try{const value=localStorage.getItem(DATE_FORMAT_KEY);return DATE_FORMATS.has(value)?value:'dd-mm-yyyy'}catch{return 'dd-mm-yyyy'}})();\n  const storedSavedViewId=(()=>{try{return localStorage.getItem(ACTIVE_SAVED_VIEW_KEY)||''}catch{return ''}})();\n  const state={preset:'main-stock',offset:0,limit:100,q:'',mappingStatus:'',sourceClassification:'',reviewReason:'',sortField:'',sortDir:'',presets:[],savedViews:[],activeSavedViewId:storedSavedViewId,registry:[],columns:null,columnWidths:{},loading:false,items:[],columnsRendered:[],selected:new Set(),activeCell:null,anchorCell:null,cellRange:null,rowAnchor:null,dragging:false,drawerIndex:null,focusMode:false,density:'comfortable',dateFormat:storedDateFormat,formatFills:new Map()};",
    "state",
)
s = replace_once(
    s,
    '      <label>View<select id="inventoryPresetSelect"><option value="main-stock">Main Stock</option></select></label>\n      <label class="inventory-search-label">Search<input id="inventoryViewSearch" type="search" placeholder="Search item or CMS evidence…"></label>',
    '      <label>View<select id="inventoryPresetSelect"><option value="main-stock">Main Stock</option></select></label>\n      <div class="inventory-saved-view-actions" aria-label="Saved view actions"><button class="secondary" id="inventorySaveView" type="button">Save view</button><button class="secondary" id="inventorySaveViewAs" type="button">Save as</button><button class="secondary" id="inventoryDeleteView" type="button" disabled>Delete view</button></div>\n      <label class="inventory-search-label">Search<input id="inventoryViewSearch" type="search" placeholder="Search item or CMS evidence…"></label>',
    "saved buttons",
)
s = replace_once(
    s,
    '      <button class="secondary" id="inventoryViewRefresh" type="button">Refresh</button>\n      <button class="secondary inventory-focus-toggle" id="inventoryFocusToggle" type="button" aria-pressed="false">Focus mode</button>',
    '      <button class="secondary" id="inventoryViewRefresh" type="button">Refresh</button>\n      <button class="secondary" id="inventoryClearAll" type="button">Clear all</button>\n      <button class="secondary inventory-focus-toggle" id="inventoryFocusToggle" type="button" aria-pressed="false">Focus mode</button>',
    "clear all",
)
s = s.replace(
    "Session layout only — reorder, width and visibility do not change database structure or the saved preset.",
    "Current layout only — Save view to persist reorder, width and visibility without changing database structure.",
    1,
)
s = s.replace(
    "Saved custom layouts come later in View Builder.",
    "Save view persists this layout; full View Builder controls come next.",
    1,
)
s = replace_once(
    s,
    "    @media(max-width:760px){.inventory-active-filters{margin-top:0}",
    "    .inventory-saved-view-actions{display:inline-flex;align-items:center;gap:5px;padding:3px;border:1px solid color-mix(in srgb,var(--accent,#2f6fed) 16%,var(--border,#d9dde7));border-radius:9px;background:color-mix(in srgb,var(--accent,#2f6fed) 3%,var(--card,#fff))}.inventory-saved-view-actions button{min-height:36px;padding:6px 9px;font-size:.7rem}.inventory-saved-view-actions #inventorySaveView{font-weight:800}.inventory-saved-view-actions #inventoryDeleteView:not(:disabled){color:#a52d43}.inventory-view-toolbar option[data-custom-view]{font-weight:700}\n    @media(max-width:760px){.inventory-active-filters{margin-top:0}.inventory-saved-view-actions{width:100%;display:grid;grid-template-columns:repeat(3,minmax(0,1fr))}",
    "saved styles",
)
s = replace_once(
    s,
    "const $=s=>panel.querySelector(s),table=$('#inventoryViewTable'),thead=table.querySelector('thead'),tbody=table.querySelector('tbody'),empty=$('#inventoryViewEmpty'),meta=$('#inventoryViewMeta'),presetSelect=$('#inventoryPresetSelect'),search=$('#inventoryViewSearch'),columnsPanel=$('#inventoryColumnPanel'),columnGrid=$('#inventoryColumnGrid'),filters=$('#inventoryReviewFilters'),activeFilters=$('#inventoryActiveFilters'),mappingStatus=$('#inventoryMappingStatus'),sourceClassification=$('#inventorySourceClassification'),reviewReason=$('#inventoryReviewReason'),selectionBar=$('#inventorySelectionBar'),drawer=$('#inventoryReviewDrawer'),detailsButton=$('#inventoryDetails'),askAI=$('#inventoryAskAI'),deepReview=$('#inventoryDeepReview'),copySelected=$('#inventoryCopySelected'),fillToggle=$('#inventoryFillToggle'),fillMenu=$('#inventoryFillMenu'),clearFill=$('#inventoryClearFill'),focusToggle=$('#inventoryFocusToggle'),densityToggle=$('#inventoryDensityToggle'),dateFormatSelect=$('#inventoryDateFormat');",
    "const $=s=>panel.querySelector(s),table=$('#inventoryViewTable'),thead=table.querySelector('thead'),tbody=table.querySelector('tbody'),empty=$('#inventoryViewEmpty'),meta=$('#inventoryViewMeta'),presetSelect=$('#inventoryPresetSelect'),saveViewButton=$('#inventorySaveView'),saveViewAsButton=$('#inventorySaveViewAs'),deleteViewButton=$('#inventoryDeleteView'),search=$('#inventoryViewSearch'),columnsPanel=$('#inventoryColumnPanel'),columnGrid=$('#inventoryColumnGrid'),filters=$('#inventoryReviewFilters'),activeFilters=$('#inventoryActiveFilters'),mappingStatus=$('#inventoryMappingStatus'),sourceClassification=$('#inventorySourceClassification'),reviewReason=$('#inventoryReviewReason'),selectionBar=$('#inventorySelectionBar'),drawer=$('#inventoryReviewDrawer'),detailsButton=$('#inventoryDetails'),askAI=$('#inventoryAskAI'),deepReview=$('#inventoryDeepReview'),copySelected=$('#inventoryCopySelected'),fillToggle=$('#inventoryFillToggle'),fillMenu=$('#inventoryFillMenu'),clearFill=$('#inventoryClearFill'),focusToggle=$('#inventoryFocusToggle'),densityToggle=$('#inventoryDensityToggle'),dateFormatSelect=$('#inventoryDateFormat');",
    "dom refs",
)
old_load = "  async function loadDefinitions(){const [presets,registry]=await Promise.all([api('/dashboard/api/inventory-view/presets'),api('/dashboard/api/inventory-view/registry')]);state.presets=presets.items||[];state.registry=registry.fields||[];presetSelect.innerHTML=state.presets.map(view=>`<option value=\"${esc(view.view_id)}\">${esc(view.name)}</option>`).join('');presetSelect.value=state.preset}"
new_load = r'''  function savedViewById(id){return state.savedViews.find(view=>view.view_id===id)||null}
  function activeSavedView(){return savedViewById(state.activeSavedViewId)}
  function renderSavedViewButtons(){deleteViewButton.disabled=!state.activeSavedViewId;saveViewButton.title=state.activeSavedViewId?'Update this custom view':'Create a custom view from the current system preset'}
  function renderViewOptions(){const system=state.presets.map(view=>`<option value="${esc(view.view_id)}">${esc(view.name)}</option>`).join(''),custom=state.savedViews.map(view=>`<option data-custom-view="1" value="custom:${esc(view.view_id)}">Custom · ${esc(view.name)}</option>`).join('');presetSelect.innerHTML=system+custom;presetSelect.value=state.activeSavedViewId?`custom:${state.activeSavedViewId}`:state.preset;renderSavedViewButtons()}
  function persistActiveSavedViewId(){try{if(state.activeSavedViewId)localStorage.setItem(ACTIVE_SAVED_VIEW_KEY,state.activeSavedViewId);else localStorage.removeItem(ACTIVE_SAVED_VIEW_KEY)}catch{}}
  function clearActiveSavedView(){state.activeSavedViewId='';persistActiveSavedViewId();renderSavedViewButtons()}
  function applySavedViewDefinition(saved){if(!saved)return false;const definition=saved.definition||{},filters=definition.filters||{},sort=definition.sort||{};state.activeSavedViewId=saved.view_id;state.preset=saved.base_preset;state.columns=Array.isArray(definition.fields)&&definition.fields.length?[...definition.fields]:null;state.columnWidths={...(definition.column_widths||{})};state.density=definition.density==='compact'?'compact':'comfortable';state.q=String(filters.q||'');state.mappingStatus=String(filters.mapping_status||'');state.sourceClassification=String(filters.source_classification||'');state.reviewReason=String(filters.review_reason||'');state.sortField=String(sort.field||'');state.sortDir=String(sort.direction||'');state.formatFills=new Map((definition.fills||[]).filter(item=>item?.row_key&&item?.field&&FILL_TOKENS.has(item.fill)).map(item=>[`${item.row_key}\u0000${item.field}`,item.fill]));search.value=state.q;mappingStatus.value=state.mappingStatus;sourceClassification.value=state.sourceClassification;reviewReason.value=state.reviewReason;state.offset=0;persistActiveSavedViewId();syncWorkspaceMode();syncReviewControls();renderSavedViewButtons();return true}
  function serializedFills(fields){const allowed=new Set(fields),fills=[];for(const [key,fill] of state.formatFills.entries()){const split=key.indexOf('\u0000'),rowKeyPart=split>=0?key.slice(0,split):'',field=split>=0?key.slice(split+1):'';if(rowKeyPart&&allowed.has(field)&&FILL_TOKENS.has(fill))fills.push({row_key:rowKeyPart,field,fill})}return fills}
  function savedViewPayload(name){const fields=(state.columns?.length?state.columns:state.columnsRendered.map(column=>column.field)).filter((field,index,array)=>field&&array.indexOf(field)===index),widths=Object.fromEntries(Object.entries(state.columnWidths||{}).filter(([field,width])=>fields.includes(field)&&Number(width)>=64&&Number(width)<=800));return {name,base_preset:state.preset,definition:{fields,column_widths:widths,density:state.density,filters:{q:state.q,mapping_status:state.mappingStatus,source_classification:state.preset==='migration-review'?state.sourceClassification:'',review_reason:state.reviewReason},sort:{field:state.sortField||'',direction:state.sortField?(state.sortDir||'asc'):null},fills:serializedFills(fields)}}}
  async function refreshSavedViews(){const saved=await api('/dashboard/api/inventory-view/saved-views');state.savedViews=saved.items||[];if(state.activeSavedViewId&&!savedViewById(state.activeSavedViewId))clearActiveSavedView();renderViewOptions()}
  async function saveCurrentView(asNew=false){if(!state.columnsRendered.length){window.alert('Load the Inventory view before saving.');return}const current=activeSavedView(),updating=Boolean(current&&!asNew),defaultName=updating?current.name:`${state.presets.find(view=>view.view_id===state.preset)?.name||'Inventory'} view`,name=updating?current.name:window.prompt(asNew?'Save current view as':'Name this saved view',defaultName);if(name===null)return;const trimmed=String(name).trim();if(!trimmed){window.alert('Enter a saved view name.');return}saveViewButton.disabled=true;saveViewAsButton.disabled=true;try{const path=updating?`/dashboard/api/inventory-view/saved-views/${current.view_id}`:'/dashboard/api/inventory-view/saved-views',saved=await api(path,{method:updating?'PUT':'POST',body:JSON.stringify(savedViewPayload(trimmed))});state.activeSavedViewId=saved.view_id;persistActiveSavedViewId();await refreshSavedViews();renderViewOptions();window.alert(updating?'Saved view updated.':'Saved view created.')}catch(err){window.alert(err.message)}finally{saveViewButton.disabled=false;saveViewAsButton.disabled=false;renderSavedViewButtons()}}
  async function deleteCurrentSavedView(){const current=activeSavedView();if(!current)return;if(!window.confirm(`Delete saved view “${current.name}”?`))return;deleteViewButton.disabled=true;try{await api(`/dashboard/api/inventory-view/saved-views/${current.view_id}`,{method:'DELETE'});const base=current.base_preset;clearActiveSavedView();state.preset=base;state.columns=null;state.columnWidths={};state.formatFills=new Map();state.q='';state.mappingStatus='';state.sourceClassification='';state.reviewReason='';state.sortField='';state.sortDir='';search.value='';mappingStatus.value='';sourceClassification.value='';reviewReason.value='';await refreshSavedViews();renderViewOptions();clearSheetSelection();syncWorkspaceMode();syncReviewControls();renderActiveFilters();load()}catch(err){window.alert(err.message)}finally{renderSavedViewButtons()}}
  async function loadDefinitions(){const [presets,registry,saved]=await Promise.all([api('/dashboard/api/inventory-view/presets'),api('/dashboard/api/inventory-view/registry'),api('/dashboard/api/inventory-view/saved-views')]);state.presets=presets.items||[];state.registry=registry.fields||[];state.savedViews=saved.items||[];const stored=state.activeSavedViewId?savedViewById(state.activeSavedViewId):null;if(stored)applySavedViewDefinition(stored);else if(state.activeSavedViewId)clearActiveSavedView();renderViewOptions()}'''
s = replace_once(s, old_load, new_load, "load definitions")
s = replace_once(
    s,
    "$('#inventoryViewName').textContent=view.name;$('#inventoryViewDescription').textContent=view.description;",
    "const custom=activeSavedView();$('#inventoryViewName').textContent=custom?custom.name:view.name;$('#inventoryViewDescription').textContent=custom?`Custom view · based on ${view.name} · presentation-only saved definition`:view.description;",
    "custom title",
)
s = replace_once(
    s,
    "  presetSelect.addEventListener('change',()=>{state.preset=presetSelect.value;state.offset=0;state.columns=null;state.columnWidths={};state.sortField='';state.sortDir='';clearSheetSelection();drawer.hidden=true;syncReviewControls();renderActiveFilters();load()});",
    "  presetSelect.addEventListener('change',()=>{const choice=presetSelect.value;if(choice.startsWith('custom:')){const saved=savedViewById(choice.slice(7));if(saved){applySavedViewDefinition(saved);clearSheetSelection();drawer.hidden=true;renderActiveFilters();renderViewOptions();load();return}}clearActiveSavedView();state.preset=choice;state.offset=0;state.columns=null;state.columnWidths={};state.formatFills=new Map();state.q='';state.mappingStatus='';state.sourceClassification='';state.reviewReason='';state.sortField='';state.sortDir='';search.value='';mappingStatus.value='';sourceClassification.value='';reviewReason.value='';clearSheetSelection();drawer.hidden=true;syncWorkspaceMode();syncReviewControls();renderActiveFilters();renderViewOptions();load()});",
    "preset change",
)
s = replace_once(
    s,
    "  $('#inventoryViewRefresh').addEventListener('click',()=>load());",
    "  saveViewButton.addEventListener('click',()=>saveCurrentView(false));\n  saveViewAsButton.addEventListener('click',()=>saveCurrentView(true));\n  deleteViewButton.addEventListener('click',()=>deleteCurrentSavedView());\n  $('#inventoryClearAll').addEventListener('click',()=>{state.q='';state.mappingStatus='';state.sourceClassification='';state.reviewReason='';state.sortField='';state.sortDir='';search.value='';mappingStatus.value='';sourceClassification.value='';reviewReason.value='';state.offset=0;clearSheetSelection();drawer.hidden=true;renderActiveFilters();load()});\n  $('#inventoryViewRefresh').addEventListener('click',()=>load());",
    "saved events",
)
p.write_text(s)

p = Path(".github/workflows/validate-inventory-view-engine.yml")
s = p.read_text()
s = replace_once(
    s,
    "      - 'backend/app/inventory_view_engine_verify.py'\n",
    "      - 'backend/app/inventory_view_engine_verify.py'\n      - 'backend/app/inventory_saved_views.py'\n      - 'backend/app/inventory_saved_views_verify.py'\n      - 'backend/alembic/versions/0023_inventory_saved_views.py'\n",
    "workflow backend paths",
)
s = replace_once(
    s,
    "      - 'tests/web/inventory_sheet_formatting_smoke.mjs'\n",
    "      - 'tests/web/inventory_sheet_formatting_smoke.mjs'\n      - 'tests/web/inventory_saved_views_smoke.mjs'\n",
    "workflow test path",
)
s = replace_once(
    s,
    "      - name: Verify reusable Excel renderer\n        run: PYTHONPATH=backend python -m app.tabular_excel_export_verify\n",
    "      - name: Verify Inventory saved view persistence contract\n        run: PYTHONPATH=backend python -m app.inventory_saved_views_verify\n      - name: Verify reusable Excel renderer\n        run: PYTHONPATH=backend python -m app.tabular_excel_export_verify\n",
    "workflow saved verify",
)
s = replace_once(
    s,
    "          assert 'from app.inventory_view_engine import router as inventory_view_router' in main_source\n",
    "          assert 'from app.inventory_view_engine import router as inventory_view_router' in main_source\n          assert 'from app.inventory_saved_views import router as inventory_saved_views_router' in main_source\n",
    "workflow main import check",
)
s = replace_once(
    s,
    "          assert 'app.include_router(inventory_view_router)' in main_source\n",
    "          assert 'app.include_router(inventory_view_router)' in main_source\n          assert 'app.include_router(inventory_saved_views_router)' in main_source\n",
    "workflow main router check",
)
s = replace_once(
    s,
    "      - name: Run Inventory Sheet Formatting smoke\n        run: node tests/web/inventory_sheet_formatting_smoke.mjs\n",
    "      - name: Run Inventory Sheet Formatting smoke\n        run: node tests/web/inventory_sheet_formatting_smoke.mjs\n      - name: Run Inventory Saved Views smoke\n        run: node tests/web/inventory_saved_views_smoke.mjs\n",
    "workflow saved smoke",
)
p.write_text(s)
