// Money personality quiz page (money-personality.html). Types and scoring in lib/personality.js.
import config from './config.js';
import { initTracking } from './lib/track.js';
import * as P from './lib/personality.js';
import { $, esc, store } from './page.js';

const KEY = 'mms-personality-v1';
let answers = {};
try { answers = JSON.parse(store.get(KEY)) || {}; } catch { /* first visit */ }
const form = $('#quiz');
$('#site-link').href = config.siteUrl;
const shared = new URLSearchParams(location.search).get('type');

form.innerHTML = `<fieldset class="card area-set"><legend><h2>8 questions</h2></legend>${P.QUESTIONS.map((q, i) => `
  <div class="question" role="radiogroup" aria-labelledby="pq-${i}"><p id="pq-${i}" class="q-text"><span class="q-num">${i + 1}.</span> ${esc(q.q)}</p>
    <div class="q-options">${q.o.map(([text], j) => `<label class="pick"><input type="radio" name="q${i}" value="${j}"${answers[i] === j ? ' checked' : ''}> <span>${esc(text)}</span></label>`).join('')}</div></div>`).join('')}</fieldset>`;

const toolList = (t) => `<ul class="plain-list">${P.TYPES[t].tools.map(([label, href]) => `<li><a href="../${esc(href)}">${esc(label)}</a></li>`).join('')}</ul>`;
function typeCard(t, lead) {
  const x = P.TYPES[t];
  return `<p class="tiny">${lead}</p><h2><span aria-hidden="true">${x.emoji}</span> ${esc(x.name)}</h2><p>${esc(x.blurb)}</p>
    <p><b>Your strength:</b> ${esc(x.strength)}</p><p><b>Watch out for:</b> ${esc(x.blindSpot)}</p><h3>Free tools for you</h3>${toolList(t)}`;
}

function render() {
  const r = P.score(answers);
  if (!r.complete) {
    if (shared && P.isType(shared) && !r.answered) { $('#result').innerHTML = `${typeCard(shared, 'Someone shared their result with you.')}<p><b>Take the quiz above to find yours.</b></p>`; return; }
    $('#result').innerHTML = `<p class="tiny">${r.answered ? `${r.answered} of ${r.total} answered. Your result appears when you finish.` : 'Answer the questions above and your result appears here.'}</p>`;
    return;
  }
  const second = r.second ? `<div class="choice"><p class="tiny">With a bit of</p><h3><span aria-hidden="true">${P.TYPES[r.second].emoji}</span> ${esc(P.TYPES[r.second].name)}</h3><p>${esc(P.TYPES[r.second].blindSpot)}</p>${toolList(r.second)}</div>` : '';
  $('#result').innerHTML = typeCard(r.top, `You're mostly (${r.pct}% of your answers)`)
    + (second ? `<div class="choices">${second}</div>` : '')
    + '<p class="tiny">Want the full picture? Try the <a href="checkup.html">annual money checkup</a>: 20 questions and a score out of 100.</p>';
}

form.addEventListener('change', (e) => {
  if (e.target.type !== 'radio') return;
  answers[Number(e.target.name.slice(1))] = Number(e.target.value);
  store.set(KEY, JSON.stringify(answers));
  render();
});
$('#share').addEventListener('click', async () => {
  const r = P.score(answers);
  const url = new URL(location.href);
  url.search = r.complete ? `?type=${r.top}` : '';
  try { await navigator.clipboard.writeText(url.href); $('#share').textContent = 'Link copied'; } catch { prompt('Copy this link:', url.href); }
});
$('#reset').addEventListener('click', () => {
  answers = {}; store.set(KEY, '{}');
  for (const el of form.querySelectorAll('input')) el.checked = false;
  render();
});
render();
initTracking({ config, app: 'budget', page: 'money-personality' });
