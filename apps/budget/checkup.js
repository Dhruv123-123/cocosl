// Annual money checkup page (checkup.html). Logic in lib/checkup.js.
import config from './config.js';
import { initTracking } from './lib/track.js';
import * as K from './lib/checkup.js';
import { $, esc, store } from './page.js';

const KEY = 'mms-checkup-v1';
let answers = {};
try { answers = JSON.parse(store.get(KEY)) || {}; } catch { /* first visit */ }
const form = $('#checkup');
$('#site-link').href = config.siteUrl;

// One fieldset per area, radio buttons per question.
form.innerHTML = Object.entries(K.AREAS).map(([area, label]) => `<fieldset class="card area-set"><legend><h2>${esc(label)}</h2></legend>
  ${K.QUESTIONS.filter((q) => q.area === area).map((q) => {
    const n = K.QUESTIONS.indexOf(q) + 1;
    return `<div class="question" role="radiogroup" aria-labelledby="q-${q.id}"><p id="q-${q.id}" class="q-text"><span class="q-num">${n}.</span> ${esc(q.q)}</p>
      <div class="q-options">${q.o.map(([text], i) => `<label class="pick"><input type="radio" name="${q.id}" value="${i}"${answers[q.id] === i ? ' checked' : ''}> <span>${esc(text)}</span></label>`).join('')}</div></div>`;
  }).join('')}</fieldset>`).join('');

const isExternal = (u) => /^https?:/.test(u);

function render() {
  const r = K.report(answers);
  if (!r.answered) { $('#report').innerHTML = '<p class="tiny">Answer the questions above and your report appears here.</p>'; return; }
  $('#report').innerHTML = `<h2>Your report${r.complete ? '' : ` (${r.answered} of ${r.total} answered)`}</h2>
    <div class="score-row"><p class="score-big"><b>${r.score}</b><small>/100</small></p><p class="grade grade-${r.grade}">Grade ${r.grade}</p></div>
    <ul class="areas">${r.areas.filter((a) => a.score !== null).map((a) => `<li><span>${esc(a.label)}</span><span class="bar" role="img" aria-label="${a.score} out of 100"><span style="width:${a.score}%" class="${a.score < 50 ? 'over' : ''}"></span></span><b>${a.score}</b></li>`).join('')}</ul>
    ${r.fixes.length ? `<h3>Fix these first</h3><ol class="fixes">${r.fixes.slice(0, 7).map((f) => `<li${f.urgent ? ' class="urgent"' : ''}><span class="tiny">${esc(f.area)}</span><br>${esc(f.fix)} <a href="${esc(f.link)}"${isExternal(f.link) ? ' target="_blank" rel="noopener"' : ''}>${esc(f.tool)}</a></li>`).join('')}</ol>${r.fixes.length > 7 ? `<p class="tiny">Plus ${r.fixes.length - 7} smaller fix${r.fixes.length - 7 === 1 ? '' : 'es'}. Start with the ones above.</p>` : ''}`
      : '<p><b>Full marks on everything you answered.</b> Do this again next year.</p>'}
    ${r.strengths.length >= 3 ? `<p class="tiny">Already strong: ${r.strengths.length} of ${r.answered} answers. Keep those habits going.</p>` : ''}
    <p class="tiny">Checked on ${new Date().toLocaleDateString('en-US', { month: 'long', day: 'numeric', year: 'numeric' })}.</p>`;
}

form.addEventListener('change', (e) => {
  if (e.target.type !== 'radio') return;
  answers[e.target.name] = Number(e.target.value);
  store.set(KEY, JSON.stringify(answers));
  render();
});
$('#print').addEventListener('click', () => window.print());
$('#reset').addEventListener('click', () => {
  if (!confirm('Clear all your answers?')) return;
  answers = {}; store.set(KEY, '{}');
  for (const el of form.querySelectorAll('input')) el.checked = false;
  render();
});
render();
initTracking({ config, app: 'budget', page: 'checkup' });
