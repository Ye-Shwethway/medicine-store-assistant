import assert from 'node:assert/strict';
import path from 'node:path';
import { chromium } from 'playwright';

const script=path.join(process.cwd(),'backend/app/dashboard_assets/dashboard_inventory_views.js');
const stylesheet=path.join(process.cwd(),'backend/app/dashboard_assets/dashboard_inventory_views.css');
const browser=await chromium.launch({headless:true});
const page=await browser.newPage({viewport:{width:1280,height:800}});
await page.setContent('<main id="msa"><section class="view" data-panel="inventory"></section></main>');
await page.evaluate(()=>{
  window.__copied='';
  Object.defineProperty(navigator,'clipboard',{configurable:true,value:{writeText:async text=>{window.__copied=text}}});
  const baseItems=[
    {lot_id:'l1',local_item_name:'Alpha',current_qty:10,cms_code:'C1',mapping_status:'REVIEW_REQUIRED'},
    {lot_id:'l2',local_item_name:'Beta',current_qty:20,cms_code:'C2',source_classification:'CONFLICT'},
    {lot_id:'l3',local_item_name:'Gamma',current_qty:30,cms_code:'C3'},
  ];
  window.fetch=async url=>{
    const requestPath=String(url);
    const json=value=>Promise.resolve({ok:true,status:200,json:async()=>value});
    if(requestPath.includes('/presets'))return json({items:[{view_id:'main-stock',name:'Main Stock'}]});
    if(requestPath.includes('/registry'))return json({fields:[{key:'local_item_name',label:'Items',data_type:'string',kind:'ENTITY_FIELD'},{key:'current_qty',label:'Current Qty',data_type:'decimal',kind:'COMPUTED_FIELD'},{key:'cms_code',label:'CMS Code',data_type:'string',kind:'ENTITY_FIELD'}]});
    if(requestPath.includes('/rows')){
      const params=new URL(requestPath,'https://example.test').searchParams;
      const dir=params.get('sort_dir');
      const items=[...baseItems];
      if(dir==='desc')items.reverse();
      return json({view:{view_id:'main-stock',name:'Main Stock',description:'Formatting proof',row_grain:'PRODUCT_LOT',store_scope:'MAIN',columns:[{field:'local_item_name',label:'Items',width:180},{field:'current_qty',label:'Current Qty',width:120},{field:'cms_code',label:'CMS Code',width:120}]},columns:[{field:'local_item_name',label:'Items',sortable:true,width:180,field_definition:{key:'local_item_name',data_type:'string'}},{field:'current_qty',label:'Current Qty',sortable:true,width:120,field_definition:{key:'current_qty',data_type:'decimal'}},{field:'cms_code',label:'CMS Code',sortable:true,width:120,field_definition:{key:'cms_code',data_type:'string'}}],items,sort:{field:params.get('sort_field'),direction:dir}});
    }
    throw new Error('Unexpected '+requestPath);
  };
});
await page.addStyleTag({path:stylesheet});
await page.addScriptTag({path:script});
await page.getByRole('cell',{name:'Alpha'}).waitFor();

const cell=(row,col)=>page.locator(`tbody tr:nth-child(${row+1}) td[data-col-index="${col}"]`);
const fill=async name=>{
  await page.getByRole('button',{name:'Fill',exact:true}).click();
  await page.getByRole('button',{name,exact:true}).click();
};

await cell(0,0).click();
assert.equal(await page.locator('#inventoryFillToggle').getAttribute('aria-haspopup'),'menu');
await page.getByRole('button',{name:'Fill',exact:true}).click();
assert.equal(await page.locator('#inventoryFillMenu .inventory-fill-menu-head strong').textContent(),'Fill color');
assert.equal(await page.locator('#inventoryFillMenu .inventory-fill-option.secondary').count(),0,'derived color tiles must not reuse native secondary button styling');
await page.getByRole('button',{name:'Fill',exact:true}).click();
await fill('Yellow');
assert.equal(await cell(0,0).getAttribute('data-user-fill'),'yellow');
assert.match(await cell(0,0).getAttribute('style'),/background-color:\s*#fff1a8\s*!important/i,'runtime fill must be applied inline with important priority');
const singleVisual=await cell(0,0).evaluate(el=>{const s=getComputedStyle(el);return {background:s.backgroundColor,boxShadow:s.boxShadow}});
assert.notEqual(singleVisual.background,'rgb(255, 255, 255)','user fill must be visibly distinct');
assert.match(singleVisual.boxShadow,/inset/i,'active selection outline must remain visible above user fill');

await cell(1,1).click({modifiers:['Shift']});
await fill('Green');
for(let row=0;row<=1;row++)for(let col=0;col<=1;col++)assert.equal(await cell(row,col).getAttribute('data-user-fill'),'green');

await page.getByRole('button',{name:'Select row 3'}).click();
await fill('Blue');
for(let col=0;col<3;col++)assert.equal(await cell(2,col).getAttribute('data-user-fill'),'blue','whole-row fill must cover visible registered cells');

await cell(0,0).click();
await page.getByRole('button',{name:'Fill',exact:true}).click();
await page.getByRole('menuitem',{name:'No fill',exact:true}).click();
assert.equal(await cell(0,0).getAttribute('data-user-fill'),null,'Clear fill must remove only user formatting from selected cell');
assert.equal(await cell(0,1).getAttribute('data-user-fill'),'green','Clear fill must not remove fill outside the selection');

const reviewSignal=await cell(0,1).evaluate(el=>{const s=getComputedStyle(el,'::before');return {width:s.width,background:s.backgroundColor,content:s.content}});
assert.notEqual(reviewSignal.width,'0px','review semantic stripe must remain visible with user fill');
assert.notEqual(reviewSignal.background,'rgba(0, 0, 0, 0)','review semantic stripe must retain its own signal');

await page.getByRole('button',{name:/Sort by Items/}).click();
await page.getByRole('button',{name:/Sort by Items/}).click();
await page.getByRole('cell',{name:'Alpha'}).waitFor();
const alphaRow=page.getByRole('cell',{name:'Alpha'}).locator('..');
assert.equal(await alphaRow.locator('td[data-field="current_qty"]').getAttribute('data-user-fill'),'green','semantic row+field fill must remain attached after sort/re-render');

await page.getByRole('cell',{name:'Alpha'}).click();
await page.getByRole('button',{name:'Copy TSV'}).click();
assert.equal(await page.evaluate(()=>window.__copied),'Alpha','TSV copy remains value-only');

await page.setViewportSize({width:390,height:844});
await page.getByRole('cell',{name:'Gamma'}).click();
await page.getByRole('button',{name:'Fill',exact:true}).click();
assert.equal(await page.getByRole('button',{name:'Orange',exact:true}).isVisible(),true,'mobile fill palette must be reachable');
await page.getByRole('button',{name:'Orange',exact:true}).click();
assert.equal(await page.getByRole('cell',{name:'Gamma'}).getAttribute('data-user-fill'),'orange');

await browser.close();
console.log('inventory_sheet_formatting=pass cell_fill=pass range_fill=pass row_fill=pass clear_fill=pass semantic_signal=pass sort_identity=pass copy_value_only=pass mobile_palette=pass mutation=false');
