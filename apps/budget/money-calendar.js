// Money calendar download, English (money-calendar.html, ?brand=mms|1099|scam) and Spanish (calendario-dinero.html).
// Builds the .ics in the browser from lib/moneycal.js. Nothing is sent anywhere.
import config from './config.js';
import { initTracking } from './lib/track.js';
import { GROUPS, BRANDS, eventsFor, calendarFile } from './lib/moneycal.js';
import { $, esc, download } from './page.js';

const es = document.documentElement.lang.startsWith('es');
const loc = es ? 'es-US' : 'en-US';
const param = new URLSearchParams(location.search).get('brand');
const brandKey = es ? 'es' : BRANDS[param] && param !== 'es' ? param : 'mms';
const brand = BRANDS[brandKey];
const d = new Date();
const today = `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-${String(d.getDate()).padStart(2, '0')}`;
const day = (s) => new Date(`${s}T12:00:00`).toLocaleDateString(loc, { weekday: 'short', month: 'short', day: 'numeric', year: 'numeric' });

const NAMES = es
  ? { taxes: 'Impuestos', freelance: 'Impuestos de independientes (pagos trimestrales)', shopping: 'Black Friday y compras de fiestas', reset: 'Reinicio de enero y revisión de mitad de año', challenge: 'Reto de ahorro de 52 semanas', scams: 'Alertas de estafas de temporada', health: 'Inscripción al seguro médico' }
  : { taxes: 'Tax deadlines', freelance: 'Freelancer quarterly taxes', shopping: 'Black Friday and holiday shopping', reset: 'January money reset and mid-year check-in', challenge: '52-week savings challenge check-ins', scams: 'Seasonal scam alerts', health: 'Health insurance enrollment' };

$('#brand').textContent = brand.name;
$('#groups').innerHTML = GROUPS.map((g) => `<label class="check"><input type="checkbox" name="g" value="${g}"${brand.groups.includes(g) ? ' checked' : ''}> ${NAMES[g]}</label>`).join('');

const chosen = () => [...document.querySelectorAll('[name=g]:checked')].map((i) => i.value);
function render() {
  const events = eventsFor({ groups: chosen(), lang: brand.lang, from: today });
  $('#count').textContent = es ? `${events.length} fechas en los próximos 12 meses` : `${events.length} dates in the next 12 months`;
  $('#preview').innerHTML = events.map((e) => `<li><b>${day(e.date)}</b> ${esc(e.title)}<span class="tiny">${esc(e.description)}</span></li>`).join('');
  $('#download').disabled = !events.length;
}
$('#groups').addEventListener('change', render);
$('#download').addEventListener('click', () => {
  const { ics } = calendarFile(brandKey, { groups: chosen(), from: today });
  download(es ? 'calendario-de-dinero.ics' : `${brand.name.toLowerCase().replace(/\W+/g, '-')}-money-calendar.ics`, ics, 'text/calendar');
  $('#done').textContent = es ? 'Listo. Abre el archivo para agregar las fechas a tu calendario.' : 'Done. Open the file to add the dates to your calendar.';
});
render();
initTracking({ config, app: 'budget', page: es ? 'calendario-dinero' : `money-calendar-${brandKey}` });
