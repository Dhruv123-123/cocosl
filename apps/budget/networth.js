// Net worth snapshot page (networth.html). Logic in lib/networth.js; PDF from lib/pdf.js.
import config from './config.js';
import { initTracking } from './lib/track.js';
import * as N from './lib/networth.js';
import { buildPdf } from './lib/pdf.js';
import { today as todayIs, prettyDay } from './lib/dates.js';
import { $, esc, money, store, download } from './page.js';
import { buildXlsx } from './lib/xlsx.js';

const KEY = 'mms-networth-v1';
const CKEY = 'mms-networth-costs';
let sheet = N.loadSheet(store.get(KEY));
const today = todayIs();
const form = $('#item-form');
const save = () => { if (!store.set(KEY, JSON.stringify(sheet))) $('#data-msg').textContent = 'Could not save here (private browsing?). Use "Download backup" before closing.'; };
const costs = () => Number(String($('#costs').value).replace(/[$,\s]/g, '')) || 0;

const kinds = () => { $('#f-kind').innerHTML = Object.entries(form.side.value === 'asset' ? N.ASSET_KINDS : N.DEBT_KINDS).map(([k, v]) => `<option value="${k}">${esc(v)}</option>`).join(''); };
form.side.addEventListener('change', kinds);
kinds();
$('#costs').value = store.get(CKEY) || '';
$('#site-link').href = config.siteUrl;

function rows(side) {
  const items = sheet.items.filter((i) => i.side === side);
  const map = side === 'asset' ? N.ASSET_KINDS : N.DEBT_KINDS;
  if (!items.length) return `<tr><td class="tiny">${side === 'asset' ? 'Nothing yet. Start with your checking and savings balances.' : 'No debts added. Lucky you, or add your cards and loans.'}</td></tr>`;
  return items.map((i) => `<tr data-id="${i.id}"><td>${esc(i.name)}<small class="tiny" style="display:block">${esc(map[i.kind])}</small></td>
    <td class="num"><input class="plan-in" inputmode="decimal" value="${i.value}" data-value="${i.id}" aria-label="Value of ${esc(i.name)}"></td>
    <td style="width:36px"><button class="x" data-del="${i.id}" aria-label="Remove ${esc(i.name)}">×</button></td></tr>`).join('');
}

function render() {
  const t = N.totals(sheet);
  $('#stats').innerHTML = `
    <div class="stat"><span>Net worth</span><b class="${t.net < 0 ? 'neg' : 'pos'}">${money(t.net)}</b></div>
    <div class="stat"><span>You own</span><b>${money(t.assets)}</b></div>
    <div class="stat"><span>You owe</span><b>${money(t.debts)}</b></div>
    <div class="stat"><span>Debt vs what you own</span><b>${t.debtRatio === null ? '—' : `${t.debtRatio}%`}</b></div>`;
  if (document.activeElement?.dataset?.value === undefined) { $('#assets').innerHTML = rows('asset'); $('#debts').innerHTML = rows('debt'); }
  const tr = N.trend(sheet);
  const snaps = sheet.snapshots.slice(-12);
  const max = Math.max(1, ...snaps.map((s) => Math.abs(s.net)));
  $('#trend').innerHTML = snaps.length
    ? `${tr ? `<p>Since ${prettyDay(tr.prevDate)}: <b class="${tr.sincePrev < 0 ? 'neg' : 'pos'}">${tr.sincePrev >= 0 ? '+' : ''}${money(tr.sincePrev)}</b> · since ${prettyDay(tr.firstDate)}: <b class="${tr.sinceFirst < 0 ? 'neg' : 'pos'}">${tr.sinceFirst >= 0 ? '+' : ''}${money(tr.sinceFirst)}</b></p>` : ''}
      <ul class="snaps">${snaps.map((s) => `<li><span>${prettyDay(s.date)}</span><span class="bar"><span style="width:${Math.round((Math.abs(s.net) / max) * 100)}%" class="${s.net < 0 ? 'over' : ''}"></span></span><b class="${s.net < 0 ? 'neg' : ''}">${money(s.net)}</b><button class="x" data-unsnap="${s.date}" aria-label="Delete snapshot ${prettyDay(s.date)}">×</button></li>`).join('')}</ul>`
    : '<p class="tiny">No snapshots yet. Add your accounts, then save one. Come back next month to see the change.</p>';
  $('#notes').innerHTML = N.notes(sheet, costs()).map((n) => `<li>${esc(n)}</li>`).join('');
}

form.addEventListener('submit', (e) => {
  e.preventDefault();
  try { N.addItem(sheet, Object.fromEntries(new FormData(form))); save(); form.name.value = ''; form.value.value = ''; $('#form-msg').textContent = ''; render(); }
  catch (err) { $('#form-msg').textContent = err.message; }
});
document.addEventListener('change', (e) => {
  const id = e.target.dataset?.value;
  if (!id) return;
  try { N.updateItem(sheet, id, e.target.value); save(); } catch (err) { $('#form-msg').textContent = err.message; }
  e.target.blur(); render();
});
document.addEventListener('click', (e) => {
  const d = e.target.dataset || {};
  if (d.del) { N.removeItem(sheet, d.del); save(); render(); }
  if (d.unsnap && confirm(`Delete the snapshot from ${prettyDay(d.unsnap)}?`)) { N.removeSnapshot(sheet, d.unsnap); save(); render(); }
});
$('#costs').addEventListener('input', () => { store.set(CKEY, $('#costs').value); render(); });
$('#snap').addEventListener('click', () => {
  if (!sheet.items.length) { $('#data-msg').textContent = 'Add at least one thing you own or owe first.'; return; }
  const s = N.takeSnapshot(sheet, today); save(); render();
  $('#data-msg').textContent = `Saved: ${money(s.net)} on ${prettyDay(today)}.`;
});

function pdfLines() {
  const t = N.totals(sheet);
  const lines = [
    { text: 'Net worth snapshot', size: 20, bold: true },
    { text: `${prettyDay(today)} · made with Money Made Simple`, size: 10 },
    { rule: true, gap: 6 },
    { text: 'Net worth', right: money(t.net), size: 16, bold: true, gap: 4 },
    { text: 'You own', right: money(t.assets) },
    { text: 'You owe', right: money(t.debts) },
    { text: 'What you own', size: 13, bold: true, gap: 14 }, { rule: true },
    ...sheet.items.filter((i) => i.side === 'asset').map((i) => ({ text: `${i.name} (${N.ASSET_KINDS[i.kind]})`, right: money(i.value) })),
    { text: 'What you owe', size: 13, bold: true, gap: 14 }, { rule: true },
    ...sheet.items.filter((i) => i.side === 'debt').map((i) => ({ text: `${i.name} (${N.DEBT_KINDS[i.kind]})`, right: money(i.value) })),
  ];
  if (sheet.snapshots.length) {
    lines.push({ text: 'Snapshots', size: 13, bold: true, gap: 14 }, { rule: true });
    for (const s of sheet.snapshots) lines.push({ text: prettyDay(s.date), right: money(s.net) });
  }
  const n = N.notes(sheet, costs());
  if (n.length) { lines.push({ text: 'Notes', size: 13, bold: true, gap: 14 }); for (const x of n) lines.push({ text: `- ${x}`, size: 10 }); }
  lines.push({ text: 'General information, not financial advice. Values are your own estimates.', size: 8, gap: 18 });
  return lines;
}
$('#pdf').addEventListener('click', () => {
  if (!sheet.items.length) { $('#data-msg').textContent = 'Add at least one thing you own or owe first.'; return; }
  download(`net-worth-${today}.pdf`, buildPdf(pdfLines(), { title: `Net worth snapshot ${today}` }), 'application/pdf');
});
$('#xlsx').addEventListener('click', () => download(`net-worth-${today}.xlsx`, buildXlsx([N.netWorthSheet(sheet)], { title: 'Net worth' }), 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'));
$('#csv').addEventListener('click', () => download(`net-worth-${today}.csv`, N.toCsv(sheet), 'text/csv'));
$('#backup').addEventListener('click', () => download(`net-worth-backup-${today}.json`, JSON.stringify(sheet, null, 2), 'application/json'));
$('#restore').addEventListener('change', async (e) => {
  const f = e.target.files[0]; if (!f) return;
  const next = N.loadSheet(await f.text());
  if (!confirm(`Replace what's on this device with the backup (${next.items.length} items, ${next.snapshots.length} snapshots)?`)) return;
  sheet = next; save(); render(); e.target.value = '';
});

render();
initTracking({ config, app: 'budget', page: 'net-worth' });
