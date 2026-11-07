import config from './config.js';
import { analyzeMessage } from './lib/scan.js';
import { setupSignup } from './signup.js';
import { ES } from './lib/i18n.js';
import { initTracking } from './lib/track.js';

const es = document.documentElement.lang.startsWith('es');

const $ = (s) => document.querySelector(s);
const esc = (s) => String(s).replace(/[&<>"']/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' })[c]);
const live = (u) => typeof u === 'string' && /^https:\/\//.test(u) && !/REPLACE_ME/i.test(u);

const EXAMPLES_EN = {
  toll: { text: 'E-ZPass: You have an unpaid toll of $6.85. To avoid a late fee of $50, pay within 24 hours: https://ezpass-tollservice.top/pay\n\n(Reply Y, then reopen this message to activate the link.)', sender: '+63 917 555 0142' },
  package: { text: 'USPS: Your package could not be delivered due to an incomplete address. Update your details and pay the $1.99 redelivery fee: usps-redelivery-center.com/track', sender: '' },
  job: { text: "Hi! I'm a recruiter with a remote part-time job. Earn $300/day just liking videos. Message me on WhatsApp to start today.", sender: '' },
  safe: { text: "Hey! Are we still on for dinner Thursday? I can pick you up around 7.", sender: '' },
};

const EXAMPLES = es ? ES.examples : EXAMPLES_EN;

const LEVEL_TEXT_EN = {
  high: ['High risk', 'This has several signs of a scam. Do not click, reply, or pay.'],
  medium: ['Be careful', 'This has some warning signs. Check with the company directly before doing anything.'],
  low: ['No common red flags found', "That's a good sign, but it isn't proof. Stay careful if it asks for money or information."],
};

const UI_EN = {
  looksLike: 'Looks like:', flags: 'Red flags we found', sender: 'Sender', links: 'Links in the message', official: 'official site',
  noIssues: 'No specific problems found with this address, but only open it if you trust the sender.', whatToDo: 'What to do',
  warn: 'Copy a warning to send to family', copied: 'Copied. Paste it into your family chat.', protect: 'Protect yourself next time',
  affiliate: 'Affiliate links: we may earn a commission at no cost to you.', getKit: 'Get the kit',
  warning: (cat, flags) => `Heads up: I got a ${cat ? cat.toLowerCase() : 'scam message'} today. ${flags}. If you get one, don't click the link or reply. Check in the official app instead.`,
};
const UI = es ? ES.ui : UI_EN;
const LEVEL_TEXT = es ? ES.ui.level : LEVEL_TEXT_EN;
const sig = (s) => (es && ES.signals[s.id] ? { ...s, label: ES.signals[s.id][0], advice: ES.signals[s.id][1] } : s);
const issue = (i) => (es && ES.links[i.code] ? ES.links[i.code](i.param) : i.label);

function render(r) {
  if (es) r = { ...r, category: ES.categories[r.categoryId] || r.category, steps: r.stepIds.map((id) => ES.steps[id]), signals: r.signals.map(sig) };
  const [title, sub] = LEVEL_TEXT[r.level];
  const signals = r.signals.filter((s) => s.id !== 'money-amount' || r.level !== 'low');
  const signalHtml = signals.length
    ? `<h3>${UI.flags}</h3><ul class="flags">${signals.map((s) => `<li><b>${esc(s.label)}</b><br><span class="quote">"${esc(s.evidence)}"</span><br>${esc(s.advice)}</li>`).join('')}</ul>`
    : '';
  const sender = r.senderIssues.length ? `<h3>${UI.sender}</h3><ul class="flags">${r.senderIssues.map((s) => `<li>${esc(issue(s))}</li>`).join('')}</ul>` : '';
  const links = r.links.length
    ? `<h3>${UI.links}</h3><ul class="links">${r.links.map((l) => `<li><code>${esc(l.host || l.url)}</code> ${l.official ? `<span class="ok">${UI.official}</span>` : ''}${l.issues.length ? `<ul>${l.issues.map((i) => `<li>${esc(issue(i))}</li>`).join('')}</ul>` : l.official ? '' : `<ul><li>${UI.noIssues}</li></ul>`}</li>`).join('')}</ul>`
    : '';
  const offers = config.offers.filter((o) => o.showWhen.includes(r.level) && live(o.url)).map((o) => (es && o.es ? { ...o, ...o.es } : o));
  const offerHtml = offers.length
    ? `<div class="offers"><h3>${UI.protect}</h3>${offers.map((o) => `<div class="offer"><b>${esc(o.title)}</b><p>${esc(o.blurb)}</p><a class="btn small" href="${esc(o.url)}" rel="sponsored noopener" target="_blank">${esc(o.label)}</a></div>`).join('')}<p class="tiny">${UI.affiliate}</p></div>`
    : '';
  const product = live(config.product.url)
    ? `<div class="offer product"><b>${esc(config.product.name)} (${esc(config.product.price)})</b><p>${esc(config.product.pitch)}</p><a class="btn small alt" href="${esc(config.product.url)}">${UI.getKit}</a></div>`
    : '';
  const share = r.level !== 'low'
    ? `<button type="button" id="warn" class="link">${UI.warn}</button>`
    : '';
  $('#result').innerHTML = `
    <div class="verdict ${r.level}">
      <div class="meter" role="meter" aria-valuemin="0" aria-valuemax="100" aria-valuenow="${r.score}" aria-label="Risk score"><span style="width:${Math.max(r.score, 3)}%"></span></div>
      <p class="score">${esc(title)} <small>${r.score}/100</small></p>
      <p>${esc(sub)}${r.category && r.level !== 'low' ? ` ${UI.looksLike} <b>${esc(r.category)}</b>.` : ''}</p>
    </div>
    ${signalHtml}${sender}${links}
    <h3>${UI.whatToDo}</h3><ol>${r.steps.map((s) => `<li>${esc(s)}</li>`).join('')}</ol>
    ${share}${offerHtml}${product}`;
  $('#result').hidden = false;
  $('#warn')?.addEventListener('click', async () => {
    const msg = UI.warning(r.category, r.signals.slice(0, 2).map((s) => s.label).join('; '));
    try { await navigator.clipboard.writeText(msg); $('#warn').textContent = UI.copied; } catch { prompt(UI.warn, msg); }
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

setupSignup();

const fromGuide = new URLSearchParams(location.hash.slice(1)).get('m');
if (fromGuide) {
  $('#message').value = fromGuide;
  history.replaceState(null, '', location.pathname + location.search);
  check();
}

initTracking({ config, app: 'scam-checker', page: 'checker' });
