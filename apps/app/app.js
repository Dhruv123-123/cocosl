// Money Made Simple app shell (app/index.html): ten tools behind one home screen.
// - Asks the site's service worker to save every file the ten tools need (app/precache.json) so they open offline.
//   The site's service worker (../sw.js, scope ../) serves them from any cache when there's no signal.
// - Remembers this page's address so tool pages opened from the installed app show a Home button
//   (shared/app-home.js); iPhone apps have no back button.
// - No account and no data leaves the device: tools keep what you type in this browser.
import { TOOLS, urlFor } from './tools.js';
import { rememberAppHome } from '../budget/lib/app-home.js';

const $ = (s) => document.querySelector(s);
const esc = (s) => String(s).replace(/[&<>"']/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' })[c]);
const store = { get: (k) => { try { return localStorage.getItem(k); } catch { return null; } }, set: (k, v) => { try { localStorage.setItem(k, v); } catch { /* private mode */ } } };
const CACHE_PREFIX = 'mms-app-';
const okOrigin = location.protocol === 'https:' || ['localhost', '127.0.0.1'].includes(location.hostname);

const T = {
  en: { lede: 'Ten free money tools on one home screen. Tap one to start.', other: 'Español', otherLang: 'es', getting: 'Getting the tools ready for offline…', ready: 'Ready offline: all 10 tools work with no signal.', partial: (n, t) => `Saved ${n} of ${t} files for offline. Open the app again with a signal to finish.`, noSw: 'This browser can\'t save the tools for offline, but they all work online.', install: 'Add Money Made Simple to your home screen. It opens like an app and works with no signal.', ios: 'To add it to your home screen: tap Share, then Add to Home Screen.', btn: 'Add to home screen', promises: ['No account, no sign-up', 'Works offline once it\'s saved', 'What you type stays on this device'], foot: '<a href="../">All free tools</a> · Not financial advice. Made by Money Made Simple.' },
  es: { lede: 'Diez herramientas de dinero gratis en una sola pantalla. Toca una para empezar.', other: 'English', otherLang: 'en', getting: 'Preparando las herramientas para usarlas sin internet…', ready: 'Lista sin internet: las 10 herramientas funcionan sin señal.', partial: (n, t) => `Se guardaron ${n} de ${t} archivos. Abre la app otra vez con señal para terminar.`, noSw: 'Este navegador no puede guardar las herramientas sin internet, pero todas funcionan en línea.', install: 'Agrega Money Made Simple a tu pantalla de inicio. Se abre como app y funciona sin señal.', ios: 'Para agregarla a tu pantalla de inicio: toca Compartir y luego Agregar a inicio.', btn: 'Agregar a inicio', promises: ['Sin cuenta y sin registro', 'Funciona sin internet una vez guardada', 'Lo que escribes se queda en este aparato'], foot: '<a href="../es/">Todas las herramientas</a> · No es asesoría financiera. Hecho por Dinero Simple.' },
};

const fromUrl = new URLSearchParams(location.search).get('lang');
let lang = ['en', 'es'].includes(fromUrl) ? fromUrl : store.get('mms-app-lang') || (navigator.language?.toLowerCase().startsWith('es') ? 'es' : 'en');
let precache = null;

function render() {
  const t = T[lang];
  document.documentElement.lang = lang;
  $('#lede').textContent = t.lede;
  $('#lang').textContent = t.other;
  $('#lang').lang = t.otherLang;
  $('#install-btn').textContent = t.btn;
  $('#promises').innerHTML = t.promises.map((p) => `<li>${esc(p)}</li>`).join('');
  $('#foot').innerHTML = t.foot;
  $('#tools').innerHTML = TOOLS.map((tool) => `<li><a class="tile" href="${esc(urlFor(tool, lang))}" data-tool="${tool.id}"><span class="ico" aria-hidden="true">${tool.icon}</span><b>${esc(tool.name[lang])}</b><small>${esc(tool.blurb[lang])}</small></a></li>`).join('');
}

function status(text, ready = false) {
  $('#status-text').textContent = text;
  $('#status').classList.toggle('ready', ready);
}

/** Ask the site's service worker to save every file for the current language; it drops older versions. */
async function saveOffline() {
  const sw = navigator.serviceWorker;
  if (!sw || !okOrigin || !precache) { status(T[lang].noSw); return; }
  status(T[lang].getting);
  const reg = await sw.ready;
  const base = new URL('../', location.href);
  const files = [...precache[lang], 'app/precache.json'].map((p) => new URL(p, base).href);
  const { saved, total } = await new Promise((resolve) => {
    const ch = new MessageChannel();
    ch.port1.onmessage = (e) => resolve(e.data || { saved: 0, total: files.length });
    reg.active.postMessage({ type: 'mms-app-precache', cache: CACHE_PREFIX + precache.version, files }, [ch.port2]);
  });
  if (saved === total) status(T[lang].ready, true); else status(T[lang].partial(saved, total));
}

$('#lang').addEventListener('click', () => {
  lang = lang === 'en' ? 'es' : 'en';
  store.set('mms-app-lang', lang);
  render();
  saveOffline();
});

// Installing: Chrome, Edge and Android fire beforeinstallprompt; iPhone needs Share > Add to Home Screen.
const standalone = window.matchMedia?.('(display-mode: standalone)').matches || navigator.standalone === true;
let deferred = null;
window.addEventListener('beforeinstallprompt', (e) => { e.preventDefault(); deferred = e; $('#install-text').textContent = T[lang].install; $('#install-btn').hidden = false; $('#install').hidden = false; });
$('#install-btn').addEventListener('click', async () => { if (!deferred) return; deferred.prompt(); await deferred.userChoice.catch(() => null); deferred = null; $('#install').hidden = true; });
if (!standalone && /iPhone|iPad|iPod/.test(navigator.userAgent)) { $('#install-text').textContent = T[lang].ios; $('#install-btn').hidden = true; $('#install').hidden = false; }

// Tool pages show a Home button back to here when opened inside the installed app.
rememberAppHome('../', location.href.split(/[?#]/)[0]);
store.set('mms-app-lang', lang);

render();
if ('serviceWorker' in navigator && okOrigin) navigator.serviceWorker.register('../sw.js', { scope: '../' }).catch(() => {});
fetch('precache.json', { cache: 'no-cache' })
  .then(async (r) => {
    if (!r.ok) throw new Error(r.status);
    precache = await r.json();
    return saveOffline();
  })
  .catch(async () => {
    // Offline on a later visit: the list itself was saved with the tools.
    const hit = await (window.caches?.match(new URL('precache.json', location.href).href) ?? null);
    status(hit ? T[lang].ready : T[lang].noSw, !!hit);
  });
