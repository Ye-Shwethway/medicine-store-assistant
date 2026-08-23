(()=>{
  const root=document.querySelector('#msa');
  if(!root||root.dataset.savedModelsReady)return;
  root.dataset.savedModelsReady='1';
  const $=s=>root.querySelector(s);
  const $$=s=>[...root.querySelectorAll(s)];
  const live=$('#live');
  let providers=[];
  let savedByProvider=new Map();
  let currentProvider=null;
  let currentModels=[];
  let currentQuery='';

  function announce(text){if(live)live.textContent=text}
  function escapeHtml(value){return String(value??'').replace(/[&<>'"]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;',"'":'&#39;','"':'&quot;'}[c]))}
  function titleize(value){return String(value||'').toLowerCase().split('_').map(x=>x?x[0].toUpperCase()+x.slice(1):'').join(' ')}
  async function api(path,opts={}){
    const response=await fetch(path,{credentials:'same-origin',headers:{'Content-Type':'application/json',...(opts.headers||{})},...opts});
    let data=null;try{data=await response.json()}catch{}
    if(!response.ok){const detail=data&&data.detail;const message=typeof detail==='string'?detail:(detail?.message||detail?.code||('Request failed: '+response.status));const err=new Error(message);err.status=response.status;throw err}
    return data;
  }

  function ensureAgentBindingFields(){
    if($('#agentProviderId'))return;
    const runtime=$('#agentRuntimeMode');
    if(!runtime)return;
    const runtimeLabel=runtime.closest('label');
    runtimeLabel?.insertAdjacentHTML('afterend',
      '<label id="agentProviderWrap">Primary provider<select id="agentProviderId"><option value="">Select provider…</option></select><small>Primary execution model. Internal agents bind only to Owner-saved provider models.</small></label>'+
      '<label id="agentSavedModelWrap">Primary saved model<select id="agentSavedModelId"><option value="">Select saved model…</option></select><small>Only tested, healthy saved models can be assigned.</small></label>'+
      '<fieldset id="agentFallbackWrap" class="agent-fallback-wrap"><legend>Fallback models</legend><div class="agent-fallback-head"><small>Optional ordered chain used only when the primary attempt fails.</small><button id="agentFallbackAdd" class="secondary compact" type="button">Add fallback</button></div><div id="agentFallbackList" class="agent-fallback-list"></div><small class="agent-fallback-help">Up to 5 fallbacks. Order matters.</small></fieldset>'
    );
    $('#agentProviderId')?.addEventListener('change',()=>syncAgentSavedModelOptions());
    $('#agentFallbackAdd')?.addEventListener('click',()=>addFallbackRow());
    runtime.addEventListener('change',syncAgentBindingVisibility);
    syncAgentBindingVisibility();
  }

  function syncAgentBindingVisibility(){
    ensureAgentBindingFields();
    const internal=$('#agentRuntimeMode')?.value==='INTERNAL_MODEL';
    ['#agentProviderWrap','#agentSavedModelWrap','#agentFallbackWrap'].forEach(selector=>{const node=$(selector);if(node)node.hidden=!internal});
    const primaryProvider=$('#agentProviderId');const primaryModel=$('#agentSavedModelId');
    if(primaryProvider)primaryProvider.disabled=!internal;
    if(primaryModel)primaryModel.disabled=!internal;
    $$('#agentFallbackList select,#agentFallbackList button').forEach(node=>node.disabled=!internal);
    if(!internal){if(primaryProvider)primaryProvider.value='';if(primaryModel)primaryModel.value='';renderFallbackRows([]);return}
    syncAgentProviderOptions();
  }

  function providerSavedModels(providerId){return savedByProvider.get(providerId)||[]}
  function assignableSavedModels(providerId){
    return providerSavedModels(providerId).filter(x=>x.state==='ACTIVE'&&x.last_test_status==='HEALTHY'&&x.currently_discovered!==false);
  }
  function usableProviders(){return providers.filter(p=>p.state==='ENABLED'&&assignableSavedModels(p.provider_id).length>0)}
  function providerForSavedModel(savedModelId){
    for(const [providerId,items] of savedByProvider.entries())if(items.some(item=>item.saved_model_id===savedModelId))return providerId;
    return '';
  }

  function providerOptions(selected=''){
    return '<option value="">Select provider…</option>'+usableProviders().map(p=>'<option value="'+escapeHtml(p.provider_id)+'" '+(p.provider_id===selected?'selected':'')+'>'+escapeHtml(p.display_name)+'</option>').join('');
  }
  function modelOptions(providerId,selected=''){
    return '<option value="">Select saved model…</option>'+assignableSavedModels(providerId).map(m=>'<option value="'+escapeHtml(m.saved_model_id)+'" '+(m.saved_model_id===selected?'selected':'')+'>'+escapeHtml(m.display_name)+' — '+escapeHtml(m.model_id)+'</option>').join('');
  }

  function syncAgentProviderOptions(selected=''){
    const select=$('#agentProviderId');if(!select)return;
    const current=selected||select.value;
    select.innerHTML=providerOptions(current);
    if(current)select.value=current;
    syncAgentSavedModelOptions();
  }

  function syncAgentSavedModelOptions(selected=''){
    const select=$('#agentSavedModelId');if(!select)return;
    const providerId=$('#agentProviderId')?.value||'';
    const current=selected||select.value;
    select.innerHTML=modelOptions(providerId,current);
    if(current)select.value=current;
  }

  function fallbackRowHtml(providerId='',savedModelId=''){
    return '<div class="agent-fallback-row">'+
      '<div class="agent-fallback-order" aria-hidden="true"></div>'+
      '<select class="agent-fallback-provider" aria-label="Fallback provider">'+providerOptions(providerId)+'</select>'+
      '<select class="agent-fallback-model" aria-label="Fallback saved model">'+modelOptions(providerId,savedModelId)+'</select>'+
      '<div class="agent-fallback-actions"><button class="secondary compact" type="button" data-fallback-move="up" aria-label="Move fallback up">↑</button><button class="secondary compact" type="button" data-fallback-move="down" aria-label="Move fallback down">↓</button><button class="secondary compact danger-text" type="button" data-fallback-remove aria-label="Remove fallback">Remove</button></div>'+
    '</div>';
  }
  function renumberFallbackRows(){
    $$('#agentFallbackList .agent-fallback-row').forEach((row,index)=>{const badge=row.querySelector('.agent-fallback-order');if(badge)badge.textContent='Fallback '+(index+1)});
  }
  function renderFallbackRows(assignments=[]){
    const list=$('#agentFallbackList');if(!list)return;
    list.innerHTML=assignments.slice(0,5).map(item=>fallbackRowHtml(item.provider_id||providerForSavedModel(item.saved_model_id),item.saved_model_id||'')).join('');
    renumberFallbackRows();
  }
  function addFallbackRow(){
    const list=$('#agentFallbackList');if(!list)return;
    if(list.querySelectorAll('.agent-fallback-row').length>=5){announce('A maximum of 5 fallback models is supported.');return}
    list.insertAdjacentHTML('beforeend',fallbackRowHtml());renumberFallbackRows();
  }
  function fallbackSavedModelIds(){
    return $$('#agentFallbackList .agent-fallback-row').map(row=>row.querySelector('.agent-fallback-model')?.value||'').filter(Boolean);
  }

  async function loadProvidersAndSaved(){
    const data=await api('/dashboard/api/providers');
    providers=data.items||[];
    const pairs=await Promise.all(providers.map(async provider=>{
      try{const saved=await api('/dashboard/api/providers/'+encodeURIComponent(provider.provider_id)+'/saved-models');return [provider.provider_id,saved.items||[]]}
      catch{return [provider.provider_id,[]]}
    }));
    savedByProvider=new Map(pairs);
    syncAgentProviderOptions();
    $$('#agentFallbackList .agent-fallback-row').forEach(row=>{
      const provider=row.querySelector('.agent-fallback-provider');const model=row.querySelector('.agent-fallback-model');
      const providerId=provider?.value||providerForSavedModel(model?.value||'');if(provider){provider.innerHTML=providerOptions(providerId);provider.value=providerId}if(model){const selected=model.value;model.innerHTML=modelOptions(providerId,selected);model.value=selected}
    });
    renderProviderSavedCatalogs();
  }

  function savedStateLabel(item){
    if(item.currently_discovered===false)return 'Stale / not discovered';
    if(item.last_test_status!=='HEALTHY')return 'Needs retest';
    return titleize(item.state||'ACTIVE');
  }

  function renderProviderSavedCatalogs(){
    $$('#providerList [data-provider-card]').forEach(card=>{
      const providerId=card.dataset.providerCard;
      const items=providerSavedModels(providerId);
      let box=card.querySelector('.provider-saved-catalog');
      if(!box){box=document.createElement('div');box.className='provider-saved-catalog';card.appendChild(box)}
      box.innerHTML='<div class="provider-saved-head"><strong>Saved model catalog</strong><span>'+items.length.toLocaleString()+' saved</span></div>'+
        (items.length?'<div class="provider-saved-list">'+items.map(item=>'<div class="provider-saved-row"><div><strong>'+escapeHtml(item.display_name)+'</strong><span>'+escapeHtml(item.model_id)+'</span></div><div class="provider-saved-actions"><span class="provider-chip">'+escapeHtml(savedStateLabel(item))+'</span><button class="secondary compact" type="button" data-saved-remove="'+escapeHtml(item.saved_model_id)+'" data-provider-id="'+escapeHtml(providerId)+'">Remove</button></div></div>').join('')+'</div>':'<p class="muted">No approved models yet. Open View models, test a candidate, then save it.</p>');
    });
  }

  function priceText(value){const n=Number(value);return Number.isFinite(n)?'$'+n.toLocaleString(undefined,{maximumFractionDigits:6})+' / 1M':'Unknown'}
  function capabilityText(value,label){return value===true?label+': yes':value===false?label+': no':label+': unknown'}
  function billingText(model){const tier=model.provider_metadata?.billing_tier;return tier==='SUBSCRIPTION_INCLUDED'?'Subscription included':tier==='PAID_ONLY'?'Paid only':'Billing unknown'}

  function renderModelBrowser(){
    const list=$('#providerModelsList');if(!list)return;
    const query=currentQuery.trim().toLowerCase();
    const filtered=currentModels.filter(model=>!query||String(model.display_name||'').toLowerCase().includes(query)||String(model.model_id||'').toLowerCase().includes(query));
    const count=$('#providerModelCount');if(count)count.textContent=filtered.length.toLocaleString()+' of '+currentModels.length.toLocaleString()+' models';
    if(!filtered.length){list.innerHTML='<div class="agent-empty"><strong>No matching models</strong><p>Try a shorter model family or provider prefix.</p></div>';return}
    list.innerHTML=filtered.map(model=>{
      const meta=model.provider_metadata||{};const caps=meta.capabilities||{};const pricing=meta.pricing||{};
      const saved=!!model.saved_model_id;const healthy=model.last_test_status==='HEALTHY';
      const testStatus=healthy?'Tested healthy':model.last_test_status==='ERROR'?'Test failed':'Not tested';
      const reasoning=Object.prototype.hasOwnProperty.call(caps,'reasoning')?'<span>'+escapeHtml(capabilityText(caps.reasoning,'Reasoning'))+'</span>':'';
      return '<div class="provider-model-detail saved-model-candidate" data-provider-model-id="'+escapeHtml(model.provider_model_id)+'">'+
        '<div class="saved-model-title"><div><strong>'+escapeHtml(model.display_name)+'</strong><span class="muted">'+escapeHtml(model.model_id)+'</span></div>'+(saved?'<span class="provider-chip enabled">Saved</span>':'')+'</div>'+
        '<div class="provider-model-caps"><span>'+escapeHtml(billingText(model))+'</span><span>Input: '+escapeHtml(priceText(pricing.prompt))+'</span><span>Output: '+escapeHtml(priceText(pricing.completion))+'</span></div>'+
        '<div class="provider-model-caps"><span>'+escapeHtml(capabilityText(model.supports_text,'Text'))+'</span><span>'+escapeHtml(capabilityText(model.supports_vision,'Vision'))+'</span><span>'+escapeHtml(capabilityText(model.supports_tools,'Tools'))+'</span><span>'+escapeHtml(capabilityText(model.supports_structured_output,'Structured'))+'</span>'+reasoning+(model.context_window?'<span>Context: '+Number(model.context_window).toLocaleString()+'</span>':'')+(model.max_output_tokens?'<span>Max output: '+Number(model.max_output_tokens).toLocaleString()+'</span>':'')+'</div>'+
        (meta.description?'<p class="provider-description">'+escapeHtml(meta.description)+'</p>':'')+
        '<div class="saved-model-candidate-actions"><span class="provider-chip '+(healthy?'healthy':model.last_test_status==='ERROR'?'error':'')+'">'+escapeHtml(testStatus)+'</span><button class="secondary" type="button" data-model-test="'+escapeHtml(model.provider_model_id)+'">Test model</button><button class="primary" type="button" data-model-save="'+escapeHtml(model.provider_model_id)+'" '+(healthy&&!saved?'':'disabled')+'>'+(saved?'Saved':'Save to catalog')+'</button></div>'+
      '</div>';
    }).join('');
  }

  async function openEnhancedModelBrowser(providerId){
    await loadProvidersAndSaved();currentProvider=providers.find(p=>p.provider_id===providerId)||null;if(!currentProvider)return;
    const modal=$('#providerModelsModal');const controls=$('#providerModelsControls');const list=$('#providerModelsList');
    $('#providerModelsTitle').textContent=currentProvider.display_name+' models';
    $('#providerModelsSubtitle').textContent='Discover → test → save. Only saved, healthy models can be assigned to internal agents.';
    controls.innerHTML='<div class="toolbar saved-model-toolbar"><input id="providerModelSearch" type="search" placeholder="Search model name or ID…" aria-label="Search provider models"><span id="providerModelCount" class="muted"></span></div>';
    list.innerHTML='<div class="empty-copy">Loading models…</div>';modal.hidden=false;currentQuery='';
    $('#providerModelSearch')?.addEventListener('input',event=>{currentQuery=event.target.value||'';renderModelBrowser()});
    try{const data=await api('/dashboard/api/providers/'+encodeURIComponent(providerId)+'/catalog-models');currentModels=data.items||[];renderModelBrowser();setTimeout(()=>$('#providerModelSearch')?.focus(),0)}catch(err){list.innerHTML='<div class="empty-copy">'+escapeHtml(err.message)+'</div>'}
  }

  async function handleModelAction(button){
    if(!currentProvider)return;const providerId=currentProvider.provider_id;const providerModelId=button.dataset.modelTest||button.dataset.modelSave;const model=currentModels.find(x=>x.provider_model_id===providerModelId);if(!model)return;
    const original=button.textContent;button.disabled=true;
    try{
      if(button.dataset.modelTest){button.textContent='Testing…';const result=await api('/dashboard/api/providers/'+encodeURIComponent(providerId)+'/models/'+encodeURIComponent(providerModelId)+'/test',{method:'POST'});model.last_test_status='HEALTHY';model.last_test_error_code=null;model.last_tested_at=new Date().toISOString();announce(model.display_name+' tested successfully in '+Number(result.latency_ms||0).toLocaleString()+' ms')}
      else{button.textContent='Saving…';const saved=await api('/dashboard/api/providers/'+encodeURIComponent(providerId)+'/models/'+encodeURIComponent(providerModelId)+'/save',{method:'POST'});model.saved_model_id=saved.saved_model_id;model.saved_model_state=saved.state;model.saved_test_status=saved.last_test_status;announce(model.display_name+' saved to provider catalog');await loadProvidersAndSaved()}
      renderModelBrowser();
    }catch(err){window.alert(err.message);announce(err.message);button.disabled=false;button.textContent=original}
  }

  async function removeSavedModel(button){
    const providerId=button.dataset.providerId;const savedModelId=button.dataset.savedRemove;if(!providerId||!savedModelId)return;if(!window.confirm('Remove this model from the saved provider catalog?'))return;
    button.disabled=true;try{await api('/dashboard/api/providers/'+encodeURIComponent(providerId)+'/saved-models/'+encodeURIComponent(savedModelId),{method:'DELETE'});announce('Saved model removed');await loadProvidersAndSaved()}catch(err){window.alert(err.message);announce(err.message);button.disabled=false}
  }

  async function hydrateAgentAssignment(agentId){
    ensureAgentBindingFields();
    try{
      await loadProvidersAndSaved();
      const data=await api('/dashboard/api/agents/'+encodeURIComponent(agentId)+'/model-assignments');
      const primary=data.primary;
      if(!primary){syncAgentProviderOptions();renderFallbackRows([]);return}
      syncAgentProviderOptions(primary.provider_id);$('#agentProviderId').value=primary.provider_id;syncAgentSavedModelOptions(primary.saved_model_id);$('#agentSavedModelId').value=primary.saved_model_id;
      renderFallbackRows(data.fallbacks||[]);
    }catch(err){announce(err.message)}
  }

  async function hydrateAgentCards(){
    const cards=$$('#agentList [data-agent-card]');
    await Promise.all(cards.map(async card=>{
      const agentId=card.dataset.agentCard;
      try{
        const data=await api('/dashboard/api/agents/'+encodeURIComponent(agentId)+'/model-assignments');const primary=data.primary;if(!primary)return;
        const fields=card.querySelectorAll('.agent-core-field');if(fields[2])fields[2].querySelector('strong').textContent=primary.provider_name+' / '+primary.model_name+(data.fallback_count?' · +'+data.fallback_count+' fallback'+(data.fallback_count===1?'':'s'):'');
      }catch{}
    }));
  }

  async function saveAgentWithBinding(event){
    event.preventDefault();event.stopImmediatePropagation();
    const form=event.currentTarget;const id=$('#agentId').value;const button=$('#agentFormSubmit');const error=$('#agentFormError');error.textContent='';button.disabled=true;button.textContent='Saving…';
    const capabilities=$$('#agentForm .agent-capabilities input[type="checkbox"]:checked').map(x=>x.value);
    const payload={display_name:$('#agentDisplayName').value,call_name:$('#agentCallName').value,description:$('#agentDescription').value||null,capability_scopes:capabilities,location_scope:{mode:'ALL_READABLE'},authority_ceiling:$('#agentAuthority').value,execution_policy:$('#agentExecution').value,confirmation_policy:$('#agentConfirmation').value};
    if(!id)payload.runtime_mode=$('#agentRuntimeMode').value;
    try{
      const agent=await api(id?'/dashboard/api/agents/'+encodeURIComponent(id):'/dashboard/api/agents',{method:id?'PATCH':'POST',body:JSON.stringify(payload)});const agentId=id||agent.agent_id;
      if($('#agentRuntimeMode').value==='INTERNAL_MODEL'){
        const primarySavedModelId=$('#agentSavedModelId')?.value||'';const fallbackIds=fallbackSavedModelIds();
        if(primarySavedModelId)await api('/dashboard/api/agents/'+encodeURIComponent(agentId)+'/model-assignments',{method:'PUT',body:JSON.stringify({primary_saved_model_id:primarySavedModelId,fallback_saved_model_ids:fallbackIds})});
        else if(id)await api('/dashboard/api/agents/'+encodeURIComponent(agentId)+'/model-assignments',{method:'DELETE'});
      }
      form.closest('.agent-modal-back').hidden=true;announce(id?'Agent updated':'Agent created');$('#agentsRefresh')?.click();
    }catch(err){error.textContent=err.message}finally{button.disabled=false;button.textContent='Save agent'}
  }

  function install(){
    ensureAgentBindingFields();loadProvidersAndSaved().catch(()=>{});$('#agentForm')?.addEventListener('submit',saveAgentWithBinding,true);
    root.addEventListener('change',event=>{
      const provider=event.target.closest('.agent-fallback-provider');if(!provider)return;const row=provider.closest('.agent-fallback-row');const model=row?.querySelector('.agent-fallback-model');if(model){model.innerHTML=modelOptions(provider.value,'');model.value=''}
    });
    root.addEventListener('click',event=>{
      const view=event.target.closest('[data-provider-action="models"]');if(view){event.preventDefault();event.stopImmediatePropagation();openEnhancedModelBrowser(view.dataset.providerId).catch(err=>announce(err.message));return}
      const modelAction=event.target.closest('[data-model-test],[data-model-save]');if(modelAction){event.preventDefault();handleModelAction(modelAction);return}
      const remove=event.target.closest('[data-saved-remove]');if(remove){event.preventDefault();removeSavedModel(remove);return}
      const fallbackRemove=event.target.closest('[data-fallback-remove]');if(fallbackRemove){event.preventDefault();fallbackRemove.closest('.agent-fallback-row')?.remove();renumberFallbackRows();return}
      const move=event.target.closest('[data-fallback-move]');if(move){event.preventDefault();const row=move.closest('.agent-fallback-row');if(!row)return;if(move.dataset.fallbackMove==='up'&&row.previousElementSibling)row.parentNode.insertBefore(row,row.previousElementSibling);if(move.dataset.fallbackMove==='down'&&row.nextElementSibling)row.parentNode.insertBefore(row.nextElementSibling,row);renumberFallbackRows();return}
      const edit=event.target.closest('[data-agent-action="edit"]');if(edit){setTimeout(()=>hydrateAgentAssignment(edit.dataset.agentId),0);return}
      if(event.target.closest('#agentCreateOpen')){setTimeout(()=>{loadProvidersAndSaved().then(()=>{syncAgentBindingVisibility();syncAgentProviderOptions();renderFallbackRows([])}).catch(err=>announce(err.message))},0)}
    },true);
    const providerObserver=new MutationObserver(()=>renderProviderSavedCatalogs());if($('#providerList'))providerObserver.observe($('#providerList'),{childList:true,subtree:true});
    const agentObserver=new MutationObserver(()=>hydrateAgentCards());if($('#agentList'))agentObserver.observe($('#agentList'),{childList:true,subtree:true});
    $('#providersRefresh')?.addEventListener('click',()=>setTimeout(()=>loadProvidersAndSaved().catch(()=>{}),250));
    $('#agentsRefresh')?.addEventListener('click',()=>setTimeout(()=>{loadProvidersAndSaved().catch(()=>{});hydrateAgentCards()},250));hydrateAgentCards();
  }

  if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',()=>setTimeout(install,0));else setTimeout(install,0);
})();