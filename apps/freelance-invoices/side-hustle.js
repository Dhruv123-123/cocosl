// Side hustle profit page (side-hustle.html). Logic in lib/sidehustle.js.
import config from './config.js';
import { initTracking } from './lib/track.js';
import * as S from './lib/sidehustle.js';

const $ = (s) => document.querySelector(s);
const money = (n) => (Number(n) || 0).toLocaleString('en-US', { style: 'currency', currency: 'USD' });
const esc = (s) => String(s ?? '').replace(/[&<>"']/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' })[c]);
const store = {
  get(k) { try { return localStorage.getItem(k); } catch { return null; } },
  set(k, v) { try { localStorage.setItem(k, v); } catch { /* private mode */ } },
};
const KEY = '1099-side-hustle-v1';
const form = $('#hustle');
const KIND_FIELDS = ['gross', 'hours', 'miles', 'orders', 'listings', 'feePct', 'perOrder', 'perListing', 'goods', 'shipping', 'other'];
const FEE_NOTES = {
  driver: 'Enter what the app paid you, after its cut, plus tips.',
  etsy: 'Etsy (US): 6.5% transaction fee plus 3% payment processing, $0.25 per order and $0.20 per listing. Offsite Ads add 12% to 15% on orders they bring in.',
  ebay: 'eBay: about 13.6% of the total plus $0.40 per order for most categories. Some categories and promoted listings cost more, so check yours.',
  poshmark: 'Poshmark: 20% on sales of $15 or more ($2.95 flat under $15). The buyer pays shipping.',
  other: 'Add your platform\'s fee, if any.',
};

$('#kind').innerHTML = Object.entries(S.KINDS).map(([k, v]) => `<option value="${k}">${esc(v.label)}</option>`).join('');
$('#bracket').innerHTML = S.BRACKETS.map((b) => `<option value="${b}">${b}%${b === 12 ? ' (most common)' : ''}</option>`).join('');

function preset(kind) {
  const p = S.KINDS[kind];
  for (const k of KIND_FIELDS) form[k].value = p[k];
}

let saved = {};
try { saved = JSON.parse(store.get(KEY)) || {}; } catch { /* first visit */ }
form.kind.value = S.KINDS[saved.kind] ? saved.kind : 'driver';
preset(form.kind.value);
form.carCost.value = S.MILEAGE_RATE;
form.weeks.value = 48;
form.bracket.value = '12';
for (const [k, v] of Object.entries(saved)) if (form[k] && v !== '') form[k].value = v;

function render() {
  const values = Object.fromEntries(new FormData(form));
  store.set(KEY, JSON.stringify(values));
  const kind = values.kind;
  const seller = kind !== 'driver';
  for (const el of form.querySelectorAll('.seller')) el.hidden = !seller;
  for (const el of form.querySelectorAll('.etsy')) el.hidden = kind !== 'etsy';
  form.querySelector('.t-gross').textContent = kind === 'driver' ? 'Earnings in a week, after the app\'s cut, with tips ($)' : 'Sales in a week, including shipping charged ($)';
  $('#fee-note').textContent = FEE_NOTES[kind];

  const r = S.profit(values);
  const per = r.hourlyAfterTax;
  $('#result').innerHTML = `
    <p class="big-num">${per === null ? '—' : money(per)} <small>an hour, after costs and taxes</small></p>
    <p>${r.hourly !== null ? `That's ${money(r.hourly)} an hour before tax. ` : 'Add your hours to see your hourly rate. '}You keep about <b>${Math.max(0, Math.round(r.keepPerDollar * 100))}¢ of every dollar</b> you bring in.</p>
    <table class="plan sh-table"><tbody>
      <tr><td>${seller ? 'Sales' : 'Earnings'}</td><td class="num">${money(r.input.gross)}</td></tr>
      ${r.fees ? `<tr><td>Platform fees</td><td class="num neg">−${money(r.fees)}</td></tr>` : ''}
      ${r.costs ? `<tr><td>Inventory, shipping and other costs</td><td class="num neg">−${money(r.costs)}</td></tr>` : ''}
      ${r.car ? `<tr><td>Driving (${r.input.miles} miles)</td><td class="num neg">−${money(r.car)}</td></tr>` : ''}
      <tr><td><b>Profit before tax</b></td><td class="num"><b>${money(r.cashProfit)}</b></td></tr>
      <tr><td>Taxes to set aside</td><td class="num neg">−${money(r.taxWeek)}</td></tr>
      <tr><td><b>What you keep this week</b></td><td class="num"><b>${money(r.keepWeek)}</b></td></tr>
    </tbody></table>
    <h3>Over a year (${r.input.weeks} weeks)</h3>
    <ul class="plain-list">
      <li>${seller ? 'Sales' : 'Earnings'}: <b>${money(r.year.gross)}</b></li>
      <li>Self-employment tax: <b>${money(r.year.se)}</b></li>
      <li>Federal income tax at ${r.input.bracket}%: <b>${money(r.year.incomeTax)}</b>${r.input.stateRate ? ` · State: <b>${money(r.year.stateTax)}</b>` : ''}</li>
      <li>You keep: <b>${money(r.year.keep)}</b></li>
    </ul>`;
  $('#tips').innerHTML = r.tips.map((t) => `<li class="warn info">${esc(t)}</li>`).join('');
}

form.addEventListener('input', render);
form.kind.addEventListener('change', () => { preset(form.kind.value); render(); });
form.addEventListener('submit', (e) => e.preventDefault());
render();
initTracking({ config, app: 'freelance-invoices', page: 'side-hustle' });
