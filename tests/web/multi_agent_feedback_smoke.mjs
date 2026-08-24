import assert from 'node:assert/strict';
import path from 'node:path';
import { chromium } from 'playwright';

const root = process.cwd();
const baseScript = path.join(root, 'backend/app/dashboard_assets/dashboard_multi_agent_review.js');
const liveScript = path.join(root, 'backend/app/dashboard_assets/dashboard_multi_agent_live_export.js');

const browser = await chromium.launch({ headless: true });
const page = await browser.newPage({ viewport: { width: 390, height: 844 } });

await page.setContent(`
  <main id="msa">
    <button id="aiMultiTab" type="button">Multi-Agent</button>
    <div id="aiMultiMode"></div>
    <div class="ai-chat-head"></div>
    <div class="ai-conversation-item active"><button data-ai-conversation="chat-1">Chat one</button></div>
    <form id="aiChatForm"><textarea id="aiMessageInput"></textarea><button id="aiSend" type="submit">Send</button></form>
  </main>
`);

await page.evaluate(() => {
  const now = new Date().toISOString();
  const baseArtifacts = [
    { artifact_id: 'owner-1', artifact_type: 'OWNER_TASK', version: 1, created_at: now, payload: { task: 'Inspect current evidence.' } },
    { artifact_id: 'native-1', artifact_type: 'PARTICIPANT_OUTPUT', version: 1, created_at: now, payload: { role: 'REVIEWER', response: 'Native review complete.', provenance: { agent_display_name: 'Reviewer', selected_provider_name: 'Test', selected_model_name: 'Model' } } },
    { artifact_id: 'external-1', artifact_type: 'EXTERNAL_REVIEW_SUBMISSION', version: 1, created_at: now, payload: { notes: 'External evidence review.', verdict: 'COMMENT', external_agent_display_name: 'IANEO', bound_artifact_id: 'native-1', bound_artifact_version: 1 } },
  ];
  window.__requests = [];
  window.__work = {
    work_item_id: 'work-1', title: 'Reliability acceptance', objective: 'Inspect current evidence.', status: 'WAITING_OWNER', session_id: 'session-1', session_name: 'Review', updated_at: now,
    artifacts: baseArtifacts, reviews: [], events: [], attention: [],
  };

  const response = (data, status = 200) => new Response(JSON.stringify(data), { status, headers: { 'Content-Type': 'application/json' } });
  window.fetch = async (input, options = {}) => {
    const url = typeof input === 'string' ? input : input.url;
    const method = options.method || 'GET';
    window.__requests.push({ url, method, body: options.body || null });

    if (url === '/dashboard/api/agents/sessions/list') return response({ items: [] });
    if (url === '/dashboard/api/ai-workspace/conversation-cards') return response({ items: [] });
    if (url === '/dashboard/api/ai-workspace/multi-agent/work-items') {
      return response({ degraded: false, items: [{ work_item_id: 'work-1', title: 'Reliability acceptance', status: window.__work.status, session_name: 'Review', updated_at: window.__work.updated_at }] });
    }
    if (url === '/dashboard/api/ai-workspace/multi-agent/work-items/work-1' && method === 'GET') return response(window.__work);
    if (url === '/dashboard/api/ai-workspace/multi-agent/work-items/work-1/owner-messages' && method === 'POST') {
      const body = JSON.parse(options.body || '{}');
      const ownerMessage = { artifact_id: 'owner-message-1', artifact_type: 'OWNER_MESSAGE', version: 1, created_at: new Date().toISOString(), payload: { message: body.message, staged_for_review: true } };
      window.__work = { ...window.__work, artifacts: [...window.__work.artifacts, ownerMessage], updated_at: new Date().toISOString() };
      return response(window.__work);
    }
    if (url === '/dashboard/api/ai-workspace/multi-agent/work-items/work-1/feedback-pass' && method === 'POST') {
      const pendingOwnerIds = window.__work.artifacts.filter(a => a.artifact_type === 'OWNER_MESSAGE').map(a => a.artifact_id);
      const pendingExternalIds = window.__work.events.some(e => e.event_type === 'OWNER_STARTED_FEEDBACK_PASS') ? [] : ['external-1'];
      const event = { event_type: 'OWNER_STARTED_FEEDBACK_PASS', actor_type: 'OWNER', created_at: new Date().toISOString(), payload: { owner_message_artifact_ids: pendingOwnerIds, external_review_artifact_ids: pendingExternalIds } };
      window.__work = { ...window.__work, status: 'REVIEWING', events: [...window.__work.events, event], updated_at: new Date().toISOString() };
      setTimeout(() => {
        const nextVersion = window.__work.artifacts.filter(a => a.artifact_type === 'PARTICIPANT_OUTPUT').length + 1;
        const participant = { artifact_id: 'native-' + nextVersion, artifact_type: 'PARTICIPANT_OUTPUT', version: nextVersion, created_at: new Date().toISOString(), payload: { role: 'REVIEWER', response: 'Native feedback pass complete.', provenance: { agent_display_name: 'Reviewer', selected_provider_name: 'Test', selected_model_name: 'Model' } } };
        window.__work = { ...window.__work, status: 'WAITING_OWNER', artifacts: [...window.__work.artifacts, participant], updated_at: new Date().toISOString() };
      }, 100);
      return response(window.__work, 202);
    }
    return response({ detail: `Unhandled test request: ${method} ${url}` }, 500);
  };
});

await page.addScriptTag({ path: baseScript });
await page.addScriptTag({ path: liveScript });
await page.getByRole('button', { name: 'Multi-Agent' }).click();

const workCard = page.getByRole('button', { name: 'Open review Reliability acceptance' });
await workCard.waitFor({ state: 'visible' });
await workCard.click();
await page.waitForFunction(() => document.querySelector('#aiMultiMode')?.classList.contains('review-chat-open'));
await page.getByText('External evidence review.').waitFor({ state: 'visible' });

// Navigation must not trap the mobile user, and reopen must restore persisted external review.
await page.getByRole('button', { name: /Back to reviews/ }).click();
assert.equal(await page.locator('#aiMultiMode').evaluate(el => el.classList.contains('review-chat-open')), false);
await workCard.click();
await page.getByText('External evidence review.').waitFor({ state: 'visible' });

// Existing external feedback is actionable exactly once.
const reviewSend = page.getByRole('button', { name: 'Send review' });
await reviewSend.waitFor({ state: 'visible' });
assert.equal(await reviewSend.isEnabled(), true);
await reviewSend.click();
await page.waitForFunction(() => window.__requests.some(r => r.url.endsWith('/feedback-pass') && r.method === 'POST'));
const feedbackRequest = await page.evaluate(() => window.__requests.find(r => r.url.endsWith('/feedback-pass') && r.method === 'POST'));
assert.deepEqual(JSON.parse(feedbackRequest.body), { instruction: null });

// After the pass settles, consumed external feedback must stay disabled on rehydration.
await page.waitForFunction(() => window.__work.status === 'WAITING_OWNER');
await page.waitForTimeout(1200);
const settled = page.getByRole('button', { name: 'Review sent' });
await settled.waitFor({ state: 'visible' });
assert.equal(await settled.isDisabled(), true);
await page.getByRole('button', { name: /Back to reviews/ }).click();
await workCard.click();
await settled.waitFor({ state: 'visible' });
assert.equal(await settled.isDisabled(), true);

// Ordinary Owner Send persists a message only and must not itself start another feedback pass.
const feedbackCallsBeforeMessage = await page.evaluate(() => window.__requests.filter(r => r.url.endsWith('/feedback-pass')).length);
await page.getByLabel('Owner message').fill('Please focus on rows 312 and 648.');
await page.getByRole('button', { name: 'Send Owner message' }).click();
await page.getByText('Please focus on rows 312 and 648.').waitFor({ state: 'visible' });
const feedbackCallsAfterMessage = await page.evaluate(() => window.__requests.filter(r => r.url.endsWith('/feedback-pass')).length);
assert.equal(feedbackCallsAfterMessage, feedbackCallsBeforeMessage);
assert.equal(await page.getByRole('button', { name: 'Send review' }).isEnabled(), true);

// Composer-side exports reuse the exact same endpoints as the top actions.
const reviewDocxHrefs = await page.locator('a[href$="/export?format=docx"]').evaluateAll(nodes => nodes.map(n => n.getAttribute('href')));
assert.ok(reviewDocxHrefs.filter(href => href === '/dashboard/api/ai-workspace/multi-agent/work-items/work-1/export?format=docx').length >= 2);
const singleDocx = page.locator('#aiChatForm .ai-chat-export-composer a', { hasText: 'DOCX' });
await singleDocx.waitFor({ state: 'visible' });
assert.equal(await singleDocx.getAttribute('href'), '/dashboard/api/ai-workspace/conversations/chat-1/export?format=docx');
assert.equal(await page.locator('#aiSend').getAttribute('aria-label'), 'Send message');

await browser.close();
console.log('multi_agent_feedback_browser_smoke=pass');