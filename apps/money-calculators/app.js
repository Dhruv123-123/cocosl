// Browser glue: builds each calculator's form, runs the math from lib/calc.js,
// keeps inputs in the URL so results can be shared, and shows the right offer.
import config from './config.js';
import * as calc from './lib/calc.js';
import { money, isLiveUrl, escapeHtml } from './lib/format.js';
import { TEXT } from './lib/text.js';

const $ = (sel, root = document) => root.querySelector(sel);

const lang = document.documentElement.lang.startsWith('es') ? 'es' : 'en';
const T = TEXT[lang];
const F = T.fields;

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
    fields: [['monthlyExpenses', F.monthlyExpenses, 2000], ['monthsTarget', F.monthsTarget, 3], ['currentSaved', F.currentSaved, 500], ['monthlySave', F.monthlySave, 250], ['apy', F.apy, 4, 0.01]],
    render(v) {
      const r = calc.emergencyFund(v);
      if (r.gap === 0) return T.efDone(r);
      if (!r.reachable) return T.efNoSave(r);
      return T.ef(v, r) + (r.starterGoal < r.target ? T.efStarter(r) : '');
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

function renderDebt(form) {
  const debts = readDebts(form);
  const extra = Number(form.extra.value || 0);
  const c = calc.compareDebtStrategies(debts, extra);
  const { avalanche: a, snowball: s } = c;
  if (!a.feasible) return T.debtInfeasible;
  const list = (r) => `<ol>${r.paidOff.map((p) => `<li>${T.debtPaidIn(escapeHtml(p.name), p.month)}</li>`).join('')}</ol>`;
  return T.debt(a, s, T.debtVerdict(c), list(a), list(s));
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
  const d = config.analytics.plausibleDomain;
  if (!d) return;
  const s = document.createElement('script');
  s.defer = true; s.dataset.domain = d; s.src = 'https://plausible.io/js/script.js';
  document.head.append(s);
}

let run = () => {};

function readValues(form, fields) {
  const v = {};
  for (const [name] of fields) v[name] = form[name].value === '' ? undefined : Number(form[name].value);
  return v;
}

function writeUrl(params) {
  const url = new URL(location.href);
  url.search = new URLSearchParams(params).toString();
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
  } else {
    const spec = CALCS[id];
    const holder = $('#fields');
    for (const [name, label, def, step = 1] of spec.fields) {
      const val = qs.has(name) ? qs.get(name) : def;
      holder.insertAdjacentHTML('beforeend',
        `<label>${label}<input name="${name}" type="number" step="${step}" min="0" value="${escapeHtml(val)}" inputmode="decimal"></label>`);
    }
    run = () => {
      try {
        const v = readValues(form, spec.fields);
        out.innerHTML = spec.render(v);
        writeUrl(Object.fromEntries(Object.entries(v).filter(([, x]) => x !== undefined)));
      } catch (err) { out.innerHTML = `<p class="error">${escapeHtml(err.message)}</p>`; }
    };
    offers.innerHTML = offerHtml(spec.cta);
  }
  form.addEventListener('input', run);
  form.addEventListener('submit', (e) => { e.preventDefault(); run(); });
  $('#share')?.addEventListener('click', async () => {
    try { await navigator.clipboard.writeText(location.href); $('#share').textContent = T.copied; }
    catch { prompt(T.copyPrompt, location.href); }
  });
  run();
}

const id = document.body.dataset.calc;
if (id) mountCalculator(id);
setupSignup();
setupAnalytics();
for (const a of document.querySelectorAll('[data-brand]')) a.textContent = config.brand;
for (const a of document.querySelectorAll('a[data-site]')) a.href = config.siteUrl;
