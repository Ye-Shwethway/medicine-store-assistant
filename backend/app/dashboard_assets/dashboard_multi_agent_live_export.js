(()=>{
  const root=document.querySelector('#msa');
  if(!root||root.dataset.liveReviewExportReady)return;
  root.dataset.liveReviewExportReady='1';

  let liveWorkId=null;
  let livePollTimer=null;
  let liveLastSignature='';
  let liveRunning=false;

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
      turns.push('<article class="review-chat-turn review-chat-agent"><div class="review-chat-meta"><div><strong>'+esc(prov.agent_display_name||payload.display_label||'Internal agent')+'</strong><span>'+esc(payload.role||'PARTICIPANT')+'</span></div>'+verdict+'</div><div class="review-chat-bubble" data-review-copy-text="'+esc(text)+'">'+esc(text)+'</div><div class="review-chat-provenance"><span>'+esc((prov.selected_provider_name||'Provider')+' · '+(prov.selected_model_name||prov.selected_model_id||'Model'))+'</span>'+(prov.fallback_used?'<span>fallback</span>':'')+(prov.latency_ms!=null?'<span>'+esc(prov.latency_ms+' ms')+'</span>':'')+'</div><button class="review-message-copy" type="button">Copy</button></article>');
    });
    const running=item.status==='REVIEWING'?'<div class="review-live-wait"><span class="review-live-dot"></span>Waiting for the next configured participant…</div>':'';
    detail.innerHTML='<div class="review-chatbox-head"><div><div class="review-detail-title"><h3>'+esc(item.title)+'</h3><span class="review-status review-status-'+esc(String(item.status||'').toLowerCase())+'">'+esc(item.status)+'</span></div><span class="review-id">'+esc(item.work_item_id)+'</span></div><div class="review-export-actions" data-review-export-for="'+esc(item.work_item_id)+'"><a href="/dashboard/api/ai-workspace/multi-agent/work-items/'+encodeURIComponent(item.work_item_id)+'/export?format=docx">DOCX</a><a href="/dashboard/api/ai-workspace/multi-agent/work-items/'+encodeURIComponent(item.work_item_id)+'/export?format=json">JSON</a></div><div class="review-safety-line"><strong>Production mutation: NO</strong><span>Database canonical: NO</span></div></div><div class="review-chat-stream">'+turns.join('')+running+'</div>';
    const stream=detail.querySelector('.review-chat-stream');if(stream)stream.scrollTop=stream.scrollHeight;
  }

  function signature(item){
    return [item.status,(item.artifacts||[]).length,(item.reviews||[]).length,(item.events||[]).length].join(':');
  }

  async function pollLive(){
    if(!liveWorkId)return;
    try{
      const item=await api('/dashboard/api/ai-workspace/multi-agent/work-items/'+encodeURIComponent(liveWorkId));
      const nextSignature=signature(item);
      if(nextSignature!==liveLastSignature){liveLastSignature=nextSignature;renderLive(item)}
      if(item.status==='WAITING_OWNER'||item.status==='FAILED'){
        liveRunning=false;
        livePollTimer=null;
        statusNotice(item.status==='WAITING_OWNER'?'Review completed and is waiting for Owner attention.':'Review failed. Open the Work Item timeline for details.',item.status==='WAITING_OWNER'?'success':'error');
        setTimeout(()=>document.querySelector('#aiMultiMode #reviewRefresh')?.click(),700);
        return;
      }
    }catch(err){statusNotice(err.message,'error');liveRunning=false;livePollTimer=null;return}
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
      const actions=document.createElement('div');actions.className='review-export-actions';actions.innerHTML='<a href="/dashboard/api/ai-workspace/multi-agent/work-items/'+encodeURIComponent(id)+'/export?format=docx">DOCX</a><a href="/dashboard/api/ai-workspace/multi-agent/work-items/'+encodeURIComponent(id)+'/export?format=json">JSON</a>';head.appendChild(actions);
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
    if(!actions){actions=document.createElement('div');actions.className='ai-chat-export-actions';head.appendChild(actions)}
    actions.innerHTML='<span>Export</span><a href="/dashboard/api/ai-workspace/conversations/'+encodeURIComponent(id)+'/export?format=docx">DOCX</a><a href="/dashboard/api/ai-workspace/conversations/'+encodeURIComponent(id)+'/export?format=json">JSON</a>';
  }

  document.addEventListener('click',event=>{
    const run=event.target.closest('#aiMultiMode #reviewRun');
    if(run){event.preventDefault();event.stopPropagation();startLiveReview();return}
    const copy=event.target.closest('.review-message-copy');
    if(copy){const text=copy.closest('.review-chat-turn')?.querySelector('.review-chat-bubble')?.dataset.reviewCopyText||'';copyText(text,copy)}
  },true);

  const observer=new MutationObserver(mutations=>{
    for(const mutation of mutations){for(const node of mutation.addedNodes){if(node.nodeType===1)polishReviewDom(node)}}
    polishReviewDom(document);syncSingleChatExport();
  });
  observer.observe(root,{childList:true,subtree:true});
  polishReviewDom(document);syncSingleChatExport();
})();
