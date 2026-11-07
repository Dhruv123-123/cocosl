// Wedding budget planner, English (wedding-budget.html) and Spanish (presupuesto-boda.html). Logic in lib/wedding.js.
// Saved in this browser only. Exports a CSV and tab-separated rows that paste into the wedding budget spreadsheet.
import config from './config.js';
import { initTracking } from './lib/track.js';
import { CATEGORIES, KEYS, nameOf, splitBudget, summary, weddingCsv, weddingTsv } from './lib/wedding.js';
import { $, esc, store, download, live } from './page.js';

const es = document.documentElement.lang.startsWith('es');
const lang = es ? 'es' : 'en';
const loc = es ? 'es-US' : 'en-US';
const money = (n, d = 0) => (Number(n) || 0).toLocaleString(loc, { style: 'currency', currency: 'USD', minimumFractionDigits: d, maximumFractionDigits: d });
const d = new Date();
const today = `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-${String(d.getDate()).padStart(2, '0')}`;
const KEY = 'mms-wedding-v1';
const FIELDS = ['budget', 'estimate', 'actual', 'paid'];

const T = es ? {
  stats: ['Costo esperado', 'Por invitado', 'Falta pagar', 'Guardar al mes'],
  fields: { budget: 'Presupuesto', estimate: 'Cotización', actual: 'Costo real', paid: 'Pagado' },
  left: (n) => (n >= 0 ? `Te quedan <b>${money(n)}</b> sin asignar.` : `Vas <b>${money(-n)}</b> arriba de tu presupuesto.`),
  over: (names) => `Arriba de lo planeado: ${names}. Recorta en otra categoría o usa el colchón.`,
  monthsTxt: (m, v) => (m ? `Con ${m} ${m === 1 ? 'mes' : 'meses'} para la boda, guarda ${money(v)} al mes para pagar lo que falta.` : 'Pon la fecha de la boda para ver cuánto guardar cada mes.'),
  perGuest: (v) => `El lugar, el banquete y el bar salen a ${money(v)} por invitado. Cada invitado menos te ahorra eso.`,
  split: 'Se repartió tu presupuesto. Cambia cualquier cantidad.',
  copied: 'Copiado. Pégalo en la hoja.', copyFail: 'No se pudo copiar: selecciona el texto y cópialo.',
  file: 'presupuesto-de-boda.csv', owed: 'falta',
} : {
  stats: ['Expected cost', 'Per guest', 'Still to pay', 'Save each month'],
  fields: { budget: 'Budget', estimate: 'Quote', actual: 'Final cost', paid: 'Paid' },
  left: (n) => (n >= 0 ? `You have <b>${money(n)}</b> not yet assigned.` : `You're <b>${money(-n)}</b> over your total budget.`),
  over: (names) => `Over plan: ${names}. Trim another category or use the buffer.`,
  monthsTxt: (m, v) => (m ? `With ${m} ${m === 1 ? 'month' : 'months'} to go, put away ${money(v)} a month to cover what's left to pay.` : 'Add the wedding date to see how much to save each month.'),
  perGuest: (v) => `Venue, catering and bar come to ${money(v)} per guest. Every guest you cut saves about that.`,
  split: 'Your budget is split across the categories. Change any amount.',
  copied: 'Copied. Paste it into the sheet.', copyFail: 'Couldn\'t copy: select the text and copy it.',
  file: 'wedding-budget.csv', owed: 'left to pay',
};

let state = { total: '', guests: '', date: '', saved: '', rows: {} };
try { const s = JSON.parse(store.get(KEY) || 'null'); if (s && typeof s === 'object' && s.rows) state = { ...state, ...s }; } catch { /* first visit */ }
const save = () => store.set(KEY, JSON.stringify(state));

const form = $('#basics');
form.date.min = today;
for (const k of ['total', 'guests', 'date', 'saved']) form[k].value = state[k] ?? '';

$('#cats').innerHTML = CATEGORIES.map(([k]) => `<li class="wcat" data-key="${k}">
  <div class="fund-top"><h3 id="n-${k}">${esc(nameOf(k, lang))}</h3><b data-out="${k}"></b></div>
  <div class="wgrid">${FIELDS.map((f) => `<label>${T.fields[f]}<input type="number" min="0" step="1" inputmode="decimal" data-k="${k}" data-f="${f}" aria-describedby="n-${k}"></label>`).join('')}</div>
  <div class="bar" role="img" data-bar="${k}"><i></i></div></li>`).join('');

function fill() {
  for (const el of document.querySelectorAll('[data-k]')) { const v = state.rows[el.dataset.k]?.[el.dataset.f]; el.value = v ?? ''; }
}

function render() {
  const s = summary(state, today);
  const vals = [s.expected, s.perGuest, s.owed, s.monthly];
  $('#stats').innerHTML = vals.map((v, i) => `<div class="stat"><span>${T.stats[i]}</span><b>${v == null ? '—' : money(v, i === 1 || i === 3 ? 2 : 0)}</b></div>`).join('');
  const notes = [];
  if (s.total) notes.push(T.left(s.left));
  if (s.overRows.length) notes.push(`<span class="warn-text">${esc(T.over(s.overRows.map((k) => nameOf(k, lang)).join(', ')))}</span>`);
  if (s.venuePerGuest) notes.push(T.perGuest(s.venuePerGuest));
  notes.push(T.monthsTxt(s.months, s.monthly));
  $('#notes').innerHTML = notes.map((n) => `<p>${n}</p>`).join('');
  for (const r of s.rows) {
    const out = $(`[data-out="${r.key}"]`);
    out.textContent = r.expected ? `${money(r.owed)} ${T.owed}` : '';
    out.className = r.over ? 'neg' : '';
    const pct = r.expected ? Math.min(100, Math.round((r.paid / r.expected) * 100)) : 0;
    const bar = $(`[data-bar="${r.key}"]`);
    bar.setAttribute('aria-label', `${nameOf(r.key, lang)}: ${pct}% ${es ? 'pagado' : 'paid'}`);
    bar.firstElementChild.style.width = `${pct}%`;
    bar.classList.toggle('over', r.over > 0);
  }
  $('#t-rows').value = weddingTsv(s, lang);
  $('#export').hidden = !s.expected;
  save();
  return s;
}

form.addEventListener('submit', (e) => e.preventDefault());
form.addEventListener('input', (e) => {
  const k = e.target.name;
  if (!(k in state)) return;
  state[k] = e.target.value;
  render();
});
$('#split').addEventListener('click', () => {
  const total = Number(form.total.value);
  if (!(total > 0)) { $('#split-msg').textContent = es ? 'Escribe tu presupuesto total primero.' : 'Enter your total budget first.'; form.total.focus(); return; }
  const parts = splitBudget(total);
  for (const k of KEYS) state.rows[k] = { ...(state.rows[k] || {}), budget: parts[k] };
  fill(); render();
  $('#split-msg').textContent = T.split;
});
$('#cats').addEventListener('input', (e) => {
  const { k, f } = e.target.dataset;
  if (!k) return;
  state.rows[k] = { ...(state.rows[k] || {}), [f]: e.target.value };
  render();
});
$('#copy').addEventListener('click', async () => {
  try { await navigator.clipboard.writeText($('#t-rows').value); $('#copy-msg').textContent = T.copied; } catch { $('#t-rows').select(); $('#copy-msg').textContent = T.copyFail; }
});
$('#csv').addEventListener('click', () => download(T.file, weddingCsv(summary(state, today), lang), 'text/csv'));

const p = config.weddingTemplate;
if (p && live(p.url)) {
  $('#upsell').innerHTML = `<h3>${esc(es ? p.nameEs : p.name)} (${esc(p.price)})</h3><p>${esc(es ? p.pitchEs : p.pitch)}</p><a class="btn small" href="${esc(p.url)}">${es ? 'Ver la plantilla' : 'Get the spreadsheet'}</a>`;
  $('#upsell').hidden = false;
}
fill();
render();
initTracking({ config, app: 'budget', page: es ? 'presupuesto-boda' : 'wedding-budget' });
