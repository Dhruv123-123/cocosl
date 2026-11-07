// Moving cost calculator, English (moving-cost.html) and Spanish (costo-mudanza.html). Logic in lib/moving.js.
// Saved in this browser only. "Copy rows" pastes into the Moving Budget Sheet's "Planner paste" tab at B7.
import config from './config.js';
import { initTracking } from './lib/track.js';
import { CATEGORIES, KEYS, nameOf, estimates, summary, movingCsv, movingTsv, ASSUMPTIONS } from './lib/moving.js';
import { $, esc, store, download, live } from './page.js';

const es = document.documentElement.lang.startsWith('es');
const lang = es ? 'es' : 'en';
const loc = es ? 'es-US' : 'en-US';
const money = (n) => (Number(n) || 0).toLocaleString(loc, { style: 'currency', currency: 'USD', maximumFractionDigits: 0 });
const KEY = 'mms-moving-v1';
const FIELDS = ['estimate', 'actual', 'paid'];
const T = es ? {
  fields: { estimate: 'Estimado', actual: 'Real', paid: 'Pagado' },
  stats: ['Costo esperado', 'Ya pagado', 'Falta pagar', 'Te falta ahorrar'],
  filled: 'Listo: llenamos estimados para empezar. Cámbialos por cotizaciones reales.',
  owed: 'falta', over: (n) => `${money(n)} más de lo estimado`,
  copied: 'Copiado. Pégalo en la hoja.', copyFail: 'No se pudo copiar: selecciona el texto y cópialo.', file: 'presupuesto-de-mudanza.csv',
  local: 'Mudanza local.', long: (d, n) => `Mudanza larga: unos ${d} ${d === 1 ? 'día' : 'días'} de manejo y ${n} ${n === 1 ? 'noche' : 'noches'} de hotel.`,
} : {
  fields: { estimate: 'Estimate', actual: 'Actual', paid: 'Paid' },
  stats: ['Expected cost', 'Paid so far', 'Still to pay', 'Still to save'],
  filled: 'Done: starting estimates are filled in. Replace them with real quotes.',
  owed: 'left to pay', over: (n) => `${money(n)} over estimate`,
  copied: 'Copied. Paste it into the sheet.', copyFail: 'Couldn\'t copy: select the text and copy it.', file: 'moving-budget.csv',
  local: 'Local move.', long: (d, n) => `Long move: about ${d} ${d === 1 ? 'day' : 'days'} of driving and ${n} ${n === 1 ? 'night' : 'nights'} in a hotel.`,
};

let state = { trip: { miles: '', size: '1br', method: 'diy', cars: '1', people: '1', newRent: '', depositMonths: '1', overlapDays: '', storageMonths: '', daysOff: '', dayPay: '' }, saved: '', rows: {} };
try { const s = JSON.parse(store.get(KEY) || 'null'); if (s && s.rows && s.trip) state = { ...state, ...s, trip: { ...state.trip, ...s.trip } }; } catch { /* first visit */ }
const save = () => store.set(KEY, JSON.stringify(state));

const trip = $('#trip');
for (const [k, v] of Object.entries(state.trip)) if (trip.elements[k]) trip.elements[k].value = v;
$('#saved').value = state.saved;
$('#assume').textContent = es
  ? `Supuestos: gasolina a $${ASSUMPTIONS.gas} el galón, camión de ${ASSUMPTIONS.truckMpg} millas por galón, mudanceros locales a $${ASSUMPTIONS.moverRate} la hora, bodega a $${ASSUMPTIONS.storageMonth} al mes, hotel a $${ASSUMPTIONS.hotelNight} la noche, ${ASSUMPTIONS.bufferPct}% de colchón. Son reglas generales, no cotizaciones.`
  : `Assumptions: gas at $${ASSUMPTIONS.gas} a gallon, a truck at ${ASSUMPTIONS.truckMpg} mpg, local movers at $${ASSUMPTIONS.moverRate} an hour, storage at $${ASSUMPTIONS.storageMonth} a month, hotels at $${ASSUMPTIONS.hotelNight} a night and a ${ASSUMPTIONS.bufferPct}% buffer. Rules of thumb, not quotes.`;

$('#cats').innerHTML = CATEGORIES.map(([k]) => `<li class="wcat" data-key="${k}">
  <div class="fund-top"><h3 id="n-${k}">${esc(nameOf(k, lang))}</h3><b data-out="${k}"></b></div>
  <div class="wgrid mv">${FIELDS.map((f) => `<label>${T.fields[f]}<input type="number" min="0" step="1" inputmode="decimal" data-k="${k}" data-f="${f}" aria-describedby="n-${k}"></label>`).join('')}</div></li>`).join('');
const fill = () => { for (const el of document.querySelectorAll('[data-k]')) el.value = state.rows[el.dataset.k]?.[el.dataset.f] ?? ''; };

function render() {
  const s = summary(state);
  $('#stats').innerHTML = [s.expected, s.paid, s.owed, s.short].map((v, i) => `<div class="stat"><span>${T.stats[i]}</span><b>${money(v)}</b></div>`).join('');
  for (const r of s.rows) {
    const out = $(`[data-out="${r.key}"]`);
    out.textContent = r.diff !== null && r.diff < 0 ? T.over(-r.diff) : r.expected ? `${money(r.owed)} ${T.owed}` : '';
    out.className = r.diff !== null && r.diff < 0 ? 'neg' : '';
  }
  $('#t-rows').value = movingTsv(s, lang);
  $('#export').hidden = !s.expected;
  save();
}

trip.addEventListener('input', (e) => { if (e.target.name in state.trip) { state.trip[e.target.name] = e.target.value; save(); } });
trip.addEventListener('submit', (e) => {
  e.preventDefault();
  const est = estimates(state.trip);
  for (const k of KEYS) state.rows[k] = { ...(state.rows[k] || {}), estimate: est.values[k] };
  fill(); render();
  $('#fill-msg').textContent = `${est.local ? T.local : T.long(est.driveDays, est.nights)} ${T.filled}`;
});
$('#saved').addEventListener('input', (e) => { state.saved = e.target.value; render(); });
$('#cats').addEventListener('input', (e) => {
  const { k, f } = e.target.dataset;
  if (!k) return;
  state.rows[k] = { ...(state.rows[k] || {}), [f]: e.target.value };
  render();
});
$('#copy').addEventListener('click', async () => {
  try { await navigator.clipboard.writeText($('#t-rows').value); $('#copy-msg').textContent = T.copied; } catch { $('#t-rows').select(); $('#copy-msg').textContent = T.copyFail; }
});
$('#csv').addEventListener('click', () => download(T.file, movingCsv(summary(state), lang), 'text/csv'));

const p = config.movingTemplate;
if (p && live(p.url)) {
  $('#upsell').innerHTML = `<h3>${esc(es ? p.nameEs : p.name)} (${esc(p.price)})</h3><p>${esc(es ? p.pitchEs : p.pitch)}</p><a class="btn small" href="${esc(p.url)}">${es ? 'Ver la hoja' : 'Get the spreadsheet'}</a>`;
  $('#upsell').hidden = false;
}
fill();
render();
initTracking({ config, app: 'budget', page: es ? 'costo-mudanza' : 'moving-cost' });
