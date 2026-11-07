import config from './config.js';
import { buildScript, scriptToText, NICHES, FORMATS } from './lib/scripts.js';
import { initTracking } from './lib/track.js';

const $ = (s) => document.querySelector(s);
const esc = (s) => String(s).replace(/[&<>"']/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' })[c]);
const live = (u) => typeof u === 'string' && /^https:\/\//.test(u) && !/REPLACE_ME/i.test(u);
const form = $('#builder');
const DRAFT = 'ad-script-draft';
let last = null;

$('#studio').textContent = config.studio;
if (live(config.packagesUrl)) { $('#packages-link').href = config.packagesUrl; $('#packages-link').hidden = false; }
$('#pitch-text').innerHTML = `We turn scripts like this into finished vertical video ads. <b>${esc(config.starter.name)}: ${esc(config.starter.price)}</b> for ${esc(config.starter.what)}.${live(config.packagesUrl) ? ` <a href="${esc(config.packagesUrl)}">See all packages</a>.` : ''}`;
$('#niche').innerHTML = Object.entries(NICHES).map(([k, n]) => `<option value="${k}">${esc(n.label)}</option>`).join('');
$('#format').innerHTML = Object.entries(FORMATS).map(([k, f]) => `<option value="${k}">${esc(f.label)}</option>`).join('');

function syncFormat() {
  const f = form.format.value;
  $('#format-best').textContent = `Best for: ${FORMATS[f].best}`;
  $('#problem-row').hidden = !['problem-solution', 'before-after'].includes(f);
  $('#alt-row').hidden = f !== 'comparison';
  if (f === 'founder') form.presenter.value = 'founder';
}
form.format.addEventListener('change', syncFormat);

const values = () => {
  const fd = Object.fromEntries(new FormData(form));
  return { ...fd, facts: [fd.fact1, fd.fact2, fd.fact3] };
};

function render(s) {
  const lint = s.lint.length
    ? `<div class="lint"><b>Check this wording before you film</b><ul>${s.lint.map((l) => `<li>"${esc(l.phrase)}": ${esc(l.reason)}</li>`).join('')}</ul></div>`
    : '';
  $('#out').innerHTML = `
    <h2>${esc(s.title)}</h2>
    <p class="meta">${esc(s.format)} · ${s.length}s · ${esc(s.presenter)} · 9:16 vertical <span class="label-chip">${esc(s.label)}</span></p>
    ${lint}
    <table class="script"><thead><tr><th>Time</th><th>What we see</th><th>Voice</th><th>On screen</th></tr></thead><tbody>
      ${s.rows.map((r) => `<tr><td>${esc(r.time)}</td><td data-h="See">${esc(r.visual)}</td><td data-h="Say" class="voice">"${esc(r.voice)}"</td><td data-h="Text" class="ost">${esc(r.text)}</td></tr>`).join('')}
    </tbody></table>
    <h3>Three hooks to test</h3>
    <ol class="hooks" type="A">${s.hooks.map((h) => `<li>"${esc(h)}"</li>`).join('')}</ol>
    <h3>Caption</h3><p class="caption">${esc(s.caption)}</p>
    <h3>Shot list</h3><ul class="shots">${s.shotList.map((x) => `<li>${esc(x.replace(/^\d+\.\s*/, ''))}</li>`).join('')}</ul>
    <h3>Before you film</h3><ul>${s.notes.map((n) => `<li>${esc(n)}</li>`).join('')}</ul>
    <div class="row"><button type="button" class="btn small" id="copy">Copy script</button><button type="button" class="btn small ghost" id="print">Print or save as PDF</button><button type="button" class="btn small ghost" id="another">Try another style</button></div>`;
  $('#out').hidden = false;
  $('#copy').addEventListener('click', async () => {
    const t = scriptToText(s);
    try { await navigator.clipboard.writeText(t); $('#copy').textContent = 'Copied'; } catch { prompt('Copy your script', t); }
  });
  $('#print').addEventListener('click', () => window.print());
  $('#another').addEventListener('click', () => {
    const keys = Object.keys(FORMATS).filter((k) => k !== 'founder');
    form.format.value = keys[(keys.indexOf(form.format.value) + 1) % keys.length];
    syncFormat();
    build();
  });
}

function build(e) {
  e?.preventDefault();
  try {
    last = buildScript(values());
  } catch (err) {
    $('#out').innerHTML = `<p><b>${esc(err.message)}</b></p>`;
    $('#out').hidden = false;
    return;
  }
  render(last);
  $('#script-field').value = scriptToText(last).slice(0, 4000);
  try { localStorage.setItem(DRAFT, JSON.stringify(Object.fromEntries(new FormData(form)))); } catch { /* private mode */ }
  if (e && window.innerWidth <= 860) $('#out').scrollIntoView({ behavior: 'smooth', block: 'start' });
}
form.addEventListener('submit', build);

// Bring back the last product they worked on.
try {
  const d = JSON.parse(localStorage.getItem(DRAFT) || 'null');
  if (d) for (const [k, v] of Object.entries(d)) if (form[k]) form[k].value = v;
} catch { /* ignore */ }
syncFormat();

$('#sample-form').addEventListener('submit', async (e) => {
  e.preventDefault();
  const f = e.target;
  if (f.website.value) return;
  if (!$('#script-field').value && form.brand.value) { try { $('#script-field').value = scriptToText(buildScript(values())).slice(0, 4000); } catch { /* optional */ } }
  f.querySelector('button').disabled = true;
  try {
    const res = await fetch('/', { method: 'POST', headers: { 'Content-Type': 'application/x-www-form-urlencoded' }, body: new URLSearchParams(new FormData(f)).toString() });
    if (!res.ok) throw new Error(String(res.status));
    $('#sample-msg').textContent = "Got it. We'll reply by email within two working days to say whether we can take it this week.";
    f.reset();
  } catch {
    $('#sample-msg').textContent = "That didn't send. Please try again in a minute.";
    f.querySelector('button').disabled = false;
  }
});

initTracking({ config, app: 'ad-script-builder', page: 'builder' });
