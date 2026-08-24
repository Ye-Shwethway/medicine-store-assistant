from pathlib import Path


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"{label}: expected 1 match, found {count}")
    return text.replace(old, new, 1)


base_path = Path("backend/app/dashboard_assets/dashboard_multi_agent_review.js")
base = base_path.read_text(encoding="utf-8")

base = replace_once(
    base,
    "  function revisionTurn(a){const payload=a.payload||{};return '<article class=\"review-chat-turn review-chat-owner\"><div class=\"review-chat-meta\"><strong>Owner</strong><span>REVISION</span></div><div class=\"review-chat-bubble\">'+esc(payload.instruction||'')+'</div></article>'}\n",
    "  function externalTurn(a){const payload=a.payload||{};const text=payload.notes||'';const verdict=payload.verdict?'<span class=\"review-verdict\">'+esc(payload.verdict)+'</span>':'';return '<article class=\"review-chat-turn review-chat-agent review-chat-external\"><div class=\"review-chat-meta\"><div><strong>'+esc(payload.external_agent_display_name||payload.external_agent_call_name||'External MCP reviewer')+'</strong><span>EXTERNAL REVIEW</span></div>'+verdict+'</div><div class=\"review-chat-bubble\">'+esc(text)+'</div><div class=\"review-chat-provenance\"><span>External MCP evidence · exact artifact v'+Number(payload.bound_artifact_version||0)+'</span></div></article>'}\n  function revisionTurn(a){const payload=a.payload||{};return '<article class=\"review-chat-turn review-chat-owner\"><div class=\"review-chat-meta\"><strong>Owner</strong><span>REVISION</span></div><div class=\"review-chat-bubble\">'+esc(payload.instruction||'')+'</div></article>'}\n",
    "external turn renderer",
)

base = replace_once(
    base,
    "    artifacts.filter(a=>a.artifact_type==='PARTICIPANT_OUTPUT').forEach(a=>turns.push(agentTurn(a,reviews)));\n    artifacts.filter(a=>a.artifact_type==='OWNER_REVISION').forEach(a=>turns.push(revisionTurn(a)));\n",
    "    artifacts.filter(a=>a.artifact_type==='PARTICIPANT_OUTPUT').forEach(a=>turns.push(agentTurn(a,reviews)));\n    artifacts.filter(a=>a.artifact_type==='EXTERNAL_REVIEW_SUBMISSION').forEach(a=>turns.push(externalTurn(a)));\n    artifacts.filter(a=>a.artifact_type==='OWNER_REVISION').forEach(a=>turns.push(revisionTurn(a)));\n",
    "persist external turns",
)

base = replace_once(
    base,
    "+(item.status==='WAITING_OWNER'?'<div class=\"review-owner-action review-chat-composer\"><label for=\"reviewRevisionInstruction\">Owner reply / return for revision</label><textarea id=\"reviewRevisionInstruction\" maxlength=\"5000\" placeholder=\"Tell the review team what needs another pass.\"></textarea><button type=\"button\" id=\"reviewReturnRevision\">Return to REVIEWING</button></div>':'')",
    "+(item.status==='WAITING_OWNER'?'<div class=\"review-owner-action review-chat-composer\"><label for=\"reviewRevisionInstruction\">Owner feedback / next review pass</label><textarea id=\"reviewRevisionInstruction\" maxlength=\"5000\" placeholder=\"Add instructions, or leave blank to send the external review back to the native team.\"></textarea><button type=\"button\" id=\"reviewReturnRevision\">Send feedback to review team</button></div>':'')",
    "feedback composer copy",
)

old_return = """  async function returnForRevision(){
    if(busy||!currentWorkItemId)return;
    const instruction=host.querySelector('#reviewRevisionInstruction')?.value.trim();
    if(!instruction){setStatus('Enter a revision instruction first.','error');return}
    setBusy(true);setStatus('Returning Work Item to REVIEWING…');
    try{const item=await api('/dashboard/api/ai-workspace/multi-agent/work-items/'+encodeURIComponent(currentWorkItemId)+'/return-for-revision',{method:'POST',body:JSON.stringify({instruction})});renderWorkDetail(item);await loadWorkItemsSafe();setStatus('Returned to REVIEWING. The Owner revision instruction is persisted.','success')}catch(err){setStatus(err.message,'error')}finally{setBusy(false)}
  }
"""
new_return = """  async function returnForRevision(){
    if(busy||!currentWorkItemId)return;
    const instruction=host.querySelector('#reviewRevisionInstruction')?.value.trim()||'';
    const hasExternal=Boolean(host.querySelector('#reviewWorkDetail .review-chat-external'));
    if(!instruction&&!hasExternal){setStatus('Enter Owner feedback or request an external review first.','error');return}
    setBusy(true);setStatus('Starting a new native feedback pass…');
    try{const item=await api('/dashboard/api/ai-workspace/multi-agent/work-items/'+encodeURIComponent(currentWorkItemId)+'/feedback-pass',{method:'POST',body:JSON.stringify({instruction:instruction||null})});renderWorkDetail(item);await loadWorkItemsSafe();setStatus('Feedback sent. Native participants are running a new pass with the persisted review evidence.','success')}catch(err){setStatus(err.message,'error')}finally{setBusy(false)}
  }
"""
base = replace_once(base, old_return, new_return, "feedback pass action")
base_path.write_text(base, encoding="utf-8")

live_path = Path("backend/app/dashboard_assets/dashboard_multi_agent_live_export.js")
live = live_path.read_text(encoding="utf-8")
live = replace_once(
    live,
    "const status=detail.querySelector('.review-status')?.textContent?.trim()||'';const needsResume=status==='WAITING_EXTERNAL';const needsHydrate=hydrateWorkId!==id;",
    "const status=detail.querySelector('.review-status')?.textContent?.trim()||'';const needsResume=status==='WAITING_EXTERNAL'||status==='REVIEWING';const needsHydrate=hydrateWorkId!==id;",
    "resume reviewing polling",
)
live = replace_once(
    live,
    "if(item.status==='WAITING_EXTERNAL'){\n        liveWorkId=id;liveLastSignature=signature(item);if(livePollTimer)clearTimeout(livePollTimer);livePollTimer=setTimeout(pollLive,1000);\n      }",
    "if(item.status==='WAITING_EXTERNAL'||item.status==='REVIEWING'){\n        liveWorkId=id;liveLastSignature=signature(item);if(livePollTimer)clearTimeout(livePollTimer);livePollTimer=setTimeout(pollLive,1000);\n      }",
    "resume reviewing timer",
)
live = replace_once(
    live,
    "if(event.target.closest('[data-ai-conversation],#aiNewConversation,#aiWorkspaceNav,[data-ai-tab],#aiMultiMode .review-work-item')){const card=event.target.closest('#aiMultiMode .review-work-item');if(card&&card.dataset.workId!==hydrateWorkId)hydrateWorkId=null;scheduleReconcile()}",
    "if(event.target.closest('[data-ai-conversation],#aiNewConversation,#aiWorkspaceNav,[data-ai-tab],#aiMultiMode .review-work-item')){const card=event.target.closest('#aiMultiMode .review-work-item');if(card)hydrateWorkId=null;scheduleReconcile()}",
    "same-card rehydrate",
)
live_path.write_text(live, encoding="utf-8")

print("federated_feedback_loop_patch=pass")
