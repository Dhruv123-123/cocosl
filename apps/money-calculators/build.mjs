// Writes one static HTML page per calculator plus the index, sitemap and robots.txt.
// Run: node build.mjs   (no dependencies). Output is committed so the folder deploys as-is.
import { writeFileSync, mkdirSync } from 'node:fs';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';
import { pages } from './pages.mjs';
import config from './config.js';

const root = dirname(fileURLToPath(import.meta.url));
const base = config.calculatorsUrl.replace(/\/$/, '');
const esc = (s) => String(s).replace(/[&<>"]/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' })[c]);

const signup = `
<section class="card signup-box">
  <h2>Free: ${esc(config.email.leadMagnet)}</h2>
  <p class="signup-pitch"></p>
  <form class="signup" name="${esc(config.email.formName)}" method="POST" data-netlify="true" netlify-honeypot="website">
    <input type="hidden" name="form-name" value="${esc(config.email.formName)}">
    <p class="hp"><label>Leave this empty <input name="website" tabindex="-1" autocomplete="off"></label></p>
    <label class="sr" for="signup-email">Email</label>
    <input id="signup-email" type="email" name="email" placeholder="you@example.com" required autocomplete="email">
    <button class="btn">Send it to me</button>
  </form>
  <p class="tiny">One useful email a week. Unsubscribe in one click.</p>
</section>`;

function layout({ slug, title, description, body, jsonld = [] }) {
  const url = slug ? `${base}/${slug}/` : `${base}/`;
  const prefix = slug ? '../' : './';
  return `<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>${esc(title)} | ${esc(config.brand)}</title>
<meta name="description" content="${esc(description)}">
<link rel="canonical" href="${url}">
<meta property="og:title" content="${esc(title)}">
<meta property="og:description" content="${esc(description)}">
<meta property="og:type" content="website">
<meta property="og:url" content="${url}">
<meta name="twitter:card" content="summary">
<meta name="theme-color" content="#0b1d13">
<link rel="stylesheet" href="${prefix}style.css">
${jsonld.map((j) => `<script type="application/ld+json">${JSON.stringify(j)}</script>`).join('\n')}
</head>
<body data-calc="${slug || ''}">
<header class="top"><a class="logo" href="${prefix}"><span class="mark">MS</span> <span data-brand>${esc(config.brand)}</span> calculators</a>
<a class="home" data-site href="${esc(config.siteUrl)}">Main site</a></header>
<main>
${body}
</main>
<footer>
<p>Educational tools, not financial, tax or investment advice. Results are estimates from the numbers you enter. Check current rules and rates with the official source before acting.</p>
<p>Your numbers stay in your browser; nothing you type into a calculator is sent anywhere. Some links are affiliate links.</p>
<p><a href="${prefix}">All calculators</a> · <a data-site href="${esc(config.siteUrl)}">${esc(config.brand)}</a></p>
</footer>
<script type="module" src="${prefix}app.js"></script>
</body>
</html>
`;
}

function calcPage(p) {
  const form = p.slug === 'debt-payoff'
    ? `<div id="debts"></div>
       <button type="button" id="add-debt" class="link">+ Add a debt</button>
       <label>Extra each month on top of minimums ($)<input name="extra" type="number" min="0" step="any" value="150"></label>`
    : '<div id="fields" class="grid"></div>';
  const faq = p.faq.map(([q, a]) => `<h3>${esc(q)}</h3><p>${esc(a)}</p>`).join('\n');
  const body = `
<h1>${esc(p.h1)}</h1>
<p class="lede">${esc(p.intro)}</p>
<div class="layout">
  <form id="calc-form" class="card" autocomplete="off">${form}
    <button type="button" id="share" class="link">Copy a link to these numbers</button>
  </form>
  <section class="card result" aria-live="polite"><div id="result"></div><div id="offers"></div></section>
</div>
${signup}
<section class="faq"><h2>Questions</h2>${faq}</section>
<p class="more"><a href="../">More calculators</a></p>`;
  const jsonld = [
    { '@context': 'https://schema.org', '@type': 'WebApplication', name: p.h1, url: `${base}/${p.slug}/`, applicationCategory: 'FinanceApplication', operatingSystem: 'Any', offers: { '@type': 'Offer', price: '0', priceCurrency: 'USD' } },
    { '@context': 'https://schema.org', '@type': 'FAQPage', mainEntity: p.faq.map(([q, a]) => ({ '@type': 'Question', name: q, acceptedAnswer: { '@type': 'Answer', text: a } })) },
  ];
  return layout({ slug: p.slug, title: p.title, description: p.description, body, jsonld });
}

function indexPage() {
  const cards = pages.map((p) => `<a class="card tile" href="./${p.slug}/"><h2>${esc(p.h1.replace(/ calculator.*$/i, '').replace(/^./, (c) => c.toUpperCase()))}</h2><p>${esc(p.description)}</p></a>`).join('\n');
  const body = `
<h1>Free money calculators</h1>
<p class="lede">Plain-English calculators for the money questions we get most. No sign-up, and your numbers never leave your browser.</p>
<div class="tiles">${cards}</div>
${signup}`;
  return layout({ slug: '', title: 'Free Money Calculators', description: 'Free debt payoff, compound interest, emergency fund, savings, credit card and Roth vs Traditional calculators.', body });
}

const write = (rel, text) => { const f = join(root, rel); mkdirSync(dirname(f), { recursive: true }); writeFileSync(f, text); };
write('index.html', indexPage());
for (const p of pages) write(`${p.slug}/index.html`, calcPage(p));
write('sitemap.xml', `<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n${['', ...pages.map((p) => p.slug + '/')].map((s) => `  <url><loc>${base}/${s}</loc></url>`).join('\n')}\n</urlset>\n`);
write('robots.txt', `User-agent: *\nAllow: /\nSitemap: ${base}/sitemap.xml\n`);
console.log(`Built ${pages.length + 1} pages`);
