from pathlib import Path


def replace_exact(path: str, old: str, new: str) -> None:
    p = Path(path)
    text = p.read_text()
    if text.count(old) != 1:
        raise SystemExit(f"{path}: expected one exact match, found {text.count(old)}")
    p.write_text(text.replace(old, new, 1))


replace_exact(
    "backend/app/multi_agent_review.py",
    '''def _set_status(connection: Any, work_item_id: str, target: str) -> None:\n    connection.execute(\n        text(\n            """\n            UPDATE workflow_work_items\n            SET status=:target, updated_at=now(),\n                completed_at=CASE WHEN :target IN ('COMMITTED','CANCELLED') THEN now() ELSE completed_at END\n            WHERE work_item_id=CAST(:work_item_id AS uuid)\n            """\n        ),\n        {"work_item_id": work_item_id, "target": target},\n    )\n''',
    '''def _set_status(connection: Any, work_item_id: str, target: str) -> None:\n    terminal = target in {"COMMITTED", "CANCELLED"}\n    statement = (\n        """\n        UPDATE workflow_work_items\n        SET status=CAST(:target AS varchar), updated_at=now(), completed_at=now()\n        WHERE work_item_id=CAST(:work_item_id AS uuid)\n        """\n        if terminal\n        else """\n        UPDATE workflow_work_items\n        SET status=CAST(:target AS varchar), updated_at=now()\n        WHERE work_item_id=CAST(:work_item_id AS uuid)\n        """\n    )\n    connection.execute(\n        text(statement),\n        {"work_item_id": work_item_id, "target": target},\n    )\n''',
)

js = Path("backend/app/dashboard_assets/dashboard_multi_agent_review.js")
text = js.read_text()
replacements = [
    ("  let busy=false;\n", "  let busy=false;\n  let rolesSaved=false;\n"),
    (
        '''  function setBusy(value){\n    busy=value;\n    host.querySelectorAll('button,input,select,textarea').forEach(el=>{if(!el.dataset.alwaysEnabled)el.disabled=value});\n    const run=host.querySelector('#reviewRun');if(run)run.textContent=value?'Review running…':'Run native review';\n  }\n''',
        '''  function syncRoleSaveState(){\n    const save=host.querySelector('#reviewSaveRoles');if(!save)return;\n    const hasRows=host.querySelectorAll('[data-role-agent]').length>0;\n    save.textContent=rolesSaved?'Saved':'Save roles';\n    save.disabled=busy||!hasRows||rolesSaved;\n  }\n  function setBusy(value){\n    busy=value;\n    host.querySelectorAll('button,input,select,textarea').forEach(el=>{if(!el.dataset.alwaysEnabled)el.disabled=value});\n    const run=host.querySelector('#reviewRun');if(run)run.textContent=value?'Review running…':'Run native review';\n    syncRoleSaveState();\n  }\n''',
    ),
    (
        "    if(!selectedSession){meta.innerHTML='';rows.innerHTML='<div class=\"empty-copy\">Choose a REVIEW preset.</div>';save.disabled=true;return}\n",
        "    if(!selectedSession){rolesSaved=false;meta.innerHTML='';rows.innerHTML='<div class=\"empty-copy\">Choose a REVIEW preset.</div>';syncRoleSaveState();return}\n",
    ),
    ("    save.disabled=!participants.length;\n", "    syncRoleSaveState();\n"),
    (
        '''  async function selectSession(id){\n    selectedSession=sessions.find(s=>s.session_id===id)||null;roleState=[];renderRoles();if(!selectedSession)return;\n    try{const data=await api('/dashboard/api/ai-workspace/multi-agent/sessions/'+encodeURIComponent(id)+'/roles');roleState=data.roles||[];renderRoles()}catch(err){if(err.status!==404)setStatus(err.message,'error')}\n  }\n''',
        '''  async function selectSession(id){\n    selectedSession=sessions.find(s=>s.session_id===id)||null;roleState=[];rolesSaved=false;renderRoles();if(!selectedSession)return;\n    try{\n      const data=await api('/dashboard/api/ai-workspace/multi-agent/sessions/'+encodeURIComponent(id)+'/roles');\n      roleState=data.roles||[];\n      const participantCount=(selectedSession.participants||[]).filter(p=>p.is_active!==false).length;\n      rolesSaved=participantCount>0&&roleState.length===participantCount;\n      renderRoles();\n    }catch(err){if(err.status!==404)setStatus(err.message,'error')}\n  }\n''',
    ),
    (
        "    try{await api('/dashboard/api/ai-workspace/multi-agent/sessions/'+encodeURIComponent(selectedSession.session_id)+'/roles',{method:'PUT',body:JSON.stringify({assignments})});const data=await api('/dashboard/api/ai-workspace/multi-agent/sessions/'+encodeURIComponent(selectedSession.session_id)+'/roles');roleState=data.roles||[];renderRoles();setStatus('Roles saved. These labels do not grant authority.','success')}catch(err){setStatus(err.message,'error')}finally{setBusy(false)}\n",
        "    try{await api('/dashboard/api/ai-workspace/multi-agent/sessions/'+encodeURIComponent(selectedSession.session_id)+'/roles',{method:'PUT',body:JSON.stringify({assignments})});const data=await api('/dashboard/api/ai-workspace/multi-agent/sessions/'+encodeURIComponent(selectedSession.session_id)+'/roles');roleState=data.roles||[];rolesSaved=true;renderRoles();setStatus('Roles saved. These labels do not grant authority.','success')}catch(err){setStatus(err.message,'error')}finally{setBusy(false)}\n",
    ),
    (
        "  host.addEventListener('change',event=>{if(event.target.id==='reviewSessionSelect')selectSession(event.target.value);if(event.target.id==='reviewEvidenceConversation')loadEvidenceFiles(event.target.value)});\n",
        "  host.addEventListener('change',event=>{if(event.target.id==='reviewSessionSelect')selectSession(event.target.value);if(event.target.id==='reviewEvidenceConversation')loadEvidenceFiles(event.target.value);if(event.target.matches('[data-role-select],[data-role-label]')){rolesSaved=false;syncRoleSaveState()}});\n  host.addEventListener('input',event=>{if(event.target.matches('[data-role-label]')){rolesSaved=false;syncRoleSaveState()}});\n",
    ),
]
for old, new in replacements:
    if text.count(old) != 1:
        raise SystemExit(f"review JS exact anchor mismatch: {old[:80]!r}; matches={text.count(old)}")
    text = text.replace(old, new, 1)
js.write_text(text)

replace_exact(
    "backend/app/main.py",
    'MULTI_AGENT_REVIEW_ASSET_VERSION = "f72d48-review-ui-1"',
    'MULTI_AGENT_REVIEW_ASSET_VERSION = "f72d48-review-ui-2"',
)

trigger = Path("docs/checkpoints/d4-8-root-fix-trigger.txt")
if trigger.exists():
    trigger.unlink()

print("d4_8_code_patch=pass")
