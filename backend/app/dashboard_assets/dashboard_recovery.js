(()=>{
  const root=document.querySelector('#msa');
  if(!root)return;
  const $=s=>root.querySelector(s);
  const form=$('#recoveryEmailForm');
  if(!form)return;

  const emailInput=$('#accountRecoveryEmail');
  const passwordInput=$('#recoveryEmailCurrentPassword');
  const statusEl=$('#recoveryEmailStatus');
  const helpEl=$('#recoveryEmailHelp');
  const errorEl=$('#recoveryEmailError');
  const successEl=$('#recoveryEmailSuccess');
  const submit=$('#recoveryEmailSubmit');

  async function api(path,opts={}){
    const response=await fetch(path,{credentials:'same-origin',headers:{'Content-Type':'application/json',...(opts.headers||{})},...opts});
    let data=null;try{data=await response.json()}catch{}
    if(!response.ok){const err=new Error((data&&data.detail)||('Request failed: '+response.status));err.status=response.status;throw err}
    return data;
  }

  function ensurePasswordConfirmation(){
    const passwordForm=$('#passwordChangeForm');
    const newPassword=$('#accountNewPassword');
    if(!passwordForm||!newPassword||$('#accountConfirmPassword'))return;
    const oldHelp=newPassword.nextElementSibling;
    const label=document.createElement('label');
    label.htmlFor='accountConfirmPassword';
    label.textContent='Confirm new password';
    const confirm=document.createElement('input');
    confirm.id='accountConfirmPassword';
    confirm.name='confirm_password';
    confirm.type='password';
    confirm.autocomplete='new-password';
    confirm.minLength=10;
    confirm.maxLength=256;
    confirm.required=true;
    const help=document.createElement('p');
    help.className='field-help';
    help.textContent='Re-enter the new password to prevent accidental lockout.';
    if(oldHelp){oldHelp.insertAdjacentElement('afterend',label)}else{newPassword.insertAdjacentElement('afterend',label)}
    label.insertAdjacentElement('afterend',confirm);
    confirm.insertAdjacentElement('afterend',help);
  }

  async function submitConfirmedPasswordChange(event){
    const passwordForm=event.target.closest('#passwordChangeForm');
    if(!passwordForm)return;
    event.preventDefault();
    event.stopImmediatePropagation();
    const current=$('#accountCurrentPassword');
    const next=$('#accountNewPassword');
    const confirm=$('#accountConfirmPassword');
    const error=$('#passwordChangeError');
    const button=$('#passwordChangeSubmit');
    error.textContent='';
    if(!confirm||next.value!==confirm.value){
      error.textContent='New passwords do not match.';
      confirm?.focus();
      return;
    }
    button.disabled=true;
    button.textContent='Changing password…';
    try{
      await api('/dashboard/api/account/password-confirmed',{method:'POST',body:JSON.stringify({current_password:current.value,new_password:next.value,confirm_password:confirm.value})});
      current.value='';next.value='';confirm.value='';
      location.replace('/dashboard/login');
    }catch(err){
      error.textContent=err.message;
      button.disabled=false;
      button.textContent='Change password';
    }
  }

  function renderState(data){
    const email=data.email||'';
    emailInput.value=email;
    if(data.verified&&email){
      statusEl.textContent='Verified';
      statusEl.className='state-pill active';
      helpEl.textContent='Automated password recovery is active for '+email+'. Enter a new address below to change it; the current verified address remains active until the new one is verified.';
      submit.textContent='Send verification to new email';
    }else if(email){
      statusEl.textContent='Unverified';
      statusEl.className='state-pill pending';
      helpEl.textContent='This address is not verified yet. Send a new verification email if needed.';
      submit.textContent='Send verification email';
    }else{
      statusEl.textContent='Not set';
      statusEl.className='state-pill pending';
      helpEl.textContent='Add a verified email so you can recover this account without Owner assistance.';
      submit.textContent='Send verification email';
    }
    if(!data.delivery_configured){
      helpEl.textContent='Email delivery is not configured on the server yet.';
      submit.disabled=true;
    }
  }

  async function load(){
    errorEl.textContent='';successEl.textContent='';
    try{renderState(await api('/dashboard/api/account/recovery-email'))}
    catch(err){if(err.status===401)return;errorEl.textContent=err.message}
  }

  form.addEventListener('submit',async event=>{
    event.preventDefault();
    errorEl.textContent='';successEl.textContent='';submit.disabled=true;const original=submit.textContent;submit.textContent='Sending…';
    try{
      const data=await api('/dashboard/api/account/recovery-email',{method:'POST',body:JSON.stringify({email:emailInput.value,current_password:passwordInput.value})});
      passwordInput.value='';
      successEl.textContent='Verification email sent to '+data.email+'. Open that inbox and use the verification link within 30 minutes.';
      submit.textContent='Verification sent';
      setTimeout(()=>{submit.disabled=false;submit.textContent=original},1200);
    }catch(err){errorEl.textContent=err.message;submit.disabled=false;submit.textContent=original}
  });

  root.addEventListener('submit',submitConfirmedPasswordChange,true);
  root.addEventListener('click',event=>{
    const button=event.target.closest('.nav-btn[data-view="account"]');
    if(button)setTimeout(load,0);
  });

  ensurePasswordConfirmation();
  load();
})();