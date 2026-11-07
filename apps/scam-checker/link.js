// "Is this website legit?" link checker. Shared by /link/ (English) and /es/enlace/ (Spanish).
import { checkPage } from './lib/site.js';
import { extractUrls } from './lib/scan.js';
import { ES } from './lib/i18n.js';

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
  },
  why: 'Lo que encontramos', more: 'Revísalo tú mismo',
  whois: 'Ver cuándo se registró el dominio (ICANN)', safe: 'Buscarlo en Google Safe Browsing', note: 'Estos enlaces abren otro sitio y le envían la dirección que revisas.',
  issue: (i) => (ES.links[i.code] ? ES.links[i.code](i.param) : i.label),
} : {
  empty: 'Paste a web address or link, for example paypal-security.com.',
  none: "We couldn't find a web address in that. Paste the full link, for example https://example.com/page.",
  level: {
    official: ['Official site', (h) => `${h} is an official site of a company we know. Still check the address is exactly this.`],
    low: ['No look-alike signs', (h) => `We don't see common tricks in ${h}, but that doesn't prove it's trustworthy. Use the steps below before you pay or type anything in.`],
    medium: ['Be careful', (h) => `${h} has some warning signs. Don't enter anything until you've checked it out.`],
    high: ['Looks like a fake site', (h) => `${h} looks like it's imitating a well-known company. Don't enter passwords, card numbers or codes.`],
  },
  why: 'What we found', more: 'Check it yourself',
  whois: 'See when the domain was registered (ICANN lookup)', safe: 'Look it up in Google Safe Browsing', note: 'These links open another site and send it the address you are checking.',
  issue: (i) => i.label,
};
const meter = { official: ['low', 3], low: ['low', 15], medium: ['medium', 55], high: ['high', 90] };

function check(e) {
  e?.preventDefault();
  const raw = $('#url').value.trim();
  const out = $('#result');
  out.hidden = false;
  if (!raw) { out.innerHTML = `<p>${T.empty}</p>`; return; }
  const candidate = /\s/.test(raw) ? extractUrls(raw)[0] : raw;
  const v = candidate ? checkPage(candidate) : { level: 'none' };
  if (v.level === 'none') { out.innerHTML = `<p>${T.none}</p>`; return; }
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
    <p class="tiny">${T.note}</p>`;
}

$('#link-form').addEventListener('submit', check);
document.querySelectorAll('[data-url]').forEach((b) => b.addEventListener('click', () => { $('#url').value = b.dataset.url; check(); }));
