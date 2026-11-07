// 52-week savings challenge page, English (savings-challenge.html) and Spanish (reto-ahorro.html).
// Logic in lib/challenge.js. Both pages share one saved challenge in this browser.
import config from './config.js';
import { initTracking } from './lib/track.js';
import * as C from './lib/challenge.js';
import { buildIcs } from './lib/ics.js';
import { today as todayIso } from './lib/dates.js';
import { $, esc, store, download } from './page.js';

const es = document.documentElement.lang.startsWith('es');
const loc = es ? 'es-US' : 'en-US';
const money = (n, d = 2) => (Number(n) || 0).toLocaleString(loc, { style: 'currency', currency: 'USD', minimumFractionDigits: d, maximumFractionDigits: d });
const day = (s) => (s ? new Date(`${s}T12:00:00`).toLocaleDateString(loc, { month: 'short', day: 'numeric' }) : '');
const T = es ? {
  plans: { classic: 'Clásico: sube cada semana ($1, $2, $3…)', reverse: 'Al revés: lo más grande primero', even: 'Parejo: lo mismo cada semana', holiday: 'Diciembre ligero: sube, pero sin subir en las últimas 6 semanas' },
  week: 'Semana', of: 'de', saved: 'ahorrado', left: 'faltan',
  ahead: (x) => `Vas <b>${money(x)}</b> adelantado. ¡Muy bien!`, onTrack: 'Vas al día.',
  behind: (x, per, n) => `Vas <b>${money(x)}</b> atrasado. Ponte al día con <b>${money(per)}</b> extra por semana durante ${n} semanas, o completa una semana chica hoy.`,
  notStarted: (d) => `Empieza el ${d}. Puedes marcar semanas antes si quieres adelantarte.`,
  next: (r) => `Siguiente: semana ${r.week}${r.date ? ` (${day(r.date)})` : ''}, ${money(r.amount)}.`,
  streak: (n) => `Racha: ${n} semana${n === 1 ? '' : 's'} seguidas.`,
  done: (g) => `<b>¡Lo lograste!</b> Ahorraste ${money(g)} en 52 semanas.`,
  ics: 'Reto de ahorro de 52 semanas', icsWeek: (r) => `Semana ${r.week}: ahorra ${money(r.amount)}`, icsDesc: (r) => `Total al terminar esta semana: ${money(r.total)}.`,
  confirmReset: '¿Borrar tu progreso y empezar de nuevo?', file: 'reto-52-semanas.ics',
  weekAria: (r) => `Semana ${r.week}, ${money(r.amount)}`,
} : {
  plans: { classic: 'Classic: a little more each week ($1, $2, $3…)', reverse: 'Reverse: biggest weeks first', even: 'Even: the same every week', holiday: 'Light December: rising, but flat for the last 6 weeks' },
  week: 'Week', of: 'of', saved: 'saved', left: 'to go',
  ahead: (x) => `You're <b>${money(x)}</b> ahead. Nice work.`, onTrack: "You're right on track.",
  behind: (x, per, n) => `You're <b>${money(x)}</b> behind. Catch up with <b>${money(per)}</b> extra a week for ${n} weeks, or tick off a small week today.`,
  notStarted: (d) => `It starts on ${d}. You can tick weeks early if you want a head start.`,
  next: (r) => `Next: week ${r.week}${r.date ? ` (${day(r.date)})` : ''}, ${money(r.amount)}.`,
  streak: (n) => `Streak: ${n} week${n === 1 ? '' : 's'} in a row.`,
  done: (g) => `<b>You did it!</b> You saved ${money(g)} in 52 weeks.`,
  ics: '52-week savings challenge', icsWeek: (r) => `Week ${r.week}: save ${money(r.amount)}`, icsDesc: (r) => `Total once this week is done: ${money(r.total)}.`,
  confirmReset: 'Clear your progress and start again?', file: '52-week-challenge.ics',
  weekAria: (r) => `Week ${r.week}, ${money(r.amount)}`,
};

const KEY = 'mms-52-week-v1';
const today = todayIso();
let st = {};
try { st = JSON.parse(store.get(KEY)) || {}; } catch { /* first visit */ }
st = { plan: 'classic', goal: C.CLASSIC_TOTAL, start: C.nextMonday(today), dollars: false, done: {}, ...st };
const save = () => store.set(KEY, JSON.stringify(st));
const form = $('#setup');
form.plan.innerHTML = C.PLANS.map((p) => `<option value="${p}">${esc(T.plans[p])}</option>`).join('');
form.plan.value = st.plan; form.goal.value = st.goal; form.start.value = st.start; form.dollars.checked = st.dollars;
if ($('#site-link')) $('#site-link').href = config.siteUrl;

const rows = () => C.schedule({ plan: st.plan, goal: st.goal, start: st.start, round: st.dollars ? 'dollars' : 'cents' });

function render() {
  const r = rows();
  const p = C.progress(r, st.done, today);
  const cu = C.catchUp(r, st.done, today);
  const dollars = st.dollars ? 0 : 2;
  let status;
  if (p.finished) status = T.done(p.goal);
  else if (p.dueWeek === 0) status = T.notStarted(day(st.start));
  else if (p.gap === null || p.gap === 0) status = T.onTrack;
  else if (p.gap > 0) status = T.ahead(p.gap);
  else status = T.behind(cu.behind, cu.extraPerWeek, cu.weeksLeft);
  $('#progress').innerHTML = `<p class="score-big"><b>${money(p.saved, 0)}</b><small> ${T.of} ${money(p.goal, 0)} ${T.saved}</small></p>
    <div class="bar big-bar" role="img" aria-label="${p.pct}%"><span style="width:${Math.min(100, p.pct)}%"></span></div>
    <p>${p.count}/52 · ${money(p.left, 0)} ${T.left}</p>
    <p>${status}</p>${p.next && !p.finished ? `<p>${T.next(p.next)}</p>` : ''}${p.streak > 1 ? `<p class="tiny">${T.streak(p.streak)}</p>` : ''}`;
  $('#weeks').innerHTML = r.map((w) => `<li class="${st.done[w.week] ? 'is-done' : ''}${p.dueWeek === w.week ? ' is-now' : ''}"><label class="pick"><input type="checkbox" data-week="${w.week}"${st.done[w.week] ? ' checked' : ''} aria-label="${esc(T.weekAria(w))}">
    <span><b>${money(w.amount, dollars)}</b><small>${T.week} ${w.week}${w.date ? ` · ${day(w.date)}` : ''}</small></span></label></li>`).join('');
}

form.addEventListener('input', (e) => {
  if (e.target.name === 'goal') st.goal = Math.min(1e7, Math.max(0, Number(e.target.value) || 0));
  if (e.target.name === 'plan') st.plan = e.target.value;
  if (e.target.name === 'start') st.start = e.target.value;
  if (e.target.name === 'dollars') st.dollars = e.target.checked;
  save(); render();
});
form.addEventListener('submit', (e) => e.preventDefault());
$('#weeks').addEventListener('change', (e) => {
  const w = e.target.dataset.week;
  if (!w) return;
  if (e.target.checked) st.done[w] = true; else delete st.done[w];
  save(); render();
});
$('#ics').addEventListener('click', () => {
  const r = rows().filter((w) => w.date && !st.done[w.week]);
  download(T.file, buildIcs(r.map((w) => ({ uid: `mms-52-${st.start}-${w.week}`, date: w.date, title: T.icsWeek(w), description: T.icsDesc(w) })), { name: T.ics }), 'text/calendar');
});
$('#print').addEventListener('click', () => window.print());
$('#reset').addEventListener('click', () => {
  if (!confirm(T.confirmReset)) return;
  st.done = {}; save(); render();
});
render();
initTracking({ config, app: 'budget', page: es ? 'reto-ahorro' : 'savings-challenge' });
