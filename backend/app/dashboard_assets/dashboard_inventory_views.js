(()=>{
  const root=document.querySelector('#msa');
  const panel=root?.querySelector('.view[data-panel="inventory"]');
  if(!root||!panel||panel.dataset.inventoryViewEngine)return;
  panel.dataset.inventoryViewEngine='1';

  const state={preset:'main-stock',offset:0,limit:100,q:'',presets:[],registry:[],columns:null,loading:false};
  const esc=value=>String(value??'').replace(/[&<>'"]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;',"'":'&#39;','"':'&quot;'}[c]));
  const api=async path=>{const res=await fetch(path,{credentials:'same-origin',headers:{'Accept':'application/json'}});let data=null;try{data=await res.json()}catch{}if(!res.ok)throw new Error(data?.detail||`Request failed: ${res.status}`);return data};

  panel.innerHTML=`
    <div class="inventory-view-head">
      <div>
        <div class="inventory-view-kicker">Configurable Inventory View</div>
        <h2 id="inventoryViewName">Main Stock</h2>
        <p id="inventoryViewDescription" class="sub">Loading view definition…</p>
      </div>
      <div class="inventory-shadow-banner"><strong>Shadow inventory — not canonical</strong><span>Google Sheet remains operational authority · baseline review in progress</span></div>
    </div>
    <div class="inventory-view-toolbar">
      <label>View<select id="inventoryPresetSelect"><option value="main-stock">Main Stock</option></select></label>
      <label class="inventory-search-label">Search<input id="inventoryViewSearch" type="search" placeholder="Search item or CMS evidence…"></label>
      <button class="secondary" id="inventoryColumnsToggle" type="button">Columns</button>
      <button class="secondary" id="inventoryViewRefresh" type="button">Refresh</button>
    </div>
    <div class="inventory-column-panel" id="inventoryColumnPanel" hidden>
      <div class="inventory-column-panel-head"><div><strong>Visible columns</strong><span>Registry fields only — this does not change database structure.</span></div><button class="secondary" id="inventoryColumnsReset" type="button">Reset preset</button></div>
      <div class="inventory-column-grid" id="inventoryColumnGrid"></div>
      <div class="inventory-column-actions"><button id="inventoryColumnsApply" type="button">Apply columns</button></div>
    </div>
    <div class="inventory-view-meta" id="inventoryViewMeta">Loading…</div>
    <div class="inventory-view-table-wrap">
      <table class="inventory-view-table" id="inventoryViewTable"><thead></thead><tbody></tbody></table>
      <div class="inventory-view-empty" id="inventoryViewEmpty">Loading inventory view…</div>
    </div>
    <div class="inventory-view-pager">
      <button class="secondary" id="inventoryPrev" type="button">← Previous</button>
      <span id="inventoryPageLabel">Rows 1–100</span>
      <button class="secondary" id="inventoryNext" type="button">Next →</button>
    </div>`;

  const $=s=>panel.querySelector(s);
  const table=$('#inventoryViewTable');
  const thead=table.querySelector('thead');
  const tbody=table.querySelector('tbody');
  const empty=$('#inventoryViewEmpty');
  const meta=$('#inventoryViewMeta');
  const presetSelect=$('#inventoryPresetSelect');
  const search=$('#inventoryViewSearch');
  const columnsPanel=$('#inventoryColumnPanel');
  const columnGrid=$('#inventoryColumnGrid');

  function format(value,def){
    if(value===null||value===undefined||value==='')return '—';
    if(def?.data_type==='decimal'){
      const number=Number(value);return Number.isFinite(number)?number.toLocaleString(undefined,{maximumFractionDigits:3}):String(value);
    }
    if(def?.data_type==='date'){
      const d=new Date(`${value}T00:00:00`);return Number.isNaN(d.getTime())?String(value):d.toLocaleDateString();
    }
    return String(value);
  }

  function cellClass(field,value){
    if(field==='mapping_status'||field==='source_classification')return ` inventory-status-cell status-${String(value||'none').toLowerCase().replace(/[^a-z0-9]+/g,'-')}`;
    if(field.endsWith('_qty')||field.includes('price'))return ' inventory-number-cell';
    return '';
  }

  function renderColumns(columns){
    thead.innerHTML=`<tr>${columns.map(col=>`<th style="${col.width?`min-width:${Number(col.width)}px`:''}">${esc(col.label)}</th>`).join('')}</tr>`;
  }

  function renderRows(columns,items){
    tbody.innerHTML='';
    if(!items.length){empty.textContent='No rows match this view and search.';empty.hidden=false;table.hidden=true;return;}
    empty.hidden=true;table.hidden=false;
    const fragment=document.createDocumentFragment();
    for(const item of items){
      const tr=document.createElement('tr');
      tr.innerHTML=columns.map(col=>{const value=item[col.field];const text=format(value,col.field_definition);return `<td class="${cellClass(col.field,value)}" title="${esc(text)}">${esc(text)}</td>`}).join('');
      fragment.appendChild(tr);
    }
    tbody.appendChild(fragment);
  }

  function renderColumnPicker(view){
    const defaults=new Set(view.columns.map(c=>c.field));
    const selected=new Set(state.columns||[...defaults]);
    const presetOrder=view.columns.map(c=>c.field);
    const extras=state.registry.map(f=>f.key).filter(k=>!presetOrder.includes(k));
    const ordered=[...presetOrder,...extras];
    const defs=new Map(state.registry.map(f=>[f.key,f]));
    columnGrid.innerHTML=ordered.map(key=>{const def=defs.get(key);if(!def)return '';return `<label class="inventory-column-option"><input type="checkbox" value="${esc(key)}" ${selected.has(key)?'checked':''}><span><strong>${esc(def.label)}</strong><small>${esc(def.kind)}</small></span></label>`}).join('');
  }

  async function loadDefinitions(){
    const [presets,registry]=await Promise.all([api('/dashboard/api/inventory-view/presets'),api('/dashboard/api/inventory-view/registry')]);
    state.presets=presets.items||[];state.registry=registry.fields||[];
    presetSelect.innerHTML=state.presets.map(view=>`<option value="${esc(view.view_id)}">${esc(view.name)}</option>`).join('');
    presetSelect.value=state.preset;
  }

  async function load(){
    if(state.loading)return;state.loading=true;
    empty.hidden=false;empty.textContent='Loading inventory view…';table.hidden=true;meta.textContent='Loading…';
    try{
      if(!state.presets.length)await loadDefinitions();
      const params=new URLSearchParams({preset:state.preset,limit:String(state.limit),offset:String(state.offset)});
      if(state.q)params.set('q',state.q);
      if(state.columns?.length)params.set('fields',state.columns.join(','));
      const data=await api('/dashboard/api/inventory-view/rows?'+params.toString());
      const view=data.view;const columns=data.columns||[];const items=data.items||[];
      $('#inventoryViewName').textContent=view.name;
      $('#inventoryViewDescription').textContent=view.description;
      renderColumns(columns);renderRows(columns,items);renderColumnPicker(view);
      meta.textContent=`${view.row_grain.replaceAll('_',' ')} · Store ${view.store_scope} · ${items.length.toLocaleString()} rows shown · Read-only shadow projection`;
      const start=items.length?state.offset+1:0;const end=state.offset+items.length;
      $('#inventoryPageLabel').textContent=`Rows ${start.toLocaleString()}–${end.toLocaleString()}`;
      $('#inventoryPrev').disabled=state.offset===0;
      $('#inventoryNext').disabled=items.length<state.limit;
    }catch(err){
      empty.hidden=false;table.hidden=true;empty.textContent=err.message;meta.textContent='Unable to load configurable inventory view.';
    }finally{state.loading=false;}
  }

  let timer=null;
  presetSelect.addEventListener('change',()=>{state.preset=presetSelect.value;state.offset=0;state.columns=null;load()});
  search.addEventListener('input',()=>{clearTimeout(timer);timer=setTimeout(()=>{state.q=search.value.trim();state.offset=0;load()},180)});
  $('#inventoryViewRefresh').addEventListener('click',()=>load());
  $('#inventoryColumnsToggle').addEventListener('click',()=>{columnsPanel.hidden=!columnsPanel.hidden});
  $('#inventoryColumnsReset').addEventListener('click',()=>{state.columns=null;columnsPanel.hidden=true;load()});
  $('#inventoryColumnsApply').addEventListener('click',()=>{const selected=[...columnGrid.querySelectorAll('input:checked')].map(input=>input.value);if(!selected.length)return;state.columns=selected;state.offset=0;columnsPanel.hidden=true;load()});
  $('#inventoryPrev').addEventListener('click',()=>{state.offset=Math.max(0,state.offset-state.limit);load()});
  $('#inventoryNext').addEventListener('click',()=>{state.offset+=state.limit;load()});
  root.addEventListener('click',event=>{const nav=event.target.closest('.nav-btn[data-view="inventory"]');if(nav)setTimeout(load,0)});

  load();
})();
