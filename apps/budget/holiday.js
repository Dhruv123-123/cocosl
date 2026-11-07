// Holiday spending planner page (holiday.html). Logic in lib/holiday.js.
import config from './config.js';
import { initTracking } from './lib/track.js';
import * as H from './lib/holiday.js';
import { today as todayIs, prettyDay } from './lib/dates.js';
import { $, esc, money, store, download } from './page.js';

const KEY = 'mms-holiday-v1';
let plan = H.loadPlan(store.get(KEY));
const today = todayIs();
const save = () => { if (!store.set(KEY, JSON.stringify(plan))) $('#data-msg').textContent = 'Could not save here (private browsing?). Use "Download backup" before closing.'; };
const gf = $('#gift-form');
const opts = (obj) => Object.entries(obj).map(([k, v]) => `<option value="${k}">${esc(v)}</option>`).join('');

$('#g-pay').innerHTML = opts(H.PAY);
$('#g-bnpl').innerHTML = opts(H.BNPL_TYPES);
$('#e-kind').innerHTML = opts(H.EXTRA_KINDS);
$('#cap').value = plan.cap || '';
$('#site-link').href = config.siteUrl;
const toggles = () => {
  const bnpl = gf.pay.value === 'bnpl';
  for (const el of gf.querySelectorAll('.bnpl-only')) el.hidden = !bnpl;
  for (const el of gf.querySelectorAll('.bnpl-monthly')) el.hidden = !bnpl || gf.bnplType.value !== 'monthly';
};
gf.pay.addEventListener('change', toggles);
gf.bnplType.addEventListener('change', toggles);
toggles();

function render() {
  const s = H.summary(plan, today);
  $('#cap-bar').innerHTML = s.cap ? `<div class="bar big-bar"><span style="width:${s.pct}%" class="${s.overCap ? 'over' : ''}"></span></div><p class="tiny">${s.overCap ? `<b class="neg">${money(s.overCap)} over your cap</b>` : `${money(s.capLeft)} left under your cap`} · planned ${money(s.expected)} of ${money(s.cap)}</p>` : '';
  $('#stats').innerHTML = `
    <div class="stat"><span>Planned in total</span><b class="${s.overCap ? 'neg' : ''}">${money(s.expected)}</b><small>gifts, unspent budgets, extras${s.bnpl.interest ? ', interest' : ''}</small></div>
    <div class="stat"><span>Bought so far</span><b>${money(s.spent)}</b></div>
    <div class="stat"><span>Gifts picked</span><b>${money(s.giftsPlanned)}</b><small>${plan.gifts.length} gift${plan.gifts.length === 1 ? '' : 's'}</small></div>
    <div class="stat"><span>Buy now, pay later</span><b class="${s.bnpl.count ? 'neg' : ''}">${money(s.bnpl.total)}</b><small>${s.bnpl.lastDate ? `last payment ${prettyDay(s.bnpl.lastDate)}` : 'none'}</small></div>`;
  $('#warnings').innerHTML = H.warnings(plan, today).map((w) => `<li class="warn ${w.level}">${esc(w.text)}</li>`).join('');

  $('#g-person').innerHTML = plan.people.map((p) => `<option value="${p.id}">${esc(p.name)}</option>`).join('') || '<option value="">Add a person first</option>';
  $('#people').innerHTML = s.people.length ? s.people.map((p) => {
    const gifts = plan.gifts.filter((g) => g.personId === p.id);
    return `<div class="bill person">
      <div class="bill-head"><div><b>${esc(p.name)}</b> <span class="tiny">${p.budget ? `${money(p.planned)} of ${money(p.budget)}` : money(p.planned)}</span>${p.over ? ` <span class="state overdue">${money(p.over)} over</span>` : ''}</div>
        <button class="x" data-del-person="${p.id}" aria-label="Remove ${esc(p.name)}">×</button></div>
      ${p.budget ? `<div class="bar"><span style="width:${Math.min(100, Math.round((p.planned / p.budget) * 100))}%" class="${p.over ? 'over' : ''}"></span></div>` : ''}
      <ul class="gifts">${gifts.map((g) => `<li><label class="pick"><input type="checkbox" data-bought="${g.id}"${g.bought ? ' checked' : ''}> <span class="${g.bought ? 'done' : ''}">${esc(g.item)}</span></label><span>${money(g.price)}${g.pay === 'bnpl' ? ' <span class="tag-bnpl">BNPL</span>' : g.pay === 'carry' ? ' <span class="tag-bnpl">card balance</span>' : ''}</span><button class="x" data-del-gift="${g.id}" aria-label="Remove ${esc(g.item)}">×</button></li>`).join('') || '<li class="tiny">No gifts yet.</li>'}</ul>
    </div>`;
  }).join('') : '<p class="tiny">Add the people you buy for, each with a budget.</p>';

  $('#extras').innerHTML = plan.extras.map((e) => `<li>${esc(e.name)}: <b>${money(e.amount)}</b> <button class="x" data-del-extra="${e.id}" aria-label="Remove ${esc(e.name)}">×</button></li>`).join('');

  if (s.bnpl.count) {
    $('#bnpl').innerHTML = `<h2>The true cost of buy now, pay later</h2>
      <table class="plan subs"><thead><tr><th>Gift</th><th>Plan</th><th>Really costs</th><th class="when">Last payment</th></tr></thead><tbody>
      ${s.bnpl.plans.map((p) => `<tr><td>${esc(p.gift.item)}</td><td class="tiny">${p.type === 'pay4' ? `4 × ${money(p.each)}` : `${p.payments.length} × ${money(p.each)} at ${p.gift.bnpl.apr}%`}</td><td class="num"><b>${money(p.total)}</b>${p.interest ? `<small class="neg" style="display:block">+${money(p.interest)} interest</small>` : ''}</td><td class="tiny when">${prettyDay(p.last)}</td></tr>`).join('')}
      </tbody></table>
      <h3>What lands in each month</h3>
      <ul class="plain-list">${Object.entries(s.bnpl.byMonth).sort().map(([m, a]) => `<li>${new Date(`${m}-15T12:00:00`).toLocaleDateString('en-US', { month: 'long', year: 'numeric' })}: <b>${money(a)}</b></li>`).join('')}</ul>
      <p class="tiny">Assumes every payment is on time and the first pay-in-4 payment is today. Late fees aren't included because they vary by provider.</p>`;
    $('#bnpl').hidden = false;
  } else $('#bnpl').hidden = true;
}

$('#cap').addEventListener('input', () => { H.setCap(plan, $('#cap').value); save(); render(); });
$('#person-form').addEventListener('submit', (e) => {
  e.preventDefault();
  try { H.addPerson(plan, Object.fromEntries(new FormData(e.target))); e.target.reset(); $('#person-msg').textContent = ''; save(); render(); }
  catch (err) { $('#person-msg').textContent = err.message; }
});
gf.addEventListener('submit', (e) => {
  e.preventDefault();
  const v = Object.fromEntries(new FormData(gf));
  try {
    H.addGift(plan, v);
    const keep = gf.personId.value;
    gf.reset(); gf.personId.value = keep; toggles();
    $('#gift-msg').textContent = ''; save(); render();
  } catch (err) { $('#gift-msg').textContent = err.message; }
});
$('#extra-form').addEventListener('submit', (e) => {
  e.preventDefault();
  try { H.addExtra(plan, Object.fromEntries(new FormData(e.target))); e.target.reset(); save(); render(); }
  catch (err) { $('#data-msg').textContent = err.message; }
});
document.addEventListener('change', (e) => { const id = e.target.dataset?.bought; if (id) { H.toggleBought(plan, id); save(); render(); } });
document.addEventListener('click', (e) => {
  const d = e.target.dataset || {};
  if (d.delPerson && confirm('Remove this person and their gifts?')) { H.removePerson(plan, d.delPerson); save(); render(); }
  if (d.delGift) { H.removeGift(plan, d.delGift); save(); render(); }
  if (d.delExtra) { H.removeExtra(plan, d.delExtra); save(); render(); }
});
$('#backup').addEventListener('click', () => download(`holiday-plan-${today}.json`, JSON.stringify(plan, null, 2), 'application/json'));
$('#restore').addEventListener('change', async (e) => {
  const f = e.target.files[0]; if (!f) return;
  const next = H.loadPlan(await f.text());
  if (!confirm(`Replace this plan with the backup (${next.people.length} people, ${next.gifts.length} gifts)?`)) return;
  plan = next; save(); $('#cap').value = plan.cap || ''; render(); e.target.value = '';
});
$('#reset').addEventListener('click', () => {
  if (!confirm('Start a fresh plan? Your people and their budgets stay; gifts and extras are cleared. Download a backup first if you want to keep this year.')) return;
  plan = { ...plan, gifts: [], extras: [] }; save(); render();
});

render();
initTracking({ config, app: 'budget', page: 'holiday-planner' });
