// Scam guide pages: send the pasted message to the checker (in the URL hash, which browsers
// never send to the server), show the relevant offers, and wire up the email signup.
import config from './config.js';
import { setupSignup } from './signup.js';
import { initTracking } from './lib/track.js';

const root = document.body.dataset.root || '../../';
const esc = (s) => String(s).replace(/[&<>"']/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' })[c]);
const live = (u) => typeof u === 'string' && /^https:\/\//.test(u) && !/REPLACE_ME/i.test(u);

const form = document.querySelector('#guide-check');
form?.addEventListener('submit', (e) => {
  e.preventDefault();
  const text = form.querySelector('textarea').value.trim();
  if (!text) return form.querySelector('textarea').focus();
  location.href = `${root}#m=${encodeURIComponent(text.slice(0, 4000))}`;
});

const es = document.documentElement.lang.startsWith('es');
const offers = config.offers.filter((o) => o.showWhen.includes('high') && live(o.url)).map((o) => (es && o.es ? { ...o, ...o.es } : o));
const box = document.querySelector('#offers');
if (box && offers.length) {
  box.innerHTML = `<h2>${es ? 'Protégete la próxima vez' : 'Protect yourself next time'}</h2>${offers.map((o) => `<div class="offer"><b>${esc(o.title)}</b><p>${esc(o.blurb)}</p><a class="btn small" href="${esc(o.url)}" rel="sponsored noopener" target="_blank">${esc(o.label)}</a></div>`).join('')}<p class="tiny">${es ? 'Enlaces de afiliado: podemos ganar una comisión sin costo para ti.' : 'Affiliate links: we may earn a commission at no cost to you.'}</p>`;
  box.hidden = false;
}
setupSignup(root);
initTracking({ config, app: 'scam-checker', page: location.pathname.split('/').filter(Boolean).pop() || 'guides' });
