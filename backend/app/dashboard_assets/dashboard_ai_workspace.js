(()=>{
  const root=document.querySelector('#msa');
  if(!root||root.dataset.aiWorkspaceReady)return;
  root.dataset.aiWorkspaceReady='1';
  const $=s=>root.querySelector(s);
  const $$=s=>[...root.querySelectorAll(s)];
  const nav=$('#aiWorkspaceNav');
  const panel=$('[data-panel="ai-workspace"]');
  if(!nav||!panel)return;

  let access=null;
  let agents=[];
  let conversations=[];
  let currentConversationId=null;
  let busy=false;

  const escapeHtml=value=>String(value??'').replace(/[&<>'"]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;',"'":'&#39;','"':'&quot;'}[c]));
  async function api(path,opts={}){
    const response=await fetch(path,{credentials:'same-origin',headers:{'Content-Type':'application/json',...(opts.headers||{})},...opts});
    let data=null;try{data=await response.json()}catch{}
    if(!response.ok){
      let message='Request failed: '+response.status;
      if(data&&data.detail){message=typeof data.detail==='string'?data.detail:(data.detail.message||data.detail.code||message)}
      const err=new Error(message);err.status=response.status;err.data=data;throw err;
    }
    return data;
  }

  function openWorkspace(){
    root.classList.remove('focus','nav-open');
    $$('.view').forEach(x=>x.classList.toggle('active',x.dataset.panel==='ai-workspace'));
    $$('.nav-btn').forEach(x=>x.classList.remove('active'));
    nav.classList.add('active');
    $('#pageTitle').textContent='AI Workspace';
    $('#pageSubtitle').textContent='Chat with native Medicine Store Assistant agents';
    loadWorkspace();
  }

  function renderBlocked(reason){
    $('#aiWorkspaceBody').innerHTML='<div class="ai-access-blocked"><strong>AI Chat is unavailable</strong><p>'+escapeHtml(reason||'AI Chat is not enabled for this account.')+'</p><small>No provider request was made.</small></div>';
  }

  function renderAgentOptions(){
    const select=$('#aiAgentSelect');
    if(!select)return;
    const current=select.value;
    select.innerHTML=agents.length?agents.map(a=>'<option value="'+escapeHtml(a.agent_id)+'">'+escapeHtml(a.display_name)+' · '+escapeHtml(a.call_name)+'</option>').join(''):'<option value="">No available internal agents</option>';
    if(current&&agents.some(a=>a.agent_id===current))select.value=current;
  }

  function renderConversations(){
    const list=$('#aiConversationList');
    if(!list)return;
    if(!conversations.length){list.innerHTML='<div class="empty-copy">No conversations yet.</div>';return}
    list.innerHTML=conversations.map(c=>'<button type="button" class="ai-conversation-item'+(c.conversation_id===currentConversationId?' active':'')+'" data-ai-conversation="'+escapeHtml(c.conversation_id)+'"><strong>'+escapeHtml(c.title)+'</strong><span>'+escapeHtml(c.agent_display_name)+' · '+Number(c.message_count||0)+' messages</span></button>').join('');
  }

  function renderMessages(data){
    const conversation=data.conversation;
    const messages=data.messages||[];
    currentConversationId=conversation.conversation_id;
    $('#aiChatTitle').textContent=conversation.title;
    $('#aiChatAgent').textContent=conversation.agent_display_name+' · '+conversation.agent_call_name;
    const thread=$('#aiChatThread');
    if(!messages.length){thread.innerHTML='<div class="ai-workspace-empty">Start the conversation with '+escapeHtml(conversation.agent_display_name)+'.</div>'}
    else thread.innerHTML=messages.map(m=>{
      const cls=m.role==='USER'?'user':'assistant';
      let meta='';
      if(m.role==='ASSISTANT'&&m.runtime_provenance){const p=m.runtime_provenance;meta='<div class="ai-message-meta">'+escapeHtml((p.provider_name||'Provider')+' · '+(p.model_name||p.model_id||'Model')+(p.fallback_used?' · fallback':'')+(p.latency_ms!=null?' · '+p.latency_ms+' ms':''))+'</div>'}
      return '<div class="ai-message '+cls+'">'+escapeHtml(m.content)+meta+'</div>';
    }).join('');
    thread.scrollTop=thread.scrollHeight;
    $('#aiChatForm').hidden=false;
    renderConversations();
  }

  async function refreshConversations(){
    const data=await api('/dashboard/api/ai-workspace/conversations');
    conversations=data.items||[];
    renderConversations();
  }

  async function loadConversation(id){
    const data=await api('/dashboard/api/ai-workspace/conversations/'+encodeURIComponent(id));
    renderMessages(data);
  }

  async function createConversation(){
    if(busy)return;
    const agentId=$('#aiAgentSelect').value;
    if(!agentId){window.alert('No available internal agent is selected.');return}
    busy=true;$('#aiNewConversation').disabled=true;
    try{
      const created=await api('/dashboard/api/ai-workspace/conversations',{method:'POST',body:JSON.stringify({agent_id:agentId})});
      await refreshConversations();
      await loadConversation(created.conversation_id);
      $('#aiMessageInput').focus();
    }catch(err){window.alert(err.message)}finally{busy=false;$('#aiNewConversation').disabled=false}
  }

  async function sendMessage(event){
    event.preventDefault();
    if(busy||!currentConversationId)return;
    const input=$('#aiMessageInput');
    const message=input.value.trim();
    if(!message)return;
    busy=true;$('#aiSend').disabled=true;input.disabled=true;
    const thread=$('#aiChatThread');
    const pending=document.createElement('div');pending.className='ai-message user';pending.textContent=message;thread.appendChild(pending);
    const thinking=document.createElement('div');thinking.className='ai-message assistant';thinking.textContent='Thinking…';thread.appendChild(thinking);thread.scrollTop=thread.scrollHeight;
    input.value='';
    try{
      await api('/dashboard/api/ai-workspace/conversations/'+encodeURIComponent(currentConversationId)+'/messages',{method:'POST',body:JSON.stringify({message})});
      await refreshConversations();
      await loadConversation(currentConversationId);
    }catch(err){thinking.textContent='Unable to respond: '+err.message;input.value=message}finally{busy=false;$('#aiSend').disabled=false;input.disabled=false;input.focus()}
  }

  function showTab(tab){
    $$('.ai-workspace-tab').forEach(x=>x.classList.toggle('active',x.dataset.aiTab===tab));
    $('#aiChatMode').hidden=tab!=='chat';
    $('#aiMultiMode').hidden=tab!=='multi';
  }

  async function loadWorkspace(){
    $('#aiWorkspaceBody').hidden=false;
    try{
      access=await api('/dashboard/api/ai-workspace/access');
      if(!access.allowed){renderBlocked('AI Chat is disabled by the Owner for this account.');return}
      $('#aiMultiTab').hidden=!access.multi_agent_allowed;
      const [agentData,conversationData]=await Promise.all([
        api('/dashboard/api/ai-workspace/chat/agents'),
        api('/dashboard/api/ai-workspace/conversations')
      ]);
      agents=agentData.items||[];conversations=conversationData.items||[];
      renderAgentOptions();renderConversations();
      if(currentConversationId&&conversations.some(c=>c.conversation_id===currentConversationId))await loadConversation(currentConversationId);
      else if(conversations.length)await loadConversation(conversations[0].conversation_id);
      else {currentConversationId=null;$('#aiChatTitle').textContent='New conversation';$('#aiChatAgent').textContent='Select an agent and start a chat.';$('#aiChatThread').innerHTML='<div class="ai-workspace-empty">Choose an agent, then create a conversation.</div>';$('#aiChatForm').hidden=true}
    }catch(err){
      if(err.status===403){renderBlocked(err.message);return}
      $('#aiWorkspaceBody').innerHTML='<div class="ai-access-blocked"><strong>Unable to load AI Workspace</strong><p>'+escapeHtml(err.message)+'</p></div>';
    }
  }

  nav.addEventListener('click',openWorkspace);
  panel.addEventListener('click',event=>{
    const item=event.target.closest('[data-ai-conversation]');if(item)loadConversation(item.dataset.aiConversation);
    const tab=event.target.closest('[data-ai-tab]');if(tab)showTab(tab.dataset.aiTab);
  });
  $('#aiNewConversation')?.addEventListener('click',createConversation);
  $('#aiChatForm')?.addEventListener('submit',sendMessage);
  $('#aiMessageInput')?.addEventListener('keydown',event=>{if(event.key==='Enter'&&!event.shiftKey){event.preventDefault();$('#aiChatForm').requestSubmit()}});
})();
