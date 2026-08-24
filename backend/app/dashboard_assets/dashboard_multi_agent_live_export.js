(()=>{
  const root=document.querySelector('#msa');
  if(!root||root.dataset.liveReviewExportReady)return;
  root.dataset.liveReviewExportReady='1';

  let liveWorkId=null;
  let livePollTimer=null;
  let liveLastSignature='';
  let liveRunning=false;
  let reconcileFrame=null;
  let hydrateWorkId=null;
  let hydrateInFlight=false;

  const esc=value=>String(value??'').replace(/[&<>'"]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;',"'":'&#39;','"':'&quot;'}[c]));
  const compact=value=>String(value??'').replace(/\s+/g,' ').trim();

  function cleanDisplayText(value){
    const input=String(value??'');
    const lines=input.replace(/^\s*#{1,6}\s+/gm,'').replace(/\*\*([^*]+)\*\*/g,'$1').replace(/__([^_]+)__/g,'$1').replace(/`([^`\n]+)`/g,'$1').split('\n');
    const output=[];
    for(let line of lines){
      const trimmed=line.trim();
      if(trimmed==='---')continue;
      if(/^\|?\s*:?-{3,}.*\|?\s*$/.test(trimmed))continue;
      if(trimmed.startsWith('|')&&trimmed.endsWith('|'))line=trimmed.slice(1,-1).split('|').map(cell=>cell.trim()).filter(Boolean).join(' · ');
      output.push(line.replace(/^\s*\|\s?/,'').replace(/\s?\|\s*$/,'').replace(/\s+\|\s+/g,' · '));
    }
    return output.join('\n').replace(/\n{3,}/g,'\n\n').trim();
  }

  async function copyText(text,button){
    const value=String(text??'');
    try{
      if(navigator.clipboard&&window.isSecureContext)await navigator.clipboard.writeText(value);
      else{const area=document.createElement('textarea');area.value=value;area.style.position='fixed';area.style.opacity='0';document.body.appendChild(area);area.select();document.execCommand('copy');area.remove()}
      if(button){const old=button.textContent;button.textContent='Copied';setTimeout(()=>button.textContent=old,1200)}
    }catch{window.alert('Could not copy this message.')}
  }

  async function api(path,opts={}){
    const response=await fetch(path,{credentials:'same-origin',headers:{'Content-Type':'application/json',...(opts.headers||{})},...opts});
    let data=null;try{data=await response.json()}catch{}
    if(!response.ok){let message='Request failed: '+response.status;if(data?.detail)message=typeof data.detail==='string'?data.detail:(data.detail.message||data.detail.code||message);const error=new Error(message);error.status=response.status;error.data=data;throw error}
    return data;
  }

  function statusNotice(text,kind='info'){const el=document.querySelector('#aiMultiMode #reviewUiStatus');if(!el)return;el.textContent=text||'';el.dataset.kind=kind;el.hidden=!text}
  function reviewExportHtml(workItemId,position='top'){const id=encodeURIComponent(workItemId);return '<div class="review-export-actions review-export-'+esc(position)+'" data-review-export-for="'+esc(workItemId)+'"><a href="/dashboard/api/ai-workspace/multi-agent/work-items/'+id+'/export?format=docx">DOCX</a><a href="/dashboard/api/ai-workspace/multi-agent/work-items/'+id+'/export?format=json">JSON</a></div>'}
  function consumedIds(item,key){const ids=new Set();(item.events||[]).forEach(event=>{if(event.event_type!=='OWNER_STARTED_FEEDBACK_PASS')return;((event.payload||{})[key]||[]).forEach(id=>{if(id)ids.add(String(id))})});return ids}
  function pendingReviewInputs(item){
    const artifacts=item.artifacts||[];
    const consumedOwner=consumedIds(item,'owner_message_artifact_ids');
    const consumedExternal=consumedIds(item,'external_review_artifact_ids');
    const ownerMessages=artifacts.filter(a=>a.artifact_type==='OWNER_MESSAGE'&&!consumedOwner.has(String(a.artifact_id)));
    const externalReviews=artifacts.filter(a=>a.artifact_type==='EXTERNAL_REVIEW_SUBMISSION'&&!consumedExternal.has(String(a.artifact_id)));
    return {ownerMessages,externalReviews,actionable:ownerMessages.length>0||externalReviews.length>0};
  }
  function latestReviewableArtifact(item){return (item.artifacts||[]).filter(a=>a.artifact_type==='PARTICIPANT_OUTPUT').slice().sort((a,b)=>Number(b.version||0)-Number(a.version||0))[0]||null}
  function hasExternalForLatest(item){const latest=latestReviewableArtifact(item);if(!latest)return false;return (item.artifacts||[]).some(a=>a.artifact_type==='EXTERNAL_REVIEW_SUBMISSION'&&String(a.payload?.bound_artifact_id||'')===String(latest.artifact_id)&&Number(a.payload?.bound_artifact_version||0)===Number(latest.version||0))}

  function enterReviewChatView(){
    const host=document.querySelector('#aiMultiMode');
    if(!host)return;
    host.classList.add('review-chat-open');
    ensureReviewBackButton();
    requestAnimationFrame(()=>document.querySelector('#aiMultiMode .review-chatbox-shell')?.scrollIntoView({block:'start'}));
  }

  function exitReviewChatView(){
    const host=document.querySelector('#aiMultiMode');
    if(!host)return;
    host.classList.remove('review-chat-open');
    const history=host.querySelector('.review-history');
    if(history)requestAnimationFrame(()=>history.scrollIntoView({block:'start'}));
  }

  function ensureReviewBackButton(){
    const head=document.querySelector('#aiMultiMode #reviewWorkDetail .review-chatbox-head');
    if(!head||head.querySelector('[data-review-back]'))return;
    const button=document.createElement('button');
    button.type='button';
    button.className='review-chat-back';
    button.dataset.reviewBack='1';
    button.textContent='← Back to reviews';
    head.prepend(button);
  }

  function federationActionHtml(workItemId,status,alreadyReviewed=false){
    if(status==='WAITING_EXTERNAL')return '<div class="review-federation-action review-federation-wait"><span class="review-live-dot"></span><div><strong>Waiting for external review</strong><small>Bound artifact snapshot is available to authorized external MCP agents.</small></div></div>';
    if(status!=='WAITING_OWNER')return '';
    if(alreadyReviewed)return '<div class="review-federation-action review-federation-settled"><div><strong>External review received</strong><small>The latest Review artifact already has an external review. A new native pass creates a new reviewable artifact.</small></div><button type="button" disabled>Review received</button></div>';
    return '<div class="review-federation-action"><div><strong>Optional external review</strong><small>Freeze the latest Review artifact/version for an authorized external MCP reviewer.</small></div><button type="button" data-request-external-review="'+esc(workItemId)+'">Request external review</button></div>';
  }

  function renderLive(item){
    const detail=document.querySelector('#aiMultiMode #reviewWorkDetail');if(!detail)return;
    const artifacts=item.artifacts||[];const reviews=item.reviews||[];const turns=[];
    const artifactTurn=a=>{
      if(a.artifact_type==='OWNER_TASK'){
        const text=cleanDisplayText(a.payload?.task||item.objective||'');
        return '<article class="review-chat-turn review-chat-owner"><div class="review-chat-meta"><strong>Owner</strong><span>TASK</span></div><div class="review-chat-bubble" data-review-copy-text="'+esc(text)+'">'+esc(text)+'</div><button class="review-message-copy" type="button">Copy</button></article>';
      }
      if(a.artifact_type==='PARTICIPANT_OUTPUT'){
        const payload=a.payload||{};const prov=payload.provenance||{};const text=cleanDisplayText(payload.response||'');const related=reviews.find(r=>r.findings?.review_output_artifact_id===a.artifact_id);const verdict=related?'<span class="review-verdict">'+esc(related.verdict)+'</span>':'';
        const uniqueTools=Array.isArray(prov.native_unique_tools_executed)?prov.native_unique_tools_executed:(Array.isArray(prov.native_model_tools_executed)?prov.native_model_tools_executed:[]);const tools=[...new Set(uniqueTools.filter(Boolean))];const rawCount=Number(prov.native_tool_call_count);const toolCalls=Number.isFinite(rawCount)?rawCount:(Array.isArray(prov.native_tool_calls)?prov.native_tool_calls.length:0);const toolInfo=tools.length?'<span>Tools: '+esc(tools.join(', '))+' · '+toolCalls+' call'+(toolCalls===1?'':'s')+'</span>':(prov.native_store_tools_allowed?'<span>Tools: none · 0 calls</span>':'');
        return '<article class="review-chat-turn review-chat-agent"><div class="review-chat-meta"><div><strong>'+esc(prov.agent_display_name||payload.display_label||'Internal agent')+'</strong><span>'+esc(payload.role||'PARTICIPANT')+'</span></div>'+verdict+'</div><div class="review-chat-bubble" data-review-copy-text="'+esc(text)+'">'+esc(text)+'</div><div class="review-chat-provenance"><span>'+esc((prov.selected_provider_name||'Provider')+' · '+(prov.selected_model_name||prov.selected_model_id||'Model'))+'</span>'+(prov.fallback_used?'<span>fallback</span>':'')+(prov.latency_ms!=null?'<span>'+esc(prov.latency_ms+' ms')+'</span>':'')+toolInfo+'</div><button class="review-message-copy" type="button">Copy</button></article>';
      }
      if(a.artifact_type==='EXTERNAL_REVIEW_SUBMISSION'){
        const payload=a.payload||{};const text=cleanDisplayText(payload.notes||'');const verdict=payload.verdict?'<span class="review-verdict">'+esc(payload.verdict)+'</span>':'';
        return '<article class="review-chat-turn review-chat-agent review-chat-external"><div class="review-chat-meta"><div><strong>'+esc(payload.external_agent_display_name||payload.external_agent_call_name||'External MCP reviewer')+'</strong><span>EXTERNAL REVIEW</span></div>'+verdict+'</div><div class="review-chat-bubble" data-review-copy-text="'+esc(text)+'">'+esc(text)+'</div><div class="review-chat-provenance"><span>External MCP evidence · exact artifact v'+Number(payload.bound_artifact_version||0)+'</span></div><button class="review-message-copy" type="button">Copy</button></article>';
      }
      if(a.artifact_type==='OWNER_MESSAGE'){
        const text=cleanDisplayText(a.payload?.message||'');
        return '<article class="review-chat-turn review-chat-owner"><div class="review-chat-meta"><strong>Owner</strong><span>MESSAGE</span></div><div class="review-chat-bubble" data-review-copy-text="'+esc(text)+'">'+esc(text)+'</div><button class="review-message-copy" type="button">Copy</button></article>';
      }
      if(a.artifact_type==='OWNER_REVISION'){
        const text=cleanDisplayText(a.payload?.instruction||'');
        return '<article class="review-chat-turn review-chat-owner"><div class="review-chat-meta"><strong>Owner</strong><span>FEEDBACK</span></div><div class="review-chat-bubble" data-review-copy-text="'+esc(text)+'">'+esc(text)+'</div><button class="review-message-copy" type="button">Copy</button></article>';
      }
      return '';
    };
    artifacts.forEach(a=>{const turn=artifactTurn(a);if(turn)turns.push(turn)});
    const running=item.status==='REVIEWING'?'<div class="review-live-wait"><span class="review-live-dot"></span>Waiting for the next configured participant…</div>':'';
    const reviewInputs=pendingReviewInputs(item);
    const ownerAction=item.status==='WAITING_OWNER'?'<div class="review-owner-action review-chat-composer">'+reviewExportHtml(item.work_item_id,'composer')+'<label for="reviewRevisionInstruction">Owner message</label><div class="review-message-compose-row"><textarea id="reviewRevisionInstruction" maxlength="5000" placeholder="Write a message, then tap Send. Messages wait here until you send the next review pass."></textarea><button type="button" class="review-message-send" data-owner-message-send="'+esc(item.work_item_id)+'" aria-label="Send Owner message" title="Send message">➤</button></div><button type="button" id="reviewReturnRevision" data-review-send-pass="'+esc(item.work_item_id)+'"'+(reviewInputs.actionable?'':' disabled')+'>'+(reviewInputs.actionable?'Send review':'Review sent')+'</button><small class="review-send-state">'+(reviewInputs.actionable?'New Owner/external feedback is ready for the native review team.':'No unsent review feedback.')+'</small></div>':'';
    detail.innerHTML='<div class="review-chatbox-head"><div><div class="review-detail-title"><h3>'+esc(item.title)+'</h3><span class="review-status review-status-'+esc(String(item.status||'').toLowerCase())+'">'+esc(item.status)+'</span></div><span class="review-id">'+esc(item.work_item_id)+'</span></div>'+reviewExportHtml(item.work_item_id)+'<div class="review-safety-line"><strong>Production mutation: NO</strong><span>Database canonical: NO</span></div>'+federationActionHtml(item.work_item_id,item.status,hasExternalForLatest(item))+'</div><div class="review-chat-stream">'+turns.join('')+running+'</div>'+ownerAction;
    ensureReviewBackButton();
    const stream=detail.querySelector('.review-chat-stream');if(stream)stream.scrollTop=stream.scrollHeight;scheduleReconcile();
  }

  window.MSAReviewChatRenderer={render:renderLive,enter:enterReviewChatView,exit:exitReviewChatView};

  function signature(item){return[item.status,(item.artifacts||[]).length,(item.reviews||[]).length,(item.events||[]).length].join(':')}
  function stopLivePolling(){if(livePollTimer){clearTimeout(livePollTimer);livePollTimer=null}liveRunning=false;liveWorkId=null;liveLastSignature=''}
  async function pollLive(){
    if(!liveWorkId)return;
    try{
      const item=await api('/dashboard/api/ai-workspace/multi-agent/work-items/'+encodeURIComponent(liveWorkId));const nextSignature=signature(item);if(nextSignature!==liveLastSignature){liveLastSignature=nextSignature;renderLive(item)}
      if(item.status==='WAITING_OWNER'||item.status==='FAILED'||item.status==='CANCELLED'){
        const terminalStatus=item.status;stopLivePolling();statusNotice(terminalStatus==='WAITING_OWNER'?'Review is waiting for Owner attention.':terminalStatus==='CANCELLED'?'Review deleted from workspace history.':'Review failed. Open the Work Item timeline for details.',terminalStatus==='WAITING_OWNER'?'success':terminalStatus==='CANCELLED'?'success':'error');setTimeout(()=>document.querySelector('#aiMultiMode #reviewRefresh')?.click(),700);return;
      }
    }catch(err){statusNotice(err.message,'error');stopLivePolling();return}
    livePollTimer=setTimeout(pollLive,1000);
  }

  async function hydrateOpenedReview(){
    const detail=document.querySelector('#aiMultiMode #reviewWorkDetail');const id=detail?.querySelector('.review-id')?.textContent?.trim();if(!id||hydrateInFlight)return;
    const status=detail.querySelector('.review-status')?.textContent?.trim()||'';const needsResume=status==='WAITING_EXTERNAL'||status==='REVIEWING';const needsHydrate=hydrateWorkId!==id;
    if(!needsResume&&!needsHydrate)return;
    hydrateInFlight=true;
    try{
      const item=await api('/dashboard/api/ai-workspace/multi-agent/work-items/'+encodeURIComponent(id));hydrateWorkId=id;renderLive(item);
      if(item.status==='WAITING_EXTERNAL'||item.status==='REVIEWING'){
        liveWorkId=id;liveLastSignature=signature(item);if(livePollTimer)clearTimeout(livePollTimer);livePollTimer=setTimeout(pollLive,1000);
      }
    }catch(err){statusNotice(err.message,'error')}finally{hydrateInFlight=false}
  }

  async function startLiveReview(){
    if(liveRunning)return;const host=document.querySelector('#aiMultiMode');if(!host)return;const sessionId=host.querySelector('#reviewSessionSelect')?.value||'';const title=compact(host.querySelector('#reviewTitle')?.value||'');const task=String(host.querySelector('#reviewTask')?.value||'').trim();if(!sessionId){statusNotice('Choose an open REVIEW preset first.','error');return}if(!title||!task){statusNotice('Enter both a Work title and Owner task.','error');return}
    const conversationId=host.querySelector('#reviewEvidenceConversation')?.value||null;const attachmentIds=[...host.querySelectorAll('#reviewEvidenceFiles input[type="checkbox"]:checked')].map(x=>x.value);liveRunning=true;statusNotice('Review started. Completed participant turns will appear here live.');const run=host.querySelector('#reviewRun');if(run){run.disabled=true;run.textContent='Review running…'}
    try{const item=await api('/dashboard/api/ai-workspace/multi-agent/reviews/live',{method:'POST',body:JSON.stringify({session_id:sessionId,title,task,evidence_conversation_id:conversationId,attachment_ids:attachmentIds})});liveWorkId=item.work_item_id;liveLastSignature='';hydrateWorkId=item.work_item_id;renderLive(item);enterReviewChatView();pollLive()}catch(err){liveRunning=false;statusNotice(err.message,'error');if(run){run.disabled=false;run.textContent='Run native review'}}
  }

  async function requestExternalReview(workItemId,button){
    if(!workItemId)return;const confirmed=window.confirm('Request an external MCP review of the latest Review artifact? The exact artifact ID and version will be frozen.');if(!confirmed)return;
    if(button){button.disabled=true;button.textContent='Requesting…'}
    try{const item=await api('/dashboard/api/ai-workspace/multi-agent/work-items/'+encodeURIComponent(workItemId)+'/request-external-review',{method:'POST',body:JSON.stringify({})});hydrateWorkId=workItemId;renderLive(item);statusNotice('External review requested. Waiting for an authorized external MCP agent.','success');liveWorkId=workItemId;liveLastSignature=signature(item);if(livePollTimer)clearTimeout(livePollTimer);livePollTimer=setTimeout(pollLive,1000);setTimeout(()=>document.querySelector('#aiMultiMode #reviewRefresh')?.click(),300)}catch(err){statusNotice(err.message,'error');if(button){button.disabled=false;button.textContent='Request external review'}}
  }

  async function sendOwnerMessage(workItemId,button){
    if(!workItemId)return;const input=document.querySelector('#aiMultiMode #reviewRevisionInstruction');const message=String(input?.value||'').trim();if(!message){statusNotice('Write a message before sending.','error');return}if(button)button.disabled=true;
    try{const item=await api('/dashboard/api/ai-workspace/multi-agent/work-items/'+encodeURIComponent(workItemId)+'/owner-messages',{method:'POST',body:JSON.stringify({message})});hydrateWorkId=workItemId;renderLive(item);statusNotice('Message saved. Send review when you want the native team to act on the pending feedback.','success')}catch(err){statusNotice(err.message,'error');if(button)button.disabled=false}
  }

  async function sendReviewPass(workItemId,button){
    if(!workItemId||button?.disabled)return;if(button){button.disabled=true;button.textContent='Sending review…'}statusNotice('Sending the pending Owner/external feedback to the native review team…');
    try{const item=await api('/dashboard/api/ai-workspace/multi-agent/work-items/'+encodeURIComponent(workItemId)+'/feedback-pass',{method:'POST',body:JSON.stringify({instruction:null})});hydrateWorkId=workItemId;renderLive(item);statusNotice('Review sent. Native participants are running a new pass.','success');liveWorkId=workItemId;liveLastSignature=signature(item);if(livePollTimer)clearTimeout(livePollTimer);livePollTimer=setTimeout(pollLive,1000)}catch(err){statusNotice(err.message,'error');if(button){button.disabled=false;button.textContent='Send review'}}
  }

  async function deleteReview(workItemId,button){
    if(!workItemId)return;const confirmed=window.confirm('Delete this Review from workspace history? Audit evidence will be preserved.');if(!confirmed)return;if(button){button.disabled=true;button.dataset.restoreText=button.textContent;button.textContent=button.classList.contains('review-work-delete')?'…':'Deleting…'}
    try{await api('/dashboard/api/ai-workspace/multi-agent/work-items/'+encodeURIComponent(workItemId),{method:'DELETE'});if(liveWorkId===workItemId)stopLivePolling();if(hydrateWorkId===workItemId)hydrateWorkId=null;const activeCard=document.querySelector('#aiMultiMode .review-work-item.active');const activeId=activeCard?.dataset.workId||'';if(activeId===workItemId){const detail=document.querySelector('#aiMultiMode #reviewWorkDetail');if(detail)detail.innerHTML='<div class="review-empty"><strong>Review deleted</strong><p>Removed from Recent Review work. Audit evidence remains preserved.</p></div>'}statusNotice('Review deleted from workspace history. Audit evidence was preserved.','success');setTimeout(()=>document.querySelector('#aiMultiMode #reviewRefresh')?.click(),250)}catch(err){statusNotice(err.message,'error');if(button){button.disabled=false;button.textContent=button.dataset.restoreText||'×'}}
  }

  function addWorkCardDeleteControls(scope=document){scope.querySelectorAll?.('#aiMultiMode .review-work-item:not([data-delete-shell-ready])').forEach(card=>{const id=card.dataset.workId;if(!id)return;card.dataset.deleteShellReady='1';const parent=card.parentNode;if(!parent)return;const shell=document.createElement('div');shell.className='review-work-card-shell';parent.insertBefore(shell,card);shell.appendChild(card);const button=document.createElement('button');button.type='button';button.className='review-delete-action review-work-delete';button.dataset.reviewDeleteFor=id;button.textContent='×';button.setAttribute('aria-label','Delete '+(card.querySelector('.review-work-title strong')?.textContent||'Review'));button.title='Delete review';shell.appendChild(button)})}

  function syncFederationAction(detail,id){
    const head=detail?.querySelector('.review-chatbox-head');if(!id||!head)return;head.querySelectorAll('.review-federation-action').forEach(el=>el.remove());const status=detail.querySelector('.review-status')?.textContent?.trim()||'';if(status!=='WAITING_OWNER'&&status!=='WAITING_EXTERNAL')return;hydrateOpenedReview()
  }

  function polishReviewDom(scope=document){
    scope.querySelectorAll?.('.review-chat-bubble:not([data-review-polished])').forEach(bubble=>{const clean=cleanDisplayText(bubble.textContent||'');bubble.textContent=clean;bubble.dataset.reviewCopyText=clean;bubble.dataset.reviewPolished='1';const turn=bubble.closest('.review-chat-turn');if(turn&&!turn.querySelector('.review-message-copy')){const button=document.createElement('button');button.type='button';button.className='review-message-copy';button.textContent='Copy';turn.appendChild(button)}});
    addWorkCardDeleteControls(scope);const detail=scope.querySelector?.('#reviewWorkDetail')||document.querySelector('#reviewWorkDetail');const id=detail?.querySelector('.review-id')?.textContent?.trim();const head=detail?.querySelector('.review-chatbox-head');if(head)head.querySelectorAll('.review-delete-action').forEach(button=>button.remove());if(id&&head&&!head.querySelector('.review-export-actions')){const wrapper=document.createElement('div');wrapper.innerHTML=reviewExportHtml(id);const actions=wrapper.firstElementChild;if(actions)head.appendChild(actions)}if(id&&head)ensureReviewBackButton();syncFederationAction(detail,id);
  }

  function currentConversationId(){return document.querySelector('.ai-conversation-item.active [data-ai-conversation]')?.dataset.aiConversation||null}
  function singleExportHtml(id,position='top'){const encoded=encodeURIComponent(id);return '<div class="ai-chat-export-actions ai-chat-export-'+esc(position)+'" data-conversation-id="'+esc(id)+'"><span>Export</span><a href="/dashboard/api/ai-workspace/conversations/'+encoded+'/export?format=docx">DOCX</a><a href="/dashboard/api/ai-workspace/conversations/'+encoded+'/export?format=json">JSON</a></div>'}
  function syncSingleChatExport(){
    const id=currentConversationId();const head=document.querySelector('.ai-chat-head');const form=document.querySelector('#aiChatForm');if(!head||!form)return;
    let actions=head.querySelector('.ai-chat-export-actions');if(!id){actions?.remove();form.querySelector('.ai-chat-export-composer')?.remove();return}
    if(!actions||actions.dataset.conversationId!==id){if(actions)actions.remove();const wrapper=document.createElement('div');wrapper.innerHTML=singleExportHtml(id);actions=wrapper.firstElementChild;if(actions)head.appendChild(actions)}
    let bottom=form.querySelector('.ai-chat-export-composer');if(!bottom||bottom.dataset.conversationId!==id){bottom?.remove();const wrapper=document.createElement('div');wrapper.innerHTML=singleExportHtml(id,'composer');bottom=wrapper.firstElementChild;if(bottom){bottom.classList.add('ai-chat-export-composer');form.prepend(bottom)}}
    const send=form.querySelector('#aiSend');if(send){send.classList.add('ai-send-icon');send.textContent='➤';send.setAttribute('aria-label','Send message');send.title='Send message'}
  }
  function reconcileDom(){reconcileFrame=null;polishReviewDom(document);syncSingleChatExport();hydrateOpenedReview()}
  function scheduleReconcile(){if(reconcileFrame!==null)return;reconcileFrame=requestAnimationFrame(reconcileDom)}

  document.addEventListener('click',event=>{
    const run=event.target.closest('#aiMultiMode #reviewRun');if(run){event.preventDefault();event.stopPropagation();startLiveReview();return}
    const copy=event.target.closest('.review-message-copy');if(copy){const text=copy.closest('.review-chat-turn')?.querySelector('.review-chat-bubble')?.dataset.reviewCopyText||'';copyText(text,copy);return}
    const back=event.target.closest('[data-review-back]');if(back){event.preventDefault();event.stopPropagation();exitReviewChatView();return}
    const ownerSend=event.target.closest('[data-owner-message-send]');if(ownerSend){event.preventDefault();event.stopPropagation();sendOwnerMessage(ownerSend.dataset.ownerMessageSend,ownerSend);return}
    const reviewSend=event.target.closest('[data-review-send-pass]');if(reviewSend){event.preventDefault();event.stopPropagation();sendReviewPass(reviewSend.dataset.reviewSendPass,reviewSend);return}
    const external=event.target.closest('[data-request-external-review]');if(external){event.preventDefault();event.stopPropagation();requestExternalReview(external.dataset.requestExternalReview,external);return}
    const deleteButton=event.target.closest('.review-delete-action');if(deleteButton){event.preventDefault();event.stopPropagation();deleteReview(deleteButton.dataset.reviewDeleteFor,deleteButton);return}
    if(event.target.closest('[data-ai-conversation],#aiNewConversation,#aiWorkspaceNav,[data-ai-tab],#aiMultiMode .review-work-item')){const card=event.target.closest('#aiMultiMode .review-work-item');if(card){hydrateWorkId=null;enterReviewChatView()}scheduleReconcile()}
  },true);

  const observer=new MutationObserver(()=>scheduleReconcile());observer.observe(root,{childList:true,subtree:true});scheduleReconcile();
})();