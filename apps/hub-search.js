// Search box on the hub. Runs in the browser against search-index.json (built by tools/build-search.mjs).
// Nothing typed here is sent anywhere: the index is a static file on this site, loaded once and cached offline.

// A few everyday words people type that don't appear on the pages.
export const SYNONYMS = {
  spouse: ['couple', 'partner'], wife: ['couple', 'partner'], husband: ['couple', 'partner'], boyfriend: ['couple'], girlfriend: ['couple'],
  salary: ['pay', 'paycheck', 'take'], wage: ['pay', 'paycheck'], wages: ['pay', 'paycheck'], net: ['take', 'paycheck'],
  house: ['home', 'rent', 'mortgage'], mortgage: ['home', 'buy'], apartment: ['rent'],
  car: ['afford', 'loan'], phone: ['afford'], iphone: ['afford', 'phone'], klarna: ['bnpl', 'later'], afterpay: ['bnpl', 'later'], affirm: ['bnpl', 'later'], bnpl: ['later'],
  christmas: ['holiday', 'gift'], gifts: ['holiday', 'gift'], xmas: ['holiday'],
  fraud: ['scam'], phishing: ['scam', 'link'], text: ['scam', 'message'], sms: ['scam', 'message'],
  college: ['student', 'loan'], tuition: ['student'], rap: ['repayment'], ibr: ['income'],
  credit: ['credit', 'card', 'dispute'], collections: ['debt', 'collector'], medical: ['medical', 'bill'], hospital: ['medical'],
  freelance: ['freelancer', 'invoice'], invoice: ['invoice', 'late'], subscriptions: ['subscription'], netflix: ['subscription'],
  sueldo: ['salario', 'neto', 'cheque'], salario: ['neto', 'cheque'], casa: ['rentar', 'comprar', 'hipoteca'], renta: ['rentar'], deuda: ['deudas', 'tarjeta'], deudas: ['deuda'],
  estafa: ['estafas', 'enlace'], fraude: ['estafa'], universidad: ['estudiantiles', 'prestamos'], prestamo: ['prestamos'], jubilacion: ['roth', '401'], ahorro: ['ahorros', 'emergencia', 'interes'],
  grad: ['first', 'paycheck'], graduate: ['first', 'paycheck'], job: ['first', 'paycheck'], w4: ['withholding', 'first'], checkup: ['checkup'], health: ['checkup'], review: ['checkup'],
  savings: ['saving', 'emergency', 'interest'], retirement: ['401', 'roth'], ira: ['roth'], tax: ['tax', 'paycheck', 'refund'], refund: ['refund', 'tax'], irs: ['tax', 'refund'], w2: ['refund', 'tax'], reembolso: ['reembolso', 'impuestos'], impuestos: ['impuestos', 'reembolso'],
};

// Small words that never decide a search.
export const STOP = new Set(['de', 'la', 'el', 'los', 'las', 'mi', 'mis', 'un', 'una', 'y', 'o', 'que', 'en', 'para', 'por', 'con', 'como', 'cuanto', 'cuánto', 'es', 'a', 'an', 'and', 'the', 'my', 'me', 'i', 'we', 'our', 'us', 'to', 'of', 'for', 'in', 'on', 'is', 'it', 'can', 'do', 'how', 'what', 'with', 'or', 'should', 'much', 'am', 'be', 'from', 'about', 'get', 'want', 'need']);

export const norm = (s) => String(s || '').toLowerCase().normalize('NFD').replace(/[̀-ͯ]/g, '');
const words = (s) => norm(s).split(/[^a-z0-9%$]+/).filter(Boolean);

// Does any word in `list` start with `token`? (So "calc" finds "calculator".)
const hit = (list, token) => list.some((w) => w.startsWith(token));

/** Rank tools for a query. Tools matching every word come first; if none do, tools matching any word. */
export function search(index, query, limit = 12) {
  const tokens = words(query).filter((t) => !STOP.has(t) && (t.length > 1 || /\d/.test(t)));
  if (!tokens.length) return [];
  const scored = index.map((item) => {
    const title = words(item.t);
    const desc = words(item.d);
    const keys = words(item.k);
    const section = words(item.s);
    let score = 0;
    let matched = 0;
    for (const t of tokens) {
      let best = 0;
      for (const [i, a] of [t, ...(SYNONYMS[t] || [])].entries()) {
        const w = i ? 0.6 : 1; // a synonym counts a little less than the word typed
        best = Math.max(best, w * ((hit(title, a) ? 6 : 0) + (title[0]?.startsWith(a) ? 2 : 0) + (hit(desc, a) ? 3 : 0) + (hit(keys, a) ? 1 : 0) + (hit(section, a) ? 1 : 0)));
      }
      if (best) { matched++; score += best; }
    }
    return { item, score, matched };
  }).filter((r) => r.matched);
  const full = scored.filter((r) => r.matched === tokens.length);
  const pool = full.length ? full : scored;
  return pool.sort((a, b) => b.matched - a.matched || b.score - a.score || a.item.t.localeCompare(b.item.t)).slice(0, limit).map((r) => ({ ...r.item, score: r.score }));
}

if (typeof document !== 'undefined') {
  const box = document.querySelector('#q');
  const out = document.querySelector('#search-results');
  const count = document.querySelector('#search-count');
  const hideWhileSearching = [...document.querySelectorAll('main > section, .jump')];
  let index = null;
  const es = document.documentElement.lang.startsWith('es');
  const esc = (s) => String(s).replace(/[&<>"]/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' })[c]);
  const load = () => (index ||= fetch('search-index.json').then((r) => r.json()).catch(() => []));

  async function run() {
    const q = box.value.trim();
    if (!q) {
      out.hidden = true; out.innerHTML = ''; count.textContent = '';
      for (const el of hideWhileSearching) el.hidden = false;
      return;
    }
    const list = search(await load(), q);
    for (const el of hideWhileSearching) el.hidden = true;
    out.hidden = false;
    out.innerHTML = list.length
      ? list.map((r) => `<a class="card" href="${esc(r.u)}"><span class="tag section-tag">${esc(r.s)}</span><h3>${esc(r.t)}</h3><p>${esc(r.d)}</p></a>`).join('')
      : `<p class="none">${es ? `Ninguna herramienta coincide con "${esc(q)}". Prueba una palabra más simple, como "deuda", "ahorro" o "estafa".` : `No tools match "${esc(q)}". Try a simpler word, like "budget", "loan" or "scam".`}</p>`;
    count.textContent = es
      ? (list.length ? `${list.length} herramienta${list.length === 1 ? '' : 's'} encontrada${list.length === 1 ? '' : 's'}` : 'No se encontraron herramientas')
      : (list.length ? `${list.length} tool${list.length === 1 ? '' : 's'} found` : 'No tools found');
  }

  box?.addEventListener('focus', load, { once: true });
  box?.addEventListener('input', run);
  box?.addEventListener('keydown', (e) => { if (e.key === 'Escape') { box.value = ''; run(); } });
  document.querySelector('#search-form')?.addEventListener('submit', (e) => { e.preventDefault(); out.querySelector('a')?.focus(); });
  // ?q=... opens with a search (handy for links from the main site).
  const q0 = new URLSearchParams(location.search).get('q');
  if (box && q0) { box.value = q0; run(); }
}
