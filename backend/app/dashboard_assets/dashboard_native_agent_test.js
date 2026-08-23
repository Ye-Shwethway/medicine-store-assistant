(()=>{
  const root=document.querySelector('#msa');
  if(!root||root.dataset.nativeAgentTestReady)return;
  root.dataset.nativeAgentTestReady='1';
  const $=s=>root.querySelector(s);
  const $$=s=>[...root.querySelectorAll(s)];
  const live=$('#live');
  let agents=[];
  let activeAgent=null;

  function announce(text){if(live)live.textContent=text}
  function escapeHtml(value){return String(value??'').replace(/[&<>'"]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;',"'":'&#39;','"':'&quot;'}[c]))}
  async function api(path,opts={}){
    const response=await fetch(path,{credentials:'same-origin',headers:{'Content-Type':'application/json',...(opts.headers||{})},...opts});
    let data=null;try{data=await response.json()}catch{}
    if(!response.ok){const detail=data?.detail;const text=typeof detail==='string'?detail:(detail?.code||('Request failed: '+response.status));const err=new Error(text);err.data=data;err.status=response.status;throw err}
    return data;
  }

  function ensureModal(){
    if($('#nativeAgentTestModal'))return;
    root.insertAdjacentHTML('beforeend',
      '<div class="agent-modal-back" id="nativeAgentTestModal" role="dialog" aria-modal="true" aria-labelledby="nativeAgentTestTitle" hidden>'+
        '<div class="agent-modal-card">'+
          '<div class="agent-modal-head"><div><h2 id="nativeAgentTestTitle">Native runtime test</h2><p id="nativeAgentTestSubtitle">Run the selected internal agent directly through the MSA backend.</p></div><button class="icon-close" id="nativeAgentTestClose" type="button" aria-label="Close native runtime test">×</button></div>'+
          '<div class="provider-security-note"><strong>MCP-independent test.</strong> This calls the internal provider-backed runtime directly. MSA typed tools are not attached yet, so this test cannot mutate store data.</div>'+
          '<label class="span-2">Test prompt<textarea id="nativeAgentTestPrompt" rows="5" maxlength="20000">State your configured Medicine Store Assistant agent identity in one short sentence. Then say whether MSA typed tools are available in this invocation.</textarea></label>'+
          '<p class="form-error" id="nativeAgentTestError" role="alert" aria-live="polite"></p>'+
          '<div id="nativeAgentTestResult" class="provider-model-detail" hidden></div>'+
          '<div class="agent-modal-actions"><button class="secondary" id="nativeAgentTestCancel" type="button">Close</button><button class="primary" id="nativeAgentTestRun" type="button">Run native test</button></div>'+
        '</div>'+
      '</div>'
    );
    $('#nativeAgentTestClose')?.addEventListener('click',closeModal);
    $('#nativeAgentTestCancel')?.addEventListener('click',closeModal);
    $('#nativeAgentTestRun')?.addEventListener('click',runTest);
    $('#nativeAgentTestModal')?.addEventListener('click',event=>{if(event.target===$('#nativeAgentTestModal'))closeModal()});
  }

  function closeModal(){
    const modal=$('#nativeAgentTestModal');if(modal)modal.hidden=true;
    activeAgent=null;
    $('#nativeAgentTestError').textContent='';
  }

  function openModal(agent){
    ensureModal();activeAgent=agent;
    $('#nativeAgentTestTitle').textContent='Native runtime test — '+agent.display_name;
    $('#nativeAgentTestSubtitle').textContent='Direct INTERNAL_MODEL invocation · '+agent.call_name;
    $('#nativeAgentTestError').textContent='';
    const result=$('#nativeAgentTestResult');result.hidden=true;result.innerHTML='';
    $('#nativeAgentTestModal').hidden=false;
    setTimeout(()=>$('#nativeAgentTestPrompt')?.focus(),0);
  }

  function renderResult(data){
    const result=$('#nativeAgentTestResult');if(!result)return;
    const attempts=(data.attempts||[]).map(item=>
      '<div class="provider-saved-row"><div><strong>'+escapeHtml(item.assignment_kind+' · '+item.provider_name+' / '+item.model_name)+'</strong><span>'+escapeHtml(item.model_id)+'</span></div><div class="provider-saved-actions"><span class="provider-chip">'+escapeHtml(item.status)+'</span>'+(item.error_code?'<span class="provider-chip">'+escapeHtml(item.error_code)+'</span>':'')+'</div></div>'
    ).join('');
    result.innerHTML=
      '<div class="saved-model-title"><div><strong>Native response</strong><span class="muted">'+escapeHtml(data.agent_display_name)+' · '+escapeHtml(data.transport)+'</span></div><span class="provider-chip healthy">'+escapeHtml(data.status)+'</span></div>'+
      '<p class="provider-description" style="white-space:pre-wrap">'+escapeHtml(data.response)+'</p>'+
      '<div class="provider-model-caps"><span>Provider: '+escapeHtml(data.selected_provider_name)+'</span><span>Model: '+escapeHtml(data.selected_model_name)+'</span><span>Fallback: '+(data.fallback_used?'yes':'no')+'</span><span>Latency: '+Number(data.latency_ms||0).toLocaleString()+' ms</span><span>MCP used: '+(data.mcp_used?'yes':'no')+'</span><span>Tools: '+(data.tool_execution_enabled?'enabled':'not attached')+'</span></div>'+
      (attempts?'<div class="provider-saved-catalog"><div class="provider-saved-head"><strong>Attempt provenance</strong><span>'+Number((data.attempts||[]).length).toLocaleString()+' attempts</span></div><div class="provider-saved-list">'+attempts+'</div></div>':'');
    result.hidden=false;
  }

  async function runTest(){
    if(!activeAgent)return;
    const prompt=$('#nativeAgentTestPrompt')?.value?.trim()||'';
    const error=$('#nativeAgentTestError');const button=$('#nativeAgentTestRun');
    if(!prompt){error.textContent='Enter a test prompt.';return}
    error.textContent='';button.disabled=true;button.textContent='Running…';
    try{
      const data=await api('/dashboard/api/agents/'+encodeURIComponent(activeAgent.agent_id)+'/invoke',{method:'POST',body:JSON.stringify({message:prompt,max_output_tokens:512,temperature:0.1})});
      renderResult(data);announce(activeAgent.display_name+' native runtime test succeeded');
    }catch(err){
      const attempts=err.data?.detail?.attempts||[];
      error.textContent=err.message+(attempts.length?' · '+attempts.map(x=>x.provider_name+'/'+x.model_name+': '+(x.error_code||x.status)).join(' | '):'');
      announce('Native runtime test failed: '+err.message);
    }finally{button.disabled=false;button.textContent='Run native test'}
  }

  async function loadAgents(){
    try{const data=await api('/dashboard/api/agents');agents=data.items||[];installButtons()}catch{}
  }

  function installButtons(){
    const byId=new Map(agents.map(agent=>[agent.agent_id,agent]));
    $$('#agentList [data-agent-card]').forEach(card=>{
      const agent=byId.get(card.dataset.agentCard);if(!agent||agent.runtime_mode!=='INTERNAL_MODEL'||agent.state!=='ACTIVE')return;
      const actions=card.querySelector('.agent-card-actions');if(!actions||actions.querySelector('[data-native-agent-test]'))return;
      const button=document.createElement('button');button.className='secondary';button.type='button';button.dataset.nativeAgentTest=agent.agent_id;button.textContent='Test native runtime';actions.prepend(button);
    });
  }

  function install(){
    ensureModal();
    root.addEventListener('click',event=>{
      const button=event.target.closest('[data-native-agent-test]');if(!button)return;
      event.preventDefault();event.stopImmediatePropagation();
      const agent=agents.find(item=>item.agent_id===button.dataset.nativeAgentTest);if(agent)openModal(agent);
    },true);
    const observer=new MutationObserver(()=>installButtons());
    const list=$('#agentList');if(list)observer.observe(list,{childList:true,subtree:false});
    $('#agentsRefresh')?.addEventListener('click',()=>setTimeout(loadAgents,250));
    loadAgents();
  }

  if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',()=>setTimeout(install,0));else setTimeout(install,0);
})();
