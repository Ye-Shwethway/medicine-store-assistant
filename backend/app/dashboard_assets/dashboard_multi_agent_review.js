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
  function setBusy(value){
    busy=value;
    host.querySelectorAll('button,input,select,textarea').forEach(el=>{if(!el.dataset.alwaysEnabled)el.disabled=value});
    const run=host.querySelector('#reviewRun');if(run)run.textContent=value?'Review running…':'Run native review';
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
          <div class="review-section-head"><div><h3>Recent Review work</h3><p>Persisted state reloads from the shared Work/Review substrate.</p></div></div>
          <div id="reviewWorkList" class="review-work-list"><div class="empty-copy">Loading Review work…</div></div>
        </section>
        <section class="card panel review-detail">
          <div id="reviewWorkDetail"><div class="review-empty"><strong>No Review work selected</strong><p>Run a review or open a recent Work Item.</p></div></div>
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
    if(!selectedSession){meta.innerHTML='';rows.innerHTML='<div class="empty-copy">Choose a REVIEW preset.</div>';save.disabled=true;return}
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
    save.disabled=!participants.length;
  }

  async function selectSession(id){
    selectedSession=sessions.find(s=>s.session_id===id)||null;roleState=[];renderRoles();if(!selectedSession)return;
    try{const data=await api('/dashboard/api/ai-workspace/multi-agent/sessions/'+encodeURIComponent(id)+'/roles');roleState=data.roles||[];renderRoles()}catch(err){if(err.status!==404)setStatus(err.message,'error')}
  }

  async function saveRoles(){
    if(busy||!selectedSession)return;
    const assignments=[...host.querySelectorAll('[data-role-agent]')].map(row=>({agent_id:row.dataset.roleAgent,orchestration_role:row.querySelector('[data-role-select]').value,display_label:compact(row.querySelector('[data-role-label]').value)||null}));
    if(!assignments.length)return;
    setBusy(true);setStatus('Saving stable orchestration roles…');
    try{await api('/dashboard/api/ai-workspace/multi-agent/sessions/'+encodeURIComponent(selectedSession.session_id)+'/roles',{method:'PUT',body:JSON.stringify({assignments})});const data=await api('/dashboard/api/ai-workspace/multi-agent/sessions/'+encodeURIComponent(selectedSession.session_id)+'/roles');roleState=data.roles||[];renderRoles();setStatus('Roles saved. These labels do not grant authority.','success')}catch(err){setStatus(err.message,'error')}finally{setBusy(false)}
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
      currentWorkItemId=item.work_item_id;setStatus('Review completed and is waiting for Owner attention.','success');await loadWorkItems();renderWorkDetail(item);
    }catch(err){setStatus(err.message,'error');await loadWorkItems()}finally{setBusy(false)}
  }

  function renderWorkItems(){
    const list=host.querySelector('#reviewWorkList');
    if(!workItems.length){list.innerHTML='<div class="review-empty"><strong>No Review work yet</strong><p>Run a native review to create the first durable Work Item.</p></div>';return}
    list.innerHTML=workItems.map(item=>'<button type="button" class="review-work-item'+(item.work_item_id===currentWorkItemId?' active':'')+'" data-work-id="'+esc(item.work_item_id)+'"><span class="review-work-title"><strong>'+esc(item.title)+'</strong>'+statusPill(item.status)+'</span><small>'+esc(item.session_name||'REVIEW')+' · '+Number(item.artifact_count||0)+' artifacts · '+Number(item.review_count||0)+' reviews</small><small>'+esc(time(item.updated_at))+'</small></button>').join('');
  }
  async function loadWorkItems(){
    const data=await api('/dashboard/api/ai-workspace/multi-agent/work-items');workItems=data.items||[];renderWorkItems();if(!currentWorkItemId&&workItems.length){currentWorkItemId=workItems[0].work_item_id;await openWork(currentWorkItemId)}
  }
  async function openWork(id){
    currentWorkItemId=id;renderWorkItems();setStatus('Loading Work Item…');
    try{const item=await api('/dashboard/api/ai-workspace/multi-agent/work-items/'+encodeURIComponent(id));renderWorkDetail(item);setStatus('')}catch(err){setStatus(err.message,'error')}
  }

  function artifactMarkup(a){
    const payload=a.payload||{};const text=payload.response||payload.task||payload.instruction||'';const prov=payload.provenance||null;
    return '<article class="review-artifact"><div class="review-artifact-head"><strong>'+esc(a.artifact_type)+' · v'+Number(a.version)+'</strong><span>'+esc(a.actor_type)+'</span></div>'+(text?'<pre>'+esc(text)+'</pre>':'<pre>'+esc(json(payload))+'</pre>')+(prov?'<div class="review-provenance"><b>'+esc(prov.agent_display_name||'Internal agent')+'</b><span>'+esc((prov.selected_provider_name||'Provider')+' · '+(prov.selected_model_name||prov.selected_model_id||'Model')+(prov.fallback_used?' · fallback':''))+'</span><span>'+esc(prov.latency_ms!=null?prov.latency_ms+' ms':'')+'</span></div>':'')+'</article>';
  }
  function renderWorkDetail(item){
    const detail=host.querySelector('#reviewWorkDetail');
    const reviews=item.reviews||[];const artifacts=item.artifacts||[];const events=item.events||[];const attention=item.attention||[];
    detail.innerHTML='<div class="review-detail-head"><div><div class="review-detail-title"><h3>'+esc(item.title)+'</h3>'+statusPill(item.status)+'</div><p>'+esc(item.objective||'')+'</p></div><span class="review-id">'+esc(item.work_item_id)+'</span></div>'
      +'<div class="review-safety-line"><strong>Production mutation: NO</strong><span>Database canonical: NO</span></div>'
      +(item.status==='WAITING_OWNER'?'<div class="review-owner-action"><label for="reviewRevisionInstruction">Return for revision</label><textarea id="reviewRevisionInstruction" maxlength="5000" placeholder="Tell the team what needs another review pass."></textarea><button type="button" id="reviewReturnRevision">Return to REVIEWING</button></div>':'')
      +'<div class="review-detail-section"><h4>Artifacts</h4>'+artifacts.map(artifactMarkup).join('')+'</div>'
      +'<div class="review-detail-section"><h4>Reviews</h4>'+(reviews.length?reviews.map(r=>'<article class="review-record"><div><strong>'+esc(r.verdict)+'</strong><span>artifact v'+Number(r.artifact_version)+' · '+esc(r.reviewer_actor_type)+'</span></div><pre>'+esc(r.notes||'')+'</pre></article>').join(''):'<p class="muted">No reviewer record.</p>')+'</div>'
      +'<div class="review-detail-section"><h4>Attention & timeline</h4>'+(attention.length?attention.map(a=>'<div class="review-timeline"><strong>'+esc(a.category)+'</strong><span>'+esc(a.status)+' · '+esc(a.summary)+'</span></div>').join(''):'')+events.slice().reverse().map(e=>'<div class="review-timeline"><strong>'+esc(e.event_type)+'</strong><span>'+esc(e.actor_type)+' · '+esc(time(e.created_at))+'</span></div>').join('')+'</div>';
    host.querySelector('#reviewReturnRevision')?.addEventListener('click',returnForRevision);
  }

  async function returnForRevision(){
    if(busy||!currentWorkItemId)return;
    const instruction=host.querySelector('#reviewRevisionInstruction')?.value.trim();
    if(!instruction){setStatus('Enter a revision instruction first.','error');return}
    setBusy(true);setStatus('Returning Work Item to REVIEWING…');
    try{const item=await api('/dashboard/api/ai-workspace/multi-agent/work-items/'+encodeURIComponent(currentWorkItemId)+'/return-for-revision',{method:'POST',body:JSON.stringify({instruction})});renderWorkDetail(item);await loadWorkItems();setStatus('Returned to REVIEWING. Automatic re-run is a later control; the revision instruction is persisted.','success')}catch(err){setStatus(err.message,'error')}finally{setBusy(false)}
  }

  async function load(){
    shell();setStatus('Loading native Review workspace…');
    try{
      const [sessionData]=await Promise.all([api('/dashboard/api/agents/sessions/list'),loadEvidenceConversations()]);
      sessions=sessionData.items||[];renderSessions();await loadWorkItems();setStatus('');
    }catch(err){setStatus(err.message,'error')}
  }

  host.addEventListener('change',event=>{if(event.target.id==='reviewSessionSelect')selectSession(event.target.value);if(event.target.id==='reviewEvidenceConversation')loadEvidenceFiles(event.target.value)});
  host.addEventListener('click',event=>{const work=event.target.closest('[data-work-id]');if(work){openWork(work.dataset.workId);return}if(event.target.id==='reviewRefresh'){load();return}if(event.target.id==='reviewSaveRoles'){saveRoles();return}if(event.target.id==='reviewRun'){runReview();return}});
  tab.addEventListener('click',()=>{if(!host.dataset.reviewLoaded){host.dataset.reviewLoaded='1';load()}});
})();
