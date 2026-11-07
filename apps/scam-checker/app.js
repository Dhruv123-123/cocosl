import config from './config.js';
import { analyzeMessage } from './lib/scan.js';

const $ = (s) => document.querySelector(s);
const esc = (s) => String(s).replace(/[&<>"']/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' })[c]);
const live = (u) => typeof u === 'string' && /^https:\/\//.test(u) && !/REPLACE_ME/i.test(u);

const EXAMPLES = {
  toll: { text: 'E-ZPass: You have an unpaid toll of $6.85. To avoid a late fee of $50, pay within 24 hours: https://ezpass-tollservice.top/pay\n\n(Reply Y, then reopen this message to activate the link.)', sender: '+63 917 555 0142' },
  package: { text: 'USPS: Your package could not be delivered due to an incomplete address. Update your details and pay the $1.99 redelivery fee: usps-redelivery-center.com/track', sender: '' },
  job: { text: "Hi! I'm a recruiter with a remote part-time job. Earn $300/day just liking videos. Message me on WhatsApp to start today.", sender: '' },
  safe: { text: "Hey! Are we still on for dinner Thursday? I can pick you up around 7.", sender: '' },
};

const LEVEL_TEXT = {
  high: ['High risk', 'This has several signs of a scam. Do not click, reply, or pay.'],
  medium: ['Be careful', 'This has some warning signs. Check with the company directly before doing anything.'],
  low: ['No common red flags found', "That's a good sign, but it isn't proof. Stay careful if it asks for money or information."],
};

function render(r) {
  const [title, sub] = LEVEL_TEXT[r.level];
  const signals = r.signals.filter((s) => s.id !== 'money-amount' || r.level !== 'low');
  const signalHtml = signals.length
    ? `<h3>Red flags we found</h3><ul class="flags">${signals.map((s) => `<li><b>${esc(s.label)}</b><br><span class="quote">"${esc(s.evidence)}"</span><br>${esc(s.advice)}</li>`).join('')}</ul>`
    : '';
  const sender = r.senderIssues.length ? `<h3>Sender</h3><ul class="flags">${r.senderIssues.map((s) => `<li>${esc(s.label)}</li>`).join('')}</ul>` : '';
  const links = r.links.length
    ? `<h3>Links in the message</h3><ul class="links">${r.links.map((l) => `<li><code>${esc(l.host || l.url)}</code> ${l.official ? '<span class="ok">official site</span>' : ''}${l.issues.length ? `<ul>${l.issues.map((i) => `<li>${esc(i.label)}</li>`).join('')}</ul>` : l.official ? '' : '<ul><li>No specific problems found with this address, but only open it if you trust the sender.</li></ul>'}</li>`).join('')}</ul>`
    : '';
  const offers = config.offers.filter((o) => o.showWhen.includes(r.level) && live(o.url));
  const offerHtml = offers.length
    ? `<div class="offers"><h3>Protect yourself next time</h3>${offers.map((o) => `<div class="offer"><b>${esc(o.title)}</b><p>${esc(o.blurb)}</p><a class="btn small" href="${esc(o.url)}" rel="sponsored noopener" target="_blank">${esc(o.label)}</a></div>`).join('')}<p class="tiny">Affiliate links: we may earn a commission at no cost to you.</p></div>`
    : '';
  const product = live(config.product.url)
    ? `<div class="offer product"><b>${esc(config.product.name)} (${esc(config.product.price)})</b><p>${esc(config.product.pitch)}</p><a class="btn small alt" href="${esc(config.product.url)}">Get the kit</a></div>`
    : '';
  const share = r.level !== 'low'
    ? `<button type="button" id="warn" class="link">Copy a warning to send to family</button>`
    : '';
  $('#result').innerHTML = `
    <div class="verdict ${r.level}">
      <div class="meter" role="meter" aria-valuemin="0" aria-valuemax="100" aria-valuenow="${r.score}" aria-label="Risk score"><span style="width:${Math.max(r.score, 3)}%"></span></div>
      <p class="score">${esc(title)} <small>${r.score}/100</small></p>
      <p>${esc(sub)}${r.category && r.level !== 'low' ? ` Looks like: <b>${esc(r.category)}</b>.` : ''}</p>
    </div>
    ${signalHtml}${sender}${links}
    <h3>What to do</h3><ol>${r.steps.map((s) => `<li>${esc(s)}</li>`).join('')}</ol>
    ${share}${offerHtml}${product}`;
  $('#result').hidden = false;
  $('#warn')?.addEventListener('click', async () => {
    const msg = `Heads up: I got a ${r.category ? r.category.toLowerCase() : 'scam message'} today. ${r.signals.slice(0, 2).map((s) => s.label).join('; ')}. If you get one, don't click the link or reply. Check in the official app instead.`;
    try { await navigator.clipboard.writeText(msg); $('#warn').textContent = 'Copied. Paste it into your family chat.'; } catch { prompt('Copy this warning', msg); }
  });
}

function check(e) {
  e?.preventDefault();
  const text = $('#message').value;
  if (!text.trim()) { $('#message').focus(); return; }
  render(analyzeMessage(text, { sender: $('#sender').value }));
  $('#result').scrollIntoView({ behavior: 'smooth', block: 'start' });
}

$('#checker').addEventListener('submit', check);
document.querySelectorAll('[data-example]').forEach((b) => b.addEventListener('click', () => {
  const ex = EXAMPLES[b.dataset.example];
  $('#message').value = ex.text;
  $('#sender').value = ex.sender;
  if (ex.sender) $('details').open = true;
  check();
}));

// Email signup (same behaviour as the calculators).
(function signup() {
  const form = document.querySelector('form.signup');
  const e = config.email;
  document.querySelector('.signup-pitch').textContent = e.pitch;
  if (e.provider === 'none') { form.parentElement.hidden = true; return; }
  if (e.provider !== 'netlify') { form.removeAttribute('data-netlify'); form.action = e.action || '#'; form.querySelector('input[type=email]').name = e.emailField || 'email'; }
  form.addEventListener('submit', async (ev) => {
    ev.preventDefault();
    if (form.website.value) return;
    if (e.provider !== 'netlify' && !e.action) { alert('Email signup is not connected yet: set email.action in config.js.'); return; }
    const btn = form.querySelector('button'); btn.disabled = true; btn.textContent = 'Sending…';
    try {
      await fetch(e.provider === 'netlify' ? '/' : form.action, { method: 'POST', mode: e.provider === 'netlify' ? 'same-origin' : 'no-cors', headers: { 'Content-Type': 'application/x-www-form-urlencoded' }, body: new URLSearchParams(new FormData(form)).toString() });
      location.href = e.thanksUrl;
    } catch { form.submit(); }
  });
})();

if (config.analytics.plausibleDomain) {
  const s = document.createElement('script'); s.defer = true; s.dataset.domain = config.analytics.plausibleDomain; s.src = 'https://plausible.io/js/script.js'; document.head.append(s);
}
