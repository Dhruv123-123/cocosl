// Packs the extension into dist/<name>-<version>.zip for the Chrome Web Store upload.
//   node scam-extension/package.mjs                       Scam Shield (this folder)
//   node scam-extension/package.mjs build/scam-decoded    a branded build from build.mjs --brand
// Plain zip writer (deflate via zlib) so there's nothing to install.
import { readFileSync, writeFileSync, readdirSync, statSync, mkdirSync } from 'node:fs';
import { join, dirname, relative, sep } from 'node:path';
import { fileURLToPath } from 'node:url';
import { deflateRawSync } from 'node:zlib';

const here = dirname(fileURLToPath(import.meta.url));
const root = process.argv[2] ? join(here, process.argv[2]) : here;
const SKIP = new Set(['dist', 'build', 'brands', 'test', 'build.mjs', 'package.mjs', 'render.mjs', 'icon.svg', 'STORE.md', 'README.md', '.gitignore', 'store-shots.mjs']);

const files = [];
(function walk(dir) {
  for (const f of readdirSync(dir).sort()) {
    if (SKIP.has(f)) continue;
    const p = join(dir, f);
    if (statSync(p).isDirectory()) walk(p); else files.push(p);
  }
})(root);

const table = new Uint32Array(256).map((_, n) => { let c = n; for (let k = 0; k < 8; k++) c = c & 1 ? 0xedb88320 ^ (c >>> 1) : c >>> 1; return c >>> 0; });
const crc32 = (buf) => { let c = 0xffffffff; for (const b of buf) c = table[(c ^ b) & 0xff] ^ (c >>> 8); return (c ^ 0xffffffff) >>> 0; };

const locals = []; const centrals = []; let offset = 0;
for (const file of files) {
  const name = Buffer.from(relative(root, file).split(sep).join('/'));
  const data = readFileSync(file);
  const packed = deflateRawSync(data);
  const crc = crc32(data);
  const local = Buffer.alloc(30);
  local.writeUInt32LE(0x04034b50, 0); local.writeUInt16LE(20, 4); local.writeUInt16LE(0, 6); local.writeUInt16LE(8, 8);
  local.writeUInt16LE(0, 10); local.writeUInt16LE(0x21, 12); // fixed date 1980-01-01 keeps builds reproducible
  local.writeUInt32LE(crc, 14); local.writeUInt32LE(packed.length, 18); local.writeUInt32LE(data.length, 22);
  local.writeUInt16LE(name.length, 26); local.writeUInt16LE(0, 28);
  const central = Buffer.alloc(46);
  central.writeUInt32LE(0x02014b50, 0); central.writeUInt16LE(20, 4); central.writeUInt16LE(20, 6); central.writeUInt16LE(0, 8); central.writeUInt16LE(8, 10);
  central.writeUInt16LE(0, 12); central.writeUInt16LE(0x21, 14); central.writeUInt32LE(crc, 16); central.writeUInt32LE(packed.length, 20); central.writeUInt32LE(data.length, 24);
  central.writeUInt16LE(name.length, 28); central.writeUInt32LE(offset, 42);
  locals.push(local, name, packed); centrals.push(central, name);
  offset += 30 + name.length + packed.length;
}
const cd = Buffer.concat(centrals);
const end = Buffer.alloc(22);
end.writeUInt32LE(0x06054b50, 0); end.writeUInt16LE(files.length, 8); end.writeUInt16LE(files.length, 10); end.writeUInt32LE(cd.length, 12); end.writeUInt32LE(offset, 16);

const manifest = JSON.parse(readFileSync(join(root, 'manifest.json'), 'utf8'));
const slug = manifest.short_name.toLowerCase().replace(/[^a-z0-9]+/g, '-');
mkdirSync(join(here, 'dist'), { recursive: true });
const out = join(here, 'dist', `${slug}-extension-${manifest.version}.zip`);
writeFileSync(out, Buffer.concat([...locals, cd, end]));
console.log(`Packed ${files.length} files into ${relative(process.cwd(), out)}`);
