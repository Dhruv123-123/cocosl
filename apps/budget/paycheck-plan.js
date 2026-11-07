// Paycheck-to-budget planner, English (paycheck-plan.html) and Spanish (plan-quincena.html).
// Everything runs and stays in this browser; the plan is kept in localStorage so the money dashboard
// maker on this site can pick it up as its budgets.
import config from './config.js';
import { initTracking } from './lib/track.js';
import { catName } from './lib/dashboard.js';
import { FREQS, BUCKETS, PLAN_KEYS, monthlyIncome, split503020, zeroBased, planCsv, PLAN_STORE } from './lib/paycheck-plan.js';
import { $, esc, store, download } from './page.js';

const es = document.documentElement.lang.startsWith('es');
const lang = es ? 'es' : 'en';
const loc = es ? 'es-US' : 'en-US';
const money = (n, d = 0) => (Number(n) || 0).toLocaleString(loc, { style: 'currency', currency: 'USD', minimumFractionDigits: d, maximumFractionDigits: d });

const T = es ? {
  freqs: { weekly: 'Cada semana', biweekly: 'Cada dos semanas', semimonthly: 'Dos veces al mes (día 15 y fin de mes)', monthly: 'Una vez al mes' },
  planOn: { base: 'Solo los cheques que llegan todos los meses (recomendado)', average: 'El promedio del año' },
  payErr: 'Escribe cuánto recibes por cheque, después de impuestos.',
  monthly: (m) => `Tu plan es para <b>${money(m)}</b> al mes.`,
  extra: (n, x) => `Te pagan cada ${n === 2 ? 'dos semanas' : 'semana'}, así que ${n} meses al año traen un cheque de más: ${money(x)} al año que no están en este plan. Mándalos directo a tus ahorros o a una deuda.`,
  buckets: { needs: 'Necesidades', wants: 'Gustos', savings: 'Ahorro y deudas extra' },
  bucketHint: { needs: '50%: renta, servicios, comida del súper, transporte, seguros y pagos mínimos', wants: '30%: comer fuera, salidas, compras y suscripciones', savings: '20%: fondo de emergencia, retiro y pagos extra a deudas' },
  left: (x) => `Te falta asignar <b>${money(x, 2)}</b>.`,
  over: (x) => `Te pasaste por <b>${money(-x, 2)}</b>. Baja alguna categoría.`,
  done: 'Cada dólar tiene un trabajo: te queda $0 por asignar.',
  vs: (b, p, t) => `${b}: ${p}% (la guía dice ${t}%)`,
  file: 'plan-de-presupuesto.csv',
} : {
  freqs: { weekly: 'Every week', biweekly: 'Every two weeks', semimonthly: 'Twice a month (15th and end of month)', monthly: 'Once a month' },
  planOn: { base: 'Only the paychecks every month gets (recommended)', average: 'The average over the year' },
  payErr: 'Enter your take-home pay per paycheck, after taxes.',
  monthly: (m) => `Your plan is for <b>${money(m)}</b> a month.`,
  extra: (n, x) => `You're paid every ${n === 2 ? 'two weeks' : 'week'}, so ${n} months a year bring an extra paycheck: ${money(x)} a year that isn't in this plan. Send it straight to savings or a debt.`,
  buckets: { needs: 'Needs', wants: 'Wants', savings: 'Savings and extra debt' },
  bucketHint: { needs: '50%: rent, utilities, groceries, transport, insurance and minimum payments', wants: '30%: eating out, going out, shopping and subscriptions', savings: '20%: emergency fund, retirement and extra debt payments' },
  left: (x) => `<b>${money(x, 2)}</b> still needs a job.`,
  over: (x) => `You've planned <b>${money(-x, 2)}</b> more than you earn. Trim a category.`,
  done: 'Every dollar has a job: $0 left to plan.',
  vs: (b, p, t) => `${b}: ${p}% (guideline ${t}%)`,
  file: 'budget-plan.csv',
};
const TARGET = { needs: 50, wants: 30, savings: 20 };

const form = $('#pay-form');
form.freq.innerHTML = Object.keys(FREQS).map((f) => `<option value="${f}"${f === 'biweekly' ? ' selected' : ''}>${T.freqs[f]}</option>`).join('');
form.planOn.innerHTML = Object.entries(T.planOn).map(([k, v]) => `<option value="${k}">${v}</option>`).join('');

$('#zero').innerHTML = Object.entries(BUCKETS).map(([b, keys]) => `<fieldset class="plan-group"><legend>${T.buckets[b]}</legend>
  ${keys.map((k) => `<label>${esc(catName(k, lang))}<input type="number" min="0" step="1" inputmode="decimal" data-cat="${k}" placeholder="$0"></label>`).join('')}</fieldset>`).join('');

let saved = {};
try { saved = JSON.parse(store.get(PLAN_STORE) || '{}') || {}; } catch { saved = {}; }
if (saved.pay) form.pay.value = saved.pay;
if (saved.freq && FREQS[saved.freq]) form.freq.value = saved.freq;
if (saved.planOn) form.planOn.value = saved.planOn;
for (const [k, v] of Object.entries(saved.amounts || {})) { const i = $(`[data-cat="${k}"]`); if (i) i.value = v; }

let income = null;
function amountsFromInputs() {
  return Object.fromEntries([...document.querySelectorAll('[data-cat]')].map((i) => [i.dataset.cat, i.value]));
}
function persist(plan) {
  store.set(PLAN_STORE, JSON.stringify({ pay: form.pay.value, freq: form.freq.value, planOn: form.planOn.value, monthly: income?.monthly || 0, amounts: plan?.amounts || {} }));
}

function render() {
  $('#plan-on-row').hidden = !['weekly', 'biweekly'].includes(form.freq.value);
  try {
    income = monthlyIncome({ pay: form.pay.value, freq: form.freq.value, planOn: $('#plan-on-row').hidden ? 'average' : form.planOn.value }, T.payErr);
  } catch (e) {
    income = null;
    $('#income').innerHTML = `<p class="error">${esc(e.message)}</p>`;
    $('#plans').hidden = true;
    return;
  }
  $('#plans').hidden = false;
  $('#income').innerHTML = `<p class="big">${T.monthly(income.monthly)}</p>${income.extra ? `<p>${T.extra(income.extraChecks, income.extra)}</p>` : ''}`;

  const s = split503020(income.monthly);
  $('#split').innerHTML = Object.entries(BUCKETS).map(([b, keys]) => `<div class="split-col">
    <h3>${T.buckets[b]} <span>${money(s.buckets[b])}</span></h3><p class="tiny">${T.bucketHint[b]}</p>
    <ul>${keys.filter((k) => s.amounts[k]).map((k) => `<li><span>${esc(catName(k, lang))}</span><b>${money(s.amounts[k])}</b></li>`).join('')}</ul></div>`).join('');

  const z = zeroBased(income.monthly, amountsFromInputs());
  $('#left').className = `plan-left ${z.balanced ? 'ok' : z.over ? 'bad' : ''}`;
  $('#left').innerHTML = `<p>${z.balanced ? T.done : z.over ? T.over(z.left) : T.left(z.left)}</p>
    <p class="tiny">${Object.keys(TARGET).map((b) => T.vs(T.buckets[b], z.pct[b], TARGET[b])).join(' · ')}</p>`;
  persist(z);
  return { s, z };
}

form.addEventListener('submit', (e) => e.preventDefault());
form.addEventListener('input', render);
form.addEventListener('change', render);
$('#zero').addEventListener('input', render);
$('#use-split').addEventListener('click', () => {
  if (!income) return;
  const { amounts } = split503020(income.monthly);
  for (const k of PLAN_KEYS) $(`[data-cat="${k}"]`).value = amounts[k] || '';
  render();
  $('#zero input').focus();
});
$('#clear').addEventListener('click', () => { for (const i of document.querySelectorAll('[data-cat]')) i.value = ''; render(); });
$('#csv').addEventListener('click', () => {
  if (!income) return;
  download(T.file, planCsv(zeroBased(income.monthly, amountsFromInputs()).amounts, lang), 'text/csv');
});
$('#to-dashboard').addEventListener('click', () => { render(); });

render();
initTracking({ config, app: 'budget', page: es ? 'plan-quincena' : 'paycheck-plan' });
