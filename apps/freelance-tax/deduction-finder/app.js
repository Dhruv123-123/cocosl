// Browser glue for the deduction finder: renders the questions from lib/deductions.js, shows the list,
// keeps the ticked answers in the URL, and copies them into the signup form's hidden field.
import { ITEMS, AUTOMATIC, findDeductions, savingPer100, scheduleOf } from '../lib/deductions.js';
import { setupSignup } from '../signup.js';
import { setupSite } from '../site.js';

const $ = (s) => document.querySelector(s);
const esc = (s) => String(s).replace(/[&<>"]/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]));
const money = (x) => '$' + Math.round(x).toLocaleString('en-US');

function answers(form) {
  return Object.fromEntries(ITEMS.map((it) => [it.id, form.elements[it.id].checked]));
}

function render(form) {
  const found = findDeductions(answers(form));
  const profit = parseFloat(String(form.elements.profit.value).replace(/[$,\s]/g, '')) || 0;
  const c = savingPer100(profit, 'single', 'C'), one = savingPer100(profit, 'single', '1');
  const card = (it) => `<article><h3>${esc(it.name)}</h3><p>${esc(it.rule)}</p><p class="where">${esc(it.where)}${it.source ? ` · ${esc(it.source)}` : ''}</p></article>`;
  const head = found.length
    ? `<p class="kicker">Your checklist</p><p class="big">${found.length + AUTOMATIC.length} deductions</p>`
    : '<p class="kicker">Your checklist</p><p class="big">Tick what applies</p><p>Answer the questions on the left. The automatic ones below apply to every freelancer with a profit.</p>';
  const worth = profit >= 100 ? `<p class="note">At about ${money(profit)} of profit (single), each $100 of Schedule C expenses saves about <b>${money(c)}</b> of 2026 federal tax; each $100 of health, retirement or HSA deductions saves about <b>${money(one)}</b> (income tax only).</p>` : '';
  const sched = (s) => found.filter((it) => scheduleOf(it) === s);
  return `${head}${worth}
    ${sched('C').length ? `<h3>Business expenses (Schedule C)</h3><div class="found">${sched('C').map(card).join('')}</div>` : ''}
    ${sched('1').length ? `<h3>Adjustments to income (Schedule 1)</h3><div class="found">${sched('1').map(card).join('')}</div>` : ''}
    <h3>Automatic for every freelancer</h3><div class="found">${AUTOMATIC.map(card).join('')}</div>`;
}

function init() {
  const form = $('#quiz-form');
  $('#quiz').innerHTML = ITEMS.map((it) => `<li><input type="checkbox" id="q-${it.id}" name="${it.id}"><label for="q-${it.id}">${esc(it.q)}</label></li>`).join('');
  const params = new URLSearchParams(location.search);
  for (const id of (params.get('yes') || '').split(',')) if (form.elements[id]) form.elements[id].checked = true;
  if (params.has('profit')) form.elements.profit.value = params.get('profit');
  const hidden = document.querySelector('form.signup input[name=deductions]');
  const update = () => {
    $('#result').innerHTML = render(form);
    const yes = ITEMS.filter((it) => form.elements[it.id].checked).map((it) => it.id);
    if (hidden) hidden.value = yes.join(',');
    history.replaceState(null, '', '?' + new URLSearchParams({ yes: yes.join(','), profit: form.elements.profit.value }).toString());
  };
  form.addEventListener('input', update);
  form.addEventListener('change', update);
  $('#print').addEventListener('click', () => window.print());
  setupSignup();
  setupSite();
  update();
}

init();
