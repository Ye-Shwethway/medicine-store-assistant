import assert from 'node:assert/strict';
import path from 'node:path';
import { chromium } from 'playwright';

const root = process.cwd();
const script = path.join(root, 'backend/app/dashboard_assets/dashboard_inventory_views.js');
const stylesheet = path.join(root, 'backend/app/dashboard_assets/dashboard_inventory_views.css');
const browser = await chromium.launch({ headless: true });
const page = await browser.newPage({ viewport: { width: 390, height: 844 } });

await page.setContent(`
  <main id="msa">
    <h1 id="pageTitle">Inventory</h1>
    <p id="pageSubtitle">Old shadow table</p>
    <button class="nav-btn" data-view="inventory" type="button">Inventory</button>
    <section class="view" data-panel="inventory">
      <div id="legacyInventorySubtree"><table><tbody><tr><td>Legacy staged row</td></tr></tbody></table></div>
    </section>
  </main>
`);
await page.addStyleTag({ path: stylesheet });

await page.evaluate(() => {
  window.__inventoryRequests = [];
  const field = (key, label, kind = 'ENTITY_FIELD', data_type = 'string') => ({ key, label, kind, data_type, editable: false, description: '' });
  window.__registry = [
    field('display_no', 'No.', 'DISPLAY_HELPER', 'integer'),
    field('local_item_name', 'Items'),
    field('expiry_date', 'Expiry Date', 'ENTITY_FIELD', 'date'),
    field('unit', 'Unit'),
    field('opening_qty', 'Opening / Original Qty', 'COMPUTED_FIELD', 'decimal'),
    field('current_qty', 'Current Qty', 'COMPUTED_FIELD', 'decimal'),
    field('cms_code', 'CMS Code'),
    field('cms_name', 'CMS Name'),
    field('mapping_status', 'Mapping Status'),
    field('catalogue_price', 'Current Catalogue Price', 'COMPUTED_FIELD', 'decimal'),
    field('accepted_operational_price', 'Accepted Store Price', 'ENTITY_FIELD', 'decimal'),
    field('source_row_no', 'Source Row', 'DISPLAY_HELPER', 'integer'),
    field('source_current_qty', 'Source Current Qty', 'DISPLAY_HELPER', 'decimal'),
    field('source_classification', 'Source Class', 'DISPLAY_HELPER'),
    field('review_reason', 'Review Reason', 'DISPLAY_HELPER'),
  ];
  const col = (field, label, width = 120) => ({ field, label, width });
  window.__presets = [
    {
      view_id: 'main-stock', name: 'Main Stock', preset_type: 'MAIN_STOCK_COMPATIBILITY', provider: 'lot_balance', row_grain: 'PRODUCT_LOT', store_scope: 'MAIN', system_preset: true,
      description: 'Main Stock projection over normalized state.',
      columns: [col('display_no','No.',70), col('local_item_name','Items',260), col('expiry_date','Expiry Date'), col('unit','Unit',90), col('opening_qty','Opening / Original Qty',150), col('current_qty','Current Qty'), col('cms_code','CMS Code'), col('mapping_status','Mapping Status',150)],
    },
    {
      view_id: 'migration-review', name: 'Migration Review', preset_type: 'MIGRATION_REVIEW', provider: 'migration_review', row_grain: 'SOURCE_MAIN_ROW', store_scope: 'MAIN', system_preset: true,
      description: 'Source versus shadow review.',
      columns: [col('source_row_no','Source Row',90), col('local_item_name','Local Item',260), col('source_current_qty','Source Current Qty',140), col('current_qty','Shadow Current Qty',140), col('source_classification','Source Class',120), col('review_reason','Review Reason',300)],
    },
    {
      view_id: 'cms-mapping-review', name: 'CMS Mapping Review', preset_type: 'CMS_MAPPING_REVIEW', provider: 'cms_mapping_review', row_grain: 'PRODUCT_CMS_MAPPING', store_scope: 'ALL', system_preset: true,
      description: 'Current Product to CMS mapping review state.',
      columns: [col('local_item_name','Local Item',260), col('unit','Unit',90), col('cms_code','CMS Code'), col('cms_name','CMS Name',240), col('mapping_status','Mapping Status',160), col('catalogue_price','Current Catalogue Price',150), col('accepted_operational_price','Accepted Store Price',150), col('review_reason','Review Reason',300)],
    },
  ];
  const response = data => new Response(JSON.stringify(data), { status: 200, headers: { 'Content-Type': 'application/json' } });
  window.fetch = async input => {
    const url = typeof input === 'string' ? input : input.url;
    window.__inventoryRequests.push(url);
    if (url === '/dashboard/api/inventory-view/presets') return response({ items: window.__presets, custom_view_persistence: false, database_canonical: false, migration_baseline_accepted: false });
    if (url === '/dashboard/api/inventory-view/registry') return response({ fields: window.__registry, semantic_classes: ['ENTITY_FIELD','COMPUTED_FIELD','COMMAND_EDITABLE_FIELD','DISPLAY_HELPER'], database_canonical: false, migration_baseline_accepted: false });
    if (url.startsWith('/dashboard/api/inventory-view/rows?')) {
      const parsed = new URL(url, 'https://msa.test');
      const preset = parsed.searchParams.get('preset') || 'main-stock';
      const view = window.__presets.find(item => item.view_id === preset);
      const requestedFields = parsed.searchParams.get('fields')?.split(',').filter(Boolean);
      const columns = (requestedFields?.length ? requestedFields.map(key => ({ field: key, label: window.__registry.find(f => f.key === key)?.label || key, width: null })) : view.columns)
        .map(column => ({ ...column, field_definition: window.__registry.find(field => field.key === column.field) }));
      let source;
      if (preset === 'main-stock') {
        source = { display_no: 1, local_item_name: '10cc Syringe', expiry_date: '2031-03-01', unit: 'Pcs', opening_qty: '120.000', current_qty: '120.000', cms_code: 'S10100667', mapping_status: 'REVIEW_REQUIRED' };
      } else if (preset === 'migration-review') {
        source = { source_row_no: 41, local_item_name: 'Bandage- Soft Bandage 6"', source_current_qty: '12.000', current_qty: '0.000', source_classification: 'REVIEW', review_reason: 'duplicate Product+Expiry source key' };
      } else {
        source = { local_item_name: 'Metformin 500mg', unit: 'Tab', cms_code: 'M500', cms_name: 'Metformin 500mg Tablet', mapping_status: 'REVIEW_REQUIRED', catalogue_price: '12.500', accepted_operational_price: null, review_reason: 'price changed in current catalogue' };
      }
      const item = Object.fromEntries(columns.map(column => [column.field, source[column.field] ?? null]));
      return response({ view, columns, items: [item], count: 1, limit: 100, offset: 0, filters: {}, read_only: true, customizable_projection: true, database_canonical: false, migration_baseline_accepted: false });
    }
    return new Response(JSON.stringify({ detail: `Unhandled ${url}` }), { status: 500, headers: { 'Content-Type': 'application/json' } });
  };
});

await page.addScriptTag({ path: script });

await page.getByText('Shadow inventory — not canonical').waitFor({ state: 'visible' });
assert.equal(await page.locator('#legacyInventorySubtree').count(), 0, 'legacy Inventory subtree must be replaced');
await page.getByText('10cc Syringe').waitFor({ state: 'visible' });
assert.equal(await page.locator('#inventoryViewName').textContent(), 'Main Stock');
assert.equal(await page.locator('#inventoryViewTable thead th').first().textContent(), 'No.');
assert.ok((await page.locator('#inventoryViewMeta').textContent()).includes('Read-only shadow projection'));

// One generic component switches presets; no second table is introduced.
await page.locator('#inventoryPresetSelect').selectOption('migration-review');
await page.getByText('Bandage- Soft Bandage 6"').waitFor({ state: 'visible' });
assert.equal(await page.locator('#inventoryViewName').textContent(), 'Migration Review');
assert.equal(await page.locator('#inventoryViewTable').count(), 1);
assert.ok((await page.locator('#inventoryViewTable thead').textContent()).includes('Review Reason'));

// Registry-driven visible-column projection changes table shape without changing preset/domain state.
await page.getByRole('button', { name: 'Columns' }).click();
const checked = page.locator('#inventoryColumnGrid input:checked');
await checked.evaluateAll(inputs => inputs.forEach(input => { input.checked = false; }));
await page.locator('#inventoryColumnGrid input[value="local_item_name"]').check();
await page.locator('#inventoryColumnGrid input[value="review_reason"]').check();
await page.getByRole('button', { name: 'Apply columns' }).click();
await page.waitForFunction(() => [...document.querySelectorAll('#inventoryViewTable thead th')].map(x => x.textContent).join('|') === 'Items|Review Reason');
assert.deepEqual(await page.locator('#inventoryViewTable thead th').allTextContents(), ['Items','Review Reason']);
const latestRowsRequest = await page.evaluate(() => window.__inventoryRequests.filter(url => url.includes('/rows?')).at(-1));
assert.ok(latestRowsRequest.includes('fields=local_item_name%2Creview_reason'));

// CMS Mapping Review is another preset over the exact same renderer/table.
await page.locator('#inventoryPresetSelect').selectOption('cms-mapping-review');
await page.getByRole('cell', { name: 'Metformin 500mg', exact: true }).waitFor({ state: 'visible' });
assert.equal(await page.locator('#inventoryViewName').textContent(), 'CMS Mapping Review');
assert.equal(await page.locator('#inventoryViewTable').count(), 1);
assert.ok((await page.locator('#inventoryViewTable thead').textContent()).includes('Current Catalogue Price'));
assert.ok((await page.locator('#inventoryViewTable thead').textContent()).includes('Accepted Store Price'));

// Mobile contract: controls remain reachable and overflow is owned by the table wrapper, not the page.
assert.equal(await page.locator('#inventoryViewRefresh').isVisible(), true);
const wrapOverflow = await page.locator('.inventory-view-table-wrap').evaluate(el => getComputedStyle(el).overflow);
assert.ok(wrapOverflow === 'auto' || wrapOverflow === 'scroll');
const bannerBox = await page.locator('.inventory-shadow-banner').boundingBox();
assert.ok(bannerBox && bannerBox.width <= 390);

// Search stays on the selected preset and updates the generic API request.
await page.locator('#inventoryViewSearch').fill('metformin');
await page.waitForTimeout(260);
const searchRequest = await page.evaluate(() => window.__inventoryRequests.filter(url => url.includes('/rows?')).at(-1));
assert.ok(searchRequest.includes('preset=cms-mapping-review'));
assert.ok(searchRequest.includes('q=metformin'));

await browser.close();
console.log('inventory_view_engine_browser_smoke=pass viewport=390x844 presets=3 shared_renderer=pass column_projection=pass');
