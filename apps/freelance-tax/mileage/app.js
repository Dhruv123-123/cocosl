// Browser glue for the driver mileage page: reads the form, runs lib/mileage.js, keeps inputs in the URL.
// Nothing typed is sent anywhere.
import { mileagePlan, RATE_JAN_JUN, RATE_JUL_DEC } from '../lib/mileage.js';
import { setupSignup } from '../signup.js';
import { setupSite } from '../site.js';

const $ = (s) => document.querySelector(s);
const money = (x) => '$' + Math.round(x).toLocaleString('en-US');
const cents = (x) => (x < 1 ? Math.round(x * 100) + '¢' : '$' + x.toFixed(2));
const pct = (x) => (x * 100).toFixed(1).replace(/\.0$/, '') + '%';
const FIELDS = ['earnings', 'miles', 'milesFromJuly', 'status', 'appMiles', 'otherCosts', 'deliveries', 'w2Wages', 'stateRate'];

function read(form) {
  const v = {};
  for (const k of FIELDS) v[k] = k === 'status' ? form.elements[k].value : parseFloat(String(form.elements[k].value).replace(/[$,%\s]/g, '')) || 0;
  if (String(form.elements.milesFromJuly.value).trim() === '') v.milesFromJuly = null;  // blank: assume half
  v.stateRate /= 100;
  return v;
}

function render(v) {
  const p = mileagePlan(v);
  if (p.earnings <= 0) return '<p class="big">Add your earnings</p><p>Enter what the apps paid you this year, tips included.</p>';
  const lines = [
    `<p class="kicker">Your miles save you about</p><p class="big">${money(p.saving)}</p>`,
    `<p class="note">${p.miles.toLocaleString('en-US')} miles (${v.milesFromJuly === null ? 'half assumed before July at' : 'before July at'} ${RATE_JAN_JUN * 100}¢, the rest at ${RATE_JUL_DEC * 100}¢) = a ${money(p.deduction)} deduction, which takes your taxable profit from ${money(p.profitNoMiles)} to ${money(p.profit)}.</p>`,
    `<div class="two stats"><div><span>Tax on this income</span><b>${money(p.tax)}</b></div><div><span>Set aside from each payout</span><b>${pct(p.setAsideRate)}</b></div></div>`,
  ];
  if (p.perDelivery !== null) lines.push(`<h3>Per delivery or trip</h3><p class="setaside">${cents(p.perDelivery)}</p>`);
  if (p.appSaving !== null && p.appSaving > 0) lines.push(`<h3>Your log vs the app's miles</h3><p>Logging your own miles is worth about <b>${money(p.appSaving)}</b> more than using only the app's figure.</p>`);
  lines.push(`<h3>Every 100 more miles you log</h3><p>saves about <b>${money(p.per100)}</b> at your rates.</p>`);
  if (p.owesEstimates) lines.push(`<h3>Quarterly payments</h3><p>You'll likely owe $1,000 or more, so quarterly payments apply: about <b>${money(p.quarterly)}</b> each. <a href="../?profit=${Math.round(p.profit)}&status=${v.status}">Work out each payment</a>.</p>`);
  lines.push(`<details><summary>How this is worked out</summary><p>Profit is payouts minus other costs minus the mileage deduction. Tax is 2026 federal self-employment tax plus the income tax this profit adds${v.w2Wages ? ' on top of your W-2 wages' : ''}, using the standard deduction and the 20% QBI deduction${v.stateRate ? ', plus your state rate' : ''}. Self-employment tax: ${money(p.seTax)}. It doesn't include credits.</p></details>`);
  return lines.join('');
}

function init() {
  const form = $('#mileage-form');
  const params = new URLSearchParams(location.search);
  for (const k of FIELDS) if (params.has(k)) form.elements[k].value = params.get(k);
  const update = () => {
    $('#result').innerHTML = render(read(form));
    history.replaceState(null, '', '?' + new URLSearchParams(FIELDS.map((k) => [k, form.elements[k].value])).toString());
  };
  form.addEventListener('input', update);
  form.addEventListener('change', update);
  $('#share').addEventListener('click', async () => {
    try { await navigator.clipboard.writeText(location.href); $('#share').textContent = 'Link copied'; } catch { /* clipboard blocked */ }
  });
  setupSignup();
  setupSite();
  update();
}

init();
