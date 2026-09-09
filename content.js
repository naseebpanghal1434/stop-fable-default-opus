(() => {
  const LOG = "[stop-fable]";
  const MENU_WAIT_MS = 1200;
  const POLL_MS = 50;
  const MAX_ATTEMPTS = 5;

  const MODEL_BTN = 'button[data-testid="model-selector-dropdown"]';
  const MENU_ITEMS =
    '[role="menuitem"], [role="menuitemradio"], [role="option"]';
  const CHAT_INPUT =
    '[data-testid="chat-input"], [contenteditable="true"][role="textbox"]';

  let lastPath = location.pathname;
  let applied = false;
  let attempts = 0;
  let busy = false;
  let debounce = null;

  function log(...args) {
    console.debug(LOG, ...args);
  }

  function sleep(ms) {
    return new Promise((r) => setTimeout(r, ms));
  }

  function visible(el) {
    if (!el) return false;
    const r = el.getBoundingClientRect();
    return r.width > 0 && r.height > 0;
  }

  function firstLine(el) {
    return (el.textContent || "").trim().split("\n")[0].trim();
  }

  function isExistingChat(pathname) {
    return /\/chat\/[0-9a-f-]{8,}/i.test(pathname);
  }

  function shouldRun() {
    const p = location.pathname;
    if (isExistingChat(p)) return false;
    if (/^\/(login|settings|code|admin|organizations)\b/i.test(p)) return false;
    return true;
  }

  function isFable(text) {
    return /\bfable\b/i.test(text);
  }

  function isNoise(text) {
    return /effort|thinking|extended|more models|show more|learn more/i.test(
      text
    );
  }

  function opusRank(text) {
    if (!text || isNoise(text) || isFable(text)) return -1;
    if (!/\bopus\b/i.test(text)) return -1;
    const m = text.match(/opus\s*(\d+(?:\.\d+)?)/i);
    return m ? parseFloat(m[1]) : 0;
  }

  function findModelButton() {
    const byId = document.querySelector(MODEL_BTN);
    if (visible(byId)) return byId;

    const hits = [];
    for (const btn of document.querySelectorAll("button, [role='button']")) {
      const t = (btn.textContent || "").trim();
      if (!t || t.length > 80) continue;
      if (!/\b(fable|opus|sonnet|haiku)\b/i.test(t)) continue;
      const r = btn.getBoundingClientRect();
      if (r.width <= 0 || r.width > 420 || r.height <= 0 || r.height > 90) {
        continue;
      }
      hits.push({ btn, top: r.top });
    }
    if (!hits.length) return null;
    hits.sort((a, b) => b.top - a.top);
    return hits[0].btn;
  }

  function visibleMenuItems() {
    return [...document.querySelectorAll(MENU_ITEMS)].filter(visible);
  }

  function bestOpus(items) {
    let best = null;
    let bestRank = -1;
    for (const el of items) {
      const rank = opusRank(firstLine(el));
      if (rank > bestRank) {
        bestRank = rank;
        best = el;
      }
    }
    return best;
  }

  function findMoreModels(items) {
    return items.find((el) =>
      /more models|show more/i.test(firstLine(el))
    );
  }

  async function waitForItems() {
    const start = Date.now();
    while (Date.now() - start < MENU_WAIT_MS) {
      const items = visibleMenuItems();
      if (items.length) return items;
      await sleep(POLL_MS);
    }
    return [];
  }

  function closeMenu() {
    document.body.dispatchEvent(
      new KeyboardEvent("keydown", { key: "Escape", bubbles: true })
    );
  }

  function refocusInput() {
    const input = document.querySelector(CHAT_INPUT);
    if (input) input.focus();
  }

  function toast(text) {
    document.querySelectorAll(".stop-fable-toast").forEach((n) => n.remove());
    const el = document.createElement("div");
    el.className = "stop-fable-toast";
    el.textContent = text;
    el.style.cssText = [
      "position:fixed",
      "bottom:20px",
      "left:20px",
      "z-index:2147483647",
      "padding:8px 12px",
      "border-radius:8px",
      "background:#1a1a1a",
      "color:#f4ede4",
      "font:13px/1.3 system-ui,sans-serif",
      "box-shadow:0 4px 16px rgba(0,0,0,.25)",
      "pointer-events:none",
      "opacity:0",
      "transition:opacity .15s ease",
    ].join(";");
    document.documentElement.appendChild(el);
    requestAnimationFrame(() => {
      el.style.opacity = "1";
    });
    setTimeout(() => {
      el.style.opacity = "0";
      setTimeout(() => el.remove(), 200);
    }, 1800);
  }

  async function pickOpusFromOpenMenu() {
    let items = await waitForItems();
    if (!items.length) return false;

    let target = bestOpus(items);
    if (!target) {
      const more = findMoreModels(items);
      if (more) {
        more.click();
        items = await waitForItems();
        target = bestOpus(items);
      }
    }

    if (!target) {
      closeMenu();
      return false;
    }

    log("clicking", firstLine(target));
    target.click();
    return true;
  }

  async function switchToOpus(btn) {
    btn.click();
    if (await pickOpusFromOpenMenu()) return true;

    await sleep(200);
    if (!visibleMenuItems().length) btn.click();
    return pickOpusFromOpenMenu();
  }

  async function trySwitch() {
    if (location.pathname !== lastPath) {
      lastPath = location.pathname;
      applied = false;
      attempts = 0;
    }

    if (busy || applied || !shouldRun() || attempts >= MAX_ATTEMPTS) return;

    const btn = findModelButton();
    if (!btn) return;

    const current = firstLine(btn);
    if (!isFable(current)) {
      applied = true;
      log("new chat already on", current);
      return;
    }

    busy = true;
    attempts += 1;
    log("Fable on new chat — switching to Opus", { attempt: attempts, current });

    try {
      const ok = await switchToOpus(btn);
      await sleep(250);
      const after = findModelButton();
      const afterText = after ? firstLine(after) : "";
      if (ok && after && !isFable(afterText)) {
        applied = true;
        log("switched to", afterText);
        toast("Using Opus for this chat");
        refocusInput();
      } else if (attempts >= MAX_ATTEMPTS) {
        applied = true;
        log("gave up after", MAX_ATTEMPTS, "attempts");
      }
    } catch (err) {
      log("switch failed", err);
    } finally {
      busy = false;
    }
  }

  function schedule() {
    if (debounce) return;
    debounce = setTimeout(() => {
      debounce = null;
      trySwitch();
    }, 200);
  }

  const obs = new MutationObserver(schedule);
  obs.observe(document.documentElement, { childList: true, subtree: true });
  setInterval(schedule, 500);
  schedule();
})();
