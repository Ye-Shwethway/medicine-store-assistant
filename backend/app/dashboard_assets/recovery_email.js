(()=>{
  const form=document.querySelector('#recoveryForm');
  if(!form)return;
  const email=document.querySelector('#recoveryEmail');
  const password=document.querySelector('#currentPassword');
  const submit=document.querySelector('#submit');
  const error=document.querySelector('#formError');
  const success=document.querySelector('#formSuccess');
  const stateTitle=document.querySelector('#stateTitle');
  const stateText=document.querySelector('#stateText');

  async function api(path,opts={}){
    const response=await fetch(path,{credentials:'same-origin',headers:{'Content-Type':'application/json',...(opts.headers||{})},...opts});
    let data=null;try{data=await response.json()}catch{}
    if(!response.ok){const err=new Error((data&&data.detail)||('Request failed: '+response.status));err.status=response.status;throw err}
    return data;
  }

  async function load(){
    try{
      const state=await api('/dashboard/api/account/recovery-email');
      if(state.email&&state.verified){stateTitle.textContent='Recovery email verified';stateText.textContent=state.email+' can receive automated password reset links.';email.value=state.email}
      else{stateTitle.textContent='No verified recovery email';stateText.textContent=state.delivery_configured?'Add an address below and verify it from your inbox.':'Email delivery is not configured on the server yet. Existing Owner-assisted reset remains available.'}
      submit.disabled=!state.delivery_configured;
      if(!state.delivery_configured)submit.textContent='Email delivery not configured';
    }catch(err){if(err.status===401){location.replace('/dashboard/login');return}stateTitle.textContent='Unable to read recovery status';stateText.textContent=err.message}
  }

  form.addEventListener('submit',async event=>{
    event.preventDefault();error.textContent='';success.textContent='';submit.disabled=true;submit.textContent='Sending…';
    try{
      const data=await api('/dashboard/api/account/recovery-email',{method:'POST',body:JSON.stringify({email:email.value,current_password:password.value})});
      password.value='';success.textContent='Verification email sent. Open your inbox and use the verification link before it expires.';submit.textContent='Verification sent';
      stateTitle.textContent='Verification pending';stateText.textContent='Check '+data.email+' for the verification link.';
    }catch(err){error.textContent=err.message;submit.disabled=false;submit.textContent='Send verification email'}
  });

  load();
})();