// Paid product cards on the tool hubs. Lives at the site root, not in shared/ (that folder is copied into every app) (index.html, es/index.html). A card starts as a "coming soon" placeholder and
// becomes a link once its checkout link in budget/config.js is real (no REPLACE_ME). Nothing is fetched.
const live = (u) => typeof u === 'string' && /^https:\/\//.test(u) && !/REPLACE_ME/i.test(u);
const esc = (s) => String(s ?? '').replace(/[&<>"']/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' })[c]);

export function productCard(p, lang = 'en') {
  if (!p || !live(p.url)) return null;
  const es = lang === 'es';
  const name = es ? p.nameEs || p.name : p.name;
  const pitch = es ? p.pitchEs || p.pitch : p.pitch;
  return `<a class="card" href="${esc(p.url)}"><span class="tag">${esc(p.price)}</span><h3>${esc(name)}</h3><p>${esc(pitch)}</p></a>`;
}

export function showProducts(config, root = document) {
  for (const el of root.querySelectorAll('[data-product]')) {
    const html = productCard(config[el.dataset.product], el.dataset.lang);
    if (html) el.outerHTML = html;
  }
}
