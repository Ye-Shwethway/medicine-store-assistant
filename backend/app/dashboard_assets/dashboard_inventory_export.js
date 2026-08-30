(()=>{
  const root=document.querySelector('#msa');
  const panel=root?.querySelector('.view[data-panel="inventory"]');
  if(!root||!panel||panel.dataset.inventoryExcelExport)return;
  panel.dataset.inventoryExcelExport='1';

  const toolbar=panel.querySelector('.inventory-view-toolbar');
  if(!toolbar)return;

  const button=document.createElement('button');
  button.className='secondary';
  button.id='inventoryExportExcel';
  button.type='button';
  button.textContent='Export Excel';
  button.title='Export the full current filtered/sorted view as a formatted Excel workbook (maximum 5,000 rows).';
  const refresh=panel.querySelector('#inventoryViewRefresh');
  if(refresh)toolbar.insertBefore(button,refresh);
  else toolbar.appendChild(button);

  const polish=document.createElement('style');
  polish.textContent=`
    .inventory-mobile-action-strip{display:contents}
    #inventoryMobileTableActionsToggle{display:none}
    @media(max-width:760px){
      .inventory-view-head{gap:8px;margin-bottom:8px}.inventory-view-kicker{display:none}.inventory-view-head h2{margin:0 0 2px}.inventory-view-head .sub{margin:0;font-size:.76rem}.inventory-shadow-banner{padding:8px 10px;border-radius:9px}.inventory-shadow-banner strong{font-size:.78rem}.inventory-shadow-banner span{font-size:.68rem}
      .inventory-view-toolbar{grid-template-columns:minmax(0,1fr) auto;gap:7px;margin-bottom:8px;align-items:end}.inventory-view-toolbar label{gap:4px}.inventory-view-toolbar input,.inventory-view-toolbar select{min-height:38px}.inventory-search-label{grid-column:1/-1}
      #inventoryMobileTableActionsToggle{display:inline-flex;align-items:center;justify-content:center;min-height:38px;padding:6px 10px;font-size:.72rem;grid-column:2}.inventory-saved-view-actions{display:none!important;grid-column:1/-1;width:100%;padding:5px;gap:5px;overflow-x:auto;grid-template-columns:none!important;white-space:nowrap}.inventory-saved-view-actions.is-mobile-open{display:flex!important}.inventory-saved-view-actions button{flex:0 0 auto;min-height:36px!important;padding:6px 10px!important;font-size:.68rem!important}.inventory-saved-view-actions #inventoryDeleteView{grid-column:auto!important}
      .inventory-mobile-action-strip{grid-column:1/-1;display:flex;gap:6px;overflow-x:auto;padding:1px 0 3px;scrollbar-width:none}.inventory-mobile-action-strip::-webkit-scrollbar{display:none}.inventory-mobile-action-strip>button{flex:0 0 auto;min-height:36px!important;padding:6px 10px!important;font-size:.69rem!important}
      .inventory-view-meta{margin:4px 0 6px;font-size:.68rem}.inventory-view-table-wrap{min-height:58dvh;max-height:68dvh;border-radius:8px}.inventory-view-pager{padding-top:7px}.inventory-view-pager button{min-height:36px;padding:6px 9px}
      .inventory-focus-mode{padding:6px!important}.inventory-focus-mode .inventory-view-toolbar{display:flex!important;align-items:center;gap:6px;margin:0 0 5px!important;padding:5px!important;border-radius:8px!important}.inventory-focus-mode .inventory-view-toolbar>label,.inventory-focus-mode .inventory-saved-view-actions,.inventory-focus-mode #inventoryMobileTableActionsToggle{display:none!important}.inventory-focus-mode .inventory-mobile-action-strip{display:flex!important;grid-column:auto;overflow:visible;padding:0;margin:0}.inventory-focus-mode .inventory-mobile-action-strip>button{display:none!important}.inventory-focus-mode .inventory-mobile-action-strip>#inventoryDensityToggle,.inventory-focus-mode .inventory-mobile-action-strip>#inventoryFocusToggle{display:inline-flex!important;min-height:34px!important;padding:5px 9px!important}.inventory-focus-mode .inventory-view-meta{display:none!important}.inventory-focus-mode .inventory-active-filters{display:none!important}.inventory-focus-mode .inventory-review-filters{display:none!important}.inventory-focus-mode .inventory-view-pager{padding-top:4px}.inventory-focus-mode .inventory-view-pager button{min-height:34px}.inventory-focus-mode .inventory-view-table-wrap{min-height:0!important;max-height:none!important}
    }
  `;
  document.head.appendChild(polish);

  const savedActions=panel.querySelector('.inventory-saved-view-actions');
  if(savedActions){
    const actionToggle=document.createElement('button');
    actionToggle.className='secondary';
    actionToggle.id='inventoryMobileTableActionsToggle';
    actionToggle.type='button';
    actionToggle.textContent='Table actions';
    actionToggle.setAttribute('aria-expanded','false');
    savedActions.insertAdjacentElement('beforebegin',actionToggle);
    actionToggle.addEventListener('click',()=>{
      const open=!savedActions.classList.contains('is-mobile-open');
      savedActions.classList.toggle('is-mobile-open',open);
      actionToggle.setAttribute('aria-expanded',String(open));
      actionToggle.textContent=open?'Hide actions':'Table actions';
    });
  }

  const mobileStrip=document.createElement('div');
  mobileStrip.className='inventory-mobile-action-strip';
  const stripIds=['inventoryColumnsToggle','inventoryDensityToggle','inventoryExportExcel','inventoryViewRefresh','inventoryClearAll','inventoryFocusToggle'];
  const firstStripButton=stripIds.map(id=>panel.querySelector(`#${id}`)).find(Boolean);
  if(firstStripButton){
    firstStripButton.insertAdjacentElement('beforebegin',mobileStrip);
    stripIds.forEach(id=>{const item=panel.querySelector(`#${id}`);if(item)mobileStrip.appendChild(item)});
  }

  const tbody=panel.querySelector('#inventoryViewTable tbody');
  if(tbody&&!tbody.dataset.mobileGestureGuard){
    tbody.dataset.mobileGestureGuard='1';
    const touches=new Map();
    const threshold=10;
    tbody.addEventListener('pointerdown',event=>{
      if(event.pointerType!=='touch')return;
      const target=event.target.closest('[data-row-selector],td[data-row-index][data-col-index]');
      if(!target)return;
      touches.set(event.pointerId,{target,x:event.clientX,y:event.clientY,moved:false});
      event.stopPropagation();
    },true);
    tbody.addEventListener('pointermove',event=>{
      const touch=touches.get(event.pointerId);if(!touch)return;
      if(Math.hypot(event.clientX-touch.x,event.clientY-touch.y)>threshold)touch.moved=true;
      event.stopPropagation();
    },true);
    const finishTouch=event=>{
      const touch=touches.get(event.pointerId);if(!touch)return;
      touches.delete(event.pointerId);
      event.stopPropagation();
      if(touch.moved)return;
      const target=touch.target?.isConnected?touch.target:event.target.closest('[data-row-selector],td[data-row-index][data-col-index]');
      if(!target)return;
      target.dispatchEvent(new PointerEvent('pointerdown',{bubbles:true,cancelable:true,button:0,buttons:1,pointerType:'mouse',clientX:event.clientX,clientY:event.clientY}));
    };
    tbody.addEventListener('pointerup',finishTouch,true);
    tbody.addEventListener('pointercancel',event=>{touches.delete(event.pointerId)},true);
  }

  async function resolvePreset(choice){
    if(!choice.startsWith('custom:'))return choice;
    const viewId=choice.slice(7);
    const response=await fetch('/dashboard/api/inventory-view/saved-views',{credentials:'same-origin',headers:{Accept:'application/json'}});
    let data=null;try{data=await response.json()}catch{}
    if(!response.ok)throw new Error(data?.detail||`Unable to resolve custom table: ${response.status}`);
    const saved=(data?.items||[]).find(item=>item.view_id===viewId);
    if(!saved?.base_preset)throw new Error('Saved custom table is no longer available.');
    return saved.base_preset;
  }

  async function exportUrl(){
    const select=panel.querySelector('#inventoryPresetSelect');
    const choice=select?.value||'main-stock';
    const preset=await resolvePreset(choice);
    const params=new URLSearchParams({preset});
    const displayName=(select?.selectedOptions?.[0]?.textContent||'Main Stock').replace(/^Custom\s*·\s*/,'').trim();
    if(displayName)params.set('export_name',displayName);
    const headers=[...panel.querySelectorAll('#inventoryViewTable thead th[data-field]')];
    const fields=headers.map(th=>th.dataset.field).filter(Boolean);
    if(fields.length)params.set('fields',fields.join(','));
    const labels=Object.fromEntries(headers.map(th=>{
      const field=th.dataset.field;
      const label=th.querySelector('.inventory-sort-label')?.textContent?.trim()||th.textContent?.trim()||'';
      return [field,label];
    }).filter(([field,label])=>field&&label));
    if(Object.keys(labels).length)params.set('column_labels',JSON.stringify(labels));

    const q=panel.querySelector('#inventoryViewSearch')?.value.trim();
    const mapping=panel.querySelector('#inventoryMappingStatus')?.value;
    const source=panel.querySelector('#inventorySourceClassification')?.value;
    const reason=panel.querySelector('#inventoryReviewReason')?.value.trim();
    if(q)params.set('q',q);
    if(mapping)params.set('mapping_status',mapping);
    if(preset==='migration-review'&&source)params.set('source_classification',source);
    if(reason)params.set('review_reason',reason);

    const sorted=panel.querySelector('#inventoryViewTable thead th[aria-sort="ascending"], #inventoryViewTable thead th[aria-sort="descending"]');
    if(sorted?.dataset.field){
      params.set('sort_field',sorted.dataset.field);
      params.set('sort_dir',sorted.getAttribute('aria-sort')==='descending'?'desc':'asc');
    }
    return `/dashboard/api/inventory-view/export.xlsx?${params.toString()}`;
  }

  button.addEventListener('click',async()=>{
    const original=button.textContent;
    button.disabled=true;
    button.textContent='Preparing…';
    try{
      const anchor=document.createElement('a');
      anchor.href=await exportUrl();
      anchor.hidden=true;
      anchor.setAttribute('aria-hidden','true');
      document.body.appendChild(anchor);
      anchor.click();
      anchor.remove();
    }catch(err){window.alert(err.message)}finally{button.disabled=false;button.textContent=original}
  });
})();
