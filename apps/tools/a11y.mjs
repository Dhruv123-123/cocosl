// Accessibility pass: opens the hub and every tool it links to in Chromium and runs axe-core
// (WCAG 2.0/2.1 A and AA rules), in light and dark mode. Fails on any violation.
// Needs Playwright and axe-core (`npm i -D playwright axe-core`, or set AXE_PATH to axe.min.js).
// Run from apps/: node tools/a11y.mjs [--only path-substring]
import { createServer } from 'node:http';
import { readFile, stat } from 'node:fs/promises';
import { readFileSync, existsSync } from 'node:fs';
import { extname, join, normalize, dirname } from 'node:path';
import { fileURLToPath } from 'node:url';
import { createRequire } from 'node:module';
import { cardsFromHub } from './build-search.mjs';

const root = join(dirname(fileURLToPath(import.meta.url)), '..');
const require = createRequire(import.meta.url);
let playwright;
let axePath = process.env.AXE_PATH;
try { playwright = require('playwright'); } catch { console.log('Playwright not installed: skipping accessibility pass.'); process.exit(0); }
if (!axePath) { try { axePath = require.resolve('axe-core/axe.min.js'); } catch { /* not installed */ } }
if (!axePath || !existsSync(axePath)) { console.log('axe-core not installed (npm i -D axe-core, or set AXE_PATH): skipping accessibility pass.'); process.exit(0); }
const axeSource = readFileSync(axePath, 'utf8');

const types = { '.html': 'text/html', '.js': 'text/javascript', '.mjs': 'text/javascript', '.css': 'text/css', '.json': 'application/json', '.svg': 'image/svg+xml', '.webmanifest': 'application/manifest+json', '.png': 'image/png' };
const server = createServer(async (req, res) => {
  const p = normalize(decodeURIComponent(new URL(req.url, 'http://x').pathname)).replace(/^(\.\.[/\\])+/, '');
  let file = join(root, p);
  try { if ((await stat(file)).isDirectory()) file = join(file, 'index.html'); res.writeHead(200, { 'content-type': types[extname(file)] || 'application/octet-stream' }); res.end(await readFile(file)); }
  catch { res.writeHead(404); res.end('not found'); }
});

const only = process.argv.includes('--only') ? process.argv[process.argv.indexOf('--only') + 1] : '';
const hubPages = (dir) => cardsFromHub(readFileSync(join(root, dir, 'index.html'), 'utf8')).map((c) => new URL(c.u, `http://x/${dir ? `${dir}/` : ''}`).pathname);
const pages = [...new Set(['/', '/es/', ...hubPages(''), ...hubPages('es')])].filter((p) => p.includes(only));

await new Promise((r) => server.listen(0, r));
const base = `http://127.0.0.1:${server.address().port}`;
const browser = await playwright.chromium.launch();
let failed = 0;
for (const path of pages) {
  for (const colorScheme of ['light', 'dark']) {
    const page = await browser.newPage({ viewport: { width: 1280, height: 900 }, colorScheme });
    await page.goto(base + path, { waitUntil: 'networkidle' });
    await page.addScriptTag({ content: axeSource });
    const result = await page.evaluate(() => window.axe.run(document, { runOnly: { type: 'tag', values: ['wcag2a', 'wcag2aa', 'wcag21a', 'wcag21aa'] } }));
    const v = result.violations;
    if (v.length) failed++;
    console.log(`${v.length ? 'FAIL' : 'ok  '} ${path} (${colorScheme})${v.map((x) => `\n     ${x.id} [${x.impact}] ${x.help}: ${x.nodes.slice(0, 3).map((n) => { const d = n.any?.[0]?.data; return `${n.target.join(' ')}${d?.fgColor ? ` (${d.fgColor} on ${d.bgColor}, ${d.contrastRatio}:1)` : ''}`; }).join(', ')}${x.nodes.length > 3 ? ` +${x.nodes.length - 3} more` : ''}`).join('')}`);
    await page.close();
  }
}
await browser.close();
server.close();
console.log(failed ? `${failed} page checks with violations` : `All ${pages.length * 2} page checks pass`);
process.exit(failed ? 1 : 0);
