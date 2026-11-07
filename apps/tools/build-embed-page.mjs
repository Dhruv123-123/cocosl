// Writes embed.html: the "embed this tool" snippet maker for every tool that can sit on a partner's site,
// with the free and white-label plans. Calculators use money-calculators/embed.js (colours, theme, licence key);
// every other tool uses embed.js at the apps root, and the tool page itself runs lib/embed-page.js.
// shared/test/embed-tools.test.js checks each tool here exists and loads embed-page.js.
// Run from apps/: node tools/build-embed-page.mjs
import { readFileSync, writeFileSync } from 'node:fs';
import { join, dirname } from 'node:path';
import { fileURLToPath } from 'node:url';
import { pages } from '../money-calculators/pages.mjs';
import { pagesEs } from '../money-calculators/pages-es.mjs';
import config from '../money-calculators/config.js';

const root = join(dirname(fileURLToPath(import.meta.url)), '..');
const esc = (s) => String(s).replace(/[&<>"]/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' })[c]);

// Tools other than calculators. en/es: page path from apps/. h: the iframe height to start at.
export const TOOLS = [
  { id: 'scam-checker', group: 'Scam safety', name: 'Is this a scam? Message checker', en: 'scam-checker/', es: 'scam-checker/es/', h: 760 },
  { id: 'link-checker', group: 'Scam safety', name: 'Suspicious link checker', en: 'scam-checker/link/', es: 'scam-checker/es/enlace/', h: 640 },
  { id: 'vendor-check', group: 'Scam safety', name: 'Vendor payment check (for businesses)', en: 'scam-checker/vendor/', h: 900 },
  { id: 'paycheck-plan', group: 'Budgeting', name: 'Paycheck-to-budget planner (50/30/20 and zero-based)', en: 'budget/paycheck-plan.html', es: 'budget/plan-quincena.html', h: 1400 },
  { id: 'sinking-funds', group: 'Budgeting', name: 'Sinking funds planner', en: 'budget/sinking-funds.html', es: 'budget/fondos-ahorro.html', h: 1100 },
  { id: 'money-calendar', group: 'Budgeting', name: 'Money calendar download (tax dates, Black Friday, reset)', en: 'budget/money-calendar.html', es: 'budget/calendario-dinero.html', h: 1000 },
  { id: 'bill-calendar', group: 'Budgeting', name: 'Bill due date calendar', en: 'budget/bill-calendar/', es: 'budget/bill-calendar/es.html', h: 1100 },
  { id: 'savings-challenge', group: 'Budgeting', name: '52-week savings challenge', en: 'budget/savings-challenge.html', es: 'budget/reto-ahorro.html', h: 1200 },
  { id: 'afford', group: 'Budgeting', name: 'Can I afford this? (cash vs loan vs buy now, pay later)', en: 'budget/afford.html', h: 1100 },
  { id: 'money-personality', group: 'Budgeting', name: 'Money personality quiz', en: 'budget/money-personality.html', h: 900 },
  { id: 'freelance-rate', group: 'Freelancers', name: 'Freelance rate calculator: what to charge', en: 'freelance-invoices/rate.html', h: 1100 },
  { id: 'side-hustle', group: 'Freelancers', name: 'Side hustle profit calculator', en: 'freelance-invoices/side-hustle.html', h: 1200 },
];

// Draft prices: Dhruv sets the final ones (see apps/README.md, "Embeds and licences"). Payment stays a contact link.
export const PLANS = [
  { name: 'Free', price: '$0', points: ['Any tool, English or Spanish', 'Calculators in your colours', 'A small "Free tool by" link under each tool', 'No cookies, no tracking, nothing your readers type is sent anywhere'] },
  { name: 'Calculator licence', price: '$29 a month', points: ['Every calculator, English and Spanish', 'No credit link', 'Your own button under every result (savings account, loan, coaching)', 'Locked to your domains'], feature: true },
  { name: 'White-label toolkit', price: '$99 a month', points: ['Every tool on this page, calculators and scam checks included', 'Hosted for you on your own subdomain, in your brand', 'Your links and your contact details', 'Or as files for your web team'] },
];

const calcName = (p) => p.h1.replace(/\s*\(.*\)$/, '').replace(/:.*$/, '');
const calcOptions = pages.map((p) => `<option value="calc:${p.slug}" data-es="${pagesEs.some((e) => e.slug === p.slug) ? '1' : ''}">${esc(calcName(p))}</option>`).join('');
const groups = [...new Set(TOOLS.map((t) => t.group))];
const toolOptions = groups.map((g) => `<optgroup label="${esc(g)}">${TOOLS.filter((t) => t.group === g).map((t) => `<option value="${t.id}" data-es="${t.es ? '1' : ''}">${esc(t.name)}</option>`).join('')}</optgroup>`).join('');

export function embedPage() {
  const hub = readFileSync(join(root, 'index.html'), 'utf8');
  const style = (/<style>[\s\S]*?<\/style>/.exec(hub) || [''])[0].replace('</style>', `.layout{display:grid;gap:16px;margin-top:16px}@media (min-width:900px){.layout{grid-template-columns:minmax(0,380px) 1fr}}
.panel{background:var(--card);border:1px solid var(--line);border-radius:16px;padding:16px;min-width:0}
.panel label{display:block;font-weight:700;font-size:14px;margin:0 0 12px}
.panel select,.panel input,.panel textarea{display:block;width:100%;margin-top:4px;font:inherit;font-weight:400;padding:9px 10px;border-radius:10px;border:1px solid var(--line);background:var(--paper);color:var(--ink)}
.panel textarea{font:13px/1.4 ui-monospace,Menlo,Consolas,monospace;resize:vertical}
.panel input[type=color]{height:42px;padding:4px}
#preview{min-height:300px}
.plans{display:grid;gap:14px;grid-template-columns:repeat(auto-fill,minmax(240px,1fr));margin-top:16px}
.plan{background:var(--card);border:1px solid var(--line);border-radius:16px;padding:18px}.plan.feature{border:2px solid var(--gold)}
.plan h3{margin:0}.plan .price{font-size:22px;font-weight:800;margin:4px 0 8px}.plan ul{margin:0;padding-left:18px;color:var(--muted);font-size:15px}
</style>`);
  return `<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Embed Free Money and Scam Tools on Your Website | Snippet Maker</title>
<meta name="description" content="Put any of our free tools on your site with one line of code: money calculators, the scam message and link checkers, the bill calendar, budget planners and freelancer tools. English and Spanish. White-label plans for credit unions, banks and coaches.">
<meta name="theme-color" content="#0b1d13">
<link rel="icon" href="budget/icon-192.png">
${style}
</head>
<body>
<main>
  <p class="brand"><a href="./">All free tools</a></p>
  <h1>Put our free tools on your website</h1>
  <p class="lede">Pick a tool, copy one line of code, and paste it into any page. It resizes itself, works on phones, sets no cookies, and keeps your readers on your site. Everything people type stays in their browser.</p>
  <div class="layout">
    <form class="panel" id="maker">
      <label>Tool<select id="tool"><optgroup label="Money calculators">${calcOptions}</optgroup>${toolOptions}</select></label>
      <label>Language<select id="lang"><option value="en">English</option><option value="es">Español</option></select></label>
      <div id="calc-opts">
        <label>Button colour<input id="accent" type="color" value="#f2b134"></label>
        <label>Theme<select id="theme"><option value="">Match the reader's device</option><option value="light">Always light</option><option value="dark">Always dark</option></select></label>
        <label>Licence key (licensed partners only)<input id="licence" placeholder="Leave blank for the free version" autocomplete="off"></label>
      </div>
      <label>Paste this where you want the tool<textarea id="code" rows="5" readonly></textarea></label>
      <button type="button" class="btn" id="copy">Copy code</button> <span id="copied" class="none" aria-live="polite"></span>
    </form>
    <section class="panel" aria-labelledby="h-preview"><h2 id="h-preview">Preview</h2><div id="preview"></div></section>
  </div>
  <section aria-labelledby="h-plans">
    <h2 id="h-plans">Plans</h2>
    <p class="brand">Free for everyone. Licences for credit unions, banks, employers and coaches who want the tools as their own.</p>
    <div class="plans">
${PLANS.map((p) => `      <div class="plan${p.feature ? ' feature' : ''}"><h3>${esc(p.name)}</h3><p class="price">${esc(p.price)}</p><ul>${p.points.map((x) => `<li>${esc(x)}</li>`).join('')}</ul></div>`).join('\n')}
    </div>
    <p style="margin-top:16px"><a class="btn" href="${esc(config.embed.licenceUrl)}">Ask about a licence</a></p>
  </section>
</main>
<footer><p>Not financial or legal advice. The tools run in your readers' browsers: no accounts and nothing sent to us.</p></footer>
<script type="module">
const TOOLS = ${JSON.stringify(Object.fromEntries(TOOLS.map((t) => [t.id, { en: t.en, es: t.es || '', h: t.h, name: t.name }])))};
const $ = (s) => document.querySelector(s);
const base = new URL('./', location.href).href;
const clean = (v) => String(v).replace(/[^a-zA-Z0-9#-]/g, '');
function update() {
  const opt = $('#tool').selectedOptions[0];
  const hasEs = opt.dataset.es === '1';
  $('#lang').disabled = !hasEs;
  if (!hasEs) $('#lang').value = 'en';
  const lang = $('#lang').value;
  const v = $('#tool').value;
  let div; let src;
  if (v.startsWith('calc:')) {
    $('#calc-opts').hidden = false;
    const accent = $('#accent').value.toLowerCase() === '#f2b134' ? '' : clean($('#accent').value);
    div = '<div class="mms-calc" data-calc="' + v.slice(5) + '" data-lang="' + lang + '"' + (accent ? ' data-accent="' + accent + '"' : '') + ($('#theme').value ? ' data-theme="' + clean($('#theme').value) + '"' : '') + ($('#licence').value.trim() ? ' data-licence="' + clean($('#licence').value.trim()) + '"' : '') + '></div>';
    src = base + 'money-calculators/embed.js';
  } else {
    $('#calc-opts').hidden = true;
    const t = TOOLS[v];
    div = '<div class="mms-tool" data-tool="' + (lang === 'es' && t.es ? t.es : t.en) + '" data-height="' + t.h + '" data-title="' + t.name.replace(/"/g, '') + '"></div>';
    src = base + 'embed.js';
  }
  $('#code').value = div + '\\n<script src="' + src + '" async><\\/script>';
  $('#preview').innerHTML = div;
  const s = document.createElement('script'); s.src = src + '?' + Date.now(); document.body.append(s);
}
for (const id of ['#tool', '#lang', '#accent', '#theme', '#licence']) $(id).addEventListener('change', update);
$('#maker').addEventListener('submit', (e) => e.preventDefault());
$('#copy').addEventListener('click', async () => {
  try { await navigator.clipboard.writeText($('#code').value); $('#copied').textContent = 'Copied.'; } catch { $('#code').select(); $('#copied').textContent = 'Press Ctrl+C or Cmd+C to copy.'; }
});
update();
</script>
</body>
</html>
`;
}

if (process.argv[1] === fileURLToPath(import.meta.url)) {
  writeFileSync(join(root, 'embed.html'), embedPage());
  console.log(`embed.html: ${pages.length} calculators, ${TOOLS.length} tools`);
}
