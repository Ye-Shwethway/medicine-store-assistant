import assert from 'node:assert/strict';
import path from 'node:path';
import { chromium } from 'playwright';

const root=process.cwd();
const script=path.join(root,'backend/app/dashboard_assets/dashboard_inventory_export.js');
const browser=await chromium.launch({headless:true});
const page=await browser.newPage({viewport:{width:390,height:844}});

await page.setContent(`
  <main id="msa">
    <section class="view" data-panel="inventory">
      <div class="inventory-view-toolbar">
        <select id="inventoryPresetSelect">
          <option value="migration-review" selected>Migration Review</option>
          <option value="cms-mapping-review">CMS Mapping Review</option>
          <option value="custom:sv-1">Custom · My Table</option>
        </select>
        <input id="inventoryViewSearch" value="Bandage">
        <select id="inventoryMappingStatus"><option value="REVIEW_REQUIRED" selected>REVIEW_REQUIRED</option></select>
        <select id="inventorySourceClassification"><option value="REVIEW" selected>REVIEW</option></select>
        <input id="inventoryReviewReason" value="duplicate">
        <button id="inventoryViewRefresh" type="button">Refresh</button>
      </div>
      <table id="inventoryViewTable"><thead><tr>
        <th data-field="source_row_no" aria-sort="none">Source Row</th>
        <th data-field="local_item_name" aria-sort="descending"><button><span class="inventory-sort-label">Local Item</span><span>▼</span></button></th>
        <th data-field="review_reason" aria-sort="none">Review Reason</th>
      </tr></thead><tbody></tbody></table>
    </section>
  </main>
`);
await page.evaluate(()=>{
  window.__exportHref='';
  window.alert=message=>{window.__alert=String(message)};
  window.fetch=async url=>{
    if(String(url).includes('/saved-views'))return {ok:true,status:200,json:async()=>({items:[{view_id:'sv-1',base_preset:'main-stock'}]})};
    throw new Error(`Unexpected fetch: ${url}`);
  };
  document.addEventListener('click',event=>{
    const anchor=event.target.closest('a[href*="/dashboard/api/inventory-view/export.xlsx"]');
    if(anchor){window.__exportHref=anchor.getAttribute('href');event.preventDefault()}
  },true);
});
await page.addScriptTag({path:script});

const button=page.getByRole('button',{name:'Export Excel'});
assert.equal(await button.isVisible(),true);
const order=await page.locator('.inventory-view-toolbar > *').evaluateAll(nodes=>nodes.map(node=>node.id));
assert.ok(order.indexOf('inventoryExportExcel')<order.indexOf('inventoryViewRefresh'),'Export Excel should sit before Refresh');
await button.click();
await page.waitForFunction(()=>Boolean(window.__exportHref));
let href=await page.evaluate(()=>window.__exportHref);
let url=new URL(href,'https://msa.test');
assert.equal(url.pathname,'/dashboard/api/inventory-view/export.xlsx');
assert.equal(url.searchParams.get('preset'),'migration-review');
assert.equal(url.searchParams.get('fields'),'source_row_no,local_item_name,review_reason');
assert.deepEqual(JSON.parse(url.searchParams.get('column_labels')),{
  source_row_no:'Source Row',
  local_item_name:'Local Item',
  review_reason:'Review Reason',
});
assert.equal(url.searchParams.get('q'),'Bandage');
assert.equal(url.searchParams.get('mapping_status'),'REVIEW_REQUIRED');
assert.equal(url.searchParams.get('source_classification'),'REVIEW');
assert.equal(url.searchParams.get('review_reason'),'duplicate');
assert.equal(url.searchParams.get('sort_field'),'local_item_name');
assert.equal(url.searchParams.get('sort_dir'),'desc');

await page.locator('#inventoryPresetSelect').selectOption('cms-mapping-review');
await page.locator('#inventoryViewSearch').fill('');
await page.locator('#inventoryReviewReason').fill('');
await page.evaluate(()=>{window.__exportHref=''});
await button.click();
await page.waitForFunction(()=>Boolean(window.__exportHref));
href=await page.evaluate(()=>window.__exportHref);
url=new URL(href,'https://msa.test');
assert.equal(url.searchParams.get('preset'),'cms-mapping-review');
assert.equal(url.searchParams.has('source_classification'),false,'source classification must not leak into non-migration export');
assert.equal(url.searchParams.has('q'),false);
assert.equal(url.searchParams.has('review_reason'),false);
assert.equal(url.searchParams.get('mapping_status'),'REVIEW_REQUIRED');
assert.equal(url.searchParams.get('sort_field'),'local_item_name');
assert.equal(url.searchParams.get('sort_dir'),'desc');

await page.locator('#inventoryPresetSelect').selectOption('custom:sv-1');
await page.locator('#inventoryViewTable thead').evaluate(thead=>{
  thead.innerHTML='<tr><th data-field="local_item_name" aria-sort="none">Medicine Name</th><th data-field="review_reason" aria-sort="none">Owner Note</th></tr>';
});
await page.evaluate(()=>{window.__exportHref=''});
await button.click();
await page.waitForFunction(()=>Boolean(window.__exportHref));
href=await page.evaluate(()=>window.__exportHref);
url=new URL(href,'https://msa.test');
assert.equal(url.searchParams.get('preset'),'main-stock','custom view export must resolve its server-owned base preset');
assert.equal(url.searchParams.get('fields'),'local_item_name,review_reason');
assert.deepEqual(JSON.parse(url.searchParams.get('column_labels')),{
  local_item_name:'Medicine Name',
  review_reason:'Owner Note',
});
assert.equal(await page.evaluate(()=>window.__alert||''),'');

await browser.close();
console.log('inventory_excel_export_smoke=pass current_fields=pass custom_base_preset=pass custom_headers=pass filters=pass sort=pass source_scope=pass row_facts=false mobile=390x844');
