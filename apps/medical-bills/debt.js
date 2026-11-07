// Debt collector letters page (debt.html). Logic in lib/debt.js.
import config from './config.js';
import { initTracking } from './lib/track.js';
import { LETTERS, LIMITS, buildDebtLetter } from './lib/debt.js';

const $ = (s) => document.querySelector(s);
const esc = (s) => String(s ?? '').replace(/[&<>"']/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' })[c]);
const ABOUT = {
  validation: 'Start here. It disputes the debt and asks the collector to show it\'s yours and the amount is right. It does not admit you owe anything.',
  cease: 'The collector must stop contacting you (with narrow exceptions), but the debt doesn\'t go away and they can still sue or report it. Consider sending the validation letter first.',
};
let kind = 'validation';
let edited = false;

$('#limits').insertAdjacentHTML('beforeend', Object.entries(LIMITS).map(([k, v]) => `<label class="pick"><input type="checkbox" name="limits" value="${k}"> ${esc(v)}</label>`).join(''));

function values() {
  const fd = new FormData($('#details'));
  return { ...Object.fromEntries(fd), limits: fd.getAll('limits') };
}

function render(force = false) {
  $('#tabs').innerHTML = Object.entries(LETTERS).map(([k, v]) => `<button type="button" role="tab" class="tab" data-kind="${k}" aria-selected="${k === kind}">${esc(v)}</button>`).join('');
  $('#about').textContent = ABOUT[kind];
  if (edited && !force) return;
  try { $('#letter').value = buildDebtLetter(kind, values()); $('#letter-msg').textContent = ''; }
  catch (err) { $('#letter').value = ''; $('#letter-msg').textContent = `${err.message} The letter appears here as you fill in the form.`; }
  edited = false;
}

$('#tabs').addEventListener('click', (e) => {
  const b = e.target.closest('[data-kind]');
  if (!b || b.dataset.kind === kind) return;
  if (edited && !confirm('Switch letters? Your edits to this one will be lost.')) return;
  kind = b.dataset.kind;
  render(true);
});
$('#details').addEventListener('input', () => render());
$('#details').addEventListener('change', () => render());
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
  a.download = `debt-${kind}-letter.txt`;
  document.body.append(a); a.click(); a.remove();
  setTimeout(() => URL.revokeObjectURL(a.href), 1000);
});
for (const a of document.querySelectorAll('[data-site]')) a.href = config.siteUrl;

render(true);
initTracking({ config, app: 'medical-bills', page: 'debt-letters' });
