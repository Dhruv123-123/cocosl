// "Is this website legit?" link checker. Shared by /link/ (English) and /es/enlace/ (Spanish).
import { checkPage } from './lib/site.js';
import { extractUrls } from './lib/scan.js';
import { ES } from './lib/i18n.js';
import config from './config.js';
import { initTracking } from './lib/track.js';
import { loadBlocklist, lookup } from './lib/blocklist.js';

// The phishing list is downloaded once (about 390 KB) the first time someone checks a link, then
// the service worker keeps it for offline use. The address being checked is never sent anywhere.
const LIST_URL = new URL('./phishlist/phish.bin', import.meta.url).href;
const warm = () => loadBlocklist(LIST_URL);

const es = document.documentElement.lang.startsWith('es');
const $ = (s) => document.querySelector(s);
const esc = (s) => String(s).replace(/[&<>"']/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' })[c]);

const T = es ? {
  empty: 'Pega una dirección web o un enlace, por ejemplo paypal-seguridad.com.',
  none: 'No encontramos una dirección web. Pega el enlace completo, por ejemplo https://ejemplo.com/pagina.',
  level: {
    official: ['Sitio oficial', (h) => `${h} es un sitio oficial de una empresa que conocemos. Aun así, revisa que la dirección sea exactamente esta.`],
    low: ['Sin señales de imitación', (h) => `No vemos trucos comunes en ${h}, pero eso no prueba que sea confiable. Usa los pasos de abajo antes de pagar o dar datos.`],
    medium: ['Ten cuidado', (h) => `${h} tiene algunas señales de alerta. No ingreses datos hasta verificarlo.`],
    high: ['Parece un sitio falso', (h) => `${h} parece imitar a una empresa conocida. No ingreses contraseñas, tarjetas ni códigos.`],
    listed: ['Reportado como phishing', (h) => `${h} está en listas públicas de sitios de phishing. No ingreses contraseñas, tarjetas ni códigos, y no descargues nada.`],
  },
  listedIssue: (d) => `${d} aparece en una lista pública de dominios de phishing.`,
  list: (date) => `También lo comparamos con una lista de dominios de phishing reportados (DestroyList y Phishing.Database, actualizada el ${date}), guardada en tu navegador. Que un sitio no esté en la lista no prueba que sea seguro.`,
  noList: 'La lista de phishing no se pudo cargar, así que solo revisamos los trucos de la dirección.',
  appeal: '¿Es tu sitio y es un error? Pide que lo quiten',
  why: 'Lo que encontramos', more: 'Revísalo tú mismo',
  whois: 'Ver cuándo se registró el dominio (ICANN)', safe: 'Buscarlo en Google Safe Browsing', note: 'Estos enlaces abren otro sitio y le envían la dirección que revisas.',
  issue: (i) => (i.code !== 'listed' && ES.links[i.code] ? ES.links[i.code](i.param) : i.label),
} : {
  empty: 'Paste a web address or link, for example paypal-security.com.',
  none: "We couldn't find a web address in that. Paste the full link, for example https://example.com/page.",
  level: {
    official: ['Official site', (h) => `${h} is an official site of a company we know. Still check the address is exactly this.`],
    low: ['No look-alike signs', (h) => `We don't see common tricks in ${h}, but that doesn't prove it's trustworthy. Use the steps below before you pay or type anything in.`],
    medium: ['Be careful', (h) => `${h} has some warning signs. Don't enter anything until you've checked it out.`],
    high: ['Looks like a fake site', (h) => `${h} looks like it's imitating a well-known company. Don't enter passwords, card numbers or codes.`],
    listed: ['Reported as phishing', (h) => `${h} is on public lists of phishing sites. Don't enter passwords, card numbers or codes, and don't download anything.`],
  },
  listedIssue: (d) => `${d} is on a public list of reported phishing domains.`,
  list: (date) => `We also compared it with a list of reported phishing domains (DestroyList and Phishing.Database, updated ${date}) kept in your browser. A site not being on the list doesn't prove it's safe.`,
  noList: "The phishing list couldn't load, so we only checked the address for tricks.",
  appeal: 'Is this your site and a mistake? Ask for it to be removed',
  why: 'What we found', more: 'Check it yourself',
  whois: 'See when the domain was registered (ICANN lookup)', safe: 'Look it up in Google Safe Browsing', note: 'These links open another site and send it the address you are checking.',
  issue: (i) => i.label,
};
const meter = { official: ['low', 3], low: ['low', 15], medium: ['medium', 55], high: ['high', 90], listed: ['high', 100] };

async function check(e) {
  e?.preventDefault();
  const raw = $('#url').value.trim();
  const out = $('#result');
  out.hidden = false;
  if (!raw) { out.innerHTML = `<p>${T.empty}</p>`; return; }
  const candidate = /\s/.test(raw) ? extractUrls(raw)[0] : raw;
  const v = candidate ? checkPage(candidate) : { level: 'none' };
  if (v.level === 'none') { out.innerHTML = `<p>${T.none}</p>`; return; }
  const list = await warm();
  // Official sites are never flagged by the list, whatever it says.
  const listed = list && v.level !== 'official' ? lookup(list, v.host) : null;
  if (listed) { v.level = 'listed'; v.issues = [{ code: 'listed', label: T.listedIssue(listed) }, ...v.issues]; }
  const [title, body] = T.level[v.level];
  const [cls, width] = meter[v.level];
  const reg = v.host.split('.').slice(-2).join('.');
  out.innerHTML = `
    <div class="verdict ${cls}"><div class="meter"><span style="width:${width}%"></span></div>
      <p class="score">${esc(title)}</p><p>${esc(body(v.host))}</p></div>
    ${v.issues.length ? `<h3>${T.why}</h3><ul class="flags">${v.issues.map((i) => `<li>${esc(T.issue(i))}</li>`).join('')}</ul>` : ''}
    <h3>${T.more}</h3>
    <ul class="flags">
      <li><a href="https://lookup.icann.org/en/lookup?name=${encodeURIComponent(reg)}" target="_blank" rel="noopener noreferrer">${T.whois}</a></li>
      <li><a href="https://transparencyreport.google.com/safe-browsing/search?url=${encodeURIComponent(v.host)}" target="_blank" rel="noopener noreferrer">${T.safe}</a></li>
    </ul>
    <p class="tiny">${T.note}</p>
    <p class="tiny">${list ? esc(T.list(list.date)) : T.noList}${listed ? ` <a href="https://phishdestroy.io/appeals/" target="_blank" rel="noopener noreferrer">${T.appeal}</a>.` : ''}</p>`;
}

$('#link-form').addEventListener('submit', check);
$('#url').addEventListener('focus', warm, { once: true });
document.querySelectorAll('[data-url]').forEach((b) => b.addEventListener('click', () => { $('#url').value = b.dataset.url; check(); }));
initTracking({ config, app: 'scam-checker', page: 'link-checker' });
