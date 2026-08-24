(()=>{
  const root=document.querySelector('#msa');
  if(!root||root.dataset.liveReviewExportReady)return;
  root.dataset.liveReviewExportReady='1';

  let liveWorkId=null;
  let livePollTimer=null;
  let liveLastSignature='';
  let liveRunning=false;
  let reconcileFrame=null;

  const esc=value=>String(value??'').replace(/[&<>'"]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;',"'":'&#39;','"':'&quot;'}[c]));
  const compact=value=>String(value??'').replace(/\s+/g,' ').trim();

  function cleanDisplayText(value){
    const input=String(value??'');
    const lines=input
      .replace(/^\s*#{1,6}\s+/gm,'')
      .replace(/\*\*([^*]+)\*\*/g,'$1')
      .replace(/__([^_]+)__/g,'$1')
      .replace(/`([^`\n]+)`/g,'$1')
      .split('\n');
    const output=[];
    for(let line of lines){
      const trimmed=line.trim();
      if(trimmed==='---')continue;
      if(/^\|?\s*:?-{3,}.*\|?\s*$/.test(trimmed))continue;
      if(trimmed.startsWith('|')&&trimmed.endsWith('|')){
        line=trimmed.slice(1,-1).split('|').map(cell=>cell.trim()).filter(Boolean).join(' · ');
      }
      output.push(line.replace(/^\s*\|\s?/,'').replace(/\s?\|\s*$/,'').replace(/\s+\|\s+/g,' · '));
    }
    return output.join('\n').replace(/\n{3,}/g,'\n\n').trim();
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
    if(!response.ok){let message='Request failed: '+response.status;if(data?.detail)message=typeof data.detail==='string'?data.detail:(data.detail.message||data.detail.code||message);const error=new Error(message);error.status=response.status;error.data=data;throw error}
    return data;
  }

  function statusNotice(text,kind='info'){
    const el=document.querySelector('#aiMultiMode #reviewUiStatus');if(!el)return;
    el.textContent=text||'';el.dataset.kind=kind;el.hidden=!text;
  }

  function reviewActionsHtml(workItemId){
    const id=encodeURIComponent(workItemId);
    return '<div class="review-export-actions" data-review-export-for="'+esc(workItemId)+'"><a href="/dashboard/api/ai-workspace/multi-agent/work-items/'+id+'/export?format=docx">DOCX</a><a href="/dashboard/api/ai-workspace/multi-agent/work-items/'+id+'/export?format=json">JSON</a><button class="review-delete-action" type="button" data-review-delete-for="'+esc(workItemId)+'">Delete</button></div>';
  }

  function renderLive(item){
    const detail=document.querySelector('#aiMultiMode #reviewWorkDetail');
    if(!detail)return;
    const artifacts=item.artifacts||[];
    const reviews=item.reviews||[];
    const owner=artifacts.find(a=>a.artifact_type==='OWNER_TASK');
    const turns=[];
    if(owner){
      const text=cleanDisplayText(owner.payload?.task||item.objective||'');
      turns.push('<article class="review-chat-turn review-chat-owner"><div class="review-chat-meta"><strong>Owner</strong><span>TASK</span></div><div class="review-chat-bubble" data-review-copy-text="'+esc(text)+'">'+esc(text)+'</div><button class="review-message-copy" type="button">Copy</button></article>');
    }
    artifacts.filter(a=>a.artifact_type==='PARTICIPANT_OUTPUT').forEach(a=>{
      const payload=a.payload||{};const prov=payload.provenance||{};const text=cleanDisplayText(payload.response||'');
      const related=reviews.find(r=>r.findings?.review_output_artifact_id===a.artifact_id);
      const verdict=related?'<span class="review-verdict">'+esc(related.verdict)+'</span>':'';
      const uniqueTools=Array.isArray(prov.native_unique_tools_executed)?prov.native_unique_tools_executed:(Array.isArray(prov.native_model_tools_executed)?prov.native_model_tools_executed:[]);
      const tools=[...new Set(uniqueTools.filter(Boolean))];
      const rawCount=Number(prov.native_tool_call_count);
      const toolCalls=Number.isFinite(rawCount)?rawCount:(Array.isArray(prov.native_tool_calls)?prov.native_tool_calls.length:0);
      const toolInfo=tools.length?'<span>Tools: '+esc(tools.join(', '))+' · '+toolCalls+' call'+(toolCalls===1?'':'s')+'</span>':(prov.native_store_tools_allowed?'<span>Tools: none · 0 calls</span>':'');
      turns.push('<article class="review-chat-turn review-chat-agent"><div class="review-chat-meta"><div><strong>'+esc(prov.agent_display_name||payload.display_label||'Internal agent')+'</strong><span>'+esc(payload.role||'PARTICIPANT')+'</span></div>'+verdict+'</div><div class="review-chat-bubble" data-review-copy-text="'+esc(text)+'">'+esc(text)+'</div><div class="review-chat-provenance"><span>'+esc((prov.selected_provider_name||'Provider')+' · '+(prov.selected_model_name||prov.selected_model_id||'Model'))+'</span>'+(prov.fallback_used?'<span>fallback</span>':'')+(prov.latency_ms!=null?'<span>'+esc(prov.latency_ms+' ms')+'</span>':'')+toolInfo+'</div><button class="review-message-copy" type="button">Copy</button></article>');
    });
    const running=item.status==='REVIEWING'?'<div class="review-live-wait"><span class="review-live-dot"></span>Waiting for the next configured participant…</div>':'';
    detail.innerHTML='<div class="review-chatbox-head"><div><div class="review-detail-title"><h3>'+esc(item.title)+'</h3><span class="review-status review-status-'+esc(String(item.status||'').toLowerCase())+'">'+esc(item.status)+'</span></div><span class="review-id">'+esc(item.work_item_id)+'</span></div>'+reviewActionsHtml(item.work_item_id)+'<div class="review-safety-line"><strong>Production mutation: NO</strong><span>Database canonical: NO</span></div></div><div class="review-chat-stream">'+turns.join('')+running+'</div>';
    const stream=detail.querySelector('.review-chat-stream');if(stream)stream.scrollTop=stream.scrollHeight;
  }

  function signature(item){
    return [item.status,(item.artifacts||[]).length,(item.reviews||[]).length,(item.events||[]).length].join(':');
  }

  function stopLivePolling(){
    if(livePollTimer){clearTimeout(livePollTimer);livePollTimer=null}
    liveRunning=false;
    liveWorkId=null;
    liveLastSignature='';
  }

  async function pollLive(){
    if(!liveWorkId)return;
    try{
      const item=await api('/dashboard/api/ai-workspace/multi-agent/work-items/'+encodeURIComponent(liveWorkId));
      const nextSignature=signature(item);
      if(nextSignature!==liveLastSignature){liveLastSignature=nextSignature;renderLive(item)}
      if(item.status==='WAITING_OWNER'||item.status==='FAILED'||item.status==='CANCELLED'){
        const terminalStatus=item.status;
        stopLivePolling();
        statusNotice(terminalStatus==='WAITING_OWNER'?'Review completed and is waiting for Owner attention.':terminalStatus==='CANCELLED'?'Review deleted from workspace history.':'Review failed. Open the Work Item timeline for details.',terminalStatus==='WAITING_OWNER'?'success':terminalStatus==='CANCELLED'?'success':'error');
        setTimeout(()=>document.querySelector('#aiMultiMode #reviewRefresh')?.click(),700);
        return;
      }
    }catch(err){statusNotice(err.message,'error');stopLivePolling();return}
    livePollTimer=setTimeout(pollLive,1000);
  }

  async function startLiveReview(){
    if(liveRunning)return;
    const host=document.querySelector('#aiMultiMode');if(!host)return;
    const sessionId=host.querySelector('#reviewSessionSelect')?.value||'';
    const title=compact(host.querySelector('#reviewTitle')?.value||'');
    const task=String(host.querySelector('#reviewTask')?.value||'').trim();
    if(!sessionId){statusNotice('Choose an open REVIEW preset first.','error');return}
    if(!title||!task){statusNotice('Enter both a Work title and Owner task.','error');return}
    const conversationId=host.querySelector('#reviewEvidenceConversation')?.value||null;
    const attachmentIds=[...host.querySelectorAll('#reviewEvidenceFiles input[type="checkbox"]:checked')].map(x=>x.value);
    liveRunning=true;statusNotice('Review started. Completed participant turns will appear here live.');
    const run=host.querySelector('#reviewRun');if(run){run.disabled=true;run.textContent='Review running…'}
    try{
      const item=await api('/dashboard/api/ai-workspace/multi-agent/reviews/live',{method:'POST',body:JSON.stringify({session_id:sessionId,title,task,evidence_conversation_id:conversationId,attachment_ids:attachmentIds})});
      liveWorkId=item.work_item_id;liveLastSignature='';renderLive(item);pollLive();
    }catch(err){liveRunning=false;statusNotice(err.message,'error');if(run){run.disabled=false;run.textContent='Run native review'}}
  }

  async function deleteReview(workItemId,button){
    if(!workItemId)return;
    const confirmed=window.confirm('Delete this Review from workspace history? Audit evidence will be preserved.');
    if(!confirmed)return;
    if(button){button.disabled=true;button.textContent='Deleting…'}
    try{
      await api('/dashboard/api/ai-workspace/multi-agent/work-items/'+encodeURIComponent(workItemId),{method:'DELETE'});
      if(liveWorkId===workItemId)stopLivePolling();
      const detail=document.querySelector('#aiMultiMode #reviewWorkDetail');
      if(detail)detail.innerHTML='<div class="review-empty"><strong>Review deleted</strong><p>Removed from Recent Review work. Audit evidence remains preserved.</p></div>';
      statusNotice('Review deleted from workspace history. Audit evidence was preserved.','success');
      setTimeout(()=>document.querySelector('#aiMultiMode #reviewRefresh')?.click(),250);
    }catch(err){statusNotice(err.message,'error');if(button){button.disabled=false;button.textContent='Delete'}}
  }

  function polishReviewDom(scope=document){
    scope.querySelectorAll?.('.review-chat-bubble:not([data-review-polished])').forEach(bubble=>{
      const clean=cleanDisplayText(bubble.textContent||'');bubble.textContent=clean;bubble.dataset.reviewCopyText=clean;bubble.dataset.reviewPolished='1';
      const turn=bubble.closest('.review-chat-turn');if(turn&&!turn.querySelector('.review-message-copy')){
        const button=document.createElement('button');button.type='button';button.className='review-message-copy';button.textContent='Copy';turn.appendChild(button);
      }
    });
    const detail=scope.querySelector?.('#reviewWorkDetail')||document.querySelector('#reviewWorkDetail');
    const id=detail?.querySelector('.review-id')?.textContent?.trim();
    const head=detail?.querySelector('.review-chatbox-head');
    if(id&&head&&!head.querySelector('.review-export-actions')){
      const wrapper=document.createElement('div');wrapper.innerHTML=reviewActionsHtml(id);const actions=wrapper.firstElementChild;if(actions)head.appendChild(actions);
    }else if(id&&head){
      const actions=head.querySelector('.review-export-actions');
      if(actions&&!actions.querySelector('.review-delete-action')){
        const button=document.createElement('button');button.type='button';button.className='review-delete-action';button.dataset.reviewDeleteFor=id;button.textContent='Delete';actions.appendChild(button);
      }
    }
  }

  function currentConversationId(){
    return document.querySelector('.ai-conversation-item.active [data-ai-conversation]')?.dataset.aiConversation||null;
  }

  function syncSingleChatExport(){
    const head=document.querySelector('.ai-chat-head');if(!head)return;
    let actions=head.querySelector('.ai-chat-export-actions');
    const id=currentConversationId();
    if(!id){actions?.remove();return}
    if(actions?.dataset.conversationId===id)return;
    if(!actions){actions=document.createElement('div');actions.className='ai-chat-export-actions';head.appendChild(actions)}
    actions.dataset.conversationId=id;
    actions.replaceChildren();
    const label=document.createElement('span');label.textContent='Export';
    const docx=document.createElement('a');docx.textContent='DOCX';docx.href='/dashboard/api/ai-workspace/conversations/'+encodeURIComponent(id)+'/export?format=docx';
    const json=document.createElement('a');json.textContent='JSON';json.href='/dashboard/api/ai-workspace/conversations/'+encodeURIComponent(id)+'/export?format=json';
    actions.append(label,docx,json);
  }

  function reconcileDom(){
    reconcileFrame=null;
    polishReviewDom(document);
    syncSingleChatExport();
  }

  function scheduleReconcile(){
    if(reconcileFrame!==null)return;
    reconcileFrame=requestAnimationFrame(reconcileDom);
  }

  document.addEventListener('click',event=>{
    const run=event.target.closest('#aiMultiMode #reviewRun');
    if(run){event.preventDefault();event.stopPropagation();startLiveReview();return}
    const copy=event.target.closest('.review-message-copy');
    if(copy){const text=copy.closest('.review-chat-turn')?.querySelector('.review-chat-bubble')?.dataset.reviewCopyText||'';copyText(text,copy);return}
    const deleteButton=event.target.closest('.review-delete-action');
    if(deleteButton){event.preventDefault();event.stopPropagation();deleteReview(deleteButton.dataset.reviewDeleteFor,deleteButton);return}
    if(event.target.closest('[data-ai-conversation],#aiNewConversation,#aiWorkspaceNav,[data-ai-tab]'))scheduleReconcile();
  },true);

  const observer=new MutationObserver(()=>scheduleReconcile());
  observer.observe(root,{childList:true,subtree:true});
  scheduleReconcile();
})();
