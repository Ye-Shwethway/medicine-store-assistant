from pathlib import Path
import re

js_path = Path('backend/app/dashboard_assets/dashboard_multi_agent_live_export.js')
js = js_path.read_text(encoding='utf-8')

anchor = "  function federationActionHtml(workItemId,status,hasExternalSubmission=false){\n"
if anchor not in js:
    raise SystemExit('federationActionHtml anchor missing')

nav_code = r'''  function enterReviewChatView(){
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

'''
js = js.replace(anchor, nav_code + anchor, 1)

start = js.index('  function renderLive(item){')
end = js.index('  function signature(item){', start)
new_render = r'''  function renderLive(item){
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
      if(a.artifact_type==='OWNER_REVISION'){
        const text=cleanDisplayText(a.payload?.instruction||'');
        return '<article class="review-chat-turn review-chat-owner"><div class="review-chat-meta"><strong>Owner</strong><span>FEEDBACK</span></div><div class="review-chat-bubble" data-review-copy-text="'+esc(text)+'">'+esc(text)+'</div><button class="review-message-copy" type="button">Copy</button></article>';
      }
      return '';
    };
    artifacts.forEach(a=>{const turn=artifactTurn(a);if(turn)turns.push(turn)});
    const running=item.status==='REVIEWING'?'<div class="review-live-wait"><span class="review-live-dot"></span>Waiting for the next configured participant…</div>':'';
    const hasExternal=artifacts.some(a=>a.artifact_type==='EXTERNAL_REVIEW_SUBMISSION');
    const ownerAction=item.status==='WAITING_OWNER'?'<div class="review-owner-action review-chat-composer"><label for="reviewRevisionInstruction">Owner message</label><textarea id="reviewRevisionInstruction" maxlength="5000" placeholder="Add instructions, or leave blank to send the external review back to the native team."></textarea><button type="button" id="reviewReturnRevision">Send feedback to review team</button></div>':'';
    detail.innerHTML='<div class="review-chatbox-head"><div><div class="review-detail-title"><h3>'+esc(item.title)+'</h3><span class="review-status review-status-'+esc(String(item.status||'').toLowerCase())+'">'+esc(item.status)+'</span></div><span class="review-id">'+esc(item.work_item_id)+'</span></div>'+reviewExportHtml(item.work_item_id)+'<div class="review-safety-line"><strong>Production mutation: NO</strong><span>Database canonical: NO</span></div>'+federationActionHtml(item.work_item_id,item.status,hasExternal)+'</div><div class="review-chat-stream">'+turns.join('')+running+'</div>'+ownerAction;
    ensureReviewBackButton();
    const stream=detail.querySelector('.review-chat-stream');if(stream)stream.scrollTop=stream.scrollHeight;scheduleReconcile();
  }

'''
js = js[:start] + new_render + js[end:]

old_start = "try{const item=await api('/dashboard/api/ai-workspace/multi-agent/reviews/live',{method:'POST',body:JSON.stringify({session_id:sessionId,title,task,evidence_conversation_id:conversationId,attachment_ids:attachmentIds})});liveWorkId=item.work_item_id;liveLastSignature='';hydrateWorkId=item.work_item_id;renderLive(item);pollLive()}"
new_start = "try{const item=await api('/dashboard/api/ai-workspace/multi-agent/reviews/live',{method:'POST',body:JSON.stringify({session_id:sessionId,title,task,evidence_conversation_id:conversationId,attachment_ids:attachmentIds})});liveWorkId=item.work_item_id;liveLastSignature='';hydrateWorkId=item.work_item_id;renderLive(item);enterReviewChatView();pollLive()}"
if old_start not in js:
    raise SystemExit('startLiveReview replacement anchor missing')
js = js.replace(old_start, new_start, 1)

old_click = "    const external=event.target.closest('[data-request-external-review]');if(external){event.preventDefault();event.stopPropagation();requestExternalReview(external.dataset.requestExternalReview,external);return}\n"
new_click = "    const back=event.target.closest('[data-review-back]');if(back){event.preventDefault();event.stopPropagation();exitReviewChatView();return}\n" + old_click
if old_click not in js:
    raise SystemExit('click anchor missing')
js = js.replace(old_click, new_click, 1)

old_cards = "    if(event.target.closest('[data-ai-conversation],#aiNewConversation,#aiWorkspaceNav,[data-ai-tab],#aiMultiMode .review-work-item')){const card=event.target.closest('#aiMultiMode .review-work-item');if(card)hydrateWorkId=null;scheduleReconcile()}"
new_cards = "    if(event.target.closest('[data-ai-conversation],#aiNewConversation,#aiWorkspaceNav,[data-ai-tab],#aiMultiMode .review-work-item')){const card=event.target.closest('#aiMultiMode .review-work-item');if(card){hydrateWorkId=null;enterReviewChatView()}scheduleReconcile()}"
if old_cards not in js:
    raise SystemExit('card navigation anchor missing')
js = js.replace(old_cards, new_cards, 1)

old_polish = "if(id&&head&&!head.querySelector('.review-export-actions')){const wrapper=document.createElement('div');wrapper.innerHTML=reviewExportHtml(id);const actions=wrapper.firstElementChild;if(actions)head.appendChild(actions)}syncFederationAction(detail,id);"
new_polish = "if(id&&head&&!head.querySelector('.review-export-actions')){const wrapper=document.createElement('div');wrapper.innerHTML=reviewExportHtml(id);const actions=wrapper.firstElementChild;if(actions)head.appendChild(actions)}if(id&&head)ensureReviewBackButton();syncFederationAction(detail,id);"
if old_polish not in js:
    raise SystemExit('polish anchor missing')
js = js.replace(old_polish, new_polish, 1)

js_path.write_text(js, encoding='utf-8')

css_path = Path('backend/app/dashboard_assets/dashboard_multi_agent_review.css')
css = css_path.read_text(encoding='utf-8')
css += r'''

/* Single-surface Multi-Agent navigation: list/setup OR one chatbox, never stacked detail. */
#aiMultiMode:not(.review-chat-open) .review-detail{display:none}
#aiMultiMode:not(.review-chat-open) .review-results-grid{grid-template-columns:1fr}
#aiMultiMode:not(.review-chat-open) .review-history{width:100%;max-width:none}
#aiMultiMode.review-chat-open .review-header,#aiMultiMode.review-chat-open .review-grid,#aiMultiMode.review-chat-open .review-history{display:none}
#aiMultiMode.review-chat-open .review-results-grid{display:block;margin-top:0}
#aiMultiMode.review-chat-open .review-detail{display:block;width:100%;max-width:none}
#aiMultiMode.review-chat-open .review-chatbox-shell,#aiMultiMode.review-chat-open .review-chatbox-shell>#reviewWorkDetail{min-height:calc(100dvh - 190px)}
#aiMultiMode.review-chat-open .review-chat-stream{max-height:none;min-height:48dvh}
.review-chat-back{display:none;border:0;background:transparent;color:var(--accent);font:inherit;font-size:.8rem;font-weight:800;padding:0 0 10px;cursor:pointer}
#aiMultiMode.review-chat-open .review-chat-back{display:inline-flex;align-items:center}
.review-chat-back:focus-visible{outline:3px solid color-mix(in srgb,var(--accent) 30%,transparent);outline-offset:3px;border-radius:6px}
@media(max-width:760px){#aiMultiMode.review-chat-open .review-chatbox-shell,#aiMultiMode.review-chat-open .review-chatbox-shell>#reviewWorkDetail{min-height:calc(100dvh - 150px)}#aiMultiMode.review-chat-open .review-chat-stream{min-height:52dvh}}
'''
css_path.write_text(css, encoding='utf-8')

print('multi_agent_single_surface_patch=pass')
