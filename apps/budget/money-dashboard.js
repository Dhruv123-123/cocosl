// Money dashboard maker, English (money-dashboard.html) and Spanish (tablero-dinero.html).
// Reads bank CSVs in the browser, sorts them into categories (lib/dashboard.js) and downloads a
// spreadsheet with live formulas (lib/xlsx.js). Nothing is uploaded. Category fixes are remembered
// in this browser only.
import config from './config.js';
import { initTracking } from './lib/track.js';
import { importBankCsv } from './lib/budget.js';
import { parseStatement } from './lib/statement.js';
import { CATEGORIES, buildDashboard, workbookSheets, catName, labels } from './lib/dashboard.js';
import { buildXlsx } from './lib/xlsx.js';
import { parsePlanCsv, PLAN_STORE } from './lib/paycheck-plan.js';
import { loadSheet, netWorthSheet } from './lib/networth.js';
import { $, esc, store, live } from './page.js';

const es = document.documentElement.lang.startsWith('es');
const lang = es ? 'es' : 'en';
const loc = es ? 'es-US' : 'en-US';
const L = labels(lang);
const money = (n, d = 0) => (Number(n) || 0).toLocaleString(loc, { style: 'currency', currency: 'USD', minimumFractionDigits: d, maximumFractionDigits: d });
const monthName = (m) => new Date(`${m}-15T12:00:00`).toLocaleDateString(loc, { month: 'short', year: '2-digit' });
const localToday = () => { const d = new Date(); return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-${String(d.getDate()).padStart(2, '0')}`; };
const today = localToday();

const T = es ? {
  read: (n, files, skipped) => `Leímos ${n} movimientos de ${files}${skipped ? `; saltamos ${skipped} líneas que no pudimos leer` : ''}.`,
  dupes: (n) => ` Quitamos ${n} repetidos.`,
  fileErr: (e) => `${e}. Revisa que sea la descarga en CSV, no un estado de cuenta en PDF.`,
  pasteErr: (e) => `${e}. Copia filas completas: fecha, descripción y monto.`,
  none: 'No encontramos movimientos. Prueba con otro archivo.',
  stats: ['Meses', 'Entra al mes (promedio)', 'Gastos al mes (promedio)', 'Te sobra al mes (promedio)'],
  sortTitle: 'Ordena lo que no reconocimos',
  sortLede: (n) => `${n} comercio${n === 1 ? '' : 's'} quedaron en «Otros». Elige una categoría y la recordamos en este navegador para la próxima vez.`,
  allSorted: 'Todo tiene categoría. También puedes cambiar cualquier movimiento en la hoja.',
  times: (n) => `${n} vez${n === 1 ? '' : 'es'}`,
  pick: 'Elige', more: (n) => `y ${n} más en la hoja.`,
  dropped: (n) => `El archivo tiene ${n} mes${n === 1 ? '' : 'es'} más antiguos; la hoja muestra los últimos 12.`,
  planLoaded: 'Cargamos tu plan en los presupuestos. Ahora agrega el CSV de tu banco.',
  sample: 'Datos de ejemplo', pasted: 'Texto pegado', filesWord: (n) => (n === 1 ? '1 archivo' : `${n} archivos`),
  saved: (f) => `Listo: se descargó ${f}. Ábrelo en Google Sheets (Archivo > Importar) o en Excel.`,
  reset: '¿Olvidar las categorías que elegiste?',
} : {
  read: (n, files, skipped) => `Read ${n} transactions from ${files}${skipped ? `; skipped ${skipped} lines we couldn't read` : ''}.`,
  dupes: (n) => ` Removed ${n} duplicates.`,
  fileErr: (e) => `${e}. Check it's the CSV download, not a PDF statement.`,
  pasteErr: (e) => `${e}. Copy whole rows: date, description and amount.`,
  none: 'No transactions found. Try another file.',
  stats: ['Months', 'Money in per month (average)', 'Spending per month (average)', 'Left over per month (average)'],
  sortTitle: "Sort the ones we didn't recognise",
  sortLede: (n) => `${n} merchant${n === 1 ? '' : 's'} ended up in Other. Pick a category and we'll remember it in this browser next time.`,
  allSorted: 'Everything has a category. You can still change any transaction in the sheet.',
  times: (n) => `${n} time${n === 1 ? '' : 's'}`,
  pick: 'Pick one', more: (n) => `and ${n} more in the sheet.`,
  dropped: (n) => `Your file has ${n} older month${n === 1 ? '' : 's'}; the sheet shows the latest 12.`,
  planLoaded: 'Your plan is loaded as the budgets. Now add your bank CSV.',
  sample: 'Sample data', pasted: 'Pasted text', filesWord: (n) => (n === 1 ? '1 file' : `${n} files`),
  saved: (f) => `Done: ${f} downloaded. Open it in Google Sheets (File > Import) or Excel.`,
  reset: 'Forget the categories you picked?',
};

const KEY = 'mms-dashboard-rules-v1';
let overrides = {};
try { overrides = JSON.parse(store.get(KEY) || '{}') || {}; } catch { overrides = {}; }
const budgets = {};
let txs = [];
let dash = null;

function sampleCsv() {
  const rows = ['Date,Description,Amount'];
  const d = new Date();
  const at = (m, day) => { const x = new Date(d.getFullYear(), d.getMonth() - m, day); return `${x.getMonth() + 1}/${x.getDate()}/${x.getFullYear()}`; };
  for (let m = 3; m >= 1; m--) {
    rows.push(`${at(m, 1)},PAYROLL DIRECT DEP ACME CO,2650.00`, `${at(m, 15)},PAYROLL DIRECT DEP ACME CO,2650.00`);
    rows.push(`${at(m, 2)},PARKVIEW APTS RENT PMT,-1450.00`, `${at(m, 3)},NETFLIX.COM 866-579-7172 CA,-17.99`, `${at(m, 9)},SPOTIFY USA,-11.99`);
    rows.push(`${at(m, 6)},VERIZON WIRELESS PAYMENT,-85.00`, `${at(m, 12)},DUKE ENERGY,-${(96 + m * 7).toFixed(2)}`, `${at(m, 20)},GEICO AUTO,-128.00`);
    [4, 11, 18, 25].forEach((day, i) => rows.push(`${at(m, day)},KROGER #555,-${(62 + ((m * 4 + i) * 17) % 60).toFixed(2)}`));
    [7, 21].forEach((day) => rows.push(`${at(m, day)},SHELL OIL 57442,-${(38 + m * 3).toFixed(2)}`));
    [5, 10, 16, 23].forEach((day, i) => rows.push(`${at(m, day)},${['CHIPOTLE 1234', 'STARBUCKS #882', 'DOORDASH*TACOS', 'MCDONALD\'S F123'][i]},-${(9 + i * 6 + m).toFixed(2)}`));
    rows.push(`${at(m, 8)},AMAZON MKTPL*AB12C,-${(34 + m * 11).toFixed(2)}`, `${at(m, 17)},CVS/PHARMACY #0441,-18.40`);
    rows.push(`${at(m, 16)},ONLINE TRANSFER TO SAVINGS,-300.00`, `${at(m, 26)},CHASE CREDIT CRD AUTOPAY,-420.00`);
    rows.push(`${at(m, 19)},SQ *LUPITAS NAILS,-35.00`);
  }
  rows.push(`${at(2, 14)},MAPLE STREET VET CLINIC,-140.00`);
  return rows.join('\n');
}

function load(results, label) {
  const msg = label === T.pasted ? '#paste-msg' : '#file-msg';
  $('#file-msg').textContent = ''; $('#paste-msg').textContent = '';
  const ok = results.filter((r) => !r.error);
  if (!ok.length) { $(msg).textContent = label === T.pasted ? T.pasteErr(results[0].error) : T.fileErr(results[0].error); return; }
  const seen = new Set(); let dupes = 0; const all = [];
  for (const r of ok) for (const t of r.transactions) { const k = `${t.date}|${t.amount}|${t.note}`; if (seen.has(k)) { dupes++; continue; } seen.add(k); all.push(t); }
  if (!all.length) { $(msg).textContent = T.none; return; }
  txs = all;
  $(msg).textContent = T.read(all.length, label, ok.reduce((s, r) => s + (r.skipped || 0), 0)) + (dupes ? T.dupes(dupes) : '');
  render();
  $('#results').hidden = false;
  $('#results').scrollIntoView({ behavior: 'smooth', block: 'start' });
}

const options = (sel) => `<option value="">${esc(T.pick)}</option>${CATEGORIES.filter((c) => c.key !== 'other').map((c) => `<option value="${c.key}"${c.key === sel ? ' selected' : ''}>${esc(catName(c.key, lang))}</option>`).join('')}`;

function render() {
  dash = buildDashboard(txs, { overrides });
  const M = dash.months;
  const avg = (k) => M.reduce((s, m) => s + dash.totals[m][k], 0) / (M.length || 1);
  $('#stats').innerHTML = [M.length, money(avg('income')), money(avg('spend')), money(avg('left'))]
    .map((v, i) => `<div class="stat"><span>${esc(T.stats[i])}</span><b${i === 3 && avg('left') < 0 ? ' class="neg"' : ''}>${v}</b></div>`).join('');
  const used = CATEGORIES.filter((c) => c.group !== 'income' && M.some((m) => dash.byCat[c.key][m] !== 0));
  const line = (name, vals, cls = '') => `<tr${cls ? ` class="${cls}"` : ''}><th scope="row">${esc(name)}</th>${vals.map((v) => `<td class="num">${money(v)}</td>`).join('')}</tr>`;
  $('#summary').innerHTML = `<table class="plan dash-table"><caption class="sr">${esc(L.summary)}</caption><thead><tr><th scope="col">${esc(L.category)}</th>${M.map((m) => `<th scope="col" class="num">${esc(monthName(m))}</th>`).join('')}</tr></thead><tbody>
    ${line(L.income, M.map((m) => dash.totals[m].income), 'in')}
    ${used.filter((c) => c.group === 'spend').map((c) => line(catName(c.key, lang), M.map((m) => dash.byCat[c.key][m]))).join('')}
    ${line(L.totalSpend, M.map((m) => dash.totals[m].spend), 'tot')}
    ${line(L.saved, M.map((m) => dash.totals[m].save))}
    ${line(L.left, M.map((m) => dash.totals[m].left), 'tot')}
    ${used.some((c) => c.key === 'transfers') ? line(`${catName('transfers', lang)} (${L.notCounted.toLowerCase()})`, M.map((m) => dash.byCat.transfers[m]), 'muted') : ''}
  </tbody></table>`;
  $('#dropped').textContent = dash.droppedMonths ? T.dropped(dash.droppedMonths) : '';

  const u = dash.uncategorized;
  const shown = u.slice(0, 15);
  $('#sort').innerHTML = `<h2>${esc(T.sortTitle)}</h2>${u.length ? `<p class="tiny">${esc(T.sortLede(u.length))}</p>
    <ul class="sort-list">${shown.map((o, i) => `<li><label for="pick-${i}"><b>${esc(o.sample)}</b><small>${esc(T.times(o.count))} · ${money(Math.abs(o.total), 2)}</small></label>
      <select id="pick-${i}" data-merchant="${esc(o.merchant)}">${options(overrides[o.merchant])}</select></li>`).join('')}</ul>
    ${u.length > shown.length ? `<p class="tiny">${esc(T.more(u.length - shown.length))}</p>` : ''}` : `<p class="tiny">${esc(T.allSorted)}</p>`}
    ${Object.keys(overrides).length ? `<button type="button" id="forget" class="link">${es ? 'Olvidar mis categorías' : 'Forget my categories'}</button>` : ''}`;
}

$('#results').addEventListener('change', (e) => {
  const m = e.target.dataset?.merchant;
  if (m !== undefined) {
    if (e.target.value) overrides[m] = e.target.value; else delete overrides[m];
    store.set(KEY, JSON.stringify(overrides));
    const id = e.target.id;
    render();
    // Keep focus near where the person was working.
    (document.getElementById(id) || $('#sort select') || $('#download')).focus();
  }
  const b = e.target.dataset?.budget;
  if (b) { const v = Number(e.target.value); if (Number.isFinite(v) && v > 0) budgets[b] = v; else delete budgets[b]; }
});
$('#results').addEventListener('click', (e) => {
  if (e.target.id === 'forget' && confirm(T.reset)) { overrides = {}; store.set(KEY, '{}'); render(); $('#download').focus(); }
});

$('#download').addEventListener('click', () => {
  if (!dash) return;
  // Net worth from the net worth tracker on this site, if this browser has one, becomes its own tab.
  const nw = loadSheet(store.get('mms-networth-v1'));
  const extra = nw.items.length || nw.snapshots.length ? [netWorthSheet(nw, { lang })] : [];
  const bytes = buildXlsx(workbookSheets(dash, { lang, made: today, budgets, extra }), { title: L.title });
  const name = `${L.file}-${dash.months[0]}-to-${dash.months.at(-1)}.xlsx`.replace('-to-', es ? '-a-' : '-to-');
  const a = document.createElement('a');
  a.href = URL.createObjectURL(new Blob([bytes], { type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' }));
  a.download = name;
  document.body.append(a); a.click(); a.remove();
  setTimeout(() => URL.revokeObjectURL(a.href), 2000);
  $('#saved').textContent = T.saved(name);
});

async function readFiles(list) {
  const files = [...(list || [])].filter(Boolean);
  if (!files.length) return;
  const texts = await Promise.all(files.map((f) => f.text()));
  // A budget plan CSV from the paycheck planner fills in the budgets instead of being read as transactions.
  const plans = texts.map(parsePlanCsv).filter(Boolean);
  for (const plan of plans) setBudgets(plan);
  const banks = texts.filter((t) => !parsePlanCsv(t));
  if (!banks.length) { $('#file-msg').textContent = T.planLoaded; return; }
  const results = banks.map((text) => { const r = importBankCsv(text); return r.error ? parseStatement(text, { today }) : r; });
  load(results, T.filesWord(banks.length));
}
$('#file').addEventListener('change', (e) => readFiles(e.target.files));
const drop = $('#drop');
['dragenter', 'dragover'].forEach((t) => drop.addEventListener(t, (e) => { e.preventDefault(); drop.classList.add('over'); }));
['dragleave', 'drop'].forEach((t) => drop.addEventListener(t, (e) => { e.preventDefault(); drop.classList.remove('over'); }));
drop.addEventListener('drop', (e) => readFiles(e.dataTransfer.files));
$('#sample').addEventListener('click', () => load([importBankCsv(sampleCsv())], T.sample));
$('#paste-form').addEventListener('submit', (ev) => { ev.preventDefault(); load([parseStatement($('#paste').value, { today })], T.pasted); });

// Budget inputs for the spreadsheet's Budget column (optional).
$('#budgets').innerHTML = CATEGORIES.filter((c) => (c.group === 'spend' && c.key !== 'other') || c.group === 'save')
  .map((c) => `<label>${esc(catName(c.key, lang))}<input type="number" min="0" step="1" inputmode="decimal" data-budget="${c.key}" placeholder="$"></label>`).join('');
function setBudgets(plan) {
  for (const [k, v] of Object.entries(plan || {})) {
    const input = document.querySelector(`[data-budget="${k}"]`);
    if (input && Number(v) > 0) { input.value = v; budgets[k] = Number(v); }
  }
}
// A plan made in the paycheck planner on this site fills in the budgets.
try { setBudgets(JSON.parse(store.get(PLAN_STORE) || '{}')?.amounts); } catch { /* no plan */ }

const p = config.sheetTemplate;
if (p && live(p.url)) {
  $('#upsell').innerHTML = `<h3>${esc(es ? p.nameEs : p.name)} (${esc(p.price)})</h3><p>${esc(es ? p.pitchEs : p.pitch)}</p><a class="btn small" href="${esc(p.url)}">${es ? 'Ver la plantilla' : 'Get the template'}</a>`;
  $('#upsell').hidden = false;
}
initTracking({ config, app: 'budget', page: es ? 'tablero-dinero' : 'money-dashboard' });
