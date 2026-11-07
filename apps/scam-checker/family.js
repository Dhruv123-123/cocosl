// Family security setup page (family/index.html). Logic in lib/family.js.
import config from './config.js';
import { initTracking } from './lib/track.js';
import * as F from './lib/family.js';

const $ = (s) => document.querySelector(s);
const esc = (s) => String(s ?? '').replace(/[&<>"']/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' })[c]);
const KEY = 'scam-family-v1';
const load = () => { try { return F.loadFamily(localStorage.getItem(KEY)); } catch { return F.emptyFamily(); } };
const save = () => { try { localStorage.setItem(KEY, JSON.stringify(data)); } catch { $('#member-msg').textContent = 'Progress can\'t be saved in this browser (private mode?). Print the checklist instead.'; } };
let data = load();
if (!data.members.length) { F.addMember(data, { name: 'Me', kind: 'adult' }); }

function render() {
  $('#members').innerHTML = data.members.map((m) => `<li><b>${esc(m.name)}</b> <span class="tiny">${m.kind === 'child' ? 'child' : 'adult'}</span> <button class="link" data-remove="${m.id}" aria-label="Remove ${esc(m.name)}">Remove</button></li>`).join('');
  const p = F.progress(data);
  $('#progress').innerHTML = `
    <h2>${p.done === p.total ? 'All done. Your family is much harder to scam.' : `${p.done} of ${p.total} steps done`}</h2>
    <div class="meter" style="--c:var(--low)"><span style="width:${p.pct}%"></span></div>
    <p class="tiny">${p.total - p.done ? `About ${p.minutesLeft} minutes left.` : ''} ${p.next ? `Next: <a href="#t-${esc(p.next.key)}">${esc(p.next.title)}${p.next.memberId ? ` (${esc(p.next.member)})` : ''}</a>` : ''}</p>
    <ul class="who">${p.byMember.map((m) => `<li>${esc(m.name)}: ${m.done}/${m.total}</li>`).join('')}</ul>`;
  const groups = [['household', 'For the whole family'], ['adult', 'For each adult'], ['child', 'For each child']];
  const all = F.tasks(data);
  $('#steps').innerHTML = groups.map(([scope, label]) => {
    const list = all.filter((t) => t.scope === scope);
    if (!list.length) return '';
    return `<section class="card"><h2>${label}</h2>${list.map((t) => `
      <div class="task${t.done ? ' done' : ''}" id="t-${esc(t.key)}">
        <label class="tick"><input type="checkbox" data-key="${esc(t.key)}" data-member="${t.memberId || ''}" data-step="${t.stepId}"${t.done ? ' checked' : ''}>
          <span><b>${esc(t.title)}</b>${t.memberId ? ` <span class="tag">${esc(t.member)}</span>` : ''} <span class="tiny">${t.minutes} min</span>${t.done ? ` <span class="ok">Done ${esc(t.done)}</span>` : ''}</span></label>
        <details${t.done ? '' : (t.key === all.find((x) => !x.done)?.key ? ' open' : '')}><summary>How</summary>
          <p>${esc(t.why)}</p>
          <ol>${t.how.map((h) => `<li>${esc(h)}</li>`).join('')}</ol>
          ${t.bureau ? `<p><a class="btn small" href="${esc(t.bureau.url)}" target="_blank" rel="noopener">Open ${esc(t.bureau.name)}'s freeze page</a> <span class="tiny">or call ${esc(t.bureau.phone)}</span></p>` : ''}
          ${t.stepId === 'child-freeze' ? `<p class="tiny">${Object.values(F.BUREAUS).map((b) => `<a href="${esc(b.url)}" target="_blank" rel="noopener">${esc(b.name)}</a> (${esc(b.phone)})`).join(' · ')}</p>` : ''}
        </details>
      </div>`).join('')}</section>`;
  }).join('');
}

$('#optional').innerHTML = F.OPTIONAL.map(([t, why, url]) => `<li><a href="${url}" target="_blank" rel="noopener">${esc(t)}</a>: ${esc(why)}</li>`).join('');

$('#member-form').addEventListener('submit', (e) => {
  e.preventDefault();
  try { F.addMember(data, { name: $('#m-name').value, kind: $('#m-kind').value }); $('#m-name').value = ''; $('#member-msg').textContent = ''; save(); render(); }
  catch (err) { $('#member-msg').textContent = err.message; }
});
$('#members').addEventListener('click', (e) => {
  const b = e.target.closest('[data-remove]');
  if (b && confirm('Remove this person and their ticks?')) { F.removeMember(data, b.dataset.remove); save(); render(); }
});
$('#steps').addEventListener('change', (e) => {
  const c = e.target.closest('input[data-key]');
  if (!c) return;
  F.toggle(data, c.dataset.member || null, c.dataset.step);
  save();
  render();
  document.getElementById(`t-${c.dataset.key}`)?.querySelector('input')?.focus();
});
$('#print').addEventListener('click', () => { document.querySelectorAll('#steps details').forEach((d) => { d.open = true; }); window.print(); });
$('#reset').addEventListener('click', () => { if (confirm('Clear everyone and every tick?')) { data = F.emptyFamily(); F.addMember(data, { name: 'Me' }); save(); render(); } });

render();
initTracking({ config, app: 'scam-checker', page: 'family-setup' });
