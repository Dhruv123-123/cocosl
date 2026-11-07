import config from './config.js';
import { initTracking } from './lib/track.js';
import { LETTERS, ERRORS, SURPRISE, buildLetter, suggest } from './lib/letters.js';

const $ = (s) => document.querySelector(s);
const esc = (s) => String(s ?? '').replace(/[&<>"']/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' })[c]);
const live = (u) => typeof u === 'string' && /^https:\/\//.test(u) && !/REPLACE_ME/i.test(u);
const KEY = 'mms-medical-letter-details';
const store = {
  get() { try { return JSON.parse(localStorage.getItem(KEY)) || {}; } catch { return {}; } },
  set(v) { try { localStorage.setItem(KEY, JSON.stringify(v)); } catch { /* private browsing */ } },
};

let kind = 'itemized';
let edited = false;

// Extra questions per letter.
const EXTRA = {
  itemized: () => '',
  dispute: () => `<fieldset><legend>What looks wrong? Tick all that apply.</legend>${Object.entries(ERRORS).map(([k, v]) => `<label class="pick"><input type="checkbox" name="errors" value="${k}"> ${esc(v)}</label>`).join('')}
    <label>Anything specific (line, date, amount) <textarea name="details" rows="3" placeholder="Line 14, 'CBC panel', billed twice on March 3"></textarea></label></fieldset>`,
  assistance: () => `<div class="grid"><label>People in your household <input name="household" type="number" min="1" max="20" inputmode="numeric"></label>
    <label>Household income a year, before tax ($) <input name="income" inputmode="decimal"></label></div>
    <p class="tiny">Optional. Many hospitals give free or discounted care below a set income, often a multiple of the federal poverty level. The policy will say.</p>`,
  surprise: () => `<fieldset><legend>Which fits your bill?</legend>${Object.entries(SURPRISE).map(([k, v], i) => `<label class="pick"><input type="radio" name="surprise" value="${k}"${i === 0 ? ' checked' : ''}> ${esc(v)}</label>`).join('')}
    <div class="grid"><label>Good Faith Estimate amount ($) <input name="estimate" inputmode="decimal"></label><label>Date on the bill <input name="billDate" placeholder="May 2, 2026"></label></div></fieldset>`,
};

function values() {
  const d = Object.fromEntries(new FormData($('#details')));
  const x = $('#extra-form');
  if (x) {
    const fd = new FormData(x);
    for (const [k, v] of fd) if (k !== 'errors') d[k] = v;
    d.errors = fd.getAll('errors');
  }
  return d;
}

function renderTabs() {
  const plan = suggest(Object.fromEntries([...new FormData($('#quiz'))].map(([k]) => [k, true])));
  $('#plan').innerHTML = `Send these, in this order: ${plan.map((k, i) => `<b>${i + 1}. ${esc(LETTERS[k])}</b>`).join(' then ')}.`;
  const order = [...plan, ...Object.keys(LETTERS).filter((k) => !plan.includes(k))];
  $('#tabs').innerHTML = order.map((k) => `<button type="button" role="tab" data-kind="${k}" aria-selected="${k === kind}" class="tab${plan.includes(k) ? ' suggested' : ''}">${esc(LETTERS[k])}</button>`).join('');
}

function renderExtra() {
  $('#extra').innerHTML = `<form id="extra-form">${EXTRA[kind]()}</form>`;
}

function renderLetter(force = false) {
  if (edited && !force) return;
  try {
    $('#letter').value = buildLetter(kind, values());
    $('#letter-msg').textContent = '';
  } catch (err) {
    $('#letter').value = '';
    $('#letter-msg').textContent = `${err.message} The letter appears here as you fill in the form.`;
  }
  edited = false;
}

function choose(k) {
  if (edited && !confirm('Switch letters? Your edits to this one will be lost (copy it first if you need it).')) return;
  kind = k;
  edited = false;
  renderTabs();
  renderExtra();
  renderLetter(true);
}

// Restore the details people typed before (on this device only).
const saved = store.get();
for (const [k, v] of Object.entries(saved)) if ($('#details')[k]) $('#details')[k].value = v;

$('#quiz').addEventListener('change', () => { const plan = suggest(Object.fromEntries([...new FormData($('#quiz'))].map(([k]) => [k, true]))); renderTabs(); if (!edited && plan[0] !== kind) choose(plan[0]); });
$('#tabs').addEventListener('click', (e) => { const b = e.target.closest('[data-kind]'); if (b && b.dataset.kind !== kind) choose(b.dataset.kind); });
$('#details').addEventListener('input', () => { store.set(Object.fromEntries(new FormData($('#details')))); renderLetter(); });
$('#extra').addEventListener('input', () => renderLetter());
$('#extra').addEventListener('change', () => renderLetter());
$('#letter').addEventListener('input', () => { edited = true; });

$('#copy').addEventListener('click', async () => {
  try { await navigator.clipboard.writeText($('#letter').value); $('#copy').textContent = 'Copied'; setTimeout(() => { $('#copy').textContent = 'Copy'; }, 1500); }
  catch { $('#letter').select(); }
});
$('#print').addEventListener('click', () => {
  let box = $('#print-letter');
  if (!box) { box = document.createElement('pre'); box.id = 'print-letter'; document.body.append(box); }
  box.textContent = $('#letter').value;
  window.print();
});
$('#download').addEventListener('click', () => {
  const a = document.createElement('a');
  a.href = URL.createObjectURL(new Blob([$('#letter').value.replace(/\n/g, '\r\n')], { type: 'text/plain' }));
  a.download = `${kind}-letter.txt`;
  document.body.append(a); a.click(); a.remove();
  setTimeout(() => URL.revokeObjectURL(a.href), 1000);
});

if (live(config.product.url)) {
  $('#product').innerHTML = `<h2>${esc(config.product.name)} (${esc(config.product.price)})</h2><p>${esc(config.product.pitch)}</p><a class="btn small" href="${esc(config.product.url)}">Get the pack</a>`;
  $('#product').hidden = false;
}
for (const a of document.querySelectorAll('[data-site]')) a.href = config.siteUrl;

// Email signup (Netlify Forms by default).
const form = document.querySelector('form.signup');
const e = config.email;
if (e.provider === 'none') form.closest('section').hidden = true;
else {
  if (e.provider !== 'netlify') { form.removeAttribute('data-netlify'); form.action = e.action || '#'; form.querySelector('input[type=email]').name = e.emailField || 'email'; }
  form.addEventListener('submit', async (ev) => {
    ev.preventDefault();
    if (form.website.value) return;
    if (e.provider !== 'netlify' && !e.action) { alert('Email signup is not connected yet: set email.action in config.js.'); return; }
    form.querySelector('button').disabled = true;
    try { await fetch(e.provider === 'netlify' ? '/' : form.action, { method: 'POST', mode: e.provider === 'netlify' ? 'same-origin' : 'no-cors', headers: { 'Content-Type': 'application/x-www-form-urlencoded' }, body: new URLSearchParams(new FormData(form)).toString() }); location.href = e.thanksUrl; }
    catch { form.submit(); }
  });
}

renderTabs();
renderExtra();
renderLetter(true);
initTracking({ config, app: 'medical-bills', page: 'letters' });
