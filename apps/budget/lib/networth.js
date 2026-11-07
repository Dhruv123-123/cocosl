// Net worth snapshot (networth.html). Pure functions, no DOM. Saved in the browser only.
// What you own minus what you owe, plus dated snapshots so you can see the trend.
import { isDay } from './dates.js';

export const ASSET_KINDS = { cash: 'Cash and savings', invest: 'Investments', retirement: 'Retirement (401(k), IRA)', home: 'Home or property', vehicle: 'Car or vehicle', other: 'Other things of value' };
export const DEBT_KINDS = { card: 'Credit cards', student: 'Student loans', car: 'Car loan', mortgage: 'Mortgage', medical: 'Medical debt', personal: 'Personal loan or BNPL', other: 'Other debt' };

const uid = () => Math.random().toString(36).slice(2, 10);
const cents = (n) => Math.round(Number(n) * 100) / 100;
const num = (v) => Number(String(v ?? '').replace(/[$,\s]/g, ''));

export const emptySheet = () => ({ version: 1, items: [], snapshots: [] });

export function loadSheet(json) {
  try {
    const s = typeof json === 'string' ? JSON.parse(json) : json;
    if (!s || !Array.isArray(s.items)) return emptySheet();
    return {
      version: 1,
      items: s.items.filter((i) => i && (i.side === 'asset' || i.side === 'debt') && Number.isFinite(i.value)),
      snapshots: (Array.isArray(s.snapshots) ? s.snapshots : []).filter((x) => x && isDay(x.date)),
    };
  } catch { return emptySheet(); }
}

export function addItem(sheet, { side, kind, name, value }) {
  if (side !== 'asset' && side !== 'debt') throw new Error('Pick something you own or owe.');
  const kinds = side === 'asset' ? ASSET_KINDS : DEBT_KINDS;
  const v = num(value);
  if (!Number.isFinite(v) || v < 0) throw new Error('Enter a value of $0 or more.');
  const item = { id: uid(), side, kind: kinds[kind] ? kind : 'other', name: String(name || '').trim().slice(0, 60) || kinds[kinds[kind] ? kind : 'other'], value: cents(v) };
  sheet.items.push(item);
  return item;
}

export function updateItem(sheet, id, value) {
  const item = sheet.items.find((i) => i.id === id);
  if (!item) throw new Error('Item not found.');
  const v = num(value);
  if (!Number.isFinite(v) || v < 0) throw new Error('Enter a value of $0 or more.');
  item.value = cents(v);
  return item;
}

export function removeItem(sheet, id) {
  sheet.items = sheet.items.filter((i) => i.id !== id);
}

export function totals(sheet) {
  const sum = (side) => cents(sheet.items.filter((i) => i.side === side).reduce((t, i) => t + i.value, 0));
  const assets = sum('asset');
  const debts = sum('debt');
  const byKind = (side, kinds) => Object.entries(kinds)
    .map(([k, label]) => ({ kind: k, label, total: cents(sheet.items.filter((i) => i.side === side && i.kind === k).reduce((t, i) => t + i.value, 0)) }))
    .filter((x) => x.total > 0);
  return {
    assets, debts, net: cents(assets - debts),
    // Debt-to-asset ratio: how much of what you own is matched by what you owe.
    debtRatio: assets > 0 ? Math.round((debts / assets) * 100) : null,
    liquid: cents(sheet.items.filter((i) => i.side === 'asset' && i.kind === 'cash').reduce((t, i) => t + i.value, 0)),
    assetsByKind: byKind('asset', ASSET_KINDS),
    debtsByKind: byKind('debt', DEBT_KINDS),
  };
}

/** Save today's totals. One snapshot per day: saving again the same day replaces it. */
export function takeSnapshot(sheet, date) {
  if (!isDay(date)) throw new Error('Bad date.');
  const t = totals(sheet);
  const snap = { date, assets: t.assets, debts: t.debts, net: t.net };
  sheet.snapshots = sheet.snapshots.filter((s) => s.date !== date).concat(snap).sort((a, b) => a.date.localeCompare(b.date));
  return snap;
}

export function removeSnapshot(sheet, date) {
  sheet.snapshots = sheet.snapshots.filter((s) => s.date !== date);
}

/** Change from the previous snapshot and from the first one. */
export function trend(sheet) {
  const s = sheet.snapshots;
  if (s.length < 2) return null;
  const last = s.at(-1);
  const prev = s.at(-2);
  const first = s[0];
  return { sincePrev: cents(last.net - prev.net), prevDate: prev.date, sinceFirst: cents(last.net - first.net), firstDate: first.date, count: s.length };
}

/** Plain-language notes on the numbers (no advice beyond general rules of thumb). */
export function notes(sheet, monthlyCosts = 0) {
  const t = totals(sheet);
  const out = [];
  if (!sheet.items.length) return out;
  if (t.net < 0) out.push('Your net worth is negative, which is common with student loans or a new car loan. Each payment that shrinks a debt raises it.');
  const cards = sheet.items.filter((i) => i.side === 'debt' && i.kind === 'card').reduce((a, i) => a + i.value, 0);
  if (cards > 0) out.push('Credit card debt usually has the highest interest rate, so paying it down raises your net worth fastest.');
  if (monthlyCosts > 0) {
    const months = Math.floor(t.liquid / monthlyCosts * 10) / 10;
    out.push(`Your cash and savings would cover about ${months} month${months === 1 ? '' : 's'} of essential costs.`);
  } else if (t.liquid === 0 && t.assets > 0) out.push('None of what you own is cash. A small emergency fund keeps a surprise bill off a credit card.');
  return out;
}

export function toCsv(sheet) {
  const q = (v) => `"${String(v ?? '').replace(/"/g, '""')}"`;
  const rows = [['Type', 'Category', 'Name', 'Value'], ...sheet.items.map((i) => [i.side === 'asset' ? 'Own' : 'Owe', (i.side === 'asset' ? ASSET_KINDS : DEBT_KINDS)[i.kind], i.name, i.value])];
  return rows.map((r) => r.map(q).join(',')).join('\r\n') + '\r\n';
}

const NW_LABELS = {
  en: { sheet: 'Net worth', title: 'Net worth', own: 'Own', owe: 'Owe', type: 'Type', category: 'Category', name: 'Name', value: 'Value', owned: 'Total owned', owed: 'Total owed', net: 'Net worth', history: 'Snapshots over time', date: 'Date', change: 'Change',
    note: 'From the net worth tracker. Update values in column D; totals are formulas. Add a row under Snapshots each month.' },
  es: { sheet: 'Patrimonio', title: 'Patrimonio neto', own: 'Tienes', owe: 'Debes', type: 'Tipo', category: 'Categoría', name: 'Nombre', value: 'Valor', owned: 'Total que tienes', owed: 'Total que debes', net: 'Patrimonio neto', history: 'Fotos en el tiempo', date: 'Fecha', change: 'Cambio',
    note: 'Del registro de patrimonio. Cambia los valores en la columna D; los totales son fórmulas. Agrega una fila en Fotos cada mes.' },
};

/**
 * A sheet spec for lib/xlsx.js: what you own and owe (with SUMIF totals), then snapshots with net worth
 * and change as formulas. Used on its own (networth.html) and inside the money dashboard workbook.
 */
export function netWorthSheet(sheet, { lang = 'en' } = {}) {
  const L = NW_LABELS[lang === 'es' ? 'es' : 'en'];
  const rows = [[{ v: L.title, s: 'title' }], [{ v: L.note, s: 'note' }], []];
  rows.push([L.type, L.category, L.name, L.value].map((v) => ({ v, s: 'head' })));
  const first = rows.length + 1;
  const items = [...sheet.items].sort((a, b) => (a.side === b.side ? 0 : a.side === 'asset' ? -1 : 1));
  for (const i of items) rows.push([i.side === 'asset' ? L.own : L.owe, (i.side === 'asset' ? ASSET_KINDS : DEBT_KINDS)[i.kind] || i.kind, i.name, { v: i.value, s: 'money' }]);
  // Totals cover the item rows only (inserting rows inside the range grows it), never the totals themselves.
  const last = Math.max(first, rows.length);
  const t = totals(sheet);
  rows.push([]);
  const ownedRow = rows.length + 1;
  rows.push([{ v: L.owned, s: 'totalText' }, null, null, { f: `SUMIF($A$${first}:$A$${last},"${L.own}",$D$${first}:$D$${last})`, v: t.assets, s: 'total' }]);
  rows.push([{ v: L.owed, s: 'totalText' }, null, null, { f: `SUMIF($A$${first}:$A$${last},"${L.owe}",$D$${first}:$D$${last})`, v: t.debts, s: 'total' }]);
  rows.push([{ v: L.net, s: 'totalText' }, null, null, { f: `D${ownedRow}-D${ownedRow + 1}`, v: t.net, s: 'total' }]);
  rows.push([]);
  rows.push([{ v: L.history, s: 'bold' }]);
  rows.push([L.date, L.owned, L.owed, L.net, L.change].map((v) => ({ v, s: 'head' })));
  sheet.snapshots.forEach((s, k) => {
    const r = rows.length + 1;
    const row = [{ d: s.date }, { v: s.assets, s: 'money' }, { v: s.debts, s: 'money' }, { f: `B${r}-C${r}`, v: s.net, s: 'money' }];
    if (k) row.push({ f: `D${r}-D${r - 1}`, v: cents(s.net - sheet.snapshots[k - 1].net), s: 'money' });
    rows.push(row);
  });
  return { name: L.sheet, rows, cols: [14, 26, 30, 16, 14] };
}
