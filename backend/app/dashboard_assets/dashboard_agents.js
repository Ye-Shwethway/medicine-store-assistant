(()=>{
  const root=document.querySelector('#msa');
  if(!root||root.dataset.agentsReady)return;
  root.dataset.agentsReady='1';
  const $=s=>root.querySelector(s);
  const $$=s=>[...root.querySelectorAll(s)];
  const live=$('#live');
  const agentList=$('#agentList');
  const sessionList=$('#agentSessionList');
  const agentModal=$('#agentModal');
  const sessionModal=$('#agentSessionModal');
  let agents=[];
  let sessions=[];
  let providers=[];

  function announce(text){if(live)live.textContent=text}
  function escapeHtml(value){return String(value??'').replace(/[&<>'"]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;',"'":'&#39;','"':'&quot;'}[c]))}
  function titleize(value){return String(value||'').toLowerCase().split('_').map(x=>x?x[0].toUpperCase()+x.slice(1):'').join(' ')}
  async function api(path,opts={}){
    const response=await fetch(path,{credentials:'same-origin',headers:{'Content-Type':'application/json',...(opts.headers||{})},...opts});
    let data=null;try{data=await response.json()}catch{}
    if(!response.ok){const err=new Error((data&&data.detail)||('Request failed: '+response.status));err.status=response.status;throw err}
    return data;
  }

  function ensureProviderUi(){
    if($('#providerRegistry'))return;
    const content=$('#agentsContent');
    content?.insertAdjacentHTML('beforeend',
      '<article class="card panel provider-registry" id="providerRegistry">'+
        '<div class="provider-registry-head"><div><h2>Provider Registry</h2><p>Owner-only provider connections and normalized model discovery. Provider health is separate from agent health.</p></div><div class="provider-head-actions"><button class="secondary" id="providersRefresh" type="button">Refresh providers</button><button class="secondary" id="providerCreateOpen" type="button">Add provider</button></div></div>'+
        '<div class="provider-security-note">API credentials are write-only. The browser never receives a saved key back, and PostgreSQL stores only an opaque credential reference.</div>'+
        '<div id="providerList" class="provider-list"><div class="empty-copy">Loading providers…</div></div>'+
      '</article>'
    );
    root.insertAdjacentHTML('beforeend',
      '<div class="agent-modal-back" id="providerModal" role="dialog" aria-modal="true" aria-labelledby="providerModalTitle" hidden><form class="agent-modal-card" id="providerForm" novalidate><div class="agent-modal-head"><div><h2 id="providerModalTitle">Add provider</h2><p>Connect a model provider without exposing its credential after save.</p></div><button class="icon-close" id="providerModalClose" type="button" aria-label="Close provider editor">×</button></div><input id="providerId" type="hidden"><div class="agent-form-grid"><label>Provider name<input id="providerDisplayName" maxlength="100" required></label><label>Provider type<select id="providerKind"><option value="OPENAI">OpenAI</option><option value="GEMINI">Google Gemini</option><option value="OPENROUTER">OpenRouter</option><option value="NANOGPT">NanoGPT</option><option value="OPENAI_COMPATIBLE">Custom OpenAI-compatible</option></select></label><label class="span-2">Base URL<input id="providerBaseUrl" maxlength="500" inputmode="url"><small id="providerBaseHelp">Built-in providers use the verified default unless you supply an override.</small></label><label class="span-2">API credential<input id="providerApiKey" type="password" maxlength="8192" autocomplete="new-password"><small>Write-only. Leave blank when editing to keep the existing credential.</small></label></div><p class="provider-dialog-note">Custom provider URLs must use public HTTPS and cannot resolve to loopback, private, link-local, or metadata-network destinations.</p><p class="form-error" id="providerFormError" role="alert" aria-live="polite"></p><div class="agent-modal-actions"><button class="secondary" id="providerFormCancel" type="button">Cancel</button><button class="primary" id="providerFormSubmit" type="submit">Save provider</button></div></form></div>'+
      '<div class="agent-modal-back" id="providerModelsModal" role="dialog" aria-modal="true" aria-labelledby="providerModelsTitle" hidden><div class="agent-modal-card"><div class="agent-modal-head"><div><h2 id="providerModelsTitle">Provider models</h2><p id="providerModelsSubtitle">Normalized discovered models</p></div><button class="icon-close" id="providerModelsClose" type="button" aria-label="Close provider models">×</button></div><div id="providerModelsList" class="provider-model-table"></div></div></div>'
    );
    $('#providersRefresh')?.addEventListener('click',loadProviders);
    $('#providerCreateOpen')?.addEventListener('click',()=>openProviderModal());
    $('#providerModalClose')?.addEventListener('click',closeProviderModal);
    $('#providerFormCancel')?.addEventListener('click',closeProviderModal);
    $('#providerForm')?.addEventListener('submit',saveProvider);
    $('#providerModelsClose')?.addEventListener('click',closeProviderModels);
    $('#providerList')?.addEventListener('click',event=>{const button=event.target.closest('[data-provider-action]');if(button)providerAction(button)});
    $('#providerModal')?.addEventListener('click',event=>{if(event.target===$('#providerModal'))closeProviderModal()});
    $('#providerModelsModal')?.addEventListener('click',event=>{if(event.target===$('#providerModelsModal'))closeProviderModels()});
  }

  function openAgentsView(event){
    if(event){event.preventDefault();event.stopImmediatePropagation()}
    root.classList.remove('focus','nav-open');
    $$('.view').forEach(x=>x.classList.toggle('active',x.dataset.panel==='agents'));
    $$('.nav-btn').forEach(x=>x.classList.toggle('active',x.dataset.view==='agents'));
    $('#pageTitle').textContent='AI Agent Management';
    $('#pageSubtitle').textContent='Named AI identities, capability policy, providers, and multi-agent sessions';
    announce('AI Agent Management opened');
    loadAll();
  }

  const nav=$('.nav-btn[data-view="agents"]');
  if(nav)nav.addEventListener('click',openAgentsView,true);
  $('#agentCreateOpen')?.classList.add('secondary');
  $('#sessionCreateOpen')?.classList.add('secondary');
  ensureProviderUi();

  function showDenied(show){$('#agentsDenied').hidden=!show;$('#agentsContent').hidden=show}

  async function loadAll(){
    agentList.innerHTML='<div class="empty-copy">Loading agents…</div>';
    sessionList.innerHTML='<div class="empty-copy">Loading sessions…</div>';
    if($('#providerList'))$('#providerList').innerHTML='<div class="empty-copy">Loading providers…</div>';
    try{
      const [agentData,sessionData,providerData]=await Promise.all([api('/dashboard/api/agents'),api('/dashboard/api/agents/sessions/list'),api('/dashboard/api/providers')]);
      showDenied(false);agents=agentData.items||[];sessions=sessionData.items||[];providers=providerData.items||[];renderAgents();renderSessions();renderProviders();renderMetrics();
    }catch(err){
      if(err.status===403){showDenied(true);announce('Access denied');return}
      if(err.status===401){location.assign('/dashboard/login');return}
      agentList.innerHTML='<div class="empty-copy">Unable to load AI agents.</div>';sessionList.innerHTML='<div class="empty-copy">Unable to load multi-agent sessions.</div>';if($('#providerList'))$('#providerList').innerHTML='<div class="empty-copy">Unable to load Provider Registry.</div>';announce(err.message)
    }
  }

  async function loadProviders(){
    const list=$('#providerList');if(!list)return;list.innerHTML='<div class="empty-copy">Loading providers…</div>';
    try{const data=await api('/dashboard/api/providers');providers=data.items||[];renderProviders();announce(providers.length+' providers loaded')}catch(err){list.innerHTML='<div class="empty-copy">Unable to load Provider Registry.</div>';announce(err.message)}
  }

  function renderMetrics(){
    $('#aActive').textContent=agents.filter(x=>x.state==='ACTIVE').length.toLocaleString();
    $('#aDisabled').textContent=agents.filter(x=>x.state==='DISABLED').length.toLocaleString();
    $('#aSessions').textContent=sessions.filter(x=>x.state==='OPEN').length.toLocaleString();
  }

  function capabilityChips(agent){return (agent.capability_scopes||[]).map(scope=>'<span class="agent-chip">'+escapeHtml(scope.replace('mcp:',''))+'</span>').join('')}
  function originLabel(agent){return agent.runtime_mode==='EXTERNAL_MCP_CLIENT'?'Custom MCP':agent.runtime_mode==='EXTERNAL_ACTION_CLIENT'?'Custom Action':agent.runtime_mode==='SYSTEM_AUTOMATION'?'MSA system':'MSA provider'}
  function modelLabel(agent){return agent.runtime_mode==='INTERNAL_MODEL'?'Not assigned':agent.runtime_mode==='SYSTEM_AUTOMATION'?'System-managed':'Client-managed'}

  function renderAgentCard(agent){
    const state=String(agent.state||'UNKNOWN');const stateClass='agent-state-'+state.toLowerCase();let lifecycle='';
    if(state==='ACTIVE')lifecycle='<button class="secondary" data-agent-action="disable" data-agent-id="'+escapeHtml(agent.agent_id)+'">Disable</button>';
    else if(state==='DISABLED')lifecycle='<button class="secondary" data-agent-action="reactivate" data-agent-id="'+escapeHtml(agent.agent_id)+'">Reactivate</button>';
    if(state!=='REVOKED')lifecycle+='<button class="danger-action" data-agent-action="revoke" data-agent-id="'+escapeHtml(agent.agent_id)+'">Revoke</button>';
    return '<div class="agent-card" data-agent-card="'+escapeHtml(agent.agent_id)+'">'+
      '<div class="agent-card-head"><div class="agent-identity"><strong>'+escapeHtml(agent.display_name)+'</strong><span>Call as “'+escapeHtml(agent.call_name)+'”</span></div><span class="agent-chip '+stateClass+'">'+escapeHtml(state)+'</span></div>'+
      '<div class="agent-core-fields"><div class="agent-core-field"><span>Agent name</span><strong>'+escapeHtml(agent.display_name)+'</strong></div><div class="agent-core-field"><span>Origin</span><strong>'+escapeHtml(originLabel(agent))+'</strong></div><div class="agent-core-field"><span>Model</span><strong>'+escapeHtml(modelLabel(agent))+'</strong></div></div>'+
      (agent.description?'<p class="agent-description">'+escapeHtml(agent.description)+'</p>':'')+
      '<div class="agent-meta"><span class="agent-chip">'+escapeHtml(titleize(agent.runtime_mode))+'</span><span class="agent-chip">Ceiling: '+escapeHtml(titleize(agent.authority_ceiling))+'</span><span class="agent-chip">'+escapeHtml(titleize(agent.execution_policy))+'</span><span class="agent-chip">'+escapeHtml(titleize(agent.confirmation_policy))+'</span>'+capabilityChips(agent)+'</div>'+
      '<div class="agent-identity-preview"><strong>Self identity preview:</strong> '+escapeHtml(agent.identity_context)+'</div>'+
      '<div class="agent-card-actions">'+(state!=='REVOKED'?'<button class="secondary" data-agent-action="edit" data-agent-id="'+escapeHtml(agent.agent_id)+'">Edit agent</button>':'')+lifecycle+'</div></div>';
  }

  function renderAgentGroup(title,subtitle,items){
    return '<section class="agent-origin-group"><div class="agent-origin-head"><div><strong>'+escapeHtml(title)+'</strong><span>'+escapeHtml(subtitle)+'</span></div><span class="agent-origin-count">'+items.length+' '+(items.length===1?'agent':'agents')+'</span></div>'+(items.length?items.map(renderAgentCard).join(''):'<div class="agent-empty"><strong>No agents in this origin yet</strong><p>'+escapeHtml(title.startsWith('External')?'Create an External MCP/Action identity for ChatGPT or another connected client.':'Create an Internal model agent now; provider and model assignment is added in F7.2D4.')+'</p></div>')+'</section>';
  }

  function renderAgents(){
    const external=agents.filter(x=>x.runtime_mode==='EXTERNAL_MCP_CLIENT'||x.runtime_mode==='EXTERNAL_ACTION_CLIENT');
    const internal=agents.filter(x=>x.runtime_mode!=='EXTERNAL_MCP_CLIENT'&&x.runtime_mode!=='EXTERNAL_ACTION_CLIENT');
    agentList.innerHTML=renderAgentGroup('External / MCP agents','ChatGPT/custom MCP and other externally hosted agent runtimes.',external)+renderAgentGroup('Internal / provider-backed agents','MSA-managed agents that will receive provider/model assignments.',internal);
  }

  function renderSessions(){
    if(!sessions.length){sessionList.innerHTML='<div class="agent-empty"><strong>No multi-agent sessions yet</strong><p>Create a participant set for future group, comparison, review, or debate workflows.</p></div>';return}
    sessionList.innerHTML=sessions.map(session=>{
      const participants=(session.participants||[]).map(p=>'<span class="agent-participant"><b>'+escapeHtml(p.call_name)+'</b>'+ (p.role_label?' · '+escapeHtml(p.role_label):'') +'</span>').join('')||'<span class="muted">No participants selected</span>';
      const state=session.state||'OPEN';const lifecycle=state==='OPEN'?'<button class="secondary" data-session-action="close" data-session-id="'+escapeHtml(session.session_id)+'">Close</button>':'<button class="secondary" data-session-action="reopen" data-session-id="'+escapeHtml(session.session_id)+'">Reopen</button>';
      return '<div class="agent-session-card" data-session-card="'+escapeHtml(session.session_id)+'"><div class="agent-session-head"><div><strong>'+escapeHtml(session.session_name)+'</strong><span>'+escapeHtml(titleize(session.mode))+' · '+escapeHtml(state)+'</span></div><span class="agent-chip">'+(session.participants||[]).length+' agents</span></div>'+(session.objective?'<p class="agent-description">'+escapeHtml(session.objective)+'</p>':'')+'<div class="agent-participants">'+participants+'</div><div class="agent-session-actions">'+(state==='OPEN'?'<button class="secondary" data-session-action="edit" data-session-id="'+escapeHtml(session.session_id)+'">Edit session</button>':'')+lifecycle+'</div></div>';
    }).join('');
  }

  function providerStatusChips(provider){
    return '<span class="provider-chip '+String(provider.state||'').toLowerCase()+'">'+escapeHtml(provider.state||'UNKNOWN')+'</span><span class="provider-chip '+String(provider.last_connection_status||'').toLowerCase()+'">Connection: '+escapeHtml(titleize(provider.last_connection_status))+'</span><span class="provider-chip">Models: '+Number(provider.model_count||0).toLocaleString()+'</span><span class="provider-chip">Credential: '+(provider.credential_configured?'Configured':'Missing')+'</span>';
  }

  function renderProviders(){
    const list=$('#providerList');if(!list)return;
    if(!providers.length){list.innerHTML='<div class="agent-empty"><strong>No providers yet</strong><p>Add OpenAI, Gemini, OpenRouter, NanoGPT, or a public HTTPS OpenAI-compatible provider.</p></div>';return}
    list.innerHTML=providers.map(provider=>{
      const enabled=provider.state==='ENABLED';const canEnable=provider.credential_configured&&provider.last_connection_status==='HEALTHY'&&provider.last_model_fetch_status==='SUCCESS';
      return '<div class="provider-card" data-provider-card="'+escapeHtml(provider.provider_id)+'"><div class="provider-card-head"><div><strong>'+escapeHtml(provider.display_name)+'</strong><span>'+escapeHtml(titleize(provider.provider_kind))+'</span></div>'+providerStatusChips(provider)+'</div><p class="provider-description provider-url">'+escapeHtml(provider.base_url)+'</p><div class="provider-meta"><span class="provider-chip">Model fetch: '+escapeHtml(titleize(provider.last_model_fetch_status))+'</span>'+(provider.last_error_code?'<span class="provider-chip">Last error: '+escapeHtml(provider.last_error_code)+'</span>':'')+'</div><div class="provider-card-actions"><button class="secondary" data-provider-action="edit" data-provider-id="'+escapeHtml(provider.provider_id)+'">Edit</button><button class="secondary" data-provider-action="test" data-provider-id="'+escapeHtml(provider.provider_id)+'">Test connection</button><button class="secondary" data-provider-action="fetch" data-provider-id="'+escapeHtml(provider.provider_id)+'">Fetch models</button><button class="secondary" data-provider-action="models" data-provider-id="'+escapeHtml(provider.provider_id)+'" '+(provider.model_count?'':'disabled')+'>View models</button>'+(enabled?'<button class="secondary" data-provider-action="disable" data-provider-id="'+escapeHtml(provider.provider_id)+'">Disable</button>':'<button class="secondary" data-provider-action="enable" data-provider-id="'+escapeHtml(provider.provider_id)+'" '+(canEnable?'':'disabled title="Test connection and fetch models first"')+'>Enable</button>')+'</div></div>';
    }).join('');
  }

  function selectedCapabilities(){return $$('#agentForm .agent-capabilities input[type="checkbox"]:checked').map(x=>x.value)}
  function setCapabilities(values){const set=new Set(values||[]);$$('#agentForm .agent-capabilities input[type="checkbox"]').forEach(x=>x.checked=set.has(x.value))}

  function openAgentModal(agent=null){
    $('#agentForm').reset();$('#agentFormError').textContent='';$('#agentId').value=agent?.agent_id||'';$('#agentModalTitle').textContent=agent?'Edit agent':'Create agent';
    $('#agentDisplayName').value=agent?.display_name||'';$('#agentCallName').value=agent?.call_name||'';$('#agentDescription').value=agent?.description||'';$('#agentRuntimeMode').value=agent?.runtime_mode||'INTERNAL_MODEL';$('#agentRuntimeMode').disabled=!!agent;
    $('#agentAuthority').value=agent?.authority_ceiling||'READ';$('#agentExecution').value=agent?.execution_policy||'DELEGATED';$('#agentConfirmation').value=agent?.confirmation_policy||'READ_ONLY';setCapabilities(agent?.capability_scopes||['mcp:read']);
    agentModal.hidden=false;setTimeout(()=>$('#agentDisplayName').focus(),0);
  }
  function closeAgentModal(){agentModal.hidden=true;$('#agentFormError').textContent=''}

  async function saveAgent(event){
    event.preventDefault();const id=$('#agentId').value;const button=$('#agentFormSubmit');$('#agentFormError').textContent='';button.disabled=true;button.textContent='Saving…';
    const payload={display_name:$('#agentDisplayName').value,call_name:$('#agentCallName').value,description:$('#agentDescription').value||null,capability_scopes:selectedCapabilities(),location_scope:{mode:'ALL_READABLE'},authority_ceiling:$('#agentAuthority').value,execution_policy:$('#agentExecution').value,confirmation_policy:$('#agentConfirmation').value};if(!id)payload.runtime_mode=$('#agentRuntimeMode').value;
    try{await api(id?'/dashboard/api/agents/'+encodeURIComponent(id):'/dashboard/api/agents',{method:id?'PATCH':'POST',body:JSON.stringify(payload)});closeAgentModal();announce(id?'Agent updated':'Agent created');await loadAll()}catch(err){$('#agentFormError').textContent=err.message}finally{button.disabled=false;button.textContent='Save agent'}
  }

  async function agentAction(button){
    const action=button.dataset.agentAction;const id=button.dataset.agentId;const agent=agents.find(x=>x.agent_id===id);if(!action||!agent)return;
    if(action==='edit'){openAgentModal(agent);return}
    if(action==='revoke'&&!window.confirm('Permanently revoke “'+agent.display_name+'”? Revoked agents cannot be reactivated.'))return;if(action==='disable'&&!window.confirm('Disable “'+agent.display_name+'”?'))return;button.disabled=true;
    try{await api('/dashboard/api/agents/'+encodeURIComponent(id)+'/'+action,{method:'POST'});announce('Agent '+action+' completed');await loadAll()}catch(err){window.alert(err.message);announce(err.message);button.disabled=false}
  }

  function participantPicker(session=null){
    const current=new Map((session?.participants||[]).map(p=>[p.agent_id,p]));const active=agents.filter(a=>a.state==='ACTIVE');if(!active.length)return '<p class="muted">Create at least one active agent first.</p>';
    return '<div class="session-picker-list">'+active.map((agent,index)=>{const p=current.get(agent.agent_id);const checked=!!p;return '<label class="session-picker-row"><input type="checkbox" data-participant-agent="'+escapeHtml(agent.agent_id)+'" '+(checked?'checked':'')+'><span class="session-picker-copy"><strong>'+escapeHtml(agent.display_name)+'</strong><span>'+escapeHtml(agent.call_name)+' · '+escapeHtml(originLabel(agent))+'</span></span><input type="number" min="0" max="31" aria-label="Position for '+escapeHtml(agent.call_name)+'" data-participant-position="'+escapeHtml(agent.agent_id)+'" value="'+escapeHtml(p?.position??index)+'"><input type="text" maxlength="80" aria-label="Role label for '+escapeHtml(agent.call_name)+'" placeholder="Optional role" data-participant-role="'+escapeHtml(agent.agent_id)+'" value="'+escapeHtml(p?.role_label||'')+'"></label>'}).join('')+'</div>';
  }

  function openSessionModal(session=null){$('#agentSessionForm').reset();$('#agentSessionFormError').textContent='';$('#agentSessionId').value=session?.session_id||'';$('#agentSessionModalTitle').textContent=session?'Edit multi-agent session':'New multi-agent session';$('#agentSessionName').value=session?.session_name||'';$('#agentSessionMode').value=session?.mode||'GROUP';$('#agentSessionObjective').value=session?.objective||'';$('#sessionParticipantPicker').innerHTML=participantPicker(session);sessionModal.hidden=false;setTimeout(()=>$('#agentSessionName').focus(),0)}
  function closeSessionModal(){sessionModal.hidden=true;$('#agentSessionFormError').textContent=''}
  function collectParticipants(){return $$('[data-participant-agent]:checked').map(box=>{const id=box.dataset.participantAgent;return {agent_id:id,position:Number($('[data-participant-position="'+CSS.escape(id)+'"]').value),role_label:$('[data-participant-role="'+CSS.escape(id)+'"]').value||null}}).sort((a,b)=>a.position-b.position).map((p,index)=>({...p,position:index}))}
  async function saveSession(event){event.preventDefault();const id=$('#agentSessionId').value;const button=$('#agentSessionFormSubmit');$('#agentSessionFormError').textContent='';button.disabled=true;button.textContent='Saving…';const payload={session_name:$('#agentSessionName').value,objective:$('#agentSessionObjective').value||null,mode:$('#agentSessionMode').value,participants:collectParticipants()};try{await api(id?'/dashboard/api/agents/sessions/'+encodeURIComponent(id):'/dashboard/api/agents/sessions',{method:id?'PATCH':'POST',body:JSON.stringify(payload)});closeSessionModal();announce(id?'Session updated':'Session created');await loadAll()}catch(err){$('#agentSessionFormError').textContent=err.message}finally{button.disabled=false;button.textContent='Save session'}}
  async function sessionAction(button){const action=button.dataset.sessionAction;const id=button.dataset.sessionId;const session=sessions.find(x=>x.session_id===id);if(!action||!session)return;if(action==='edit'){openSessionModal(session);return}button.disabled=true;try{await api('/dashboard/api/agents/sessions/'+encodeURIComponent(id)+'/'+action,{method:'POST'});announce('Session '+action+' completed');await loadAll()}catch(err){window.alert(err.message);announce(err.message);button.disabled=false}}

  function providerDefaultBase(kind){return kind==='OPENAI'?'https://api.openai.com/v1':kind==='GEMINI'?'https://generativelanguage.googleapis.com/v1beta':kind==='OPENROUTER'?'https://openrouter.ai/api/v1':kind==='NANOGPT'?'https://nano-gpt.com/api/v1':''}
  function syncProviderBaseHelp(){const kind=$('#providerKind')?.value;if(!kind)return;const custom=kind==='OPENAI_COMPATIBLE';$('#providerBaseUrl').required=custom;if(!$('#providerId').value&&!$('#providerBaseUrl').value)$('#providerBaseUrl').placeholder=providerDefaultBase(kind)||'https://provider.example/v1';$('#providerBaseHelp').textContent=custom?'Required public HTTPS API root; MSA calls /models beneath it.':'Verified default: '+providerDefaultBase(kind)+' — override only if needed.'}

  function openProviderModal(provider=null){
    ensureProviderUi();const modal=$('#providerModal');$('#providerForm').reset();$('#providerFormError').textContent='';$('#providerId').value=provider?.provider_id||'';$('#providerModalTitle').textContent=provider?'Edit provider':'Add provider';$('#providerDisplayName').value=provider?.display_name||'';$('#providerKind').value=provider?.provider_kind||'OPENAI';$('#providerKind').disabled=!!provider;$('#providerBaseUrl').value=provider?.base_url||'';$('#providerApiKey').value='';syncProviderBaseHelp();modal.hidden=false;setTimeout(()=>$('#providerDisplayName').focus(),0)
  }
  function closeProviderModal(){const modal=$('#providerModal');if(modal)modal.hidden=true;if($('#providerFormError'))$('#providerFormError').textContent=''}

  async function saveProvider(event){
    event.preventDefault();const id=$('#providerId').value;const button=$('#providerFormSubmit');const error=$('#providerFormError');error.textContent='';button.disabled=true;button.textContent='Saving…';
    const kind=$('#providerKind').value;const base=$('#providerBaseUrl').value.trim();const key=$('#providerApiKey').value;
    try{
      let providerId=id;
      if(id){await api('/dashboard/api/providers/'+encodeURIComponent(id),{method:'PATCH',body:JSON.stringify({display_name:$('#providerDisplayName').value,...(base?{base_url:base}:{})})})}
      else{const created=await api('/dashboard/api/providers',{method:'POST',body:JSON.stringify({display_name:$('#providerDisplayName').value,provider_kind:kind,base_url:base||null})});providerId=created.provider_id}
      if(key)await api('/dashboard/api/providers/'+encodeURIComponent(providerId)+'/credential',{method:'PUT',body:JSON.stringify({api_key:key})});
      closeProviderModal();announce(id?'Provider updated':'Provider created');await loadProviders();
    }catch(err){error.textContent=err.message}finally{button.disabled=false;button.textContent='Save provider'}
  }

  async function providerAction(button){
    const action=button.dataset.providerAction;const id=button.dataset.providerId;const provider=providers.find(x=>x.provider_id===id);if(!action||!provider)return;
    if(action==='edit'){openProviderModal(provider);return}
    if(action==='models'){await openProviderModels(provider);return}
    button.disabled=true;const oldText=button.textContent;button.textContent=action==='test'?'Testing…':action==='fetch'?'Fetching…':oldText;
    try{if(action==='test')await api('/dashboard/api/providers/'+encodeURIComponent(id)+'/test',{method:'POST'});else if(action==='fetch')await api('/dashboard/api/providers/'+encodeURIComponent(id)+'/models/fetch',{method:'POST'});else if(action==='enable'||action==='disable')await api('/dashboard/api/providers/'+encodeURIComponent(id)+'/'+action,{method:'POST'});announce('Provider '+action+' completed');await loadProviders()}catch(err){window.alert(err.message);announce(err.message);button.disabled=false;button.textContent=oldText}
  }

  function capabilityText(value,label){return value===true?label+': yes':value===false?label+': no':label+': unknown'}
  async function openProviderModels(provider){
    const modal=$('#providerModelsModal');const list=$('#providerModelsList');$('#providerModelsTitle').textContent=provider.display_name+' models';$('#providerModelsSubtitle').textContent='Normalized provider catalog. Unknown capability stays unknown.';list.innerHTML='<div class="empty-copy">Loading models…</div>';modal.hidden=false;
    try{const data=await api('/dashboard/api/providers/'+encodeURIComponent(provider.provider_id)+'/models');const items=data.items||[];list.innerHTML=items.length?items.map(model=>'<div class="provider-model-detail"><strong>'+escapeHtml(model.display_name)+'</strong><span class="muted">'+escapeHtml(model.model_id)+'</span><div class="provider-model-caps"><span>'+escapeHtml(capabilityText(model.supports_text,'Text'))+'</span><span>'+escapeHtml(capabilityText(model.supports_vision,'Vision'))+'</span><span>'+escapeHtml(capabilityText(model.supports_tools,'Tools'))+'</span><span>'+escapeHtml(capabilityText(model.supports_structured_output,'Structured'))+'</span>'+(model.context_window?'<span>Context: '+Number(model.context_window).toLocaleString()+'</span>':'')+'</div></div>').join(''):'<div class="agent-empty"><strong>No fetched models</strong><p>Fetch models from the provider first.</p></div>'}catch(err){list.innerHTML='<div class="empty-copy">'+escapeHtml(err.message)+'</div>'}
  }
  function closeProviderModels(){const modal=$('#providerModelsModal');if(modal)modal.hidden=true}

  $('#agentsRefresh')?.addEventListener('click',loadAll);$('#agentCreateOpen')?.addEventListener('click',()=>openAgentModal());$('#sessionCreateOpen')?.addEventListener('click',()=>openSessionModal());
  $('#agentModalClose')?.addEventListener('click',closeAgentModal);$('#agentFormCancel')?.addEventListener('click',closeAgentModal);$('#agentForm')?.addEventListener('submit',saveAgent);
  $('#agentSessionModalClose')?.addEventListener('click',closeSessionModal);$('#agentSessionFormCancel')?.addEventListener('click',closeSessionModal);$('#agentSessionForm')?.addEventListener('submit',saveSession);
  $('#agentsDeniedOverview')?.addEventListener('click',()=>$('.nav-btn[data-view="overview"]')?.click());
  agentList?.addEventListener('click',event=>{const button=event.target.closest('[data-agent-action]');if(button)agentAction(button)});sessionList?.addEventListener('click',event=>{const button=event.target.closest('[data-session-action]');if(button)sessionAction(button)});
  agentModal?.addEventListener('click',event=>{if(event.target===agentModal)closeAgentModal()});sessionModal?.addEventListener('click',event=>{if(event.target===sessionModal)closeSessionModal()});
  $('#providerKind')?.addEventListener('change',syncProviderBaseHelp);
  document.addEventListener('keydown',event=>{if(event.key==='Escape'){if(!agentModal.hidden)closeAgentModal();else if(!sessionModal.hidden)closeSessionModal();else if($('#providerModal')&&!$('#providerModal').hidden)closeProviderModal();else if($('#providerModelsModal')&&!$('#providerModelsModal').hidden)closeProviderModels()}});
})();
