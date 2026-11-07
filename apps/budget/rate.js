import config from './config.js';
import { rateBudget, FIELDS } from './lib/rate.js';

const $ = (s) => document.querySelector(s);
const esc = (s) => String(s).replace(/[&<>"']/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' })[c]);
const live = (u) => typeof u === 'string' && /^https:\/\//.test(u) && !/REPLACE_ME/i.test(u);
const form = $('#rate-form');
let last = null;

function values() {
  const v = {};
  for (const k of FIELDS) v[k] = form[k].value;
  return v;
}

function render(e) {
  e?.preventDefault();
  let r;
  try { r = rateBudget(values()); } catch (err) { $('#rate-result').innerHTML = `<p class="neg">${esc(err.message)}</p>`; $('#rate-result').hidden = false; return; }
  last = r;
  $('#rate-result').innerHTML = `
    <div class="grade-row"><div class="grade g${r.grade}">${r.grade}</div><div><p class="score-big">${r.score}<small>/100</small></p>
      <p class="tiny">${r.score >= 85 ? 'Strong. Keep it on autopilot.' : r.score >= 70 ? 'Solid, with a couple of easy wins.' : r.score >= 55 ? 'Getting there. The moves below matter.' : 'Fixable. Start with move 1 this week.'}</p></div></div>
    <h3>Your three next moves</h3>
    <ol class="moves">${r.moves.map((m) => `<li>${esc(m.text)}</li>`).join('')}</ol>
    <h3>How the score breaks down</h3>
    <table class="plan breakdown"><tbody>${r.parts.map((p) => `<tr><td>${esc(p.label)}<small>${esc(p.value)} · guide: ${esc(p.guide)}</small></td>
      <td class="num">${p.score}/${p.max}<div class="bar"><span style="width:${(p.score / p.max) * 100}%"></span></div></td></tr>`).join('')}</tbody></table>
    <div class="row" style="margin-top:12px"><button type="button" id="share-score" class="btn ghost small">Copy my score</button><a class="btn small" href="./">Fix it with the free budget app</a></div>`;
  $('#rate-result').hidden = false;
  $('#numbers-field').value = JSON.stringify({ ...values(), score: r.score, grade: r.grade });
  $('#share-score').addEventListener('click', async () => {
    const t = `My budget scored ${r.score}/100 (${r.grade}) on Rate My Budget. What's yours? ${location.href.split('?')[0]}`;
    try { await navigator.clipboard.writeText(t); $('#share-score').textContent = 'Copied'; } catch { prompt('Copy this', t); }
  });
  $('#rate-result').scrollIntoView({ behavior: 'smooth', block: 'start' });
}

form.addEventListener('submit', render);

const offer = config.review;
if (offer && live(offer.url)) {
  $('#review-offer').innerHTML = `<div class="offer-box"><h3>${esc(offer.name)} (${esc(offer.price)})</h3><p>${esc(offer.pitch)}</p><a class="btn small" href="${esc(offer.url)}">Book a review</a></div>`;
}

$('#submit-form').addEventListener('submit', async (e) => {
  e.preventDefault();
  const f = e.target;
  if (f.website.value) return;
  if (!last) render();
  $('#numbers-field').value = JSON.stringify({ ...values(), score: last?.score, grade: last?.grade });
  f.querySelector('button').disabled = true;
  try {
    await fetch('/', { method: 'POST', headers: { 'Content-Type': 'application/x-www-form-urlencoded' }, body: new URLSearchParams(new FormData(f)).toString() });
    $('#submit-msg').textContent = "Got it, thank you. If we feature your budget, we'll email you first.";
    f.reset();
  } catch {
    $('#submit-msg').textContent = "That didn't send. Please try again in a minute.";
    f.querySelector('button').disabled = false;
  }
});
