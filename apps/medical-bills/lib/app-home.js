// GENERATED from apps/shared/ by tools/sync-shared.mjs. Edit the shared copy, not this one.
// Home button for tool pages opened inside the installed Money Made Simple app (apps/app/).
// The app saves its own address as localStorage 'mms-app-home'. When a tool page runs as an installed
// app (display-mode standalone) and that address is known, a small "Home" button goes back to the
// ten-tool home screen. iPhone home-screen apps have no back button, so without it people get stuck.
// Called from initTracking (track.js) so every tool page gets it with no extra wiring.

export function appHomeUrl({ standalone, saved, here }) {
  if (!standalone || !saved) return null;
  try {
    const home = new URL(saved);
    const now = new URL(here);
    if (home.origin !== now.origin || home.pathname === now.pathname) return null;
    return home.href;
  } catch { return null; }
}

export function addAppHome(win = globalThis.window, doc = globalThis.document) {
  try {
    if (!win || !doc?.body || doc.getElementById('mms-app-home')) return false;
    const standalone = win.matchMedia?.('(display-mode: standalone)').matches || win.navigator?.standalone === true;
    let saved = null;
    try { saved = win.localStorage.getItem('mms-app-home'); } catch { /* blocked */ }
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
