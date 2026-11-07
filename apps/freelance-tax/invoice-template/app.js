// Browser glue for the invoice template: builds the line-item rows, renders a printable invoice from the
// form, shows what's missing, and keeps the draft in localStorage (this browser only). Nothing is sent.
import config from '../config.js';
import { TERMS, dueDate, longDate, totals, nextNumber, lateFeeLine, missing } from '../lib/invoice.js';
import { setupSignup } from '../signup.js';
import { setupSite, live } from '../site.js';

const $ = (s) => document.querySelector(s);
const esc = (s) => String(s ?? '').replace(/[&<>"]/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]));
const money = (x) => '$' + x.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 });
const KEY = '1099money-invoice';
const FIELDS = ['fromName', 'fromEmail', 'fromAddr', 'toName', 'toEmail', 'po', 'number', 'issued', 'terms', 'deposit', 'taxRate', 'lateFee', 'payHow', 'note'];
const form = $('#inv-form');
const body = $('#items tbody');

function addLine(it = {}) {
  const tr = document.createElement('tr');
  tr.innerHTML = '<td><input class="d" maxlength="160" placeholder="Website design, phase 1"></td><td><input class="q" inputmode="decimal"></td><td><input class="r" inputmode="decimal"></td><td><button type="button" aria-label="Remove line">×</button></td>';
  tr.querySelector('.d').value = it.desc || '';
  tr.querySelector('.q').value = it.qty ?? '';
  tr.querySelector('.r').value = it.rate ?? '';
  tr.querySelector('button').addEventListener('click', () => { tr.remove(); if (!body.children.length) addLine(); update(); });
  body.appendChild(tr);
}

function read() {
  const v = Object.fromEntries(FIELDS.map((k) => [k, form.elements[k].value]));
  v.items = [...body.children].map((tr) => ({ desc: tr.querySelector('.d').value, qty: tr.querySelector('.q').value, rate: tr.querySelector('.r').value }));
  return v;
}

function render(v) {
  const t = totals(v.items, v);
  const due = dueDate(v.issued, v.terms);
  const fee = lateFeeLine(v.lateFee, due);
  const rows = t.lines.map((l) => `<tr><td>${esc(l.desc)}</td><td class="n">${l.qty}</td><td class="n">${money(l.rate)}</td><td class="n">${money(l.amount)}</td></tr>`).join('');
  return `<h2>INVOICE</h2>
    <div class="meta">
      <div><b>${esc(v.fromName) || 'Your name'}</b><br>${esc(v.fromEmail)}${v.fromAddr ? '<br>' + esc(v.fromAddr) : ''}</div>
      <div><span class="small">Invoice</span> <b>${esc(v.number) || '—'}</b><br><span class="small">Date</span> ${esc(longDate(v.issued)) || '—'}<br>
        <span class="small">Due</span> <b>${esc(longDate(due)) || '—'}</b> <span class="small">(${esc(TERMS[v.terms]?.label || '')})</span>${v.po ? `<br><span class="small">PO</span> ${esc(v.po)}` : ''}</div>
    </div>
    <p><span class="small">Bill to</span><br><b>${esc(v.toName) || 'Client'}</b>${v.toEmail ? '<br>' + esc(v.toEmail) : ''}</p>
    <table><thead><tr><th>Description</th><th class="n">Qty</th><th class="n">Rate</th><th class="n">Amount</th></tr></thead>
    <tbody>${rows || '<tr><td colspan="4">Add a line of work</td></tr>'}</tbody></table>
    <table>
      <tr><td>Subtotal</td><td class="n">${money(t.subtotal)}</td></tr>
      ${t.tax ? `<tr><td>Sales tax</td><td class="n">${money(t.tax)}</td></tr>` : ''}
      ${t.deposit ? `<tr><td>Deposit received</td><td class="n">−${money(t.deposit)}</td></tr>` : ''}
      <tr class="total"><td>Amount due${due ? ' by ' + esc(longDate(due)) : ''}</td><td class="n">${money(t.due)}</td></tr>
    </table>
    ${v.payHow ? `<p><b>How to pay</b></p><p class="small">${esc(v.payHow)}</p>` : ''}
    ${fee ? `<p class="small">${esc(fee)}</p>` : ''}
    ${v.note ? `<p class="small">${esc(v.note)}</p>` : ''}`;
}

function check(v) {
  const m = missing(v);
  return m.length ? `<p><b>Before you send it, add:</b></p><ul class="ready">${m.map((x) => `<li>${esc(x)}</li>`).join('')}</ul>`
    : '<p class="ok">✓ Everything a client needs to pay you is on it.</p>';
}

function save(v) { try { localStorage.setItem(KEY, JSON.stringify(v)); } catch { /* storage blocked */ } }
function load() { try { return JSON.parse(localStorage.getItem(KEY) || 'null'); } catch { return null; } }

function update() {
  const v = read();
  $('#sheet').innerHTML = render(v);
  $('#check').innerHTML = check(v);
  save(v);
}

function more() {
  const parts = [];
  const tracker = config.tools && config.tools.invoiceTracker;
  if (live(tracker)) parts.push(`<p><b>Sent it?</b> Track when it's due, work out late fees and get a polite reminder email with the free <a href="${esc(tracker)}">invoice tracker</a>.</p>`);
  const kit = (config.upsells || []).find((u) => /Contract/.test(u.name) && live(u.url));
  if (kit) parts.push(`<div class="offer"><h3>${esc(kit.name)} · ${esc(kit.price)}</h3><p>${esc(kit.pitch)}</p><a class="btn alt" rel="noopener" href="${esc(kit.url)}">Get the kit</a></div>`);
  $('#more').innerHTML = parts.join('');
}

function init() {
  const saved = load();
  const today = new Date().toISOString().slice(0, 10);
  if (saved) for (const k of FIELDS) if (saved[k] != null) form.elements[k].value = saved[k];
  if (!form.elements.issued.value) form.elements.issued.value = today;
  (saved && saved.items && saved.items.length ? saved.items : [{}]).forEach(addLine);
  $('#add-line').addEventListener('click', () => { addLine(); update(); });
  $('#print').addEventListener('click', () => window.print());
  $('#next').addEventListener('click', () => {
    form.elements.number.value = nextNumber(form.elements.number.value);
    form.elements.issued.value = today;
    for (const k of ['toName', 'toEmail', 'po', 'note']) form.elements[k].value = '';
    form.elements.deposit.value = '0';
    body.innerHTML = ''; addLine(); update();
  });
  form.addEventListener('input', update);
  form.addEventListener('change', update);
  more();
  setupSignup();
  setupSite();
  update();
}

init();
