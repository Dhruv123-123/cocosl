import config from './config.js';
import { importBankCsv } from './lib/budget.js';
import { findRecurring } from './lib/recurring.js';

const $ = (s) => document.querySelector(s);
const esc = (s) => String(s).replace(/[&<>"']/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' })[c]);
const money = (n) => (Number(n) || 0).toLocaleString('en-US', { style: 'currency', currency: 'USD' });
const live = (u) => typeof u === 'string' && /^https:\/\//.test(u) && !/REPLACE_ME/i.test(u);
const today = new Date().toISOString().slice(0, 10);

function sampleCsv() {
  const rows = ['Date,Description,Amount'];
  const d = new Date();
  const ago = (months, day) => { const x = new Date(d.getFullYear(), d.getMonth() - months, day); return `${x.getMonth() + 1}/${x.getDate()}/${x.getFullYear()}`; };
  for (let m = 5; m >= 0; m--) {
    rows.push(`${ago(m, 3)},NETFLIX.COM 866-579-7172 CA,-${m < 2 ? '17.99' : '15.49'}`);
    rows.push(`${ago(m, 9)},SPOTIFY USA *P${m}A9C3,-11.99`);
    rows.push(`${ago(m, 14)},PLANET FITNESS #1022,-24.99`);
    rows.push(`${ago(m, 21)},ICLOUD APPLE.COM/BILL,-2.99`);
    rows.push(`${ago(m, 1)},PAYROLL DIRECT DEP,2650.00`);
    [4, 11, 18, 25].forEach((day, i) => rows.push(`${ago(m, day)},KROGER #555,-${(38 + ((m * 4 + i) * 23) % 90).toFixed(2)}`));
    if (m < 4) rows.push(`${ago(m, 26)},UBER ONE MEMBERSHIP,-9.99`);
  }
  rows.push(`${ago(2, 16)},BEST BUY 00123,-129.99`);
  return rows.join('\n');
}

function render(csvText, label) {
  const { transactions, skipped, error } = importBankCsv(csvText);
  if (error) { $('#file-msg').textContent = error + '. Check it\'s the CSV download, not a PDF statement.'; return; }
  const r = findRecurring(transactions, { today });
  $('#file-msg').textContent = `${label}: read ${transactions.length} transactions${skipped ? `, skipped ${skipped}` : ''}.`;
  const active = r.subscriptions.filter((s) => !s.stale);
  const stale = r.subscriptions.filter((s) => s.stale);
  if (!r.subscriptions.length) {
    $('#results').innerHTML = '<h2>No repeating charges found</h2><p>Try a longer date range: we need at least two charges from the same place to spot a pattern.</p>';
    $('#results').hidden = false; return;
  }
  const row = (s) => `<tr>
    <td><label class="pick"><input type="checkbox" data-yearly="${s.yearly}"><span><b>${esc(s.name)}</b><small>${esc(s.cadence)} · ${s.count} charges · ${esc(s.confidence)}${s.priceChange ? ` · <span class="neg">up ${money(s.priceChange)}</span>` : ''}</small></span></label></td>
    <td class="num">${money(s.amount)}</td><td class="num"><b>${money(s.yearly)}</b></td><td class="tiny when">${s.stale ? 'last ' + s.lastDate : 'next ~' + s.nextDate}</td></tr>`;
  $('#results').innerHTML = `
    <div class="stats">
      <div class="stat"><span>Recurring charges</span><b>${active.length}</b></div>
      <div class="stat"><span>Per month</span><b>${money(r.monthlyTotal)}</b></div>
      <div class="stat"><span>Per year</span><b>${money(r.yearlyTotal)}</b></div>
      <div class="stat"><span>If you cancel the ticked ones</span><b id="savings" class="pos">${money(0)}</b><small>saved a year</small></div>
    </div>
    <table class="plan subs"><thead><tr><th>Charge (tick to cancel)</th><th>Each</th><th>Per year</th><th class="when">When</th></tr></thead>
    <tbody>${active.map(row).join('')}</tbody></table>
    ${stale.length ? `<h3>Probably already stopped</h3><table class="plan subs"><tbody>${stale.map(row).join('')}</tbody></table>` : ''}
    <p class="tiny">We look for charges from the same place at a regular interval with a similar amount. Bills like rent or utilities may show up too.</p>
    <div class="offer-box"><h3>Keep it from creeping back</h3><p>The free <a href="./">20-Minute Budget app</a> gives every dollar a job each month. Pro imports this same CSV and sorts it into categories automatically.</p><a class="btn small" href="./">Open the budget app</a></div>
    ${live(config.billCutKit.url) ? `<div class="offer-box"><h3>${esc(config.billCutKit.name)} (${esc(config.billCutKit.price)})</h3><p>${esc(config.billCutKit.pitch)}</p><a class="btn small" href="${esc(config.billCutKit.url)}">Get the kit</a></div>` : ''}`;
  $('#results').hidden = false;
  $('#results').addEventListener('change', () => {
    const total = [...document.querySelectorAll('[data-yearly]:checked')].reduce((s, c) => s + Number(c.dataset.yearly), 0);
    $('#savings').textContent = money(total);
  });
  $('#results').scrollIntoView({ behavior: 'smooth' });
}

async function readFile(f) { if (f) render(await f.text(), f.name); }
$('#file').addEventListener('change', (e) => readFile(e.target.files[0]));
const drop = $('#drop');
['dragenter', 'dragover'].forEach((t) => drop.addEventListener(t, (e) => { e.preventDefault(); drop.classList.add('over'); }));
['dragleave', 'drop'].forEach((t) => drop.addEventListener(t, (e) => { e.preventDefault(); drop.classList.remove('over'); }));
drop.addEventListener('drop', (e) => readFile(e.dataTransfer.files[0]));
$('#sample').addEventListener('click', () => render(sampleCsv(), 'Sample data'));

// Email signup
const form = document.querySelector('form.signup');
const e = config.email;
if (e.provider === 'none') form.closest('section').hidden = true;
else {
  if (e.provider !== 'netlify') { form.removeAttribute('data-netlify'); form.action = e.action || '#'; form.querySelector('input[type=email]').name = e.emailField || 'email'; }
  form.addEventListener('submit', async (ev) => {
    ev.preventDefault();
    if (form.website.value) return;
    if (e.provider !== 'netlify' && !e.action) { alert('Email signup is not connected yet: set email.action in config.js.'); return; }
    form.querySelector('button').disabled = true;
    try { await fetch(e.provider === 'netlify' ? '/' : form.action, { method: 'POST', mode: e.provider === 'netlify' ? 'same-origin' : 'no-cors', headers: { 'Content-Type': 'application/x-www-form-urlencoded' }, body: new URLSearchParams(new FormData(form)).toString() }); location.href = e.thanksUrl; }
    catch { form.submit(); }
  });
}
