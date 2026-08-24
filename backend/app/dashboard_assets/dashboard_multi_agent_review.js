(()=>{
  const root=document.querySelector('#msa');
  const host=document.querySelector('#aiMultiMode');
  const tab=document.querySelector('#aiMultiTab');
  if(!root||!host||!tab||host.dataset.reviewUiReady)return;
  host.dataset.reviewUiReady='1';

  let sessions=[];
  let selectedSession=null;
  let roleState=[];
  let workItems=[];
  let currentWorkItemId=null;
  let conversations=[];
  let evidenceAttachments=[];
  let busy=false;
  let rolesSaved=false;

  const esc=value=>String(value??'').replace(/[&<>'"]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;',"'":'&#39;','"':'&quot;'}[c]));
  const compact=value=>String(value??'').replace(/\s+/g,' ').trim();
  const json=value=>{try{return JSON.stringify(value??{},null,2)}catch{return String(value??'')}};
  const time=value=>{const d=new Date(value);return Number.isNaN(d.getTime())?'':d.toLocaleString([],{month:'short',day:'numeric',hour:'numeric',minute:'2-digit'})};
  async function api(path,opts={}){
    const response=await fetch(path,{credentials:'same-origin',headers:{'Content-Type':'application/json',...(opts.headers||{})},...opts});
    let data=null;try{data=await response.json()}catch{}
    if(!response.ok){let message='Request failed: '+response.status;if(data?.detail)message=typeof data.detail==='string'?data.detail:(data.detail.message||data.detail.code||message);const error=new Error(message);error.status=response.status;error.data=data;throw error}
    return data;
  }
  function setStatus(text,kind='info'){
    const el=host.querySelector('#reviewUiStatus');if(!el)return;el.textContent=text||'';el.dataset.kind=kind;el.hidden=!text;
  }
  function syncRoleSaveState(){
    const save=host.querySelector('#reviewSaveRoles');if(!save)return;
    const hasRows=host.querySelectorAll('[data-role-agent]').length>0;
    save.textContent=rolesSaved?'Saved':'Save roles';
    save.disabled=busy||!hasRows||rolesSaved;
  }
  function setBusy(value){
    busy=value;
    host.querySelectorAll('button,input,select,textarea').forEach(el=>{if(!el.dataset.alwaysEnabled)el.disabled=value});
    const run=host.querySelector('#reviewRun');if(run)run.textContent=value?'Review running…':'Run native review';
    syncRoleSaveState();
  }
  function statusPill(status){return '<span class="review-status review-status-'+esc(String(status||'').toLowerCase())+'">'+esc(status||'UNKNOWN')+'</span>'}

  function shell(){
    host.innerHTML=`
      <div class="review-header">
        <div><h2>Multi-Agent Review</h2><p>Owner-only native REVIEW workflow. Internal agents run independently; no public MCP or inventory mutation is used.</p></div>
        <div class="review-mode-badges"><span>REVIEW live</span><span class="muted-chip">GROUP / COMPARE / DEBATE later</span></div>
      </div>
      <div id="reviewUiStatus" class="review-notice" role="status" aria-live="polite" hidden></div>
      <div class="review-grid">
        <section class="card panel review-config">
          <div class="review-section-head"><div><h3>1 · Review preset</h3><p>Select an open native REVIEW session and assign stable orchestration roles.</p></div><button class="secondary" id="reviewRefresh" type="button">Refresh</button></div>
          <label for="reviewSessionSelect">REVIEW preset</label>
          <select id="reviewSessionSelect"><option value="">Loading REVIEW presets…</option></select>
          <div id="reviewPresetMeta" class="review-preset-meta"></div>
          <div id="reviewRoleRows" class="review-role-rows"><div class="empty-copy">Choose a REVIEW preset.</div></div>
          <button id="reviewSaveRoles" type="button" disabled>Save roles</button>
        </section>
        <section class="card panel review-compose">
          <div class="review-section-head"><div><h3>2 · Task & evidence</h3><p>Create a durable Work Item. Saved Chat attachments can be referenced as evidence; vision/OCR is not processed yet.</p></div></div>
          <label for="reviewTitle">Work title</label>
          <input id="reviewTitle" maxlength="180" placeholder="e.g. Review NEW_UNMAPPED mapping proposal">
          <label for="reviewTask">Owner task</label>
          <textarea id="reviewTask" maxlength="20000" placeholder="Describe what the agents should analyze, review, and synthesize."></textarea>
          <label for="reviewEvidenceConversation">Saved Chat evidence <span class="optional">optional</span></label>
          <select id="reviewEvidenceConversation"><option value="">No saved Chat evidence</option></select>
          <div id="reviewEvidenceFiles" class="review-evidence-files"><p class="muted">Select a Chat conversation to reference its saved attachments.</p></div>
          <div class="review-boundary"><strong>No store mutation</strong><span>The automatic workflow stops at WAITING_OWNER. APPROVED is not COMMITTED.</span></div>
          <button id="reviewRun" type="button">Run native review</button>
        </section>
      </div>
      <div class="review-results-grid">
        <section class="card panel review-history">
          <div class="review-section-head"><div><h3>Recent Review work</h3><p>Persisted Work Items. History read failures do not block a new Review.</p></div></div>
          <div id="reviewHistoryNotice" class="review-history-notice" hidden></div>
          <div id="reviewWorkList" class="review-work-list"><div class="empty-copy">Loading Review work…</div></div>
        </section>
        <section class="card panel review-detail review-chatbox-shell">
          <div id="reviewWorkDetail"><div class="review-empty"><strong>Review chat</strong><p>Run a review or open a recent Work Item to see the Owner and agent turns here.</p></div></div>
        </section>
      </div>`;
  }

  function renderSessions(){
    const select=host.querySelector('#reviewSessionSelect');
    const reviewSessions=sessions.filter(s=>s.mode==='REVIEW'&&s.state==='OPEN');
    select.innerHTML='<option value="">Choose a REVIEW preset…</option>'+reviewSessions.map(s=>'<option value="'+esc(s.session_id)+'">'+esc(s.session_name)+' · '+Number((s.participants||[]).length)+' agents</option>').join('');
    if(selectedSession&&reviewSessions.some(s=>s.session_id===selectedSession.session_id))select.value=selectedSession.session_id;
    if(!reviewSessions.length)host.querySelector('#reviewRoleRows').innerHTML='<div class="review-empty"><strong>No open REVIEW preset</strong><p>Create one in AI Agent Management, then return here.</p></div>';
  }

  function defaultRole(index,total){if(index===0)return'ANALYST';if(index===total-1&&total>2)return'SYNTHESIZER';return'REVIEWER'}
  function renderRoles(){
    const meta=host.querySelector('#reviewPresetMeta');
    const rows=host.querySelector('#reviewRoleRows');
    const save=host.querySelector('#reviewSaveRoles');
    if(!selectedSession){rolesSaved=false;meta.innerHTML='';rows.innerHTML='<div class="empty-copy">Choose a REVIEW preset.</div>';syncRoleSaveState();return}
    const participants=(selectedSession.participants||[]).filter(p=>p.is_active!==false);
    meta.innerHTML='<strong>'+esc(selectedSession.session_name)+'</strong><span>'+esc(selectedSession.objective||'No preset objective')+'</span>';
    rows.innerHTML=participants.map((p,index)=>{
      const existing=roleState.find(r=>r.agent_id===p.agent_id);
      const role=existing?.orchestration_role||defaultRole(index,participants.length);
      const label=existing?.display_label||p.role_label||'';
      return '<div class="review-role-row" data-role-agent="'+esc(p.agent_id)+'">'
        +'<div class="review-agent"><strong>'+esc(p.display_name)+'</strong><span>'+esc(p.call_name)+' · position '+Number(p.position)+'</span></div>'
        +'<label><span>Role</span><select data-role-select><option'+(role==='ANALYST'?' selected':'')+'>ANALYST</option><option'+(role==='REVIEWER'?' selected':'')+'>REVIEWER</option><option'+(role==='SYNTHESIZER'?' selected':'')+'>SYNTHESIZER</option></select></label>'
        +'<label><span>Display label</span><input data-role-label maxlength="80" value="'+esc(label)+'" placeholder="Optional label"></label>'
        +'</div>';
    }).join('');
    syncRoleSaveState();
  }

  async function selectSession(id){
    selectedSession=sessions.find(s=>s.session_id===id)||null;roleState=[];rolesSaved=false;renderRoles();if(!selectedSession)return;
    try{
      const data=await api('/dashboard/api/ai-workspace/multi-agent/sessions/'+encodeURIComponent(id)+'/roles');
      roleState=data.roles||[];
      const participantCount=(selectedSession.participants||[]).filter(p=>p.is_active!==false).length;
      rolesSaved=participantCount>0&&roleState.length===participantCount;
      renderRoles();
    }catch(err){if(err.status!==404)setStatus(err.message,'error')}
  }

  async function saveRoles(){
    if(busy||!selectedSession)return;
    const assignments=[...host.querySelectorAll('[data-role-agent]')].map(row=>({agent_id:row.dataset.roleAgent,orchestration_role:row.querySelector('[data-role-select]').value,display_label:compact(row.querySelector('[data-role-label]').value)||null}));
    if(!assignments.length)return;
    setBusy(true);setStatus('Saving stable orchestration roles…');
    try{await api('/dashboard/api/ai-workspace/multi-agent/sessions/'+encodeURIComponent(selectedSession.session_id)+'/roles',{method:'PUT',body:JSON.stringify({assignments})});const data=await api('/dashboard/api/ai-workspace/multi-agent/sessions/'+encodeURIComponent(selectedSession.session_id)+'/roles');roleState=data.roles||[];rolesSaved=true;renderRoles();setStatus('Roles saved. These labels do not grant authority.','success')}catch(err){setStatus(err.message,'error')}finally{setBusy(false)}
  }

  async function loadEvidenceConversations(){
    try{const data=await api('/dashboard/api/ai-workspace/conversation-cards');conversations=data.items||[];const select=host.querySelector('#reviewEvidenceConversation');select.innerHTML='<option value="">No saved Chat evidence</option>'+conversations.map(c=>'<option value="'+esc(c.conversation_id)+'">'+esc(c.title)+' · '+esc(c.agent_display_name)+'</option>').join('')}catch{conversations=[]}
  }
  async function loadEvidenceFiles(conversationId){
    const box=host.querySelector('#reviewEvidenceFiles');evidenceAttachments=[];
    if(!conversationId){box.innerHTML='<p class="muted">Select a Chat conversation to reference its saved attachments.</p>';return}
    try{const data=await api('/dashboard/api/ai-workspace/conversations/'+encodeURIComponent(conversationId)+'/attachments');evidenceAttachments=data.items||[];if(!evidenceAttachments.length){box.innerHTML='<p class="muted">This conversation has no saved attachments.</p>';return}box.innerHTML=evidenceAttachments.map(a=>'<label class="review-evidence-file"><input type="checkbox" value="'+esc(a.attachment_id)+'"><span><strong>'+esc(a.filename)+'</strong><small>'+esc(a.kind)+' · '+Math.max(1,Math.round(Number(a.byte_size||0)/1024))+' KB · '+esc(a.state)+'</small></span></label>').join('')}catch(err){box.innerHTML='<p class="error-text">'+esc(err.message)+'</p>'}
  }
  function selectedAttachmentIds(){return[...host.querySelectorAll('#reviewEvidenceFiles input[type="checkbox"]:checked')].map(x=>x.value)}

  async function runReview(){
    if(busy)return;
    const sessionId=host.querySelector('#reviewSessionSelect').value;
    const title=compact(host.querySelector('#reviewTitle').value);
    const task=host.querySelector('#reviewTask').value.trim();
    if(!sessionId){setStatus('Choose an open REVIEW preset first.','error');return}
    if(!title||!task){setStatus('Enter both a Work title and Owner task.','error');return}
    const conversationId=host.querySelector('#reviewEvidenceConversation').value||null;
    const attachmentIds=selectedAttachmentIds();
    setBusy(true);setStatus('Native participants are reviewing in preset order. This can take a little while…');
    try{
      const item=await api('/dashboard/api/ai-workspace/multi-agent/reviews',{method:'POST',body:JSON.stringify({session_id:sessionId,title,task,evidence_conversation_id:conversationId,attachment_ids:attachmentIds})});
      currentWorkItemId=item.work_item_id;renderWorkDetail(item);setStatus('Review completed and is waiting for Owner attention.','success');await loadWorkItemsSafe();
    }catch(err){setStatus(err.message,'error');await loadWorkItemsSafe()}finally{setBusy(false)}
  }

  function renderWorkItems(){
    const list=host.querySelector('#reviewWorkList');
    if(!workItems.length){list.innerHTML='<div class="review-empty"><strong>No Review work yet</strong><p>Run a native review to create the first durable Work Item.</p></div>';return}
    list.innerHTML=workItems.map(item=>'<button type="button" class="review-work-item'+(item.work_item_id===currentWorkItemId?' active':'')+'" data-work-id="'+esc(item.work_item_id)+'"><span class="review-work-title"><strong>'+esc(item.title)+'</strong>'+statusPill(item.status)+'</span><small>'+esc(item.session_name||'REVIEW')+'</small><small>'+esc(time(item.updated_at))+'</small></button>').join('');
  }
  function renderHistoryNotice(text){const el=host.querySelector('#reviewHistoryNotice');if(!el)return;el.textContent=text||'';el.hidden=!text}
  async function loadWorkItemsSafe(){
    try{
      const data=await api('/dashboard/api/ai-workspace/multi-agent/work-items');
      workItems=data.items||[];
      renderHistoryNotice(data.degraded?'Recent Review history is temporarily unavailable. You can still configure and run a new Review.':'');
      renderWorkItems();
      if(!data.degraded&&!currentWorkItemId&&workItems.length){currentWorkItemId=workItems[0].work_item_id;await openWork(currentWorkItemId)}
    }catch{
      workItems=[];renderWorkItems();renderHistoryNotice('Recent Review history is temporarily unavailable. You can still configure and run a new Review.');
    }
  }
  async function openWork(id){
    currentWorkItemId=id;renderWorkItems();
    try{const item=await api('/dashboard/api/ai-workspace/multi-agent/work-items/'+encodeURIComponent(id));renderWorkDetail(item)}catch(err){setStatus(err.message,'error')}
  }

  function ownerTurn(item,artifact){
    const payload=artifact?.payload||{};const text=payload.task||item.objective||'';
    return '<article class="review-chat-turn review-chat-owner"><div class="review-chat-meta"><strong>Owner</strong><span>TASK</span></div><div class="review-chat-bubble">'+esc(text)+'</div></article>';
  }
  function agentTurn(a,reviews){
    const payload=a.payload||{};const text=payload.response||payload.instruction||json(payload);const prov=payload.provenance||{};const role=payload.role||a.artifact_type;const related=reviews.find(r=>r.findings?.review_output_artifact_id===a.artifact_id);const verdict=related?'<span class="review-verdict">'+esc(related.verdict)+'</span>':'';
    return '<article class="review-chat-turn review-chat-agent"><div class="review-chat-meta"><div><strong>'+esc(prov.agent_display_name||payload.display_label||'Internal agent')+'</strong><span>'+esc(role)+'</span></div>'+verdict+'</div><div class="review-chat-bubble">'+esc(text)+'</div><div class="review-chat-provenance"><span>'+esc((prov.selected_provider_name||'Provider')+' · '+(prov.selected_model_name||prov.selected_model_id||'Model'))+'</span>'+(prov.fallback_used?'<span>fallback</span>':'')+(prov.latency_ms!=null?'<span>'+esc(prov.latency_ms+' ms')+'</span>':'')+'</div></article>';
  }
  function externalTurn(a){const payload=a.payload||{};const text=payload.notes||'';const verdict=payload.verdict?'<span class="review-verdict">'+esc(payload.verdict)+'</span>':'';return '<article class="review-chat-turn review-chat-agent review-chat-external"><div class="review-chat-meta"><div><strong>'+esc(payload.external_agent_display_name||payload.external_agent_call_name||'External MCP reviewer')+'</strong><span>EXTERNAL REVIEW</span></div>'+verdict+'</div><div class="review-chat-bubble">'+esc(text)+'</div><div class="review-chat-provenance"><span>External MCP evidence · exact artifact v'+Number(payload.bound_artifact_version||0)+'</span></div></article>'}
  function revisionTurn(a){const payload=a.payload||{};return '<article class="review-chat-turn review-chat-owner"><div class="review-chat-meta"><strong>Owner</strong><span>REVISION</span></div><div class="review-chat-bubble">'+esc(payload.instruction||'')+'</div></article>'}
  function renderWorkDetail(item){
    if(window.MSAReviewChatRenderer?.render){window.MSAReviewChatRenderer.render(item);return}
    const detail=host.querySelector('#reviewWorkDetail');
    const reviews=item.reviews||[];const artifacts=item.artifacts||[];const events=item.events||[];const attention=item.attention||[];
    const ownerArtifact=artifacts.find(a=>a.artifact_type==='OWNER_TASK');
    const turns=[];if(ownerArtifact||item.objective)turns.push(ownerTurn(item,ownerArtifact));
    artifacts.filter(a=>a.artifact_type==='PARTICIPANT_OUTPUT').forEach(a=>turns.push(agentTurn(a,reviews)));
    artifacts.filter(a=>a.artifact_type==='EXTERNAL_REVIEW_SUBMISSION').forEach(a=>turns.push(externalTurn(a)));
    artifacts.filter(a=>a.artifact_type==='OWNER_REVISION').forEach(a=>turns.push(revisionTurn(a)));
    detail.innerHTML='<div class="review-chatbox-head"><div><div class="review-detail-title"><h3>'+esc(item.title)+'</h3>'+statusPill(item.status)+'</div><span class="review-id">'+esc(item.work_item_id)+'</span></div><div class="review-safety-line"><strong>Production mutation: NO</strong><span>Database canonical: NO</span></div></div>'
      +'<div class="review-chat-stream">'+(turns.length?turns.join(''):'<div class="review-empty">No persisted turns yet.</div>')+'</div>'
      +(item.status==='WAITING_OWNER'?'<div class="review-owner-action review-chat-composer"><label for="reviewRevisionInstruction">Owner feedback / next review pass</label><textarea id="reviewRevisionInstruction" maxlength="5000" placeholder="Add instructions, or leave blank to send the external review back to the native team."></textarea><button type="button" id="reviewReturnRevision">Send feedback to review team</button></div>':'')
      +'<details class="review-debug-details"><summary>Review records & timeline</summary><div class="review-detail-section"><h4>Reviews</h4>'+(reviews.length?reviews.map(r=>'<article class="review-record"><div><strong>'+esc(r.verdict)+'</strong><span>artifact v'+Number(r.artifact_version)+' · '+esc(r.reviewer_actor_type)+'</span></div><pre>'+esc(r.notes||'')+'</pre></article>').join(''):'<p class="muted">No reviewer record.</p>')+'</div><div class="review-detail-section"><h4>Attention & timeline</h4>'+(attention.length?attention.map(a=>'<div class="review-timeline"><strong>'+esc(a.category)+'</strong><span>'+esc(a.status)+' · '+esc(a.summary)+'</span></div>').join(''):'')+events.slice().reverse().map(e=>'<div class="review-timeline"><strong>'+esc(e.event_type)+'</strong><span>'+esc(e.actor_type)+' · '+esc(time(e.created_at))+'</span></div>').join('')+'</div></details>';
    const stream=host.querySelector('.review-chat-stream');if(stream)stream.scrollTop=stream.scrollHeight;
  }

  async function returnForRevision(){
    if(busy||!currentWorkItemId)return;
    const instruction=host.querySelector('#reviewRevisionInstruction')?.value.trim()||'';
    const hasExternal=Boolean(host.querySelector('#reviewWorkDetail .review-chat-external'));
    if(!instruction&&!hasExternal){setStatus('Enter Owner feedback or request an external review first.','error');return}
    setBusy(true);setStatus('Starting a new native feedback pass…');
    try{const item=await api('/dashboard/api/ai-workspace/multi-agent/work-items/'+encodeURIComponent(currentWorkItemId)+'/feedback-pass',{method:'POST',body:JSON.stringify({instruction:instruction||null})});renderWorkDetail(item);await loadWorkItemsSafe();setStatus('Feedback sent. Native participants are running a new pass with the persisted review evidence.','success')}catch(err){setStatus(err.message,'error')}finally{setBusy(false)}
  }

  async function load(){
    shell();setStatus('Loading native Review workspace…');
    try{
      const sessionData=await api('/dashboard/api/agents/sessions/list');
      sessions=sessionData.items||[];renderSessions();setStatus('');
      loadEvidenceConversations();
      loadWorkItemsSafe();
    }catch(err){setStatus(err.message,'error')}
  }

  host.addEventListener('change',event=>{if(event.target.id==='reviewSessionSelect')selectSession(event.target.value);if(event.target.id==='reviewEvidenceConversation')loadEvidenceFiles(event.target.value);if(event.target.matches('[data-role-select],[data-role-label]')){rolesSaved=false;syncRoleSaveState()}});
  host.addEventListener('input',event=>{if(event.target.matches('[data-role-label]')){rolesSaved=false;syncRoleSaveState()}});
  host.addEventListener('click',event=>{const work=event.target.closest('[data-work-id]');if(work){openWork(work.dataset.workId);return}if(event.target.id==='reviewReturnRevision'){returnForRevision();return}if(event.target.id==='reviewRefresh'){load();return}if(event.target.id==='reviewSaveRoles'){saveRoles();return}if(event.target.id==='reviewRun'){runReview();return}});
  tab.addEventListener('click',()=>{if(!host.dataset.reviewLoaded){host.dataset.reviewLoaded='1';load()}});
})();