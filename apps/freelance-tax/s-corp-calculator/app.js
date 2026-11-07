// Browser glue for the S corp calculator: reads the form, runs lib/scorp.js, keeps inputs in the URL.
import { scorpCompare, breakEven } from '../lib/scorp.js';
import { setupSignup } from '../signup.js';
import { setupSite } from '../site.js';

const $ = (s) => document.querySelector(s);
const money = (x) => (x < 0 ? '−' : '') + '$' + Math.round(Math.abs(x)).toLocaleString('en-US');
const FIELDS = ['profit', 'salary', 'costs', 'status'];

function read(form) {
  const v = {};
  for (const k of FIELDS) v[k] = k === 'status' ? form.elements[k].value : parseFloat(String(form.elements[k].value).replace(/[$,\s]/g, '')) || 0;
  return v;
}

function render(v) {
  if (v.profit <= 0) return '<p class="big">Add your profit</p><p>Enter your yearly profit before paying yourself.</p>';
  const r = scorpCompare(v);
  const be = breakEven({ salaryShare: r.salaryShare, costs: v.costs, status: v.status });
  const head = r.saving > 0
    ? `<p class="kicker">An S corp would save about</p><p class="big">${money(r.saving)}/year</p>`
    : `<p class="kicker">An S corp would cost you about</p><p class="big">${money(-r.saving)}/year</p>`;
  const warn = r.outOfRange ? '<p class="note"><b>Above this tool\'s range.</b> At this profit the Additional Medicare Tax and QBI limits change the answer. Use this as a rough guide and talk to a CPA.</p>' : '';
  const small = r.saving > 0 && r.saving < 2000 ? '<p class="note">A saving this size can disappear with state taxes, a higher salary or your own time. Weigh it against the paperwork.</p>' : '';
  return `${head}
    <p class="note">Salary ${money(r.salary)} (${Math.round(r.salaryShare * 100)}% of profit), extra running costs ${money(r.costs)}. ${be ? `At this salary share, the S corp starts to come out ahead from about <b>${money(be)}</b> of profit.` : 'At this salary share, it doesn\'t come out ahead in this tool\'s range.'}</p>
    ${warn}${small}
    <table>
      <tr><th></th><th class="r">Sole proprietor</th><th class="r">S corp</th></tr>
      <tr><td>Self-employment / payroll tax</td><td class="r">${money(r.sole.seTax)}</td><td class="r">${money(r.scorp.employee + r.scorp.employer + r.scorp.futa)}</td></tr>
      <tr><td>Federal income tax</td><td class="r">${money(r.sole.incomeTax)}</td><td class="r">${money(r.scorp.incomeTax)}</td></tr>
      <tr><td>Extra running costs</td><td class="r">$0</td><td class="r">${money(r.costs)}</td></tr>
      <tr class="now"><td>You keep</td><td class="r">${money(r.sole.keep)}</td><td class="r">${money(r.scorp.keep)}</td></tr>
    </table>
    <p class="note">S corp payroll tax is 7.65% from you and 7.65% from the business on the salary, plus $42 of federal unemployment tax. The QBI deduction is ${money(r.scorp.qbi)} (20% of the ${money(r.scorp.k1)} left after salary and costs). State taxes aren't included.</p>`;
}

function init() {
  const form = $('#scorp-form');
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
