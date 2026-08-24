from pathlib import Path


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"{label}: expected 1 match, found {count}")
    return text.replace(old, new, 1)

js_path = Path('backend/app/dashboard_assets/dashboard_multi_agent_review.js')
js = js_path.read_text(encoding='utf-8')
old_click = "host.addEventListener('click',event=>{const work=event.target.closest('[data-work-id]');if(work){openWork(work.dataset.workId);return}if(event.target.id==='reviewRefresh'){load();return}if(event.target.id==='reviewSaveRoles'){saveRoles();return}if(event.target.id==='reviewRun'){runReview();return}});"
new_click = "host.addEventListener('click',event=>{const work=event.target.closest('[data-work-id]');if(work){openWork(work.dataset.workId);return}if(event.target.id==='reviewReturnRevision'){returnForRevision();return}if(event.target.id==='reviewRefresh'){load();return}if(event.target.id==='reviewSaveRoles'){saveRoles();return}if(event.target.id==='reviewRun'){runReview();return}});"
js = replace_once(js, old_click, new_click, 'delegated feedback click')
js_path.write_text(js, encoding='utf-8')

py_path = Path('backend/app/multi_agent_review_feedback.py')
py = py_path.read_text(encoding='utf-8')
old = "            revision_artifact_id = None\n            if instruction:\n                revision_version = connection.execute("
new = "            revision_artifact_id = None\n            if not instruction and external:\n                instruction = 'Use the external review as feedback for the next pass.'\n            if instruction:\n                revision_version = connection.execute("
py = replace_once(py, old, new, 'default owner feedback')
py_path.write_text(py, encoding='utf-8')
print('feedback_button_patch=pass')
