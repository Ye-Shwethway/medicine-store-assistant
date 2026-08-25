import assert from 'node:assert/strict';
import path from 'node:path';
import { chromium } from 'playwright';

const root=process.cwd();
const script=path.join(root,'backend/app/dashboard_assets/dashboard_inventory_views.js');
const stylesheet=path.join(root,'backend/app/dashboard_assets/dashboard_inventory_views.css');
const browser=await chromium.launch({headless:true});
const page=await browser.newPage({viewport:{width:390,height:844}});

await page.setContent(`<main id="msa"><button class="nav-btn" data-view="inventory">Inventory</button><button id="aiWorkspaceNav">AI Workspace</button><button class="ai-workspace-tab" data-ai-tab="chat">Chat</button><button id="aiMultiTab" hidden>Multi-Agent</button><select id="aiAgentSelect"><option value="a">A</option></select><button id="aiNewConversation">New chat</button><div class="ai-conversation-item active" data-ai-conversation-row="old"></div><div id="aiChatThread"></div><form id="aiChatForm"><textarea id="aiMessageInput"></textarea></form><section class="view" data-panel="inventory"></section></main>`);
await page.addStyleTag({path:stylesheet});
await page.evaluate(()=>{
  window.__inventoryRequests=[];
  const field=(key,label,kind='ENTITY_FIELD',data_type='string')=>({key,label,kind,data_type,editable:false,description:''});
  window.__registry=[field('display_no','No.','DISPLAY_HELPER','integer'),field('product_id','Product ID'),field('lot_id','Lot ID'),field('local_item_name','Items'),field('current_qty','Current Qty','COMPUTED_FIELD','decimal'),field('mapping_status','Mapping Status')];
  const col=(field,label,width=120)=>({field,label,width});
  window.__presets=[{view_id:'main-stock',name:'Main Stock',preset_type:'MAIN_STOCK_COMPATIBILITY',provider:'lot_balance',row_grain:'PRODUCT_LOT',store_scope:'MAIN',system_preset:true,description:'Main Stock projection.',columns:[col('display_no','No.',70),col('local_item_name','Items',260),col('current_qty','Current Qty'),col('mapping_status','Mapping Status')]}];
  const response=data=>new Response(JSON.stringify(data),{status:200,headers:{'Content-Type':'application/json'}});
  window.fetch=async input=>{
    const url=typeof input==='string'?input:input.url;window.__inventoryRequests.push(url);
    if(url==='/dashboard/api/inventory-view/presets')return response({items:window.__presets});
    if(url==='/dashboard/api/inventory-view/registry')return response({fields:window.__registry});
    if(url.startsWith('/dashboard/api/inventory-view/rows?')){
      const parsed=new URL(url,'https://msa.test');
      const requested=parsed.searchParams.get('fields')?.split(',').filter(Boolean);
      const view=window.__presets[0];
      const columns=(requested?.length?requested.map(key=>({field:key,label:window.__registry.find(f=>f.key===key)?.label||key,width:null})):view.columns).map(c=>({...c,field_definition:window.__registry.find(f=>f.key===c.field)}));
      const source={display_no:1,product_id:'p-main',lot_id:'lot-main-1',local_item_name:'10cc Syringe',current_qty:'120.000',mapping_status:'REVIEW_REQUIRED'};
      const item={...Object.fromEntries(columns.map(c=>[c.field,source[c.field]??null])),product_id:source.product_id,lot_id:source.lot_id,local_item_name:source.local_item_name,current_qty:source.current_qty,mapping_status:source.mapping_status};
      return response({view,columns,items:[item],count:1,limit:100,offset:0,read_only:true,database_canonical:false,migration_baseline_accepted:false});
    }
    return response({items:[]});
  };
});

await page.addScriptTag({path:script});
await page.getByText('10cc Syringe').waitFor({state:'visible'});
await page.locator('#inventoryColumnsToggle').click();
const option=page.locator('.inventory-column-option[data-column-key="local_item_name"]');
await option.locator('[data-column-move="up"]').click();
await option.locator('[data-column-width]').fill('208');
const before=await page.evaluate(()=>({checks:[...document.querySelectorAll('.inventory-column-option')].map(x=>({key:x.dataset.columnKey,checked:x.querySelector('input[type=checkbox]')?.checked,width:x.querySelector('[data-column-width]')?.value})),requests:window.__inventoryRequests.slice()}));
console.log('LAYOUT_BEFORE='+JSON.stringify(before));
await page.locator('#inventoryColumnsApply').click();
await page.waitForTimeout(250);
const after=await page.evaluate(()=>({requests:window.__inventoryRequests.slice(),tableHidden:document.querySelector('#inventoryViewTable').hidden,emptyHidden:document.querySelector('#inventoryViewEmpty').hidden,emptyText:document.querySelector('#inventoryViewEmpty').textContent,meta:document.querySelector('#inventoryViewMeta').textContent,headers:[...document.querySelectorAll('#inventoryViewTable thead th')].map(x=>x.textContent),html:document.querySelector('#inventoryViewTable thead').innerHTML}));
console.log('LAYOUT_AFTER='+JSON.stringify(after));
assert.ok(after.requests.at(-1).includes('fields='),'Apply layout should issue a fields projection request');
await browser.close();