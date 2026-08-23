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
  let pendingAttachments=[];
  let busy=false;
  const MAX_ATTACHMENTS=4;
  const MAX_ATTACHMENT_BYTES=8*1024*1024;

  const escapeHtml=value=>String(value??'').replace(/[&<>'"]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;',"'":'&#39;','"':'&quot;'}[c]));
  const truncate=(value,max=82)=>{const text=String(value??'').replace(/\s+/g,' ').trim();return text.length>max?text.slice(0,max-1)+'…':text};
  const humanBytes=value=>{const n=Number(value||0);if(n<1024)return n+' B';if(n<1024*1024)return (n/1024).toFixed(n<10*1024?1:0)+' KB';return (n/(1024*1024)).toFixed(1)+' MB'};
  function cleanDisplayText(value){
    return String(value??'')
      .replace(/^\s*#{1,6}\s+/gm,'')
      .replace(/\*\*([^*]+)\*\*/g,'$1')
      .replace(/__([^_]+)__/g,'$1')
      .replace(/`([^`\n]+)`/g,'$1')
      .replace(/^\s*\|?\s*:?-{3,}.*\|?\s*$/gm,'')
      .replace(/^\s*\|\s?/gm,'')
      .replace(/\s?\|\s*$/gm,'')
      .replace(/\s+\|\s+/g,' · ')
      .replace(/\n{3,}/g,'\n\n')
      .trim();
  }
  function humanTime(value){
    const date=new Date(value);
    if(Number.isNaN(date.getTime()))return '';
    const diff=Math.max(0,Date.now()-date.getTime());
    if(diff<60_000)return 'Just now';
    if(diff<3_600_000){const n=Math.max(1,Math.round(diff/60_000));return n+' min ago'}
    if(diff<86_400_000){const n=Math.max(1,Math.round(diff/3_600_000));return n+' hr'+(n===1?'':'s')+' ago'}
    if(diff<604_800_000){const n=Math.max(1,Math.round(diff/86_400_000));return n+' day'+(n===1?'':'s')+' ago'}
    return date.toLocaleString([],{month:'short',day:'numeric',year:date.getFullYear()===new Date().getFullYear()?undefined:'numeric',hour:'numeric',minute:'2-digit'});
  }
  async function copyText(text,button){
    const value=String(text??'');
    try{
      if(navigator.clipboard&&window.isSecureContext)await navigator.clipboard.writeText(value);
      else{
        const area=document.createElement('textarea');area.value=value;area.style.position='fixed';area.style.opacity='0';document.body.appendChild(area);area.select();document.execCommand('copy');area.remove();
      }
      if(button){const old=button.textContent;button.textContent='Copied';setTimeout(()=>button.textContent=old,1200)}
    }catch{window.alert('Could not copy this message.')}
  }
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
  async function uploadApi(path,file){
    const form=new FormData();form.append('file',file,file.name);
    const response=await fetch(path,{method:'POST',credentials:'same-origin',body:form});
    let data=null;try{data=await response.json()}catch{}
    if(!response.ok){
      let message='Upload failed: '+response.status;
      if(data&&data.detail)message=typeof data.detail==='string'?data.detail:(data.detail.message||message);
      const err=new Error(message);err.status=response.status;throw err;
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
    list.innerHTML=conversations.map(c=>{
      const active=c.conversation_id===currentConversationId?' active':'';
      const preview=truncate(c.first_user_preview||'No messages yet',78);
      const time=humanTime(c.updated_at);
      return '<div class="ai-conversation-item'+active+'" data-ai-conversation-row="'+escapeHtml(c.conversation_id)+'">'
        +'<button type="button" class="ai-conversation-open" data-ai-conversation="'+escapeHtml(c.conversation_id)+'">'
        +'<strong>'+escapeHtml(c.title)+'</strong>'
        +'<span class="ai-conversation-preview">'+escapeHtml(preview)+'</span>'
        +'<span class="ai-conversation-meta">'+escapeHtml(c.agent_display_name)+' · '+Number(c.message_count||0)+' messages · '+escapeHtml(time)+'</span>'
        +'</button>'
        +'<button type="button" class="ai-conversation-delete" data-ai-delete="'+escapeHtml(c.conversation_id)+'" aria-label="Delete conversation" title="Delete conversation">×</button>'
        +'</div>';
    }).join('');
  }

  function attachmentChips(items,bound=false){
    if(!items?.length)return '';
    return '<div class="ai-message-attachments">'+items.map(item=>{
      const icon=item.kind==='IMAGE'?'Photo':'File';
      return '<span class="ai-message-attachment"><span>'+icon+'</span><strong>'+escapeHtml(item.filename||'attachment')+'</strong><small>'+escapeHtml(humanBytes(item.byte_size))+(bound?' · saved':'')+'</small></span>';
    }).join('')+'</div>';
  }

  function messageMarkup(message){
    const cls=message.role==='USER'?'user':'assistant';
    const visible=cleanDisplayText(message.content);
    let meta='';
    if(message.role==='ASSISTANT'&&message.runtime_provenance){
      const p=message.runtime_provenance;
      meta='<div class="ai-message-meta">'+escapeHtml((p.provider_name||'Provider')+' · '+(p.model_name||p.model_id||'Model')+(p.fallback_used?' · fallback':'')+(p.latency_ms!=null?' · '+p.latency_ms+' ms':''))+'</div>';
    }
    const content=visible?escapeHtml(visible):'<span class="ai-attachment-only-label">Attachment evidence</span>';
    return '<div class="ai-message-wrap '+cls+'">'
      +'<div class="ai-message '+cls+'" data-copy-text="'+escapeHtml(visible)+'">'+content+attachmentChips(message.attachments||[],true)+meta+'</div>'
      +(visible?'<button type="button" class="ai-message-copy" data-copy-message="'+escapeHtml(message.message_id||'')+'">Copy</button>':'')
      +'</div>';
  }

  function renderPendingAttachments(){
    const box=$('#aiPendingAttachments');
    if(!box)return;
    box.hidden=!pendingAttachments.length;
    box.innerHTML=pendingAttachments.map(item=>'<div class="ai-pending-attachment">'
      +'<span class="ai-pending-kind">'+(item.kind==='IMAGE'?'Photo':'File')+'</span>'
      +'<span class="ai-pending-name">'+escapeHtml(item.filename)+'</span>'
      +'<span class="ai-pending-size">'+escapeHtml(humanBytes(item.byte_size))+'</span>'
      +'<button type="button" data-ai-remove-attachment="'+escapeHtml(item.attachment_id)+'" aria-label="Remove attachment">×</button>'
      +'</div>').join('');
  }

  async function refreshPendingAttachments(id=currentConversationId){
    if(!id){pendingAttachments=[];renderPendingAttachments();return}
    const data=await api('/dashboard/api/ai-workspace/conversations/'+encodeURIComponent(id)+'/attachments');
    pendingAttachments=(data.items||[]).filter(item=>item.state==='PENDING'&&!item.message_id);
    renderPendingAttachments();
  }

  function renderMessages(data){
    const conversation=data.conversation;
    const messages=data.messages||[];
    currentConversationId=conversation.conversation_id;
    $('#aiChatTitle').textContent=conversation.title;
    $('#aiChatAgent').textContent=conversation.agent_display_name+' · '+conversation.agent_call_name;
    const thread=$('#aiChatThread');
    if(!messages.length){thread.innerHTML='<div class="ai-workspace-empty">Start the conversation with '+escapeHtml(conversation.agent_display_name)+'.</div>'}
    else thread.innerHTML=messages.map(messageMarkup).join('');
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
    await refreshPendingAttachments(id);
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

  async function deleteConversation(id){
    if(busy)return;
    const item=conversations.find(c=>c.conversation_id===id);
    if(!window.confirm('Delete '+(item?.title||'this conversation')+'? This removes its saved messages and attachments.'))return;
    busy=true;
    try{
      await api('/dashboard/api/ai-workspace/conversations/'+encodeURIComponent(id),{method:'DELETE'});
      if(currentConversationId===id){currentConversationId=null;pendingAttachments=[];renderPendingAttachments()}
      await refreshConversations();
      if(conversations.length)await loadConversation(conversations[0].conversation_id);
      else{
        $('#aiChatTitle').textContent='New conversation';
        $('#aiChatAgent').textContent='Select an agent and start a chat.';
        $('#aiChatThread').innerHTML='<div class="ai-workspace-empty">Choose an agent, then create a conversation.</div>';
        $('#aiChatForm').hidden=true;
      }
    }catch(err){window.alert(err.message)}finally{busy=false}
  }

  function setComposeBusy(value){
    $('#aiSend').disabled=value;
    $('#aiMessageInput').disabled=value;
    $('#aiPhotoButton').disabled=value;
    $('#aiFileButton').disabled=value;
  }

  async function addFiles(fileList){
    if(busy||!currentConversationId)return;
    const files=[...fileList];
    const room=Math.max(0,MAX_ATTACHMENTS-pendingAttachments.length);
    if(!room){window.alert('This message already has 4 pending attachments.');return}
    const selected=files.slice(0,room);
    if(files.length>room)window.alert('Only the first '+room+' attachment'+(room===1?'':'s')+' will be added.');
    for(const file of selected){
      if(file.size>MAX_ATTACHMENT_BYTES){window.alert(file.name+' exceeds the 8 MB attachment limit.');continue}
      busy=true;setComposeBusy(true);
      try{
        const uploaded=await uploadApi('/dashboard/api/ai-workspace/conversations/'+encodeURIComponent(currentConversationId)+'/attachments',file);
        pendingAttachments.push(uploaded);renderPendingAttachments();
      }catch(err){window.alert(err.message)}finally{busy=false;setComposeBusy(false)}
    }
  }

  async function removeAttachment(id){
    if(busy||!currentConversationId)return;
    busy=true;setComposeBusy(true);
    try{
      await api('/dashboard/api/ai-workspace/conversations/'+encodeURIComponent(currentConversationId)+'/attachments/'+encodeURIComponent(id),{method:'DELETE'});
      pendingAttachments=pendingAttachments.filter(item=>item.attachment_id!==id);renderPendingAttachments();
    }catch(err){window.alert(err.message)}finally{busy=false;setComposeBusy(false)}
  }

  async function sendMessage(event){
    event.preventDefault();
    if(busy||!currentConversationId)return;
    const input=$('#aiMessageInput');
    const message=input.value.trim();
    if(!message&&!pendingAttachments.length)return;
    busy=true;setComposeBusy(true);
    const thread=$('#aiChatThread');
    const pending=document.createElement('div');pending.className='ai-message-wrap user';pending.innerHTML='<div class="ai-message user"></div>';
    pending.querySelector('.ai-message').textContent=message||'Attachment evidence';
    thread.appendChild(pending);
    const thinking=document.createElement('div');thinking.className='ai-message-wrap assistant';thinking.innerHTML='<div class="ai-message assistant">Thinking…</div>';thread.appendChild(thinking);thread.scrollTop=thread.scrollHeight;
    const attachmentIds=pendingAttachments.map(item=>item.attachment_id);
    input.value='';
    try{
      await api('/dashboard/api/ai-workspace/conversations/'+encodeURIComponent(currentConversationId)+'/messages',{method:'POST',body:JSON.stringify({message,attachment_ids:attachmentIds})});
      pendingAttachments=[];renderPendingAttachments();
      await refreshConversations();
      await loadConversation(currentConversationId);
    }catch(err){thinking.querySelector('.ai-message').textContent='Unable to respond: '+err.message;input.value=message}finally{busy=false;setComposeBusy(false);input.focus()}
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
      else {currentConversationId=null;pendingAttachments=[];renderPendingAttachments();$('#aiChatTitle').textContent='New conversation';$('#aiChatAgent').textContent='Select an agent and start a chat.';$('#aiChatThread').innerHTML='<div class="ai-workspace-empty">Choose an agent, then create a conversation.</div>';$('#aiChatForm').hidden=true}
    }catch(err){
      if(err.status===403){renderBlocked(err.message);return}
      $('#aiWorkspaceBody').innerHTML='<div class="ai-access-blocked"><strong>Unable to load AI Workspace</strong><p>'+escapeHtml(err.message)+'</p></div>';
    }
  }

  nav.addEventListener('click',openWorkspace);
  panel.addEventListener('click',event=>{
    const copy=event.target.closest('[data-copy-message]');
    if(copy){const wrap=copy.closest('.ai-message-wrap');const bubble=wrap?.querySelector('.ai-message');copyText(bubble?.dataset.copyText||bubble?.textContent||'',copy);return}
    const remove=event.target.closest('[data-ai-remove-attachment]');if(remove){removeAttachment(remove.dataset.aiRemoveAttachment);return}
    const del=event.target.closest('[data-ai-delete]');if(del){deleteConversation(del.dataset.aiDelete);return}
    const item=event.target.closest('[data-ai-conversation]');if(item){loadConversation(item.dataset.aiConversation);return}
    const tab=event.target.closest('[data-ai-tab]');if(tab)showTab(tab.dataset.aiTab);
  });
  $('#aiNewConversation')?.addEventListener('click',createConversation);
  $('#aiChatForm')?.addEventListener('submit',sendMessage);
  $('#aiPhotoButton')?.addEventListener('click',()=>$('#aiPhotoInput').click());
  $('#aiFileButton')?.addEventListener('click',()=>$('#aiFileInput').click());
  $('#aiPhotoInput')?.addEventListener('change',async event=>{await addFiles(event.target.files);event.target.value=''});
  $('#aiFileInput')?.addEventListener('change',async event=>{await addFiles(event.target.files);event.target.value=''});
  $('#aiMessageInput')?.addEventListener('keydown',event=>{if(event.key==='Enter'&&!event.shiftKey){event.preventDefault();$('#aiChatForm').requestSubmit()}});
})();
