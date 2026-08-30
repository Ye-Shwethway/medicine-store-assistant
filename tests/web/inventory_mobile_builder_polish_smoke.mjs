import assert from 'node:assert/strict';
import path from 'node:path';
import { chromium } from 'playwright';

const viewsScript=path.join(process.cwd(),'backend/app/dashboard_assets/dashboard_inventory_views.js');
const exportScript=path.join(process.cwd(),'backend/app/dashboard_assets/dashboard_inventory_export.js');
const stylesheet=path.join(process.cwd(),'backend/app/dashboard_assets/dashboard_inventory_views.css');
const browser=await chromium.launch({headless:true});
const page=await browser.newPage({viewport:{width:390,height:844}});

const registry=[
  {key:'local_item_name',label:'Items',data_type:'string',kind:'ENTITY_FIELD'},
  {key:'current_qty',label:'Current Qty',data_type:'decimal',kind:'COMPUTED_FIELD'},
  {key:'cms_code',label:'CMS Code',data_type:'string',kind:'ENTITY_FIELD'},
];
const preset={view_id:'main-stock',name:'Main Stock',description:'Mobile polish proof',row_grain:'PRODUCT_LOT',store_scope:'MAIN',columns:[{field:'local_item_name',label:'Items',width:180},{field:'current_qty',label:'Current Qty',width:120},{field:'cms_code',label:'CMS Code',width:120}]};
const saved={view_id:'sv-1',name:'TEST STOCK',base_preset:'main-stock',definition:{fields:['local_item_name','current_qty','cms_code'],column_labels:{local_item_name:'Medicine Name',current_qty:'Balance',cms_code:'CMS Code'},column_widths:{},density:'comfortable',filters:{q:'',mapping_status:'',source_classification:'',review_reason:''},sort:null,fills:[]},system_preset:false};

await page.route('https://msa.test/',route=>route.fulfill({status:200,contentType:'text/html',body:'<main id="msa"><section class="view" data-panel="inventory"></section></main>'}));
await page.route('https://msa.test/dashboard/api/inventory-view/export.xlsx*',route=>route.fulfill({status:200,contentType:'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',body:'proof'}));
await page.goto('https://msa.test/');
await page.evaluate(({registry,preset,saved})=>{
  const json=(value,status=200)=>Promise.resolve({ok:status>=200&&status<300,status,json:async()=>value});
  window.fetch=async(url,opts={})=>{
    const p=String(url),method=String(opts.method||'GET').toUpperCase();
    if(p.includes('/saved-views'))return json({items:[saved],database_canonical:false,migration_baseline_accepted:false});
    if(p.includes('/presets'))return json({items:[preset]});
    if(p.includes('/registry'))return json({fields:registry});
    if(p.includes('/rows'))return json({view:preset,columns:preset.columns.map(c=>({...c,sortable:true,field_definition:registry.find(r=>r.key===c.field)})),items:[{lot_id:'l1',local_item_name:'Alpha',current_qty:10,cms_code:'C1'}],sort:{field:null,direction:null}});
    throw new Error(`Unexpected ${method} ${p}`);
  };
},{registry,preset,saved});
await page.addStyleTag({path:stylesheet});
await page.addScriptTag({path:viewsScript});
await page.addScriptTag({path:exportScript});
await page.getByRole('cell',{name:'Alpha'}).waitFor();

await page.locator('#inventoryNewTable').click();
const dialog=page.locator('.inventory-table-builder');
await dialog.waitFor();
const dialogBox=await dialog.boundingBox();
assert.ok(dialogBox,'builder dialog must render');
assert.ok(dialogBox.x>=0 && dialogBox.x+dialogBox.width<=390.5,'builder must stay within mobile viewport');
assert.ok(dialogBox.y>0,'bottom sheet must leave some backdrop above it');
const backdrop=page.locator('.inventory-table-builder-backdrop');
assert.equal(await backdrop.evaluate(el=>getComputedStyle(el).alignItems),'end','mobile builder must align as bottom sheet');
const nameBox=await dialog.locator('[data-inventory-builder-name]').boundingBox();
const sourceBox=await dialog.locator('[data-inventory-builder-source]').boundingBox();
assert.ok(nameBox && sourceBox && sourceBox.y>nameBox.y+nameBox.height-1,'name and row source must stack vertically on mobile');
for(const selector of ['[data-builder-close]','[data-builder-move="up"]','[data-builder-move="down"]','[data-inventory-builder-save]']){
  const box=await dialog.locator(selector).first().boundingBox();
  assert.ok(box && box.height>=43.5,`${selector} must provide a 44px touch target`);
}
await dialog.locator('[data-builder-cancel]').click();

await page.locator('#inventoryPresetSelect').selectOption('custom:sv-1');
await page.getByText('Medicine Name',{exact:true}).waitFor();
const tableActionsToggle=page.locator('#inventoryMobileTableActionsToggle');
assert.equal(await tableActionsToggle.isVisible(),true,'mobile must expose one compact table-actions disclosure');
assert.equal(await page.locator('.inventory-saved-view-actions').isVisible(),false,'saved-view CRUD actions must be collapsed by default on mobile');
await tableActionsToggle.click();
assert.equal(await page.locator('.inventory-saved-view-actions').isVisible(),true,'table-actions disclosure must reveal saved-view CRUD actions');
const actionStripBox=await page.locator('.inventory-mobile-action-strip').boundingBox();
assert.ok(actionStripBox && actionStripBox.height<=44.5,'routine mobile actions must stay in one compact strip');
await tableActionsToggle.click();

const cell=page.getByRole('cell',{name:'Alpha'});
const cellBox=await cell.boundingBox();
assert.ok(cellBox,'test cell must render');
const cx=cellBox.x+Math.min(20,cellBox.width/2),cy=cellBox.y+Math.min(20,cellBox.height/2);
await cell.dispatchEvent('pointerdown',{pointerType:'touch',pointerId:71,clientX:cx,clientY:cy,button:0,buttons:1});
await cell.dispatchEvent('pointermove',{pointerType:'touch',pointerId:71,clientX:cx,clientY:cy+42,button:0,buttons:1});
await cell.dispatchEvent('pointerup',{pointerType:'touch',pointerId:71,clientX:cx,clientY:cy+42,button:0,buttons:0});
assert.equal(await page.locator('#inventorySelectionBar').isVisible(),false,'touch scroll gesture must not create a cell selection');
await cell.dispatchEvent('pointerdown',{pointerType:'touch',pointerId:72,clientX:cx,clientY:cy,button:0,buttons:1});
await cell.dispatchEvent('pointerup',{pointerType:'touch',pointerId:72,clientX:cx+2,clientY:cy+2,button:0,buttons:0});
await page.getByText('1 cell selected',{exact:true}).waitFor();
assert.equal(await page.locator('#inventorySelectionBar').isVisible(),true,'stationary touch tap must still select a cell');
await page.locator('#inventoryClearSelection').click();

await page.locator('#inventoryFocusToggle').click();
assert.equal(await page.locator('.view[data-panel="inventory"]').evaluate(el=>el.classList.contains('inventory-focus-mode')),true,'focus mode must activate');
assert.equal(await tableActionsToggle.isVisible(),false,'focus mode must hide table-management disclosure');
const focusToolbarBox=await page.locator('.inventory-view-toolbar').boundingBox();
const focusTableBox=await page.locator('.inventory-view-table-wrap').boundingBox();
assert.ok(focusToolbarBox && focusToolbarBox.height<=52,'focus mode controls must stay compact');
assert.ok(focusTableBox && focusTableBox.height>=680,'focus mode must give most of the phone viewport to the table');
await page.locator('#inventoryFocusToggle').click();

const requestPromise=page.waitForRequest(request=>request.url().includes('/dashboard/api/inventory-view/export.xlsx?'));
await page.locator('#inventoryExportExcel').click();
const exportRequest=await requestPromise;
const href=exportRequest.url();
assert.match(href,/preset=main-stock/,'custom export must resolve server-owned base preset');
assert.match(href,/export_name=TEST(?:\+|%20)STOCK/,'custom export must send current custom table display name');
assert.match(href,/column_labels=/,'custom export must retain displayed headers');

await browser.close();
console.log('inventory_mobile_builder_polish=pass viewport=390x844 table_first=pass actions_collapsed=pass touch_scroll_no_select=pass tap_select=pass focus_table_space=pass custom_export_name=pass');
