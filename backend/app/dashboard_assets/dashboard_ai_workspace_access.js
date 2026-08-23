(() => {
  "use strict";

  const SETTINGS_URL = "/dashboard/api/ai-workspace/settings";

  async function requestJson(url, options = {}) {
    const response = await fetch(url, {
      credentials: "same-origin",
      headers: { "Content-Type": "application/json", ...(options.headers || {}) },
      ...options,
    });
    let body = null;
    try { body = await response.json(); } catch (_) {}
    if (!response.ok) {
      const detail = body && body.detail;
      const message = typeof detail === "string" ? detail : "Unable to update AI Workspace access.";
      throw new Error(message);
    }
    return body || {};
  }

  function buildCard() {
    const container = document.getElementById("agentsContent");
    if (!container || document.getElementById("aiWorkspaceAccessCard")) return null;

    const card = document.createElement("article");
    card.id = "aiWorkspaceAccessCard";
    card.className = "card panel agents-panel";
    card.innerHTML = `
      <div class="users-panel-head">
        <div>
          <h2>AI Workspace access</h2>
          <p class="sub">Owner access is always available. This switch controls Chat access for all non-owner users before any provider request is made.</p>
        </div>
      </div>
      <label style="display:flex;align-items:center;gap:.75rem;margin-top:1rem;font-weight:700;">
        <input id="aiWorkspaceNonOwnerToggle" type="checkbox" style="width:1.25rem;height:1.25rem;">
        <span id="aiWorkspaceNonOwnerLabel">Loading…</span>
      </label>
      <p class="sub" id="aiWorkspaceAccessHelp" style="margin-top:.65rem;">Checking backend policy…</p>
    `;
    container.insertBefore(card, container.firstChild);
    return card;
  }

  async function load() {
    buildCard();
    const toggle = document.getElementById("aiWorkspaceNonOwnerToggle");
    const label = document.getElementById("aiWorkspaceNonOwnerLabel");
    const help = document.getElementById("aiWorkspaceAccessHelp");
    if (!toggle || !label || !help) return;
    toggle.disabled = true;
    try {
      const settings = await requestJson(SETTINGS_URL);
      toggle.checked = !!settings.non_owner_chat_enabled;
      label.textContent = toggle.checked ? "Non-owner AI Chat enabled" : "Non-owner AI Chat disabled";
      help.textContent = toggle.checked
        ? "Eligible users may use single-agent Chat according to their per-user entitlement. Multi-Agent remains Owner-only."
        : "All non-owner AI Chat requests are blocked before provider invocation. Owner access is unaffected.";
    } catch (error) {
      label.textContent = "Unable to read AI Workspace policy";
      help.textContent = error.message;
      return;
    } finally {
      toggle.disabled = false;
    }
  }

  async function save(toggle) {
    const label = document.getElementById("aiWorkspaceNonOwnerLabel");
    const help = document.getElementById("aiWorkspaceAccessHelp");
    const desired = toggle.checked;
    toggle.disabled = true;
    try {
      const settings = await requestJson(SETTINGS_URL, {
        method: "PUT",
        body: JSON.stringify({ non_owner_chat_enabled: desired }),
      });
      toggle.checked = !!settings.non_owner_chat_enabled;
      label.textContent = toggle.checked ? "Non-owner AI Chat enabled" : "Non-owner AI Chat disabled";
      help.textContent = toggle.checked
        ? "Eligible users may use single-agent Chat. Multi-Agent remains Owner-only."
        : "Non-owner Chat is blocked before provider invocation. No model tokens are consumed for denied requests.";
    } catch (error) {
      toggle.checked = !desired;
      help.textContent = error.message;
    } finally {
      toggle.disabled = false;
    }
  }

  document.addEventListener("change", (event) => {
    if (event.target && event.target.id === "aiWorkspaceNonOwnerToggle") save(event.target);
  });

  document.addEventListener("click", (event) => {
    const button = event.target.closest && event.target.closest('[data-view="agents"],#agentsRefresh');
    if (button) setTimeout(load, 0);
  });

  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", load);
  else load();
})();
