// Builds the comparison pages from tools/compare-data.mjs into compare/ and rewrites sitemap.xml.
//   node tools/build-pages.mjs           write the files
//   node tools/build-pages.mjs --check   exit 1 if the committed files are out of date (used by the tests)
// The output is plain static HTML, so the site still deploys with no build step.
import { readFile, writeFile, mkdir } from 'node:fs/promises';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';
import config from '../config.js';
import { pages } from './compare-data.mjs';

const root = join(dirname(fileURLToPath(import.meta.url)), '..');
const SITE = config.siteUrl.replace(/\/$/, '');
const esc = (s) => String(s).replace(/[&<>"]/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]));
const json = (o) => JSON.stringify(o).replace(/</g, '\\u003c');

function shell({ title, description, path, pre, body, ld, current }) {
  const url = `${SITE}/${path}`;
  const nav = [['', 'Calculator'], ['mileage/', 'Driver mileage'], ['compare/', 'Compare tools'], ['free/', 'Free calendar']]
    .map(([p, l]) => `<a href="${pre}${p || ''}"${p === current ? ' aria-current="page"' : ''}>${l}</a>`).join('');
  return `<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>${esc(title)} | 1099 Money</title>
<meta name="description" content="${esc(description)}">
<link rel="canonical" href="${url}">
<meta property="og:title" content="${esc(title)}">
<meta property="og:description" content="${esc(description)}">
<meta property="og:type" content="article">
<meta property="og:url" content="${url}">
<meta name="twitter:card" content="summary">
<meta name="theme-color" content="#14213d">
<link rel="stylesheet" href="${pre}style.css">
${ld.map((o) => `<script type="application/ld+json">${json(o)}</script>`).join('\n')}
</head>
<body>
<header class="top"><a class="logo" href="${pre || './'}"><span class="mark">1M</span> <span>1099 Money</span></a>
<nav class="nav">${nav}</nav></header>
<main>
${body}
</main>
<footer>
<p>Educational content, not tax, legal or financial advice. Features and prices change: check each provider's site before you sign up. Picks are ours; some links are affiliate links, and we may earn a commission at no cost to you. That never changes the order.</p>
<p>1099 Money · get paid, keep more, never fear April. Written with help from AI tools.</p>
</footer>
<script type="module">
import config from '${pre}config.js';
import { setupSite, live } from '${pre}site.js';
import { setupSignup } from '${pre}signup.js';
const p = config.product, box = document.getElementById('our-tool');
if (box && live(p.url)) {
  box.innerHTML = '<h2></h2><p></p><a class="btn"></a>';
  box.querySelector('h2').textContent = p.name + ' · ' + p.price;
  box.querySelector('p').textContent = p.pitch;
  const a = box.querySelector('a'); a.href = p.url; a.textContent = 'Get the tracker'; a.rel = 'noopener';
  box.hidden = false;
}
setupSignup();
setupSite();
</script>
</body>
</html>
`;
}

const breadcrumbs = (items) => ({
  '@context': 'https://schema.org', '@type': 'BreadcrumbList',
  itemListElement: items.map(([name, path], i) => ({ '@type': 'ListItem', position: i + 1, name, item: `${SITE}/${path}` })),
});

const signup = (pre) => `<section class="card signup-box">
  <h2>Free: the 2027 Freelancer Tax Calendar</h2>
  <p class="signup-pitch"></p>
  <form class="signup" name="tax-calendar" method="POST" action="${pre}free/thanks/" data-thanks="${pre}free/thanks/" data-netlify="true" netlify-honeypot="website">
    <input type="hidden" name="form-name" value="tax-calendar"><input type="hidden" name="source" value="compare">
    <p class="hp"><label>Leave this empty <input name="website" tabindex="-1" autocomplete="off"></label></p>
    <label class="sr" for="signup-email">Email</label>
    <input id="signup-email" type="email" name="email" placeholder="you@example.com" required autocomplete="email">
    <button class="btn">Send me the calendar</button>
  </form>
  <p class="tiny">Deadline reminders plus one short email a week. Unsubscribe in one click.</p>
</section>`;

function comparePage(pg) {
  const pre = '../../';
  const path = `compare/${pg.slug}/`;
  const picks = pg.providers.map((p) => `<article class="card pick" id="${p.key}">
  <h3>${esc(p.name)}<span class="tag">Affiliate link</span></h3>
  <p class="best">Best for: ${esc(p.best)}</p>
  <p class="lbl">What stands out</p><ul>${p.good.map((g) => `<li>${esc(g)}</li>`).join('')}</ul>
  <p class="lbl">Watch out for</p><ul class="minus">${p.watch.map((g) => `<li>${esc(g)}</li>`).join('')}</ul>
  <a class="btn alt" href="${p.site}" ${p.aff ? `data-aff="${p.aff}" data-site="${p.site}" ` : ''}rel="noopener" target="_blank">${esc(p.cta || 'Visit ' + p.name.replace(/ \(.*\)$/, ''))}</a>
</article>`).join('\n');
  const quick = pg.quick.map(([who, pick]) => `<tr><td>${esc(who)}</td><td><b>${esc(pick)}</b></td></tr>`).join('');
  const sections = pg.sections.map(([h, html]) => `<h2>${esc(h)}</h2>\n${html}`).join('\n');
  const faq = pg.faq.map(([q, a]) => `<h3>${esc(q)}</h3><p>${esc(a)}</p>`).join('\n');
  const body = `<p class="crumbs"><a href="${pre}">1099 Money</a> › <a href="../">Compare tools</a> › ${esc(pg.nav)}</p>
<h1>${esc(pg.h1)}</h1>
<p class="lede">${esc(pg.lede)}</p>
<p class="disclose">How we picked: ${esc(pg.picked)} <span class="aff-note" hidden>Buttons marked "Affiliate link" may earn us a commission at no cost to you.</span></p>

<section class="card"><h2 style="margin-top:0">Quick picks</h2>
<table class="quick"><tr><th>If you…</th><th>Look at</th></tr>${quick}</table></section>

<section class="picks">
${picks}
</section>

<section class="prose">
${sections}
</section>

<section class="card" id="our-tool" hidden></section>
${signup(pre)}

<section class="faq"><h2>Questions</h2>
${faq}
<p>Next: work out what you owe this quarter with the free <a href="${pre}">quarterly tax calculator</a>, or see the <a href="../">other comparisons</a>.</p>
</section>`;
  const ld = [
    breadcrumbs([['1099 Money', ''], ['Compare tools', 'compare/'], [pg.nav, path]]),
    { '@context': 'https://schema.org', '@type': 'FAQPage', mainEntity: pg.faq.map(([q, a]) => ({ '@type': 'Question', name: q, acceptedAnswer: { '@type': 'Answer', text: a } })) },
  ];
  return [path, shell({ title: pg.title, description: pg.description, path, pre, body, ld, current: 'compare/' })];
}

function hubPage() {
  const pre = '../';
  const cards = pages.map((pg) => `<a class="card" href="${pg.slug}/"><h2>${esc(pg.h1)}</h2><p>${esc(pg.description)}</p></a>`).join('\n');
  const body = `<h1>Tools for freelancers, compared</h1>
<p class="lede">Honest comparisons of the banking, tax, invoicing, S corp and health insurance options US freelancers actually use, with the tax angle on each.</p>
<p class="disclose">Picks are made on fit, not payout. Some links on these pages are affiliate links: we may earn a commission at no cost to you, and every page says how its picks were made.</p>
<section class="hub">
${cards}
</section>
${signup(pre)}
<section class="card" id="our-tool" hidden></section>`;
  return ['compare/', shell({ title: 'Freelancer Tools Compared: Banking, Tax Software, Invoicing, S Corp, Health Insurance', description: 'Side-by-side comparisons of the tools US freelancers use for banking, taxes, invoicing, S corps and health insurance.', path: 'compare/', pre, body, ld: [breadcrumbs([['1099 Money', ''], ['Compare tools', 'compare/']])], current: 'compare/' })];
}

function sitemap(paths) {
  return `<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
${paths.map((p) => `  <url><loc>${SITE}/${p}</loc></url>`).join('\n')}
</urlset>
`;
}

export function build() {
  const out = [hubPage(), ...pages.map(comparePage)].map(([p, html]) => [`${p}index.html`, html]);
  out.push(['sitemap.xml', sitemap(['', 'mileage/', 'free/', 'compare/', ...pages.map((p) => `compare/${p.slug}/`)])]);
  return out;
}

if (process.argv[1] === fileURLToPath(import.meta.url)) {
  const check = process.argv.includes('--check');
  let stale = [];
  for (const [rel, html] of build()) {
    const file = join(root, rel);
    if (check) {
      const cur = await readFile(file, 'utf8').catch(() => '');
      if (cur !== html) stale.push(rel);
    } else {
      await mkdir(dirname(file), { recursive: true });
      await writeFile(file, html);
    }
  }
  if (check && stale.length) { console.error('Out of date, run node tools/build-pages.mjs:', stale.join(', ')); process.exit(1); }
  console.log(check ? 'pages up to date' : `wrote ${build().length} files`);
}
