// Browser glue: builds each calculator's form, runs the math from lib/calc.js,
// keeps inputs in the URL so results can be shared, and shows the right offer.
import config from './config.js';
import * as calc from './lib/calc.js';
import { STATE_OPTIONS } from './lib/state-tax-2026.js';
import { comparePlans } from './lib/student-loans.js';
import { rentVsBuy } from './lib/rent-vs-buy.js';
import { estimateRefund } from './lib/refund.js';
import { EXTRA } from './lib/text-extra.js';
import { analyzeFees } from './lib/fees.js';
import { remittanceCost } from './lib/remit.js';
import { money, isLiveUrl, escapeHtml } from './lib/format.js';
import { TEXT } from './lib/text.js';
import { initTracking, withUtm } from './lib/track.js';
import { embedOptions } from './lib/embed-options.js';

const $ = (sel, root = document) => root.querySelector(sel);

const lang = document.documentElement.lang.startsWith('es') ? 'es' : 'en';
const T = TEXT[lang];
const F = T.fields;
const X = EXTRA[lang];
const XF = X.f;

// Budget Pro upsell on calculators that lead into budgeting (English only: the app is in English).
function budgetProBox(where) {
  const b = config.budgetApp;
  if (lang !== 'en' || !b || !b.url) return '';
  const pricing = `${b.pricingUrl}?from=${encodeURIComponent(where)}`;
  return `<div class="pro-box"><p><b>Make it happen month by month.</b> Add this goal to the free 20-Minute Budget app and see each month's progress. Budget Pro adds unlimited goals, every past and future month and bank CSV import.</p>
    <p><a class="btn small" href="${escapeHtml(b.url)}" data-upgrade="${escapeHtml(where)}-app">Open the budget app</a> <a href="${escapeHtml(pricing)}" data-upgrade="${escapeHtml(where)}">See Budget Pro</a></p></div>`;
}

const CALCS = {
  'compound-interest': {
    cta: 'brokerage',
    fields: [['initial', F.initial, 1000], ['monthly', F.monthly, 200], ['annualRate', F.annualRate, 7, 0.1], ['years', F.years, 30]],
    render(v) {
      const r = calc.compoundGrowth(v);
      return `${T.growth(v, r)}${lineChart(r.rows)}<p class="note">${T.growthNote(v)}</p>`;
    },
  },
  'emergency-fund': {
    cta: 'hysa',
    fields: [['monthlyExpenses', F.monthlyExpenses, 2000], ['monthsTarget', F.monthsTarget, 0], ['currentSaved', F.currentSaved, 500], ['monthlySave', F.monthlySave, 250], ['apy', F.apy, 4, 0.01]],
    select: ['stability', F.stability, [['average', F.stAverage], ['steady', F.stSteady], ['variable', F.stVariable], ['unstable', F.stUnstable]]],
    render(v) {
      const r = calc.emergencyFund(v);
      const suggest = T.efSuggest(r, !Number(v.monthsTarget));
      const timeline = `<h3>${T.efTimeline}</h3><ol class="timeline">${r.milestones.map((m) => `<li><b>${T.efMarks[m.key]}</b> ${money(m.amount)}: ${m.months === 0 ? T.efNow : m.months ? T.efIn(m.months) : T.efNever}</li>`).join('')}</ol>`;
      const extra = suggest + budgetProBox('emergency-fund');
      if (r.gap === 0) return T.efDone(r) + extra;
      if (!r.reachable) return T.efNoSave(r) + extra;
      return T.ef(v, r) + timeline + extra;
    },
  },
  'savings-interest': {
    cta: 'hysa',
    fields: [['balance', F.balance, 5000], ['monthlyDeposit', F.monthlyDeposit, 100], ['apy', F.hyApy, 4, 0.01], ['compareApy', F.compareApy, 0.01, 0.01], ['months', F.months, 12]],
    render: (v) => T.savings(v, calc.savingsInterest(v)),
  },
  'credit-card-minimum': {
    cta: 'debt',
    fields: [['balance', F.cardBalance, 5000], ['apr', F.apr, 22.99, 0.01], ['minPercent', F.minPercent, 1, 0.1], ['minFloor', F.minFloor, 25], ['fixedPayment', F.fixedPayment, 250]],
    render(v) {
      const r = calc.minimumPaymentTrap(v);
      let fixed = '';
      if (r.fixed) fixed = Number.isFinite(r.fixed.months) ? T.ccFixed(v, r.fixed, r.interestSaved) : T.ccFixedNever(v);
      return T.cc(r.minimumOnly, fixed);
    },
  },
  'take-home-pay': {
    cta: 'hysa',
    fields: [['salary', F.salary, 60000], ['pretax401k', F.pretax401k, 3000], ['pretaxHealth', F.pretaxHealth, 0], ['stateRate', F.stateRate, 4, 0.1], ['payPeriods', F.payPeriods, 26]],
    select: [['filing', F.filing, [['single', F.single], ['married', F.married]]], ['state', F.state, [['custom', F.stateCustom], ...STATE_OPTIONS]]],
    render: (v) => T.takeHome(v, calc.takeHomePay(v)),
  },
  'student-loans': {
    cta: 'credit',
    fields: [['balance', XF.slBalance, 35000], ['rate', XF.slRate, 6.5, 0.01], ['agi', XF.slAgi, 45000], ['household', XF.slHousehold, 1], ['dependents', XF.slDependents, 0], ['growth', XF.slGrowth, 3, 0.1]],
    select: [
      ['cohort', XF.slCohort, [['before2026', XF.slBefore], ['after2026', XF.slAfter]]],
      ['newBorrower2014', XF.slNew2014, [['yes', XF.yes], ['no', XF.no]]],
      ['region', XF.slRegion, [['contiguous', XF.contiguous], ['alaska', XF.alaska], ['hawaii', XF.hawaii]]],
    ],
    render: (v) => X.loans(comparePlans(v)) + budgetProBox('student-loans'),
  },
  'rent-vs-buy': {
    cta: 'hysa',
    fields: [['price', XF.rbPrice, 400000], ['downPct', XF.rbDown, 20, 0.1], ['mortgageRate', XF.rbRate, 6.5, 0.01], ['termYears', XF.rbTerm, 30], ['rent', XF.rbRent, 2200], ['years', XF.rbYears, 7],
      ['propertyTaxPct', XF.rbTax, 1.1, 0.01], ['insurance', XF.rbIns, 1800], ['hoa', XF.rbHoa, 0], ['maintenancePct', XF.rbUpkeep, 1, 0.1], ['closingPct', XF.rbClosing, 3, 0.1], ['sellingPct', XF.rbSelling, 6, 0.1],
      ['appreciation', XF.rbApp, 3, 0.1], ['rentGrowth', XF.rbRentGrowth, 3, 0.1], ['rentersInsurance', XF.rbRentersIns, 15], ['investReturn', XF.rbReturn, 6, 0.1]],
    render: (v) => X.rentBuy(rentVsBuy(v)),
  },
  'tax-refund': {
    cta: 'hysa',
    fields: [['wages', XF.trWages, 55000], ['withheld', XF.trWithheld, 5200], ['otherIncome', XF.trOther, 0], ['estimated', XF.trEstimated, 0], ['kids', XF.trKids, 0], ['otherDeps', XF.trOtherDeps, 0],
      ['tips', XF.trTips, 0], ['overtime', XF.trOvertime, 0], ['seniors', XF.trSeniors, 0]],
    select: ['filing', XF.trFiling, [['single', XF.trSingle], ['married', XF.trMarried], ['hoh', XF.trHoh]]],
    render: (v) => X.refund(estimateRefund(v)) + budgetProBox('tax-refund'),
  },
  'remittance-cost': {
    cta: 'remit',
    fields: [['amount', X.rf.amount, 300], ['fee', X.rf.fee, 4.99, 0.01], ['feePct', X.rf.feePct, 0, 0.01], ['midRate', X.rf.midRate, 0, 0.0001], ['quotedRate', X.rf.quotedRate, 0, 0.0001], ['markupPct', X.rf.markupPct, 2, 0.01], ['perYear', X.rf.perYear, 12]],
    select: [['feeMode', X.rf.feeMode, [['top', X.rf.top], ['inside', X.rf.inside]]], ['pay', X.rf.pay, [['bank', X.rf.bank], ['cash', X.rf.cash]]]],
    render: (v) => X.remit(remittanceCost(v, X.rf.errors)),
  },
  'roth-vs-traditional': {
    cta: 'brokerage',
    fields: [['annualContribution', F.annualContribution, 6000], ['currentRate', F.currentRate, 22], ['retirementRate', F.retirementRate, 15], ['years', F.yearsToWithdraw, 35], ['annualReturn', F.annualReturn, 7, 0.1]],
    render: (v) => T.roth(calc.rothVsTraditional(v)),
  },
};

// ---------- debt payoff (dynamic rows) ----------
const DEFAULT_DEBTS = () => [
  { name: T.defaultDebts[0], balance: 3200, apr: 24.99, minPayment: 95 },
  { name: T.defaultDebts[1], balance: 650, apr: 29.99, minPayment: 30 },
  { name: T.defaultDebts[2], balance: 7800, apr: 6.9, minPayment: 230 },
];

function debtRow(d = { name: '', balance: '', apr: '', minPayment: '' }) {
  const row = document.createElement('div');
  row.className = 'debt-row';
  row.innerHTML = `
    <label>${F.debtName}<input name="name" value="${escapeHtml(d.name)}" maxlength="40"></label>
    <label>${F.debtBalance}<input name="balance" type="number" min="0" step="any" value="${d.balance}" required></label>
    <label>${F.debtApr}<input name="apr" type="number" min="0" max="100" step="any" value="${d.apr}" required></label>
    <label>${F.debtMin}<input name="minPayment" type="number" min="0" step="any" value="${d.minPayment}" required></label>
    <button type="button" class="link remove" aria-label="${F.removeAria}">${F.remove}</button>`;
  row.querySelector('.remove').addEventListener('click', () => { row.remove(); run(); });
  return row;
}

function readDebts(form) {
  return [...form.querySelectorAll('.debt-row')].map((row) => ({
    name: row.querySelector('[name=name]').value.trim(),
    balance: Number(row.querySelector('[name=balance]').value),
    apr: Number(row.querySelector('[name=apr]').value),
    minPayment: Number(row.querySelector('[name=minPayment]').value),
  }));
}

function fundRow(f = ['', 'us-stock', '', '']) {
  const [name, category, er, balance] = f;
  const row = document.createElement('div');
  row.className = 'debt-row fund-row';
  const opts = Object.entries(T.fees.categories).map(([k, v]) => `<option value="${k}"${k === category ? ' selected' : ''}>${v}</option>`).join('');
  row.innerHTML = `
    <label>${T.fees.name}<input name="name" value="${escapeHtml(name)}" maxlength="50"></label>
    <label>${T.fees.category}<select name="category">${opts}</select></label>
    <label>${T.fees.er}<input name="er" type="number" min="0" max="5" step="any" value="${er}" required></label>
    <label>${T.fees.balance}<input name="balance" type="number" min="0" step="any" value="${balance}" required></label>
    <button type="button" class="link remove" aria-label="${F.removeAria}">${F.remove}</button>`;
  row.querySelector('.remove').addEventListener('click', () => { row.remove(); run(); });
  return row;
}

function readFunds(form) {
  return [...form.querySelectorAll('.fund-row')].map((row) => [
    row.querySelector('[name=name]').value.trim(), row.querySelector('[name=category]').value,
    row.querySelector('[name=er]').value, row.querySelector('[name=balance]').value]);
}

function renderFees(form) {
  const funds = readFunds(form).map(([name, category, er, balance]) => ({ name, category, expenseRatio: er === '' ? NaN : Number(er), balance: balance === '' ? NaN : Number(balance) }));
  const r = analyzeFees(funds, { monthly: Number(form.monthly.value || 0), years: Number(form.years.value || 30), annualReturn: Number(form.annualReturn.value || 0) });
  const rows = r.funds.map((f) => `<tr><td>${escapeHtml(f.name)}${f.cheaperInCategory ? `<small>${escapeHtml(T.fees.cheaper(f.cheaperInCategory.name, f.cheaperInCategory.expenseRatio))}</small>` : ''}</td><td>${f.expenseRatio}%</td><td>${money(f.yearlyFee, 2)}</td></tr>`).join('');
  return T.fees.result(r) + T.fees.table(rows) + T.fees.gap(r) + `<p class="note">${T.fees.note}</p>`;
}

function renderDebt(form) {
  const debts = readDebts(form);
  const extra = Number(form.extra.value || 0);
  const c = calc.compareDebtStrategies(debts, extra);
  const { avalanche: a, snowball: s } = c;
  if (!a.feasible) return T.debtInfeasible;
  const list = (r) => `<ol>${r.paidOff.map((p) => `<li>${T.debtPaidIn(escapeHtml(p.name), p.month)}</li>`).join('')}</ol>`;
  const printBtns = `<div class="row print-row"><button type="button" class="btn small" data-print="avalanche">${T.printAva}</button><button type="button" class="btn small ghost" data-print="snowball">${T.printSnow}</button></div>`;
  return T.debt(a, s, T.debtVerdict(c), list(a), list(s)) + debtChart(debts, extra) + printBtns;
}

// Avalanche vs snowball: total balance left each month, two lines.
function debtChart(debts, extra) {
  const series = ['avalanche', 'snowball'].map((strategy) => {
    const r = calc.debtPayoff(debts, { extra, strategy, schedule: true });
    return [debts.reduce((t, d) => t + (Number(d.balance) || 0), 0), ...r.schedule.map((row) => row.balances.reduce((t, b) => t + b, 0))];
  });
  const [ava, snow] = series;
  const months = Math.max(ava.length, snow.length) - 1;
  if (months < 1) return '';
  const w = 600, h = 200, pad = 8;
  const max = Math.max(...ava, ...snow, 1);
  const x = (i) => pad + (i / months) * (w - pad * 2);
  const y = (v) => h - pad - (v / max) * (h - pad * 2);
  const path = (pts) => pts.map((v, i) => `${i ? 'L' : 'M'}${x(i).toFixed(1)},${y(v).toFixed(1)}`).join(' ');
  return `<h3>${X.debtChartTitle}</h3><svg class="chart" viewBox="0 0 ${w} ${h}" role="img" aria-label="${escapeHtml(X.debtChart(money(ava[0]), months))}">
    <path d="${path(snow)}" class="line-in"/><path d="${path(ava)}" class="line-total"/></svg>
    <p class="legend chart-axis"><span>${X.debtChartNow}</span><span>${X.debtChartEnd(months)}</span></p>
    <p class="legend"><span class="key total"></span> ${X.debtLegendA} <span class="key in"></span> ${X.debtLegendS}${ava.join() === snow.join() ? ` · ${X.debtSame}` : ''}</p>`;
}

function printPlan(strategy) {
  const form = $('#calc-form');
  const r = calc.debtPayoff(readDebts(form), { extra: Number(form.extra.value || 0), strategy, schedule: true });
  if (!r.feasible) return;
  const now = new Date();
  const label = (m) => new Date(now.getFullYear(), now.getMonth() + m, 1).toLocaleDateString(lang === 'es' ? 'es-US' : 'en-US', { month: 'short', year: 'numeric' });
  const head = r.names.map((n) => `<th>${escapeHtml(n)}</th>`).join('');
  const body = r.schedule.map((row) => `<tr><td>☐ ${label(row.month)}</td>${row.payments.map((p, i) => `<td>${p ? money(p, 2) : ''}<small>${row.balances[i] ? `${money(row.balances[i])} ${T.planLeft}` : row.payments[i] ? '✓' : ''}</small></td>`).join('')}</tr>`).join('');
  let box = $('#print-plan');
  if (!box) { box = document.createElement('section'); box.id = 'print-plan'; document.body.append(box); }
  box.innerHTML = `<h1>${T.planTitle(strategy)}</h1><p>${T.planIntro(r)}</p>
    <table><thead><tr><th>${T.planMonth}</th>${head}</tr></thead><tbody>${body}</tbody></table><p class="tiny">${T.planFooter}</p>`;
  window.print();
}

// ---------- shared UI ----------
function lineChart(rows) {
  const w = 600, h = 200, pad = 8;
  const max = Math.max(...rows.map((r) => r.balance), 1);
  const x = (i) => pad + (i / Math.max(rows.length - 1, 1)) * (w - pad * 2);
  const y = (v) => h - pad - (v / max) * (h - pad * 2);
  const path = (key) => rows.map((r, i) => `${i ? 'L' : 'M'}${x(i).toFixed(1)},${y(r[key]).toFixed(1)}`).join(' ');
  return `<svg class="chart" viewBox="0 0 ${w} ${h}" role="img" aria-label="${T.chartLabel(money(rows[0].balance), money(rows.at(-1).balance))}">
    <path d="${path('balance')}" class="line-total"/><path d="${path('contributed')}" class="line-in"/></svg>
    <p class="legend"><span class="key total"></span> ${T.legendTotal} <span class="key in"></span> ${T.legendIn}</p>`;
}

function offerHtml(key) {
  const blocks = [];
  if (new URLSearchParams(location.search).get('embed') === '1' && !config.embed.showOffers) return '';
  const affBase = config.affiliates[key];
  const aff = affBase && lang === 'es' && affBase.es ? { ...affBase, ...affBase.es } : affBase;
  if (aff && isLiveUrl(aff.url)) {
    blocks.push(`<div class="offer"><h3>${T.nextStep}</h3><p>${escapeHtml(aff.blurb)}</p>
      <a class="btn" href="${escapeHtml(aff.url)}" rel="sponsored noopener" target="_blank" data-event="affiliate-${key}">${escapeHtml(aff.label)}</a>
      <p class="tiny">${T.affiliateNote}</p></div>`);
  }
  const product = lang === 'es' ? config.product.es : config.product;
  if (product && isLiveUrl(product.url)) {
    blocks.push(`<div class="offer"><h3>${escapeHtml(product.name)} (${escapeHtml(product.price)})</h3><p>${escapeHtml(product.pitch)}</p>
      <a class="btn alt" href="${escapeHtml(product.url)}" data-event="product">${T.getIt}</a></div>`);
  }
  return blocks.join('');
}

function setupSignup() {
  const form = $('form.signup');
  if (!form) return;
  const e = lang === 'es' ? { ...config.email, ...config.email.es } : config.email;
  $('.signup-pitch', form.parentElement).textContent = e.pitch;
  if (e.provider === 'none') { form.parentElement.hidden = true; return; }
  if (e.provider !== 'netlify') {
    form.removeAttribute('data-netlify');
    form.action = e.action || '#';
    form.querySelector('input[type=email]').name = e.emailField || 'email';
  }
  form.addEventListener('submit', async (ev) => {
    if (form.website.value) { ev.preventDefault(); return; } // honeypot
    if (e.provider !== 'netlify' && !e.action) { ev.preventDefault(); alert(T.notConnected); return; }
    ev.preventDefault();
    const btn = form.querySelector('button');
    btn.disabled = true; btn.textContent = T.sending;
    const body = new URLSearchParams(new FormData(form)).toString();
    try {
      await fetch(e.provider === 'netlify' ? '/' : form.action, {
        method: 'POST', mode: e.provider === 'netlify' ? 'same-origin' : 'no-cors',
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' }, body,
      });
      window.location.href = new URL(e.thanksUrl, new URL(document.body.dataset.root || './', location.href)).href;
    } catch { form.submit(); }
  });
}

function setupAnalytics() {
  initTracking({ config, app: 'money-calculators', page: document.body.dataset.calc || 'index' });
}

let run = () => {};

function readValues(form, fields) {
  const v = {};
  for (const [name] of fields) v[name] = form[name].value === '' ? undefined : Number(form[name].value);
  return v;
}

function writeUrl(values) {
  const url = new URL(location.href);
  const keep = ['embed', 'brand', 'frame'].filter((k) => url.searchParams.has(k)).map((k) => [k, url.searchParams.get(k)]);
  url.search = new URLSearchParams([...keep, ...Object.entries(values)]).toString();
  history.replaceState(null, '', url);
}

function mountCalculator(id) {
  const form = $('#calc-form');
  const out = $('#result');
  const offers = $('#offers');
  const qs = new URLSearchParams(location.search);

  if (id === 'debt-payoff') {
    const rows = $('#debts');
    let initial = DEFAULT_DEBTS();
    try { if (qs.get('d')) initial = JSON.parse(qs.get('d')); } catch { /* bad share link: use defaults */ }
    initial.slice(0, 15).forEach((d) => rows.append(debtRow(d)));
    if (qs.get('extra')) form.extra.value = qs.get('extra');
    $('#add-debt').addEventListener('click', () => { rows.append(debtRow()); });
    run = () => {
      try {
        out.innerHTML = renderDebt(form);
        writeUrl({ d: JSON.stringify(readDebts(form)), extra: form.extra.value });
      } catch (err) { out.innerHTML = `<p class="error">${escapeHtml(err.message)}</p>`; }
    };
    offers.innerHTML = offerHtml('debt');
  } else if (id === '401k-fees') {
    const rows = $('#funds');
    let initial = T.fees.defaults;
    try { if (qs.get('f')) initial = JSON.parse(qs.get('f')); } catch { /* bad share link: use defaults */ }
    initial.slice(0, 20).forEach((f) => rows.append(fundRow(f)));
    for (const k of ['monthly', 'years', 'annualReturn']) if (qs.get(k)) form[k].value = qs.get(k);
    $('#add-fund').addEventListener('click', () => { rows.append(fundRow()); });
    run = () => {
      try {
        out.innerHTML = renderFees(form);
        writeUrl({ f: JSON.stringify(readFunds(form)), monthly: form.monthly.value, years: form.years.value, annualReturn: form.annualReturn.value });
      } catch (err) { out.innerHTML = `<p class="error">${escapeHtml(err.message)}</p>`; }
    };
    offers.innerHTML = offerHtml('fees');
  } else {
    const spec = CALCS[id];
    const holder = $('#fields');
    for (const [name, label, def, step = 1] of spec.fields) {
      const val = qs.has(name) ? qs.get(name) : def;
      holder.insertAdjacentHTML('beforeend',
        `<label>${label}<input name="${name}" type="number" step="${step}" min="0" value="${escapeHtml(val)}" inputmode="decimal"></label>`);
    }
    // One select ([name, label, options]) or several ([[name, label, options], ...]), shown above the number fields.
    const selects = !spec.select ? [] : Array.isArray(spec.select[0]) ? spec.select : [spec.select];
    for (const [name, label, options] of [...selects].reverse()) {
      const cur = qs.get(name) || options[0][0];
      holder.insertAdjacentHTML('afterbegin', `<label>${label}<select name="${name}">${options.map(([val, txt]) => `<option value="${val}"${val === cur ? ' selected' : ''}>${escapeHtml(txt)}</option>`).join('')}</select></label>`);
    }
    // Take-home pay: the custom rate box only matters when no state is picked.
    const syncState = () => { const st = form.state, rate = form.stateRate; if (st && rate) rate.closest('label').hidden = st.value !== 'custom'; };
    syncState();
    run = () => {
      try {
        const v = readValues(form, spec.fields);
        for (const [name] of selects) v[name] = form[name].value;
        syncState();
        out.innerHTML = spec.render(v);
        writeUrl(Object.fromEntries(Object.entries(v).filter(([, x]) => x !== undefined)));
      } catch (err) { out.innerHTML = `<p class="error">${escapeHtml(err.message)}</p>`; }
    };
    offers.innerHTML = offerHtml(spec.cta);
  }
  form.addEventListener('input', run);
  out.addEventListener('click', (e) => { const b = e.target.closest('[data-print]'); if (b) printPlan(b.dataset.print); });
  form.addEventListener('submit', (e) => { e.preventDefault(); run(); });
  $('#share')?.addEventListener('click', async () => {
    try { await navigator.clipboard.writeText(location.href); $('#share').textContent = T.copied; }
    catch { prompt(T.copyPrompt, location.href); }
  });
  run();
}

// Embed mode (?embed=1): just the calculator, a credit link, and height messages for embed.js.
const params = new URLSearchParams(location.search);
const embedded = params.get('embed') === '1';
if (embedded) {
  const opt = embedOptions(params, document.referrer, config.embed);
  const root = document.documentElement;
  root.classList.add('embed');
  if (opt.theme !== 'auto') root.classList.add(`theme-${opt.theme}`);
  if (opt.accent) { root.style.setProperty('--gold', opt.accent); root.style.setProperty('--accent-ink', opt.accentInk); }
  if (opt.radius !== null) root.style.setProperty('--radius', `${opt.radius}px`);
  if (opt.licenceProblem) console.warn(`Calculator licence not applied (${opt.licenceProblem === 'domain' ? 'this site is not on the licence' : 'unknown key'}).`);
  const credit = document.createElement('p');
  credit.className = 'embed-credit';
  const href = withUtm(location.href.split('?')[0], { source: 'embed', medium: 'referral', campaign: document.body.dataset.calc || 'calculator' });
  credit.innerHTML = opt.showCredit
    ? `<a href="${href}" target="_blank" rel="noopener">${lang === 'es' ? 'Calculadora gratis de' : 'Free calculator by'} ${escapeHtml(config.brand)}</a>`
    : '';
  if (opt.cta) {
    const box = document.createElement('div');
    box.className = 'partner-cta';
    box.innerHTML = `<a class="btn" href="${escapeHtml(opt.cta.url)}" target="_top" rel="noopener">${escapeHtml(opt.cta.label)}</a>${opt.partner ? `<p class="tiny">${lang === 'es' ? 'De' : 'From'} ${escapeHtml(opt.partner)}</p>` : ''}`;
    document.querySelector('main').append(box);
  }
  document.querySelector('main').append(credit);
  const post = () => parent.postMessage({ type: 'mms-calc-height', id: params.get('frame') || '', height: document.documentElement.scrollHeight }, '*');
  new ResizeObserver(post).observe(document.body);
  post();
}

const id = document.body.dataset.calc;
if (id === 'debt-payoff' || id === '401k-fees' || CALCS[id]) mountCalculator(id);
setupSignup();
setupAnalytics();
for (const a of document.querySelectorAll('[data-brand]')) a.textContent = config.brand;
for (const a of document.querySelectorAll('a[data-site]')) a.href = config.siteUrl;
