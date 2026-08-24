from pathlib import Path

path = Path('backend/app/dashboard_assets/dashboard_multi_agent_review.js')
text = path.read_text(encoding='utf-8')
old = "list.innerHTML=workItems.map(item=>'<button type=\"button\" class=\"review-work-item'+(item.work_item_id===currentWorkItemId?' active':'')+'\" data-work-id=\"'+esc(item.work_item_id)+'\">"
new = "list.innerHTML=workItems.map(item=>'<button type=\"button\" class=\"review-work-item'+(item.work_item_id===currentWorkItemId?' active':'')+'\" data-work-id=\"'+esc(item.work_item_id)+'\" aria-label=\"Open review '+esc(item.title)+'\">"
if text.count(old) != 1:
    raise SystemExit(f'work card anchor count={text.count(old)}')
path.write_text(text.replace(old, new, 1), encoding='utf-8')

test_path = Path('tests/web/multi_agent_feedback_smoke.mjs')
test = test_path.read_text(encoding='utf-8')
test = test.replace("const workCard = page.getByRole('button', { name: /Reliability acceptance/ });", "const workCard = page.getByRole('button', { name: 'Open review Reliability acceptance' });")
test_path.write_text(test, encoding='utf-8')
print('web_hardening_followup=pass')
