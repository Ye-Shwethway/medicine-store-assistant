import assert from 'node:assert/strict';
import path from 'node:path';
import { chromium } from 'playwright';

const root=process.cwd();
const script=path.join(root,'backend/app/dashboard_assets/dashboard_inventory_views.js');
const stylesheet=path.join(root,'backend/app/dashboard_assets/dashboard_inventory_views.css');
const browser=await chromium.launch({headless:true});
const page=await browser.newPage({viewport:{width:390,height:844}});

await page.setContent(`<main id="msa"><button class="nav-btn" data-view="inventory">Inventory</button><button id="aiWorkspaceNav" type="button">AI Workspace</button><textarea id="aiMessageInput"></textarea><section class="view" data-panel="inventory"><div id="legacyInventorySubtree">legacy</div></section></main>`);
await page.addStyleTag({path:stylesheet});
await page.evaluate(()=>{
  window.__inventoryRequests=[];
  window.__lastReviewContextBody=null;
  window.__aiNavClicks=0;
  document.querySelector('#aiWorkspaceNav').addEventListener('click',()=>{window.__aiNavClicks+=1});
  const field=(key,label,kind='ENTITY_FIELD',data_type='string')=>({key,label,kind,data_type,editable:false,description:''});
  window.__registry=[field('display_no','No.','DISPLAY_HELPER','integer'),field('product_id','Product ID'),field('local_item_name','Items'),field('expiry_date','Expiry Date','ENTITY_FIELD','date'),field('unit','Unit'),field('opening_qty','Opening Qty','COMPUTED_FIELD','decimal'),field('current_qty','Current Qty','COMPUTED_FIELD','decimal'),field('cms_code','CMS Code'),field('cms_name','CMS Name'),field('mapping_status','Mapping Status'),field('catalogue_price','Current Catalogue Price','COMPUTED_FIELD','decimal'),field('accepted_operational_price','Accepted Store Price','ENTITY_FIELD','decimal'),field('source_row_no','Source Row','DISPLAY_HELPER','integer'),field('source_current_qty','Source Current Qty','DISPLAY_HELPER','decimal'),field('source_classification','Source Class','DISPLAY_HELPER'),field('review_reason','Review Reason','DISPLAY_HELPER')];
  const col=(field,label,width=120)=>({field,label,width});
  window.__presets=[
    {view_id:'main-stock',name:'Main Stock',preset_type:'MAIN_STOCK_COMPATIBILITY',provider:'lot_balance',row_grain:'PRODUCT_LOT',store_scope:'MAIN',system_preset:true,description:'Main Stock projection.',columns:[col('display_no','No.',70),col('local_item_name','Items',260),col('current_qty','Current Qty'),col('mapping_status','Mapping Status')]},
    {view_id:'migration-review',name:'Migration Review',preset_type:'MIGRATION_REVIEW',provider:'migration_review',row_grain:'SOURCE_MAIN_ROW',store_scope:'MAIN',system_preset:true,description:'Source versus shadow review.',columns:[col('source_row_no','Source Row',90),col('local_item_name','Local Item',260),col('source_current_qty','Source Current Qty',140),col('current_qty','Shadow Current Qty',140),col('source_classification','Source Class'),col('review_reason','Review Reason',300)]},
    {view_id:'cms-mapping-review',name:'CMS Mapping Review',preset_type:'CMS_MAPPING_REVIEW',provider:'cms_mapping_review',row_grain:'PRODUCT_CMS_MAPPING',store_scope:'ALL',system_preset:true,description:'Current Product to CMS mapping review state.',columns:[col('local_item_name','Local Item',260),col('cms_code','CMS Code'),col('cms_name','CMS Name',240),col('mapping_status','Mapping Status',160),col('catalogue_price','Current Catalogue Price',150),col('accepted_operational_price','Accepted Store Price',150),col('review_reason','Review Reason',300)]}
  ];
  const response=data=>new Response(JSON.stringify(data),{status:200,headers:{'Content-Type':'application/json'}});
  window.fetch=async (input,opts={})=>{
    const url=typeof input==='string'?input:input.url;window.__inventoryRequests.push(url);
    if(url==='/dashboard/api/inventory-view/presets')return response({items:window.__presets});
    if(url==='/dashboard/api/inventory-view/registry')return response({fields:window.__registry});
    if(url==='/dashboard/api/inventory-view/review-context'){
      const body=JSON.parse(opts.body||'{}');window.__lastReviewContextBody=body;
      const reviewReason=JSON.stringify({category:'CONTINUITY_EXACT_NAME_PRICE_SAME',previous_price:'12.500',catalogue_price:'12.500'});
      return response({context_type:'INVENTORY_REVIEW_CONTEXT_V1',context_origin:'SERVER_REHYDRATED_INVENTORY_VIEW',view:{view_id:'cms-mapping-review',name:'CMS Mapping Review',row_grain:'PRODUCT_CMS_MAPPING',store_scope:'ALL',columns:[{field:'local_item_name',label:'Local Item',data_type:'string'},{field:'cms_code',label:'CMS Code',data_type:'string'},{field:'mapping_status',label:'Mapping Status',data_type:'string'},{field:'review_reason',label:'Review Reason',data_type:'string'}]},filters:{q:null,mapping_status:null,source_classification:null,review_reason:null},page:{limit:100,offset:0},selected_indices:body.selected_indices,selected_count:1,rows:[{local_item_name:'Metformin 500mg',cms_code:'M500',mapping_status:'REVIEW_REQUIRED',review_reason:reviewReason}],read_only:true,database_canonical:false,migration_baseline_accepted:false});
    }
    if(url.startsWith('/dashboard/api/inventory-view/rows?')){
      const parsed=new URL(url,'https://msa.test'),preset=parsed.searchParams.get('preset')||'main-stock',view=window.__presets.find(x=>x.view_id===preset),requested=parsed.searchParams.get('fields')?.split(',').filter(Boolean),columns=(requested?.length?requested.map(key=>({field:key,label:window.__registry.find(f=>f.key===key)?.label||key,width:null})):view.columns).map(c=>({...c,field_definition:window.__registry.find(f=>f.key===c.field)}));
      let source;
      if(preset==='main-stock')source={display_no:1,product_id:'p-main',local_item_name:'10cc Syringe',current_qty:'120.000',mapping_status:'REVIEW_REQUIRED'};
      else if(preset==='migration-review')source={source_row_no:41,local_item_name:'Bandage- Soft Bandage 6"',source_current_qty:'12.000',current_qty:'0.000',source_classification:'REVIEW',mapping_status:'REVIEW_REQUIRED',review_reason:'duplicate Product+Expiry source key'};
      else source={product_id:'p-met',local_item_name:'Metformin 500mg',cms_code:'M500',cms_name:'Metformin 500mg Tablet',mapping_status:'REVIEW_REQUIRED',catalogue_price:'12.500',accepted_operational_price:null,review_reason:JSON.stringify({category:'CONTINUITY_EXACT_NAME_PRICE_SAME',previous_price:'12.500',catalogue_price:'12.500'})};
      const item={...Object.fromEntries(columns.map(c=>[c.field,source[c.field]??null])),product_id:source.product_id,source_row_no:source.source_row_no,mapping_status:source.mapping_status,source_classification:source.source_classification,review_reason:source.review_reason,source_current_qty:source.source_current_qty,current_qty:source.current_qty,cms_code:source.cms_code,cms_name:source.cms_name,catalogue_price:source.catalogue_price,accepted_operational_price:source.accepted_operational_price,local_item_name:source.local_item_name};
      return response({view,columns,items:[item],count:1,limit:100,offset:0,read_only:true,database_canonical:false,migration_baseline_accepted:false});
    }
    return new Response('{}',{status:500});
  };
});

await page.addScriptTag({path:script});
await page.getByText('Shadow inventory — not canonical').waitFor({state:'visible'});
assert.equal(await page.locator('#legacyInventorySubtree').count(),0);
await page.getByText('10cc Syringe').waitFor({state:'visible'});
assert.equal(await page.locator('#inventoryViewTable').count(),1);
assert.equal(await page.locator('#inventoryReviewFilters').isHidden(),true);

await page.locator('#inventoryPresetSelect').selectOption('migration-review');
await page.getByText('Bandage- Soft Bandage 6"').waitFor({state:'visible'});
assert.equal(await page.locator('#inventoryReviewFilters').isVisible(),true);
assert.equal(await page.locator('#inventoryClassificationLabel').isVisible(),true);
assert.ok((await page.locator('#inventoryViewTable tbody tr').first().getAttribute('class')).includes('inventory-row-review'));
assert.ok((await page.locator('#inventoryViewTable tbody tr').first().textContent()).includes('duplicate Product+Expiry source key'),'plain-text Migration Review reasons stay readable');

await page.locator('#inventoryMappingStatus').selectOption('REVIEW_REQUIRED');
await page.locator('#inventorySourceClassification').selectOption('REVIEW');
await page.locator('#inventoryReviewReason').fill('duplicate');
await page.waitForTimeout(260);
let request=await page.evaluate(()=>window.__inventoryRequests.filter(x=>x.includes('/rows?')).at(-1));
assert.ok(request.includes('mapping_status=REVIEW_REQUIRED'));
assert.ok(request.includes('source_classification=REVIEW'));
assert.ok(request.includes('review_reason=duplicate'));

await page.locator('.inventory-row-check').check();
assert.equal(await page.locator('#inventorySelectionBar').isVisible(),true);
assert.ok((await page.locator('#inventorySelectionCount').textContent()).includes('1 selected'));
assert.equal(await page.getByRole('button',{name:'Ask AI'}).isVisible(),true);
await page.locator('#inventoryViewTable tbody tr').first().click();
assert.equal(await page.locator('#inventoryReviewDrawer').isVisible(),true);
assert.ok((await page.locator('#inventoryDrawerBody').textContent()).includes('Source'));
assert.ok((await page.locator('#inventoryDrawerBody').textContent()).includes('Shadow'));
await page.locator('#inventoryDrawerClose').click();

await page.getByRole('button',{name:'Columns'}).click();
await page.locator('#inventoryColumnGrid input:checked').evaluateAll(inputs=>inputs.forEach(input=>input.checked=false));
await page.locator('#inventoryColumnGrid input[value="local_item_name"]').check();
await page.locator('#inventoryColumnGrid input[value="review_reason"]').check();
await page.getByRole('button',{name:'Apply columns'}).click();
await page.waitForFunction(()=>[...document.querySelectorAll('#inventoryViewTable thead th')].slice(1).map(x=>x.textContent).join('|')==='Items|Review Reason');

await page.locator('#inventoryPresetSelect').selectOption('cms-mapping-review');
await page.getByRole('cell',{name:'Metformin 500mg',exact:true}).waitFor({state:'visible'});
assert.equal(await page.locator('#inventoryClassificationLabel').isHidden(),true);
const reasonCell=page.locator('#inventoryViewTable tbody tr').first().locator('td').last();
assert.equal((await reasonCell.textContent()).trim(),'Continuity: exact name, same price');
assert.ok(!(await reasonCell.textContent()).includes('{'),'structured review reason must not render as raw JSON');
await page.locator('#inventoryViewTable tbody tr').first().click();
const drawerText=await page.locator('#inventoryDrawerBody').textContent();
assert.ok(drawerText.includes('Current catalogue price'));
assert.ok(drawerText.includes('Accepted store price'));
assert.ok(drawerText.includes('Continuity: exact name, same price'));
assert.ok(drawerText.includes('Previous Price'));
assert.ok(!drawerText.includes('CONTINUITY_EXACT_NAME_PRICE_SAME'),'drawer must humanize category token');
const drawerBox=await page.locator('#inventoryReviewDrawer').boundingBox();assert.ok(drawerBox&&drawerBox.width<=390);
await page.locator('#inventoryDrawerClose').click();

await page.locator('.inventory-row-check').check();
await page.getByRole('button',{name:'Ask AI'}).click();
await page.waitForFunction(()=>document.querySelector('#aiMessageInput').value.includes('Review these 1 selected rows from CMS Mapping Review.'));
const handoff=await page.evaluate(()=>({body:window.__lastReviewContextBody,navClicks:window.__aiNavClicks,draft:document.querySelector('#aiMessageInput').value,requests:window.__inventoryRequests}));
assert.equal(handoff.navClicks,1);
assert.equal(handoff.body.preset,'cms-mapping-review');
assert.deepEqual(handoff.body.selected_indices,[0]);
assert.equal(handoff.body.offset,0);
assert.equal(handoff.body.limit,100);
assert.ok(!JSON.stringify(handoff.body).includes('Metformin 500mg'),'client sends selection coordinates, not row facts');
assert.ok(handoff.draft.includes('server-rehydrated shadow review evidence'));
assert.ok(handoff.draft.includes('Continuity: exact name, same price'));
assert.ok(!handoff.draft.includes('CONTINUITY_EXACT_NAME_PRICE_SAME'));
assert.ok(!handoff.requests.some(url=>url.includes('/messages')),'Ask AI must prefill only and must not auto-send/model-call');

assert.equal(await page.locator('#inventoryViewRefresh').isVisible(),true);
const overflow=await page.locator('.inventory-view-table-wrap').evaluate(el=>getComputedStyle(el).overflow);assert.ok(overflow==='auto'||overflow==='scroll');
const banner=await page.locator('.inventory-shadow-banner').boundingBox();assert.ok(banner&&banner.width<=390);

await browser.close();
console.log('inventory_review_workspace_smoke=pass viewport=390x844 filters=pass selection=pass drawer=pass human_review_reason=pass ask_ai_context=pass auto_send=false presets=3');
