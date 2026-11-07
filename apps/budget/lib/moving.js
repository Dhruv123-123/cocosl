// Moving cost calculator (moving-cost.html, costo-mudanza.html). Pure functions, no DOM.
// Same 11 categories, in the same order, as the products thread's Moving Budget Sheet ($9) and Moving
// Planner printable: rows paste into the sheet's "Planner paste" tab at B7 as Category, Estimate, Actual, Paid.
//
// The starting estimates are rough rules of thumb so the page isn't blank, NOT quotes: every number in
// ASSUMPTIONS is shown on the page, and the page tells people to replace each estimate with real quotes.
// Re-check the assumptions once a year.

export const CATEGORIES = [
  ['movers', 'Movers or truck rental', 'Mudanceros o renta de camión'],
  ['fuel', 'Fuel and mileage', 'Gasolina y millas'],
  ['packing', 'Packing supplies', 'Material de empaque'],
  ['storage', 'Storage', 'Bodega'],
  ['travel', 'Travel and lodging', 'Viaje y hospedaje'],
  ['deposits', 'Deposits (new place)', 'Depósitos (nuevo hogar)'],
  ['overlap', 'Overlap rent', 'Renta doble'],
  ['utilities', 'Utility setup', 'Conexión de servicios'],
  ['cleaning', 'Cleaning', 'Limpieza'],
  ['timeoff', 'Time off work', 'Días sin trabajar'],
  ['buffer', 'Buffer', 'Colchón'],
];
export const KEYS = CATEGORIES.map((c) => c[0]);
export const nameOf = (k, lang = 'en') => { const c = CATEGORIES.find((x) => x[0] === k); return c ? c[lang === 'es' ? 2 : 1] : k; };

export const SIZES = { studio: 0, '1br': 1, '2br': 2, '3br': 3, '4br': 4 };
export const ASSUMPTIONS = {
  gas: 3.5, // $ a gallon
  truckMpg: 10, carMpg: 25,
  truckBase: [100, 130, 170, 220, 270], // DIY truck rental for a local move, by home size
  truckPerMile: 1.0, // one-way rental for long moves, $ a mile on top of the base
  containerBase: [700, 900, 1200, 1600, 2000], containerPerMile: 1.0,
  moverHours: [3, 4, 6, 8, 10], moverRate: 150, // local full service: crew of 2-3, $ an hour
  pounds: [2000, 3500, 5000, 7500, 10000], perPound: 0.75, longMovePounds: 100, // long-distance full service
  packing: [60, 100, 150, 220, 300],
  storageMonth: 150,
  milesPerDay: 500, hotelNight: 130, mealsPerPersonDay: 40,
  utilities: 150, cleaning: [120, 150, 200, 260, 320],
  bufferPct: 10,
  local: 100, // miles: at or under this is a local move
};

const num = (v, d = 0) => { const x = Number(String(v ?? '').replace(/[$,\s]/g, '')); return Number.isFinite(x) && x >= 0 ? x : d; };
const r0 = (n) => Math.round(n);
const r2 = (n) => Math.round((n + Number.EPSILON) * 100) / 100;

/**
 * input: { miles, size, method: 'diy' | 'container' | 'movers', cars, people, newRent, depositMonths,
 *          overlapDays, storageMonths, daysOff, dayPay }
 * Returns whole-dollar starting estimates for every category, plus how each was worked out.
 */
export function estimates(input, a = ASSUMPTIONS) {
  const miles = num(input.miles);
  const s = SIZES[input.size] ?? 1;
  const method = ['diy', 'container', 'movers'].includes(input.method) ? input.method : 'diy';
  const local = miles <= a.local;
  const cars = Math.round(num(input.cars, 1));
  const people = Math.max(1, Math.round(num(input.people, 1)));
  let movers;
  if (method === 'diy') movers = a.truckBase[s] + (local ? 0 : miles * a.truckPerMile);
  else if (method === 'container') movers = a.containerBase[s] + (local ? 0 : miles * a.containerPerMile);
  else movers = local ? a.moverHours[s] * a.moverRate : a.pounds[s] * a.perPound + miles * (a.pounds[s] / a.longMovePounds) * 0.01;
  const truckGas = method === 'diy' ? (miles / a.truckMpg) * a.gas : 0;
  const carGas = cars * (miles / a.carMpg) * a.gas;
  const driveDays = local ? 0 : Math.ceil(miles / a.milesPerDay);
  const nights = Math.max(0, driveDays - 1);
  const rent = num(input.newRent);
  const out = {
    movers: r0(movers),
    fuel: r0(truckGas + carGas),
    packing: a.packing[s],
    storage: r0(num(input.storageMonths) * a.storageMonth),
    travel: r0(nights * a.hotelNight + driveDays * people * a.mealsPerPersonDay),
    deposits: r0(rent * num(input.depositMonths, 1)),
    overlap: r0((rent / 30) * num(input.overlapDays)),
    utilities: a.utilities,
    cleaning: a.cleaning[s],
    timeoff: r0(num(input.daysOff) * num(input.dayPay)),
  };
  out.buffer = r0(Object.values(out).reduce((t, v) => t + v, 0) * (a.bufferPct / 100));
  return { values: out, local, driveDays, nights, method };
}

/** state.rows: { key: { estimate, actual, paid } }. Expected = actual if known, else the estimate. */
export function summary(state) {
  const rows = KEYS.map((k) => {
    const r = state.rows?.[k] || {};
    const estimate = num(r.estimate); const actual = num(r.actual); const paid = num(r.paid);
    const expected = actual || estimate;
    return { key: k, estimate, actual, paid, expected, owed: r2(Math.max(0, expected - paid)), diff: actual ? r2(estimate - actual) : null };
  });
  const sum = (f) => r2(rows.reduce((t, r) => t + r[f], 0));
  const saved = num(state.saved);
  return { rows, estimate: sum('estimate'), expected: sum('expected'), paid: sum('paid'), owed: sum('owed'), saved, short: r2(Math.max(0, sum('owed') - saved)) };
}

const csvCell = (s) => (/[",\n]/.test(String(s)) ? `"${String(s).replace(/"/g, '""')}"` : String(s));
export function movingCsv(sum, lang = 'en') {
  const head = lang === 'es' ? ['Categoría', 'Estimado', 'Real', 'Pagado', 'Falta pagar'] : ['Category', 'Estimate', 'Actual', 'Paid', 'Still to pay'];
  const lines = [head, ...sum.rows.map((r) => [nameOf(r.key, lang), r.estimate, r.actual || '', r.paid || '', r.owed])];
  lines.push(['Total', sum.estimate, '', sum.paid, sum.owed]);
  return `${lines.map((l) => l.map(csvCell).join(',')).join('\r\n')}\r\n`;
}
/** Tab-separated, no header, 11 rows: Category, Estimate, Actual, Paid. Pastes into the sheet's "Planner paste" tab at B7. */
export const movingTsv = (sum, lang = 'en') => sum.rows.map((r) => [nameOf(r.key, lang), r.estimate || '', r.actual || '', r.paid || ''].join('\t')).join('\n');
