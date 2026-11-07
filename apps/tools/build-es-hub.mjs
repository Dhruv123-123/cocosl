// Writes es/index.html: the Spanish landing page for every Spanish tool (for Dinero Simple to link to /es/).
// Calculator cards come from money-calculators/pages-es.mjs, so new Spanish calculators show up on rebuild.
// Run from apps/: node tools/build-es-hub.mjs   (Netlify runs it on deploy, before build-search.mjs)
import { readFileSync, writeFileSync, mkdirSync } from 'node:fs';
import { join, dirname } from 'node:path';
import { fileURLToPath } from 'node:url';
import { pagesEs } from '../money-calculators/pages-es.mjs';

const root = join(dirname(fileURLToPath(import.meta.url)), '..');
const esc = (s) => String(s).replace(/[&<>"]/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' })[c]);
const hub = readFileSync(join(root, 'index.html'), 'utf8');
const style = (/<style>[\s\S]*?<\/style>/.exec(hub) || [''])[0];

const SCAMS = [
  { u: '../scam-checker/es/', t: '¿Es una estafa?', d: 'Pega un mensaje, correo o DM sospechoso y revisa al instante las señales de estafa.', feature: true },
  { u: '../scam-checker/es/enlace/', t: 'Revisor de enlaces', d: '¿Este sitio web es confiable? Revisa un enlace antes de abrirlo: letras cambiadas, marcas falsas y dominios riesgosos.' },
  { u: '../scam-checker/es/estafas/', t: 'Guías de estafas comunes', d: 'USPS, peajes, IRS, Amazon, alertas de fraude, empleos falsos y más, explicados en español.' },
];
const SAVE = [
  { u: '../budget/bill-calendar/es.html', t: 'Calendario de pagos', d: 'Agrega cada recibo una vez y ve todas las fechas de pago del mes en un calendario. Márcalos al pagar y manda recordatorios a tu teléfono. Funciona sin internet.' },
  { u: '../budget/tablero-dinero.html', t: 'Tablero de dinero en hoja de cálculo', d: 'Sube el CSV de tu banco y descarga una hoja de cálculo para Google Sheets o Excel: cada gasto en su categoría y lo que entra, gastas y te sobra cada mes. Tu archivo no sale de tu navegador.' },
  { u: '../budget/reto-ahorro.html', t: 'Reto de ahorro de 52 semanas', d: 'Ahorra $1 más cada semana y junta $1,378 en un año, o pon tu propia meta. Marca cada semana, recibe recordatorios e imprime la tabla.' },
  { u: '../budget/plan-quincena.html', t: 'Presupuesto 50/30/20 y base cero', d: 'Escribe cuánto recibes en cada pago y arma tu presupuesto del mes con la regla 50/30/20 y un plan base cero donde cada dólar tiene un trabajo. Pasa directo al tablero de dinero.' },
  { u: '../budget/fondos-ahorro.html', t: 'Fondos de ahorro', d: 'Anota los gastos grandes que sabes que vienen, como el seguro del carro o las fiestas, y ve cuánto guardar cada mes y en cada cheque. Se pega en el Tablero de dinero Pro.' },
  { u: '../app/', t: 'App Money Made Simple', d: 'Las diez herramientas más usadas en una sola pantalla: presupuesto, salario neto, pagos, deudas, ahorro, dividir gastos y revisar estafas. Agrégala a tu teléfono y úsala sin internet y sin cuenta.' },
  { u: '../budget/dividir-gastos.html', t: 'Dividir gastos entre roomies o en pareja', d: 'Divide la renta, los servicios y el súper entre 2 a 6 personas: igual, según el ingreso o con tus porcentajes. Ve quién le debe a quién y copia un resumen para el chat del grupo.' },
  { u: '../budget/costo-mudanza.html', t: 'Costo de mudanza', d: 'Calcula cuánto te costará la mudanza: camión o mudanceros, gasolina, depósitos, renta doble, hotel y días sin trabajar. Cambia los estimados por cotizaciones y lleva lo que ya pagaste.' },
  { u: '../budget/presupuesto-boda.html', t: 'Presupuesto de boda', d: 'Escribe tu presupuesto total y tus invitados y reparte el dinero en 20 categorías. Anota cotizaciones, anticipos y pagos, el costo por invitado y cuánto ahorrar al mes.' },
  { u: '../budget/calendario-dinero.html', t: 'Calendario de dinero', d: 'Fechas de impuestos, Black Friday, el reinicio de enero y el reto de ahorro: una descarga agrega las fechas de dinero de los próximos 12 meses a tu calendario.' },
];
const calcs = pagesEs.map((p) => ({ u: `../money-calculators/es/${p.slug}/`, t: p.tile || p.h1, d: p.description }));
const card = (c) => `      <a class="card${c.feature ? ' feature' : ''}" href="${esc(c.u)}"><span class="tag free">Gratis</span><h3>${esc(c.t)}</h3><p>${esc(c.d)}</p></a>`;
const list = [...calcs, ...SAVE, ...SCAMS];
const itemList = { '@context': 'https://schema.org', '@type': 'ItemList', name: 'Herramientas de dinero gratis en español', itemListElement: list.map((c, i) => ({ '@type': 'ListItem', position: i + 1, name: c.t, url: c.u.replace(/^\.\.\//, '../') })) };

const html = `<!doctype html>
<html lang="es">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Herramientas de dinero gratis en español: calculadoras y verificador de estafas</title>
<meta name="description" content="Calculadoras de dinero gratis en español (sueldo neto por estado, deudas, ahorro, préstamos estudiantiles, rentar o comprar) y un verificador de estafas. Sin registro: lo que escribes se queda en tu navegador.">
<meta name="theme-color" content="#0b1d13">
<link rel="alternate" hreflang="en" href="../">
<link rel="alternate" hreflang="es" href="./">
<link rel="manifest" href="../manifest.webmanifest">
<link rel="icon" href="../budget/icon.svg" type="image/svg+xml">
<script type="application/ld+json">${JSON.stringify(itemList)}</script>
${style}
</head>
<body>
<main>
  <p class="brand"><a href="../" hreflang="en" lang="en">English</a></p>
  <h1>Herramientas gratis para tu dinero y tu seguridad</h1>
  <p class="lede">Calculadoras y un verificador de estafas, en español. Sin registro, y todo lo que escribes se queda en tu navegador.</p>
  <form id="search-form" class="search" role="search">
    <label for="q">Buscar en todas las herramientas</label>
    <input id="q" type="search" placeholder="Prueba: sueldo, deudas, estafa, préstamo" autocomplete="off" enterkeyhint="search">
    <p id="search-count" class="search-count" aria-live="polite"></p>
  </form>
  <div id="search-results" class="grid" hidden></div>
  <ul class="jump" aria-label="Ir a">
    <li><a href="#calculadoras">Calculadoras</a></li>
    <li><a href="#estafas">Estafas</a></li>
  </ul>

  <section id="calculadoras" aria-labelledby="h-calculadoras">
    <h2 id="h-calculadoras">Calculadoras de dinero</h2>
    <div class="grid">
${[...calcs, ...SAVE].map(card).join('\n')}
    </div>
  </section>

  <section id="estafas" aria-labelledby="h-estafas">
    <h2 id="h-estafas">Protégete de estafas</h2>
    <div class="grid">
${SCAMS.map(card).join('\n')}
    </div>
  </section>

  <aside id="plantillas" aria-labelledby="h-plantillas" class="products">
    <h2 id="h-plantillas">Plantillas de hoja de cálculo</h2>
    <div class="grid">
      <div class="card product" data-product="sheetTemplate" data-lang="es"><span class="tag soon">Muy pronto · $12</span><h3>Tablero de dinero Pro</h3><p>El tablero de dinero gratis, para usarlo cada mes: pega tus movimientos y ve tendencias de 12 meses, presupuesto vs real y fondos de ahorro, con gráficas. Google Sheets y Excel.</p><p class="tiny-note">Prueba ya el <a href="../budget/tablero-dinero.html">tablero de dinero gratis</a>.</p></div>
    </div>
  </aside>
</main>
<footer><p>No es asesoría financiera ni legal. Privado por diseño: sin cuentas, y las herramientas funcionan en tu navegador. <a href="apps.html">Instala las apps</a>.</p></footer>
<script type="module">
import config from '../budget/config.js';
import { showProducts } from '../products.js';
showProducts(config);
</script>
<script type="module" src="../hub-search.js"></script>
</body>
</html>
`;
mkdirSync(join(root, 'es'), { recursive: true });
writeFileSync(join(root, 'es/index.html'), html);
console.log(`es/index.html: ${list.length} tools`);
