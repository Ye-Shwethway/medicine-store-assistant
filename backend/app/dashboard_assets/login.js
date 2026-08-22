(()=>{
  const root=document.querySelector('#loginRoot');
  const form=document.querySelector('#loginForm');
  if(!root||!form)return;
  const username=document.querySelector('#username');
  const password=document.querySelector('#password');
  const error=document.querySelector('#loginError');
  const submit=document.querySelector('#submitButton');
  const theme=document.querySelector('#themeToggle');
  const panels={signIn:document.querySelector('#signInPanel'),request:document.querySelector('#requestPanel'),forgot:document.querySelector('#forgotPanel'),reset:document.querySelector('#resetPanel')};
  const requestForm=document.querySelector('#requestForm');
  const forgotForm=document.querySelector('#forgotForm');
  const resetForm=document.querySelector('#resetForm');
  let resetToken='';

  theme?.addEventListener('click',()=>{root.dataset.theme=root.dataset.theme==='dark'?'light':'dark'});

  async function api(path,opts={}){
    const response=await fetch(path,{credentials:'same-origin',headers:{'Content-Type':'application/json',...(opts.headers||{})},...opts});
    let data=null;try{data=await response.json()}catch{}
    if(!response.ok){const err=new Error((data&&data.detail)||('Request failed: '+response.status));err.status=response.status;throw err}
    return data;
  }

  function show(name){
    Object.entries(panels).forEach(([key,panel])=>{panel.hidden=key!==name});
    error.textContent='';
    if(name==='signIn')username.focus();
    if(name==='request')document.querySelector('#requestDisplayName').focus();
    if(name==='forgot')document.querySelector('#forgotUsername').focus();
    if(name==='reset')document.querySelector('#resetPassword').focus();
  }

  function resetHashToken(){
    const match=location.hash.match(/^#reset=([^&]+)$/);
    if(!match)return false;
    try{resetToken=decodeURIComponent(match[1])}catch{resetToken=''}
    if(!resetToken)return false;
    show('reset');
    return true;
  }

  async function bootstrap(){
    if(resetHashToken())return;
    try{const state=await api('/dashboard/api/session');if(state.authenticated){location.replace('/dashboard');return}if(!state.configured){error.textContent='Dashboard access is not provisioned on the server yet.';submit.disabled=true}}
    catch{error.textContent='Unable to read dashboard authentication state.'}
  }

  form.addEventListener('submit',async e=>{
    e.preventDefault();error.textContent='';submit.disabled=true;submit.textContent='Signing in…';
    try{await api('/dashboard/api/session',{method:'POST',body:JSON.stringify({username:username.value,password:password.value})});password.value='';location.replace('/dashboard')}
    catch(err){error.textContent=err.status===401?'Sign-in failed. Check your username and password and try again.':err.message;submit.disabled=false;submit.textContent='Sign in'}
  });

  document.querySelector('#requestOpen')?.addEventListener('click',()=>show('request'));
  document.querySelector('#requestCancel')?.addEventListener('click',()=>show('signIn'));
  document.querySelector('#forgotOpen')?.addEventListener('click',()=>show('forgot'));
  document.querySelector('#forgotCancel')?.addEventListener('click',()=>show('signIn'));
  document.querySelector('#resetCancel')?.addEventListener('click',()=>{history.replaceState(null,'',location.pathname);resetToken='';show('signIn')});

  requestForm?.addEventListener('submit',async e=>{
    e.preventDefault();const requestError=document.querySelector('#requestError');const requestSuccess=document.querySelector('#requestSuccess');const requestSubmit=document.querySelector('#requestSubmit');requestError.textContent='';requestSuccess.textContent='';requestSubmit.disabled=true;requestSubmit.textContent='Submitting…';
    try{const data=await api('/dashboard/api/access-requests',{method:'POST',body:JSON.stringify({display_name:document.querySelector('#requestDisplayName').value,username:document.querySelector('#requestUsername').value,password:document.querySelector('#requestPassword').value})});document.querySelector('#requestPassword').value='';requestSuccess.textContent=data.message||'Request submitted for Owner review.';requestSubmit.textContent='Request submitted'}
    catch(err){requestError.textContent=err.message;requestSubmit.disabled=false;requestSubmit.textContent='Submit request'}
  });

  forgotForm?.addEventListener('submit',async e=>{
    e.preventDefault();const forgotError=document.querySelector('#forgotError');const forgotSuccess=document.querySelector('#forgotSuccess');const forgotSubmit=document.querySelector('#forgotSubmit');forgotError.textContent='';forgotSuccess.textContent='';forgotSubmit.disabled=true;forgotSubmit.textContent='Submitting…';
    try{const data=await api('/dashboard/api/password-reset-requests',{method:'POST',body:JSON.stringify({username:document.querySelector('#forgotUsername').value})});forgotSuccess.textContent=data.message||'If the account is eligible, the request is pending Owner review.';forgotSubmit.textContent='Request submitted'}
    catch(err){forgotError.textContent='Unable to submit the reset request.';forgotSubmit.disabled=false;forgotSubmit.textContent='Request reset'}
  });

  resetForm?.addEventListener('submit',async e=>{
    e.preventDefault();const resetError=document.querySelector('#resetError');const resetSuccess=document.querySelector('#resetSuccess');const resetSubmit=document.querySelector('#resetSubmit');resetError.textContent='';resetSuccess.textContent='';resetSubmit.disabled=true;resetSubmit.textContent='Resetting…';
    try{const data=await api('/dashboard/api/password-resets/complete',{method:'POST',body:JSON.stringify({token:resetToken,new_password:document.querySelector('#resetPassword').value})});document.querySelector('#resetPassword').value='';resetToken='';history.replaceState(null,'',location.pathname);resetSuccess.textContent=data.message||'Password reset complete. Sign in with the new password.';resetSubmit.textContent='Password reset';setTimeout(()=>show('signIn'),700)}
    catch(err){resetError.textContent=err.message;resetSubmit.disabled=false;resetSubmit.textContent='Reset password'}
  });

  bootstrap();
})();