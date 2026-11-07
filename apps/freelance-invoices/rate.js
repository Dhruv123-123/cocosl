// Freelance rate calculator page (rate.html). Logic in lib/rate.js.
import config from './config.js';
import { initTracking } from './lib/track.js';
import { rateFor, DEFAULTS } from './lib/rate.js';
import { BRACKETS } from './lib/sidehustle.js';

const $ = (s) => document.querySelector(s);
const money = (n, d = 0) => (Number(n) || 0).toLocaleString('en-US', { style: 'currency', currency: 'USD', minimumFractionDigits: d, maximumFractionDigits: d });
const esc = (s) => String(s ?? '').replace(/[&<>"']/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' })[c]);
const store = {
  get(k) { try { return localStorage.getItem(k); } catch { return null; } },
  set(k, v) { try { localStorage.setItem(k, v); } catch { /* private mode */ } },
};
const KEY = '1099-rate-v1';
const form = $('#rate');
$('#bracket').innerHTML = BRACKETS.map((b) => `<option value="${b}">${b}%</option>`).join('');

let saved = {};
try { saved = JSON.parse(store.get(KEY)) || {}; } catch { /* first visit */ }
// Starting numbers from the link (?takeHome=80000&hours=35), then what this browser saved, then defaults.
const params = new URLSearchParams(location.search);
for (const k of Object.keys(DEFAULTS)) {
  const v = params.get(k) ?? saved[k] ?? DEFAULTS[k];
  if (form[k]) form[k].value = /^[\d.]*$/.test(String(v)) ? v : DEFAULTS[k];
}

function render() {
  const values = Object.fromEntries(new FormData(form));
  store.set(KEY, JSON.stringify(values));
  const r = rateFor(values);
  const v = r.input;
  const c = r.current;
  $('#result').innerHTML = `
    <p class="big-num">${r.quote === null ? '—' : money(r.quote)} <small>an hour</small></p>
    <p>Charge at least <b>${money(r.quote)} an hour</b> (${money(r.hourly, 2)} before rounding up). That's <b>${money(r.day)} for a full day</b> and about <b>${money(r.week)} a week</b> of billable work.</p>
    <table class="plan sh-table"><tbody>
      <tr><td>Take-home pay you want</td><td class="num">${money(v.takeHome)}</td></tr>
      <tr><td>Self-employment tax</td><td class="num">${money(r.tax.se)}</td></tr>
      <tr><td>Federal income tax at ${v.bracket}%${v.stateRate ? ' and state tax' : ''}</td><td class="num">${money(r.tax.income + r.tax.state)}</td></tr>
      <tr><td>Health insurance and retirement</td><td class="num">${money((v.health + v.retire) * 12)}</td></tr>
      <tr><td>Business costs</td><td class="num">${money(r.costsYear)}</td></tr>
      <tr><td>Cushion for slow months (${v.buffer}%)</td><td class="num">${money(r.cushion)}</td></tr>
      <tr><td><b>You need to bill a year</b></td><td class="num"><b>${money(r.revenue)}</b></td></tr>
      <tr><td>Hours you can bill (${r.workWeeks} weeks × ${v.hours} hours × ${v.billable}%)</td><td class="num">${r.billableHours.toLocaleString('en-US')}</td></tr>
    </tbody></table>
    <p>That's about ${money(r.monthRevenue)} a month in invoices. Of every dollar a client pays, you take home about ${Math.round(r.perDollar * 100)}¢.</p>
    ${c ? `<div class="offer-box"><h3>At your rate now (${money(c.rate)} an hour)</h3><p>You'd take home about <b>${money(c.keep)}</b> a year, ${c.gap < 0 ? `<b>${money(-c.gap)} short</b> of your goal. Raise your rate for new clients first, and tell current clients 30 to 60 days ahead.` : `<b>${money(c.gap)} more</b> than your goal. Nicely done.`}</p></div>` : ''}`;
  const tips = [];
  if (v.billable > 75) tips.push('Billing more than 75% of your hours is rare once you count finding work, proposals, invoicing and admin. If your rate only works at a high billable share, it\'s fragile.');
  if (r.billableHours < 800) tips.push(`Only ${r.billableHours} billable hours a year: a retainer or project pricing can earn more from the same hours.`);
  if (!v.health) tips.push('No health insurance in the plan. Marketplace plans for self-employed people are at HealthCare.gov, and the premiums lower your income tax.');
  tips.push(`Put about ${Math.ceil((r.tax.total / r.revenue) * 100)}% of every payment aside for taxes and pay quarterly estimates.`);
  $('#tips').innerHTML = tips.map((t) => `<li class="warn info">${esc(t)}</li>`).join('');
}

form.addEventListener('input', render);
form.addEventListener('submit', (e) => e.preventDefault());
render();
initTracking({ config, app: 'freelance-invoices', page: 'rate' });
