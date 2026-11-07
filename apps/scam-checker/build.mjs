// Builds the scam guide pages (/scams/ and /scams/<slug>/), sitemap.xml and robots.txt.
// Run: node build.mjs (no dependencies). Output is committed so the folder deploys as-is.
import { writeFileSync, mkdirSync } from 'node:fs';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';
import { scams } from './scams.mjs';
import config from './config.js';

const root = dirname(fileURLToPath(import.meta.url));
const base = config.siteUrl.replace(/\/$/, '');
const esc = (s) => String(s).replace(/[&<>"]/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' })[c]);

const IF_CLICKED = [
  ['You only opened the message', 'You\'re fine. Delete it and block the sender.'],
  ['You clicked the link but typed nothing', 'Close the page. Don\'t download anything it offers. Keep your phone updated.'],
  ['You typed a password', 'Change that password now, plus anywhere you reused it, and turn on two-factor login.'],
  ['You entered card or bank details', 'Call your bank or card issuer using the number on your card and ask them to block it.'],
  ['You paid by gift card, wire, Zelle or crypto', 'Contact the company you paid through right away (gift card company, bank, or exchange) and report it. Speed matters.'],
  ['You gave your Social Security number', 'Freeze your credit at Equifax, Experian and TransUnion (free) and see IdentityTheft.gov for a recovery plan.'],
];

const signup = `
<section class="card signup-box">
  <h2>Get the weekly scam alert</h2>
  <p class="signup-pitch"></p>
  <form class="signup" name="${esc(config.email.formName)}" method="POST" data-netlify="true" netlify-honeypot="website">
    <input type="hidden" name="form-name" value="${esc(config.email.formName)}">
    <p class="hp"><label>Leave this empty <input name="website" tabindex="-1" autocomplete="off"></label></p>
    <label class="sr" for="signup-email">Email</label>
    <input id="signup-email" type="email" name="email" placeholder="you@example.com" required autocomplete="email">
    <button class="btn">Sign me up</button>
  </form>
  <p class="tiny">Unsubscribe in one click. We never sell your address.</p>
</section>`;

function layout({ path, title, description, body, jsonld = [], depth }) {
  const up = '../'.repeat(depth);
  return `<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>${esc(title)} | ${esc(config.brand)}</title>
<meta name="description" content="${esc(description)}">
<link rel="canonical" href="${base}/${path}">
<meta property="og:title" content="${esc(title)}">
<meta property="og:description" content="${esc(description)}">
<meta property="og:type" content="article">
<meta property="og:url" content="${base}/${path}">
<meta name="theme-color" content="#0d1b2a">
<link rel="stylesheet" href="${up}style.css">
${jsonld.map((j) => `<script type="application/ld+json">${JSON.stringify(j)}</script>`).join('\n')}
</head>
<body data-root="${up}">
<header class="top"><a class="logo" href="${up}"><span class="mark" aria-hidden="true"><svg viewBox="0 0 24 24" width="18" height="18"><path fill="currentColor" d="M12 2 4 5v6c0 5 3.4 9.7 8 11 4.6-1.3 8-6 8-11V5l-8-3Zm-1.2 14.2-3.5-3.5 1.4-1.4 2.1 2.1 4.9-4.9 1.4 1.4-6.3 6.3Z"/></svg></span> ${esc(config.brand)}</a></header>
<main>
${body}
</main>
<footer>
<p>Scam Shield is an educational resource, not legal or financial advice. Some links are affiliate links: we may earn a commission at no cost to you.</p>
<p><a href="${up}">Scam checker</a> · <a href="${up}scams/">All scam guides</a></p>
</footer>
<script type="module" src="${up}guide.js"></script>
</body>
</html>
`;
}

function guide(s) {
  const others = scams.filter((o) => o.slug !== s.slug).slice(0, 5);
  const faq = [
    [`Is the ${s.h1.replace(/^Is this |\?$|^Someone asked for my |^Did I really win\? /g, '').replace(/ a scam$/, '')} real?`, `${s.real} ${s.check}`],
    ['What should I do if I already clicked?', 'It depends on what you shared. If you typed a password, change it and turn on two-factor login. If you shared card or bank details, call your bank using the number on your card. If you paid by gift card, wire or crypto, contact that company right away.'],
    ['Where do I report it?', 'Forward scam texts to 7726 (SPAM), then report at ReportFraud.ftc.gov. If you lost money, also file at IC3.gov and call your bank.'],
  ];
  const body = `
<p class="crumb"><a href="../">Scam guides</a></p>
<h1>${esc(s.h1)}</h1>
<p class="lede">${esc(s.description)}</p>

<section class="card">
  <h2>What it looks like</h2>
  <blockquote class="sample">${esc(s.example).replace(/\n/g, '<br>')}</blockquote>
  <p class="tiny">An illustration based on reported messages. Names, amounts and links are made up.</p>
  <p><a class="btn small" href="../../#m=${encodeURIComponent(s.example)}">See how the checker scores this example</a></p>
</section>

<section class="card">
  <h2>Got one? Check it now</h2>
  <form id="guide-check">
    <label for="guide-msg">Paste your message</label>
    <textarea id="guide-msg" rows="5" maxlength="4000" placeholder="Paste the whole message, including any links"></textarea>
    <div class="row"><button class="btn" type="submit">Check it</button><span class="tiny">Runs in your browser. Nothing is uploaded.</span></div>
  </form>
</section>

<h2>Signs it's a scam</h2>
<ul class="flags">${s.signs.map((x) => `<li>${esc(x)}</li>`).join('')}</ul>

<h2>What the real one does</h2>
<p>${esc(s.real)}</p>
<h2>How to check safely</h2>
<p>${esc(s.check)}</p>

<h2>If you already clicked or replied</h2>
<table class="steps"><tbody>${IF_CLICKED.map(([a, b]) => `<tr><th>${esc(a)}</th><td>${esc(b)}</td></tr>`).join('')}</tbody></table>

<h2>Report it</h2>
<p>Forward scam texts to <b>7726</b> (SPAM). Report fraud at <a href="https://reportfraud.ftc.gov/" rel="noopener">ReportFraud.ftc.gov</a>, and internet crime or money lost at <a href="https://www.ic3.gov/" rel="noopener">IC3.gov</a>.</p>

<section id="offers" class="card" hidden></section>
${signup}

<h2>Sources</h2>
<ul class="sources">${s.sources.map(([t, u]) => `<li><a href="${esc(u)}" rel="noopener">${esc(t)}</a></li>`).join('')}</ul>

<h2>Other scams going around</h2>
<ul class="related">${others.map((o) => `<li><a href="../${o.slug}/">${esc(o.h1)}</a></li>`).join('')}</ul>`;
  const jsonld = [
    { '@context': 'https://schema.org', '@type': 'Article', headline: s.title, description: s.description, mainEntityOfPage: `${base}/scams/${s.slug}/`, publisher: { '@type': 'Organization', name: config.brand } },
    { '@context': 'https://schema.org', '@type': 'FAQPage', mainEntity: faq.map(([q, a]) => ({ '@type': 'Question', name: q, acceptedAnswer: { '@type': 'Answer', text: a } })) },
    { '@context': 'https://schema.org', '@type': 'BreadcrumbList', itemListElement: [{ '@type': 'ListItem', position: 1, name: 'Scam guides', item: `${base}/scams/` }, { '@type': 'ListItem', position: 2, name: s.h1, item: `${base}/scams/${s.slug}/` }] },
  ];
  return layout({ path: `scams/${s.slug}/`, title: s.title, description: s.description, body, jsonld, depth: 2 });
}

function index() {
  const body = `
<h1>Scams going around right now</h1>
<p class="lede">Plain-English guides to the texts, emails and calls people ask us about most: what they look like, how to check, and what to do if you clicked.</p>
<p><a class="btn" href="../">Paste a message into the checker</a></p>
<div class="tiles">${scams.map((s) => `<a class="card tile" href="./${s.slug}/"><h2>${esc(s.h1)}</h2><p>${esc(s.short)}</p></a>`).join('\n')}</div>
${signup}`;
  return layout({ path: 'scams/', title: 'Common Scam Texts, Emails and Calls', description: 'Guides to the most common scam texts, emails and calls: USPS, unpaid tolls, IRS, Amazon, bank fraud alerts, job offers and more.', body, depth: 1 });
}

const write = (rel, text) => { const f = join(root, rel); mkdirSync(dirname(f), { recursive: true }); writeFileSync(f, text); };
write('scams/index.html', index());
for (const s of scams) write(`scams/${s.slug}/index.html`, guide(s));
const urls = ['', 'scams/', ...scams.map((s) => `scams/${s.slug}/`)];
write('sitemap.xml', `<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n${urls.map((u) => `  <url><loc>${base}/${u}</loc></url>`).join('\n')}\n</urlset>\n`);
write('robots.txt', `User-agent: *\nAllow: /\nSitemap: ${base}/sitemap.xml\n`);
console.log(`Built ${scams.length + 1} scam guide pages`);
