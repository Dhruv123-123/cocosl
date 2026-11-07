// Builds the Money Toolkit: every tool in tools/toolkit.mjs as one self-contained HTML file (CSS, scripts and
// images inlined), plus an index page, in a folder and a zip. Opens from the folder with no internet: browsers
// won't load JavaScript modules from file:// pages, so each page's modules are bundled into one plain script.
// Needs esbuild: `npm i -D esbuild`, or set ESBUILD_PATH to its package folder.
// Run from apps/: node tools/build-toolkit.mjs [out-dir]   (default: ../launch/money-toolkit/dist)
import { readFileSync, writeFileSync, mkdirSync, rmSync, existsSync } from 'node:fs';
import { join, dirname, posix, extname } from 'node:path';
import { fileURLToPath } from 'node:url';
import { createRequire } from 'node:module';
import { execFileSync } from 'node:child_process';
import { SECTIONS, ITEMS, sourceFile } from './toolkit.mjs';

const root = join(dirname(fileURLToPath(import.meta.url)), '..');
const require = createRequire(import.meta.url);
let esbuild;
try { esbuild = require(process.env.ESBUILD_PATH || 'esbuild'); } catch { console.log('esbuild not installed (npm i -D esbuild, or set ESBUILD_PATH): skipping the toolkit build.'); process.exit(0); }

export const VERSION = '2026.11';
const outRoot = process.argv[2] || join(root, '..', 'launch', 'money-toolkit', 'dist');
const dir = join(outRoot, 'Money-Toolkit');
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
  const back = item.lang === 'es' ? 'Volver al Money Toolkit' : 'Back to the Money Toolkit';
  html = html.replace(/<body([^>]*)>/, `<body$1>\n<p class="tk-bar"><a href="index.html">← ${back}</a></p>`);
  html = html.replace(/<\/body>/, () => `${bundled.map((js) => `<script>${js}</script>`).join('\n')}\n</body>`); // a function, so $& in the code isn't a pattern
  writeFileSync(join(dir, item.out), html);
  return { out: item.out, kb: Math.round(html.length / 1024) };
}

function indexPage() {
  const hub = readFileSync(join(root, 'index.html'), 'utf8');
  const style = (/<style>([\s\S]*?)<\/style>/.exec(hub) || ['', ''])[1];
  const sections = SECTIONS.map((s) => `  <section id="${s.id}" aria-labelledby="h-${s.id}"${s.lang ? ` lang="${s.lang}"` : ''}>
    <h2 id="h-${s.id}">${esc(s.en)}</h2>
    <div class="grid">
${ITEMS.filter((i) => i.section === s.id).map((i) => `      <a class="card" href="${i.out}"><h3>${esc(i.title)}</h3><p>${esc(i.blurb)}</p></a>`).join('\n')}
    </div>
  </section>`).join('\n');
  return `<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Money Toolkit</title>
<meta name="description" content="${ITEMS.length} private money tools that work with no internet: calculators, budget planners, bill calendar, scam checkers and freelancer tools.">
<style>${style}</style>
</head>
<body>
<main>
  <h1>Money Toolkit</h1>
  <p class="lede">${ITEMS.length} money tools that run on your computer with no internet and no account. Everything you type stays on this device. Bookmark this page, or keep the folder on your desktop.</p>
  <ul class="jump">${SECTIONS.map((s) => `<li><a href="#${s.id}">${esc(s.en)}</a></li>`).join('')}</ul>
${sections}
  <section aria-labelledby="h-tips">
    <h2 id="h-tips">Good to know</h2>
    <p>Your entries are saved in your browser on this computer. Use the same browser to come back to them, and use each tool's download or backup button for anything you want to keep. Clearing your browser's data deletes them.</p>
    <p>Tax and benefit numbers are for 2026. Version ${VERSION}. Not financial, tax or legal advice.</p>
  </section>
</main>
<footer><p>Money Toolkit by Money Made Simple. For your own personal use: please don't share or resell the files.</p></footer>
</body>
</html>
`;
}

const START = `MONEY TOOLKIT (version ${VERSION})

1. Unzip this folder (on Windows: right-click > Extract All; on a Mac: double-click).
2. Open "index.html" in Chrome, Edge, Firefox or Safari.
3. Pick a tool. Everything works with no internet, and nothing you type leaves your computer.

Your entries are saved in the browser you use. Use the same browser next time.
Questions: reply to your purchase receipt email.

Not financial, tax or legal advice. For your own personal use.
`;

if (process.argv[1] === fileURLToPath(import.meta.url)) {
  if (existsSync(dir)) rmSync(dir, { recursive: true });
  mkdirSync(dir, { recursive: true });
  const sizes = [];
  for (const item of ITEMS) sizes.push(await buildPage(item));
  writeFileSync(join(dir, 'index.html'), indexPage());
  writeFileSync(join(dir, 'START HERE.txt'), START);
  const zip = join(outRoot, 'Money-Toolkit.zip');
  if (existsSync(zip)) rmSync(zip);
  execFileSync('python3', ['-c', 'import shutil,sys; shutil.make_archive(sys.argv[1], "zip", sys.argv[2], "Money-Toolkit")', zip.replace(/\.zip$/, ''), outRoot]);
  const total = sizes.reduce((t, s) => t + s.kb, 0);
  console.log(`Money Toolkit: ${sizes.length} tools + index, ${total} KB of HTML, ${zip}`);
}
