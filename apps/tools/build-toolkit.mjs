// Builds the Money Toolkit: every tool in tools/toolkit.mjs as one self-contained HTML file (CSS, scripts and
// images inlined), plus an index page, in a folder and a zip. Opens from the folder with no internet: browsers
// won't load JavaScript modules from file:// pages, so each page's modules are bundled into one plain script.
// Needs esbuild: `npm i -D esbuild`, or set ESBUILD_PATH to its package folder.
// Run from apps/: node tools/build-toolkit.mjs [--edition es] [out-dir]   (default: ../launch/money-toolkit/dist)
// --edition es builds the Spanish "Caja de herramientas de dinero" for Dinero Simple from SECTIONS_ES.
import { readFileSync, writeFileSync, mkdirSync, rmSync, existsSync } from 'node:fs';
import { join, dirname, posix, extname } from 'node:path';
import { fileURLToPath } from 'node:url';
import { createRequire } from 'node:module';
import { execFileSync } from 'node:child_process';
import { EDITIONS, itemsOf, sourceFile } from './toolkit.mjs';

const root = join(dirname(fileURLToPath(import.meta.url)), '..');
const require = createRequire(import.meta.url);
let esbuild;
try { esbuild = require(process.env.ESBUILD_PATH || 'esbuild'); } catch { console.log('esbuild not installed (npm i -D esbuild, or set ESBUILD_PATH): skipping the toolkit build.'); process.exit(0); }

export const VERSION = '2026.11';
const args = process.argv.slice(2);
const edKey = args.includes('--edition') ? args[args.indexOf('--edition') + 1] : 'en';
const ED = EDITIONS[edKey] || EDITIONS.en;
const SECTIONS = ED.sections;
const ITEMS = itemsOf(SECTIONS);
const es = ED.lang === 'es';
const outRoot = args.filter((a, i) => a !== '--edition' && args[i - 1] !== '--edition')[0] || join(root, '..', 'launch', 'money-toolkit', 'dist');
const dir = join(outRoot, ED.folder);
const esc = (s) => String(s).replace(/[&<>"]/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' })[c]);
const MIME = { '.png': 'image/png', '.svg': 'image/svg+xml', '.jpg': 'image/jpeg', '.webp': 'image/webp' };
const bySrc = new Map(ITEMS.map((i) => [sourceFile(i.src), i.out]));

async function bundle(opts) {
  const r = await esbuild.build({ bundle: true, write: false, format: 'iife', minify: true, target: 'es2020', legalComments: 'none', logLevel: 'silent', ...opts });
  return r.outputFiles[0].text.replace(/<\/script/gi, '<\\/script');
}

/** Where a relative link from a page points, as a path from apps/ (or null for outside links). */
function resolveLink(fromFile, href) {
  if (/^(https?:|mailto:|tel:|#|data:|javascript:)/i.test(href) || !href) return null;
  const clean = href.split('#')[0].split('?')[0];
  if (!clean) return null;
  let p = posix.normalize(posix.join(posix.dirname(fromFile), clean));
  if (p.endsWith('/') || !extname(p)) p = `${p.replace(/\/$/, '')}/index.html`;
  return p.replace(/^\.\//, '');
}

const KIT_CSS = `.signup-box,form.signup,.signup,.install,[data-embed-hide]{display:none!important}
.tk-bar{font:15px/1.4 system-ui,sans-serif;margin:0;padding:10px 16px;background:#0b1d13;color:#f4f1e8}
.tk-bar a{color:#f2b134;font-weight:700}`;

async function buildPage(item) {
  const file = sourceFile(item.src);
  const srcDir = join(root, dirname(file));
  let html = readFileSync(join(root, file), 'utf8');
  const scripts = [];
  // Modules: bundle each external one (skip the embed helper), and any inline module.
  html = html.replace(/<script type="module" src="([^"]+)"><\/script>\n?/g, (m, src) => { if (!/embed-page\.js$/.test(src)) scripts.push({ entry: join(srcDir, src) }); return ''; });
  html = html.replace(/<script type="module">([\s\S]*?)<\/script>\n?/g, (m, code) => { scripts.push({ code }); return ''; });
  const bundled = [];
  for (const s of scripts) bundled.push(s.entry ? await bundle({ entryPoints: [s.entry] }) : await bundle({ stdin: { contents: s.code, resolveDir: srcDir, loader: 'js' } }));
  // Stylesheets inline; icons, manifests and alternates dropped (they point at files that aren't in the kit).
  html = html.replace(/<link rel="stylesheet" href="([^"]+)">/g, (m, href) => (/^https?:/.test(href) ? m : `<style>${readFileSync(join(srcDir, href), 'utf8')}</style>`));
  html = html.replace(/<link rel="(icon|apple-touch-icon|manifest|alternate|canonical)"[^>]*>\n?/g, '');
  html = html.replace(/<img([^>]*?) src="([^"]+)"/g, (m, pre, src) => {
    if (/^(https?:|data:)/.test(src)) return m;
    const b = readFileSync(join(srcDir, src));
    return `<img${pre} src="data:${MIME[extname(src)] || 'application/octet-stream'};base64,${b.toString('base64')}"`;
  });
  // Links to other tools in the kit stay in the kit; other links on this site go to the kit's index page.
  html = html.replace(/(<a\b[^>]*?\bhref=")([^"]*)"/g, (m, pre, href) => {
    const p = resolveLink(file, href);
    if (p === null) return m;
    return `${pre}${bySrc.get(p) || 'index.html'}"`;
  });
  html = html.replace(/<\/head>/, `<style>${KIT_CSS}</style>\n</head>`);
  const back = es ? 'Volver a la Caja de herramientas' : item.lang === 'es' ? 'Volver al Money Toolkit' : 'Back to the Money Toolkit';
  html = html.replace(/<body([^>]*)>/, `<body$1>\n<p class="tk-bar"><a href="index.html">← ${back}</a></p>`);
  html = html.replace(/<\/body>/, () => `${bundled.map((js) => `<script>${js}</script>`).join('\n')}\n</body>`); // a function, so $& in the code isn't a pattern
  writeFileSync(join(dir, item.out), html);
  return { out: item.out, kb: Math.round(html.length / 1024) };
}

const TXT = es ? {
  title: 'Caja de herramientas de dinero', desc: (n) => `${n} herramientas de dinero en español que funcionan sin internet: calculadoras, presupuesto, calendario de pagos y protección contra estafas.`,
  lede: (n) => `${n} herramientas de dinero que funcionan en tu computadora sin internet y sin cuenta. Todo lo que escribes se queda en este aparato. Guarda esta página en favoritos o deja la carpeta en tu escritorio.`,
  tipsH: 'Bueno saber', tips: ['Lo que escribes se guarda en el navegador de esta computadora. Usa el mismo navegador para volver a verlo, y usa el botón de descargar o respaldar de cada herramienta para lo que quieras guardar. Si borras los datos del navegador, se borra.', `Los números de impuestos y beneficios son de 2026. Versión ${VERSION}. No es asesoría financiera, de impuestos ni legal.`],
  foot: 'Caja de herramientas de dinero de Dinero Simple. Para tu uso personal: por favor no compartas ni revendas los archivos.',
  start: `CAJA DE HERRAMIENTAS DE DINERO (versión ${VERSION})

1. Descomprime esta carpeta (en Windows: clic derecho > Extraer todo; en Mac: doble clic).
2. Abre "index.html" en Chrome, Edge, Firefox o Safari.
3. Elige una herramienta. Todo funciona sin internet y nada de lo que escribes sale de tu computadora.

Lo que escribes se guarda en el navegador que uses. Usa el mismo la próxima vez.
¿Preguntas? Responde al correo de tu recibo de compra.

No es asesoría financiera, de impuestos ni legal. Para tu uso personal.
`,
} : {
  title: 'Money Toolkit', desc: (n) => `${n} private money tools that work with no internet: calculators, budget planners, bill calendar, scam checkers and freelancer tools.`,
  lede: (n) => `${n} money tools that run on your computer with no internet and no account. Everything you type stays on this device. Bookmark this page, or keep the folder on your desktop.`,
  tipsH: 'Good to know', tips: ['Your entries are saved in your browser on this computer. Use the same browser to come back to them, and use each tool\'s download or backup button for anything you want to keep. Clearing your browser\'s data deletes them.', `Tax and benefit numbers are for 2026. Version ${VERSION}. Not financial, tax or legal advice.`],
  foot: 'Money Toolkit by Money Made Simple. For your own personal use: please don\'t share or resell the files.',
  start: `MONEY TOOLKIT (version ${VERSION})

1. Unzip this folder (on Windows: right-click > Extract All; on a Mac: double-click).
2. Open "index.html" in Chrome, Edge, Firefox or Safari.
3. Pick a tool. Everything works with no internet, and nothing you type leaves your computer.

Your entries are saved in the browser you use. Use the same browser next time.
Questions: reply to your purchase receipt email.

Not financial, tax or legal advice. For your own personal use.
`,
};

function indexPage() {
  const hub = readFileSync(join(root, 'index.html'), 'utf8');
  const style = (/<style>([\s\S]*?)<\/style>/.exec(hub) || ['', ''])[1];
  const head = (sec) => (es ? sec.es : sec.en);
  const sections = SECTIONS.map((sec) => `  <section id="${sec.id}" aria-labelledby="h-${sec.id}"${sec.lang && sec.lang !== ED.lang ? ` lang="${sec.lang}"` : ''}>
    <h2 id="h-${sec.id}">${esc(head(sec))}</h2>
    <div class="grid">
${ITEMS.filter((i) => i.section === sec.id).map((i) => `      <a class="card" href="${i.out}"><h3>${esc(i.title)}</h3><p>${esc(i.blurb)}</p></a>`).join('\n')}
    </div>
  </section>`).join('\n');
  return `<!doctype html>
<html lang="${ED.lang}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>${TXT.title}</title>
<meta name="description" content="${esc(TXT.desc(ITEMS.length))}">
<style>${style}</style>
</head>
<body>
<main>
  <h1>${TXT.title}</h1>
  <p class="lede">${esc(TXT.lede(ITEMS.length))}</p>
  <ul class="jump">${SECTIONS.map((sec) => `<li><a href="#${sec.id}">${esc(head(sec))}</a></li>`).join('')}</ul>
${sections}
  <section aria-labelledby="h-tips">
    <h2 id="h-tips">${TXT.tipsH}</h2>
${TXT.tips.map((t) => `    <p>${esc(t)}</p>`).join('\n')}
  </section>
</main>
<footer><p>${esc(TXT.foot)}</p></footer>
</body>
</html>
`;
}

if (process.argv[1] === fileURLToPath(import.meta.url)) {
  if (existsSync(dir)) rmSync(dir, { recursive: true });
  mkdirSync(dir, { recursive: true });
  const sizes = [];
  for (const item of ITEMS) sizes.push(await buildPage(item));
  writeFileSync(join(dir, 'index.html'), indexPage());
  writeFileSync(join(dir, es ? 'EMPIEZA AQUI.txt' : 'START HERE.txt'), TXT.start);
  const zip = join(outRoot, ED.zip);
  if (existsSync(zip)) rmSync(zip);
  execFileSync('python3', ['-c', 'import shutil,sys; shutil.make_archive(sys.argv[1], "zip", sys.argv[2], sys.argv[3])', zip.replace(/\.zip$/, ''), outRoot, ED.folder]);
  const total = sizes.reduce((t, s) => t + s.kb, 0);
  console.log(`${TXT.title}: ${sizes.length} tools + index, ${total} KB of HTML, ${zip}`);
}
