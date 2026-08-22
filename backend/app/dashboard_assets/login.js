(()=>{
  const root=document.querySelector('#loginRoot');
  const form=document.querySelector('#loginForm');
  if(!root||!form)return;
  const username=document.querySelector('#username');
  const password=document.querySelector('#password');
  const error=document.querySelector('#loginError');
  const submit=document.querySelector('#submitButton');
  const theme=document.querySelector('#themeToggle');
  const panels={signIn:document.querySelector('#signInPanel'),request:document.querySelector('#requestPanel'),forgot:document.querySelector('#forgotPanel'),reset:document.querySelector('#resetPanel'),verifyEmail:document.querySelector('#verifyEmailPanel')};
  const requestForm=document.querySelector('#requestForm');
  const forgotForm=document.querySelector('#forgotForm');
  const resetForm=document.querySelector('#resetForm');
  let resetToken='';
  let verifyEmailToken='';
  let recoveryMode='username';

  theme?.addEventListener('click',()=>{root.dataset.theme=root.dataset.theme==='dark'?'light':'dark'});

  async function api(path,opts={}){
    const response=await fetch(path,{credentials:'same-origin',headers:{'Content-Type':'application/json',...(opts.headers||{})},...opts});
    let data=null;try{data=await response.json()}catch{}
    if(!response.ok){const err=new Error((data&&data.detail)||('Request failed: '+response.status));err.status=response.status;throw err}
    return data;
  }

  function configureRecoveryChoice(){
    const input=document.querySelector('#forgotUsername');
    const label=input?.previousElementSibling;
    const heading=document.querySelector('#forgotTitle')?.closest('.login-heading');
    if(!input||!label||!heading||document.querySelector('#recoveryModeSwitch'))return;
    const intro=heading.querySelector('p:not(.eyebrow)');
    if(intro)intro.textContent='Use either your account username or verified recovery email. The response stays generic for account privacy.';
    const switcher=document.createElement('div');
    switcher.id='recoveryModeSwitch';
    switcher.className='recovery-mode-switch';
    switcher.setAttribute('role','group');
    switcher.setAttribute('aria-label','Choose recovery identifier');
    switcher.innerHTML='<button type="button" data-recovery-mode="username" aria-pressed="true">Username</button><button type="button" data-recovery-mode="email" aria-pressed="false">Recovery email</button>';
    label.parentNode.insertBefore(switcher,label);
    const help=document.createElement('p');
    help.id='forgotIdentifierHelp';
    help.className='field-help recovery-mode-help';
    input.insertAdjacentElement('afterend',help);

    function renderMode(){
      const email=recoveryMode==='email';
      label.textContent=email?'Verified recovery email':'Username';
      input.name='identifier';
      input.type=email?'email':'text';
      input.autocomplete=email?'email':'username';
      input.maxLength=email?320:64;
      input.placeholder=email?'name@example.com':'Your account username';
      help.textContent=email?'Use the verified recovery email linked to your account.':'Use your Medicine Store Assistant username.';
      switcher.querySelectorAll('button').forEach(button=>button.setAttribute('aria-pressed',String(button.dataset.recoveryMode===recoveryMode)));
    }

    switcher.addEventListener('click',event=>{
      const button=event.target.closest('button[data-recovery-mode]');
      if(!button)return;
      recoveryMode=button.dataset.recoveryMode;
      input.value='';
      renderMode();
      input.focus();
    });
    renderMode();
  }

  function show(name){
    Object.entries(panels).forEach(([key,panel])=>{panel.hidden=key!==name});
    error.textContent='';
    if(name==='signIn')username.focus();
    if(name==='request')document.querySelector('#requestDisplayName').focus();
    if(name==='forgot')document.querySelector('#forgotUsername').focus();
    if(name==='reset')document.querySelector('#resetPassword').focus();
  }

  function hashToken(prefix){
    const match=location.hash.match(new RegExp('^#'+prefix+'=([^&]+)$'));
    if(!match)return '';
    try{return decodeURIComponent(match[1])}catch{return ''}
  }

  async function completeAccessEmailVerification(){
    const token=hashToken('verify-access-email');
    if(!token)return false;
    show('verifyEmail');
    const verifyError=document.querySelector('#verifyEmailError');
    const verifySuccess=document.querySelector('#verifyEmailSuccess');
    document.querySelector('#verifyEmailCopy').textContent='Confirming the recovery email attached to your pending access request.';
    try{
      const data=await api('/dashboard/api/access-email-verifications/complete',{method:'POST',body:JSON.stringify({token})});
      verifySuccess.textContent=data.message||'Email verified. Your request still requires Owner approval.';
      document.querySelector('#verifyEmailCopy').textContent='Email verification is complete. Dashboard access remains pending until the Owner approves your request and assigns a role.';
    }catch(err){verifyError.textContent=err.message}
    history.replaceState(null,'',location.pathname);
    return true;
  }

  async function completeEmailVerification(){
    verifyEmailToken=hashToken('verify-email');
    if(!verifyEmailToken)return false;
    show('verifyEmail');
    const verifyError=document.querySelector('#verifyEmailError');
    const verifySuccess=document.querySelector('#verifyEmailSuccess');
    try{
      const data=await api('/dashboard/api/recovery-email-verifications/complete',{method:'POST',body:JSON.stringify({token:verifyEmailToken})});
      verifySuccess.textContent=data.message||'Recovery email verified.';
      document.querySelector('#verifyEmailCopy').textContent='Your verified recovery email can now receive automated password reset links.';
    }catch(err){verifyError.textContent=err.message}
    verifyEmailToken='';
    history.replaceState(null,'',location.pathname);
    return true;
  }

  async function bootstrap(){
    configureRecoveryChoice();
    if(await completeAccessEmailVerification())return;
    if(await completeEmailVerification())return;
    resetToken=hashToken('reset');
    if(resetToken){show('reset');return}
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
  document.querySelector('#verifyEmailBack')?.addEventListener('click',()=>location.assign('/dashboard/login'));

  requestForm?.addEventListener('submit',async e=>{
    e.preventDefault();const requestError=document.querySelector('#requestError');const requestSuccess=document.querySelector('#requestSuccess');const requestSubmit=document.querySelector('#requestSubmit');const requestPassword=document.querySelector('#requestPassword');const requestConfirm=document.querySelector('#requestConfirmPassword');requestError.textContent='';requestSuccess.textContent='';
    if(requestPassword.value!==requestConfirm.value){requestError.textContent='Passwords do not match.';requestConfirm.focus();return}
    requestSubmit.disabled=true;requestSubmit.textContent='Submitting…';
    try{
      const data=await api('/dashboard/api/access-requests/confirmed',{method:'POST',body:JSON.stringify({display_name:document.querySelector('#requestDisplayName').value,username:document.querySelector('#requestUsername').value,email:document.querySelector('#requestEmail').value,password:requestPassword.value,confirm_password:requestConfirm.value})});
      requestPassword.value='';requestConfirm.value='';requestSuccess.textContent=data.message||'Request submitted for Owner review.';requestSubmit.textContent='Request submitted';
    }catch(err){requestError.textContent=err.message;requestSubmit.disabled=false;requestSubmit.textContent='Submit request'}
  });

  forgotForm?.addEventListener('submit',async e=>{
    e.preventDefault();const forgotError=document.querySelector('#forgotError');const forgotSuccess=document.querySelector('#forgotSuccess');const forgotSubmit=document.querySelector('#forgotSubmit');const identifier=document.querySelector('#forgotUsername');forgotError.textContent='';forgotSuccess.textContent='';forgotSubmit.disabled=true;forgotSubmit.textContent='Sending…';
    try{const data=await api('/dashboard/api/password-recovery/request-by-identifier',{method:'POST',body:JSON.stringify({mode:recoveryMode,identifier:identifier.value})});forgotSuccess.textContent=data.message||'If the account is eligible, password recovery instructions will be sent.';forgotSubmit.textContent='Request submitted'}
    catch{forgotError.textContent='Unable to submit the recovery request.';forgotSubmit.disabled=false;forgotSubmit.textContent='Send recovery instructions'}
  });

  resetForm?.addEventListener('submit',async e=>{
    e.preventDefault();const resetError=document.querySelector('#resetError');const resetSuccess=document.querySelector('#resetSuccess');const resetSubmit=document.querySelector('#resetSubmit');resetError.textContent='';resetSuccess.textContent='';resetSubmit.disabled=true;resetSubmit.textContent='Resetting…';
    try{const data=await api('/dashboard/api/password-resets/complete',{method:'POST',body:JSON.stringify({token:resetToken,new_password:document.querySelector('#resetPassword').value})});document.querySelector('#resetPassword').value='';resetToken='';history.replaceState(null,'',location.pathname);resetSuccess.textContent=data.message||'Password reset complete. Sign in with the new password.';resetSubmit.textContent='Password reset';setTimeout(()=>show('signIn'),700)}
    catch(err){resetError.textContent=err.message;resetSubmit.disabled=false;resetSubmit.textContent='Reset password'}
  });

  bootstrap();
})();