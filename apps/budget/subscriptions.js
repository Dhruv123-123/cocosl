import config from './config.js';
import { initTracking } from './lib/track.js';
import { importBankCsv } from './lib/budget.js';
import { findRecurring } from './lib/recurring.js';
import { parseStatement } from './lib/statement.js';
import { submitSignup } from './lib/optin.js';
import { SERVICES, GROUPS, PRICES_CHECKED, totals, guessLine, matchService, storeFor, STORE_HELP, yearlyOf } from './lib/subs.js';
import { cardModel, shareCard } from './lib/sharecard.js';

const $ = (s) => document.querySelector(s);
const esc = (s) => String(s).replace(/[&<>"']/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' })[c]);
const money = (n) => (Number(n) || 0).toLocaleString('en-US', { style: 'currency', currency: 'USD' });
const live = (u) => typeof u === 'string' && /^https:\/\//.test(u) && !/REPLACE_ME/i.test(u);
const today = new Date().toISOString().slice(0, 10);
const KEY = 'mms-subs-audit-v1';
const address = () => `${location.host}${location.pathname}`;

// ---------- Share card (only the total and the count go on it, never names) ----------
function shareBlock(id) {
  return `<div class="row share-row" style="margin-top:12px"><button class="btn small" type="button" data-share="${id}">Share my result</button>
    <label class="pick" style="font-size:14px"><input type="checkbox" data-hide="${id}"> Hide my total</label><span class="tiny" data-share-msg="${id}" role="status"></span></div>
    <p class="tiny">Makes a picture with your yearly total and how many subscriptions. No names, no bank details.</p>`;
}
const shareData = {};
document.addEventListener('click', async (ev) => {
  const b = ev.target.closest('[data-share]');
  if (!b) return;
  const id = b.dataset.share;
  const d = shareData[id];
  if (!d) return;
  const hide = document.querySelector(`[data-hide="${id}"]`)?.checked;
  b.disabled = true;
  try {
    const how = await shareCard(cardModel('subs', { yearly: d.yearly, count: d.count, showTotal: !hide }, address()), { filename: 'my-subscriptions.png', title: 'My subscription audit', text: 'What do your subscriptions cost a year?' });
    document.querySelector(`[data-share-msg="${id}"]`).textContent = how === 'downloaded' ? 'Saved the picture. Post it anywhere.' : how === 'shared' ? 'Shared.' : '';
    try { window.plausible?.('Share', { props: { app: 'budget', page: 'subscription-audit', how } }); } catch { /* analytics off */ }
  } catch { document.querySelector(`[data-share-msg="${id}"]`).textContent = "Couldn't make the picture in this browser."; }
  b.disabled = false;
});

function ahaHtml(t, guess) {
  const g = guessLine(guess, t.monthly);
  const gl = !g ? '' : g.kind === 'more' ? `You guessed ${money(Number(guess))} a month. It's ${money(t.monthly)}: ${g.ratio}x your guess.` : g.kind === 'less' ? `You guessed ${money(Number(guess))} a month. It's ${money(t.monthly)}, less than you thought.` : `You guessed ${money(Number(guess))} a month and it's ${money(t.monthly)}. Close!`;
  return `<p class="tiny" style="margin:0">Your ${t.count} subscription${t.count === 1 ? '' : 's'} cost</p>
    <p class="aha-big">${money(t.yearly)} a year</p>
    ${gl ? `<p class="aha-guess">${esc(gl)}</p>` : ''}
    <div class="stats"><div class="stat"><span>A month</span><b>${money(t.monthly)}</b></div><div class="stat"><span>A day</span><b>${money(t.daily)}</b></div>
    <div class="stat"><span>Over 10 years</span><b>${money(t.tenYears)}</b><small>at today's prices</small></div><div class="stat"><span>Average subscription</span><b>${money(t.yearly / Math.max(1, t.count))}</b><small>a year</small></div></div>`;
}

function cancelHtml(sv, extra = '') {
  return `<div class="cancel-item"><h3>${esc(sv.name)}</h3><p>${esc(sv.how)}</p>${sv.store ? '<p class="tiny">Signed up in the iPhone or Android app? Cancel in Apple or Google Play instead.</p>' : ''}${extra}<p><a href="${esc(sv.url)}" target="_blank" rel="noopener">${esc(sv.name)} help page</a></p></div>`;
}

// ---------- Quick audit ----------
let saved = {};
try { saved = JSON.parse(localStorage.getItem(KEY) || '{}') || {}; } catch { saved = {}; }
const st = { on: saved.on || {}, price: saved.price || {}, extras: Array.isArray(saved.extras) ? saved.extras : [], guess: saved.guess || '' };
const persist = () => { try { localStorage.setItem(KEY, JSON.stringify(st)); } catch { /* private mode */ } };

function drawServices() {
  $('#checked').textContent = PRICES_CHECKED;
  $('#services').innerHTML = GROUPS.map(([g, label]) => {
    const list = SERVICES.filter((x) => x.group === g);
    return `<h3>${esc(label)}</h3><div class="svc">${list.map((x) => `<div class="svc-row${st.on[x.id] ? ' on' : ''}" data-row="${x.id}">
      <label class="pick"><input type="checkbox" data-id="${x.id}"${st.on[x.id] ? ' checked' : ''}><span>${esc(x.name)}</span></label>
      <input type="number" min="0" step="0.01" inputmode="decimal" data-price="${x.id}" value="${st.price[x.id] ?? x.price}" aria-label="${esc(x.name)} price per ${x.per}"><span class="per">/${x.per === 'year' ? 'yr' : 'mo'}</span></div>`).join('')}</div>`;
  }).join('') + (st.extras.length ? `<h3>Your own</h3><div class="svc">${st.extras.map((x, i) => `<div class="svc-row on"><label class="pick"><input type="checkbox" data-extra="${i}" checked><span>${esc(x.name)}</span></label><span>${money(x.price)}</span><span class="per">/${x.per === 'year' ? 'yr' : 'mo'}</span></div>`).join('')}</div>` : '');
}

function quick() {
  const picks = SERVICES.filter((x) => st.on[x.id]).map((x) => ({ price: st.price[x.id] ?? x.price, per: x.per }));
  for (const x of st.extras) picks.push(x);
  const t = totals(picks);
  $('#aha').hidden = !t.count;
  $('#cancel').hidden = !SERVICES.some((x) => st.on[x.id]);
  if (t.count) {
    shareData.quick = t;
    if (!$('#aha-body')) $('#aha').innerHTML = `<div id="aha-body"></div>${shareBlock('quick')}`;
    $('#aha-body').innerHTML = ahaHtml(t, st.guess);
    $('#cancel-list').innerHTML = SERVICES.filter((x) => st.on[x.id]).sort((a, b) => yearlyOf(st.price[b.id] ?? b.price, b.per) - yearlyOf(st.price[a.id] ?? a.price, a.per)).map((x) => cancelHtml(x)).join('');
  }
  persist();
}

$('#services').addEventListener('change', (ev) => {
  const c = ev.target;
  if (c.type !== 'checkbox') return; // prices are handled on input; a blur 'change' would redraw under the pointer
  if (c.dataset.id) { st.on[c.dataset.id] = c.checked; c.closest('.svc-row').classList.toggle('on', c.checked); }
  if (c.dataset.extra) { st.extras.splice(Number(c.dataset.extra), 1); drawServices(); }
  quick();
});
$('#services').addEventListener('input', (ev) => {
  const c = ev.target;
  if (!c.dataset.price) return;
  st.price[c.dataset.price] = Math.max(0, Number(c.value) || 0);
  if (c.value && !st.on[c.dataset.price]) { st.on[c.dataset.price] = true; const box = document.querySelector(`[data-id="${c.dataset.price}"]`); box.checked = true; c.closest('.svc-row').classList.add('on'); }
  quick();
});
$('#guess').value = st.guess;
$('#guess').addEventListener('input', () => { st.guess = $('#guess').value; quick(); });
$('#add-form').addEventListener('submit', (ev) => {
  ev.preventDefault();
  const name = $('#add-name').value.trim().slice(0, 40);
  const price = Number($('#add-price').value);
  if (!name || !(price > 0)) { $('#add-name').focus(); return; }
  st.extras.push({ name, price, per: $('#add-per').value === 'year' ? 'year' : 'month' });
  $('#add-name').value = ''; $('#add-price').value = '';
  drawServices(); quick();
});
drawServices();
quick();

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

function render(csvText, label, parsed = importBankCsv(csvText)) {
  const { transactions, skipped, error } = parsed;
  const msg = label === 'Pasted text' ? '#paste-msg' : '#file-msg';
  if (error) { $(msg).textContent = label === 'Pasted text' ? `${error}. Copy whole rows: date, description and amount.` : `${error}. Check it's the CSV download, not a PDF statement.`; return; }
  $('#file-msg').textContent = ''; $('#paste-msg').textContent = '';
  const r = findRecurring(transactions, { today });
  $(msg).textContent = `${label}: read ${transactions.length} transactions${skipped ? `, skipped ${skipped} lines we couldn't read` : ''}.`;
  const active = r.subscriptions.filter((s) => !s.stale);
  const stale = r.subscriptions.filter((s) => s.stale);
  if (!r.subscriptions.length) {
    $('#results').innerHTML = '<h2>No repeating charges found</h2><p>Try a longer date range: we need at least two charges from the same place to spot a pattern.</p>';
    $('#results').hidden = false; return;
  }
  const row = (s) => `<tr>
    <td><label class="pick"><input type="checkbox" data-yearly="${s.yearly}"><span><b>${esc(s.name)}</b><small>${esc(s.cadence)} · ${s.count} charges · ${esc(s.confidence)}${s.priceChange ? ` · <span class="neg">up ${money(s.priceChange)}</span>` : ''}</small></span></label></td>
    <td class="num">${money(s.amount)}</td><td class="num"><b>${money(s.yearly)}</b></td><td class="tiny when">${s.stale ? 'last ' + s.lastDate : 'next ~' + s.nextDate}</td></tr>`;
  shareData.csv = { yearly: r.yearlyTotal, count: active.length };
  const matched = active.map((x) => ({ x, sv: matchService(`${x.key} ${x.name}`), store: storeFor(x.name) })).filter((m) => m.sv || m.store);
  const seen = new Set();
  const cancels = matched.filter((m) => { const k = m.sv ? m.sv.id : m.store; if (seen.has(k)) return false; seen.add(k); return true; })
    .map((m) => (m.sv ? cancelHtml(m.sv) : cancelHtml({ ...STORE_HELP[m.store], name: `${STORE_HELP[m.store].name} subscriptions`, how: STORE_HELP[m.store].how }))).join('');
  $('#results').innerHTML = `
    ${active.length ? ahaHtml(totals(active.map((x) => ({ price: x.yearly, per: 'year' }))), st.guess) + shareBlock('csv') : ''}
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
    ${cancels ? `<h3>How to cancel the ones we recognised</h3>${cancels}` : ''}
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
$('#paste-form').addEventListener('submit', (ev) => {
  ev.preventDefault();
  render('', 'Pasted text', parseStatement($('#paste').value, { today }));
});

// Email signup
const form = document.querySelector('form.signup');
const e = config.email;
if (e.provider === 'none') form.closest('section').hidden = true;
else {
  if (!['netlify', 'sender'].includes(e.provider)) { form.removeAttribute('data-netlify'); form.action = e.action || '#'; form.querySelector('input[type=email]').name = e.emailField || 'email'; }
  form.addEventListener('submit', async (ev) => {
    ev.preventDefault();
    if (form.website.value) return;
    if (!['netlify', 'sender'].includes(e.provider) && !e.action) { alert('Email signup is not connected yet: set email.action in config.js.'); return; }
    form.querySelector('button').disabled = true;
    try { e.provider === 'sender' ? await submitSignup(form, { app: 'budget' }) : await fetch(e.provider === 'netlify' ? '/' : form.action, { method: 'POST', mode: e.provider === 'netlify' ? 'same-origin' : 'no-cors', headers: { 'Content-Type': 'application/x-www-form-urlencoded' }, body: new URLSearchParams(new FormData(form)).toString() }); location.href = e.thanksUrl; }
    catch { form.submit(); }
  });
}
initTracking({ config, app: 'budget', page: 'subscription-finder' });

