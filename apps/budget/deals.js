import config from './config.js';
import { initTracking } from './lib/track.js';
import * as Deals from './lib/promos.js';
import { buildIcs } from './lib/ics.js';
import { today as todayIs, prettyDay } from './lib/dates.js';
import { $, esc, money, store, currentPlan, download, upsellHtml } from './page.js';

const KEY = 'mms-deals-v1';
let data = Deals.loadDeals(store.get(KEY));
const { pro, plan } = currentPlan();
const today = todayIs();
const form = $('#deal-form');

const save = () => { if (!store.set(KEY, JSON.stringify(data))) $('#deal-msg').textContent = 'Could not save here (private browsing?). Use "Download my data" before closing.'; };

$('#plan-badge').textContent = pro ? 'Pro' : 'Free · Upgrade';
$('#plan-badge').classList.toggle('pro', pro);
$('#d-kind').innerHTML = Object.entries(Deals.KINDS).map(([k, v]) => `<option value="${k}">${esc(v)}</option>`).join('');
const toggleKind = () => { for (const el of form.querySelectorAll('.deferred-only')) el.hidden = form.kind.value !== 'deferred'; };
form.kind.addEventListener('change', toggleKind);
toggleKind();

const values = () => {
  const v = Object.fromEntries(new FormData(form));
  if (v.kind !== 'deferred') { v.purchase = ''; v.start = ''; }
  return v;
};
const plural = (n, w) => `${n} ${w}${n === 1 ? '' : 's'}`;

function verdict(a) {
  if (a.status === 'paid') return '<p class="okay">Paid off. Nice work.</p>';
  if (a.status === 'ended') return `<p class="alert">The promo ended on ${prettyDay(a.end)}. ${a.kind === 'deferred' ? 'If a balance was left, check your statement for back-dated interest and call the lender if it looks wrong.' : 'Interest now applies to what\'s left: pay it down or look at a lower-rate option.'}</p>`;
  if (!a.onTrack) return `<p class="alert"><b>At your current payment you won't clear it in time.</b> ${esc(a.costNote)} Pay <b>${money(a.safe)}</b> a month instead.</p>`;
  return `<p class="okay">On track: ${money(a.payment)} a month clears it before ${prettyDay(a.end)}.</p>`;
}

function resultHtml(a) {
  const deferredLine = a.kind === 'deferred' && a.worstCase > 0
    ? `<p class="tiny">If you stopped paying today, the back-dated interest on ${prettyDay(a.end)} would be about ${money(a.worstCase)}.</p>` : '';
  return `
    <div class="countdown">${a.days >= 0 ? plural(a.days, 'day') : 'Ended'} <small>${a.days >= 0 ? `left, until ${prettyDay(a.end)}` : ''}</small></div>
    <div class="result-grid">
      <div class="stat"><span>Pay each month to be safe</span><b>${money(a.safe)}</b><small>Clears it a month early</small></div>
      <div class="stat"><span>Bare minimum to clear it</span><b>${money(a.toClear)}</b><small>${plural(a.paymentsLeft, 'payment')} left</small></div>
      <div class="stat"><span>Left at the end at your payment</span><b class="${a.leftover ? 'neg' : ''}">${money(a.leftover)}</b></div>
      <div class="stat"><span>${a.kind === 'zero' ? 'Interest a month after' : 'Cost if you miss'}</span><b class="${a.cost ? 'neg' : ''}">${money(a.cost)}</b></div>
    </div>
    ${verdict(a)}${deferredLine}`;
}

function check() {
  try {
    const a = Deals.analyzeDeal(Deals.makeDeal(values()), today);
    $('#result').innerHTML = resultHtml(a);
    $('#result').hidden = false;
    $('#deal-msg').textContent = '';
    return true;
  } catch (err) {
    $('#deal-msg').textContent = err.message;
    return false;
  }
}

form.addEventListener('submit', (e) => { e.preventDefault(); if (check()) $('#result').scrollIntoView({ behavior: 'smooth', block: 'nearest' }); });
$('#save').addEventListener('click', () => {
  if (!check()) return;
  try {
    Deals.addDeal(data, values(), { max: plan.deals });
    save();
    render();
    $('#deal-msg').textContent = 'Saved. It stays on this device.';
  } catch (err) {
    $('#deal-msg').innerHTML = err instanceof Deals.LimitError ? upsellHtml('deals', plan) : esc(err.message);
  }
});

function render() {
  const s = Deals.summarizeDeals(data, today);
  $('#deals').innerHTML = s.rows.length
    ? `<p class="tiny">${money(s.owed)} owed across ${plural(s.rows.length, 'deal')}. To clear them all a month early, pay about ${money(s.neededMonthly)} a month in total.</p>`
      + s.rows.map((a) => `
      <article class="bill" data-id="${a.id}">
        <div class="bill-head">
          <div><b>${esc(a.name)}</b> <span class="tiny">${a.kind === 'deferred' ? 'Deferred interest' : a.kind === 'zero' ? '0% APR' : 'Pay over time'}</span><br>
            <span class="pill ${a.status === 'behind' || a.status === 'ended' ? 'bad' : a.status === 'soon' ? 'warn' : ''}">${a.days >= 0 ? `${plural(a.days, 'day')} left` : 'Ended'}</span> <span class="tiny">${prettyDay(a.end)}</span></div>
          <div class="bill-price"><b>${money(a.safe)}</b><small>a month to be safe</small></div>
        </div>
        ${verdict(a)}
        <form class="tx-form bal-form" data-id="${a.id}"><label>Balance now ($) <input name="balance" type="number" min="0" step="any" inputmode="decimal" value="${a.balance}"></label><label>You pay a month ($) <input name="payment" type="number" min="0" step="any" inputmode="decimal" value="${a.payment || ''}"></label><button class="btn small ghost">Update</button></form>
        <button class="x del" data-del="${a.id}" aria-label="Delete ${esc(a.name)}">Delete</button>
      </article>`).join('')
    : '<p class="tiny">No saved deals yet. Check one above, then save it to get the countdown here.</p>';
}

$('#deals').addEventListener('submit', (e) => {
  const f = e.target.closest('.bal-form');
  if (!f) return;
  e.preventDefault();
  const d = data.deals.find((x) => x.id === f.dataset.id);
  try {
    const next = Deals.makeDeal({ ...d, balance: f.balance.value, payment: f.payment.value });
    Object.assign(d, next);
    save();
    render();
  } catch (err) { alert(err.message); }
});
$('#deals').addEventListener('click', (e) => {
  const del = e.target.closest('[data-del]');
  if (del && confirm('Delete this deal?')) { Deals.removeDeal(data, del.dataset.del); save(); render(); }
});

$('#ics').addEventListener('click', () => {
  if (!plan.reminders) { $('#ics-msg').innerHTML = upsellHtml('reminders'); return; }
  const events = Deals.dealReminders(data, today);
  if (!events.length) { $('#ics-msg').textContent = 'Save a deal with a balance and a future end date first.'; return; }
  download('deal-reminders.ics', buildIcs(events, { name: '0% deal reminders' }), 'text/calendar');
  $('#ics-msg').textContent = `${plural(events.length, 'reminder')} downloaded (60, 30 and 7 days before each deadline). Open the file to add them to your calendar.`;
});
$('#backup').addEventListener('click', () => download('deal-countdown.json', JSON.stringify(data, null, 2), 'application/json'));

render();
initTracking({ config, app: 'budget', page: 'deal-countdown' });
