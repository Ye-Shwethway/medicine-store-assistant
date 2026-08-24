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
  </main>
`);

await page.evaluate(() => {
  const now = new Date().toISOString();
  const baseArtifacts = [
    { artifact_id: 'owner-1', artifact_type: 'OWNER_TASK', version: 1, created_at: now, payload: { task: 'Inspect current evidence.' } },
    { artifact_id: 'native-1', artifact_type: 'PARTICIPANT_OUTPUT', version: 1, created_at: now, payload: { role: 'REVIEWER', response: 'Native review complete.', provenance: { agent_display_name: 'Reviewer', selected_provider_name: 'Test', selected_model_name: 'Model' } } },
    { artifact_id: 'external-1', artifact_type: 'EXTERNAL_REVIEW_SUBMISSION', version: 1, created_at: now, payload: { notes: 'External evidence review.', verdict: 'COMMENT', external_agent_display_name: 'IANEO', bound_artifact_version: 2 } },
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
    if (url === '/dashboard/api/ai-workspace/multi-agent/work-items/work-1/feedback-pass' && method === 'POST') {
      const ownerRevision = {
        artifact_id: 'owner-feedback-1', artifact_type: 'OWNER_REVISION', version: 1, created_at: new Date().toISOString(),
        payload: { instruction: 'Use the external review as feedback for the next pass.', feedback_pass: true },
      };
      window.__work = { ...window.__work, status: 'REVIEWING', artifacts: [...window.__work.artifacts, ownerRevision], updated_at: new Date().toISOString() };
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

// The button lives in replaceable DOM. Delegated event wiring must survive the live renderer.
const feedback = page.getByRole('button', { name: 'Send feedback to review team' });
await feedback.waitFor({ state: 'visible' });
await feedback.click();
await page.waitForFunction(() => window.__requests.some(r => r.url.endsWith('/feedback-pass') && r.method === 'POST'));

const feedbackRequest = await page.evaluate(() => window.__requests.find(r => r.url.endsWith('/feedback-pass') && r.method === 'POST'));
assert.deepEqual(JSON.parse(feedbackRequest.body), { instruction: null });
await page.getByText('Use the external review as feedback for the next pass.').waitFor({ state: 'visible' });

await browser.close();
console.log('multi_agent_feedback_browser_smoke=pass');
