(()=>{
  const root=document.querySelector('#msa');
  if(!root||root.dataset.mcpBindingReady)return;
  root.dataset.mcpBindingReady='1';
  const $=s=>root.querySelector(s);
  const $$=s=>[...root.querySelectorAll(s)];
  const live=$('#live');
  let grants=[];
  let agents=[];

  function announce(text){if(live)live.textContent=text}
  function escapeHtml(value){return String(value??'').replace(/[&<>'"]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;',"'":'&#39;','"':'&quot;'}[c]))}
  async function api(path,opts={}){
    const response=await fetch(path,{credentials:'same-origin',headers:{'Content-Type':'application/json',...(opts.headers||{})},...opts});
    let data=null;try{data=await response.json()}catch{}
    if(!response.ok){throw new Error((data&&data.detail)||('Request failed: '+response.status))}
    return data;
  }

  function grantLabel(item){
    const base=item.client_name||item.client_id||'MCP client';
    return base+(item.authorizing_username?' · '+item.authorizing_username:'');
  }

  function bindingForAgent(agentId){return grants.find(x=>x.agent_id===agentId)||null}

  function render(){
    const externalIds=new Set(agents.filter(x=>x.runtime_mode==='EXTERNAL_MCP_CLIENT').map(x=>x.agent_id));
    $$('#agentList [data-agent-card]').forEach(card=>{
      const agentId=card.dataset.agentCard;
      let box=card.querySelector('.mcp-binding-box');
      if(!externalIds.has(agentId)){box?.remove();return}
      const current=bindingForAgent(agentId);
      if(!box){box=document.createElement('div');box.className='mcp-binding-box';const actions=card.querySelector('.agent-card-actions');card.insertBefore(box,actions||null)}
      const options=grants.map(item=>'<option value="'+escapeHtml(item.grant_id)+'" '+(current&&item.grant_id===current.grant_id?'selected':'')+'>'+escapeHtml(grantLabel(item))+(item.agent_id&&item.agent_id!==agentId?' — bound to '+escapeHtml(item.agent_call_name||item.agent_display_name||'another agent'):'')+'</option>').join('');
      box.innerHTML='<div class="mcp-binding-head"><div><strong>MCP connection</strong><span>Transport identity → named MSA agent</span></div><span>'+(current?'BOUND':'UNBOUND')+'</span></div>'+
        '<div class="mcp-binding-controls"><select data-mcp-grant-select aria-label="MCP connection"><option value="">Select active MCP connection…</option>'+options+'</select><button class="primary" type="button" data-mcp-bind="'+escapeHtml(agentId)+'" '+(grants.length?'':'disabled')+'>'+(current?'Rebind':'Bind')+'</button>'+(current?'<button class="secondary" type="button" data-mcp-unbind="'+escapeHtml(current.grant_id)+'">Unbind</button>':'')+'</div>'+
        '<div class="mcp-binding-meta">'+(current?'Client: '+escapeHtml(current.client_name||current.client_id)+' · Effective named actor: '+escapeHtml(current.agent_display_name||current.agent_call_name||'configured agent'):'OAuth stays connected when unbound; calls are not attributed to a named agent until a binding exists.')+'</div>';
    });
  }

  async function load(){
    try{
      const [grantData,agentData]=await Promise.all([api('/dashboard/api/mcp-bindings'),api('/dashboard/api/agents')]);
      grants=grantData.items||[];agents=agentData.items||[];render();
    }catch(err){announce(err.message)}
  }

  root.addEventListener('click',async event=>{
    const bind=event.target.closest('[data-mcp-bind]');
    if(bind){
      const card=bind.closest('[data-agent-card]');const select=card?.querySelector('[data-mcp-grant-select]');const grantId=select?.value||'';
      if(!grantId){announce('Select an active MCP connection first');return}
      bind.disabled=true;
      try{await api('/dashboard/api/mcp-bindings',{method:'PUT',body:JSON.stringify({grant_id:grantId,agent_id:bind.dataset.mcpBind})});announce('MCP connection bound to named agent');await load()}catch(err){window.alert(err.message);announce(err.message);bind.disabled=false}
      return;
    }
    const unbind=event.target.closest('[data-mcp-unbind]');
    if(unbind){
      unbind.disabled=true;
      try{await api('/dashboard/api/mcp-bindings/'+encodeURIComponent(unbind.dataset.mcpUnbind),{method:'DELETE'});announce('MCP connection unbound');await load()}catch(err){window.alert(err.message);announce(err.message);unbind.disabled=false}
    }
  });

  const list=$('#agentList');
  if(list)new MutationObserver(()=>setTimeout(()=>render(),0)).observe(list,{childList:true,subtree:false});
  $('#agentsRefresh')?.addEventListener('click',()=>setTimeout(load,250));
  if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',()=>setTimeout(load,0));else setTimeout(load,0);
})();