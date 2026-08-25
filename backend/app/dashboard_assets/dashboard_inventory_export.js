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
