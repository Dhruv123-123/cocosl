// Money date (couples budget) page: couples.html. Logic in lib/couples.js.
import config from './config.js';
import { initTracking } from './lib/track.js';
import * as C from './lib/couples.js';
import { $, esc, money, store, download } from './page.js';

const KEY = 'mms-couples-v1';
let plan = C.loadPlan(store.get(KEY));
const pf = $('#partners');
const ef = $('#expense-form');
const save = () => { if (!store.set(KEY, JSON.stringify(plan))) $('#data-msg').textContent = 'Could not save here (private browsing?). Use "Download backup" before closing.'; };
const pct = (x) => `${Math.round(x * 1000) / 10}%`;
let month = C.monthKey();

$('#site-link').href = config.siteUrl;
$('#e-cat').innerHTML = Object.entries(C.CATEGORIES).map(([k, v]) => `<option value="${k}">${esc(v)}</option>`).join('');
$('#month').value = month;

function fillPartners() {
  plan.partners.forEach((p, i) => { pf[`name${i}`].value = p.name; pf[`income${i}`].value = p.income || ''; });
  pf.customA.value = plan.customA;
}

function render() {
  const [n1, n2] = C.names(plan);
  const s = C.summary(plan);
  $('#method-list').innerHTML = Object.entries(C.METHODS).map(([k, v]) => `<label class="pick"><input type="radio" name="method" value="${k}"${plan.method === k ? ' checked' : ''}> <span>${esc(v)}</span></label>`).join('');
  pf.querySelector('.custom-only').hidden = plan.method !== 'custom';
  $('#custom-label').textContent = `${n1} pays (%)`;
  const keep = ef.paidBy.value;
  $('#e-paid').innerHTML = [['joint', 'Joint account'], ['a', n1], ['b', n2]].map(([k, v]) => `<option value="${k}">${esc(v)}</option>`).join('');
  ef.paidBy.value = keep || 'joint';

  $('#stats').innerHTML = `
    <div class="stat"><span>Shared costs a month</span><b>${money(s.total)}</b><small>${plan.expenses.length} expense${plan.expenses.length === 1 ? '' : 's'}</small></div>
    <div class="stat"><span>${esc(n1)}'s share</span><b>${money(s.owed[0])}</b><small>${pct(s.shareA)}${s.pctOfIncome[0] !== null ? ` · ${pct(s.pctOfIncome[0])} of pay` : ''}</small></div>
    <div class="stat"><span>${esc(n2)}'s share</span><b>${money(s.owed[1])}</b><small>${pct(s.shareB)}${s.pctOfIncome[1] !== null ? ` · ${pct(s.pctOfIncome[1])} of pay` : ''}</small></div>
    <div class="stat"><span>Left for each of you</span><b class="${s.left.some((x) => x < 0) ? 'neg' : ''}">${s.incomes[0] || s.incomes[1] ? `${money(s.left[0])} / ${money(s.left[1])}` : '—'}</b><small>after shared costs</small></div>`;

  $('#expenses').innerHTML = plan.expenses.map((e) => `<li><span><b>${esc(e.name)}</b> <span class="tiny">${esc(C.CATEGORIES[e.category])} · paid by ${esc(e.paidBy === 'a' ? n1 : e.paidBy === 'b' ? n2 : 'joint account')}</span></span><span>${money(e.amount)} <button class="x" type="button" data-del="${e.id}" aria-label="Remove ${esc(e.name)}">×</button></span></li>`).join('') || '<li class="tiny">Add rent, utilities, groceries and anything else you share.</li>';

  const why = s.reason === 'no-income' ? 'Add both take-home pays to split by income; until then it\'s 50/50.' : s.reason === 'income' ? `Each of you pays the same share of your pay: ${pct(s.pctOfIncome[0] ?? 0)}.` : s.reason === 'custom' ? 'Your own split.' : 'An even split.';
  $('#split').innerHTML = plan.expenses.length ? `<h2>Who pays what</h2>
    <p>${esc(why)}</p>
    ${s.paid.joint ? `<h3>Into the joint account each month</h3><ul class="plain-list"><li>${esc(n1)}: <b>${money(s.joint[0])}</b></li><li>${esc(n2)}: <b>${money(s.joint[1])}</b></li></ul><p class="tiny">Covers the ${money(s.paid.joint)} of bills paid from the joint account.</p>` : ''}
    ${s.paid.a || s.paid.b ? `<h3>Settle up</h3><p>${esc(n1)} pays ${money(s.paid.a)} and ${esc(n2)} pays ${money(s.paid.b)} of shared bills from their own accounts. ${s.settle ? `To even it out, <b>${esc([n1, n2][s.settle.from])} sends ${esc([n1, n2][s.settle.to])} ${money(s.settle.amount)}</b> each month.` : 'That already matches your split, so nobody owes anything.'}</p>` : ''}` : '<p class="tiny">Add your shared expenses to see who pays what.</p>';

  const done = new Set(plan.checks[month] || []);
  $('#checklist').innerHTML = C.CHECKLIST.map((c) => `<li><label class="pick"><input type="checkbox" data-check="${c.id}"${done.has(c.id) ? ' checked' : ''}> <span>${esc(c.text)}</span></label></li>`).join('');
  const pr = C.progress(plan, month);
  const st = C.streak(plan, month);
  $('#streak').textContent = `${pr.done} of ${pr.total} done${pr.complete ? ' · money date done!' : ''}${st > 1 ? ` · ${st} months in a row` : ''}`;
  $('#note').value = plan.notes[month] || '';
}

pf.addEventListener('input', (e) => {
  const t = e.target;
  const m = /^(name|income)([01])$/.exec(t.name || '');
  if (m) C.setPartner(plan, Number(m[2]), { [m[1]]: t.value });
  if (t.name === 'method' || t.name === 'customA') C.setMethod(plan, pf.querySelector('[name=method]:checked')?.value || plan.method, pf.customA.value);
  save();
  if (m && m[1] === 'name') renderSoon(); else render();
});
// Re-render names after typing pauses, so the field keeps focus while you type.
let timer;
const renderSoon = () => { clearTimeout(timer); timer = setTimeout(() => { const f = document.activeElement; const pos = f?.selectionStart; render(); if (f && f.isConnected) { f.focus(); if (pos != null) f.setSelectionRange(pos, pos); } }, 300); };

ef.addEventListener('submit', (e) => {
  e.preventDefault();
  try {
    C.addExpense(plan, Object.fromEntries(new FormData(ef)));
    const paidBy = ef.paidBy.value;
    ef.reset(); ef.paidBy.value = paidBy;
    $('#expense-msg').textContent = ''; save(); render(); ef.name.focus();
  } catch (err) { $('#expense-msg').textContent = err.message; }
});
document.addEventListener('click', (e) => { const id = e.target.dataset?.del; if (id) { C.removeExpense(plan, id); save(); render(); } });
$('#checklist').addEventListener('change', (e) => { const id = e.target.dataset?.check; if (id) { C.toggleCheck(plan, month, id); save(); render(); } });
$('#month').addEventListener('change', (e) => { if (/^\d{4}-\d{2}$/.test(e.target.value)) { month = e.target.value; render(); } });
$('#note').addEventListener('input', (e) => { C.setNote(plan, month, e.target.value); save(); });

$('#backup').addEventListener('click', () => download(`money-date-${month}.json`, JSON.stringify(plan, null, 2), 'application/json'));
$('#restore').addEventListener('change', async (e) => {
  const f = e.target.files[0]; if (!f) return;
  const next = C.loadPlan(await f.text());
  if (!confirm(`Replace this plan with the backup (${next.expenses.length} expenses)?`)) return;
  plan = next; save(); fillPartners(); render(); e.target.value = '';
});
$('#reset').addEventListener('click', () => {
  if (!confirm('Clear everything and start over? Download a backup first if you want to keep it.')) return;
  plan = C.emptyPlan(); save(); fillPartners(); render();
});

fillPartners();
render();
initTracking({ config, app: 'budget', page: 'couples' });
