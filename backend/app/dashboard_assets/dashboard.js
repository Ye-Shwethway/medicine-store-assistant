(()=>{
  const root=document.querySelector('#msa');
  if(!root||root.dataset.ready)return;
  root.dataset.ready='1';
  const $=s=>root.querySelector(s);
  const $$=s=>[...root.querySelectorAll(s)];
  const live=$('#live');
  const title=$('#pageTitle');
  const subtitle=$('#pageSubtitle');
  const sessionText=$('#sessionText');
  const loginOpen=$('#loginOpen');
  const logout=$('#logout');
  const loginModal=$('#loginModal');
  const loginForm=$('#loginForm');
  const loginError=$('#loginError');
  const rowsBody=$('#inventoryRows');
  const tableEmpty=$('#tableEmpty');
  const search=$('#search');
  const classFilter=$('#classFilter');
  const sheetFilter=$('#sheetFilter');
  const userList=$('#userList');
  let authenticated=false;
  let configured=false;
  let currentUser=null;
  let rowTimer=null;

  const labels={
    overview:['Inventory overview','Read-only operational view of the current test dataset'],
    inventory:['Inventory','Spreadsheet-style test/shadow inventory grid'],
    alerts:['Expiry & alerts','Read-only attention queues'],
    shadow:['Shadow inspection','Developer-grade test-data visibility'],
    catalogue:['Catalogue','CMS catalogue and mapping diagnostics'],
    users:['User Management','Owner-only human accounts and access requests'],
    audit:['Audit','Operational audit remains a separate later slice']
  };

  function announce(text){live.textContent=text}
  function escapeHtml(value){return String(value??'').replace(/[&<>'"]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;',"'":'&#39;','"':'&quot;'}[c]))}
  function initials(value){
    const parts=String(value||'U').trim().split(/[\s._-]+/).filter(Boolean);
    return (parts.slice(0,2).map(x=>x[0]).join('')||'U').toUpperCase();
  }
  function className(value){return value==='SAFE'?'safe':value==='REVIEW'?'review':value==='NEW_UNMAPPED'?'unmapped':'conflict'}

  async function api(path,opts={}){
    const response=await fetch(path,{credentials:'same-origin',headers:{'Content-Type':'application/json',...(opts.headers||{})},...opts});
    let data=null;
    try{data=await response.json()}catch{}
    if(!response.ok){
      const err=new Error((data&&data.detail)||('Request failed: '+response.status));
      err.status=response.status;
      throw err;
    }
    return data;
  }

  function setView(view){
    if(!labels[view])view='overview';
    root.classList.remove('focus','nav-open');
    $$('.view').forEach(x=>x.classList.toggle('active',x.dataset.panel===view));
    $$('.nav-btn').forEach(x=>x.classList.toggle('active',x.dataset.view===view));
    title.textContent=labels[view][0];
    subtitle.textContent=labels[view][1];
    if(view==='inventory'&&authenticated)loadRows();
    if(view==='shadow'&&authenticated)loadReasons();
    if(view==='users'&&authenticated)loadUsers();
    announce(labels[view][0]+' opened');
  }

  function toggleTheme(){
    const next=root.dataset.theme==='dark'?'light':'dark';
    root.dataset.theme=next;
    $$('.theme-control').forEach(button=>button.setAttribute('aria-label',next==='dark'?'Switch to light theme':'Switch to dark theme'));
    announce(next+' theme enabled');
  }

  function showLogin(){location.assign('/dashboard/login')}
  function hideLogin(){loginModal.classList.remove('open');loginError.textContent=''}

  function renderProfile(user){
    if(!user){
      $('#profileAvatar').textContent='—';
      $('#profileUsername').textContent='Not signed in';
      $('#profileRole').textContent='—';
      $$('.owner-only').forEach(el=>el.hidden=true);
      return;
    }
    $('#profileAvatar').textContent=initials(user.username);
    $('#profileUsername').textContent=user.username;
    $('#profileRole').textContent=user.role.replace('_',' ');
    $$('.owner-only').forEach(el=>el.hidden=user.role!=='OWNER');
  }

  function setSessionState(state){
    configured=!!state.configured;
    authenticated=!!state.authenticated;
    currentUser=state.user||null;
    renderProfile(currentUser);
    if(authenticated&&currentUser){
      sessionText.textContent=currentUser.username+' · '+currentUser.role.replace('_',' ')+' session active — inventory remains read-only.';
      loginOpen.hidden=true;
      logout.hidden=false;
      loadOverview();
      loadRows();
      loadReasons();
      return;
    }
    if(configured){location.replace('/dashboard/login');return}
    sessionText.textContent='Dashboard access is not provisioned on the server yet.';
    loginOpen.hidden=true;
    logout.hidden=true;
    clearPrivateData();
  }

  function clearPrivateData(){
    $('#mRows').textContent='—';
    $('#mSafe').textContent='—';
    $('#mReview').textContent='—';
    $('#mUnmapped').textContent='—';
    $('#attention').innerHTML='<div class="empty-copy">Private inventory data is unavailable without an authenticated session.</div>';
    $('#shadowReasons').innerHTML='<div class="empty-copy">Private review data is unavailable without an authenticated session.</div>';
    rowsBody.innerHTML='';
    tableEmpty.textContent='Private inventory data is unavailable.';
    tableEmpty.style.display='block';
  }

  async function refreshSession(){
    try{setSessionState(await api('/dashboard/api/session'))}
    catch(err){sessionText.textContent='Unable to read dashboard session state.';announce(err.message)}
  }

  async function loadOverview(){
    if(!authenticated)return;
    try{
      const data=await api('/dashboard/api/overview');
      const batch=data.batch;
      if(!batch){clearPrivateData();return}
      $('#mRows').textContent=Number(batch.row_count||0).toLocaleString();
      $('#mSafe').textContent=Number(batch.safe_count||0).toLocaleString();
      $('#mReview').textContent=Number(batch.review_count||0).toLocaleString();
      $('#mUnmapped').textContent=Number(batch.new_unmapped_count||0).toLocaleString();
      const attention=data.attention||[];
      $('#attention').innerHTML=attention.length?attention.map(x=>'<div class="qrow"><div class="qcopy"><b>'+escapeHtml(x.review_reason)+'</b><span>'+escapeHtml(x.classification)+'</span></div><span class="status '+className(x.classification)+'">'+Number(x.row_count).toLocaleString()+'</span></div>').join(''):'<div class="empty-copy">No attention rows in the latest test batch.</div>';
      $('#healthCopy').textContent='Authenticated dashboard BFF is reading the latest test-only shadow batch.';
    }catch(err){handleReadError(err)}
  }

  async function loadRows(){
    if(!authenticated)return;
    clearTimeout(rowTimer);
    rowTimer=setTimeout(async()=>{
      const params=new URLSearchParams({limit:'100',offset:'0'});
      if(search.value.trim())params.set('q',search.value.trim());
      if(classFilter.value)params.set('classification',classFilter.value);
      if(sheetFilter.value)params.set('source_sheet',sheetFilter.value);
      rowsBody.innerHTML='';
      tableEmpty.textContent='Loading rows…';
      tableEmpty.style.display='block';
      try{const data=await api('/dashboard/api/rows?'+params.toString());renderRows(data.items||[])}
      catch(err){handleReadError(err)}
    },120);
  }

  function renderRows(items){
    rowsBody.innerHTML='';
    if(!items.length){tableEmpty.textContent='No rows match the current filters.';tableEmpty.style.display='block';return}
    tableEmpty.style.display='none';
    for(const row of items){
      const payload=row.payload||{};
      const tr=document.createElement('tr');
      tr.tabIndex=0;
      const item=payload.item_name||payload.items||'(unnamed source row)';
      const expiry=payload.expiry_date||payload.expiry||'—';
      const code=payload.serial_code||payload.cms_code||'—';
      const rowStatus=row.review_reason||'Read-only';
      tr.innerHTML='<td><strong>'+escapeHtml(item)+'</strong></td><td>'+escapeHtml(expiry)+'</td><td>'+escapeHtml(code)+'</td><td>'+escapeHtml(row.source_sheet||'—')+'</td><td><span class="status '+className(row.classification)+'">'+escapeHtml(row.classification||'—')+'</span></td><td>'+escapeHtml(rowStatus)+'</td>';
      tr.addEventListener('click',()=>openDetail(row,tr));
      tr.addEventListener('keydown',event=>{if(event.key==='Enter'||event.key===' '){event.preventDefault();openDetail(row,tr)}});
      rowsBody.appendChild(tr);
    }
    announce(items.length+' inventory rows shown');
  }

  async function loadReasons(){
    if(!authenticated)return;
    try{
      const data=await api('/dashboard/api/review-reasons');
      const items=data.items||[];
      $('#shadowReasons').innerHTML=items.length?items.map(x=>'<div class="qrow"><div class="qcopy"><b>'+escapeHtml(x.review_reason)+'</b><span>'+escapeHtml(x.classification)+'</span></div><strong>'+Number(x.row_count).toLocaleString()+'</strong></div>').join(''):'<div class="empty-copy">No review reasons found.</div>';
    }catch(err){handleReadError(err)}
  }

  function showUsersDenied(show){
    $('#usersDenied').hidden=!show;
    $('#usersContent').hidden=show;
  }

  async function loadUsers(){
    if(!authenticated)return;
    userList.innerHTML='<div class="user-list-loading">Loading human accounts…</div>';
    try{
      const data=await api('/dashboard/api/users');
      showUsersDenied(false);
      renderUsers(data.items||[]);
    }catch(err){
      if(err.status===403){showUsersDenied(true);announce('Access denied');return}
      if(err.status===401){handleReadError(err);return}
      userList.innerHTML='<div class="empty-copy">Unable to load User Management.</div>';
      announce(err.message);
    }
  }

  function renderUsers(items){
    const pending=items.filter(x=>x.request_status==='PENDING').length;
    const active=items.filter(x=>x.state==='ACTIVE').length;
    const disabled=items.filter(x=>x.state==='DISABLED').length;
    $('#uPending').textContent=pending.toLocaleString();
    $('#uActive').textContent=active.toLocaleString();
    $('#uDisabled').textContent=disabled.toLocaleString();
    if(!items.length){userList.innerHTML='<div class="empty-copy">No human accounts found.</div>';return}
    userList.innerHTML=items.map(renderUserRow).join('');
    announce(items.length+' human accounts loaded');
  }

  function roleOptions(selected){
    return ['ADMIN','STAFF','READ_ONLY'].map(role=>'<option value="'+role+'"'+(role===selected?' selected':'')+'>'+role.replace('_',' ')+'</option>').join('');
  }

  function renderUserRow(user){
    const state=String(user.state||'').toUpperCase();
    const role=user.role||'';
    const owner=role==='OWNER';
    const pending=user.request_status==='PENDING'&&state==='PENDING';
    let actions='';
    if(owner){
      actions='<span class="role-label">Protected Owner account</span>';
    }else if(pending){
      actions='<select aria-label="Role for '+escapeHtml(user.username)+'" data-role-select="'+escapeHtml(user.user_id)+'">'+roleOptions('READ_ONLY')+'</select><button class="approve" data-action="approve" data-user-id="'+escapeHtml(user.user_id)+'">Approve access</button><button class="danger-action" data-action="reject" data-user-id="'+escapeHtml(user.user_id)+'">Reject</button>';
    }else if(state==='ACTIVE'){
      actions='<select aria-label="Role for '+escapeHtml(user.username)+'" data-role-select="'+escapeHtml(user.user_id)+'">'+roleOptions(role||'READ_ONLY')+'</select><button data-action="apply-role" data-user-id="'+escapeHtml(user.user_id)+'">Assign role</button><button data-action="revoke" data-user-id="'+escapeHtml(user.user_id)+'">Revoke sessions</button><button class="danger-action" data-action="disable" data-user-id="'+escapeHtml(user.user_id)+'">Disable account</button>';
    }else if(state==='DISABLED'&&role){
      actions='<button class="approve" data-action="reactivate" data-user-id="'+escapeHtml(user.user_id)+'">Reactivate</button><button data-action="revoke" data-user-id="'+escapeHtml(user.user_id)+'">Revoke sessions</button>';
    }else{
      actions='<span class="role-label">Rejected access request</span>';
    }
    return '<div class="user-row" data-user-row="'+escapeHtml(user.user_id)+'"><div class="user-identity"><div class="user-avatar" aria-hidden="true">'+escapeHtml(initials(user.display_name||user.username))+'</div><div class="user-identity-copy"><strong>'+escapeHtml(user.display_name||user.username)+'</strong><span>@'+escapeHtml(user.username)+'</span></div></div><div class="user-state"><span class="state-pill '+state.toLowerCase()+'">'+escapeHtml(state||'UNKNOWN')+'</span></div><div class="user-role"><span class="role-label">'+escapeHtml(role?role.replace('_',' '):'Unassigned')+'</span></div><div class="user-actions">'+actions+'</div></div>';
  }

  async function performUserAction(button){
    const action=button.dataset.action;
    const userId=button.dataset.userId;
    if(!action||!userId)return;
    const row=button.closest('[data-user-row]');
    const select=row?.querySelector('[data-role-select]');
    const role=select?.value||'READ_ONLY';
    if((action==='reject'||action==='disable')&&!window.confirm(action==='reject'?'Reject this access request?':'Disable this account and revoke protected access?'))return;
    button.disabled=true;
    try{
      if(action==='approve')await api('/dashboard/api/users/'+encodeURIComponent(userId)+'/approve',{method:'POST',body:JSON.stringify({role})});
      else if(action==='reject')await api('/dashboard/api/users/'+encodeURIComponent(userId)+'/reject',{method:'POST'});
      else if(action==='apply-role')await api('/dashboard/api/users/'+encodeURIComponent(userId)+'/role',{method:'PATCH',body:JSON.stringify({role})});
      else if(action==='disable')await api('/dashboard/api/users/'+encodeURIComponent(userId)+'/disable',{method:'POST'});
      else if(action==='reactivate')await api('/dashboard/api/users/'+encodeURIComponent(userId)+'/reactivate',{method:'POST'});
      else if(action==='revoke')await api('/dashboard/api/users/'+encodeURIComponent(userId)+'/revoke-sessions',{method:'POST'});
      announce('User Management action completed');
      await loadUsers();
    }catch(err){
      announce(err.message);
      window.alert(err.message);
      button.disabled=false;
    }
  }

  function handleReadError(err){
    if(err.status===401){authenticated=false;location.replace('/dashboard/login')}
    else{announce(err.message)}
  }

  function openDetail(row,tr){
    $$('#inventoryRows tr').forEach(x=>x.classList.remove('selected'));
    tr.classList.add('selected');
    const payload=row.payload||{};
    const item=payload.item_name||payload.items||'(unnamed source row)';
    $('#detailTitle').textContent=item;
    $('#detailContent').innerHTML='<div class="detail-grid"><div class="detail"><label>Expiry</label><span>'+escapeHtml(payload.expiry_date||payload.expiry||'—')+'</span></div><div class="detail"><label>CMS code</label><span>'+escapeHtml(payload.serial_code||payload.cms_code||'—')+'</span></div><div class="detail"><label>Source sheet</label><span>'+escapeHtml(row.source_sheet||'—')+'</span></div><div class="detail"><label>Source row</label><span>'+escapeHtml(row.source_row_no||'—')+'</span></div><div class="detail"><label>Classification</label><span>'+escapeHtml(row.classification||'—')+'</span></div><div class="detail"><label>Status</label><span>'+escapeHtml(row.review_reason||'Read-only')+'</span></div></div><div class="callout"><strong>Read-only detail</strong><br>No inventory edit or save action exists in F7.</div>';
    $('#detailBack').classList.add('open');
    $('#detailClose').focus();
  }

  function closeDetail(){
    $('#detailBack').classList.remove('open');
    $$('#inventoryRows tr').forEach(x=>x.classList.remove('selected'));
  }

  $$('.nav-btn').forEach(button=>button.addEventListener('click',()=>setView(button.dataset.view)));
  $$('.theme-control').forEach(button=>button.addEventListener('click',toggleTheme));
  $('#hamburger').addEventListener('click',()=>root.classList.add('nav-open'));
  $('#drawerClose').addEventListener('click',()=>root.classList.remove('nav-open'));
  $('#navOverlay').addEventListener('click',()=>root.classList.remove('nav-open'));
  $('#backOverview').addEventListener('click',()=>setView('overview'));
  $('#fullView').addEventListener('click',()=>{root.classList.add('focus');announce('Full table view enabled')});
  $('#exitFocus').addEventListener('click',()=>{root.classList.remove('focus');setView('inventory')});
  $('#detailClose').addEventListener('click',closeDetail);
  $('#detailBack').addEventListener('click',event=>{if(event.target===event.currentTarget)closeDetail()});
  loginOpen.addEventListener('click',showLogin);
  $('#loginCancel').addEventListener('click',hideLogin);
  loginModal.addEventListener('click',event=>{if(event.target===event.currentTarget)hideLogin()});
  loginForm.addEventListener('submit',event=>{event.preventDefault();location.assign('/dashboard/login')});
  logout.addEventListener('click',async()=>{try{await api('/dashboard/api/session',{method:'DELETE'});location.replace('/dashboard/login')}catch(err){announce(err.message)}});
  [search,classFilter,sheetFilter].forEach(el=>el.addEventListener(el.tagName==='INPUT'?'input':'change',loadRows));
  $('#refresh').addEventListener('click',()=>{loadOverview();loadRows();loadReasons()});
  $('#usersRefresh').addEventListener('click',loadUsers);
  $('#deniedOverview').addEventListener('click',()=>setView('overview'));
  userList.addEventListener('click',event=>{const button=event.target.closest('button[data-action]');if(button)performUserAction(button)});
  root.addEventListener('keydown',event=>{
    if(event.key!=='Escape')return;
    if($('#detailBack').classList.contains('open'))closeDetail();
    else if(loginModal.classList.contains('open'))hideLogin();
    else if(root.classList.contains('nav-open'))root.classList.remove('nav-open');
    else if(root.classList.contains('focus'))root.classList.remove('focus');
  });

  refreshSession();
})();
