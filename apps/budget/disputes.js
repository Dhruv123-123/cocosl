// Credit dispute tracker page (disputes.html). Logic in lib/disputes.js. Free: no plan limits.
import config from './config.js';
import { initTracking } from './lib/track.js';
import * as D from './lib/disputes.js';
import { buildIcs } from './lib/ics.js';
import { today as todayIs, prettyDay } from './lib/dates.js';
import { $, esc, store, download } from './page.js';

const KEY = 'mms-disputes-v1';
let data = D.loadDisputes(store.get(KEY));
const today = todayIs();
const form = $('#dispute-form');
const save = () => { if (!store.set(KEY, JSON.stringify(data))) $('#data-msg').textContent = 'Could not save here (private browsing?). Use "Download my data" before closing.'; };
const opts = (obj) => Object.entries(obj).map(([k, v]) => `<option value="${k}">${esc(typeof v === 'string' ? v : v.name)}</option>`).join('');
const plural = (n, w) => `${n} ${w}${n === 1 ? '' : 's'}`;

$('#f-target').innerHTML = opts(D.TARGETS);
$('#f-reason').innerHTML = opts(D.REASONS);
$('#f-method').innerHTML = opts(D.METHODS);
form.sent.value = today;
form.sent.max = today;
$('#where').innerHTML = Object.values(D.TARGETS).filter((t) => t.url).map((t) => `<li><a href="${esc(t.url)}" target="_blank" rel="noopener">${esc(t.name)} dispute page</a></li>`).join('')
  + '<li>The lender or collector itself: use the dispute address on its statements or website.</li>';
$('#site-link').href = config.siteUrl;

const LABEL = { overdue: 'No reply, overdue', late: 'Deadline passed', 'due-soon': 'Due soon', waiting: 'Waiting', answered: 'Answered' };

function clockLine(r) {
  const c = r.clock;
  if (c.state === 'answered') return `<b>${esc(D.OUTCOMES[r.outcome])}</b> on ${prettyDay(r.outcomeDate)}`;
  if (c.left >= 0) return `<b>${plural(c.left, 'day')} left</b> · investigation due ${prettyDay(c.due)}${c.estimatedStart ? ' (estimated)' : ''}`;
  return `<b>Due ${prettyDay(c.due)}</b> · results expected by ${prettyDay(c.noticeBy)}`;
}

function render() {
  const s = D.summary(data, today);
  $('#stats').innerHTML = `
    <div class="stat"><span>Open disputes</span><b>${s.open}</b></div>
    <div class="stat"><span>Past their deadline</span><b class="${s.overdue ? 'neg' : ''}">${s.overdue}</b></div>
    <div class="stat"><span>Removed or corrected</span><b class="${s.removedOrFixed ? 'pos' : ''}">${s.removedOrFixed}</b></div>
    <div class="stat"><span>Next deadline</span><b>${s.nextDue ? prettyDay(s.nextDue) : '—'}</b></div>`;
  const rows = D.board(data, today);
  $('#disputes').innerHTML = rows.length ? rows.map((r) => `
    <div class="bill dispute" data-id="${r.id}">
      <div class="bill-head"><div><b>${esc(r.item)}</b> <span class="state ${r.clock.state}">${LABEL[r.clock.state]}</span>
        <div class="tiny">${esc(D.TARGETS[r.target].name)} · ${esc(D.REASONS[r.reason])} · sent ${prettyDay(r.sent)} by ${esc(D.METHODS[r.method].toLowerCase())}${r.confirmation ? ` · #${esc(r.confirmation)}` : ''}${r.furnisher ? ` · ${esc(r.furnisher)}` : ''}</div></div>
        <button class="x" data-del="${r.id}" aria-label="Delete ${esc(r.item)}">×</button></div>
      <p>${clockLine(r)}</p>
      ${r.clock.state === 'answered' ? '' : `<div class="bar"><span style="width:${r.clock.pct}%" class="${r.clock.left < 0 ? 'over' : ''}"></span></div>`}
      <ul class="steps">${D.nextSteps(r, today).map((t) => `<li>${esc(t)}</li>`).join('')}</ul>
      ${r.notes ? `<p class="tiny">${esc(r.notes)}</p>` : ''}
      <form class="row outcome" data-outcome="${r.id}">
        <select name="outcome" aria-label="Their reply"><option value="">${r.outcome ? 'Clear reply' : 'They replied…'}</option>${opts(D.OUTCOMES).replace(`value="${r.outcome}"`, `value="${r.outcome}" selected`)}</select>
        <input name="date" type="date" value="${r.outcomeDate || today}" max="${today}" aria-label="Date of their reply">
        <button class="btn small ghost">Save reply</button>
      </form>
    </div>`).join('') : '<p class="tiny">No disputes yet. Add one above when you send it.</p>';
}

form.addEventListener('submit', (e) => {
  e.preventDefault();
  try {
    D.addDispute(data, Object.fromEntries(new FormData(form)));
    save(); render();
    const keep = form.sent.value;
    form.reset(); form.sent.value = keep;
    $('#form-msg').textContent = 'Added. Disputing the same error with another bureau? Change "Sent to" and add it again.';
  } catch (err) { $('#form-msg').textContent = err.message; }
});

$('#disputes').addEventListener('submit', (e) => {
  const f = e.target.closest('[data-outcome]');
  if (!f) return;
  e.preventDefault();
  try { D.setOutcome(data, f.dataset.outcome, f.outcome.value, f.date.value); save(); render(); }
  catch (err) { $('#data-msg').textContent = err.message; }
});
$('#disputes').addEventListener('click', (e) => {
  const id = e.target.dataset?.del;
  if (id && confirm('Delete this dispute from your tracker?')) { D.removeDispute(data, id); save(); render(); }
});
$('#ics').addEventListener('click', () => {
  const events = D.reminderEvents(data, today);
  if (!events.length) { $('#data-msg').textContent = 'No upcoming deadlines to add.'; return; }
  download('credit-dispute-deadlines.ics', buildIcs(events, { name: 'Credit dispute deadlines' }), 'text/calendar');
  $('#data-msg').textContent = `Downloaded ${plural(events.length, 'reminder')}. Open the file to add them to your calendar.`;
});
$('#backup').addEventListener('click', () => download(`credit-disputes-${today}.json`, JSON.stringify(data, null, 2), 'application/json'));
$('#restore').addEventListener('change', async (e) => {
  const f = e.target.files[0]; if (!f) return;
  const next = D.loadDisputes(await f.text());
  if (!confirm(`Replace what's on this device with the backup (${plural(next.disputes.length, 'dispute')})?`)) return;
  data = next; save(); render();
  e.target.value = '';
});

render();
initTracking({ config, app: 'budget', page: 'credit-disputes' });
