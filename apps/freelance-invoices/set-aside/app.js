// 1099 Tax Set-Aside app (set-aside/). Math in ../lib/setaside.js; data stays in localStorage on this device.
import config from '../config.js';
import { initTracking } from '../lib/track.js';
import * as S from '../lib/setaside.js';

const $ = (s) => document.querySelector(s);
const money = (n, d = 2) => (Number(n) || 0).toLocaleString('en-US', { style: 'currency', currency: 'USD', minimumFractionDigits: d, maximumFractionDigits: d });
const esc = (s) => String(s ?? '').replace(/[&<>"']/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' })[c]);
const pretty = (iso) => new Date(`${iso}T12:00:00`).toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' });
const localToday = () => { const d = new Date(); return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-${String(d.getDate()).padStart(2, '0')}`; };
const KEY = '1099-set-aside-v1';
const today = localToday();

let st = { payments: [], paid: {}, settings: { bracket: 12, stateRate: '', costsPct: 10, override: '', lastYearTax: '', highIncome: false } };
try { const s = JSON.parse(localStorage.getItem(KEY) || '{}'); st = { ...st, ...s, settings: { ...st.settings, ...(s.settings || {}) } }; } catch { /* first visit or private mode */ }
const save = () => { try { localStorage.setItem(KEY, JSON.stringify(st)); } catch { /* private mode */ } };

const settingsForm = $('#settings');
settingsForm.bracket.innerHTML = S.BRACKETS.map((b) => `<option value="${b}">${b}%${b === 12 ? ' (most common)' : ''}</option>`).join('');
for (const [k, v] of Object.entries(st.settings)) { const el = settingsForm[k]; if (!el) continue; if (el.type === 'checkbox') el.checked = !!v; else el.value = v; }
const yearSel = $('#year');
const years = Object.keys(S.QUARTERS);
let year = years.includes(today.slice(0, 4)) ? today.slice(0, 4) : years.at(-1);
yearSel.innerHTML = years.map((y) => `<option${y === year ? ' selected' : ''}>${y}</option>`).join('');
$('#paid').date.value = today;

function currentPct() {
  const o = st.settings.override;
  if (o !== '' && o !== undefined && Number.isFinite(Number(o))) return Math.min(60, Math.max(0, Number(o)));
  return S.rate(st.settings).pct;
}

function render() {
  const pct = currentPct();
  const r = S.rate(st.settings);
  $('#rate-sum').textContent = `${pct}% of each payment`;
  $('#rate-detail').innerHTML = st.settings.override !== '' && st.settings.override !== undefined
    ? `Using your own rate of ${pct}%. Our estimate would be ${r.pct}%.`
    : `Self-employment tax ${(r.se * 100).toFixed(1)}% + federal income tax ${(r.income * 100).toFixed(1)}% + state ${(r.state * 100).toFixed(1)}% = ${(r.exact * 100).toFixed(1)}%, rounded up to ${r.pct}%.`;

  // Widget: next due date and what's due for it.
  const nd = S.nextDue(today);
  const qsNext = nd ? S.quarters(st.payments, nd.year, st.paid) : [];
  const q = nd ? qsNext.find((x) => x.q === nd.q) : null;
  const sh = S.safeHarbor(st.settings.lastYearTax, st.settings.highIncome);
  const days = nd ? S.daysUntil(today, nd.due) : null;
  const toSend = q ? Math.max(0, Math.round((q.reserved - q.sent) * 100) / 100) : 0;
  $('#widget').innerHTML = nd ? `
    <p class="w-label">Next IRS payment</p>
    <p class="w-date"><b>${pretty(nd.due)}</b> <span class="w-days${days <= 14 ? ' soon' : ''}">${days === 0 ? 'today' : `in ${days} day${days === 1 ? '' : 's'}`}</span></p>
    <div class="w-grid">
      <div><span>Set aside for ${nd.year} Q${nd.q}</span><b>${money(q.reserved, 0)}</b></div>
      <div><span>Sent to the IRS</span><b>${money(q.sent, 0)}</b></div>
      <div><span>Left to send</span><b class="w-big">${money(toSend, 0)}</b></div>
    </div>
    ${sh ? `<p class="tiny">Safe harbor: paying ${money(sh.quarter, 0)} each quarter (${money(sh.year, 0)} a year) avoids the underpayment penalty.${sh.quarter > q.reserved ? ' That\'s more than you\'ve set aside this quarter.' : ''}</p>` : ''}
    <p class="tiny">Income from ${pretty(nd.from)} to ${pretty(nd.to)} counts toward this payment.</p>`
    : '<p>Due dates after 2027 will be added when the IRS publishes them.</p>';

  // Quarters table.
  const qs = S.quarters(st.payments, year, st.paid);
  const tot = S.yearTotals(qs);
  $('#quarters').innerHTML = `<div class="table-scroll" tabindex="0" role="region" aria-label="Quarters for ${year}"><table class="plan qtable"><thead><tr><th>Quarter</th><th>Due</th><th>Income</th><th>Set aside</th><th>Sent</th></tr></thead><tbody>
    ${qs.map((x) => `<tr${nd && nd.year === Number(year) && nd.q === x.q ? ' class="is-now"' : ''}><td>Q${x.q}</td><td>${pretty(x.due).replace(/, \d{4}$/, '')}${x.due.slice(0, 4) !== year ? ` ${x.due.slice(0, 4)}` : ''}</td><td>${money(x.income, 0)}</td><td>${money(x.reserved, 0)}</td>
      <td><label class="sr" for="sent-${x.key}">Sent to the IRS for Q${x.q}</label><input id="sent-${x.key}" data-sent="${x.key}" inputmode="decimal" value="${st.paid[x.key] ?? ''}" placeholder="0"></td></tr>`).join('')}
    <tr class="total"><td colspan="2"><b>Year</b></td><td><b>${money(tot.income, 0)}</b></td><td><b>${money(tot.reserved, 0)}</b></td><td><b>${money(tot.sent, 0)}</b></td></tr></tbody></table></div>`;

  // Payments list.
  const mine = st.payments.filter((p) => p.date.startsWith(year)).sort((a, b) => b.date.localeCompare(a.date));
  $('#list').innerHTML = mine.length ? mine.slice(0, 100).map((p) => `<li><span class="d">${esc(p.date.slice(5))}</span><span class="n">${money(p.amount)}${p.client ? `<small>${esc(p.client)}</small>` : ''}</span><b>${money(S.setAside(p.amount, p.pct))}<small>${p.pct}% set aside</small></b><button type="button" class="x" data-del="${p.id}" aria-label="Delete ${money(p.amount)} payment">✕</button></li>`).join('')
    : '<li class="empty">No payments logged for this year yet.</li>';
}

$('#paid').addEventListener('submit', (e) => {
  e.preventDefault();
  const f = e.target;
  const amount = Number(String(f.amount.value).replace(/[$,\s]/g, ''));
  if (!Number.isFinite(amount) || amount <= 0) { $('#move').textContent = 'Enter the amount you were paid, like 1500.'; f.amount.focus(); return; }
  const pct = currentPct();
  const p = { id: Date.now().toString(36), date: f.date.value || today, amount, client: f.client.value.trim(), pct };
  st.payments.push(p);
  save();
  const q = S.quarterOf(p.date);
  $('#move').innerHTML = `Move <b>${money(S.setAside(amount, pct))}</b> to your tax savings now (${pct}%). You keep ${money(amount - S.setAside(amount, pct))}.${q ? ` It counts toward the payment due ${pretty(q.due)}.` : ''}`;
  f.amount.value = ''; f.client.value = '';
  render();
});
$('#quarters').addEventListener('change', (e) => {
  const k = e.target.dataset.sent;
  if (!k) return;
  const v = Number(String(e.target.value).replace(/[$,\s]/g, ''));
  if (e.target.value.trim() === '' || !Number.isFinite(v)) delete st.paid[k]; else st.paid[k] = Math.max(0, v);
  // Re-render after the blur that fired this change has finished, so the table isn't swapped out mid-event.
  save(); setTimeout(render, 0);
});
$('#list').addEventListener('click', (e) => {
  const b = e.target.closest('[data-del]');
  if (!b) return;
  st.payments = st.payments.filter((p) => p.id !== b.dataset.del);
  save(); render();
});
settingsForm.addEventListener('input', () => {
  for (const el of settingsForm.elements) if (el.name) st.settings[el.name] = el.type === 'checkbox' ? el.checked : el.value;
  save(); render();
});
settingsForm.addEventListener('submit', (e) => e.preventDefault());
yearSel.addEventListener('change', () => { year = yearSel.value; render(); });
$('#csv').addEventListener('click', () => {
  const cell = (v) => { const s = String(v ?? ''); return /[",\n]/.test(s) || /^[=+\-@]/.test(s) ? `"${(/^[=+\-@]/.test(s) ? `'${s}` : s).replace(/"/g, '""')}"` : s; };
  const rows = [['Date', 'Client', 'Amount', 'Set-aside %', 'Set aside'], ...st.payments.filter((p) => p.date.startsWith(year)).map((p) => [p.date, p.client, p.amount.toFixed(2), p.pct, S.setAside(p.amount, p.pct).toFixed(2)])];
  const a = document.createElement('a');
  a.href = URL.createObjectURL(new Blob([rows.map((r) => r.map(cell).join(',')).join('\r\n')], { type: 'text/csv' }));
  a.download = `tax-set-aside-${year}.csv`;
  document.body.append(a); a.click(); a.remove();
});

// Install and offline.
let deferred = null;
window.addEventListener('beforeinstallprompt', (e) => { e.preventDefault(); deferred = e; $('#install').hidden = false; });
$('#install').addEventListener('click', async () => { if (!deferred) return; deferred.prompt(); await deferred.userChoice; deferred = null; $('#install').hidden = true; });
if ('serviceWorker' in navigator) navigator.serviceWorker.register('sw.js').catch(() => {});
if (new URLSearchParams(location.search).get('add')) $('#amount').focus();

for (const a of document.querySelectorAll('[data-site]')) a.href = config.siteUrl;
render();
initTracking({ config, app: 'freelance-invoices', page: 'set-aside' });
