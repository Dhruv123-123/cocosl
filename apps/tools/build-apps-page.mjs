// Writes apps.html and es/apps.html: every tool that installs like an app (each has its own web app manifest),
// with how to add it to a phone or computer. Names, descriptions and icons come from the manifests, so the page
// stays in step with them. shared/test/apps-page.test.js fails if a manifest is added and not listed here,
// if a listed icon is missing or the wrong size, or if these pages are out of date.
// Run from apps/: node tools/build-apps-page.mjs
import { readFileSync, writeFileSync } from 'node:fs';
import { join, dirname, posix } from 'node:path';
import { fileURLToPath } from 'node:url';

const root = join(dirname(fileURLToPath(import.meta.url)), '..');
const esc = (s) => String(s).replace(/[&<>"]/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' })[c]);

// manifest: path from apps/. open: the page that links that manifest (where the install happens).
// es: the Spanish card. A Spanish page with its own manifest gets its own entry; English-only apps say so.
export const APPS = [
  { manifest: 'manifest.webmanifest', open: 'index.html', what: 'Every calculator, tracker, letter and scam check in one place. The tools you\'ve opened work offline.',
    es: { open: 'es/index.html', name: 'Herramientas de dinero', what: 'Todas las calculadoras y herramientas en español en un solo lugar. Las que ya abriste funcionan sin internet.' } },
  { manifest: 'app/manifest.webmanifest', open: 'app/index.html', what: 'Ten money tools on one home screen: budget, paycheck, bills, debt, savings, bill splitting and a scam check. All ten work offline, with no account.',
    es: { open: 'app/index.html?lang=es', what: 'Diez herramientas de dinero en una sola pantalla: presupuesto, salario neto, pagos, deudas, ahorro, dividir gastos y revisar estafas. Funcionan sin internet y sin cuenta.' } },
  { manifest: 'budget/manifest.webmanifest', open: 'budget/index.html', what: 'A monthly budget you keep up in 20 minutes, plus the bill tracker and 0% deal countdown. Your numbers stay on your phone.',
    es: { name: 'The 20-Minute Budget', what: 'Un presupuesto mensual sencillo. Por ahora solo en inglés.', englishOnly: true } },
  { manifest: 'budget/bill-calendar/manifest.webmanifest', open: 'budget/bill-calendar/index.html', what: 'Every bill this month on a calendar. Tick them off as you pay and send reminders to your phone\'s calendar.' },
  { manifest: 'budget/bill-calendar/manifest-es.webmanifest', open: 'budget/bill-calendar/es.html', lang: 'es',
    es: { what: 'Todos tus recibos del mes en un calendario. Márcalos al pagar y manda recordatorios al calendario de tu teléfono.' } },
  { manifest: 'freelance-invoices/set-aside/manifest.webmanifest', open: 'freelance-invoices/set-aside/index.html', what: 'Log each client payment and see how much to save for taxes and what to send the IRS each quarter.',
    es: { name: '1099 Tax Set-Aside', what: 'Para trabajadores independientes: cuánto guardar de cada pago para impuestos. Por ahora solo en inglés.', englishOnly: true } },
];

export function readApp(app) {
  const m = JSON.parse(readFileSync(join(root, app.manifest), 'utf8'));
  const dir = posix.dirname(app.manifest);
  const icon = m.icons.find((i) => i.sizes === '192x192' && i.type === 'image/png');
  return { ...app, m, icon: posix.normalize(posix.join(dir, icon.src)) };
}

const T = {
  en: {
    lang: 'en', file: 'apps.html', up: '', other: '<a href="es/apps.html" hreflang="es" lang="es">En español</a>',
    title: 'Install the Free Money Apps on Your Phone (No App Store)',
    desc: 'The free money tools that install like apps: a budget, a bill calendar, a tax set-aside for freelancers and the full toolbox. No app store, no account, and they work offline.',
    h1: 'Put the free tools on your phone', lede: 'These tools install like apps, straight from the browser: no app store, no account, nothing to pay. They open full screen, work offline once you\'ve used them, and your numbers stay on your device.',
    how: 'How to install', open: 'Open', install: 'Install this one now', installHere: 'Install the toolbox',
    steps: [
      ['iPhone and iPad', 'Open the app in <b>Safari</b>, tap <b>Share</b> (the square with an arrow), then <b>Add to Home Screen</b> and <b>Add</b>. In Chrome on iPhone it\'s the Share button in the address bar.'],
      ['Android', 'Open the app in <b>Chrome</b>, tap the <b>⋮</b> menu, then <b>Install app</b> or <b>Add to Home screen</b>. Samsung Internet: menu, then <b>Add page to</b>, then <b>Home screen</b>.'],
      ['Computer', 'In <b>Chrome</b> or <b>Edge</b>, click the install icon at the right end of the address bar (a screen with a down arrow), or the menu, then <b>Install</b>. On a Mac, Safari\'s <b>File</b> menu has <b>Add to Dock</b>.'],
    ],
    apps: 'The apps', offline: 'Works offline', english: '',
    faq: [
      ['Are these real apps?', 'They are web apps (sometimes called PWAs). They get an icon on your home screen and open full screen like any app, but they install from the browser instead of an app store, so there is no account and nothing to update by hand.'],
      ['Where is my data kept?', 'In your browser\'s storage on that device. Nothing you type is sent to a server. Because of that, removing the app or clearing your browser data deletes it, so use each app\'s export or backup if it has one.'],
      ['How do I remove one?', 'Like any app: press and hold the icon and choose Remove (iPhone) or Uninstall (Android). On a computer, open the app and use its menu.'],
    ],
    note: 'Not financial or legal advice. Private by design: no accounts, and the tools run in your browser.',
    back: '<a href="./">All free tools</a>',
  },
  es: {
    lang: 'es', file: 'es/apps.html', up: '../', other: '<a href="../apps.html" hreflang="en" lang="en">In English</a>',
    title: 'Instala las apps de dinero gratis en tu teléfono (sin tienda de apps)',
    desc: 'Las herramientas de dinero gratis que se instalan como apps: calendario de pagos y todas las herramientas en español. Sin tienda de apps, sin cuenta y funcionan sin internet.',
    h1: 'Pon las herramientas gratis en tu teléfono', lede: 'Estas herramientas se instalan como apps desde el navegador: sin tienda de apps, sin cuenta y sin pagar nada. Se abren en pantalla completa, funcionan sin internet cuando ya las usaste y tus números se quedan en tu teléfono.',
    how: 'Cómo instalarlas', open: 'Abrir', install: 'Instalar esta ahora', installHere: 'Instalar las herramientas',
    steps: [
      ['iPhone y iPad', 'Abre la app en <b>Safari</b>, toca <b>Compartir</b> (el cuadro con una flecha), luego <b>Agregar a inicio</b> y <b>Agregar</b>. En Chrome para iPhone es el botón de Compartir en la barra de direcciones.'],
      ['Android', 'Abre la app en <b>Chrome</b>, toca el menú <b>⋮</b> y luego <b>Instalar app</b> o <b>Agregar a la pantalla principal</b>. En Samsung Internet: menú, <b>Agregar página a</b> y <b>Pantalla de inicio</b>.'],
      ['Computadora', 'En <b>Chrome</b> o <b>Edge</b>, haz clic en el ícono de instalar al final de la barra de direcciones (una pantalla con una flecha), o en el menú y luego <b>Instalar</b>. En una Mac, el menú <b>Archivo</b> de Safari tiene <b>Agregar al Dock</b>.'],
    ],
    apps: 'Las apps', offline: 'Funciona sin internet', english: 'En inglés',
    faq: [
      ['¿Son apps de verdad?', 'Son apps web (también llamadas PWA). Tienen su ícono en tu pantalla de inicio y se abren en pantalla completa como cualquier app, pero se instalan desde el navegador y no desde una tienda, así que no necesitas cuenta ni actualizarlas a mano.'],
      ['¿Dónde se guardan mis datos?', 'En el almacenamiento del navegador de ese teléfono o computadora. Nada de lo que escribes se manda a un servidor. Por eso, si borras la app o los datos del navegador, se borran también: usa la opción de exportar o respaldar de cada app si la tiene.'],
      ['¿Cómo quito una?', 'Como cualquier app: deja presionado el ícono y elige Eliminar (iPhone) o Desinstalar (Android). En la computadora, abre la app y usa su menú.'],
    ],
    note: 'No es asesoría financiera ni legal. Privado por diseño: sin cuentas, y las herramientas funcionan en tu navegador.',
    back: '<a href="./">Todas las herramientas en español</a>',
  },
};

function card(a, t) {
  const es = t.lang === 'es' ? a.es || {} : {};
  const name = es.name || a.m.name;
  const what = t.lang === 'es' ? es.what : a.what;
  const open = t.up + (es.open || a.open).replace(/index\.html$/, '');
  return `      <li class="app"><img src="${esc(t.up + a.icon)}" width="64" height="64" alt="">
        <div><h3>${esc(name)}${es.englishOnly ? ` <span class="tag">${t.english}</span>` : ''}</h3><p>${esc(what)}</p>
        <p class="meta">${t.offline}</p></div>
        <a class="btn" href="${esc(open)}">${t.open}</a></li>`;
}

export function appsPage(lang) {
  const t = T[lang];
  const list = APPS.filter((a) => (lang === 'es' ? a.es : a.lang !== 'es')).map(readApp);
  const faq = { '@context': 'https://schema.org', '@type': 'FAQPage', mainEntity: t.faq.map(([q, a]) => ({ '@type': 'Question', name: q, acceptedAnswer: { '@type': 'Answer', text: a } })) };
  const hub = readFileSync(join(root, 'index.html'), 'utf8');
  const style = (/<style>[\s\S]*?<\/style>/.exec(hub) || [''])[0].replace('</style>', `.apps{list-style:none;padding:0;margin:16px 0 0;display:grid;gap:12px}
.app{display:grid;grid-template-columns:64px 1fr;gap:12px 14px;align-items:start;background:var(--card);border:1px solid var(--line);border-radius:16px;padding:16px}
.app img{border-radius:14px}.app h3{font-size:18px;margin:0}.app p{margin:4px 0 0;color:var(--muted);font-size:15px}
.app .meta{font-size:13px}.app .btn{grid-column:1/-1;justify-self:start}
@media (min-width:640px){.app{grid-template-columns:64px 1fr auto;align-items:center}.app .btn{grid-column:auto}}
.steps{display:grid;gap:12px;grid-template-columns:repeat(auto-fill,minmax(250px,1fr));margin-top:16px}
.steps div{background:var(--card);border:1px solid var(--line);border-radius:16px;padding:16px}.steps h3{margin:0 0 4px;font-size:17px}.steps p{margin:0;color:var(--muted);font-size:15px}
.steps .here{border:2px solid var(--gold)}
details{border-top:1px solid var(--line);padding:10px 0}summary{font-weight:700;cursor:pointer}
.tag{margin:0 0 0 6px;vertical-align:middle}
</style>`);
  return `<!doctype html>
<html lang="${t.lang}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>${esc(t.title)}</title>
<meta name="description" content="${esc(t.desc)}">
<meta name="theme-color" content="#0b1d13">
<link rel="manifest" href="${t.up}manifest.webmanifest">
<link rel="icon" href="${t.up}budget/icon-192.png">
<link rel="apple-touch-icon" href="${t.up}budget/icon-192.png">
<link rel="alternate" hreflang="en" href="${lang === 'en' ? '' : '../'}apps.html">
<link rel="alternate" hreflang="es" href="${lang === 'en' ? 'es/' : ''}apps.html">
<script type="application/ld+json">${JSON.stringify(faq)}</script>
${style}
</head>
<body>
<main>
  <p class="brand">${t.back} · ${t.other}</p>
  <h1>${esc(t.h1)}</h1>
  <p class="lede">${esc(t.lede)}</p>
  <p id="install-here" hidden><button id="install-btn" class="btn" type="button">${t.installHere}</button></p>
  <section aria-labelledby="h-how">
    <h2 id="h-how">${t.how}</h2>
    <div class="steps" id="steps">
${t.steps.map(([h, p], i) => `      <div data-os="${['ios', 'android', 'desktop'][i]}"><h3>${h}</h3><p>${p}</p></div>`).join('\n')}
    </div>
  </section>
  <section aria-labelledby="h-apps">
    <h2 id="h-apps">${t.apps}</h2>
    <ul class="apps" id="apps">
${list.map((a) => card(a, t)).join('\n')}
    </ul>
  </section>
  <section aria-labelledby="h-faq">
    <h2 id="h-faq">FAQ</h2>
${t.faq.map(([q, a]) => `    <details><summary>${esc(q)}</summary><p>${esc(a)}</p></details>`).join('\n')}
  </section>
</main>
<footer><p>${esc(t.note)}</p></footer>
<script type="module">
// Highlight the steps for this device, and offer the browser's own install prompt for the toolbox where it exists.
const ua = navigator.userAgent;
const os = /iPhone|iPad|iPod/.test(ua) || (/Macintosh/.test(ua) && navigator.maxTouchPoints > 1) ? 'ios' : /Android/.test(ua) ? 'android' : 'desktop';
document.querySelector(\`[data-os=\${os}]\`)?.classList.add('here');
let deferred = null;
addEventListener('beforeinstallprompt', (e) => { e.preventDefault(); deferred = e; document.getElementById('install-here').hidden = false; });
document.getElementById('install-btn').addEventListener('click', async () => { if (!deferred) return; deferred.prompt(); await deferred.userChoice.catch(() => null); deferred = null; document.getElementById('install-here').hidden = true; });
if ('serviceWorker' in navigator && (location.protocol === 'https:' || ['localhost', '127.0.0.1'].includes(location.hostname))) navigator.serviceWorker.register('${t.up}sw.js').catch(() => {});
</script>
</body>
</html>
`;
}

if (process.argv[1] === fileURLToPath(import.meta.url)) {
  for (const lang of ['en', 'es']) {
    writeFileSync(join(root, T[lang].file), appsPage(lang));
    console.log(`${T[lang].file}: ${APPS.filter((a) => (lang === 'es' ? a.es : a.lang !== 'es')).length} apps`);
  }
}
