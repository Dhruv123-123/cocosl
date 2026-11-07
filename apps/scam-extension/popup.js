import config from './lib/config.js';
import { analyzeMessage } from './lib/scan.js';
import { ES, translateResult } from './lib/i18n.js';
import { checkPage } from './verdict.js';

const ext = globalThis.chrome?.runtime?.id ? globalThis.chrome : null; // null when opened as a plain page (store screenshots)
const lang = ext?.i18n?.getUILanguage?.() || navigator.language || 'en';
const es = lang.toLowerCase().startsWith('es');
document.documentElement.lang = es ? 'es' : 'en';

const $ = (s) => document.querySelector(s);
const esc = (s) => String(s).replace(/[&<>"']/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' })[c]);
const live = (u) => typeof u === 'string' && /^https:\/\//.test(u) && !/REPLACE_ME/i.test(u);

const TEXT = {
  en: {
    message: 'Paste a text, email or link', check: 'Check it', warnings: 'Warn me with a red badge on look-alike websites',
    privacy: 'Checks run on your device. Nothing you paste is sent anywhere.', site: 'Full checker and scam guides', kit: 'Family kit',
    level: { high: ['High risk', 'Several signs of a scam. Don\'t click, reply or pay.'], medium: ['Be careful', 'Some warning signs. Check with the company directly.'], low: ['No common red flags', 'A good sign, not proof. Be careful if it asks for money or info.'] },
    page: { official: (h) => `<b>${h}</b> is an official site we know.`, low: (h) => `No look-alike signs on <b>${h}</b>.`, medium: (h) => `<b>${h}</b> has some warning signs:`, high: (h) => `<b>${h}</b> looks like a fake site:` },
    looksLike: 'Looks like:', whatToDo: 'What to do',
  },
  es: {
    message: 'Pega un mensaje, correo o enlace', check: 'Revisar', warnings: 'Avísame con una señal roja en sitios que imitan a otros',
    privacy: 'Todo se revisa en tu dispositivo. Nada de lo que pegas se envía.', site: 'Revisor completo y guías de estafas', kit: 'Kit familiar',
    level: ES.ui.level,
    page: { official: (h) => `<b>${h}</b> es un sitio oficial que conocemos.`, low: (h) => `No vemos señales de imitación en <b>${h}</b>.`, medium: (h) => `<b>${h}</b> tiene algunas señales de alerta:`, high: (h) => `<b>${h}</b> parece un sitio falso:` },
    looksLike: ES.ui.looksLike, whatToDo: ES.ui.whatToDo,
  },
};
const T = es ? TEXT.es : TEXT.en;
const issueLabel = (i) => (es && ES.links[i.code] ? ES.links[i.code](i.param) : i.label);

$('#brand').textContent = config.brand;
$('#l-message').textContent = T.message;
$('#b-check').textContent = T.check;
$('#l-warnings').textContent = T.warnings;
$('#privacy').textContent = T.privacy;
$('#site').textContent = T.site;
$('#site').href = `${config.siteUrl}/${es ? 'es/' : ''}`;
if (live(config.product.url)) $('#kit').innerHTML = ` · <a href="${esc(config.product.url)}" target="_blank" rel="noopener">${T.kit} (${esc(config.product.price)})</a>`;
if (ext && !new URLSearchParams(location.search).has('window')) document.body.classList.add('ext');

function render(r) {
  if (es) r = translateResult(r);
  const [title, sub] = T.level[r.level];
  const flags = r.signals.filter((s) => s.id !== 'money-amount' || r.level !== 'low').slice(0, 4);
  const linkIssues = r.links.flatMap((l) => l.issues.map((i) => `${l.host}: ${issueLabel(i)}`));
  $('#result').innerHTML = `
    <div class="verdict ${r.level}"><div class="meter"><span style="width:${Math.max(r.score, 3)}%"></span></div>
      <p class="score">${esc(title)} <small>${r.score}/100</small></p>
      <p>${esc(sub)}${r.category && r.level !== 'low' ? ` ${T.looksLike} <b>${esc(r.category)}</b>.` : ''}</p></div>
    ${flags.length || linkIssues.length ? `<ul class="flags">${flags.map((s) => `<li><b>${esc(s.label)}</b> ${esc(s.advice)}</li>`).join('')}${linkIssues.map((t) => `<li>${esc(t)}</li>`).join('')}</ul>` : ''}
    <p class="h">${T.whatToDo}</p><ol>${r.steps.map((s) => `<li>${esc(s)}</li>`).join('')}</ol>`;
  $('#result').hidden = false;
}

function check(e) {
  e?.preventDefault();
  const text = $('#message').value;
  if (!text.trim()) { $('#message').focus(); return; }
  render(analyzeMessage(text));
}
$('#checker').addEventListener('submit', check);

// Text sent from the right-click menu arrives in the hash.
const sent = new URLSearchParams(location.hash.slice(1)).get('m');
if (sent) { $('#message').value = sent; check(); }

// The site in the current tab. Opening the popup grants activeTab, so the URL is readable.
async function showPage() {
  if (!ext?.tabs || sent) return;
  const [tab] = await ext.tabs.query({ active: true, currentWindow: true });
  const v = checkPage(tab?.url || '');
  if (v.level === 'none') return;
  const issues = v.issues.map((i) => `<li>${esc(issueLabel(i))}</li>`).join('');
  $('#page').className = `page ${v.level}`;
  $('#page').innerHTML = `<p>${T.page[v.level](esc(v.host))}</p>${issues ? `<ul>${issues}</ul>` : ''}`;
  $('#page').hidden = false;
}
showPage().catch(() => {});

// Optional look-alike warnings need the "tabs" permission, asked for only when turned on.
const toggle = $('#site-warnings');
if (ext?.permissions) {
  Promise.all([ext.storage.local.get('siteWarnings'), ext.permissions.contains({ permissions: ['tabs'] })])
    .then(([s, ok]) => { toggle.checked = Boolean(s.siteWarnings && ok); }).catch(() => {});
  toggle.addEventListener('change', async () => {
    let on = toggle.checked;
    if (on) on = await ext.permissions.request({ permissions: ['tabs'] }).catch(() => false);
    toggle.checked = on;
    await ext.storage.local.set({ siteWarnings: on });
  });
} else {
  toggle.parentElement.hidden = true;
}
