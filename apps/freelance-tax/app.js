// Browser glue: reads the form, runs lib/tax.js, keeps inputs in the URL so results can be
// shared, and shows the tracker, signup and (live) affiliate offers. Nothing is sent anywhere.
import config from './config.js';
import { quarterlyPlan, nextPayment, TAX_YEAR } from './lib/tax.js';
import { setupSignup } from './signup.js';

const $ = (s, r = document) => r.querySelector(s);
const money = (x) => '$' + Math.round(x).toLocaleString('en-US');
const pct = (x) => (x * 100).toFixed(1).replace(/\.0$/, '') + '%';
const live = (url) => typeof url === 'string' && /^https?:\/\//.test(url) && !url.includes('REPLACE_ME');
const esc = (s) => String(s).replace(/[&<>"']/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));
const dateFmt = (d) => d.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric', timeZone: 'UTC' });

const FIELDS = ['profit', 'status', 'w2Wages', 'withholding', 'priorYearTax', 'priorYearAgi', 'paidSoFar', 'stateRate', 'nextQuarter'];

function read(form) {
  const v = {};
  for (const k of FIELDS) {
    const el = form.elements[k];
    if (!el) continue;
    v[k] = k === 'status' ? el.value : parseFloat(String(el.value).replace(/[$,%\s]/g, '')) || 0;
  }
  v.stateRate = v.stateRate / 100;
  return v;
}

function render(v) {
  const p = quarterlyPlan(v);
  if (p.profit <= 0) return '<p class="big">Add your profit</p><p>Enter what you expect to earn this year minus business expenses.</p>';
  const q = p.nextQuarter;
  const headline = q <= 4
    ? `<p class="kicker">Pay by ${dateFmt(p.schedule[q - 1].date)} (${p.schedule[q - 1].label})</p><p class="big">${money(p.thisPayment)}</p>`
    : `<p class="kicker">All ${TAX_YEAR} deadlines have passed</p><p class="big">${money(Math.max(0, p.total - v.withholding - v.paidSoFar))}</p><p>Pay what's left when you file. Paying sooner reduces any penalty.</p>`;
  const why = p.method === 'safe-harbor'
    ? `Based on the <b>prior-year safe harbor</b>: ${p.safeHarborRate > 1 ? '110' : '100'}% of last year's tax (${money(p.safeHarbor)}), which is less than 90% of this year's estimate (${money(p.currentYear)}). Paying this on time generally avoids the underpayment penalty.`
    : `Based on <b>90% of this year's estimated tax</b> (${money(p.currentYear)})${p.safeHarbor !== null ? `, which is less than the prior-year safe harbor (${money(p.safeHarbor)})` : ' (add last year\'s total tax to compare the safe harbor)'}.`;
  const rows = p.schedule.map((d) => `<tr${d.q === q ? ' class="now"' : ''}><td>${d.label} · ${dateFmt(d.date)}</td><td>${d.covers}</td><td class="r">${money(d.cumulativeRequired)}</td></tr>`).join('');
  return `
    ${headline}
    <p class="note">${why}${v.paidSoFar ? ` Already paid this year: ${money(v.paidSoFar)}.` : ''}${p.needFromEstimates <= 0 ? ' Your withholding already covers it.' : ''}</p>
    <div class="two stats">
      <div><span>Full-year federal tax</span><b>${money(p.total)}</b></div>
      <div><span>Effective rate on profit</span><b>${pct(p.effectiveRate)}</b></div>
      <div><span>Self-employment tax</span><b>${money(p.seTax)}</b></div>
      <div><span>Income tax</span><b>${money(p.incomeTax)}</b></div>
    </div>
    <h3>Set aside from every payment</h3>
    <p class="setaside">${pct(Math.ceil(p.setAsideRate * 100) / 100)}</p>
    <p class="note">Federal${p.state ? ' plus your state estimate' : ''}, as a share of profit. Round up for a cushion.</p>
    <h3>Required by each deadline (total so far)</h3>
    <table><tr><th>Deadline</th><th>Covers</th><th class="r">Paid by then</th></tr>${rows}</table>
    ${p.balanceAtFiling > 0 ? `<p class="note">Still due when you file in April: about <b>${money(p.balanceAtFiling)}</b>${p.state ? ` federal, plus about ${money(p.state)} state for the year` : ''}. Keep saving for it.</p>` : ''}
    <details><summary>How this was worked out</summary>
      <p>Profit ${money(p.profit)} × 92.35% = ${money(p.netEarnings)} net earnings → SE tax ${money(p.seTax)}.
      AGI ${money(p.agi)} (profit − half of SE tax${v.w2Wages ? ' + wages' : ''}) − standard deduction ${money(p.standardDeduction)}
      − QBI deduction ${money(p.qbi)} = taxable income ${money(p.taxable)} → income tax ${money(p.incomeTax)}.</p>
      <p>Assumes ${TAX_YEAR} federal figures, Schedule C, the standard deduction, no credits and income below the QBI threshold. Weekend or holiday deadlines move to the next business day.</p>
    </details>`;
}

function offers() {
  const out = [];
  const pr = config.product;
  if (live(pr.url)) out.push(`<div class="offer product"><h3>${esc(pr.name)} · ${esc(pr.price)}</h3><p>${esc(pr.pitch)}</p><a class="btn" href="${esc(pr.url)}" rel="noopener">Get the tracker</a></div>`);
  const affs = Object.values(config.affiliates).filter((a) => live(a.url));
  for (const a of affs) out.push(`<div class="offer"><h3>${esc(a.label)}</h3><p>${esc(a.blurb)}</p><a class="btn alt" href="${esc(a.url)}" rel="sponsored noopener">See the offer</a></div>`);
  if (affs.length) out.push('<p class="tiny">Affiliate links: we may earn a commission if you sign up, at no extra cost to you.</p>');
  return out.join('');
}

function init() {
  const form = $('#calc-form');
  const params = new URLSearchParams(location.search);
  for (const k of FIELDS) if (params.has(k) && form.elements[k]) form.elements[k].value = params.get(k);
  if (!params.has('nextQuarter')) form.elements.nextQuarter.value = String(Math.min(nextPayment(new Date()), 5));
  const update = () => {
    $('#result').innerHTML = render(read(form));
    const qs = new URLSearchParams(FIELDS.map((k) => [k, form.elements[k].value]));
    history.replaceState(null, '', '?' + qs.toString());
  };
  form.addEventListener('input', update);
  form.addEventListener('change', update);
  $('#share').addEventListener('click', async () => {
    try { await navigator.clipboard.writeText(location.href); $('#share').textContent = 'Link copied'; } catch { /* clipboard blocked */ }
  });
  $('#offers').innerHTML = offers();
  setupSignup();
  if (config.analytics.plausibleDomain) {
    const s = document.createElement('script');
    s.defer = true; s.dataset.domain = config.analytics.plausibleDomain; s.src = 'https://plausible.io/js/script.js';
    document.head.appendChild(s);
  }
  update();
}

init();
