// First paycheck guide page (first-paycheck.html). Logic in lib/firstpaycheck.js.
import config from './config.js';
import { initTracking } from './lib/track.js';
import * as F from './lib/firstpaycheck.js';
import { $, esc, money, store } from './page.js';

const KEY = 'mms-first-paycheck-v1';
let state = {};
try { state = JSON.parse(store.get(KEY)) || {}; } catch { /* first visit */ }
state.done ||= {};
state.extras ||= {};
const save = () => store.set(KEY, JSON.stringify(state));
const w4 = $('#w4');
const mf = $('#match');

$('#site-link').href = config.siteUrl;
$('#extras').innerHTML = F.EXTRAS.map((x) => `<li><label class="pick"><input type="checkbox" data-extra="${x.id}"> <span>${esc(x.text)}${x.link ? ` <a href="${esc(x.link)}">${esc(x.label)}</a>` : ''}</span></label></li>`).join('');

// Restore inputs.
for (const [id, v] of Object.entries(state.inputs || {})) { const el = document.getElementById(id); if (el) el.value = v; }
for (const [k, v] of Object.entries(state.w4 || {})) if (w4[k]) w4[k].value = v;
for (const [k, v] of Object.entries(state.match || {})) if (mf[k]) mf[k].value = v;
for (const el of document.querySelectorAll('[data-done]')) el.checked = !!state.done[el.dataset.done];
for (const el of document.querySelectorAll('[data-extra]')) el.checked = !!state.extras[el.dataset.extra];

function render() {
  const salary = Number($('#salary').value) || 0;
  // W-4
  const a = Object.fromEntries(new FormData(w4));
  w4.querySelector('.side-only').hidden = a.side !== 'yes';
  const advice = F.w4Advice(a);
  $('#w4-out').innerHTML = advice.steps.map((s) => `<li><b>${esc(s.step)}:</b> ${esc(s.text)}${s.link ? ` <a href="${esc(s.link)}" target="_blank" rel="noopener">IRS Tax Withholding Estimator</a>` : ''}</li>`).join('')
    + (advice.simple ? '<li class="tiny">Simple case: Step 1 and Step 5 are all you need.</li>' : '');

  // 401(k) match
  const m = Object.fromEntries(new FormData(mf));
  if (salary) {
    const r = F.matchPlan({ salary, ...m });
    $('#match-out').innerHTML = `<p class="callout">Set your 401(k) to at least <b>${r.contributePct}%</b> of pay. That's about <b>${money(r.youPerPaycheck)}</b> a paycheck from you, and your employer adds <b>${money(r.freeMoneyPerPaycheck)}</b>: <b>${money(r.freeMoneyYear)}</b> a year you'd otherwise leave behind.</p>
      <p class="tiny">${r.capped ? `That hits the 2026 limit of ${money(F.LIMIT_401K_2026)}. ` : ''}The match is an instant ${Math.round(r.instantReturn * 100)}% return before any investment growth. Check how long the match takes to vest (become yours) in your plan documents. Not sure whether to choose Roth or traditional? <a href="../money-calculators/roth-vs-traditional/">Compare them</a>.</p>`;
  } else $('#match-out').innerHTML = '<p class="tiny">Enter your salary at the top to see the numbers.</p>';

  // Emergency fund
  const ess = Number($('#essentials').value) || 0;
  $('#cushion-out').innerHTML = ess ? `<ol class="plain-list cushion">${F.cushionTargets(ess).map((t) => `<li><b>${esc(t.label)}:</b> ${money(t.amount)}</li>`).join('')}</ol>
    <p class="tiny">See how long each takes and what interest you'd earn: <a href="../money-calculators/emergency-fund/?monthlyExpenses=${ess}">emergency fund calculator</a>.</p>` : '';

  // Budget
  const th = Number($('#takehome').value) || 0;
  const link = $('#paycheck-link');
  link.href = `../money-calculators/take-home-pay/${salary ? `?salary=${salary}&pretax401k=${Math.round(salary * ((Number(mf.upToPct.value) || 0) / 100))}` : ''}`;
  if (th) {
    const b = F.budgetSplits(th);
    $('#budget-out').innerHTML = `<div class="choices">
      <div class="choice"><h3>50/30/20</h3><p>Needs ${money(b.fiftyThirtyTwenty.needs)} · Wants ${money(b.fiftyThirtyTwenty.wants)} · Savings and debt ${money(b.fiftyThirtyTwenty.savings)}</p><p class="tiny">Simple and flexible. Good if you've never budgeted.</p></div>
      <div class="choice"><h3>Pay yourself first</h3><p>Save ${money(b.payYourselfFirst.save)} on payday, spend the other ${money(b.payYourselfFirst.spend)} freely.</p><p class="tiny">The least tracking. Good if you hate spreadsheets.</p></div>
      <div class="choice"><h3>Every dollar a job</h3><p>Plan each dollar of ${money(th)} before the month starts.</p><p class="tiny">The most control. The <a href="./">20-Minute Budget</a> does this.</p></div>
    </div><p class="tiny">See how your plan scores: <a href="rate.html">Rate my budget</a>.</p>`;
  } else $('#budget-out').innerHTML = '';

  // Progress
  const done = F.STEPS.filter((s) => state.done[s.id]).length;
  $('#progress').innerHTML = `<p><b>${done} of ${F.STEPS.length} steps done</b>${done === F.STEPS.length ? ': nice work. Your first paycheck is set up.' : ''}</p><div class="bar"><span style="width:${(done / F.STEPS.length) * 100}%"></span></div>`;
  for (const s of F.STEPS) document.getElementById(`step-${s.id}`).classList.toggle('is-done', !!state.done[s.id]);

  state.inputs = { salary: $('#salary').value, essentials: $('#essentials').value, takehome: $('#takehome').value };
  state.w4 = a;
  state.match = m;
  save();
}

document.addEventListener('input', render);
document.addEventListener('change', (e) => {
  const d = e.target.dataset || {};
  if (d.done) state.done[d.done] = e.target.checked;
  if (d.extra) state.extras[d.extra] = e.target.checked;
  render();
});
for (const f of [w4, mf]) f.addEventListener('submit', (e) => e.preventDefault());
render();
initTracking({ config, app: 'budget', page: 'first-paycheck' });
