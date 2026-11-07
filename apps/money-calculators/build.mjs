// Writes the calculator pages in English (/) and Spanish (/es/), plus sitemap.xml and robots.txt.
// Run: node build.mjs   (no dependencies). Output is committed so the folder deploys as-is.
import { writeFileSync, mkdirSync } from 'node:fs';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';
import { pages } from './pages.mjs';
import { pagesEs } from './pages-es.mjs';
import config from './config.js';

const root = dirname(fileURLToPath(import.meta.url));
const base = config.calculatorsUrl.replace(/\/$/, '');
const esc = (s) => String(s).replace(/[&<>"]/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' })[c]);

const L = {
  en: {
    dir: '', brandLine: `${esc(config.brand)} calculators`, mainSite: 'Main site', other: 'Español', otherDir: 'es/',
    signupTitle: `Free: ${esc(config.email.leadMagnet)}`, formName: config.email.formName, emailPh: 'you@example.com', send: 'Send it to me', emailLabel: 'Email',
    signupNote: 'One useful email a week. Unsubscribe in one click.', honeypot: 'Leave this empty',
    footer: ['Educational tools, not financial, tax or investment advice. Results are estimates from the numbers you enter. Check current rules and rates with the official source before acting.', 'Your numbers stay in your browser; nothing you type into a calculator is sent anywhere. Some links are affiliate links.'],
    all: 'All calculators', addDebt: '+ Add a debt', addFund: '+ Add a fund', feeMonthly: 'Added each month, you and employer ($)', feeYears: 'Years until retirement', feeReturn: 'Yearly return before fees (%)', extra: 'Extra each month on top of minimums ($)', share: 'Copy a link to these numbers', questions: 'Questions', more: 'More calculators',
    indexTitle: 'Free Money Calculators', indexH1: 'Free money calculators', indexLede: 'Plain-English calculators for the money questions we get most. No sign-up, and your numbers never leave your browser.',
    indexDesc: 'Free debt payoff, compound interest, emergency fund, savings, credit card and Roth vs Traditional calculators.',
  },
  es: {
    dir: 'es/', brandLine: 'Calculadoras de dinero', mainSite: 'Sitio principal', other: 'English', otherDir: '',
    signupTitle: esc(config.email.es.title), formName: config.email.es.formName, emailPh: 'tu@ejemplo.com', send: 'Suscribirme', emailLabel: 'Correo',
    signupNote: 'Un correo útil por semana. Cancela con un clic.', honeypot: 'Deja esto vacío',
    footer: ['Herramientas educativas, no asesoría financiera, fiscal ni de inversión. Los resultados son estimaciones con los números que ingresas. Revisa las reglas y tasas actuales con la fuente oficial antes de actuar.', 'Tus números se quedan en tu navegador; nada de lo que escribes se envía a ningún lado. Algunos enlaces son de afiliado.'],
    all: 'Todas las calculadoras', addDebt: '+ Agregar una deuda', addFund: '+ Agregar un fondo', feeMonthly: 'Aporte mensual, tuyo y de tu empleador ($)', feeYears: 'Años hasta tu jubilación', feeReturn: 'Rendimiento anual antes de comisiones (%)', extra: 'Extra cada mes además de los mínimos ($)', share: 'Copiar un enlace con estos números', questions: 'Preguntas', more: 'Más calculadoras',
    indexTitle: 'Calculadoras de dinero gratis', indexH1: 'Calculadoras de dinero gratis', indexLede: 'Calculadoras sencillas para las preguntas de dinero más comunes. Sin registro, y tus números nunca salen de tu navegador.',
    indexDesc: 'Calculadoras gratis para pagar deudas, interés compuesto, fondo de emergencia, ahorro, tarjeta de crédito y Roth vs Tradicional.',
  },
};

const signup = (t) => `
<section class="card signup-box">
  <h2>${t.signupTitle}</h2>
  <p class="signup-pitch"></p>
  <form class="signup" name="${esc(t.formName)}" method="POST" data-netlify="true" netlify-honeypot="website">
    <input type="hidden" name="form-name" value="${esc(t.formName)}">
    <p class="hp"><label>${t.honeypot} <input name="website" tabindex="-1" autocomplete="off"></label></p>
    <label class="sr" for="signup-email">${t.emailLabel}</label>
    <input id="signup-email" type="email" name="email" placeholder="${t.emailPh}" required autocomplete="email">
    <button class="btn">${t.send}</button>
  </form>
  <p class="tiny">${t.signupNote}</p>
</section>`;

function layout({ lang, slug, title, description, body, jsonld = [] }) {
  const t = L[lang];
  const depth = (t.dir ? 1 : 0) + (slug ? 1 : 0);
  const up = depth ? '../'.repeat(depth) : './';
  const rel = `${t.dir}${slug ? slug + '/' : ''}`;
  const alt = (l) => `${base}/${L[l].dir}${slug ? slug + '/' : ''}`;
  return `<!doctype html>
<html lang="${lang}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>${esc(title)} | ${lang === 'es' ? 'Calculadoras' : esc(config.brand)}</title>
<meta name="description" content="${esc(description)}">
<link rel="canonical" href="${base}/${rel}">
<link rel="alternate" hreflang="en" href="${alt('en')}">
<link rel="alternate" hreflang="es" href="${alt('es')}">
<meta property="og:title" content="${esc(title)}">
<meta property="og:description" content="${esc(description)}">
<meta property="og:type" content="website">
<meta property="og:url" content="${base}/${rel}">
<meta name="twitter:card" content="summary">
<meta name="theme-color" content="#0b1d13">
<link rel="stylesheet" href="${up}style.css">
${jsonld.map((j) => `<script type="application/ld+json">${JSON.stringify(j)}</script>`).join('\n')}
</head>
<body data-calc="${slug || ''}" data-root="${up}">
<header class="top"><a class="logo" href="${up}${t.dir}"><span class="mark">MS</span> <span>${t.brandLine}</span></a>
<nav class="nav"><a class="home" href="${up}${L[lang === 'es' ? 'en' : 'es'].dir}${slug ? slug + '/' : ''}" hreflang="${lang === 'es' ? 'en' : 'es'}">${t.other}</a>${lang === 'en' ? ` <a class="home" data-site href="${esc(config.siteUrl)}">${t.mainSite}</a>` : ''}</nav></header>
<main>
${body}
</main>
<footer>
${t.footer.map((p) => `<p>${p}</p>`).join('\n')}
<p><a href="${up}${t.dir}">${t.all}</a>${lang === 'en' ? ` · <a href="${up}embed/">Add these calculators to your site</a>` : ''}</p>
</footer>
<script type="module" src="${up}app.js"></script>
</body>
</html>
`;
}

function calcPage(p, lang) {
  const t = L[lang];
  const form = p.slug === 'debt-payoff'
    ? `<div id="debts"></div>
       <button type="button" id="add-debt" class="link">${t.addDebt}</button>
       <label>${t.extra}<input name="extra" type="number" min="0" step="any" value="150"></label>`
    : p.slug === '401k-fees'
      ? `<div id="funds"></div>
       <button type="button" id="add-fund" class="link">${t.addFund}</button>
       <div class="grid"><label>${t.feeMonthly}<input name="monthly" type="number" min="0" step="any" value="500"></label>
       <label>${t.feeYears}<input name="years" type="number" min="1" max="60" step="1" value="30"></label>
       <label>${t.feeReturn}<input name="annualReturn" type="number" min="0" max="15" step="any" value="7"></label></div>`
      : '<div id="fields" class="grid"></div>';
  const faq = p.faq.map(([q, a]) => `<h3>${esc(q)}</h3><p>${esc(a)}</p>`).join('\n');
  const body = `
<h1>${esc(p.h1)}</h1>
<p class="lede">${esc(p.intro)}</p>
<div class="layout">
  <form id="calc-form" class="card" autocomplete="off">${form}
    <button type="button" id="share" class="link">${t.share}</button>
  </form>
  <section class="card result" aria-live="polite"><div id="result"></div><div id="offers"></div></section>
</div>
${signup(t)}
<section class="faq"><h2>${t.questions}</h2>${faq}</section>
<p class="more"><a href="../">${t.more}</a></p>`;
  const url = `${base}/${t.dir}${p.slug}/`;
  const jsonld = [
    { '@context': 'https://schema.org', '@type': 'WebApplication', name: p.h1, url, inLanguage: lang, applicationCategory: 'FinanceApplication', operatingSystem: 'Any', offers: { '@type': 'Offer', price: '0', priceCurrency: 'USD' } },
    { '@context': 'https://schema.org', '@type': 'FAQPage', inLanguage: lang, mainEntity: p.faq.map(([q, a]) => ({ '@type': 'Question', name: q, acceptedAnswer: { '@type': 'Answer', text: a } })) },
  ];
  return layout({ lang, slug: p.slug, title: p.title, description: p.description, body, jsonld });
}

function indexPage(list, lang) {
  const t = L[lang];
  const name = (p) => p.tile || p.h1.replace(/ calculator.*$/i, '').replace(/^./, (c) => c.toUpperCase());
  const cards = list.map((p) => `<a class="card tile" href="./${p.slug}/"><h2>${esc(name(p))}</h2><p>${esc(p.description)}</p></a>`).join('\n');
  const body = `
<h1>${t.indexH1}</h1>
<p class="lede">${t.indexLede}</p>
<div class="tiles">${cards}</div>
${signup(t)}`;
  return layout({ lang, slug: '', title: t.indexTitle, description: t.indexDesc, body });
}

const thanks = `<!doctype html>
<html lang="es"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>¡Listo!</title><meta name="robots" content="noindex"><link rel="stylesheet" href="../../style.css"></head>
<body><main><h1>¡Listo!</h1><p class="lede">Tu primer correo llega esta semana. Si no lo ves, revisa Promociones o Spam.</p>
<p><a class="btn" href="../">Volver a las calculadoras</a></p></main></body></html>
`;

function embedPage() {
  const opts = pages.map((p) => `<option value="${p.slug}">${esc(p.h1)}</option>`).join('');
  const body = `
<h1>Add a free calculator to your site</h1>
<p class="lede">Bloggers, financial coaches, credit unions and schools can embed any of our calculators for free. It resizes itself, works on phones, sets no cookies, and keeps your readers on your page.</p>
<div class="layout">
  <form id="embed-form" class="card">
    <label>Calculator<select id="e-calc">${opts}</select></label>
    <label>Language<select id="e-lang"><option value="en">English</option><option value="es">Español</option></select></label>
    <label>Paste this where you want it
      <textarea id="e-code" rows="5" readonly></textarea></label>
    <button type="button" class="btn small" id="e-copy">Copy code</button>
    <p class="tiny">Free embeds show a small "Free calculator by ${esc(config.brand)}" link under the tool.</p>
  </form>
  <section class="card"><h2 style="margin-top:0">Preview</h2><div id="e-preview"></div></section>
</div>
<section class="card">
  <h2>For credit unions, banks and financial coaches</h2>
  <p>Want the calculators in your colours, without our link, and pointing to your own products (savings accounts, loans, coaching)? A white-label licence covers all six calculators in English and Spanish, with updates, for a flat monthly fee.</p>
  <ul><li>Your brand colours and logo</li><li>No credit link, your own call-to-action under every result</li><li>English and Spanish versions</li><li>Hosted for you, or as files for your web team</li></ul>
  <p><a class="btn" href="${esc(config.embed.licenceUrl)}">Ask about a licence</a></p>
</section>
<script type="module">
  const $ = (s) => document.querySelector(s);
  const base = new URL('../', location.href).href;
  function update() {
    const code = '<div class="mms-calc" data-calc="' + $('#e-calc').value + '" data-lang="' + $('#e-lang').value + '"></div>\\n<script src="' + base + 'embed.js" async><\\/script>';
    $('#e-code').value = code;
    $('#e-preview').innerHTML = '<div class="mms-calc" data-calc="' + $('#e-calc').value + '" data-lang="' + $('#e-lang').value + '"></div>';
    const s = document.createElement('script'); s.src = base + 'embed.js?' + Date.now(); document.body.append(s);
  }
  $('#e-calc').addEventListener('change', update); $('#e-lang').addEventListener('change', update);
  $('#e-copy').addEventListener('click', async () => { try { await navigator.clipboard.writeText($('#e-code').value); $('#e-copy').textContent = 'Copied'; } catch { $('#e-code').select(); } });
  update();
</script>`;
  return layout({ lang: 'en', slug: 'embed', title: 'Free Money Calculators for Your Website', description: 'Embed free debt payoff, compound interest, emergency fund, savings, credit card and Roth vs Traditional calculators on your site. White-label licences for credit unions and coaches.', body });
}

const write = (rel, text) => { const f = join(root, rel); mkdirSync(dirname(f), { recursive: true }); writeFileSync(f, text); };
if (pagesEs.map((p) => p.slug).join() !== pages.map((p) => p.slug).join()) throw new Error('pages-es.mjs must have the same slugs, in the same order, as pages.mjs');
write('index.html', indexPage(pages, 'en'));
write('es/index.html', indexPage(pagesEs, 'es'));
write('es/gracias/index.html', thanks);
write('embed/index.html', embedPage());
for (const p of pages) write(`${p.slug}/index.html`, calcPage(p, 'en'));
for (const p of pagesEs) write(`es/${p.slug}/index.html`, calcPage(p, 'es'));
const urls = ['', 'embed/', ...pages.map((p) => p.slug + '/'), 'es/', ...pagesEs.map((p) => `es/${p.slug}/`)];
write('sitemap.xml', `<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n${urls.map((s) => `  <url><loc>${base}/${s}</loc></url>`).join('\n')}\n</urlset>\n`);
write('robots.txt', `User-agent: *\nAllow: /\nSitemap: ${base}/sitemap.xml\n`);
console.log(`Built ${pages.length + pagesEs.length + 2} pages`);
