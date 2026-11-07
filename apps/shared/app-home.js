// Home button for tool pages opened inside an installed app (apps/app/ Money Made Simple, scam-checker/app/ Scam Shield).
// Each app's home screen saves itself with rememberAppHome(scope, home) under localStorage 'mms-app-home'
// as { scope URL: home URL }. When a tool page runs as an installed app (display-mode standalone), the
// home whose scope is the closest match gets a small "Home" button. iPhone home-screen apps have no back
// button, so without it people get stuck. Called from initTracking (track.js), so every tool page gets it.

export const KEY = 'mms-app-home';

/** Parse what's saved: a { scope: home } map (or a single home URL from the first version). */
export function homesFrom(saved) {
  if (!saved) return {};
  try { const m = JSON.parse(saved); if (m && typeof m === 'object') return m; } catch { /* plain URL */ }
  try { const u = new URL(saved); return { [new URL('../', u).href]: u.href }; } catch { return {}; }
}

export function appHomeUrl({ standalone, saved, here }) {
  if (!standalone) return null;
  let now;
  try { now = new URL(here); } catch { return null; }
  let best = null;
  for (const [scope, home] of Object.entries(homesFrom(saved))) {
    try {
      const s = new URL(scope); const h = new URL(home);
      if (s.origin !== now.origin || h.origin !== now.origin || !now.href.startsWith(s.href)) continue;
      if (!best || s.href.length > best.scope.length) best = { scope: s.href, home: h };
    } catch { /* skip bad entries */ }
  }
  if (!best || best.home.pathname === now.pathname) return null;
  return best.home.href;
}

export function rememberAppHome(scope, home, win = globalThis.window) {
  try {
    const m = homesFrom(win.localStorage.getItem(KEY));
    m[new URL(scope, home).href] = home;
    win.localStorage.setItem(KEY, JSON.stringify(m));
  } catch { /* private mode */ }
}

export function addAppHome(win = globalThis.window, doc = globalThis.document) {
  try {
    if (!win || !doc?.body || doc.getElementById('mms-app-home')) return false;
    const standalone = win.matchMedia?.('(display-mode: standalone)').matches || win.navigator?.standalone === true;
    let saved = null;
    try { saved = win.localStorage.getItem(KEY); } catch { /* blocked */ }
    const href = appHomeUrl({ standalone, saved, here: win.location.href });
    if (!href) return false;
    const es = (doc.documentElement.lang || '').startsWith('es');
    const a = doc.createElement('a');
    a.id = 'mms-app-home';
    a.href = href;
    a.textContent = es ? '⌂ Inicio' : '⌂ Home';
    a.setAttribute('aria-label', es ? 'Volver al inicio de la app' : 'Back to the app home screen');
    a.style.cssText = 'position:fixed;left:12px;bottom:calc(12px + env(safe-area-inset-bottom));z-index:9999;display:inline-flex;align-items:center;min-height:44px;padding:0 16px;border-radius:999px;background:#f2b134;color:#0b1d13;font:700 15px/1 system-ui,-apple-system,sans-serif;text-decoration:none;box-shadow:0 2px 10px rgba(0,0,0,.25)';
    doc.body.append(a);
    return true;
  } catch { return false; }
}
