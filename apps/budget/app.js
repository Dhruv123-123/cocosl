import config from './config.js';
import { initTracking, trackEvent, EVENTS } from './lib/track.js';
import * as B from './lib/budget.js';
import { planFor, can } from './lib/plans.js';
import { verifyLicense, isActive, needsRecheck } from './lib/license.js';
import { checkoutOptions, reasonText, keyFromUrl, limitPrompt, pricingHref, starterPlan, needsOnboarding } from './lib/checkout.js';

const $ = (s) => document.querySelector(s);
const esc = (s) => String(s).replace(/[&<>"']/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' })[c]);
const money = (n) => (Number(n) || 0).toLocaleString('en-US', { style: 'currency', currency: 'USD' });
const KEY = 'mms-budget-v1';
const LKEY = 'mms-budget-license';
const OKEY = 'mms-budget-onboarded';

const store = {
  get(k) { try { return localStorage.getItem(k); } catch { return null; } },
  set(k, v) { try { localStorage.setItem(k, v); return true; } catch { return false; } },
};

let state = B.loadState(store.get(KEY));
let license = (() => { try { return JSON.parse(store.get(LKEY)); } catch { return null; } })();
let month = B.thisMonth();
B.ensureMonth(state, month);

const pro = () => isActive(license);
const plan = () => planFor(pro() ? license : null);
const save = () => { if (!store.set(KEY, JSON.stringify(state))) $('#data-msg').textContent = 'Could not save (private browsing?). Download a backup before closing.'; };

function monthLabel(m) {
  const [y, mo] = m.split('-').map(Number);
  return new Date(y, mo - 1, 1).toLocaleDateString('en-US', { month: 'long', year: 'numeric' });
}
function shiftMonth(m, by) {
  const [y, mo] = m.split('-').map(Number);
  const d = new Date(y, mo - 1 + by, 1);
  return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}`;
}

function render() {
  const s = B.summarize(state, month);
  $('#month-label').textContent = monthLabel(month);
  $('#plan-badge').textContent = pro() ? 'Pro' : 'Free · Upgrade';
  $('#plan-badge').classList.toggle('pro', pro());
  if (document.activeElement !== $('#income')) $('#income').value = s.income || '';

  const unassignedNote = s.income === 0 ? 'Add your take-home pay'
    : s.unassigned > 0 ? 'Give these dollars a job' : s.unassigned < 0 ? 'Planned more than you earn' : 'Every dollar has a job';
  $('#summary').innerHTML = `
    <div class="stat"><span>Left to spend</span><b class="${s.leftToSpend < 0 ? 'neg' : ''}">${money(s.leftToSpend)}</b></div>
    <div class="stat"><span>Spent</span><b>${money(s.spent)}</b></div>
    <div class="stat"><span>Planned</span><b>${money(s.planned)}</b></div>
    <div class="stat"><span>Not assigned</span><b class="${s.unassigned < 0 ? 'neg' : ''}">${money(s.unassigned)}</b><small>${unassignedNote}</small></div>`;

  $('#rows').innerHTML = s.rows.map((r) => {
    const pct = r.planned ? Math.min(100, (r.spent / r.planned) * 100) : r.spent ? 100 : 0;
    return `<tr data-id="${r.id}">
      <td><span class="grp ${r.group}" title="${r.group}"></span>${esc(r.name)} <button class="x" data-del-cat="${r.id}" aria-label="Delete ${esc(r.name)}">×</button></td>
      <td><input class="plan-in" type="number" min="0" step="any" value="${r.planned || ''}" data-plan="${r.id}" aria-label="Planned for ${esc(r.name)}"></td>
      <td>${money(r.spent)}</td>
      <td class="${r.over ? 'neg' : ''}">${money(r.left)}<div class="bar"><span style="width:${pct}%" class="${r.over ? 'over' : ''}"></span></div></td></tr>`;
  }).join('') + (s.uncategorized ? `<tr><td><i>Uncategorised</i></td><td></td><td>${money(s.uncategorized)}</td><td></td></tr>` : '');

  $('#split').innerHTML = s.split ? `<div class="split">${['needs', 'wants', 'savings'].map((k) => {
    const v = s.split[k];
    return `<div><span>${k === 'savings' ? 'Savings & debt' : k[0].toUpperCase() + k.slice(1)}</span><b>${v.pct}%</b><small>guide ${v.target}%</small></div>`;
  }).join('')}</div><p class="tiny">The 50/30/20 split is a starting point, not a rule. High-rent cities often need more than 50% for needs.</p>` : '';

  $('#tx-cat').innerHTML = '<option value="">Uncategorised</option>' + state.categories.map((c) => `<option value="${c.id}">${esc(c.name)}</option>`).join('');
  const names = Object.fromEntries(state.categories.map((c) => [c.id, c.name]));
  $('#tx-list').innerHTML = s.transactions.length
    ? s.transactions.slice(0, 200).map((t) => `<li><span class="d">${t.date.slice(5)}</span><span class="n">${esc(t.note || names[t.categoryId] || 'Spending')}<small>${esc(names[t.categoryId] || 'Uncategorised')}</small></span><b class="${t.amount < 0 ? 'pos' : ''}">${money(-t.amount)}</b><button class="x" data-del-tx="${t.id}" aria-label="Delete">×</button></li>`).join('')
    : '<li class="empty">Nothing logged this month yet.</li>';

  $('#goals').innerHTML = state.goals.map((g, i) => {
    const p = B.goalPlan(g);
    const pct = Math.min(100, (g.saved / g.target) * 100);
    return `<li><div><b>${esc(g.name)}</b> ${money(g.saved)} of ${money(g.target)}<div class="bar"><span style="width:${pct}%"></span></div>
      <small>${p.done ? 'Done!' : `Save ${money(p.monthly)} a month for ${p.months} month${p.months === 1 ? '' : 's'}`}</small></div>
      <button class="x" data-del-goal="${i}" aria-label="Delete goal">×</button></li>`;
  }).join('');
}

function upsell(reason, where = 'badge') {
  $('#license-msg').textContent = '';
  $('#upgrade-reason').textContent = reason || limitPrompt('');
  $('#pro-features').innerHTML = config.proFeatures.map((f) => `<li>${esc(f)}</li>`).join('');
  const inStore = (config.distribution || 'web') !== 'web';
  const links = checkoutOptions(config);
  $('#buy').innerHTML = links.map((p) => `<a class="btn${p.best ? '' : ' ghost'}" href="${esc(p.url)}" data-id="budget-pro-${esc(p.id)}" data-upgrade="${esc(where)}" target="_blank" rel="noopener">${esc(p.label)}</a>`).join('');
  $('#no-checkout').textContent = inStore ? 'Already have Pro? Enter your license key below.' : "Checkout isn't connected yet (set pricing links in config.js).";
  $('#no-checkout').hidden = links.length > 0;
  $('#compare').href = pricingHref(where);
  $('#compare').dataset.upgrade = where;
  if (!$('#upgrade').open) $('#upgrade').showModal();
  trackEvent(EVENTS.upgradeShown, { where });
}

async function activate(key) {
  $('#license-msg').textContent = 'Checking…';
  license = await verifyLicense(key, { endpoint: config.verifyEndpoint, previous: license });
  store.set(LKEY, JSON.stringify(license));
  $('#license-msg').textContent = license.valid ? 'Pro is on. Thank you!' : reasonText(license.reason);
  render();
  return license.valid;
}

// ---------- first run ----------
function onboard() {
  const d = $('#welcome');
  const step = (n) => { for (const s of d.querySelectorAll('[data-step]')) s.hidden = s.dataset.step !== String(n); };
  step(1);
  d.showModal();
  d.addEventListener('close', () => store.set(OKEY, new Date().toISOString()), { once: true });
  $('#welcome-pay').addEventListener('submit', (e) => {
    e.preventDefault();
    const pay = Number($('#welcome-income').value);
    if (pay > 0) {
      B.setIncome(state, month, pay);
      if ($('#welcome-split').checked) for (const [id, amt] of Object.entries(starterPlan(state.categories, pay))) B.setPlan(state, month, id, amt);
      save(); render();
    }
    step(2);
  });
  $('#welcome-next').addEventListener('click', () => step(3));
}

// ---------- events ----------
$('#prev').addEventListener('click', () => {
  const target = shiftMonth(month, -1);
  if (!plan().history && target !== B.thisMonth()) return upsell(limitPrompt('history'), 'history');
  month = target; B.ensureMonth(state, month); save(); render();
});
$('#next').addEventListener('click', () => {
  const target = shiftMonth(month, 1);
  if (!plan().history && target !== B.thisMonth()) return upsell(limitPrompt('history'), 'history');
  month = target; B.ensureMonth(state, month); save(); render();
});
$('#plan-badge').addEventListener('click', () => (pro() ? null : upsell('', 'badge')));

$('#income').addEventListener('input', (e) => { B.setIncome(state, month, e.target.value); save(); render(); });
$('#rows').addEventListener('change', (e) => {
  if (e.target.dataset.plan) { B.setPlan(state, month, e.target.dataset.plan, e.target.value); save(); render(); }
});
document.addEventListener('click', (e) => {
  const t = e.target;
  if (t.dataset.delCat && confirm('Delete this category? Its spending becomes uncategorised.')) { B.removeCategory(state, t.dataset.delCat); save(); render(); }
  if (t.dataset.delTx) { B.removeTransaction(state, t.dataset.delTx); save(); render(); }
  if (t.dataset.delGoal) { state.goals.splice(Number(t.dataset.delGoal), 1); save(); render(); }
});
$('#cat-form').addEventListener('submit', (e) => {
  e.preventDefault();
  try { B.addCategory(state, $('#cat-name').value, $('#cat-group').value, { limit: plan().maxCategories }); $('#cat-name').value = ''; save(); render(); }
  catch (err) { if (err instanceof B.LimitError) upsell(limitPrompt('categories', plan()), 'categories'); else alert(err.message); }
});
$('#tx-date').value = new Date().toISOString().slice(0, 10);
$('#tx-form').addEventListener('submit', (e) => {
  e.preventDefault();
  try {
    const date = $('#tx-date').value;
    if (!plan().history && B.monthOf(date) !== B.thisMonth()) return upsell(limitPrompt('history'), 'history');
    B.addTransaction(state, { date, amount: $('#tx-amount').value, categoryId: $('#tx-cat').value || null, note: $('#tx-note').value });
    $('#tx-amount').value = ''; $('#tx-note').value = '';
    month = B.monthOf(date);
    save(); render(); $('#tx-amount').focus();
  } catch (err) { alert(err.message); }
});
$('#goal-deadline').value = shiftMonth(B.thisMonth(), 6);
$('#goal-form').addEventListener('submit', (e) => {
  e.preventDefault();
  if (state.goals.length >= plan().goals) return upsell(limitPrompt('goals', plan()), 'goals');
  state.goals.push({ name: $('#goal-name').value.trim(), target: Number($('#goal-target').value), saved: Number($('#goal-saved').value || 0), deadline: $('#goal-deadline').value });
  e.target.reset(); $('#goal-deadline').value = shiftMonth(B.thisMonth(), 6);
  save(); render();
});

const download = (name, text, type) => {
  const a = document.createElement('a');
  a.href = URL.createObjectURL(new Blob([text], { type }));
  a.download = name; a.click();
  setTimeout(() => URL.revokeObjectURL(a.href), 1000);
};
$('#export-csv').addEventListener('click', () => download('budget-transactions.csv', B.exportCsv(state), 'text/csv'));
$('#backup').addEventListener('click', () => download(`budget-backup-${new Date().toISOString().slice(0, 10)}.json`, JSON.stringify(state, null, 2), 'application/json'));
$('#restore').addEventListener('change', async (e) => {
  const f = e.target.files[0]; if (!f) return;
  const next = B.loadState(await f.text());
  if (!confirm(`Replace what's on this device with the backup (${next.transactions.length} transactions)?`)) return;
  state = next; month = B.thisMonth(); B.ensureMonth(state, month); save(); render();
  $('#data-msg').textContent = 'Backup restored.';
});
$('#import-csv').addEventListener('click', (e) => { if (!can(pro() ? license : null, 'csvImport')) { e.preventDefault(); upsell(limitPrompt('csv'), 'csv'); } });
$('#import-csv').addEventListener('change', async (e) => {
  const f = e.target.files[0]; if (!f) return;
  const { transactions, skipped, error } = B.importBankCsv(await f.text());
  if (error) { $('#data-msg').textContent = error; return; }
  const seen = new Set(state.transactions.map((t) => `${t.date}|${t.amount}|${t.note}`));
  let added = 0;
  for (const t of transactions) {
    if (seen.has(`${t.date}|${t.amount}|${t.note}`)) continue; // importing the same file twice is harmless
    B.addTransaction(state, { ...t, categoryId: B.guessCategory(state, t.note) });
    added++;
  }
  save(); render();
  $('#data-msg').textContent = `Imported ${added} transactions${skipped ? `, skipped ${skipped} rows we couldn't read` : ''}. Income rows show as negative spending; delete them if you track pay separately.`;
  e.target.value = '';
});
$('#license-form').addEventListener('submit', (e) => { e.preventDefault(); activate($('#license-key').value); });
$('#site-link').href = config.siteUrl;

// Returning from checkout: ?session_id=cs_... (Stripe) or ?license_key=... activates Pro.
const returnedKey = keyFromUrl(location.search);
if (returnedKey) {
  history.replaceState(null, '', location.pathname);
  activate(returnedKey).then((ok) => { $('#data-msg').textContent = ok ? 'Pro is on. Thank you for supporting the app!' : `${reasonText(license.reason)} You can paste your key from the receipt under Upgrade.`; });
} else if (needsRecheck(license)) {
  verifyLicense(license.key, { endpoint: config.verifyEndpoint, previous: license }).then((l) => { license = l; store.set(LKEY, JSON.stringify(l)); render(); });
}

initTracking({ config, app: 'budget', page: 'budget' });
render();
if ('serviceWorker' in navigator && location.protocol === 'https:') navigator.serviceWorker.register('sw.js').catch(() => {});
if (location.hash === '#upgrade' && !pro()) {
  history.replaceState(null, '', location.pathname + location.search);
  upsell('', 'link');
} else if (!returnedKey && !pro() && needsOnboarding(state, store.get(OKEY))) {
  onboard();
}
