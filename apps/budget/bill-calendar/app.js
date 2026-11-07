// Bill-due calendar app, English (index.html) and Spanish (es.html). Logic in ../lib/billcal.js.
// Bills and paid marks stay in this browser (localStorage); both languages share them.
import config from '../config.js';
import { initTracking } from '../lib/track.js';
import * as B from '../lib/billcal.js';
import { today as todayIso } from '../lib/dates.js';

const $ = (s) => document.querySelector(s);
const esc = (s) => String(s ?? '').replace(/[&<>"']/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' })[c]);
const es = document.documentElement.lang.startsWith('es');
const loc = es ? 'es-US' : 'en-US';
const money = (n, d = 2) => (Number(n) || 0).toLocaleString(loc, { style: 'currency', currency: 'USD', minimumFractionDigits: d, maximumFractionDigits: d });
const short = (n) => (n >= 1000 ? `$${(n / 1000).toFixed(n >= 10000 ? 0 : 1)}k` : `$${Math.round(n)}`);
const dayName = (d, o) => new Date(`${d}T12:00:00`).toLocaleDateString(loc, o);
const today = todayIso();

const T = es ? {
  freqs: { monthly: 'Cada mes', weekly: 'Cada semana', biweekly: 'Cada 2 semanas', quarterly: 'Cada 3 meses', yearly: 'Cada año', once: 'Una sola vez' },
  weekdays: ['Dom', 'Lun', 'Mar', 'Mié', 'Jue', 'Vie', 'Sáb'],
  stats: ['Vence este mes', 'Pagado', 'Falta pagar', 'Con pago automático'],
  none: 'No hay pagos este mes.', noBills: 'Todavía no hay recibos. Agrega el primero arriba.',
  paid: 'Pagado', auto: 'automático', overdue: 'vencido', due: 'vence',
  markPaid: (n) => `Marcar ${n} como pagado`,
  upcomingNone: 'Nada que pagar en los próximos 14 días.',
  overdueHead: (n) => `${n} pago${n === 1 ? '' : 's'} vencido${n === 1 ? '' : 's'}`,
  inDays: (n) => (n === 0 ? 'hoy' : n === 1 ? 'mañana' : `en ${n} días`),
  perMonth: (n) => `${money(n)} al mes`, del: (n) => `Borrar ${n}`, edit: (n) => `Editar ${n}`,
  confirmDel: (n) => `¿Borrar ${n} y todas sus marcas de pagado?`,
  added: (n) => `Agregado: ${n}.`, saved: (n) => `Guardado: ${n}.`, fix: 'Escribe un nombre, un monto y la fecha del próximo pago.',
  ics: (n) => `Se descargó un archivo con ${n} recibo${n === 1 ? '' : 's'}. Ábrelo para agregarlos a tu calendario; se repiten solos.`,
  icsNone: 'Agrega un recibo primero.', title: (b) => `Pagar ${b.name}`,
  describe: (b) => `${T.freqs[b.freq]}${b.autopay ? ' · pago automático: revisa que haya saldo' : ''}. Del calendario de recibos de Money Made Simple.`,
  restored: (n) => `Se restauraron ${n} recibos.`, badFile: 'Ese archivo no es una copia de este calendario.',
  file: 'recibos', cal: 'Recibos',
} : {
  freqs: { monthly: 'Every month', weekly: 'Every week', biweekly: 'Every 2 weeks', quarterly: 'Every 3 months', yearly: 'Every year', once: 'Just once' },
  weekdays: ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'],
  stats: ['Due this month', 'Paid', 'Still to pay', 'On autopay'],
  none: 'Nothing due this month.', noBills: 'No bills yet. Add your first one above.',
  paid: 'Paid', auto: 'autopay', overdue: 'overdue', due: 'due',
  markPaid: (n) => `Mark ${n} paid`,
  upcomingNone: 'Nothing to pay in the next 14 days.',
  overdueHead: (n) => `${n} bill${n === 1 ? '' : 's'} overdue`,
  inDays: (n) => (n === 0 ? 'today' : n === 1 ? 'tomorrow' : `in ${n} days`),
  perMonth: (n) => `${money(n)} a month`, del: (n) => `Delete ${n}`, edit: (n) => `Edit ${n}`,
  confirmDel: (n) => `Delete ${n} and its paid marks?`,
  added: (n) => `Added ${n}.`, saved: (n) => `Saved ${n}.`, fix: 'Add a name, an amount and the next due date.',
  ics: (n) => `Downloaded a calendar file with ${n} bill${n === 1 ? '' : 's'}. Open it to add them to your calendar; they repeat by themselves.`,
  icsNone: 'Add a bill first.', title: (b) => `Pay ${b.name}`,
  describe: (b) => `${T.freqs[b.freq]}${b.autopay ? ' · autopay: check the money is there' : ''}. From the Money Made Simple bill calendar.`,
  restored: (n) => `Restored ${n} bills.`, badFile: "That file isn't a backup from this calendar.",
  file: 'bills', cal: 'Bills',
};

const KEY = 'mms-bill-calendar-v1';
let st = { bills: [], paid: {} };
try { st = B.loadState(localStorage.getItem(KEY) || '{}'); } catch { /* private mode */ }
const save = () => { try { localStorage.setItem(KEY, JSON.stringify(st)); } catch { /* private mode */ } };
let ym = today.slice(0, 7);
let editing = null;

const form = $('#bill-form');
form.freq.innerHTML = B.FREQS.map((f) => `<option value="${f}">${esc(T.freqs[f])}</option>`).join('');
form.start.value = today;
$('#weekdays').innerHTML = T.weekdays.map((d) => `<span>${d}</span>`).join('');

function itemRow(it, showDate = true) {
  const n = esc(it.bill.name);
  const days = Math.round((Date.parse(`${it.date}T00:00:00Z`) - Date.parse(`${today}T00:00:00Z`)) / 86400000);
  return `<li class="due${it.paid ? ' is-paid' : ''}${it.overdue ? ' is-late' : ''}">
    <label class="pick"><input type="checkbox" data-key="${esc(it.key)}"${it.paid ? ' checked' : ''} aria-label="${esc(T.markPaid(it.bill.name))}">
    <span>${showDate ? `<span class="d">${esc(dayName(it.date, { weekday: 'short', month: 'short', day: 'numeric' }))}</span>` : ''}<b>${n}</b>
    <small>${it.paid ? T.paid : it.overdue ? `<span class="late">${T.overdue}</span>` : days >= 0 && days <= 14 ? `${T.due} ${T.inDays(days)}` : ''}${it.bill.autopay ? ` · ${T.auto}` : ''}</small></span></label>
    <span class="amt">${money(it.amount)}</span></li>`;
}

function render() {
  const v = B.monthView(st, ym, today);
  $('#month').textContent = new Date(`${ym}-15T12:00:00`).toLocaleDateString(loc, { month: 'long', year: 'numeric' });
  $('#stats').innerHTML = [v.total, v.paid, v.left, v.autopay].map((n, i) => `<div class="stat"><span>${T.stats[i]}</span><b>${money(n, 0)}</b></div>`).join('');
  $('#grid').innerHTML = v.weeks.map((w) => w.map((c) => {
    if (!c) return '<div class="cell empty" aria-hidden="true"></div>';
    const unpaid = c.items.filter((i) => !i.paid);
    const sum = c.items.reduce((s, i) => s + i.amount, 0);
    const label = `${dayName(c.date, { weekday: 'long', month: 'long', day: 'numeric' })}${c.items.length ? `: ${c.items.map((i) => `${i.bill.name} ${money(i.amount)}${i.paid ? ` (${T.paid})` : ''}`).join(', ')}` : ''}`;
    const cls = ['cell', c.today && 'today', c.items.length && 'has', c.items.length && !unpaid.length && 'all-paid', c.items.some((i) => i.overdue) && 'late'].filter(Boolean).join(' ');
    return `<button type="button" class="${cls}" data-day="${c.date}" aria-label="${esc(label)}"><span class="n">${Number(c.date.slice(8))}</span>${c.items.length ? `<span class="sum">${short(sum)}</span><span class="dots">${c.items.slice(0, 4).map((i) => `<i class="${i.paid ? 'p' : ''}"></i>`).join('')}</span>` : ''}</button>`;
  }).join('')).join('');
  $('#list').innerHTML = v.items.length ? v.items.map((it) => itemRow(it)).join('') : `<li class="empty">${T.none}</li>`;

  const late = B.overdue(st, today);
  const up = B.upcoming(st, today, 14);
  $('#soon').innerHTML = (late.length ? `<p class="late-head">${T.overdueHead(late.length)}</p><ul class="dues">${late.map((it) => itemRow(it)).join('')}</ul>` : '')
    + (up.length ? `<ul class="dues">${up.map((it) => itemRow(it)).join('')}</ul>` : `<p class="tiny">${T.upcomingNone}</p>`);

  $('#bills').innerHTML = st.bills.length ? [...st.bills].sort((a, b) => a.name.localeCompare(b.name)).map((b) => `<li>
    <span><b>${esc(b.name)}</b><small>${money(b.amount)} · ${esc(T.freqs[b.freq])}${b.autopay ? ` · ${T.auto}` : ''}${b.freq !== 'once' ? ` · ${T.perMonth(B.perMonth(b))}` : ''}</small></span>
    <span class="acts"><button type="button" class="link" data-edit="${b.id}" aria-label="${esc(T.edit(b.name))}">✎</button><button type="button" class="x" data-del="${b.id}" aria-label="${esc(T.del(b.name))}">✕</button></span></li>`).join('')
    : `<li class="empty">${T.noBills}</li>`;
  $('#bill-count').textContent = st.bills.length ? `(${st.bills.length})` : '';
}

form.addEventListener('submit', (e) => {
  e.preventDefault();
  const b = B.normalizeBill({ id: editing || undefined, name: form.name.value, amount: form.amount.value, start: form.start.value, freq: form.freq.value, autopay: form.autopay.checked });
  if (!b) { $('#form-msg').textContent = T.fix; return; }
  st = { ...st, bills: editing ? st.bills.map((x) => (x.id === editing ? b : x)) : [...st.bills, b] };
  save();
  $('#form-msg').textContent = editing ? T.saved(b.name) : T.added(b.name);
  editing = null; form.reset(); form.start.value = today; $('#save').textContent = $('#save').dataset.add;
  ym = b.start.slice(0, 7) < today.slice(0, 7) ? today.slice(0, 7) : b.start.slice(0, 7);
  render();
  form.name.focus();
});

document.addEventListener('change', (e) => {
  const k = e.target.dataset?.key;
  if (!k) return;
  st = B.togglePaid(st, k, e.target.checked);
  save();
  const id = e.target.closest('section')?.id;
  render();
  // Keep focus on the same checkbox after the redraw.
  const again = document.querySelector(`${id ? `#${id} ` : ''}[data-key="${CSS.escape(k)}"]`);
  if (again) again.focus();
});

$('#bills').addEventListener('click', (e) => {
  const del = e.target.closest('[data-del]'); const ed = e.target.closest('[data-edit]');
  if (del) {
    const b = st.bills.find((x) => x.id === del.dataset.del);
    if (b && confirm(T.confirmDel(b.name))) { st = B.removeBill(st, b.id); save(); render(); $('#bills').focus(); }
  }
  if (ed) {
    const b = st.bills.find((x) => x.id === ed.dataset.edit);
    if (!b) return;
    editing = b.id;
    form.name.value = b.name; form.amount.value = b.amount; form.start.value = b.start; form.freq.value = b.freq; form.autopay.checked = b.autopay;
    $('#save').textContent = $('#save').dataset.save;
    form.scrollIntoView({ behavior: 'smooth', block: 'start' });
    form.name.focus();
  }
});

$('#grid').addEventListener('click', (e) => {
  const c = e.target.closest('[data-day]');
  if (!c) return;
  const row = $(`#list [data-key$="|${c.dataset.day}"]`);
  if (row) { row.closest('li').scrollIntoView({ behavior: 'smooth', block: 'center' }); row.focus({ preventScroll: true }); }
  else { form.start.value = c.dataset.day; form.name.focus(); }
});
$('#prev').addEventListener('click', () => { ym = B.shiftMonth(ym, -1); render(); });
$('#next').addEventListener('click', () => { ym = B.shiftMonth(ym, 1); render(); });
$('#this').addEventListener('click', () => { ym = today.slice(0, 7); render(); });

function download(name, text, type) {
  const a = document.createElement('a');
  a.href = URL.createObjectURL(new Blob([text], { type }));
  a.download = name; document.body.append(a); a.click(); a.remove();
  setTimeout(() => URL.revokeObjectURL(a.href), 1000);
}
$('#ics').addEventListener('click', () => {
  if (!st.bills.length) { $('#ics-msg').textContent = T.icsNone; return; }
  const daysBefore = Number($('#remind').value) || 0;
  download(`${T.file}.ics`, B.billsIcs(st, { daysBefore, title: T.title, describe: T.describe, calName: T.cal, money: (n) => money(n) }), 'text/calendar');
  $('#ics-msg').textContent = T.ics(st.bills.length);
});
$('#backup').addEventListener('click', () => download(`${T.file}-backup-${today}.json`, JSON.stringify({ app: 'mms-bill-calendar', version: 1, ...st }, null, 2), 'application/json'));
$('#restore').addEventListener('change', async (e) => {
  const f = e.target.files[0];
  if (!f) return;
  try {
    const raw = JSON.parse(await f.text());
    if (raw.app !== 'mms-bill-calendar') throw new Error('not ours');
    st = B.loadState(raw); save(); render();
    $('#ics-msg').textContent = T.restored(st.bills.length);
  } catch { $('#ics-msg').textContent = T.badFile; }
  e.target.value = '';
});

// Install and offline.
let deferred = null;
window.addEventListener('beforeinstallprompt', (e) => { e.preventDefault(); deferred = e; $('#install').hidden = false; });
$('#install').addEventListener('click', async () => { if (!deferred) return; deferred.prompt(); await deferred.userChoice; deferred = null; $('#install').hidden = true; });
if ('serviceWorker' in navigator) navigator.serviceWorker.register('sw.js').catch(() => {});
if (new URLSearchParams(location.search).get('add')) form.name.focus();

render();
initTracking({ config, app: 'budget', page: es ? 'calendario-recibos' : 'bill-calendar' });
