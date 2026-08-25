import assert from 'node:assert/strict';
import path from 'node:path';
import { chromium } from 'playwright';

const root=process.cwd();
const script=path.join(root,'backend/app/dashboard_assets/dashboard_inventory_views.js');
const stylesheet=path.join(root,'backend/app/dashboard_assets/dashboard_inventory_views.css');
const browser=await chromium.launch({headless:true});
const page=await browser.newPage({viewport:{width:390,height:844}});

await page.setContent(`<main id="msa"><button class="nav-btn" data-view="inventory">Inventory</button><button id="aiWorkspaceNav" type="button">AI Workspace</button><button class="ai-workspace-tab" id="aiChatTab" data-ai-tab="chat" type="button">Chat</button><button class="ai-workspace-tab" id="aiMultiTab" type="button" hidden>Multi-Agent</button><article class="ai-chat-panel"><select id="aiAgentSelect"><option value="agent-a">Agent A</option></select><button id="aiNewConversation" type="button">New chat</button><div class="ai-conversation-item active" data-ai-conversation-row="old-chat"></div><div id="aiChatThread">Existing</div><form id="aiChatForm"><textarea id="aiMessageInput"></textarea><button type="submit">Send</button></form></article><section class="view" data-panel="inventory"></section></main>`);
await page.addStyleTag({path:stylesheet});
await page.evaluate(()=>{
  window.__requests=[];
  window.__reviewBody=null;
  const field=(key,label,kind='ENTITY_FIELD',data_type='string')=>({key,label,kind,data_type,editable:false,description:''});
  window.__registry=[field('product_id','Product ID'),field('local_item_name','Local Item'),field('unit','Unit'),field('cms_code','CMS Code'),field('cms_name','CMS Name'),field('mapping_status','Mapping Status'),field('catalogue_price','Current Catalogue Price','COMPUTED_FIELD','decimal'),field('accepted_operational_price','Accepted Store Price','ENTITY_FIELD','decimal'),field('review_reason','Review Reason','DISPLAY_HELPER')];
  const col=(field,label,width=120)=>({field,label,width});
  window.__presets=[{view_id:'cms-mapping-review',name:'CMS Mapping Review',preset_type:'CMS_MAPPING_REVIEW',provider:'cms_mapping_review',row_grain:'PRODUCT_CMS_MAPPING',store_scope:'ALL',system_preset:true,description:'Mapping review.',columns:[col('local_item_name','Local Item',220),col('cms_code','CMS Code'),col('catalogue_price','Current Catalogue Price',150),col('mapping_status','Mapping Status',160),col('review_reason','Review Reason',260)]}];
  const response=data=>new Response(JSON.stringify(data),{status:200,headers:{'Content-Type':'application/json'}});
  const rows=[
    {product_id:'p-a',local_item_name:'Alpha Tablet',cms_code:'A1',catalogue_price:'8.000',mapping_status:'REVIEW_REQUIRED',review_reason:'alpha evidence'},
    {product_id:'p-z',local_item_name:'Zebra Tablet',cms_code:'Z9',catalogue_price:'20.000',mapping_status:'REVIEW_REQUIRED',review_reason:'zebra evidence'},
  ];
  window.fetch=async (input,opts={})=>{
    const url=typeof input==='string'?input:input.url;window.__requests.push(url);
    if(url==='/dashboard/api/inventory-view/presets')return response({items:window.__presets});
    if(url==='/dashboard/api/inventory-view/registry')return response({fields:window.__registry});
    if(url==='/dashboard/api/inventory-view/review-context'){
      const body=JSON.parse(opts.body||'{}');window.__reviewBody=body;
      const ordered=body.sort_field==='local_item_name'&&body.sort_dir==='desc'?[...rows].reverse():[...rows];
      const selected=body.selected_indices.map(index=>ordered[index]);
      return response({context_type:'INVENTORY_REVIEW_CONTEXT_V1',context_origin:'SERVER_REHYDRATED_INVENTORY_VIEW',view:{view_id:'cms-mapping-review',name:'CMS Mapping Review',row_grain:'PRODUCT_CMS_MAPPING',store_scope:'ALL',columns:window.__presets[0].columns.map(c=>({field:c.field,label:c.label,data_type:window.__registry.find(f=>f.key===c.field)?.data_type||'string'}))},filters:{q:null,mapping_status:null,source_classification:null,review_reason:null},sort:{field:body.sort_field,direction:body.sort_dir},page:{limit:100,offset:0},selected_indices:body.selected_indices,selected_count:selected.length,rows:selected,read_only:true,database_canonical:false,migration_baseline_accepted:false});
    }
    if(url.startsWith('/dashboard/api/inventory-view/rows?')){
      const parsed=new URL(url,'https://msa.test');
      const sortField=parsed.searchParams.get('sort_field');
      const sortDir=parsed.searchParams.get('sort_dir');
      let ordered=[...rows];
      if(sortField==='local_item_name')ordered.sort((a,b)=>a.local_item_name.localeCompare(b.local_item_name)*(sortDir==='desc'?-1:1));
      if(sortField==='catalogue_price')ordered.sort((a,b)=>(Number(a.catalogue_price)-Number(b.catalogue_price))*(sortDir==='desc'?-1:1));
      const view=window.__presets[0];
      const columns=view.columns.map(c=>({...c,sortable:true,field_definition:window.__registry.find(f=>f.key===c.field)}));
      return response({view,columns,items:ordered,count:ordered.length,limit:100,offset:0,filters:{q:null,mapping_status:null,source_classification:null,review_reason:null},sort:{field:sortField,direction:sortDir},read_only:true,database_canonical:false,migration_baseline_accepted:false});
    }
    if(url==='/dashboard/api/ai-workspace/chat/agents')return response({items:[{agent_id:'agent-a',display_name:'Agent A',call_name:'Agent A'}]});
    return response({items:[]});
  };
});

await page.addScriptTag({path:script});
await page.locator('#inventoryPresetSelect').selectOption('cms-mapping-review');
await page.getByText('Alpha Tablet').waitFor({state:'visible'});

const nameSort=page.locator('[data-sort-field="local_item_name"]');
assert.equal(await nameSort.isVisible(),true);
assert.equal(await page.locator('th[data-field="local_item_name"]').getAttribute('aria-sort'),'none');

await nameSort.click();
await page.waitForFunction(()=>window.__requests.filter(x=>x.includes('/rows?')).at(-1)?.includes('sort_field=local_item_name')&&window.__requests.filter(x=>x.includes('/rows?')).at(-1)?.includes('sort_dir=asc'));
assert.equal(await page.locator('th[data-field="local_item_name"]').getAttribute('aria-sort'),'ascending');
let names=await page.locator('#inventoryViewTable tbody tr td[data-field="local_item_name"]').allTextContents();
assert.deepEqual(names.map(x=>x.trim()),['Alpha Tablet','Zebra Tablet']);
assert.ok((await page.locator('#inventoryActiveFilters').textContent()).includes('Sort:'));
assert.ok((await page.locator('#inventoryActiveFilters').textContent()).includes('Local Item ↑'));

await page.locator('[data-sort-field="local_item_name"]').click();
await page.waitForFunction(()=>window.__requests.filter(x=>x.includes('/rows?')).at(-1)?.includes('sort_dir=desc'));
assert.equal(await page.locator('th[data-field="local_item_name"]').getAttribute('aria-sort'),'descending');
names=await page.locator('#inventoryViewTable tbody tr td[data-field="local_item_name"]').allTextContents();
assert.deepEqual(names.map(x=>x.trim()),['Zebra Tablet','Alpha Tablet']);

await page.locator('.inventory-row-check').first().check();
await page.getByRole('button',{name:'Ask AI'}).click();
await page.locator('.inventory-ai-dialog-backdrop').waitFor({state:'visible'});
const reviewBody=await page.evaluate(()=>window.__reviewBody);
assert.equal(reviewBody.sort_field,'local_item_name');
assert.equal(reviewBody.sort_dir,'desc');
assert.deepEqual(reviewBody.selected_indices,[0]);
assert.ok(!JSON.stringify(reviewBody).includes('Zebra Tablet'),'browser sends sorted coordinates, not row facts');
await page.getByRole('button',{name:'Cancel'}).click();

await page.getByRole('button',{name:'Clear Sort'}).click();
await page.waitForFunction(()=>!window.__requests.filter(x=>x.includes('/rows?')).at(-1)?.includes('sort_field='));
assert.equal(await page.locator('th[data-field="local_item_name"]').getAttribute('aria-sort'),'none');
assert.ok(!(await page.locator('#inventoryActiveFilters').textContent()).includes('Sort:'));

await page.locator('[data-sort-field="catalogue_price"]').click();
await page.waitForFunction(()=>window.__requests.filter(x=>x.includes('/rows?')).at(-1)?.includes('sort_field=catalogue_price'));
const priceRequest=await page.evaluate(()=>window.__requests.filter(x=>x.includes('/rows?')).at(-1));
assert.ok(priceRequest.includes('sort_dir=asc'));

await browser.close();
console.log('inventory_server_sorting_smoke=pass header_toggle=pass aria_sort=pass active_sort_chip=pass review_context_sort_parity=pass client_row_facts=false');