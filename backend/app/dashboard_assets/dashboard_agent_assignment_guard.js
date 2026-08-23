(()=>{
  const root=document.querySelector('#msa');
  if(!root||root.dataset.agentAssignmentGuardReady)return;
  root.dataset.agentAssignmentGuardReady='1';

  const $=selector=>root.querySelector(selector);

  function syncAssignmentFields(){
    const runtime=$('#agentRuntimeMode');
    const provider=$('#agentProviderId');
    const savedModel=$('#agentSavedModelId');
    const providerWrap=$('#agentProviderWrap');
    const savedModelWrap=$('#agentSavedModelWrap');
    if(!runtime||!provider||!savedModel)return;

    const internal=runtime.value==='INTERNAL_MODEL';
    provider.disabled=!internal;
    savedModel.disabled=!internal;
    if(providerWrap)providerWrap.hidden=!internal;
    if(savedModelWrap)savedModelWrap.hidden=!internal;

    if(!internal){
      provider.value='';
      savedModel.value='';
    }
  }

  function install(){
    const runtime=$('#agentRuntimeMode');
    const modal=$('#agentModal');
    if(!runtime||!modal){setTimeout(install,50);return;}

    runtime.addEventListener('change',()=>setTimeout(syncAssignmentFields,0));

    const modalObserver=new MutationObserver(mutations=>{
      if(mutations.some(mutation=>mutation.type==='attributes'&&mutation.attributeName==='hidden')&&!modal.hidden){
        setTimeout(syncAssignmentFields,0);
      }
    });
    modalObserver.observe(modal,{attributes:true,attributeFilter:['hidden']});

    root.addEventListener('click',event=>{
      if(event.target.closest('#agentCreateOpen,[data-agent-action="edit"]')){
        setTimeout(syncAssignmentFields,0);
      }
    },true);

    $('#agentForm')?.addEventListener('submit',()=>{
      syncAssignmentFields();
    },true);

    syncAssignmentFields();
  }

  if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',()=>setTimeout(install,0));
  else setTimeout(install,0);
})();
