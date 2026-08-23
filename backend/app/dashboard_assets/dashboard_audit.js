(()=>{
  const root=document.querySelector('#msa');
  if(!root||root.dataset.auditReady)return;
  root.dataset.auditReady='1';
  const nav=root.querySelector('.nav-btn[data-view="audit"]');
  const content=root.querySelector('.content');
  if(!nav||!content)return;

  let panel=root.querySelector('.view[data-panel="audit"]');
  if(!panel){
    panel=document.createElement('section');
    panel.className='view';
    panel.dataset.panel='audit';
    content.appendChild(panel);
  }
  panel.innerHTML=`
    <div class="management-head audit-head">
      <div><h2>Audit</h2><p>Recent append-only operational evidence. Full filters and monthly history arrive in F7.3.</p></div>
      <button class="secondary" id="auditRefresh" type="button">Refresh</button>
    </div>
    <div class="agent-boundary"><strong>Current audit proof boundary</strong><p>This preview records verified external MCP inventory-summary reads. It does not yet represent the full operational ledger.</p></div>
    <article class="card panel audit-panel"><div class="users-panel-head"><div><h2>Recent activity</h2><p class="sub">Newest server-recorded events first.</p></div></div><div id="auditRecent" class="audit-list"><div class="empty-copy">Open Audit to load recent activity.</div></div></article>`;

  const list=()=>root.querySelector('#auditRecent');
  const esc=v=>String(v??'').replace(/[&<>'\"]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;',"'":'&#39;','\"':'&quot;'}[c]));
  const fmt=t=>{try{return new Date(t).toLocaleString()}catch{return String(t||'')}};

  async function loadAudit(){
    const target=list(); if(!target)return;
    target.innerHTML='<div class="empty-copy">Loading recent audit activity…</div>';
    try{
      const r=await fetch('/dashboard/api/audit/recent?limit=50',{credentials:'same-origin',headers:{Accept:'application/json'}});
      if(r.status===401){location.assign('/dashboard/login');return}
      if(!r.ok)throw new Error('Audit request failed: '+r.status);
      const data=await r.json(); const items=data.items||[];
      if(!items.length){target.innerHTML='<div class="agent-empty"><strong>No audit events yet</strong><p>Run an MSA MCP inventory summary read, then refresh this list.</p></div>';return}
      target.innerHTML=items.map(x=>`<div class="audit-row"><div class="audit-row-head"><strong>${esc(x.agent_name||x.actor_type)}</strong><span class="agent-chip">${esc(x.outcome)}</span></div><div class="audit-action">${esc(x.action_type)}</div><div class="audit-meta"><span>${esc(x.client_source)}</span><span>${esc(x.runtime_type||'—')}</span><span>${esc(x.capability_scope||'—')}</span><span>${esc(fmt(x.occurred_at))}</span></div><div class="audit-id">Correlation: ${esc(x.correlation_id)}</div></div>`).join('');
    }catch(e){target.innerHTML='<div class="empty-copy">Unable to load audit activity.</div>'}
  }

  function openAudit(e){
    if(e){e.preventDefault();e.stopImmediatePropagation()}
    root.classList.remove('focus','nav-open');
    root.querySelectorAll('.view').forEach(v=>v.classList.toggle('active',v.dataset.panel==='audit'));
    root.querySelectorAll('.nav-btn').forEach(b=>b.classList.toggle('active',b.dataset.view==='audit'));
    const title=root.querySelector('#pageTitle'); const sub=root.querySelector('#pageSubtitle');
    if(title)title.textContent='Audit'; if(sub)sub.textContent='Recent actor-aware operational evidence';
    loadAudit();
  }

  nav.addEventListener('click',openAudit,true);
  root.querySelector('#auditRefresh')?.addEventListener('click',loadAudit);
})();
