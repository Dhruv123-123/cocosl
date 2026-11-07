// Vendor payment check page (vendor/index.html). Logic in lib/vendor.js.
import config from './config.js';
import { initTracking } from './lib/track.js';
import * as V from './lib/vendor.js';

const $ = (s) => document.querySelector(s);
const esc = (s) => String(s ?? '').replace(/[&<>"']/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' })[c]);
const live = (u) => typeof u === 'string' && /^https:\/\//.test(u) && !/REPLACE_ME/i.test(u);
const form = $('#vendor-form');

$('#kinds').innerHTML = Object.entries(V.KINDS).map(([k, v], i) => `<label class="pick"><input type="radio" name="kind" value="${k}"${i === 0 ? ' checked' : ''}> ${esc(v)}</label>`).join('');
$('#flags').innerHTML = V.FLAGS.filter(([id]) => id !== 'replyTo').map(([id, , label]) => `<label class="pick"><input type="checkbox" name="flags" value="${id}"> ${esc(label)}</label>`).join('');

const TITLE = {
  high: 'Stop. Don\'t pay until you\'ve verified this by phone.',
  medium: 'Hold the payment and verify it first.',
  low: 'No strong warning signs.',
};

function show() {
  const fd = new FormData(form);
  const r = V.checkRequest({ kind: fd.get('kind'), known: fd.get('known'), sender: fd.get('sender'), replyTo: fd.get('replyTo'), flags: fd.getAll('flags') });
  const title = r.level === 'low' && r.hold ? TITLE.medium : TITLE[r.level];
  $('#result').innerHTML = `
    <div class="verdict ${r.level}">
      <p class="score">${esc(title)}</p>
      <div class="meter"><span style="width:${Math.max(6, r.score)}%"></span></div>
      <p class="tiny">Risk score ${r.score}/100, from the warning signs you ticked. A low score doesn't prove a request is real.</p>
    </div>
    ${r.reasons.length ? `<h3>Warning signs</h3><ul class="plain">${r.reasons.map((x) => `<li><b>${esc(x.label)}.</b> ${esc(x.why)}</li>`).join('')}</ul>` : ''}
    <h3>${r.hold ? 'Before you pay' : 'Good habits anyway'}</h3>
    <ol>${V.VERIFY_STEPS.map((s) => `<li>${esc(s)}</li>`).join('')}</ol>
    <details><summary>Already paid?</summary><ol>${V.IF_PAID.map((s) => `<li>${esc(s)}</li>`).join('')}</ol></details>`;
  $('#result').hidden = false;
  $('#result').scrollIntoView({ behavior: 'smooth', block: 'start' });
}

form.addEventListener('submit', (e) => { e.preventDefault(); show(); });
$('#example').addEventListener('click', () => {
  form.querySelector('[name=kind][value=bank-change]').checked = true;
  form.known.value = 'accounts@summitsupply.com';
  form.sender.value = 'accounts@summit-supply.co';
  form.replyTo.value = 'summit.ar.dept@gmail.com';
  for (const id of ['changedBank', 'urgent', 'newPhone']) form.querySelector(`[name=flags][value=${id}]`).checked = true;
  show();
});

const policy = () => V.policyText($('#biz').value);
const renderPolicy = () => { $('#policy').textContent = policy(); };
$('#biz').addEventListener('input', renderPolicy);
$('#print-policy').addEventListener('click', () => { document.body.classList.add('print-policy'); window.print(); document.body.classList.remove('print-policy'); });
$('#copy-policy').addEventListener('click', async () => {
  try { await navigator.clipboard.writeText(policy()); $('#copy-policy').textContent = 'Copied'; setTimeout(() => { $('#copy-policy').textContent = 'Copy'; }, 1500); } catch { /* select manually */ }
});
renderPolicy();

const pack = config.teamPack;
if (pack && live(pack.url)) {
  $('#pack').innerHTML = `<h2>Train your team in 20 minutes</h2><p>${esc(pack.pitch)}</p><p><a class="btn" href="${esc(pack.url)}" data-id="team-pack" target="_blank" rel="noopener">${esc(pack.name)}: ${esc(pack.price)}</a></p>`;
  $('#pack').hidden = false;
}

initTracking({ config, app: 'scam-checker', page: 'vendor-check' });
