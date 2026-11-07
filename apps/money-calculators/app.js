// Browser glue: builds each calculator's form, runs the math from lib/calc.js,
// keeps inputs in the URL so results can be shared, and shows the right offer.
import config from './config.js';
import * as calc from './lib/calc.js';
import { money, duration, isLiveUrl, escapeHtml } from './lib/format.js';

const $ = (sel, root = document) => root.querySelector(sel);

const CALCS = {
  'compound-interest': {
    cta: 'brokerage',
    fields: [
      ['initial', 'Starting amount ($)', 1000],
      ['monthly', 'Added each month ($)', 200],
      ['annualRate', 'Yearly return (%)', 7, 0.1],
      ['years', 'Years', 30],
    ],
    render(v) {
      const r = calc.compoundGrowth(v);
      return `
        <p class="big">${money(r.finalBalance)}</p>
        <p>After ${v.years} years you would have put in <b>${money(r.totalContributed)}</b> and growth would add
        <b>${money(r.totalGrowth)}</b>. That growth share is ${Math.round((r.totalGrowth / Math.max(r.finalBalance, 1)) * 100)}% of the total.</p>
        ${lineChart(r.rows)}
        <p class="note">Assumes a steady ${v.annualRate}% a year, compounded monthly. Real returns go up and down, and are not guaranteed.</p>`;
    },
  },

  'emergency-fund': {
    cta: 'hysa',
    fields: [
      ['monthlyExpenses', 'Essential monthly costs ($)', 2000],
      ['monthsTarget', 'Months to cover', 3],
      ['currentSaved', 'Already saved ($)', 500],
      ['monthlySave', 'You can save each month ($)', 250],
      ['apy', 'Savings APY (%)', 4, 0.01],
    ],
    render(v) {
      const r = calc.emergencyFund(v);
      if (r.gap === 0) return `<p class="big">You're there</p><p>Your ${money(r.target)} goal is already covered. Keep it somewhere boring, insured and separate from spending money.</p>`;
      if (!r.reachable) return `<p class="big">Add a monthly amount</p><p>Your goal is ${money(r.target)}. Even $25 a week gets you moving.</p>`;
      const starter = r.starterGoal < r.target ? `<p>First milestone: <b>${money(r.starterGoal)}</b>. It covers most surprise bills and is the hardest part.</p>` : '';
      return `
        <p class="big">${duration(r.months)}</p>
        <p>That's how long until you have <b>${money(r.target)}</b> (${v.monthsTarget} months of costs). You need ${money(r.gap)} more.</p>
        ${starter}`;
    },
  },

  'savings-interest': {
    cta: 'hysa',
    fields: [
      ['balance', 'Savings balance ($)', 5000],
      ['monthlyDeposit', 'Added each month ($)', 100],
      ['apy', 'High-yield APY (%)', 4, 0.01],
      ['compareApy', 'Your current APY (%)', 0.01, 0.01],
      ['months', 'Months', 12],
    ],
    render(v) {
      const r = calc.savingsInterest(v);
      return `
        <p class="big">+${money(r.difference, 2)}</p>
        <p>At ${v.apy}% APY you'd earn <b>${money(r.interest, 2)}</b> in interest over ${duration(v.months)}, versus
        <b>${money(r.compareInterest, 2)}</b> at ${v.compareApy}%.</p>
        <p class="note">APYs change. Check the current rate and that the bank is FDIC insured (or the credit union NCUA insured).</p>`;
    },
  },

  'credit-card-minimum': {
    cta: 'debt',
    fields: [
      ['balance', 'Card balance ($)', 5000],
      ['apr', 'APR (%)', 22.99, 0.01],
      ['minPercent', 'Minimum: % of balance + interest', 1, 0.1],
      ['minFloor', 'Minimum payment floor ($)', 25],
      ['fixedPayment', 'What if you paid each month ($)', 250],
    ],
    render(v) {
      const r = calc.minimumPaymentTrap(v);
      const m = r.minimumOnly;
      let fixed = '';
      if (r.fixed) {
        fixed = Number.isFinite(r.fixed.months)
          ? `<p>Paying a flat <b>${money(v.fixedPayment)}</b> a month clears it in <b>${duration(r.fixed.months)}</b> with ${money(r.fixed.interest)} interest.
             You'd keep <b>${money(r.interestSaved)}</b>.</p>`
          : `<p>${money(v.fixedPayment)} a month doesn't cover the interest, so the balance would never shrink.</p>`;
      }
      return `
        <p class="big">${duration(m.months)}</p>
        <p>That's how long the minimum payment takes. You'd pay <b>${money(m.interest)}</b> in interest, ${money(m.paid)} in total.</p>
        ${fixed}
        <p class="note">Card issuers calculate minimums differently. Your statement's "minimum payment warning" box shows your card's real numbers.</p>`;
    },
  },

  'roth-vs-traditional': {
    cta: 'brokerage',
    fields: [
      ['annualContribution', 'Yearly contribution, before tax ($)', 6000],
      ['currentRate', 'Your tax bracket now (%)', 22],
      ['retirementRate', 'Expected tax rate in retirement (%)', 15],
      ['years', 'Years until you withdraw', 35],
      ['annualReturn', 'Yearly return (%)', 7, 0.1],
    ],
    render(v) {
      const r = calc.rothVsTraditional(v);
      const head = r.winner === 'tie' ? "It's a tie" : r.winner === 'roth' ? 'Roth comes out ahead' : 'Traditional comes out ahead';
      return `
        <p class="big">${head}</p>
        <p>After tax: Roth <b>${money(r.roth)}</b>, Traditional <b>${money(r.traditional)}</b>${r.winner === 'tie' ? '' : `, a difference of <b>${money(r.difference)}</b>`}.</p>
        <p>The one question that decides it: <b>is your tax rate higher now, or later?</b> Higher now favours Traditional. Higher later favours Roth. Unsure? Many people split contributions.</p>
        <p class="note">Simplified: same pre-tax dollars, flat tax rates, no employer match or income limits. Check IRS contribution and income limits for the current year.</p>`;
    },
  },
};

// ---------- debt payoff (dynamic rows) ----------
const DEFAULT_DEBTS = [
  { name: 'Credit card', balance: 3200, apr: 24.99, minPayment: 95 },
  { name: 'Store card', balance: 650, apr: 29.99, minPayment: 30 },
  { name: 'Car loan', balance: 7800, apr: 6.9, minPayment: 230 },
];

function debtRow(d = { name: '', balance: '', apr: '', minPayment: '' }) {
  const row = document.createElement('div');
  row.className = 'debt-row';
  row.innerHTML = `
    <label>Name<input name="name" value="${escapeHtml(d.name)}" maxlength="40"></label>
    <label>Balance ($)<input name="balance" type="number" min="0" step="any" value="${d.balance}" required></label>
    <label>APR (%)<input name="apr" type="number" min="0" max="100" step="any" value="${d.apr}" required></label>
    <label>Minimum ($)<input name="minPayment" type="number" min="0" step="any" value="${d.minPayment}" required></label>
    <button type="button" class="link remove" aria-label="Remove this debt">Remove</button>`;
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
  if (!a.feasible) return `<p class="big">Not paid off at this budget</p><p>The payments don't outrun the interest. Raise the extra amount, or look at a lower-rate option.</p>`;
  const list = (r) => `<ol>${r.paidOff.map((p) => `<li>${escapeHtml(p.name)}: paid off in ${duration(p.month)}</li>`).join('')}</ol>`;
  const verdict = c.interestSaved > 0
    ? `Avalanche saves <b>${money(c.interestSaved)}</b> in interest${c.monthsSaved > 0 ? ` and ${duration(c.monthsSaved)}` : ''}. Snowball gives you quicker wins. Pick the one you'll stick with.`
    : 'Both orders cost about the same here, so go with snowball for the quick wins.';
  return `
    <p class="big">Debt-free in ${duration(a.months)}</p>
    <p>Paying <b>${money(a.budget)}</b> a month in total. ${verdict}</p>
    <div class="two">
      <div><h3>Avalanche (highest APR first)</h3><p>${money(a.totalInterest)} interest, ${duration(a.months)}</p>${list(a)}</div>
      <div><h3>Snowball (smallest balance first)</h3><p>${money(s.totalInterest)} interest, ${duration(s.months)}</p>${list(s)}</div>
    </div>`;
}

// ---------- shared UI ----------
function lineChart(rows) {
  const w = 600, h = 200, pad = 8;
  const max = Math.max(...rows.map((r) => r.balance), 1);
  const x = (i) => pad + (i / Math.max(rows.length - 1, 1)) * (w - pad * 2);
  const y = (v) => h - pad - (v / max) * (h - pad * 2);
  const path = (key) => rows.map((r, i) => `${i ? 'L' : 'M'}${x(i).toFixed(1)},${y(r[key]).toFixed(1)}`).join(' ');
  return `<svg class="chart" viewBox="0 0 ${w} ${h}" role="img" aria-label="Balance grows from ${money(rows[0].balance)} to ${money(rows.at(-1).balance)}">
    <path d="${path('balance')}" class="line-total"/><path d="${path('contributed')}" class="line-in"/></svg>
    <p class="legend"><span class="key total"></span> Total balance <span class="key in"></span> What you put in</p>`;
}

function offerHtml(key) {
  const blocks = [];
  const aff = config.affiliates[key];
  if (aff && isLiveUrl(aff.url)) {
    blocks.push(`<div class="offer"><h3>Next step</h3><p>${escapeHtml(aff.blurb)}</p>
      <a class="btn" href="${escapeHtml(aff.url)}" rel="sponsored noopener" target="_blank" data-event="affiliate-${key}">${escapeHtml(aff.label)}</a>
      <p class="tiny">Affiliate link: we may earn a commission at no cost to you.</p></div>`);
  }
  if (isLiveUrl(config.product.url)) {
    blocks.push(`<div class="offer"><h3>${escapeHtml(config.product.name)} (${escapeHtml(config.product.price)})</h3><p>${escapeHtml(config.product.pitch)}</p>
      <a class="btn alt" href="${escapeHtml(config.product.url)}" data-event="product">Get it</a></div>`);
  }
  return blocks.join('');
}

function setupSignup() {
  const form = $('form.signup');
  if (!form) return;
  const e = config.email;
  $('.signup-pitch', form.parentElement).textContent = e.pitch;
  if (e.provider === 'none') { form.parentElement.hidden = true; return; }
  if (e.provider !== 'netlify') {
    form.removeAttribute('data-netlify');
    form.action = e.action || '#';
    form.querySelector('input[type=email]').name = e.emailField || 'email';
  }
  form.addEventListener('submit', async (ev) => {
    if (form.website.value) { ev.preventDefault(); return; } // honeypot
    if (e.provider !== 'netlify' && !e.action) { ev.preventDefault(); alert('Email signup is not connected yet: set email.action in config.js.'); return; }
    ev.preventDefault();
    const btn = form.querySelector('button');
    btn.disabled = true; btn.textContent = 'Sending…';
    const body = new URLSearchParams(new FormData(form)).toString();
    try {
      await fetch(e.provider === 'netlify' ? '/' : form.action, {
        method: 'POST', mode: e.provider === 'netlify' ? 'same-origin' : 'no-cors',
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' }, body,
      });
      window.location.href = e.thanksUrl;
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
    let initial = DEFAULT_DEBTS;
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
    try { await navigator.clipboard.writeText(location.href); $('#share').textContent = 'Link copied'; }
    catch { prompt('Copy this link', location.href); }
  });
  run();
}

const id = document.body.dataset.calc;
if (id) mountCalculator(id);
setupSignup();
setupAnalytics();
for (const a of document.querySelectorAll('[data-brand]')) a.textContent = config.brand;
for (const a of document.querySelectorAll('a[data-site]')) a.href = config.siteUrl;
