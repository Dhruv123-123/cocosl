// Scam Shield app (scam-checker/app/): home screen, checklist, red-flag quiz and report-it directory.
// One script for all four pages (body[data-page]). Data and logic in ../lib/scamapp.js. No network:
// the only requests are this site's own files, which ../sw.js saves for offline.
import { rememberAppHome } from '../lib/app-home.js';
import { mountOptin } from '../lib/optin.js';
import { mountOffer } from '../lib/offers.js';
import { QUESTIONS, verdict, VERDICT_TEXT, QUIZ, quizScore, PLACES, SITUATIONS, STATE_AGS, AG_DIRECTORY, agFor } from '../lib/scamapp.js';
import { cardModel, shareCard } from '../lib/sharecard.js';

const $ = (s) => document.querySelector(s);
const esc = (s) => String(s ?? '').replace(/[&<>"']/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' })[c]);
const store = { get: (k) => { try { return JSON.parse(localStorage.getItem(k) || 'null'); } catch { return null; } }, set: (k, v) => { try { localStorage.setItem(k, JSON.stringify(v)); } catch { /* private mode */ } } };
const page = document.body.dataset.page;
const okOrigin = location.protocol === 'https:' || ['localhost', '127.0.0.1'].includes(location.hostname);

if ('serviceWorker' in navigator && okOrigin) {
  navigator.serviceWorker.register('../sw.js', { scope: '../' }).then(() => navigator.serviceWorker.ready).then(() => {
    const s = $('#status');
    if (s) { s.classList.add('ready'); $('#status-text').textContent = 'Ready offline: every tool here works with no signal.'; }
  }).catch(() => { if ($('#status-text')) $('#status-text').textContent = 'Works online. This browser can\'t save it for offline.'; });
} else if ($('#status-text')) $('#status-text').textContent = 'Works online. This browser can\'t save it for offline.';
// Tool pages outside app/ show a Home button back here when opened from the installed app (lib/app-home.js).
if (page === 'home') rememberAppHome('../', location.href.split(/[?#]/)[0]);

function home() {
  const standalone = window.matchMedia?.('(display-mode: standalone)').matches || navigator.standalone === true;
  let deferred = null;
  window.addEventListener('beforeinstallprompt', (e) => { e.preventDefault(); deferred = e; $('#install').hidden = false; });
  $('#install-btn').addEventListener('click', async () => { if (!deferred) return; deferred.prompt(); await deferred.userChoice.catch(() => null); deferred = null; $('#install').hidden = true; });
  if (!standalone && /iPhone|iPad|iPod/.test(navigator.userAgent)) { $('#install-text').textContent = 'To add it to your home screen: tap Share, then Add to Home Screen.'; $('#install-btn').hidden = true; $('#install').hidden = false; }
}

function checklist() {
  const KEY = 'scam-app-checklist-v1';
  let answers = store.get(KEY) || {};
  $('#questions').innerHTML = QUESTIONS.map((x) => `<li><fieldset><legend>${esc(x.q)}</legend><div class="yn">
    <label><input type="radio" name="${x.id}" value="yes"${answers[x.id] === true ? ' checked' : ''}> Yes</label>
    <label><input type="radio" name="${x.id}" value="no"${answers[x.id] === false ? ' checked' : ''}> No</label></div>
    <p class="why" id="why-${x.id}" hidden>${esc(x.why)}</p></fieldset></li>`).join('');
  const render = () => {
    const v = verdict(answers);
    const t = VERDICT_TEXT[v.level];
    for (const x of QUESTIONS) $(`#why-${x.id}`).hidden = answers[x.id] !== true;
    const box = $('#verdict');
    box.className = `card verdict ${v.level}`;
    box.innerHTML = `<h2>${esc(t.title)}</h2>${v.flags.length ? `<p>${v.flags.length} red flag${v.flags.length === 1 ? '' : 's'} from ${v.answered} answer${v.answered === 1 ? '' : 's'}.</p>` : ''}${t.steps.length ? `<ol>${t.steps.map((s) => `<li>${esc(s)}</li>`).join('')}</ol>` : ''}`;
    store.set(KEY, answers);
  };
  $('#checklist').addEventListener('change', (e) => { if (e.target.name) { answers[e.target.name] = e.target.value === 'yes'; render(); } });
  $('#checklist').addEventListener('submit', (e) => e.preventDefault());
  $('#reset').addEventListener('click', () => { answers = {}; for (const i of document.querySelectorAll('#questions input')) i.checked = false; render(); document.querySelector('#questions input')?.focus(); });
  render();
}

function quiz() {
  let picks = {};
  const render = () => {
    $('#quiz').innerHTML = QUIZ.map((x, i) => {
      const p = picks[i];
      const done = typeof p === 'boolean';
      return `<li><p class="tiny">Message ${i + 1} of ${QUIZ.length}</p><p class="msg">${esc(x.m)}</p>
        <div class="pick" role="group" aria-label="Message ${i + 1}: scam or real?"><button type="button" data-i="${i}" data-a="1" aria-pressed="${p === true}">Scam</button><button type="button" data-i="${i}" data-a="0" aria-pressed="${p === false}">Real</button></div>
        ${done ? `<p class="result"><b class="${p === x.a ? 'ok' : 'no'}">${p === x.a ? 'Right' : 'Not quite'}:</b> it's ${x.a ? 'a scam' : 'real'}. ${esc(x.flags)}</p>` : ''}</li>`;
    }).join('');
    const s = quizScore(picks);
    $('#score').hidden = !s.done;
    if (s.done) {
      const level = s.right >= 9 ? 'low' : s.right >= 7 ? 'medium' : 'high';
      $('#score').className = `card verdict ${level}`;
      $('#score').innerHTML = `<h2>You got ${s.right} of ${s.total}</h2><p>${s.right >= 9 ? 'Sharp eyes. Share this quiz with someone who\'d get fooled.' : 'Scammers are good at this. The red flags to remember: pressure, a link to log in or pay, and payment by gift card, crypto or wire.'}</p><p><a href="checklist.html">Use the checklist on a real message</a></p>
        <p class="row"><button id="share-score" class="btn" type="button">Share my score</button><span id="share-msg" class="tiny" role="status"></span></p><p class="tiny">Makes a picture with your score to post or send. Nothing else is on it.</p>`;
      $('#share-score').addEventListener('click', async (ev) => {
        ev.target.disabled = true;
        try {
          const how = await shareCard(cardModel('quiz', s, `${location.host}${location.pathname}`), { filename: 'scam-quiz-score.png', title: 'Scam or real?', text: `I spotted ${s.right} of ${s.total} scams. Can you beat me?` });
          $('#share-msg').textContent = how === 'downloaded' ? 'Saved the picture. Post it anywhere.' : how === 'shared' ? 'Shared.' : '';
          try { window.plausible?.('Share', { props: { app: 'scam-checker', page: 'quiz', how } }); } catch { /* analytics off */ }
        } catch { $('#share-msg').textContent = "Couldn't make the picture in this browser."; }
        ev.target.disabled = false;
      });
    }
  };
  $('#quiz').addEventListener('click', (e) => {
    const b = e.target.closest('button[data-i]');
    if (!b) return;
    const i = Number(b.dataset.i);
    picks[i] = b.dataset.a === '1';
    render();
    document.querySelector(`button[data-i="${i}"][data-a="${b.dataset.a}"]`)?.focus();
  });
  $('#again').addEventListener('click', () => { picks = {}; render(); document.querySelector('#quiz button')?.focus(); });
  render();
}

function report() {
  const placeHtml = (k) => { const p = PLACES[k]; return `<li><a href="${esc(p.url)}"${/^https:/.test(p.url) ? ' rel="noopener"' : ''}>${esc(p.name)}</a><p>${esc(p.what)}</p></li>`; };
  $('#situations').innerHTML = SITUATIONS.map((s) => `<button type="button" data-s="${s.id}" aria-pressed="false">${esc(s.label)}</button>`).join('');
  $('#situations').addEventListener('click', (e) => {
    const b = e.target.closest('button[data-s]');
    if (!b) return;
    for (const x of document.querySelectorAll('#situations button')) x.setAttribute('aria-pressed', String(x === b));
    const s = SITUATIONS.find((x) => x.id === b.dataset.s);
    $('#advice').innerHTML = `<p class="first">First: ${esc(s.first)}</p><ul class="places">${s.places.map(placeHtml).join('')}<li><a href="#state">Your state attorney general</a><p>Choose your state below.</p></li></ul>`;
  });
  $('#state').innerHTML += STATE_AGS.map(([c, n]) => `<option value="${c}">${esc(n)}</option>`).join('');
  $('#ag-dir').href = AG_DIRECTORY;
  const saved = store.get('scam-app-state');
  const showAg = (code) => {
    const s = agFor(code);
    $('#ag').innerHTML = s ? `<a href="${esc(s[2])}" rel="noopener">File a complaint with ${esc(s[1])}'s attorney general or consumer protection office</a>` : '';
  };
  if (saved && agFor(saved)) { $('#state').value = saved; showAg(saved); }
  $('#state').addEventListener('change', (e) => { store.set('scam-app-state', e.target.value); showAg(e.target.value); });
  $('#places').innerHTML = Object.keys(PLACES).map(placeHtml).join('');
}

({ home, checklist, quiz, report })[page]?.();
if (page !== 'home') { mountOptin({ app: 'scam-checker', page: `app-${page}` }); mountOffer({ app: 'scam-checker', page: `app-${page}` }); }
