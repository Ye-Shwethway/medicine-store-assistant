from pathlib import Path

export_path = Path('backend/app/inventory_view_export.py')
text = export_path.read_text(encoding='utf-8')
old = '''def _excel_columns(columns: list[ViewColumn]) -> tuple[ExcelColumn, ...]:
    return tuple(
        ExcelColumn(
            key=column.field,
            label=column.label or FIELD_REGISTRY[column.field].label,
            data_type=FIELD_REGISTRY[column.field].data_type,
            preferred_width=(column.width / 7.0) if column.width else None,
        )
        for column in columns
    )
'''
new = '''def _inventory_excel_number_format(field: str) -> str | None:
    if field.endswith("_qty"):
        return "0"
    if "price" in field:
        return "0.00"
    if field == "expiry_date":
        return "mmm-yy"
    return None


def _excel_columns(columns: list[ViewColumn]) -> tuple[ExcelColumn, ...]:
    return tuple(
        ExcelColumn(
            key=column.field,
            label=column.label or FIELD_REGISTRY[column.field].label,
            data_type=FIELD_REGISTRY[column.field].data_type,
            preferred_width=(column.width / 7.0) if column.width else None,
            number_format=_inventory_excel_number_format(column.field),
        )
        for column in columns
    )
'''
if old in text:
    export_path.write_text(text.replace(old, new, 1), encoding='utf-8')
elif '_inventory_excel_number_format' not in text:
    raise SystemExit('inventory export anchor not found')

js_path = Path('backend/app/dashboard_assets/dashboard_inventory_views.js')
js = js_path.read_text(encoding='utf-8')
state_anchor = "  const state={preset:'main-stock',offset:0,limit:100,q:'',mappingStatus:'',sourceClassification:'',reviewReason:'',sortField:'',sortDir:'',presets:[],registry:[],columns:null,columnWidths:{},loading:false,items:[],columnsRendered:[],selected:new Set(),drawerIndex:null,focusMode:false,density:'comfortable'};"
state_replacement = """  const DATE_FORMAT_KEY='msa.inventory.dateFormat';
  const DATE_FORMATS=new Set(['dd-mm-yyyy','mm-dd-yyyy','yyyy-mm-dd','dd-mmm-yyyy']);
  const storedDateFormat=(()=>{try{const value=localStorage.getItem(DATE_FORMAT_KEY);return DATE_FORMATS.has(value)?value:'dd-mm-yyyy'}catch{return 'dd-mm-yyyy'}})();
  const state={preset:'main-stock',offset:0,limit:100,q:'',mappingStatus:'',sourceClassification:'',reviewReason:'',sortField:'',sortDir:'',presets:[],registry:[],columns:null,columnWidths:{},loading:false,items:[],columnsRendered:[],selected:new Set(),drawerIndex:null,focusMode:false,density:'comfortable',dateFormat:storedDateFormat};"""
if state_anchor in js:
    js = js.replace(state_anchor, state_replacement, 1)
elif 'DATE_FORMAT_KEY' not in js:
    raise SystemExit('state anchor not found')

search_anchor = '      <label class="inventory-search-label">Search<input id="inventoryViewSearch" type="search" placeholder="Search item or CMS evidence…"></label>'
if 'inventoryDateFormat' not in js:
    if search_anchor not in js:
        raise SystemExit('toolbar anchor not found')
    js = js.replace(search_anchor, search_anchor + '\n      <label>Date format<select id="inventoryDateFormat"><option value="dd-mm-yyyy">DD-MM-YYYY</option><option value="mm-dd-yyyy">MM-DD-YYYY</option><option value="yyyy-mm-dd">YYYY-MM-DD</option><option value="dd-mmm-yyyy">DD-MMM-YYYY</option></select></label>', 1)

refs_anchor = "densityToggle=$('#inventoryDensityToggle');"
if "dateFormatSelect=$('#inventoryDateFormat')" not in js:
    if refs_anchor not in js:
        raise SystemExit('refs anchor not found')
    js = js.replace(refs_anchor, "densityToggle=$('#inventoryDensityToggle'),dateFormatSelect=$('#inventoryDateFormat');", 1)

old_format = "  function format(value,def,field){if(field==='review_reason')return reasonEvidence(value).summary;if(value===null||value===undefined||value==='')return '—';if(def?.data_type==='decimal'){const n=Number(value);return Number.isFinite(n)?n.toLocaleString(undefined,{maximumFractionDigits:3}):String(value)}if(def?.data_type==='date'){const d=new Date(`${value}T00:00:00`);return Number.isNaN(d.getTime())?String(value):d.toLocaleDateString()}return String(value)}"
new_format = """  function formatDate(value){const raw=String(value??'');const match=/^(\\d{4})-(\\d{2})-(\\d{2})$/.exec(raw);if(!match)return raw;const [,year,month,day]=match;if(state.dateFormat==='mm-dd-yyyy')return `${month}-${day}-${year}`;if(state.dateFormat==='yyyy-mm-dd')return `${year}-${month}-${day}`;if(state.dateFormat==='dd-mmm-yyyy'){const names=['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'];return `${day}-${names[Number(month)-1]||month}-${year}`}return `${day}-${month}-${year}`}
  function format(value,def,field){if(field==='review_reason')return reasonEvidence(value).summary;if(value===null||value===undefined||value==='')return '—';if(def?.data_type==='decimal'){const n=Number(value);return Number.isFinite(n)?n.toLocaleString(undefined,{maximumFractionDigits:3}):String(value)}if(def?.data_type==='date')return formatDate(value);return String(value)}"""
if 'function formatDate(value)' not in js:
    if old_format not in js:
        raise SystemExit('format anchor not found')
    js = js.replace(old_format, new_format, 1)

drawer_anchor = "${drawerPair('Expiry','Source',item.expiry_date,'Shadow',item.expiry_date)}"
if drawer_anchor in js:
    js = js.replace(drawer_anchor, "${drawerPair('Expiry','Source',formatDate(item.expiry_date),'Shadow',formatDate(item.expiry_date))}", 1)

listener_anchor = "  densityToggle.addEventListener('click',toggleDensity);"
if "dateFormatSelect.addEventListener('change'" not in js:
    if listener_anchor not in js:
        raise SystemExit('listener anchor not found')
    listener_replacement = """  dateFormatSelect.value=state.dateFormat;
  dateFormatSelect.addEventListener('change',()=>{state.dateFormat=DATE_FORMATS.has(dateFormatSelect.value)?dateFormatSelect.value:'dd-mm-yyyy';try{localStorage.setItem(DATE_FORMAT_KEY,state.dateFormat)}catch{};if(state.columnsRendered.length)renderRows(state.columnsRendered,state.items);if(state.drawerIndex!==null)openDrawer(state.drawerIndex)});
  densityToggle.addEventListener('click',toggleDensity);"""
    js = js.replace(listener_anchor, listener_replacement, 1)

js_path.write_text(js, encoding='utf-8')
print('inventory_format_patch=pass')
