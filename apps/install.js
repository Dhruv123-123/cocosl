// Hub page: offline support and the add-to-home-screen prompt.
// Chrome, Edge and Android fire `beforeinstallprompt`; we hold it and show our own banner.
// iPhone and iPad Safari never fire it, so there we explain Share > Add to Home Screen instead.
// "Not now" hides the banner for 30 days. Already installed (standalone): no banner.
const KEY = 'tools-install-dismissed';
const DAYS = 30;
const $ = (s) => document.querySelector(s);

export function shouldOffer({ standalone, dismissedAt, now = Date.now() }) {
  if (standalone) return false;
  const t = Number(dismissedAt);
  return !(t && now - t < DAYS * 86400000);
}

export function isIos(ua = '', maxTouchPoints = 0) {
  return /iPhone|iPad|iPod/.test(ua) || (/Macintosh/.test(ua) && maxTouchPoints > 1);
}

function track(name, props) { try { window.plausible?.(name, { props: { app: 'hub', ...props } }); } catch { /* analytics off */ } }

if (typeof window !== 'undefined' && typeof document !== 'undefined') {
  const get = () => { try { return localStorage.getItem(KEY); } catch { return null; } };
  const set = (v) => { try { localStorage.setItem(KEY, v); } catch { /* private mode */ } };
  const standalone = window.matchMedia?.('(display-mode: standalone)').matches || navigator.standalone === true;
  const banner = $('#install');
  let deferred = null;

  if ('serviceWorker' in navigator && (location.protocol === 'https:' || ['localhost', '127.0.0.1'].includes(location.hostname))) {
    navigator.serviceWorker.register('sw.js').catch(() => {});
  }

  const show = (text) => {
    if (!banner || !shouldOffer({ standalone, dismissedAt: get() })) return;
    if (text) $('#install-text').innerHTML = text;
    banner.hidden = false;
  };

  window.addEventListener('beforeinstallprompt', (e) => {
    e.preventDefault();
    deferred = e;
    show();
  });
  if (isIos(navigator.userAgent, navigator.maxTouchPoints) && !standalone) {
    show('Add these tools to your home screen: tap <b>Share</b> and then <b>Add to Home Screen</b>. The tools you\'ve used work offline.');
    const b = $('#install-btn'); if (b) b.hidden = true;
  }
  $('#install-btn')?.addEventListener('click', async () => {
    if (!deferred) return;
    deferred.prompt();
    const choice = await deferred.userChoice.catch(() => ({ outcome: 'dismissed' }));
    track('Install Prompt', { outcome: choice.outcome });
    deferred = null;
    banner.hidden = true;
  });
  $('#install-later')?.addEventListener('click', () => { set(String(Date.now())); banner.hidden = true; });
  window.addEventListener('appinstalled', () => { banner.hidden = true; track('App Installed', {}); });
}
