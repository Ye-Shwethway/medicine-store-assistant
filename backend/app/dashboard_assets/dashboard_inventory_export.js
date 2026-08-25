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

  function exportUrl(){
    const preset=panel.querySelector('#inventoryPresetSelect')?.value||'main-stock';
    const params=new URLSearchParams({preset});
    const fields=[...panel.querySelectorAll('#inventoryViewTable thead th[data-field]')]
      .map(th=>th.dataset.field)
      .filter(Boolean);
    if(fields.length)params.set('fields',fields.join(','));

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

  button.addEventListener('click',()=>{
    const anchor=document.createElement('a');
    anchor.href=exportUrl();
    anchor.hidden=true;
    anchor.setAttribute('aria-hidden','true');
    document.body.appendChild(anchor);
    anchor.click();
    anchor.remove();
  });
})();
