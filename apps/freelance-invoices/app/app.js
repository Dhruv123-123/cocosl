// 1099 Money app (freelance-invoices/app/): home screen, quarterly estimated tax, mileage log and
// deduction checklist. One script for all four pages (body[data-page]). Logic in ../lib/ten99.js.
// Everything stays in this browser (localStorage); ../sw.js saves the pages for offline.
import { rememberAppHome } from '../lib/app-home.js';
import { mountOptin } from '../lib/optin.js';
import { estimate, normalizeTrip, mileageSummary, mileageCsv, deductionsFor, WHO, YEARS } from '../lib/ten99.js';

const $ = (s) => document.querySelector(s);
const esc = (s) => String(s ?? '').replace(/[&<>"']/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' })[c]);
const store = { get: (k) => { try { return JSON.parse(localStorage.getItem(k) || 'null'); } catch { return null; } }, set: (k, v) => { try { localStorage.setItem(k, JSON.stringify(v)); } catch { /* private mode */ } } };
const money = (n, d = 2) => (Number(n) || 0).toLocaleString('en-US', { style: 'currency', currency: 'USD', minimumFractionDigits: d, maximumFractionDigits: d });
const day = (s) => new Date(`${s}T12:00:00`).toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' });
const d0 = new Date();
const today = `${d0.getFullYear()}-${String(d0.getMonth() + 1).padStart(2, '0')}-${String(d0.getDate()).padStart(2, '0')}`;
const page = document.body.dataset.page;
const okOrigin = location.protocol === 'https:' || ['localhost', '127.0.0.1'].includes(location.hostname);

if ('serviceWorker' in navigator && okOrigin) {
  navigator.serviceWorker.register('../sw.js', { scope: '../' }).then(() => navigator.serviceWorker.ready).then(() => {
    if ($('#status')) { $('#status').classList.add('ready'); $('#status-text').textContent = 'Ready offline: every tool here works with no signal.'; }
  }).catch(() => { if ($('#status-text')) $('#status-text').textContent = 'Works online. This browser can\'t save it for offline.'; });
} else if ($('#status-text')) $('#status-text').textContent = 'Works online. This browser can\'t save it for offline.';
if (page === 'home') rememberAppHome('../', location.href.split(/[?#]/)[0]);

function home() {
  const standalone = window.matchMedia?.('(display-mode: standalone)').matches || navigator.standalone === true;
  let deferred = null;
  window.addEventListener('beforeinstallprompt', (e) => { e.preventDefault(); deferred = e; $('#install').hidden = false; });
  $('#install-btn').addEventListener('click', async () => { if (!deferred) return; deferred.prompt(); await deferred.userChoice.catch(() => null); deferred = null; $('#install').hidden = true; });
  if (!standalone && /iPhone|iPad|iPod/.test(navigator.userAgent)) { $('#install-text').textContent = 'To add it to your home screen: tap Share, then Add to Home Screen.'; $('#install-btn').hidden = true; $('#install').hidden = false; }
}

function quarterly() {
  const KEY = 'ten99-estimate-v1';
  const form = $('#est');
  const saved = store.get(KEY);
  if (saved) for (const [k, v] of Object.entries(saved)) { const el = form.elements[k]; if (!el) continue; if (el.type === 'checkbox') el.checked = !!v; else el.value = v; }
  else form.year.value = String(YEARS.find((y) => `${y + 1}-01-15` >= today) || YEARS[YEARS.length - 1]);
  const read = () => {
    const f = Object.fromEntries(new FormData(form));
    f.highIncome = form.highIncome.checked;
    return f;
  };
  const render = () => {
    const f = read();
    store.set(KEY, f);
    const e = estimate({ ...f, paid: [f.paid0, f.paid1, f.paid2, f.paid3] }, today);
    const stats = [['Total federal tax', e.federal], ['Least to pay to avoid a penalty', e.required], ['Paid so far', e.paidTotal], ['Still to pay', e.left]];
    $('#stats').innerHTML = stats.map(([l, v]) => `<div class="stat"><span>${l}</span><b>${money(v, 0)}</b></div>`).join('');
    const why = !e.profit ? 'Enter your expected profit to see your payments.'
      : e.owesNothing ? `You're likely to owe under $1,000 after withholding, so you may not need quarterly payments for ${e.year}.`
        : `${e.method === 'safe' ? 'Paying last year\'s tax' + (f.highIncome ? ' plus 10%' : '') + ' (the safe harbor) is less than 90% of this year\'s, so that\'s the minimum.' : '90% of this year\'s tax is the minimum. Add last year\'s tax to see if the safe harbor is lower.'} This year's tax: ${money(e.se, 0)} self-employment tax plus ${money(e.income, 0)} income tax.${e.state ? ` Plan about ${money(e.stateQuarter, 0)} a quarter for state tax too.` : ''}`;
    $('#summary').textContent = why;
    $('#rows').innerHTML = e.quarters.map((q) => `<tr class="${q.past ? 'past' : e.next && q.due === e.next.due ? 'next' : ''}"><td>Q${q.q}${q.paid ? `<br><small>paid ${money(q.paid, 0)}</small>` : ''}</td><td>${day(q.due)}${q.past ? ' (passed)' : ''}</td><td class="num">${money(q.even)}</td><td class="num">${q.past ? '—' : money(q.suggested)}</td></tr>`).join('');
  };
  form.addEventListener('input', render);
  form.addEventListener('submit', (e) => e.preventDefault());
  render();
}

function mileage() {
  const KEY = 'ten99-mileage-v1';
  let trips = (store.get(KEY) || []).map(normalizeTrip).filter((t) => !t.error);
  const form = $('#trip');
  form.date.value = today;
  const years = () => [...new Set([...YEARS, ...trips.map((t) => Number(t.date.slice(0, 4)))])].sort();
  let year = Number(today.slice(0, 4));
  const render = () => {
    $('#year').innerHTML = years().map((y) => `<option value="${y}"${y === year ? ' selected' : ''}>${y}</option>`).join('');
    const s = mileageSummary(trips, year);
    $('#stats').innerHTML = [['Trips', String(s.rows.length)], ['Business miles', s.miles.toLocaleString('en-US')], ['Deduction', money(s.deduction, 0)], ['Rate now', `${(s.rows.at(-1)?.rate ?? 0.76) * 100}¢ a mile`]].map(([l, v]) => `<div class="stat"><span>${l}</span><b>${v}</b></div>`).join('');
    $('#prov').hidden = !s.provisional;
    $('#rows').innerHTML = s.rows.length ? s.rows.slice().reverse().map((r) => `<tr><td>${esc(r.date)}</td><td>${esc(r.purpose)}${r.from || r.to ? `<br><small>${esc(r.from)}${r.from && r.to ? ' to ' : ''}${esc(r.to)}</small>` : ''}</td><td class="num">${r.miles}</td><td class="num">${money(r.deduction)}</td><td><button type="button" class="link" data-del="${esc(r.id)}">Remove<span class="sr-only"> trip on ${esc(r.date)}</span></button></td></tr>`).join('')
      : `<tr><td colspan="5">No trips logged for ${year} yet.</td></tr>`;
    $('#csv').disabled = !s.rows.length;
    store.set(KEY, trips);
  };
  const ERR = { date: 'Pick the date of the trip.', miles: 'Enter the miles (more than 0).', purpose: 'Say why you drove: the IRS needs a business purpose.' };
  form.addEventListener('submit', (e) => {
    e.preventDefault();
    const t = normalizeTrip(Object.fromEntries(new FormData(form)));
    if (t.error) { $('#trip-msg').textContent = ERR[t.error]; form[t.error].focus(); return; }
    trips.push(t);
    year = Number(t.date.slice(0, 4));
    $('#trip-msg').textContent = `Added ${t.miles} miles.`;
    form.miles.value = ''; form.purpose.value = ''; form.from.value = ''; form.to.value = '';
    render();
    form.miles.focus();
  });
  $('#year').addEventListener('change', (e) => { year = Number(e.target.value); render(); });
  $('#rows').addEventListener('click', (e) => {
    const id = e.target.closest('[data-del]')?.dataset.del;
    if (!id) return;
    trips = trips.filter((t) => t.id !== id);
    render();
    form.miles.focus();
  });
  $('#csv').addEventListener('click', () => {
    const blob = new Blob([mileageCsv(mileageSummary(trips, year))], { type: 'text/csv' });
    const a = Object.assign(document.createElement('a'), { href: URL.createObjectURL(blob), download: `mileage-log-${year}.csv` });
    document.body.append(a); a.click(); a.remove(); setTimeout(() => URL.revokeObjectURL(a.href), 1000);
  });
  render();
}

function deductions() {
  const KEY = 'ten99-deductions-v1';
  const st = store.get(KEY) || { who: 'all', done: {} };
  $('#who').innerHTML = [['all', 'All'], ...Object.entries(WHO).filter(([k]) => k !== 'everyone')].map(([k, v]) => `<option value="${k}"${k === st.who ? ' selected' : ''}>${v}</option>`).join('');
  const render = () => {
    const list = deductionsFor(st.who);
    $('#list').innerHTML = list.map((x) => `<li><label class="check"><input type="checkbox" data-id="${x.id}"${st.done[x.id] ? ' checked' : ''}> <b>${esc(x.t)}</b></label><p>${esc(x.d)}</p></li>`).join('');
    $('#count').textContent = `${list.filter((x) => st.done[x.id]).length} of ${list.length} ticked.`;
    store.set(KEY, st);
  };
  $('#who').addEventListener('change', (e) => { st.who = e.target.value; render(); });
  $('#list').addEventListener('change', (e) => { const id = e.target.dataset.id; if (id) { st.done[id] = e.target.checked; $('#count').textContent = `${deductionsFor(st.who).filter((x) => st.done[x.id]).length} of ${deductionsFor(st.who).length} ticked.`; store.set(KEY, st); } });
  $('#print').addEventListener('click', () => window.print());
  render();
}

({ home, quarterly, mileage, deductions })[page]?.();
if (page !== 'home') mountOptin({ app: 'freelance-invoices', page: `app-${page}` });
