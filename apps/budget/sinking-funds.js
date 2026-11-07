// Sinking-funds planner, English (sinking-funds.html) and Spanish (fondos-ahorro.html). Logic in lib/sinking.js.
// Funds are saved in this browser only. The copy buttons put tab-separated rows on the clipboard that paste
// straight into the Sinking Funds tab of Money Dashboard Pro.
import config from './config.js';
import { initTracking } from './lib/track.js';
import { PRESETS, presetDate, normalizeFund, plan, fundsTsv, depositsTsv, plannerCsv } from './lib/sinking.js';
import { $, esc, store, download, live } from './page.js';

const es = document.documentElement.lang.startsWith('es');
const lang = es ? 'es' : 'en';
const loc = es ? 'es-US' : 'en-US';
const money = (n, d = 0) => (Number(n) || 0).toLocaleString(loc, { style: 'currency', currency: 'USD', minimumFractionDigits: d, maximumFractionDigits: d });
const day = (s) => new Date(`${s}T12:00:00`).toLocaleDateString(loc, { month: 'short', day: 'numeric', year: 'numeric' });
const d = new Date();
const today = `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-${String(d.getDate()).padStart(2, '0')}`;
const KEY = 'mms-sinking-funds-v1';

const T = es ? {
  errors: { name: 'Ponle nombre al fondo.', target: 'Escribe cuánto necesitas.', due: 'Elige para cuándo lo necesitas.', saved: 'Escribe lo que ya tienes guardado (o 0).' },
  stats: ['Guardar al mes', 'Por cheque', 'Ya ahorrado', 'Falta'],
  months: (n) => (n === 0 ? 'ya llegó la fecha' : n === 1 ? '1 mes' : `${n} meses`),
  perMonth: 'al mes', due: 'para el', remove: 'Quitar', late: 'Ya llegó la fecha y falta dinero: decide si lo pagas de este mes o mueves la fecha.',
  done: '¡Listo!', empty: 'Todavía no tienes fondos. Agrega uno arriba o empieza con una idea.',
  next: (r) => `Lo siguiente: <b>${esc(r.name)}</b> el ${day(r.due)}. Guarda ${money(r.monthly)} al mes.`,
  copied: 'Copiado. Pégalo en la hoja.', copyFail: 'No se pudo copiar: selecciona el texto y cópialo.',
  file: 'fondos-de-ahorro.csv', pay: { 4: 'Cada semana', 2: 'Cada dos semanas o dos veces al mes', 1: 'Una vez al mes' },
} : {
  errors: { name: 'Give the fund a name.', target: 'Enter how much you need.', due: 'Pick when you need it.', saved: 'Enter what you have saved already (or 0).' },
  stats: ['Save each month', 'Per paycheck', 'Saved so far', 'Still to save'],
  months: (n) => (n === 0 ? 'due now' : n === 1 ? '1 month' : `${n} months`),
  perMonth: 'a month', due: 'by', remove: 'Remove', late: 'The date has come and it isn\'t fully saved: pay the rest from this month or move the date.',
  done: 'Fully saved!', empty: 'No funds yet. Add one above or start from an idea.',
  next: (r) => `Next up: <b>${esc(r.name)}</b> on ${day(r.due)}. Put away ${money(r.monthly)} a month.`,
  copied: 'Copied. Paste it into the sheet.', copyFail: 'Couldn\'t copy: select the text and copy it.',
  file: 'sinking-funds.csv', pay: { 4: 'Every week', 2: 'Every two weeks or twice a month', 1: 'Once a month' },
};

let state = { funds: [], perPay: 2 };
try { const s = JSON.parse(store.get(KEY) || 'null'); if (s && Array.isArray(s.funds)) state = { funds: s.funds.map(normalizeFund).filter((f) => !f.error), perPay: [1, 2, 4].includes(s.perPay) ? s.perPay : 2 }; } catch { /* first visit */ }
const save = () => store.set(KEY, JSON.stringify(state));

const form = $('#fund-form');
form.due.min = today;
$('#per-pay').innerHTML = Object.entries(T.pay).sort((a, b) => b[0] - a[0]).map(([k, v]) => `<option value="${k}"${Number(k) === state.perPay ? ' selected' : ''}>${v}</option>`).join('');
$('#ideas').innerHTML = PRESETS[lang].map(([name, target, months], i) => `<button type="button" class="chip" data-i="${i}">${esc(name)}</button>`).join('');

function render() {
  const p = plan(state.funds, today, { perPay: state.perPay });
  const vals = [p.monthly, p.perPaycheck, p.saved, p.still];
  $('#stats').innerHTML = vals.map((v, i) => `<div class="stat"><span>${T.stats[i]}</span><b>${money(v, i < 2 ? 2 : 0)}</b></div>`).join('');
  $('#next').innerHTML = p.next ? T.next(p.next) : '';
  $('#funds').innerHTML = p.rows.length ? p.rows.map((r) => `<li class="fund${r.done ? ' done' : ''}${r.late ? ' late' : ''}">
      <div class="fund-top"><h3>${esc(r.name)}</h3><b>${r.done ? T.done : `${money(r.monthly, 2)} ${T.perMonth}`}</b></div>
      <p class="tiny">${money(r.saved)} / ${money(r.target)} · ${T.due} ${day(r.due)} · ${T.months(r.monthsLeft)}</p>
      <div class="bar" role="img" aria-label="${Math.round(r.pct * 100)}%"><i style="width:${Math.round(r.pct * 100)}%"></i></div>
      ${r.late ? `<p class="tiny warn-text">${T.late}</p>` : ''}
      <div class="row"><label class="inline">${es ? 'Ahorrado' : 'Saved'} <input type="number" min="0" step="1" inputmode="decimal" value="${r.saved}" data-saved="${r.id}" aria-label="${esc(r.name)}: ${es ? 'ahorrado' : 'saved so far'}"></label>
      <button type="button" class="link" data-remove="${r.id}">${T.remove}<span class="sr-only"> ${esc(r.name)}</span></button></div></li>`).join('')
    : `<li class="none">${T.empty}</li>`;
  $('#t-funds').value = fundsTsv(p.rows);
  $('#t-deposits').value = depositsTsv(p.rows, today);
  $('#export').hidden = !p.rows.length;
  save();
}

form.addEventListener('submit', (e) => {
  e.preventDefault();
  const f = normalizeFund(Object.fromEntries(new FormData(form)));
  if (f.error) { $('#form-msg').textContent = T.errors[f.error]; form[f.error]?.focus(); return; }
  state.funds.push(f);
  $('#form-msg').textContent = '';
  form.reset();
  render();
  form.name.focus();
});
$('#ideas').addEventListener('click', (e) => {
  const b = e.target.closest('[data-i]');
  if (!b) return;
  const [name, target, months] = PRESETS[lang][Number(b.dataset.i)];
  form.name.value = name; form.target.value = target; form.due.value = presetDate(name, months, today);
  form.saved.focus();
});
$('#funds').addEventListener('click', (e) => {
  const id = e.target.closest('[data-remove]')?.dataset.remove;
  if (!id) return;
  state.funds = state.funds.filter((f) => f.id !== id);
  render();
  form.name.focus();
});
$('#funds').addEventListener('change', (e) => {
  const id = e.target.dataset.saved;
  if (!id) return;
  const f = state.funds.find((x) => x.id === id);
  const v = Number(e.target.value);
  if (f && Number.isFinite(v) && v >= 0) { f.saved = Math.round(v * 100) / 100; render(); $(`[data-saved="${id}"]`)?.focus(); }
});
$('#per-pay').addEventListener('change', (e) => { state.perPay = Number(e.target.value); render(); });
for (const [btn, area] of [['#copy-funds', '#t-funds'], ['#copy-deposits', '#t-deposits']]) {
  $(btn).addEventListener('click', async () => {
    try { await navigator.clipboard.writeText($(area).value); $('#copy-msg').textContent = T.copied; } catch { $(area).select(); $('#copy-msg').textContent = T.copyFail; }
  });
}
$('#csv').addEventListener('click', () => download(T.file, plannerCsv(plan(state.funds, today, { perPay: state.perPay }), lang), 'text/csv'));

const p = config.sheetTemplate;
if (p && live(p.url)) {
  $('#upsell').innerHTML = `<h3>${esc(es ? p.nameEs : p.name)} (${esc(p.price)})</h3><p>${esc(es ? p.pitchEs : p.pitch)}</p><a class="btn small" href="${esc(p.url)}">${es ? 'Ver la plantilla' : 'Get the template'}</a>`;
  $('#upsell').hidden = false;
}
render();
initTracking({ config, app: 'budget', page: es ? 'fondos-ahorro' : 'sinking-funds' });
