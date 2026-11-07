// Browser glue for the rate calculator: reads the form, runs lib/rate.js, keeps inputs in the URL, and
// shows the Rate & Contract Kit card once its store link is live in config.js. Nothing typed is sent anywhere.
import config from '../config.js';
import { ratePlan } from '../lib/rate.js';
import { setupSignup } from '../signup.js';
import { setupSite, live } from '../site.js';

const $ = (s) => document.querySelector(s);
const money = (x) => '$' + Math.round(x).toLocaleString('en-US');
const pct = (x) => (x * 100).toFixed(1).replace(/\.0$/, '') + '%';
const FIELDS = ['takeHome', 'health', 'retirement', 'costs', 'weeks', 'hoursPerWeek', 'status', 'stateRate', 'dayHours'];

function read(form) {
  const v = {};
  for (const k of FIELDS) v[k] = k === 'status' ? form.elements[k].value : parseFloat(String(form.elements[k].value).replace(/[$,%\s]/g, '')) || 0;
  v.stateRate /= 100;
  return v;
}

function render(v) {
  const p = ratePlan(v);
  if (p.afterTax <= 0) return '<p class="big">Add your target</p><p>Enter the take-home pay you want per year.</p>';
  if (p.hours <= 0) return '<p class="big">Add your hours</p><p>Enter working weeks and billable hours per week.</p>';
  if (p.tooHigh) return '<p class="big">Over $400,000 of profit</p><p>At that level, an S corp and other planning change the answer. Talk to a CPA.</p>';
  const salaryHourly = v.takeHome / 2080;
  return `<p class="kicker">Your hourly floor</p><p class="big">${money(p.hourly)}/hour</p>
    <p class="note">Day rate (${v.dayHours || 6} hours): <b>${money(p.day)}</b>. The same take-home as a salary is about ${money(salaryHourly)} an hour over 2,080 hours.</p>
    <div class="two stats"><div><span>Revenue needed per year</span><b>${money(p.revenue)}</b></div><div><span>Billable hours per year</span><b>${p.hours.toLocaleString('en-US')}</b></div></div>
    <h3>How it adds up</h3>
    <table>
      <tr><td>Take-home + health + retirement</td><td class="r">${money(p.afterTax)}</td></tr>
      <tr><td>Profit needed before tax</td><td class="r">${money(p.profit)}</td></tr>
      <tr><td>Federal tax on that (SE + income)</td><td class="r">${money(p.federal)}</td></tr>
      ${p.state ? `<tr><td>State tax (estimate)</td><td class="r">${money(p.state)}</td></tr>` : ''}
      <tr><td>+ business costs</td><td class="r">${money(v.costs)}</td></tr>
      <tr class="now"><td>Revenue needed</td><td class="r">${money(p.revenue)}</td></tr>
    </table>
    <h3>Then, every time a client pays</h3>
    <p>Move <b>${pct(Math.ceil(p.setAside * 100) / 100)}</b> to a tax savings account. That's what the tax on this profit works out to.</p>
    <p class="note">That's ${money(p.monthly)} of revenue a month, or ${money(p.weekly)} per working week. A floor, not a ceiling: if your market pays more, charge more.</p>`;
}

function kit() {
  const k = (config.upsells || []).find((u) => /Rate/.test(u.name) && live(u.url));
  if (!k) return;
  const box = $('#kit');
  box.className = 'offer';
  box.innerHTML = '<h3></h3><p></p><a class="btn alt" rel="noopener"></a>';
  box.querySelector('h3').textContent = `${k.name} · ${k.price}`;
  box.querySelector('p').textContent = k.pitch;
  const a = box.querySelector('a'); a.href = k.url; a.textContent = 'Get the kit';
  box.hidden = false;
}

function init() {
  const form = $('#rate-form');
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
  kit();
  setupSignup();
  setupSite();
  update();
}

init();
