// Builds the comparison pages from tools/compare-data.mjs into compare/, the about/ page, and sitemap.xml.
//   node tools/build-pages.mjs           write the files (every page, whatever its date)
//   node tools/build-pages.mjs --check   exit 1 if the committed files are out of date (used by the tests)
//   node tools/build-pages.mjs --release [--date YYYY-MM-DD]
//                                        deploy build: drop pages not yet due (tools/schedule.mjs)
// The output is plain static HTML, so the site still deploys with no build step.
import { readFile, writeFile, mkdir, rm, readdir } from 'node:fs/promises';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';
import config from '../config.js';
import { pages } from './compare-data.mjs';
import { releases, released } from './schedule.mjs';

const root = join(dirname(fileURLToPath(import.meta.url)), '..');
const SITE = config.siteUrl.replace(/\/$/, '');
const esc = (s) => String(s).replace(/[&<>"]/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]));
const json = (o) => JSON.stringify(o).replace(/</g, '\\u003c');
const AUTHOR = (config.author && config.author.name || '').trim();
const longDate = (d) => new Date(d + 'T12:00:00Z').toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric', timeZone: 'UTC' });
const author = () => (AUTHOR
  ? { '@type': 'Person', name: AUTHOR, url: `${SITE}/about/` }
  : { '@type': 'Organization', name: config.brand, url: `${SITE}/about/` });

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
<p>1099 Money · get paid, keep more, never fear April. Written with help from AI tools. <a href="${pre}about/">About these pages</a> · <a href="${pre}how-we-make-money/">How we make money</a></p>
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
<p class="byline">By <a href="${pre}about/">${esc(AUTHOR || config.brand)}</a> · Published <time datetime="${pg.published}">${longDate(pg.published)}</time></p>
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
    { '@context': 'https://schema.org', '@type': 'Article', headline: pg.h1, description: pg.description, url: `${SITE}/${path}`,
      datePublished: pg.published, dateModified: pg.updated || pg.published, author: author(),
      publisher: { '@type': 'Organization', name: config.brand, url: `${SITE}/` } },
    { '@context': 'https://schema.org', '@type': 'FAQPage', mainEntity: pg.faq.map(([q, a]) => ({ '@type': 'Question', name: q, acceptedAnswer: { '@type': 'Answer', text: a } })) },
  ];
  return [path, shell({ title: pg.title, description: pg.description, path, pre, body, ld, current: 'compare/' })];
}

function hubPage(list = pages) {
  const pre = '../';
  const cards = list.map((pg) => `<a class="card" href="${pg.slug}/"><h2>${esc(pg.h1)}</h2><p>${esc(pg.description)}</p></a>`).join('\n');
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

function aboutPage() {
  const pre = '../';
  const editor = AUTHOR
    ? `<h2>Who writes it</h2>\n<p><b>${esc(AUTHOR)}</b>${config.author.bio ? `: ${esc(config.author.bio)}` : ''}</p>`
    : '';
  const body = `<h1>About 1099 Money</h1>
<p class="lede">Free tools and plain-English guides on taxes and money for US freelancers, 1099 workers and gig drivers.</p>
<section class="prose">
${editor}
<h2>How these pages are made</h2>
<p>Pages are drafted with help from AI tools. The tax figures come from IRS, SSA and healthcare.gov publications, and each page names its sources or the form it relies on. A person decides what gets published and when, and each comparison page shows the date it went up. Figures are for the 2026 tax year and are re-checked each January.</p>
<p>The calculators run entirely in your browser. Nothing you type is sent anywhere.</p>
<h2>How the site makes money</h2>
<p>Some links on the comparison pages are affiliate links, labeled on the page: we may earn a commission at no cost to you. We also sell our own spreadsheets and templates. Neither changes which tools we pick or the order they're in, and every comparison page says how its picks were made. The full list is on <a href="${pre}how-we-make-money/">How we make money</a>.</p>
<h2>What this isn't</h2>
<p>This is educational content, not tax, legal or financial advice. For your own situation, check irs.gov or talk to a CPA or enrolled agent.</p>
</section>`;
  const ld = [breadcrumbs([['1099 Money', ''], ['About', 'about/']]),
    { '@context': 'https://schema.org', '@type': 'AboutPage', name: 'About 1099 Money', url: `${SITE}/about/`, publisher: { '@type': 'Organization', name: config.brand, url: `${SITE}/` } }];
  return ['about/', shell({ title: 'About 1099 Money: How These Pages Are Made', description: 'What 1099 Money is, how its tax pages and calculators are made and checked, and how the site makes money.', path: 'about/', pre, body, ld, current: 'about/' })];
}

// "How we make money": built from config.js, so it only lists products that are on sale, affiliate partners
// whose links are live, and sponsors that exist. Re-run the build after changing config.js.
// research/scouting/faceless-teardown.md (PR #2), change 7.
const isLive = (url) => typeof url === 'string' && /^https?:\/\//.test(url) && !url.includes('REPLACE_ME');
const PARTNER_NAMES = Object.fromEntries(pages.flatMap((p) => p.providers)
  .filter((x) => x && x.aff).map((x) => [x.aff, x.name]));

export function moneyFacts(cfg = config) {
  const products = [cfg.product, ...(cfg.upsells || [])].filter(Boolean)
    .map((x) => ({ name: x.name, price: x.price, onSale: isLive(x.url) }));
  const partners = [...new Set(Object.entries(cfg.affiliates || {})
    .filter(([, v]) => isLive(v.url)).map(([k]) => PARTNER_NAMES[k] || k))].sort();
  const sponsors = (cfg.disclosures && cfg.disclosures.sponsors) || [];
  return { products, partners, sponsors, analytics: Boolean(cfg.analytics && cfg.analytics.plausibleDomain) };
}

function moneyPage() {
  const pre = '../';
  const f = moneyFacts();
  const li = (xs) => `<ul>\n${xs.map((x) => `<li>${x}</li>`).join('\n')}\n</ul>`;
  const products = li(f.products.map((x) => `<b>${esc(x.name)}</b>, ${esc(x.price)}${x.onSale ? '' : ' (not on sale yet)'}`));
  const partners = f.partners.length
    ? `<p>We currently have affiliate partnerships with:</p>\n${li(f.partners.map(esc))}\n<p>If you sign up through one of their buttons on a comparison page, we may earn a commission, at no extra cost to you. Those buttons are labeled on the page.</p>`
    : '<p>We have no active affiliate partnerships right now. Buttons on the comparison pages go straight to each provider\'s own site, and we earn nothing from them. When that changes, partners will be listed here and every affiliate button will be labeled.</p>';
  const sponsors = f.sponsors.length
    ? `<p>Current sponsors:</p>\n${li(f.sponsors.map(esc))}\n<p>Sponsored videos and posts are labeled as paid promotion on the platform and in the description.</p>`
    : '<p>None. If that changes, sponsors will be listed here, and sponsored videos and posts will be labeled as paid promotion.</p>';
  const body = `<h1>How 1099 Money makes money</h1>
<p class="lede">Everything on this site is free to use. Here's exactly how it pays for itself, and what we don't do for money.</p>
<section class="prose">
<h2>1. Our own products</h2>
<p>We sell spreadsheets, templates and guides that do the same math as the free tools in more depth. This is the main way the site is meant to earn.</p>
${products}
<p>The free calculators never need a purchase, and they aren't cut down to push you toward one.</p>
<h2>2. Affiliate links</h2>
${partners}
<p>An affiliate payment doesn't change which tools a comparison page includes or the order they're in. Each comparison page says how its picks were made, and some picks can never pay us, like HealthCare.gov and a local CPA or enrolled agent.</p>
<h2>3. Sponsors</h2>
${sponsors}
<h2>What we don't do</h2>
<ul>
<li>We don't take money for a review, a better position in a comparison, or a mention in a guide.</li>
<li>We don't give investment or trading tips, and we don't sell courses that promise income.</li>
<li>We don't sell or rent email addresses. Emails come from us, about taxes and money, and every one has a one-click unsubscribe.</li>
<li>We never ask for your Social Security number, bank details or tax documents.</li>
<li>Calculator inputs stay in your browser. The one exception: if you ask the deduction finder to email you your list, the items you ticked are sent with your email address.</li>
</ul>
<h2>How AI is used</h2>
<p>Pages, posts and videos are drafted with help from AI tools, then checked against IRS, SSA and healthcare.gov sources before they're published. Video narration may use an AI voice. A person decides what goes up. See <a href="${pre}about/">About these pages</a> for how pages are made and checked.</p>
<h2>What we collect</h2>
<p>${f.analytics ? 'We count visits with Plausible, which uses no cookies and doesn\'t track you across sites. ' : ''}If you sign up for the free calendar or the deduction list, we keep your email address (and, for the list, the items you ticked) to send it and the reminders. That's all.</p>
<p class="tiny">This page is built from the same settings file as the rest of the site, so the lists above update when a product goes on sale or a partnership starts.</p>
</section>`;
  const ld = [breadcrumbs([['1099 Money', ''], ['How we make money', 'how-we-make-money/']])];
  return ['how-we-make-money/', shell({ title: 'How 1099 Money Makes Money: Products, Affiliates, Sponsors', description: 'Exactly how 1099 Money pays for its free tax tools: our own products, labeled affiliate links, sponsors (none yet), and what we never do for money.', path: 'how-we-make-money/', pre, body, ld, current: 'how-we-make-money/' })];
}

const ALL_PATHS = ['', 'q4/', 'rate-calculator/', 'deduction-finder/', 'mileage/', 'free/', 'compare/', ...pages.map((p) => `compare/${p.slug}/`), 'about/', 'how-we-make-money/'];

// today: null builds every page (the committed files); a YYYY-MM-DD builds only what's due by then.
export function build(today = null) {
  const due = (path) => !today || released(path, today);
  const live = pages.filter((p) => due(`compare/${p.slug}/`));
  const out = [hubPage(live), ...live.map(comparePage), aboutPage(), moneyPage()].map(([p, html]) => [`${p}index.html`, html]);
  out.push(['sitemap.xml', sitemap(ALL_PATHS.filter(due))]);
  return out;
}

// Paths whose release date is after `today`.
export const notYet = (today) => Object.keys(releases).filter((p) => !released(p, today));

if (process.argv[1] === fileURLToPath(import.meta.url)) {
  const check = process.argv.includes('--check');
  const release = process.argv.includes('--release');
  const di = process.argv.indexOf('--date');
  const today = release ? (di > 0 ? process.argv[di + 1] : new Date().toISOString().slice(0, 10)) : null;
  let stale = [];
  for (const [rel, html] of build(today)) {
    const file = join(root, rel);
    if (check) {
      const cur = await readFile(file, 'utf8').catch(() => '');
      if (cur !== html) stale.push(rel);
    } else {
      await mkdir(dirname(file), { recursive: true });
      await writeFile(file, html);
    }
  }
  if (release) {
    // Deploy build only: remove pages that aren't due, and the nav links pointing at them.
    const hidden = notYet(today);
    for (const p of hidden) await rm(join(root, p), { recursive: true, force: true });
    const htmlFiles = async (dir) => (await readdir(dir, { withFileTypes: true, recursive: true }))
      .filter((d) => d.isFile() && d.name.endsWith('.html')).map((d) => join(d.parentPath || d.path, d.name));
    for (const f of await htmlFiles(root)) {
      let html = await readFile(f, 'utf8');
      for (const p of hidden) html = html.replace(new RegExp(`<a href="(?:\\.\\./)*${p.replace(/[/.-]/g, '\\$&')}"[^>]*>([^<]*)</a>`, 'g'), '');
      await writeFile(f, html);
    }
    console.log(`release ${today}: hid ${hidden.length ? hidden.join(', ') : 'nothing'}`);
  }
  if (check && stale.length) { console.error('Out of date, run node tools/build-pages.mjs:', stale.join(', ')); process.exit(1); }
  console.log(check ? 'pages up to date' : `wrote ${build(today).length} files`);
}
