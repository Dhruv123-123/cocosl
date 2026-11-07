// Rename the scam brand everywhere in one go, then rebuild the guide pages and the browser extension.
//   node scam-checker/rename-brand.mjs "Scam Decoded" scamdecoded.netlify.app
// Replaces the current name (config.js `brand`) and domain (config.js `siteUrl`) in every
// page, script and doc in this folder.
import { readFileSync, writeFileSync, readdirSync, statSync } from 'node:fs';
import { join, dirname, extname } from 'node:path';
import { fileURLToPath } from 'node:url';
import { execFileSync } from 'node:child_process';
import config from './config.js';

const [newName, newDomain] = process.argv.slice(2);
if (!newName) { console.error('Usage: node rename-brand.mjs "New Name" [new-domain.com]'); process.exit(1); }
const root = dirname(fileURLToPath(import.meta.url));
const oldName = config.brand;
const oldDomain = new URL(config.siteUrl).host;
const exts = new Set(['.html', '.js', '.mjs', '.md', '.json']);

const files = [];
(function walk(dir) {
  for (const f of readdirSync(dir)) {
    const p = join(dir, f);
    if (statSync(p).isDirectory()) walk(p);
    else if (exts.has(extname(p)) && !p.endsWith('rename-brand.mjs')) files.push(p);
  }
})(root);

let changed = 0;
for (const f of files) {
  const before = readFileSync(f, 'utf8');
  let after = before.split(oldName).join(newName);
  if (newDomain) after = after.split(oldDomain).join(newDomain);
  if (after !== before) { writeFileSync(f, after); changed++; }
}
console.log(`Renamed "${oldName}" to "${newName}"${newDomain ? ` and ${oldDomain} to ${newDomain}` : ''} in ${changed} files.`);
execFileSync(process.execPath, [join(root, 'build.mjs')], { stdio: 'inherit' });
// The browser extension takes its name and site from this config, so rebuild it too.
execFileSync(process.execPath, [join(root, '..', 'scam-extension', 'build.mjs')], { stdio: 'inherit' });
