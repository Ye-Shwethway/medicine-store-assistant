import assert from 'node:assert/strict';
import path from 'node:path';
import { chromium } from 'playwright';

const script=path.join(process.cwd(),'backend/app/dashboard_assets/dashboard_inventory_views.js');
const browser=await chromium.launch({headless:true});
const page=await browser.newPage({viewport:{width:1280,height:800}});
await page.setContent('<main id="msa"><section class="view" data-panel="inventory"></section></main>');
await page.evaluate(()=>{
  window.__copied='';
  Object.defineProperty(navigator,'clipboard',{configurable:true,value:{writeText:async text=>{window.__copied=text}}});
  const items=[
    {lot_id:'l1',local_item_name:'Alpha',current_qty:10,cms_code:'C1',mapping_status:'REVIEW_REQUIRED'},
    {lot_id:'l2',local_item_name:'Beta',current_qty:20,cms_code:'C2',mapping_status:'REVIEW_REQUIRED'},
    {lot_id:'l3',local_item_name:'Gamma',current_qty:30,cms_code:'C3',mapping_status:'REVIEW_REQUIRED'},
  ];
  window.fetch=async url=>{
    const requestPath=String(url);
    const json=value=>Promise.resolve({ok:true,status:200,json:async()=>value});
    if(requestPath.includes('/presets'))return json({items:[{view_id:'main-stock',name:'Main Stock'},{view_id:'migration-review',name:'Migration Review'}]});
    if(requestPath.includes('/registry'))return json({fields:[{key:'local_item_name',label:'Items',data_type:'string',kind:'ENTITY_FIELD'},{key:'current_qty',label:'Current Qty',data_type:'decimal',kind:'COMPUTED_FIELD'},{key:'cms_code',label:'CMS Code',data_type:'string',kind:'ENTITY_FIELD'}]});
    if(requestPath.includes('/rows'))return json({view:{view_id:'main-stock',name:'Main Stock',description:'Test view',row_grain:'PRODUCT_LOT',store_scope:'MAIN',columns:[{field:'local_item_name',label:'Items',width:180},{field:'current_qty',label:'Current Qty',width:120},{field:'cms_code',label:'CMS Code',width:120}]},columns:[{field:'local_item_name',label:'Items',sortable:true,width:180,field_definition:{key:'local_item_name',data_type:'string'}},{field:'current_qty',label:'Current Qty',sortable:true,width:120,field_definition:{key:'current_qty',data_type:'decimal'}},{field:'cms_code',label:'CMS Code',sortable:true,width:120,field_definition:{key:'cms_code',data_type:'string'}}],items,sort:{field:null,direction:null}});
    throw new Error('Unexpected '+requestPath);
  };
});
await page.addScriptTag({path:script});
await page.getByText('Alpha',{exact:true}).waitFor();

const cell=(row,col)=>page.locator(`tbody tr:nth-child(${row+1}) td[data-col-index="${col}"]`);
await cell(0,0).click();
assert.equal(await page.locator('#inventorySelectionCount').textContent(),'1 cell selected');
assert.equal(await page.locator('#inventoryReviewDrawer').isHidden(),true,'cell click must not open details');
assert.equal(await cell(0,0).getAttribute('aria-selected'),'true');

await cell(1,1).click({modifiers:['Shift']});
assert.match(await page.locator('#inventorySelectionCount').textContent(),/2×2 range · 4 cells/);
assert.equal(await cell(1,1).getAttribute('aria-selected'),'true');
await page.getByRole('button',{name:'Copy TSV'}).click();
assert.equal(await page.evaluate(()=>window.__copied),'Alpha\t10\nBeta\t20','range copy must contain real TSV row breaks');

await cell(1,1).focus();
await page.keyboard.press('ArrowRight');
assert.equal(await cell(1,2).getAttribute('aria-selected'),'true');
assert.equal(await page.locator('#inventorySelectionCount').textContent(),'1 cell selected');
await page.keyboard.press('Shift+ArrowDown');
assert.match(await page.locator('#inventorySelectionCount').textContent(),/2×1 range · 2 cells/);

const box1=await cell(0,0).boundingBox(),box3=await cell(2,2).boundingBox();
assert.ok(box1&&box3);
await page.mouse.move(box1.x+8,box1.y+8);
await page.mouse.down();
await page.mouse.move(box3.x+8,box3.y+8,{steps:5});
await page.mouse.up();
assert.match(await page.locator('#inventorySelectionCount').textContent(),/3×3 range · 9 cells/);

await cell(0,0).click();
await page.getByRole('button',{name:'Copy TSV'}).click();
assert.equal(await page.evaluate(()=>window.__copied),'Alpha');

const row1=page.getByRole('button',{name:'Select row 1'}),row3=page.getByRole('button',{name:'Select row 3'});
await row1.click();
assert.equal(await page.locator('#inventorySelectionCount').textContent(),'1 row selected');
assert.equal(await page.getByRole('button',{name:'Details'}).isEnabled(),true);
await page.getByRole('button',{name:'Details'}).click();
assert.equal(await page.locator('#inventoryReviewDrawer').isVisible(),true);
assert.match(await page.locator('#inventoryDrawerTitle').textContent(),/Alpha/);
await page.getByRole('button',{name:'Close review detail'}).click();
await row3.click({modifiers:['Shift']});
assert.equal(await page.locator('#inventorySelectionCount').textContent(),'3 rows selected');

await page.getByRole('button',{name:'Select visible rows'}).click();
assert.equal(await page.locator('#inventorySelectionCount').textContent(),'0 selected');
assert.equal(await page.locator('#inventorySelectionBar').isHidden(),true);

await cell(0,1).click();
assert.equal(await page.locator('#inventorySelectionCount').textContent(),'1 cell selected');
await page.locator('#inventorySearch').fill('Alpha');
await page.waitForTimeout(260);
assert.equal(await page.locator('#inventorySelectionBar').isHidden(),true,'search coordinate changes must clear stale selection');
await page.locator('#inventorySearch').fill('');
await page.waitForTimeout(260);

await page.setViewportSize({width:390,height:844});
await cell(0,1).click();
assert.equal(await page.locator('#inventoryReviewDrawer').isHidden(),true);
assert.equal(await page.locator('#inventorySelectionCount').textContent(),'1 cell selected');
const touchTarget=await row1.boundingBox();
assert.ok(touchTarget&&touchTarget.height>=40,'row selector remains a practical touch target');

await browser.close();
console.log('inventory_sheet_selection=pass cell_click=pass range=pass drag=pass keyboard=pass rows=pass details=explicit copy=pass stale_selection=cleared mobile=pass');