// Freelancer invoice tracker page. Logic in lib/invoices.js.
import config from './config.js';
import { initTracking } from './lib/track.js';
import * as I from './lib/invoices.js';
import { buildIcs } from './lib/ics.js';
import { today as todayIs, prettyDay } from './lib/dates.js';

const $ = (s) => document.querySelector(s);
const esc = (s) => String(s ?? '').replace(/[&<>"']/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' })[c]);
const money = (n) => (Number(n) || 0).toLocaleString('en-US', { style: 'currency', currency: 'USD' });
const live = (u) => typeof u === 'string' && /^https:\/\//.test(u) && !/REPLACE_ME/i.test(u);
const plural = (n, w) => `${n} ${w}${n === 1 ? '' : 's'}`;
const KEY = 'money1099-invoices-v1';
const store = {
  get() { try { return localStorage.getItem(KEY); } catch { return null; } },
  set(v) { try { localStorage.setItem(KEY, v); return true; } catch { return false; } },
};
let book = I.loadBook(store.get());
const today = todayIs();
const form = $('#inv-form');
const save = () => { if (!store.set(JSON.stringify(book))) $('#data-msg').textContent = 'Could not save here (private browsing?). Use "Download backup" before closing.'; };

function download(name, text, type) {
  const a = document.createElement('a');
  a.href = URL.createObjectURL(new Blob([text], { type }));
  a.download = name; document.body.append(a); a.click(); a.remove();
  setTimeout(() => URL.revokeObjectURL(a.href), 1000);
}

// ---------- form ----------
$('#f-terms').innerHTML = Object.entries(I.TERMS).map(([k, v]) => `<option value="${k}"${k === '30' ? ' selected' : ''}>${esc(v)}</option>`).join('') + '<option value="custom">Pick a due date</option>';
$('#f-fee').innerHTML = Object.entries(I.FEE_TYPES).map(([k, v]) => `<option value="${k}">${esc(v)}</option>`).join('');
form.issued.value = today;
const toggles = () => {
  $('#due-wrap').hidden = form.terms.value !== 'custom';
  for (const el of form.querySelectorAll('.fee-percent')) el.hidden = form.feeType.value !== 'percent';
  for (const el of form.querySelectorAll('.fee-flat')) el.hidden = form.feeType.value !== 'flat';
  for (const el of form.querySelectorAll('.fee-any')) el.hidden = form.feeType.value === 'none';
};
form.terms.addEventListener('change', toggles);
form.feeType.addEventListener('change', toggles);
toggles();

form.addEventListener('submit', (e) => {
  e.preventDefault();
  const v = Object.fromEntries(new FormData(form));
  if (v.sentNow) v.sent = v.issued;
  try {
    const inv = I.addInvoice(book, v);
    save(); render();
    const keep = { terms: form.terms.value, feeType: form.feeType.value, feeRate: form.feeRate.value, grace: form.grace.value };
    form.reset(); form.issued.value = today;
    for (const [k, val] of Object.entries(keep)) form[k].value = val;
    toggles();
    $('#form-msg').textContent = `Added. Due ${prettyDay(inv.due)}.`;
  } catch (err) { $('#form-msg').textContent = err.message; }
});

// ---------- your details ----------
const me = $('#me-form');
for (const k of ['name', 'business', 'payHow']) me[k].value = book.me[k] || '';
me.addEventListener('input', () => { book.me = { name: me.name.value, business: me.business.value, payHow: me.payHow.value }; save(); });

// ---------- list ----------
const LABEL = { overdue: 'Overdue', 'due-today': 'Due today', 'due-soon': 'Due soon', sent: 'Sent', draft: 'Not sent yet', paid: 'Paid', 'written-off': 'Written off' };

function line(r) {
  const s = r.status;
  if (s.state === 'paid') return `Paid ${money(r.amount)} on ${prettyDay(s.paidDate)}${s.daysToPay !== null ? ` · ${plural(s.daysToPay, 'day')} after invoicing` : ''}`;
  if (s.state === 'written-off') return `Written off: ${money(s.owed)}`;
  const due = s.state === 'overdue' ? `<b class="neg">${plural(s.daysLate, 'day')} late</b> (due ${prettyDay(r.due)})` : s.state === 'due-today' ? '<b>Due today</b>' : `Due ${prettyDay(r.due)} · ${plural(s.daysLeft, 'day')} left`;
  const fee = s.fee > 0 ? ` · late fee ${money(s.fee)}${s.months ? ` (${s.months} × ${r.feeRate}%)` : ''} · <b>total ${money(s.total)}</b>` : '';
  return `${due} · owed ${money(s.owed)}${s.partly ? ` of ${money(r.amount)}` : ''}${fee}`;
}

function render() {
  const s = I.summary(book, today);
  $('#stats').innerHTML = `
    <div class="stat"><span>Waiting to be paid</span><b>${money(s.outstanding)}</b></div>
    <div class="stat"><span>Overdue</span><b class="${s.overdue ? 'neg' : ''}">${money(s.overdue)}</b><small>${plural(s.overdueCount, 'invoice')}</small></div>
    <div class="stat"><span>Late fees under your terms</span><b>${money(s.fees)}</b></div>
    <div class="stat"><span>Paid this year</span><b class="pos">${money(s.paidThisYear)}</b><small>${s.avgDaysToPay !== null ? `Clients take ${plural(s.avgDaysToPay, 'day')} on average` : ''}</small></div>`;
  const rows = I.board(book, today);
  $('#invoices').innerHTML = rows.length ? rows.map((r) => {
    const st = r.status.state;
    const stage = I.suggestedStage(r, today);
    const open = !['paid', 'written-off'].includes(st);
    const last = r.reminders.at(-1);
    return `<div class="bill inv" data-id="${r.id}">
      <div class="bill-head"><div><b>${esc(r.client)}</b>${r.number ? ` #${esc(r.number)}` : ''} <span class="state ${st}">${LABEL[st]}</span>
        <div class="tiny">${money(r.amount)}${r.project ? ` · ${esc(r.project)}` : ''} · invoiced ${prettyDay(r.issued)} · ${esc(I.TERMS[r.terms] || 'Custom due date')}</div></div>
        <button class="x" data-act="delete" aria-label="Delete invoice">×</button></div>
      <p>${line(r)}</p>
      ${last ? `<p class="tiny">Last reminder: ${esc(I.STAGES[last.stage] || last.stage)}, ${prettyDay(last.date)}</p>` : ''}
      ${open ? `<div class="actions">
        ${st === 'draft' ? '<button class="btn small" data-act="sent">Mark as sent today</button>' : `<button class="btn small${stage ? '' : ' ghost'}" data-act="remind" data-stage="${stage || 'before'}">${stage ? 'Write a reminder' : 'Reminder email'}</button>`}
        <button class="btn ghost small" data-act="paid">Paid in full</button>
        <button class="btn ghost small" data-act="partial">Part payment</button>
        ${st === 'overdue' ? '<button class="btn ghost small" data-act="writeoff">Write off</button>' : ''}
      </div>
      <form class="pay-form" data-pay hidden><input name="amount" inputmode="decimal" placeholder="Amount paid ($)" aria-label="Amount paid"><input name="date" type="date" value="${today}" max="${today}" aria-label="Date paid"><button class="btn small">Save payment</button></form>` : ''}
    </div>`;
  }).join('') : '<p class="tiny">No invoices yet. Add your first one above.</p>';
}

let current = null;
function openReminder(id, stage) {
  current = { id, stage };
  const inv = book.invoices.find((i) => i.id === id);
  const suggested = I.suggestedStage(inv, today);
  $('#stages').innerHTML = Object.entries(I.STAGES).map(([k, v]) => `<button type="button" role="tab" class="tab${k === suggested ? ' suggested' : ''}" data-stage="${k}" aria-selected="${k === stage}">${esc(v)}</button>`).join('');
  const email = I.reminderEmail(inv, stage, today, book.me);
  $('#rem-subject').value = email.subject;
  $('#rem-body').value = email.body;
  updateMail();
  if (!$('#reminder').open) $('#reminder').showModal();
}
function updateMail() {
  const inv = book.invoices.find((i) => i.id === current.id);
  $('#rem-mail').href = I.mailto(inv, { subject: $('#rem-subject').value, body: $('#rem-body').value });
}
$('#stages').addEventListener('click', (e) => { const b = e.target.closest('[data-stage]'); if (b) openReminder(current.id, b.dataset.stage); });
$('#rem-subject').addEventListener('input', updateMail);
$('#rem-body').addEventListener('input', updateMail);
$('#rem-copy').addEventListener('click', async () => {
  try { await navigator.clipboard.writeText(`Subject: ${$('#rem-subject').value}\n\n${$('#rem-body').value}`); $('#rem-copy').textContent = 'Copied'; setTimeout(() => { $('#rem-copy').textContent = 'Copy'; }, 1500); }
  catch { $('#rem-body').select(); }
});
$('#rem-log').addEventListener('click', () => { I.logReminder(book, current.id, current.stage, today); save(); render(); $('#reminder').close(); });

$('#invoices').addEventListener('click', (e) => {
  const b = e.target.closest('[data-act]');
  if (!b) return;
  const id = b.closest('[data-id]').dataset.id;
  const act = b.dataset.act;
  if (act === 'delete' && confirm('Delete this invoice from your tracker?')) { I.removeInvoice(book, id); }
  else if (act === 'sent') I.markSent(book, id, today);
  else if (act === 'paid') I.markPaid(book, id, today);
  else if (act === 'writeoff' && confirm('Mark this invoice as written off? You can still record a payment later.')) book.invoices.find((i) => i.id === id).writtenOff = true;
  else if (act === 'partial') { const f = b.closest('[data-id]').querySelector('[data-pay]'); f.hidden = !f.hidden; f.amount.focus(); return; }
  else if (act === 'remind') { openReminder(id, b.dataset.stage); return; }
  else return;
  save(); render();
});
$('#invoices').addEventListener('submit', (e) => {
  const f = e.target.closest('[data-pay]');
  if (!f) return;
  e.preventDefault();
  try { I.recordPayment(book, f.closest('[data-id]').dataset.id, f.amount.value, f.date.value); save(); render(); }
  catch (err) { $('#data-msg').textContent = err.message; }
});

$('#ics').addEventListener('click', () => {
  const events = I.reminderEvents(book, today);
  if (!events.length) { $('#data-msg').textContent = 'No upcoming due dates to add.'; return; }
  download('invoice-reminders.ics', buildIcs(events, { name: 'Invoice reminders' }), 'text/calendar');
  $('#data-msg').textContent = `Downloaded ${plural(events.length, 'reminder')}. Open the file to add them to your calendar.`;
});
$('#csv').addEventListener('click', () => download(`invoices-${today}.csv`, I.toCsv(book, today), 'text/csv'));
$('#backup').addEventListener('click', () => download(`invoices-backup-${today}.json`, JSON.stringify(book, null, 2), 'application/json'));
$('#restore').addEventListener('change', async (e) => {
  const f = e.target.files[0]; if (!f) return;
  const next = I.loadBook(await f.text());
  if (!confirm(`Replace what's on this device with the backup (${plural(next.invoices.length, 'invoice')})?`)) return;
  book = next; save(); render();
  for (const k of ['name', 'business', 'payHow']) me[k].value = book.me[k] || '';
  e.target.value = '';
});

const p = config.product;
if (p && live(p.url)) {
  $('#product').innerHTML = `<h2>Put your terms in writing</h2><p>${esc(p.pitch)}</p><p><a class="btn" href="${esc(p.url)}" data-id="rate-contract-kit" target="_blank" rel="noopener">${esc(p.name)}: ${esc(p.price)}</a></p>`;
  $('#product').hidden = false;
}
for (const a of document.querySelectorAll('[data-site]')) a.href = config.siteUrl;

render();
initTracking({ config, app: 'freelance-invoices', page: 'invoice-tracker' });
