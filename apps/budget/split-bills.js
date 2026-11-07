// Bill splitter for roommates and couples, English (split-bills.html) and Spanish (dividir-gastos.html).
// Logic in lib/splitbills.js. Saved in this browser only.
import config from './config.js';
import { initTracking } from './lib/track.js';
import { MAX_PEOPLE, emptyGroup, loadGroup, label, summary, splitCsv, splitText } from './lib/splitbills.js';
import { $, esc, store, download } from './page.js';

const es = document.documentElement.lang.startsWith('es');
const lang = es ? 'es' : 'en';
const loc = es ? 'es-US' : 'en-US';
const money = (n) => (Number(n) || 0).toLocaleString(loc, { style: 'currency', currency: 'USD' });
const KEY = 'mms-split-bills-v1';
const T = es ? {
  name: 'Nombre', income: 'Ingreso neto al mes ($)', pct: 'Porcentaje', remove: 'Quitar', methods: { income: 'Por ingreso', equal: 'Igual para todos', custom: 'Porcentajes a la medida' },
  billSplit: { group: 'Como el grupo', equal: 'Igual para todos', income: 'Por ingreso', custom: 'A la medida' },
  cols: ['Persona', 'Le toca', 'Pagó', 'Saldo'], pctInc: 'de su ingreso', square: 'Todos están a mano.', none: 'Agrega los gastos que comparten.',
  errName: 'Ponle nombre al gasto.', errAmt: 'Escribe el monto.', copied: 'Copiado. Pégalo en el chat del grupo.', copyFail: 'No se pudo copiar: selecciona el texto y cópialo.',
  file: 'gastos-compartidos.csv', paidBy: 'pagó', pays: 'le paga a', customWarn: (t) => `Los porcentajes suman ${t}%. Los ajustamos para que sumen 100.`,
} : {
  name: 'Name', income: 'Take-home pay a month ($)', pct: 'Percent', remove: 'Remove', methods: { income: 'By income', equal: 'Equally', custom: 'Custom percentages' },
  billSplit: { group: 'Same as the group', equal: 'Equally', income: 'By income', custom: 'Custom' },
  cols: ['Person', 'Their share', 'Paid', 'Balance'], pctInc: 'of income', square: 'Everyone is square.', none: 'Add the bills you share.',
  errName: 'Name the bill.', errAmt: 'Enter the amount.', copied: 'Copied. Paste it into the group chat.', copyFail: 'Couldn\'t copy: select the text and copy it.',
  file: 'shared-bills.csv', paidBy: 'paid', pays: 'pays', customWarn: (t) => `The percentages add up to ${t}%. We scale them to 100.`,
};

let g = emptyGroup(2);
try { const raw = store.get(KEY); if (raw) g = loadGroup(raw); } catch { /* first visit */ }
const save = () => store.set(KEY, JSON.stringify(g));

$('#method').innerHTML = Object.entries(T.methods).map(([k, v]) => `<option value="${k}">${v}</option>`).join('');
$('#b-split').innerHTML = Object.entries(T.billSplit).map(([k, v]) => `<option value="${k === 'group' ? 'group' : k}">${v}</option>`).join('');

function renderPeople() {
  $('#method').value = g.method;
  const custom = g.method === 'custom';
  $('#people').innerHTML = g.people.map((p, i) => `<li class="person"><fieldset><legend>${esc(label(g, i, lang))}</legend>
    <label>${T.name}<input data-i="${i}" data-f="name" maxlength="30" autocomplete="off" value="${esc(p.name)}"></label>
    <label>${T.income}<input data-i="${i}" data-f="income" type="number" min="0" step="1" inputmode="decimal" value="${p.income || ''}"></label>
    ${custom ? `<label>${T.pct}<input data-i="${i}" data-f="pct" type="number" min="0" max="100" step="1" value="${p.pct}"></label>` : ''}
    ${g.people.length > 2 ? `<button type="button" class="link" data-drop="${i}">${T.remove}<span class="sr-only"> ${esc(label(g, i, lang))}</span></button>` : ''}
  </fieldset></li>`).join('');
  $('#add-person').hidden = g.people.length >= MAX_PEOPLE;
  $('#b-paid').innerHTML = g.people.map((_, i) => `<option value="${i}">${esc(label(g, i, lang))}</option>`).join('');
}

function renderResult() {
  const s = summary(g);
  const custom = g.method === 'custom' ? g.people.reduce((t, p) => t + (p.pct || 0), 0) : 100;
  $('#custom-msg').textContent = custom !== 100 ? T.customWarn(custom) : '';
  $('#bills').innerHTML = s.rows.length ? s.rows.map((r) => `<li><div class="fund-top"><b>${esc(r.name)}</b><span>${money(r.amount)}</span></div>
    <p class="tiny">${esc(label(g, r.paidBy, lang))} ${T.paidBy} · ${T.billSplit[r.used]}: ${r.parts.map((p, i) => `${esc(label(g, i, lang))} ${money(p)}`).join(', ')}</p>
    <button type="button" class="link" data-bill="${esc(r.id)}">${T.remove}<span class="sr-only"> ${esc(r.name)}</span></button></li>`).join('') : `<li class="none">${T.none}</li>`;
  $('#result-body').innerHTML = g.people.map((_, i) => `<tr><th scope="row">${esc(label(g, i, lang))}</th><td class="num">${money(s.share[i])}${s.pctOfIncome[i] != null ? `<small> ${Math.round(s.pctOfIncome[i] * 100)}% ${T.pctInc}</small>` : ''}</td><td class="num">${money(s.paid[i])}</td><td class="num ${s.balance[i] < 0 ? 'neg' : s.balance[i] > 0 ? 'pos' : ''}">${money(s.balance[i])}</td></tr>`).join('');
  $('#moves').innerHTML = s.rows.length ? (s.moves.length ? s.moves.map((m) => `<li><b>${esc(label(g, m.from, lang))}</b> ${T.pays} <b>${esc(label(g, m.to, lang))}</b> ${money(m.amount)}</li>`).join('') : `<li>${T.square}</li>`) : '';
  $('#t-text').value = splitText(g, s, lang, money);
  $('#result').hidden = !s.rows.length;
  save();
}
const renderAll = () => { renderPeople(); renderResult(); };

$('#people').addEventListener('input', (e) => {
  const { i, f } = e.target.dataset;
  if (i === undefined) return;
  const p = g.people[Number(i)];
  if (f === 'name') p.name = e.target.value.slice(0, 30);
  else { const v = Number(e.target.value); p[f] = Number.isFinite(v) && v >= 0 ? v : 0; }
  if (f === 'name') { e.target.closest('fieldset').querySelector('legend').textContent = label(g, Number(i), lang); $('#b-paid').options[Number(i)].textContent = label(g, Number(i), lang); }
  renderResult();
});
$('#people').addEventListener('click', (e) => {
  const i = e.target.closest('[data-drop]')?.dataset.drop;
  if (i === undefined) return;
  const k = Number(i);
  g.people.splice(k, 1);
  g.bills = g.bills.map((b) => ({ ...b, paidBy: b.paidBy === k ? 0 : b.paidBy > k ? b.paidBy - 1 : b.paidBy }));
  renderAll();
  $('#add-person').focus();
});
$('#add-person').addEventListener('click', () => {
  if (g.people.length >= MAX_PEOPLE) return;
  g.people.push({ name: '', income: 0, pct: 0 });
  renderAll();
  $(`[data-i="${g.people.length - 1}"][data-f="name"]`)?.focus();
});
$('#method').addEventListener('change', (e) => { g.method = e.target.value; renderAll(); });

const form = $('#bill-form');
form.addEventListener('submit', (e) => {
  e.preventDefault();
  const name = form.name.value.trim(); const amount = Math.round(Number(form.amount.value) * 100) / 100;
  if (!name) { $('#bill-msg').textContent = T.errName; form.name.focus(); return; }
  if (!(amount > 0)) { $('#bill-msg').textContent = T.errAmt; form.amount.focus(); return; }
  g.bills.push({ id: Math.random().toString(36).slice(2, 10), name: name.slice(0, 60), amount, paidBy: Number(form.paidBy.value) || 0, method: form.split.value });
  $('#bill-msg').textContent = '';
  form.name.value = ''; form.amount.value = '';
  renderResult();
  form.name.focus();
});
$('#bills').addEventListener('click', (e) => {
  const id = e.target.closest('[data-bill]')?.dataset.bill;
  if (!id) return;
  g.bills = g.bills.filter((b) => b.id !== id);
  renderResult();
  form.name.focus();
});
$('#copy').addEventListener('click', async () => {
  try { await navigator.clipboard.writeText($('#t-text').value); $('#copy-msg').textContent = T.copied; } catch { $('#t-text').select(); $('#copy-msg').textContent = T.copyFail; }
});
$('#csv').addEventListener('click', () => download(T.file, splitCsv(g, summary(g), lang), 'text/csv'));

renderAll();
initTracking({ config, app: 'budget', page: es ? 'dividir-gastos' : 'split-bills' });
