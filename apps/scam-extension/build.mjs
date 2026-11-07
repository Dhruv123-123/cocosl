// Builds the extension from the scam checker: copies the shared rule engine and translations into
// lib/, and writes the manifest and store names from scam-checker/config.js.
//   node scam-extension/build.mjs                         Scam Shield, in place (CI checks it's committed and current)
//   node scam-extension/build.mjs --brand scam-decoded    a branded copy in build/scam-decoded/ (load it unpacked)
// A brand file (brands/<name>.json) sets the name, site, colours and the explainer page for each scam type;
// its icons live in brands/<name>/icons/.
import { readFileSync, writeFileSync, mkdirSync, copyFileSync, readdirSync } from 'node:fs';
import { join, dirname } from 'node:path';
import { fileURLToPath } from 'node:url';
import config from '../scam-checker/config.js';
import { GUIDES } from '../scam-checker/lib/scan.js';

const here = dirname(fileURLToPath(import.meta.url));
const src = join(here, '..', 'scam-checker');
const header = '// GENERATED from scam-checker/ by scam-extension/build.mjs. Edit the original, then rebuild.\n';
const version = '1.0.0';
const argBrand = (() => { const a = process.argv.slice(2); const i = a.findIndex((x) => x.startsWith('--brand')); if (i < 0) return null; return a[i].includes('=') ? a[i].split('=')[1] : a[i + 1]; })();

function build(out, { brand, siteUrl, product, explainers, css = '', iconsDir = null }) {
  mkdirSync(join(out, 'lib'), { recursive: true });
  for (const f of ['scan.js', 'i18n.js', 'site.js']) writeFileSync(join(out, 'lib', f), header + readFileSync(join(src, 'lib', f), 'utf8'));
  // Only what the popup needs; no email or analytics settings.
  writeFileSync(join(out, 'lib', 'config.js'), `${header}export default ${JSON.stringify({ brand, siteUrl, product, explainers }, null, 2)};\n`);
  if (out !== here) {
    for (const f of ['popup.html', 'popup.js', 'background.js']) copyFileSync(join(here, f), join(out, f));
    writeFileSync(join(out, 'popup.css'), readFileSync(join(here, 'popup.css'), 'utf8') + css);
    mkdirSync(join(out, 'icons'), { recursive: true });
    for (const f of readdirSync(iconsDir)) if (/\.(png|svg)$/.test(f)) copyFileSync(join(iconsDir, f), join(out, 'icons', f));
  }
  const manifest = {
    manifest_version: 3,
    name: '__MSG_extName__',
    short_name: brand,
    description: '__MSG_extDescription__',
    version,
    default_locale: 'en',
    icons: { 16: 'icons/icon-16.png', 32: 'icons/icon-32.png', 48: 'icons/icon-48.png', 128: 'icons/icon-128.png' },
    action: { default_popup: 'popup.html', default_title: '__MSG_actionTitle__', default_icon: { 16: 'icons/icon-16.png', 32: 'icons/icon-32.png' } },
    background: { service_worker: 'background.js', type: 'module' },
    // scripting + activeTab: read the current page's words once, when the person clicks the button. No host permissions.
    permissions: ['contextMenus', 'activeTab', 'storage', 'scripting'],
    optional_permissions: ['tabs'],
    homepage_url: siteUrl,
  };
  writeFileSync(join(out, 'manifest.json'), JSON.stringify(manifest, null, 2) + '\n');

  const locales = {
    en: {
      extName: `${brand}: Is This a Scam?`,
      extDescription: 'Check a text, email, link or the page you\'re on for scam red flags in one click. Runs on your device; nothing is sent anywhere.',
      actionTitle: 'Is this a scam?',
      menuSelection: `Check this text with ${brand}`,
      menuLink: `Check this link with ${brand}`,
      badgeTitle: 'Warning: this website looks like a fake. Click for details.',
    },
    es: {
      extName: `${brand}: ¿Es una estafa?`,
      extDescription: 'Revisa un mensaje, correo, enlace o la página en la que estás en busca de señales de estafa con un clic. Funciona en tu dispositivo; nada se envía.',
      actionTitle: '¿Es una estafa?',
      menuSelection: `Revisar este texto con ${brand}`,
      menuLink: `Revisar este enlace con ${brand}`,
      badgeTitle: 'Cuidado: este sitio parece falso. Haz clic para ver detalles.',
    },
  };
  for (const [lang, msgs] of Object.entries(locales)) {
    mkdirSync(join(out, '_locales', lang), { recursive: true });
    const o = Object.fromEntries(Object.entries(msgs).map(([k, message]) => [k, { message }]));
    writeFileSync(join(out, '_locales', lang, 'messages.json'), JSON.stringify(o, null, 2) + '\n');
  }
  console.log(`Built ${brand} extension v${version}${out === here ? '' : ` in ${out.slice(here.length + 1)}`}`);
}

if (argBrand) {
  if (!/^[a-z0-9-]+$/.test(argBrand)) throw new Error('Brand names are lowercase letters, digits and dashes');
  const b = JSON.parse(readFileSync(join(here, 'brands', `${argBrand}.json`), 'utf8'));
  const css = `\n/* ${b.brand} colours (brands/${argBrand}.json) */\n:root { --brand: ${b.colors.brand}; }\n@media (prefers-color-scheme: dark) { :root { --brand: ${b.colors.brandDark || b.colors.brand}; } }\n`;
  build(join(here, 'build', argBrand), { brand: b.brand, siteUrl: b.siteUrl, product: b.product || { url: '' }, explainers: b.explainers, css, iconsDir: join(here, 'brands', argBrand, 'icons') });
} else {
  // Scam Shield's own guides: scams/<slug>/ in English, es/estafas/<slug>/ in Spanish.
  const base = config.siteUrl.replace(/\/$/, '');
  const explainers = { base: `${base}/scams/`, es: `${base}/es/estafas/`, map: GUIDES };
  build(here, { brand: config.brand, siteUrl: config.siteUrl, product: config.product, explainers });
}
