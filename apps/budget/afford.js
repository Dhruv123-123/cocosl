// "Can I afford this?" page (afford.html). Logic in lib/afford.js.
import config from './config.js';
import { initTracking } from './lib/track.js';
import * as A from './lib/afford.js';
import { today as todayIs, prettyDay } from './lib/dates.js';
import { $, esc, money, store } from './page.js';

const KEY = 'mms-afford-v1';
const form = $('#afford-form');
const today = todayIs();
const opts = (obj) => Object.entries(obj).map(([k, v]) => `<option value="${k}">${esc(v)}</option>`).join('');
const NUMS = ['price', 'salesTax', 'fees', 'tradeIn', 'down', 'extraMonthly', 'loanApr', 'loanMonths', 'bnplApr', 'bnplMonths'];
const MINE = ['savings', 'keepSaved', 'takeHome', 'bills']; // your own money: kept when you switch what you're buying

$('#kind').innerHTML = opts(A.KINDS);
$('#bnpl-type').innerHTML = opts(A.BNPL_TYPES);
$('#site-link').href = config.siteUrl;

function fill(values) {
  for (const [k, v] of Object.entries(values)) if (form[k] && v !== undefined) form[k].value = v;
}
function loadPreset(kind) {
  const { bnplType, ...nums } = A.PRESETS[kind];
  fill({ ...nums, bnplType });
}

let saved = {};
try { saved = JSON.parse(store.get(KEY)) || {}; } catch { /* first visit */ }
form.kind.value = A.KINDS[saved.kind] ? saved.kind : 'car';
loadPreset(form.kind.value);
fill(saved);

const LABEL = { cash: 'Pay cash', loan: 'Take a loan', bnpl: 'Buy now, pay later' };
const VERDICT = { yes: ['Fits', 'ok'], tight: ['Tight', 'warn'], no: ["Doesn't fit", 'bad'] };

function render() {
  const values = Object.fromEntries(new FormData(form));
  store.set(KEY, JSON.stringify(values));
  const car = values.kind === 'car';
  for (const el of form.querySelectorAll('.car-only')) el.hidden = !car;
  form.querySelector('.car-only-text').hidden = !car;
  form.querySelector('.not-car-text').hidden = car;
  for (const el of form.querySelectorAll('.bnpl-monthly')) el.hidden = values.bnplType !== 'monthly';
  $('#loan-title').textContent = values.kind === 'phone' ? 'The installment plan (carrier, store or loan)' : 'The loan';

  const r = A.compare(values, today);
  const best = r.options.find((o) => o.key === r.best);
  const cheapest = r.options.reduce((a, b) => (b.total < a.total ? b : a));
  $('#verdict').innerHTML = best
    ? `<p class="big-verdict"><b>Yes, if you ${best.key === 'cash' ? 'pay cash' : best.key === 'loan' ? (values.kind === 'phone' && !Number(values.loanApr) ? 'use the 0% installment plan' : 'take the loan') : 'use buy now, pay later'}.</b></p>
       <p>That's the cheapest way that fits: <b>${money(best.total)}</b> in total${best.monthly ? `, about <b>${money(best.monthly)}</b> a month` : ''}. It costs ${money(r.upfront)} all-in${r.input.kind === 'car' ? ' with tax and fees' : ' with tax'}.</p>`
    : `<p class="big-verdict"><b>${r.input.takeHome ? 'Not yet.' : 'Add your take-home pay and bills.'}</b></p>
       <p>${r.input.takeHome ? `None of the three ways fits comfortably right now. It costs ${money(r.upfront)} all-in.${r.saveMonths ? ` Putting aside everything left after bills (${money(r.leftover)} a month), you could pay cash in about <b>${r.saveMonths} month${r.saveMonths === 1 ? '' : 's'}</b>.` : ''}` : `It costs ${money(r.upfront)} all-in. Your pay and bills tell us whether the payments fit.`}</p>`;

  $('#compare').innerHTML = `<h2>Three ways to pay</h2>
    <div class="table-scroll" tabindex="0" role="region" aria-label="Three ways to pay"><table class="plan subs afford"><thead><tr><th></th>${r.options.map((o) => `<th>${LABEL[o.key]}</th>`).join('')}</tr></thead><tbody>
      <tr><td>Verdict</td>${r.options.map((o) => `<td><span class="pill ${VERDICT[o.verdict][1]}">${VERDICT[o.verdict][0]}</span>${o.key === r.best ? ' <span class="pill muted">best</span>' : ''}</td>`).join('')}</tr>
      <tr><td>Up front</td>${r.options.map((o) => `<td class="num">${money(o.cashNow)}</td>`).join('')}</tr>
      <tr><td>Each month</td>${r.options.map((o) => `<td class="num">${o.monthly ? money(o.monthly) : '—'}${o.months ? `<small style="display:block">for ${o.key === 'bnpl' && values.bnplType === 'pay4' ? 'about 6 weeks' : `${o.months} months`}</small>` : ''}</td>`).join('')}</tr>
      <tr><td>Interest</td>${r.options.map((o) => `<td class="num ${o.interest ? 'neg' : ''}">${money(o.interest)}</td>`).join('')}</tr>
      <tr><td><b>True total</b></td>${r.options.map((o) => `<td class="num"><b>${money(o.total)}</b>${o.total > cheapest.total + 0.005 ? `<small class="neg" style="display:block">+${money(o.total - cheapest.total)}</small>` : ''}</td>`).join('')}</tr>
    </tbody></table></div>
    <p class="tiny">"Each month" includes ${r.input.extraMonthly ? `${money(r.input.extraMonthly)} of running costs` : 'no running costs'}. ${values.bnplType !== 'pay4' ? '' : 'Pay in 4 is shown as two payments a month. '}${r.options[2].last ? `The last buy now, pay later payment would be ${prettyDay(r.options[2].last)}.` : ''}</p>
    ${r.options.map((o) => (o.reasons.length ? `<h3>${LABEL[o.key]}</h3><ul class="plain-list">${o.reasons.map((x) => `<li>${esc(x)}</li>`).join('')}</ul>` : '')).join('')}`;
  $('#tips').innerHTML = r.tips.map((t) => `<li class="warn info">${esc(t)}</li>`).join('');
}

form.addEventListener('input', render);
form.kind.addEventListener('change', () => {
  const mine = Object.fromEntries(MINE.map((k) => [k, form[k].value]));
  for (const k of NUMS) form[k].value = '';
  loadPreset(form.kind.value);
  fill(mine);
  render();
});
form.addEventListener('submit', (e) => e.preventDefault());

render();
initTracking({ config, app: 'budget', page: 'afford-checker' });
