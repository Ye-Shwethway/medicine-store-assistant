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
await page.goto('https://msa.test/');
await page.evaluate(({registry,preset,saved})=>{
  window.__exportHref='';
  const realCreate=document.createElement.bind(document);
  document.createElement=(tag,...rest)=>{
    const el=realCreate(tag,...rest);
    if(String(tag).toLowerCase()==='a'){
      const original=el.click.bind(el);
      el.click=()=>{window.__exportHref=el.href; return original();};
    }
    return el;
  };
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
const actionBoxes=await page.locator('.inventory-saved-view-actions button').evaluateAll(nodes=>nodes.map(node=>{const r=node.getBoundingClientRect();return {left:r.left,right:r.right,top:r.top,bottom:r.bottom,height:r.height}}));
assert.ok(actionBoxes.every(box=>box.left>=0&&box.right<=390.5&&box.height>=43.5),'saved-view mobile actions must fit viewport with touch targets');
await page.locator('#inventoryExportExcel').click();
await page.waitForTimeout(50);
const href=await page.evaluate(()=>window.__exportHref);
assert.match(href,/preset=main-stock/,'custom export must resolve server-owned base preset');
assert.match(href,/export_name=TEST(?:\+|%20)STOCK/,'custom export must send current custom table display name');
assert.match(href,/column_labels=/,'custom export must retain displayed headers');

await browser.close();
console.log('inventory_mobile_builder_polish=pass viewport=390x844 bottom_sheet=pass stacked_fields=pass touch_targets=pass saved_actions=pass custom_export_name=pass');
