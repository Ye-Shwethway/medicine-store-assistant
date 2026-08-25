import assert from 'node:assert/strict';
import path from 'node:path';
import { chromium } from 'playwright';

const script=path.join(process.cwd(),'backend/app/dashboard_assets/dashboard_inventory_views.js');
const stylesheet=path.join(process.cwd(),'backend/app/dashboard_assets/dashboard_inventory_views.css');
const browser=await chromium.launch({headless:true});

const baseItems=[
  {lot_id:'l1',local_item_name:'Alpha',current_qty:10,cms_code:'C1'},
  {lot_id:'l2',local_item_name:'Beta',current_qty:20,cms_code:'C2'},
  {lot_id:'l3',local_item_name:'Gamma',current_qty:30,cms_code:'C3'},
];
const registry=[
  {key:'local_item_name',label:'Items',data_type:'string',kind:'ENTITY_FIELD'},
  {key:'current_qty',label:'Current Qty',data_type:'decimal',kind:'COMPUTED_FIELD'},
  {key:'cms_code',label:'CMS Code',data_type:'string',kind:'ENTITY_FIELD'},
];
const preset={view_id:'main-stock',name:'Main Stock',description:'Saved view proof',row_grain:'PRODUCT_LOT',store_scope:'MAIN',columns:[{field:'local_item_name',label:'Items',width:180},{field:'current_qty',label:'Current Qty',width:120},{field:'cms_code',label:'CMS Code',width:120}]};
let savedViews=[];

async function installPage(page,{activeId=''}={}){
  await page.route('https://msa.test/',route=>route.fulfill({status:200,contentType:'text/html',body:'<main id="msa"><section class="view" data-panel="inventory"></section></main>'}));
  await page.goto('https://msa.test/');
  await page.evaluate(({baseItems,registry,preset,initialSaved,activeId})=>{
    window.__savedViews=structuredClone(initialSaved);
    window.__requests=[];
    window.__nextId=window.__savedViews.length+1;
    window.__prompts=[];
    window.__alerts=[];
    window.prompt=()=>window.__prompts.shift()??null;
    window.confirm=()=>true;
    window.alert=message=>window.__alerts.push(String(message));
    if(activeId)localStorage.setItem('msa.inventory.activeSavedViewId',activeId);else localStorage.removeItem('msa.inventory.activeSavedViewId');
    Object.defineProperty(navigator,'clipboard',{configurable:true,value:{writeText:async()=>{}}});
    const json=(value,status=200)=>Promise.resolve({ok:status>=200&&status<300,status,json:async()=>value});
    window.fetch=async (url,opts={})=>{
      const requestPath=String(url);
      const method=String(opts.method||'GET').toUpperCase();
      if(requestPath.includes('/saved-views')){
        window.__requests.push({method,path:requestPath,body:opts.body?JSON.parse(opts.body):null});
        const idMatch=requestPath.match(/\/saved-views\/([^/?]+)/);
        if(method==='GET')return json({items:structuredClone(window.__savedViews),database_canonical:false,migration_baseline_accepted:false});
        if(method==='POST'){
          const body=JSON.parse(opts.body);
          const saved={view_id:`sv-${window.__nextId++}`,name:body.name,base_preset:body.base_preset,definition:body.definition,system_preset:false,created_at:'2026-08-25T00:00:00Z',updated_at:'2026-08-25T00:00:00Z'};
          window.__savedViews.push(saved);
          return json(structuredClone(saved),201);
        }
        if(method==='PUT'&&idMatch){
          const body=JSON.parse(opts.body),id=idMatch[1],index=window.__savedViews.findIndex(item=>item.view_id===id);
          if(index<0)return json({detail:'Saved view not found'},404);
          window.__savedViews[index]={...window.__savedViews[index],name:body.name,base_preset:body.base_preset,definition:body.definition,updated_at:'2026-08-25T00:01:00Z'};
          return json(structuredClone(window.__savedViews[index]));
        }
        if(method==='DELETE'&&idMatch){
          const id=idMatch[1];
          window.__savedViews=window.__savedViews.filter(item=>item.view_id!==id);
          return json(null,204);
        }
      }
      if(requestPath.includes('/presets'))return json({items:[preset]});
      if(requestPath.includes('/registry'))return json({fields:registry});
      if(requestPath.includes('/rows')){
        const params=new URL(requestPath,'https://example.test').searchParams;
        const requested=(params.get('fields')||'local_item_name,current_qty,cms_code').split(',').filter(Boolean);
        let items=[...baseItems];
        const q=(params.get('q')||'').toLowerCase();
        if(q)items=items.filter(item=>item.local_item_name.toLowerCase().includes(q)||item.cms_code.toLowerCase().includes(q));
        if(params.get('sort_field')==='local_item_name'&&params.get('sort_dir')==='desc')items.reverse();
        const columns=requested.map(field=>{const def=registry.find(item=>item.key===field);return {field,label:def?.label||field,sortable:true,width:field==='local_item_name'?180:120,field_definition:def||{key:field,data_type:'string'}}});
        return json({view:preset,columns,items,sort:{field:params.get('sort_field'),direction:params.get('sort_dir')}});
      }
      throw new Error(`Unexpected ${method} ${requestPath}`);
    };
  },{baseItems,registry,preset,initialSaved:savedViews,activeId});
  await page.addStyleTag({path:stylesheet});
  await page.addScriptTag({path:script});
  await page.getByRole('cell',{name:'Alpha'}).waitFor();
}

const builderPage=await browser.newPage({viewport:{width:1280,height:800}});
await installPage(builderPage);
await builderPage.locator('#inventoryNewTable').click();
await builderPage.locator('[data-inventory-builder-name]').fill('My Custom Table');
await builderPage.locator('[data-builder-select][value="local_item_name"]').check();
await builderPage.locator('[data-builder-select][value="current_qty"]').check();
await builderPage.locator('[data-builder-label][data-field="local_item_name"]').fill('Medicine Name');
await builderPage.locator('[data-builder-label][data-field="current_qty"]').fill('Balance');
await builderPage.locator('[data-inventory-builder-save]').click();
await builderPage.locator('#inventoryPresetSelect option[value="custom:sv-1"]').waitFor({state:'attached'});
await builderPage.getByText('Medicine Name',{exact:true}).waitFor();
await builderPage.getByText('Balance',{exact:true}).waitFor();
const builderCreated=await builderPage.evaluate(()=>window.__requests.find(item=>item.method==='POST'));
assert.deepEqual(builderCreated.body.definition.fields,['local_item_name','current_qty']);
assert.deepEqual(builderCreated.body.definition.column_labels,{local_item_name:'Medicine Name',current_qty:'Balance'});
assert.equal(builderCreated.body.base_preset,'main-stock');
assert.equal(builderCreated.body.definition.provider,undefined);
await builderPage.locator('#inventoryEditTable').click();
assert.equal(await builderPage.locator('[data-inventory-builder-name]').inputValue(),'My Custom Table');
assert.equal(await builderPage.locator('[data-builder-label][data-field="local_item_name"]').inputValue(),'Medicine Name');
await builderPage.locator('[data-builder-cancel]').click();
await builderPage.close();

const page=await browser.newPage({viewport:{width:1280,height:800}});
await installPage(page);

await page.locator('#inventoryDensityToggle').click();
assert.equal(await page.locator('.view[data-panel="inventory"]').getAttribute('data-inventory-density'),'compact');
await page.getByRole('cell',{name:'Alpha'}).click();
await page.locator('#inventoryFillToggle').click();
await page.getByRole('menuitem',{name:'Green',exact:true}).click();
assert.equal(await page.getByRole('cell',{name:'Alpha'}).getAttribute('data-user-fill'),'green');
await page.getByRole('button',{name:/Sort by Items/}).click();
await page.locator('#inventoryViewSearch').fill('Alpha');
await page.waitForTimeout(260);
await page.getByRole('cell',{name:'Alpha'}).waitFor();

await page.evaluate(()=>window.__prompts.push('My Stock View'));
await page.locator('#inventorySaveView').click();
await page.locator('#inventoryPresetSelect option[value="custom:sv-1"]').waitFor({state:'attached'});
assert.equal(await page.locator('#inventoryPresetSelect').inputValue(),'custom:sv-1');
assert.equal(await page.evaluate(()=>localStorage.getItem('msa.inventory.activeSavedViewId')),'sv-1');
const created=await page.evaluate(()=>window.__requests.find(item=>item.method==='POST'));
assert.ok(created,'Save view must POST a server-owned definition');
assert.equal(created.body.name,'My Stock View');
assert.equal(created.body.base_preset,'main-stock');
assert.equal(created.body.definition.density,'compact');
assert.equal(created.body.definition.filters.q,'Alpha');
assert.deepEqual(created.body.definition.sort,{field:'local_item_name',direction:'asc'});
assert.ok(created.body.definition.fills.some(fill=>fill.row_key==='l1'&&fill.field==='local_item_name'&&fill.fill==='green'),'fill metadata must persist by row identity + field');
assert.equal(created.body.definition.provider,undefined,'client must not persist provider/SQL authority');

await page.locator('#inventoryPresetSelect').selectOption('main-stock');
await page.getByRole('cell',{name:'Alpha'}).waitFor();
assert.equal(await page.locator('#inventoryViewSearch').inputValue(),'');
await page.locator('#inventoryPresetSelect').selectOption('custom:sv-1');
await page.getByRole('cell',{name:'Alpha'}).waitFor();
assert.equal(await page.locator('#inventoryViewSearch').inputValue(),'Alpha');
assert.equal(await page.locator('.view[data-panel="inventory"]').getAttribute('data-inventory-density'),'compact');
assert.equal(await page.getByRole('cell',{name:'Alpha'}).getAttribute('data-user-fill'),'green');
assert.match(await page.locator('#inventoryViewDescription').textContent(),/Custom table\/view · row source Main Stock/);

await page.locator('#inventorySaveView').click();
assert.ok(await page.evaluate(()=>window.__requests.some(item=>item.method==='PUT'&&item.path.includes('/saved-views/sv-1'))),'active custom Save must update its own definition');
await page.evaluate(()=>window.__prompts.push('Stock Copy'));
await page.locator('#inventorySaveViewAs').click();
await page.locator('#inventoryPresetSelect option[value="custom:sv-2"]').waitFor({state:'attached'});
assert.equal(await page.locator('#inventoryPresetSelect').inputValue(),'custom:sv-2');

await page.locator('#inventoryClearAll').click();
await page.getByRole('cell',{name:'Alpha'}).waitFor();
assert.equal(await page.locator('#inventoryViewSearch').inputValue(),'');
assert.equal(await page.locator('#inventoryActiveFilters').getByText('Sort:',{exact:false}).count(),0);
assert.equal(await page.getByRole('cell',{name:'Alpha'}).getAttribute('data-user-fill'),'green','Clear all must not clear user fill');
assert.equal(await page.locator('#inventoryPresetSelect').inputValue(),'custom:sv-2','Clear all must not delete the active saved view');

savedViews=await page.evaluate(()=>structuredClone(window.__savedViews));
const reopenId=await page.evaluate(()=>localStorage.getItem('msa.inventory.activeSavedViewId'));
assert.equal(reopenId,'sv-2');

const reopen=await browser.newPage({viewport:{width:1280,height:800}});
await installPage(reopen,{activeId:reopenId});
await reopen.locator('#inventoryPresetSelect option[value="custom:sv-2"]').waitFor({state:'attached'});
assert.equal(await reopen.locator('#inventoryPresetSelect').inputValue(),'custom:sv-2');
assert.equal(await reopen.locator('.view[data-panel="inventory"]').getAttribute('data-inventory-density'),'compact');
assert.equal(await reopen.getByRole('cell',{name:'Alpha'}).getAttribute('data-user-fill'),'green','fresh load must rehydrate saved formatting');

await reopen.setViewportSize({width:390,height:844});
assert.equal(await reopen.locator('#inventorySaveView').isVisible(),true);
assert.equal(await reopen.locator('#inventorySaveViewAs').isVisible(),true);
assert.equal(await reopen.locator('#inventoryDeleteView').isVisible(),true);
await reopen.locator('#inventoryDeleteView').click();
await reopen.getByRole('cell',{name:'Alpha'}).waitFor();
assert.equal(await reopen.locator('#inventoryPresetSelect').inputValue(),'main-stock');
assert.equal(await reopen.evaluate(()=>localStorage.getItem('msa.inventory.activeSavedViewId')),null);
assert.ok(await reopen.evaluate(()=>window.__requests.some(item=>item.method==='DELETE'&&item.path.includes('/saved-views/sv-2'))));

await browser.close();
console.log('inventory_saved_views=pass custom_table_builder=pass editable_headers=pass create=pass readback=pass custom_selector=pass rehydrate=pass update=pass save_as=pass clear_all_isolated=pass reopen=pass mobile=pass delete_fallback=pass owner_api_boundary=server mutation_inventory=false');
