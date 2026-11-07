// Browser glue for the January 15 page: reads the form, runs lib/q4.js, keeps inputs in the URL.
// Nothing typed is sent anywhere.
import { q4Plan } from '../lib/q4.js';
import { setupSignup } from '../signup.js';
import { setupSite } from '../site.js';

const $ = (s) => document.querySelector(s);
const money = (x) => '$' + Math.round(x).toLocaleString('en-US');
const FIELDS = ['profit', 'paidSoFar', 'status', 'priorYearTax', 'priorYearAgi', 'w2Wages', 'withholding'];

function read(form) {
  const v = {};
  for (const k of FIELDS) v[k] = k === 'status' ? form.elements[k].value : parseFloat(String(form.elements[k].value).replace(/[$,%\s]/g, '')) || 0;
  return v;
}

function render(v) {
  const p = q4Plan(v);
  if (p.profit <= 0) return '<p class="big">Add your profit</p><p>Enter your 2026 freelance income minus business expenses.</p>';
  const out = [`<p class="kicker">Pay by Fri, Jan 15, 2027 · tax year 2026</p><p class="big">${money(p.jan15)}</p>`];
  if (p.jan15 <= 0) out.push(`<p>Your payments${v.withholding ? ' and withholding' : ''} already cover the requirement for 2026. Nothing is needed on January 15.</p>`);
  else if (p.behind > 0) out.push(`<div class="two stats"><div><span>Q4's own share</span><b>${money(p.q4Share)}</b></div><div><span>Catch-up for earlier quarters</span><b>${money(p.behind)}</b></div></div><p class="note">The catch-up part was due by Sept 15. A small penalty has been running on it; paying now stops it growing.</p>`);
  out.push(`<p class="note">Based on ${p.method === 'safe-harbor' ? `the safe harbor: ${p.safeHarborRate > 1 ? '110' : '100'}% of your 2025 tax (${money(p.safeHarbor)})` : `90% of your 2026 tax (${money(p.currentYear)})${p.safeHarbor === null ? '. Add your 2025 total tax to compare the safe harbor' : ''}`}. Full-year 2026 federal tax: about ${money(p.total)}.</p>`);
  out.push(`<h3>Or: file and pay by Feb 1, 2027</h3><p>Pay the whole balance, about <b>${money(p.fileEarlyInstead)}</b>, with your return by February 1 and skip January 15.</p>`);
  if (p.afterJan15 > 0) out.push(`<h3>Still due in April</h3><p>About <b>${money(p.afterJan15)}</b> when you file. Keep it in your tax savings.</p>`);
  out.push(`<details><summary>How to pay</summary><p>irs.gov/payments → Direct Pay or your online account → Estimated Tax → 1040-ES → <b>2026</b>. Save the confirmation number.</p></details>`);
  return out.join('');
}

function init() {
  const form = $('#q4-form');
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
