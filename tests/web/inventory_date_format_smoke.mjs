import assert from 'node:assert/strict';
import path from 'node:path';
import { chromium } from 'playwright';

const root=process.cwd();
const script=path.join(root,'backend/app/dashboard_assets/dashboard_inventory_views.js');
const browser=await chromium.launch({headless:true});
const context=await browser.newContext({viewport:{width:390,height:844}});

await context.route('https://msa.test/dashboard',async route=>route.fulfill({
  status:200,
  contentType:'text/html',
  body:'<main id="msa"><button class="nav-btn" data-view="inventory" type="button">Inventory</button><section class="view" data-panel="inventory"></section></main>'
}));

async function preparePage(){
  const page=await context.newPage();
  await page.goto('https://msa.test/dashboard');
  await page.evaluate(()=>{
    const field=(key,label,data_type='string')=>({key,label,kind:'ENTITY_FIELD',data_type,editable:false,description:''});
    const registry=[field('local_item_name','Items'),field('expiry_date','Expiry Date','date'),field('current_qty','Current Qty','decimal')];
    const columns=[
      {field:'local_item_name',label:'Items',width:260,field_definition:registry[0],sortable:true},
      {field:'expiry_date',label:'Expiry Date',width:130,field_definition:registry[1],sortable:true},
      {field:'current_qty',label:'Current Qty',width:120,field_definition:registry[2],sortable:true}
    ];
    const view={view_id:'main-stock',name:'Main Stock',preset_type:'MAIN_STOCK_COMPATIBILITY',provider:'lot_balance',row_grain:'PRODUCT_LOT',store_scope:'MAIN',system_preset:true,description:'Main Stock projection.',columns:columns.map(({field,label,width})=>({field,label,width}))};
    const response=data=>new Response(JSON.stringify(data),{status:200,headers:{'Content-Type':'application/json'}});
    window.fetch=async input=>{
      const url=typeof input==='string'?input:input.url;
      if(url==='/dashboard/api/inventory-view/presets')return response({items:[view]});
      if(url==='/dashboard/api/inventory-view/registry')return response({fields:registry});
      if(url.startsWith('/dashboard/api/inventory-view/rows?'))return response({
        view,columns,items:[{product_id:'p1',lot_id:'l1',local_item_name:'Date Test Item',expiry_date:'2026-03-15',current_qty:'10.000'}],count:1,limit:100,offset:0,sort:null,read_only:true,database_canonical:false,migration_baseline_accepted:false
      });
      return new Response('{}',{status:500});
    };
  });
  await page.addScriptTag({path:script});
  await page.getByText('Date Test Item').waitFor({state:'visible'});
  return page;
}

let page=await preparePage();
const dateSelect=page.locator('#inventoryDateFormat');
assert.equal(await dateSelect.inputValue(),'dd-mm-yyyy','default date display must be DD-MM-YYYY');
let expiryCell=page.locator('#inventoryViewTable tbody tr td').nth(2);
assert.equal((await expiryCell.textContent()).trim(),'15-03-2026');

await dateSelect.selectOption('dd-mmm-yyyy');
assert.equal((await expiryCell.textContent()).trim(),'15-Mar-2026');
assert.equal(await page.evaluate(()=>localStorage.getItem('msa.inventory.dateFormat')),'dd-mmm-yyyy');
await page.close();

page=await preparePage();
assert.equal(await page.locator('#inventoryDateFormat').inputValue(),'dd-mmm-yyyy','date format preference must survive reopen');
expiryCell=page.locator('#inventoryViewTable tbody tr td').nth(2);
assert.equal((await expiryCell.textContent()).trim(),'15-Mar-2026');

await browser.close();
console.log('inventory_date_format_smoke=pass default_dd_mm_yyyy=pass selector=pass persistence=pass');
