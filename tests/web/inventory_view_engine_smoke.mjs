import assert from 'node:assert/strict';
import path from 'node:path';
import { chromium } from 'playwright';

const root=process.cwd();
const script=path.join(root,'backend/app/dashboard_assets/dashboard_inventory_views.js');
const stylesheet=path.join(root,'backend/app/dashboard_assets/dashboard_inventory_views.css');
const browser=await chromium.launch({headless:true});
const page=await browser.newPage({viewport:{width:390,height:844}});

await page.setContent(`<main id="msa"><button class="nav-btn" data-view="inventory">Inventory</button><button id="aiWorkspaceNav" type="button">AI Workspace</button><button class="ai-workspace-tab" id="aiChatTab" data-ai-tab="chat" type="button">Chat</button><button class="ai-workspace-tab" id="aiMultiTab" type="button">Multi-Agent</button><article class="ai-chat-panel"><select id="aiAgentSelect"><option value="agent-a">Agent A</option><option value="agent-b">Agent B</option></select><button id="aiNewConversation" type="button">New chat</button><div id="aiConversationList"><div class="ai-conversation-item active" data-ai-conversation-row="old-chat"></div></div><div id="aiChatThread">Existing conversation</div><form id="aiChatForm"><textarea id="aiMessageInput"></textarea><button type="submit">Send</button></form></article><section class="view" data-panel="inventory"><div id="legacyInventorySubtree">legacy</div></section></main>`);
await page.addStyleTag({path:stylesheet});
await page.evaluate(()=>{
  window.__inventoryRequests=[];
  window.__lastReviewContextBody=null;
  window.__aiNavClicks=0;
  window.__chatClicks=0;
  window.__multiClicks=0;
  window.__reviewRunClicks=0;
  window.__newChatClicks=0;
  window.__copiedText='';
  Object.defineProperty(navigator,'clipboard',{configurable:true,value:{writeText:async text=>{window.__copiedText=text}}});
  document.querySelector('#aiWorkspaceNav').addEventListener('click',()=>{window.__aiNavClicks+=1});
  document.querySelector('#aiChatTab').addEventListener('click',()=>{window.__chatClicks+=1});
  document.querySelector('#aiNewConversation').addEventListener('click',()=>{
    window.__newChatClicks+=1;
    const id='new-chat-'+window.__newChatClicks;
    setTimeout(()=>{
      const active=document.querySelector('.ai-conversation-item.active');
      active.dataset.aiConversationRow=id;
      document.querySelector('#aiChatThread').hidden=false;
      document.querySelector('#aiChatForm').hidden=false;
    },25);
  });
  document.querySelector('#aiMultiTab').addEventListener('click',()=>{
    window.__multiClicks+=1;
    setTimeout(()=>{
      if(document.querySelector('#reviewTitle'))return;
      const config=document.createElement('section');config.className='review-config';config.innerHTML='<h3>Review preset & roles</h3>';
      document.querySelector('#msa').appendChild(config);
      const box=document.createElement('section');box.id='fakeMultiReviewComposer';box.className='review-compose';
      box.innerHTML='<div class="review-section-head"><h3>Task & evidence</h3></div><select id="reviewSessionSelect"><option value="">Choose a REVIEW preset…</option><option value="review-a">Review A</option><option value="review-b">Review B</option></select><input id="reviewTitle"><textarea id="reviewTask"></textarea><button id="reviewRun" type="button">Run native review</button>';
      document.querySelector('#msa').appendChild(box);
      box.querySelector('#reviewRun').addEventListener('click',()=>{window.__reviewRunClicks+=1});
    },20);
  });
  const field=(key,label,kind='ENTITY_FIELD',data_type='string')=>({key,label,kind,data_type,editable:false,description:''});
  window.__registry=[field('display_no','No.','DISPLAY_HELPER','integer'),field('product_id','Product ID'),field('lot_id','Lot ID'),field('local_item_name','Items'),field('expiry_date','Expiry Date','ENTITY_FIELD','date'),field('unit','Unit'),field('opening_qty','Opening Qty','COMPUTED_FIELD','decimal'),field('current_qty','Current Qty','COMPUTED_FIELD','decimal'),field('cms_code','CMS Code'),field('cms_name','CMS Name'),field('mapping_status','Mapping Status'),field('catalogue_price','Current Catalogue Price','COMPUTED_FIELD','decimal'),field('accepted_operational_price','Accepted Store Price','ENTITY_FIELD','decimal'),field('source_row_no','Source Row','DISPLAY_HELPER','integer'),field('source_current_qty','Source Current Qty','DISPLAY_HELPER','decimal'),field('source_classification','Source Class','DISPLAY_HELPER'),field('review_reason','Review Reason','DISPLAY_HELPER')];
  const col=(field,label,width=120)=>({field,label,width});
  window.__presets=[
    {view_id:'main-stock',name:'Main Stock',preset_type:'MAIN_STOCK_COMPATIBILITY',provider:'lot_balance',row_grain:'PRODUCT_LOT',store_scope:'MAIN',system_preset:true,description:'Main Stock projection.',columns:[col('display_no','No.',70),col('local_item_name','Items',260),col('current_qty','Current Qty'),col('mapping_status','Mapping Status')]},
    {view_id:'migration-review',name:'Migration Review',preset_type:'MIGRATION_REVIEW',provider:'migration_review',row_grain:'SOURCE_MAIN_ROW',store_scope:'MAIN',system_preset:true,description:'Source versus shadow review.',columns:[col('source_row_no','Source Row',90),col('local_item_name','Local Item',260),col('source_current_qty','Source Current Qty',140),col('current_qty','Shadow Current Qty',140),col('source_classification','Source Class'),col('review_reason','Review Reason',300)]},
    {view_id:'cms-mapping-review',name:'CMS Mapping Review',preset_type:'CMS_MAPPING_REVIEW',provider:'cms_mapping_review',row_grain:'PRODUCT_CMS_MAPPING',store_scope:'ALL',system_preset:true,description:'Current Product to CMS mapping review state.',columns:[col('local_item_name','Local Item',260),col('cms_code','CMS Code'),col('cms_name','CMS Name',240),col('mapping_status','Mapping Status',160),col('catalogue_price','Current Catalogue Price',150),col('accepted_operational_price','Accepted Store Price',150),col('review_reason','Review Reason',300)]}
  ];
  const response=data=>new Response(JSON.stringify(data),{status:200,headers:{'Content-Type':'application/json'}});
  window.fetch=async (input,opts={})=>{
    const url=typeof input==='string'?input:input.url;window.__inventoryRequests.push(url);
    if(url==='/dashboard/api/inventory-view/presets')return response({items:window.__presets});
    if(url==='/dashboard/api/inventory-view/registry')return response({fields:window.__registry});
    if(url==='/dashboard/api/inventory-view/review-context'){
      const body=JSON.parse(opts.body||'{}');window.__lastReviewContextBody=body;
      const reviewReason=JSON.stringify({category:'CONTINUITY_EXACT_NAME_PRICE_SAME',previous_price:'12.500',catalogue_price:'12.500'});
      return response({context_type:'INVENTORY_REVIEW_CONTEXT_V1',context_origin:'SERVER_REHYDRATED_INVENTORY_VIEW',view:{view_id:'cms-mapping-review',name:'CMS Mapping Review',row_grain:'PRODUCT_CMS_MAPPING',store_scope:'ALL',columns:[{field:'local_item_name',label:'Local Item',data_type:'string'},{field:'cms_code',label:'CMS Code',data_type:'string'},{field:'mapping_status',label:'Mapping Status',data_type:'string'},{field:'review_reason',label:'Review Reason',data_type:'string'}]},filters:{q:null,mapping_status:null,source_classification:null,review_reason:null},page:{limit:100,offset:0},selected_indices:body.selected_indices,selected_count:1,rows:[{local_item_name:'Metformin 500mg',cms_code:'M500',mapping_status:'REVIEW_REQUIRED',review_reason:reviewReason}],read_only:true,database_canonical:false,migration_baseline_accepted:false});
    }
    if(url.startsWith('/dashboard/api/inventory-view/rows?')){
      const parsed=new URL(url,'https://msa.test'),preset=parsed.searchParams.get('preset')||'main-stock',view=window.__presets.find(x=>x.view_id===preset),requested=parsed.searchParams.get('fields')?.split(',').filter(Boolean),columns=(requested?.length?requested.map(key=>({field:key,label:window.__registry.find(f=>f.key===key)?.label||key,width:null})):view.columns).map(c=>({...c,field_definition:window.__registry.find(f=>f.key===c.field)}));
      let source;
      if(preset==='main-stock')source={display_no:1,product_id:'p-main',lot_id:'lot-main-1',local_item_name:'10cc Syringe',current_qty:'120.000',mapping_status:'REVIEW_REQUIRED'};
      else if(preset==='migration-review')source={source_row_no:41,local_item_name:'Bandage- Soft Bandage 6"',source_current_qty:'12.000',current_qty:'0.000',source_classification:'REVIEW',mapping_status:'REVIEW_REQUIRED',review_reason:'duplicate Product+Expiry source key'};
      else source={product_id:'p-met',local_item_name:'Metformin 500mg',cms_code:'M500',cms_name:'Metformin 500mg Tablet',mapping_status:'REVIEW_REQUIRED',catalogue_price:'12.500',accepted_operational_price:null,review_reason:JSON.stringify({category:'CONTINUITY_EXACT_NAME_PRICE_SAME',previous_price:'12.500',catalogue_price:'12.500'})};
      const item={...Object.fromEntries(columns.map(c=>[c.field,source[c.field]??null])),product_id:source.product_id,lot_id:source.lot_id,source_row_no:source.source_row_no,mapping_status:source.mapping_status,source_classification:source.source_classification,review_reason:source.review_reason,source_current_qty:source.source_current_qty,current_qty:source.current_qty,cms_code:source.cms_code,cms_name:source.cms_name,catalogue_price:source.catalogue_price,accepted_operational_price:source.accepted_operational_price,local_item_name:source.local_item_name};
      return response({view,columns,items:[item],count:1,limit:100,offset:0,read_only:true,database_canonical:false,migration_baseline_accepted:false});
    }
    return new Response('{}',{status:500});
  };
});

await page.addScriptTag({path:script});
await page.getByText('Shadow inventory — not canonical').waitFor({state:'visible'});
assert.equal(await page.locator('#legacyInventorySubtree').count(),0);
await page.getByText('10cc Syringe').waitFor({state:'visible'});
assert.equal(await page.locator('#inventoryReviewFilters').isHidden(),true);

assert.equal(await page.getByRole('button',{name:'Focus mode'}).isVisible(),true);
await page.getByRole('button',{name:'Focus mode'}).click();
const focusPanel=page.locator('.inventory-focus-mode');
await focusPanel.waitFor({state:'visible'});
const focusBox=await focusPanel.boundingBox();
assert.ok(focusBox&&focusBox.width<=390&&focusBox.height<=844&&focusBox.height>800,'focus mode should occupy nearly the full mobile viewport');
assert.equal(await page.locator('#inventoryFocusToggle').getAttribute('aria-pressed'),'true');
const frozenSelectPosition=await page.locator('#inventoryViewTable thead .inventory-frozen-select').evaluate(el=>getComputedStyle(el).position);
const frozenFirstPosition=await page.locator('#inventoryViewTable thead .inventory-frozen-first').evaluate(el=>getComputedStyle(el).position);
assert.equal(frozenSelectPosition,'sticky');
assert.equal(frozenFirstPosition,'sticky');
await page.locator('#inventorySelectVisible').check();
assert.equal(await page.locator('.inventory-row-check').isChecked(),true,'header checkbox should select visible rows');
assert.equal(await page.getByRole('button',{name:'Clear selection'}).isVisible(),true);
await page.getByRole('button',{name:'Clear selection'}).click();
assert.equal(await page.locator('.inventory-row-check').isChecked(),false,'Clear selection should clear visible row selection');
assert.equal(await page.locator('#inventorySelectionBar').isHidden(),true);
assert.equal((await page.locator('#inventoryDensityToggle').textContent()).trim(),'Compact');
await page.locator('#inventoryDensityToggle').click();
assert.equal(await focusPanel.getAttribute('data-inventory-density'),'compact');
assert.equal((await page.locator('#inventoryDensityToggle').textContent()).trim(),'Comfortable');
await page.locator('#inventoryColumnsToggle').click();
const localOption=page.locator('.inventory-column-option[data-column-key="local_item_name"]');
assert.equal(await localOption.getByRole('button',{name:'Auto-fit'}).isVisible(),true);
await localOption.locator('[data-column-move="up"]').click();
await localOption.locator('[data-column-width]').fill('208');
await page.getByRole('button',{name:'Apply layout'}).click();
await page.waitForFunction(()=>window.__inventoryRequests.filter(x=>x.includes('/rows?')).at(-1)?.includes('fields=local_item_name%2Cdisplay_no%2Ccurrent_qty%2Cmapping_status'));
const itemHeader=page.locator('#inventoryViewTable thead th[data-field="local_item_name"]');
await itemHeader.waitFor({state:'visible'});
const headerLabels=await page.locator('#inventoryViewTable thead th').allTextContents();
assert.equal(headerLabels[1].trim(),'Items','session column move should change projection order');
const itemHeaderStyle=await itemHeader.getAttribute('style');
assert.ok(itemHeaderStyle.includes('208px'),'session column width should apply to the rendered table');
let layoutRequest=await page.evaluate(()=>window.__inventoryRequests.filter(x=>x.includes('/rows?')).at(-1));
assert.ok(layoutRequest.includes('fields=local_item_name%2Cdisplay_no%2Ccurrent_qty%2Cmapping_status'),'layout order should remain a registry-driven fields request');
await page.keyboard.press('Escape');
assert.equal(await page.locator('.inventory-focus-mode').count(),0,'Escape should leave focus mode');

await page.locator('#inventoryPresetSelect').selectOption('migration-review');
await page.getByText('Bandage- Soft Bandage 6"').waitFor({state:'visible'});
assert.equal(await page.locator('#inventoryReviewFilters').isVisible(),true);
assert.ok((await page.locator('#inventoryViewTable tbody tr').first().getAttribute('class')).includes('inventory-row-review'));
await page.locator('#inventoryMappingStatus').selectOption('REVIEW_REQUIRED');
await page.locator('#inventorySourceClassification').selectOption('REVIEW');
await page.locator('#inventoryReviewReason').fill('duplicate');
await page.waitForTimeout(260);
let request=await page.evaluate(()=>window.__inventoryRequests.filter(x=>x.includes('/rows?')).at(-1));
assert.ok(request.includes('mapping_status=REVIEW_REQUIRED'));
assert.ok(request.includes('source_classification=REVIEW'));
assert.ok(request.includes('review_reason=duplicate'));
const filterText=await page.locator('#inventoryActiveFilters').textContent();
assert.ok(filterText.includes('Mapping:'));
assert.ok(filterText.includes('Review Required'));
assert.ok(filterText.includes('Source class:'));
assert.ok(filterText.includes('Review reason:'));
await page.getByRole('button',{name:'Clear Source class filter'}).click();
await page.waitForTimeout(30);
request=await page.evaluate(()=>window.__inventoryRequests.filter(x=>x.includes('/rows?')).at(-1));
assert.ok(request.includes('mapping_status=REVIEW_REQUIRED'));
assert.ok(!request.includes('source_classification='),'clearing one filter chip must preserve the other active filters');
assert.ok(request.includes('review_reason=duplicate'));

await page.locator('.inventory-row-check').check();
assert.equal(await page.locator('#inventorySelectionBar').isVisible(),true);
assert.equal(await page.getByRole('button',{name:'Ask AI'}).isVisible(),true);
assert.equal(await page.getByRole('button',{name:'Deep Review'}).isVisible(),true);
assert.equal(await page.getByRole('button',{name:'Copy TSV'}).isVisible(),true);
await page.getByRole('button',{name:'Copy TSV'}).click();
await page.waitForFunction(()=>window.__copiedText.includes('Bandage- Soft Bandage 6"'));
const copied=await page.evaluate(()=>window.__copiedText);
assert.ok(copied.startsWith('Source Row\tLocal Item'),'TSV copy should include visible column headers in current order');
assert.ok(copied.includes('duplicate Product+Expiry source key'));
const askBox=await page.getByRole('button',{name:'Ask AI'}).boundingBox();
const deepBox=await page.getByRole('button',{name:'Deep Review'}).boundingBox();
const clearBox=await page.getByRole('button',{name:'Clear selection'}).boundingBox();
assert.ok(askBox&&deepBox&&clearBox);
assert.ok(Math.abs(askBox.y-deepBox.y)<2,'Ask AI and Deep Review should align on the same mobile action row');
assert.ok(Math.abs(askBox.width-deepBox.width)<3,'primary review actions should use balanced widths');
assert.ok(clearBox.y>askBox.y,'Clear selection should occupy a clean secondary row on mobile');
await page.locator('#inventoryViewTable tbody tr').first().click();
assert.equal(await page.locator('#inventoryReviewDrawer').isVisible(),true);
assert.ok((await page.locator('#inventoryDrawerBody').textContent()).includes('Source'));
await page.locator('#inventoryDrawerClose').click();

await page.locator('#inventoryPresetSelect').selectOption('cms-mapping-review');
await page.getByRole('cell',{name:'Metformin 500mg',exact:true}).waitFor({state:'visible'});
const reasonCell=page.locator('#inventoryViewTable tbody tr').first().locator('td').last();
assert.equal((await reasonCell.textContent()).trim(),'Continuity: exact name, same price');
await page.locator('#inventoryViewTable tbody tr').first().click();
const drawerText=await page.locator('#inventoryDrawerBody').textContent();
assert.ok(drawerText.includes('Current catalogue price'));
assert.ok(drawerText.includes('Previous Price'));
assert.ok(!drawerText.includes('CONTINUITY_EXACT_NAME_PRICE_SAME'));
const drawerBox=await page.locator('#inventoryReviewDrawer').boundingBox();assert.ok(drawerBox&&drawerBox.width<=390);
await page.locator('#inventoryDrawerClose').click();

await page.locator('.inventory-row-check').check();
await page.getByRole('button',{name:'Ask AI'}).click();
const chatCard=page.locator('.inventory-ai-handoff-card[data-mode="chat"]');
await chatCard.waitFor({state:'visible'});
let handoff=await page.evaluate(()=>({body:window.__lastReviewContextBody,navClicks:window.__aiNavClicks,chatClicks:window.__chatClicks,multiClicks:window.__multiClicks,draft:document.querySelector('#aiMessageInput').value,newChatClicks:window.__newChatClicks,threadHidden:document.querySelector('#aiChatThread').hidden,formHidden:document.querySelector('#aiChatForm').hidden,requests:window.__inventoryRequests.slice()}));
assert.equal(handoff.chatClicks,1,'Ask AI must explicitly route to Chat');
assert.equal(handoff.multiClicks,0,'Ask AI must not open Multi-Agent');
assert.equal(handoff.newChatClicks,0,'Ask AI must not silently create a conversation before agent choice');
assert.equal(handoff.draft,'','old conversation composer must not receive the selected-row prompt');
assert.equal(handoff.threadHidden,true,'existing conversation should be hidden while choosing a fresh-chat agent');
assert.equal(handoff.formHidden,true,'old conversation composer should be unavailable during fresh-chat choice');
assert.equal(handoff.body.preset,'cms-mapping-review');
assert.deepEqual(handoff.body.selected_indices,[0]);
assert.ok(!JSON.stringify(handoff.body).includes('Metformin 500mg'),'client sends selection coordinates, not row facts');
let chatCardText=await chatCard.textContent();
assert.ok(chatCardText.includes('Start a new Inventory chat'));
assert.ok(chatCardText.includes('Metformin 500mg'));
assert.ok(chatCardText.includes('Choose agent'));
const quickAgent=chatCard.locator('[data-inventory-chat-agent]');
assert.equal(await quickAgent.isVisible(),true,'fresh-chat handoff must expose agent choice near the context');
await quickAgent.selectOption('agent-b');
await chatCard.getByRole('button',{name:'Start new chat'}).click();
await page.waitForFunction(()=>document.querySelector('#aiMessageInput').value.includes('Review these 1 selected rows from CMS Mapping Review.'));
handoff=await page.evaluate(()=>({draft:document.querySelector('#aiMessageInput').value,newChatClicks:window.__newChatClicks,agent:document.querySelector('#aiAgentSelect').value,active:document.querySelector('.ai-conversation-item.active')?.dataset.aiConversationRow,threadHidden:document.querySelector('#aiChatThread').hidden,formHidden:document.querySelector('#aiChatForm').hidden,requests:window.__inventoryRequests.slice()}));
assert.equal(handoff.newChatClicks,1,'agent confirmation must create exactly one fresh conversation');
assert.equal(handoff.agent,'agent-b','selected handoff agent must sync to the canonical Chat agent chooser');
assert.ok(handoff.active.startsWith('new-chat-'),'fresh handoff must not remain on the previous conversation');
assert.equal(handoff.threadHidden,false);
assert.equal(handoff.formHidden,false);
assert.ok(handoff.draft.includes('server-rehydrated shadow review evidence'));
chatCardText=await chatCard.textContent();
assert.ok(chatCardText.includes('Not sent yet'));
assert.ok(chatCardText.includes('Fresh chat created'));
assert.ok(!handoff.requests.some(url=>url.includes('/messages')),'Ask AI must still require explicit Send before model execution');

const beforeDeepRequests=await page.evaluate(()=>window.__inventoryRequests.length);
await page.getByRole('button',{name:'Deep Review'}).click();
await page.waitForFunction(()=>document.querySelector('#reviewTask')?.value.includes('Perform a deep multi-agent review of these 1 selected rows from CMS Mapping Review.'));
const deepCard=page.locator('.inventory-ai-handoff-card[data-mode="deep"]');
await deepCard.waitFor({state:'visible'});
let deep=await page.evaluate(()=>({body:window.__lastReviewContextBody,multiClicks:window.__multiClicks,runClicks:window.__reviewRunClicks,title:document.querySelector('#reviewTitle').value,task:document.querySelector('#reviewTask').value,session:document.querySelector('#reviewSessionSelect').value,requests:window.__inventoryRequests.slice()}));
assert.equal(deep.multiClicks,1,'Deep Review opens the existing Multi-Agent tab');
assert.equal(deep.session,'','handoff must not silently choose a REVIEW preset');
assert.ok(deep.title.includes('Deep review · CMS Mapping Review · 1 row'));
assert.ok(deep.task.includes('server-rehydrated shadow review evidence'));
assert.ok(deep.task.includes('Continuity: exact name, same price'));
assert.ok(!deep.task.includes('CONTINUITY_EXACT_NAME_PRICE_SAME'));
let deepCardText=await deepCard.textContent();
assert.ok(deepCardText.includes('Deep Review context ready'));
assert.ok(deepCardText.includes('Metformin 500mg'));
assert.ok(deepCardText.includes('Review not started'));
const quickPreset=deepCard.locator('[data-inventory-review-preset]');
assert.equal(await quickPreset.isVisible(),true,'Deep Review must expose preset choice beside the handoff context');
assert.equal(await deepCard.getByRole('button',{name:'Review roles'}).isVisible(),true);
assert.equal(await deepCard.getByRole('button',{name:'Run native review'}).isVisible(),true);
assert.equal(deep.runClicks,0,'Deep Review handoff must not auto-run native review');
await quickPreset.selectOption('review-a');
assert.equal(await page.locator('#reviewSessionSelect').inputValue(),'review-a','quick preset must sync the canonical REVIEW selector');
assert.equal(await page.evaluate(()=>window.__reviewRunClicks),0,'choosing a quick preset must not execute review');
await deepCard.getByRole('button',{name:'Run native review'}).click();
assert.equal(await page.evaluate(()=>window.__reviewRunClicks),1,'explicit quick Run action must invoke the canonical native review button');
deep=await page.evaluate(()=>({requests:window.__inventoryRequests.slice(),body:window.__lastReviewContextBody}));
assert.ok(deep.requests.length>beforeDeepRequests,'Deep Review still obtains a fresh server-rehydrated context');
assert.ok(!JSON.stringify(deep.body).includes('Metformin 500mg'),'Deep Review client request still sends coordinates, not row facts');

assert.equal(await page.locator('#inventoryViewRefresh').isVisible(),true);
const overflow=await page.locator('.inventory-view-table-wrap').evaluate(el=>getComputedStyle(el).overflow);assert.ok(overflow==='auto'||overflow==='scroll');
const banner=await page.locator('.inventory-shadow-banner').boundingBox();assert.ok(banner&&banner.width<=390);

await browser.close();
console.log('inventory_review_workspace_smoke=pass viewport=390x844 focus_mode=pass select_visible=pass clear_selection=pass density=pass frozen_columns=pass filter_chips=pass session_layout=pass copy_tsv=pass ask_ai_fresh_chat=pass agent_choice=pass auto_send=false deep_review_quick_preset=pass explicit_run=pass presets=3');