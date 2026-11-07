// Builds the extension from the scam checker: copies the shared rule engine and translations into
// lib/, and writes the manifest and store names from scam-checker/config.js.
//   node scam-extension/build.mjs        (CI checks the output is committed and current)
import { readFileSync, writeFileSync, mkdirSync } from 'node:fs';
import { join, dirname } from 'node:path';
import { fileURLToPath } from 'node:url';
import config from '../scam-checker/config.js';

const here = dirname(fileURLToPath(import.meta.url));
const src = join(here, '..', 'scam-checker');
const header = '// GENERATED from scam-checker/ by scam-extension/build.mjs. Edit the original, then rebuild.\n';
mkdirSync(join(here, 'lib'), { recursive: true });
for (const f of ['scan.js', 'i18n.js']) writeFileSync(join(here, 'lib', f), header + readFileSync(join(src, 'lib', f), 'utf8'));

// Only what the popup needs; no email or analytics settings.
const { brand, siteUrl, product } = config;
writeFileSync(join(here, 'lib', 'config.js'), `${header}export default ${JSON.stringify({ brand, siteUrl, product }, null, 2)};\n`);

const version = '1.0.0';
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
  permissions: ['contextMenus', 'activeTab', 'storage'],
  optional_permissions: ['tabs'],
  homepage_url: siteUrl,
};
writeFileSync(join(here, 'manifest.json'), JSON.stringify(manifest, null, 2) + '\n');

const locales = {
  en: {
    extName: `${brand}: Is This a Scam?`,
    extDescription: 'Check a text, email or link for scam red flags in one click. Runs on your device; nothing you check is sent anywhere.',
    actionTitle: 'Is this a scam?',
    menuSelection: `Check this text with ${brand}`,
    menuLink: `Check this link with ${brand}`,
    badgeTitle: 'Warning: this website looks like a fake. Click for details.',
  },
  es: {
    extName: `${brand}: ¿Es una estafa?`,
    extDescription: 'Revisa un mensaje, correo o enlace en busca de señales de estafa con un clic. Funciona en tu dispositivo; nada se envía.',
    actionTitle: '¿Es una estafa?',
    menuSelection: `Revisar este texto con ${brand}`,
    menuLink: `Revisar este enlace con ${brand}`,
    badgeTitle: 'Cuidado: este sitio parece falso. Haz clic para ver detalles.',
  },
};
for (const [lang, msgs] of Object.entries(locales)) {
  mkdirSync(join(here, '_locales', lang), { recursive: true });
  const out = Object.fromEntries(Object.entries(msgs).map(([k, message]) => [k, { message }]));
  writeFileSync(join(here, '_locales', lang, 'messages.json'), JSON.stringify(out, null, 2) + '\n');
}
console.log(`Built ${brand} extension v${version}`);
