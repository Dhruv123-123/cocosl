import config from './config.js';
import { initTracking } from './lib/track.js';
import * as Bills from './lib/bills.js';
import { importBankCsv } from './lib/budget.js';
import { findRecurring } from './lib/recurring.js';
import { buildIcs } from './lib/ics.js';
import { today as todayIs, prettyDay } from './lib/dates.js';
import { $, esc, money, live, store, currentPlan, download, upsellHtml } from './page.js';

const KEY = 'mms-bills-v1';
let data = Bills.loadBills(store.get(KEY));
const { pro, plan } = currentPlan();
const today = todayIs();
let openBill = null;

const save = () => { if (!store.set(KEY, JSON.stringify(data))) $('#bill-msg').textContent = 'Could not save here (private browsing?). Use "Download my data" before closing.'; };

$('#plan-badge').textContent = pro ? 'Pro' : 'Free · Upgrade';
$('#plan-badge').classList.toggle('pro', pro);
$('#b-kind').innerHTML = Object.entries(Bills.KINDS).map(([k, v]) => `<option value="${k}">${esc(v)}</option>`).join('');

const STATUS = {
  ended: (s) => `<span class="pill bad">Promo ended ${-s.days} day${s.days === -1 ? '' : 's'} ago: call now</span>`,
  soon: (s) => `<span class="pill warn">Promo ends in ${s.days} day${s.days === 1 ? '' : 's'}: call this week</span>`,
  ok: (s) => `<span class="pill">Promo ends in ${s.days} days</span>`,
  none: () => '<span class="pill muted">No promo date</span>',
};

function scriptHtml(kind) {
  const s = Bills.SCRIPTS[kind];
  return `<p><b>Who to ask for:</b> ${esc(s.who)}</p><ol class="script">${s.lines.map((l) => `<li>${esc(l)}</li>`).join('')}</ol><p class="tiny">${esc(s.close)}</p>`;
}

function render() {
  const s = Bills.summarizeBills(data, today);
  $('#stats').innerHTML = `
    <div class="stat"><span>Bills a month</span><b>${money(s.monthly)}</b><small>${money(s.yearly)} a year</small></div>
    <div class="stat"><span>Saved this year</span><b class="pos">${money(s.savedThisYear)}</b><small>${money(s.savedTotal)} from all calls</small></div>
    <div class="stat"><span>Calls logged</span><b>${s.calls}</b></div>
    <div class="stat"><span>Need a call</span><b class="${s.needsCall ? 'neg' : ''}">${s.needsCall}</b><small>Promo ended or ending within 30 days</small></div>`;
  $('#bills').innerHTML = s.rows.length ? s.rows.map((b) => `
    <article class="bill" data-id="${b.id}">
      <div class="bill-head">
        <div><b>${esc(b.name)}</b> <span class="tiny">${esc(Bills.KINDS[b.kind])}</span><br>${STATUS[b.status.code](b.status)}${b.promoEnd ? ` <span class="tiny">${prettyDay(b.promoEnd)}</span>` : ''}</div>
        <div class="bill-price"><b>${money(b.monthly)}</b><small>a month</small></div>
      </div>
      <details${openBill === b.id ? ' open' : ''}><summary>Call script</summary>${scriptHtml(b.kind)}</details>
      <details class="log"${openBill === b.id ? ' open' : ''}><summary>Log a call</summary>
        <form class="tx-form call-form" data-bill="${b.id}">
          <label>Date <input name="date" type="date" value="${today}" required></label>
          <label>New monthly price ($) <input name="newMonthly" type="number" min="0" step="any" inputmode="decimal" placeholder="${b.monthly}"></label>
          <label>For how many months <input name="months" type="number" min="0" max="60" step="1" value="12"></label>
          <label>What happened <input name="outcome" maxlength="300" placeholder="Retention: $15 off for 12 months"></label>
          <button class="btn small">Save call</button>
        </form>
        <p class="tiny">Leave the price blank if nothing changed. It still counts: try again in a week.</p>
      </details>
      ${b.calls.length ? `<ul class="calls">${b.calls.map((c) => `<li><span class="d">${prettyDay(c.date)}</span> ${esc(c.outcome || 'Call')} ${Bills.callSavings(c) ? `<b class="pos">saves ${money(Bills.callSavings(c))}</b>` : ''}</li>`).join('')}</ul>` : ''}
      <button class="x del" data-del="${b.id}" aria-label="Delete ${esc(b.name)}">Delete</button>
    </article>`).join('')
    : '<p class="tiny">No bills yet. Start with the biggest one: internet, phone or car insurance usually have the most room.</p>';
}

function tryAdd(values) {
  try {
    Bills.addBill(data, values, { max: plan.bills });
    save();
    return true;
  } catch (err) {
    $('#bill-msg').innerHTML = err instanceof Bills.LimitError ? upsellHtml(err.message) : esc(err.message);
    return false;
  }
}

$('#bill-form').addEventListener('submit', (e) => {
  e.preventDefault();
  $('#bill-msg').textContent = '';
  if (tryAdd({ name: $('#b-name').value, kind: $('#b-kind').value, monthly: $('#b-monthly').value, promoEnd: $('#b-end').value })) {
    e.target.reset();
    render();
  }
});

$('#bills').addEventListener('submit', (e) => {
  const f = e.target.closest('.call-form');
  if (!f) return;
  e.preventDefault();
  try {
    Bills.logCall(data, f.dataset.bill, Object.fromEntries(new FormData(f)));
    openBill = null;
    save();
    render();
  } catch (err) { alert(err.message); }
});

$('#bills').addEventListener('click', (e) => {
  const del = e.target.closest('[data-del]');
  if (del && confirm('Delete this bill and its call log?')) { Bills.removeBill(data, del.dataset.del); save(); render(); }
});

// Find bills in a bank CSV with the subscription finder's logic.
function showFound(csv) {
  const { transactions, error } = importBankCsv(csv);
  if (error) { $('#found').innerHTML = `<p class="tiny">${esc(error)}</p>`; return; }
  const found = Bills.billsFromRecurring(findRecurring(transactions, { today }).subscriptions, data.bills);
  $('#found').innerHTML = found.length
    ? `<form id="found-form"><p class="tiny">Monthly charges we found. Tick the ones to track:</p>${found.map((b, i) => `<label class="pick"><input type="checkbox" name="pick" value="${i}" checked> <span>${esc(b.name)} <small>${money(b.monthly)} a month · ${esc(Bills.KINDS[b.kind])}</small></span></label>`).join('')}<button class="btn small">Add these</button></form>`
    : '<p class="tiny">No new monthly bills found in that file.</p>';
  $('#found-form')?.addEventListener('submit', (e) => {
    e.preventDefault();
    for (const i of new FormData(e.target).getAll('pick')) if (!tryAdd(found[Number(i)])) break;
    $('#found').innerHTML = '';
    render();
  });
}
$('#csv').addEventListener('change', async (e) => { const f = e.target.files[0]; if (f) showFound(await f.text()); });
$('#sample').addEventListener('click', () => {
  const rows = ['Date,Description,Amount'];
  const now = new Date();
  for (let m = 5; m >= 0; m--) {
    const day = (d) => { const x = new Date(now.getFullYear(), now.getMonth() - m, d); return `${x.getMonth() + 1}/${x.getDate()}/${x.getFullYear()}`; };
    rows.push(`${day(2)},COMCAST XFINITY 800-266-2278,-${m < 2 ? '95.00' : '70.00'}`, `${day(8)},VERIZON WIRELESS PAYMENT,-85.00`,
      `${day(15)},GEICO AUTO INSURANCE,-142.10`, `${day(5)},KROGER #555,-${(40 + m * 7).toFixed(2)}`);
  }
  showFound(rows.join('\n'));
});

$('#ics').addEventListener('click', () => {
  if (!plan.reminders) { $('#ics-msg').innerHTML = upsellHtml('Calendar reminders are a Pro feature.'); return; }
  const events = Bills.billReminders(data, today);
  if (!events.length) { $('#ics-msg').textContent = 'Add a promo end date to a bill first.'; return; }
  download('bill-reminders.ics', buildIcs(events, { name: 'Bill reminders' }), 'text/calendar');
  $('#ics-msg').textContent = `${events.length} reminder${events.length === 1 ? '' : 's'} downloaded. Open the file to add them to your calendar.`;
});
$('#backup').addEventListener('click', () => download('bill-tracker.json', JSON.stringify(data, null, 2), 'application/json'));

const kit = config.billCutKit;
if (kit && live(kit.url)) {
  $('#kit').innerHTML = `<h2>${esc(kit.name)} (${esc(kit.price)})</h2><p>${esc(kit.pitch)}</p><a class="btn small" href="${esc(kit.url)}">Get the kit</a>`;
  $('#kit').hidden = false;
}

render();
initTracking({ config, app: 'budget', page: 'bill-tracker' });
