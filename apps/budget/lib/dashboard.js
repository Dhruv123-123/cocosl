// Money dashboard: sort a bank CSV's transactions into categories and lay out a monthly
// spreadsheet (Summary, Transactions, Categories) whose totals are live formulas, so changing a
// category in Google Sheets or Excel updates the summary. Pure functions; the page builds the file
// with lib/xlsx.js. Input transactions come from importBankCsv(): amount > 0 is money out.
import { merchantKey } from './recurring.js';

// key, English, Spanish, group, keyword rule. Order matters: the first match wins.
// Groups: income, spend, save (savings and investing), move (transfers, not counted as spending).
export const CATEGORIES = [
  { key: 'income', en: 'Income', es: 'Ingresos', group: 'income' },
  { key: 'transfers', en: 'Transfers & card payments', es: 'Transferencias y pagos de tarjeta', group: 'move',
    re: /payment thank ?you|\bcre?di?t ?crd\b|\bcrd\b.{0,12}(autopay|pmt|payment|epay)|(chase|citi|amex|american express|discover|capital one|barclays|synchrony|apple ?card|wells fargo) (card|crd|e-?payment|epay|pymt|pmt|autopay)|thank you for your payment|autopay pay|credit card (payment|pmt)|card ?payment|crd ?pmt|epay|online (banking )?transfer|transfer (to|from)|\bxfer\b|internal transfer|mobile transfer|zelle|venmo|cash ?app|paypal transfer|apple cash|ach transfer|pago de tarjeta|transferencia/ },
  { key: 'savings', en: 'Savings & investing', es: 'Ahorro e inversión', group: 'save',
    re: /to savings|savings transfer|vanguard|fidelity|schwab|robinhood|acorns|betterment|wealthfront|stash|\b401 ?k\b|\bira\b|treasury ?direct|ahorro/ },
  { key: 'fees', en: 'Bank fees & interest', es: 'Comisiones e intereses', group: 'spend',
    re: /\bfee\b|overdraft|\bnsf\b|insufficient funds|interest charge|finance charge|late charge|service charge|comisi[oó]n|cargo por/ },
  { key: 'cash', en: 'Cash (ATM)', es: 'Efectivo (cajero)', group: 'spend', re: /\batm\b|cash withdrawal|withdrawal at|cajero|retiro/ },
  { key: 'debt', en: 'Loans & debt', es: 'Préstamos y deudas', group: 'spend',
    re: /\bloan\b|navient|nelnet|mohela|aidvantage|sallie ?mae|edfinancial|affirm|klarna|afterpay|sezzle|ally (auto|financial)|toyota (financial|motor credit)|honda financial|santander consumer|capital one auto|carmax auto|pr[eé]stamo/ },
  { key: 'housing', en: 'Rent & housing', es: 'Renta y vivienda', group: 'spend',
    re: /\brent\b|mortgage|landlord|apartment|apts?\b|property management|\bhoa\b|homeowners assoc|rocket mortgage|mr\.? cooper|zillow rent|renta|alquiler|hipoteca/ },
  { key: 'utilities', en: 'Utilities & phone', es: 'Servicios y teléfono', group: 'spend',
    re: /verizon|at&t|\batt\b|t-mobile|tmobile|mint mobile|cricket|metro ?pcs|boost mobile|comcast|xfinity|spectrum|cox comm|frontier|optimum|electric|power|energy|edison|pg&e|duke energy|con ed|water|sewer|\bgas co|utility|utilities|internet|waste|trash/ },
  { key: 'insurance', en: 'Insurance', es: 'Seguros', group: 'spend',
    re: /insurance|geico|progressive|state farm|allstate|liberty mutual|farmers ins|usaa ins|lemonade|nationwide|root ins|seguro/ },
  { key: 'dining', en: 'Eating out & delivery', es: 'Comer fuera y a domicilio', group: 'spend',
    re: /restaurant|cafe|caf[eé]|coffee|starbucks|dunkin|mcdonald|burger|wendy|taco bell|chipotle|subway|chick-fil|popeyes|kfc|domino|pizza|panera|sonic|doordash|grubhub|uber ?eats|postmates|\bbar\b|grill|kitchen|diner|bakery|taqueria|restaurante/ },
  { key: 'groceries', en: 'Groceries', es: 'Supermercado', group: 'spend',
    re: /grocer|supermarket|safeway|kroger|aldi|trader joe|whole foods|walmart|wal-mart|wm supercenter|costco|sam'?s club|lidl|publix|h-e-b|\bheb\b|wegmans|albertsons|vons|ralphs|food lion|giant|stop & shop|meijer|winco|sprouts|smart & final|food 4 less|el super|vallarta|cardenas|fiesta mart|instacart|market|mercado|supermercado/ },
  { key: 'transport', en: 'Gas & transport', es: 'Gasolina y transporte', group: 'spend',
    re: /\buber\b|lyft|shell|chevron|exxon|mobil|\bbp\b|arco|valero|marathon|speedway|sunoco|circle k|wawa|sheetz|quiktrip|\bqt\b|76 |gas station|fuel|transit|metro|mta|bart|parking|park mobile|parkmobile|toll|e-?zpass|fastrak|sunpass|dmv|jiffy lube|autozone|o'?reilly auto|car wash|gasolina|estacionamiento/ },
  { key: 'health', en: 'Health & pharmacy', es: 'Salud y farmacia', group: 'spend',
    re: /pharmacy|cvs|walgreens|rite aid|doctor|medical|clinic|hospital|dental|dentist|vision|optometr|urgent care|labcorp|quest diag|kaiser|copay|farmacia|m[eé]dico|cl[ií]nica/ },
  { key: 'subscriptions', en: 'Subscriptions & streaming', es: 'Suscripciones y streaming', group: 'spend',
    re: /netflix|spotify|hulu|disney|hbo|max\.com|paramount|peacock|apple\.com|icloud|itunes|google \*|google one|youtube|prime video|amazon prime|audible|xbox|playstation|nintendo|adobe|dropbox|canva|chatgpt|openai|patreon|siriusxm|sirius|nytimes|planet fitness|gym|fitness|membership|subscription|suscripci[oó]n/ },
  { key: 'shopping', en: 'Shopping', es: 'Compras', group: 'spend',
    re: /amazon|amzn|target|best buy|ebay|etsy|home depot|lowe'?s|ikea|wayfair|tj ?maxx|marshalls|ross |old navy|gap |kohl'?s|macy'?s|nordstrom|shein|temu|dollar tree|dollar general|family dollar|five below|walgreens.com|apple store|nike|tienda/ },
  { key: 'fun', en: 'Fun & going out', es: 'Diversión y salidas', group: 'spend',
    re: /cinema|movie|theat(er|re)|amc |regal|ticketmaster|stubhub|eventbrite|steam|bowling|concert|museum|zoo|airbnb|hotel|airline|delta air|united air|american air|southwest|spirit air|jetblue|expedia|booking\.com|cine|boletos/ },
  { key: 'kids', en: 'Kids & school', es: 'Niños y escuela', group: 'spend', re: /daycare|child ?care|school|tuition|kindercare|bright horizons|guarder[ií]a|escuela|colegiatura/ },
  { key: 'giving', en: 'Gifts & giving', es: 'Regalos y donaciones', group: 'spend', re: /donation|charity|church|tithe|gofundme|red cross|united way|iglesia|donaci[oó]n|diezmo/ },
  { key: 'other', en: 'Other', es: 'Otros', group: 'spend' },
];
export const CAT = Object.fromEntries(CATEGORIES.map((c) => [c.key, c]));
const INCOME = /payroll|direct dep|dir dep|salary|paycheck|deposit|interest (paid|earned)|irs treas|tax ref|ssa treas|social security|unemployment|gusto|adp|paychex|dividend|n[oó]mina|dep[oó]sito|sueldo/;
const REFUND = /refund|return|reversal|reembolso|devoluci[oó]n|cashback|cash back/;

/** Category key for one transaction (amount > 0 is money out). overrides: { merchantKey: categoryKey }. */
export function categorize(note, amount, overrides = {}) {
  const key = merchantKey(note);
  if (overrides[key] && CAT[overrides[key]]) return overrides[key];
  const n = String(note || '').toLowerCase();
  // Savings first ("transfer to savings" is saving, not a plain transfer), then transfers.
  if (CAT.savings.re.test(n)) return 'savings';
  if (CAT.transfers.re.test(n)) return 'transfers';
  if (amount < 0) {
    if (REFUND.test(n)) { for (const c of CATEGORIES) if (c.group === 'spend' && c.re && c.re.test(n)) return c.key; return 'other'; }
    if (INCOME.test(n) || !CATEGORIES.some((c) => c.group === 'spend' && c.re && c.re.test(n))) return 'income';
  }
  for (const c of CATEGORIES) if (c.group === 'spend' && c.re && c.re.test(n)) return c.key;
  return 'other';
}

const r2 = (n) => Math.round(n * 100) / 100;

/**
 * Sort transactions and total them by month.
 * Returns { rows: [{date, month, note, merchant, amount (money in > 0), category}], months: ['YYYY-MM'...],
 *   byCat: {key: {month: total spent}}, totals: {month: {income, spend, save, left}}, uncategorized: [{merchant, count, total, sample}] }
 * Spending is shown as a positive number in byCat (money out), refunds lower it.
 */
export function buildDashboard(transactions, { overrides = {}, maxMonths = 12 } = {}) {
  const sorted = [...transactions].filter((t) => /^\d{4}-\d{2}-\d{2}$/.test(t.date)).sort((a, b) => a.date.localeCompare(b.date));
  const allMonths = [...new Set(sorted.map((t) => t.date.slice(0, 7)))];
  const months = allMonths.slice(-maxMonths);
  const keep = new Set(months);
  const rows = sorted.filter((t) => keep.has(t.date.slice(0, 7))).map((t) => ({
    date: t.date, month: t.date.slice(0, 7), note: t.note || '', merchant: merchantKey(t.note), amount: r2(-t.amount), category: categorize(t.note, t.amount, overrides),
  }));
  const byCat = Object.fromEntries(CATEGORIES.map((c) => [c.key, Object.fromEntries(months.map((m) => [m, 0]))]));
  for (const r of rows) byCat[r.category][r.month] = r2(byCat[r.category][r.month] + (r.category === 'income' ? r.amount : -r.amount));
  const totals = Object.fromEntries(months.map((m) => {
    const sum = (g) => r2(CATEGORIES.filter((c) => c.group === g).reduce((s, c) => s + byCat[c.key][m], 0));
    const income = sum('income'); const spend = sum('spend'); const save = sum('save');
    return [m, { income, spend, save, left: r2(income - spend - save) }];
  }));
  const other = new Map();
  for (const r of rows.filter((x) => x.category === 'other')) {
    const o = other.get(r.merchant) || { merchant: r.merchant, count: 0, total: 0, sample: r.note };
    o.count += 1; o.total = r2(o.total - r.amount); other.set(r.merchant, o);
  }
  const uncategorized = [...other.values()].sort((a, b) => Math.abs(b.total) - Math.abs(a.total));
  return { rows, months, byCat, totals, uncategorized, droppedMonths: allMonths.length - months.length };
}

const LABELS = {
  en: {
    summary: 'Summary', transactions: 'Transactions', categories: 'Categories', guide: 'How to use',
    title: 'Money dashboard', category: 'Category', avg: 'Monthly average', total: 'Total',
    income: 'Money in', spending: 'Spending', totalSpend: 'Total spending', saved: 'Saved & invested', left: 'Left over',
    rate: 'Share of money in kept (left over + saved)', notCounted: 'Not counted as spending', budget: 'Monthly budget', vsBudget: 'Average vs budget',
    date: 'Date', month: 'Month', description: 'Description', amount: 'Amount', type: 'Type',
    types: { income: 'Money in', spend: 'Spending', save: 'Saving', move: 'Transfer (not counted)' },
    tHead: 'Money in is positive, money out is negative. Change any Category and the Summary updates.',
    made: (d) => `Made on ${d} with the free Money Dashboard maker from Money Made Simple. Your bank file never left your browser.`,
    steps: [
      'Change a category: go to Transactions, click a cell in the Category column and pick from the list. The Summary recalculates.',
      'Add a category: type a new name at the bottom of the Categories list, then use it in Transactions. Add a row for it on the Summary by copying a category row.',
      'Set a budget: type a monthly amount in the Budget column on Categories. The Summary compares your average with it.',
      'Add next month: download a new CSV and make a fresh file, or paste new rows at the bottom of Transactions and add a month column to the Summary.',
      'Google Sheets: drive.google.com > New > File upload, then open the file with Google Sheets. Or in Sheets, File > Import > Upload.',
      'Transfers between your own accounts and credit card payments are listed but not counted, so nothing is counted twice.',
    ],
    file: 'money-dashboard',
  },
  es: {
    summary: 'Resumen', transactions: 'Movimientos', categories: 'Categorías', guide: 'Cómo usarlo',
    title: 'Tablero de dinero', category: 'Categoría', avg: 'Promedio mensual', total: 'Total',
    income: 'Dinero que entra', spending: 'Gastos', totalSpend: 'Total de gastos', saved: 'Ahorrado e invertido', left: 'Te sobra',
    rate: 'Parte de lo que entra que guardas (sobra + ahorro)', notCounted: 'No cuenta como gasto', budget: 'Presupuesto mensual', vsBudget: 'Promedio vs presupuesto',
    date: 'Fecha', month: 'Mes', description: 'Descripción', amount: 'Monto', type: 'Tipo',
    types: { income: 'Entra', spend: 'Gasto', save: 'Ahorro', move: 'Transferencia (no cuenta)' },
    tHead: 'Lo que entra es positivo, lo que sale es negativo. Cambia cualquier Categoría y el Resumen se actualiza.',
    made: (d) => `Hecho el ${d} con el Tablero de dinero gratis de Money Made Simple. El archivo de tu banco nunca salió de tu navegador.`,
    steps: [
      'Cambiar una categoría: ve a Movimientos, haz clic en la columna Categoría y elige de la lista. El Resumen se recalcula.',
      'Agregar una categoría: escribe el nombre nuevo al final de la lista de Categorías y úsalo en Movimientos. Copia una fila de categoría en el Resumen para verla ahí.',
      'Poner un presupuesto: escribe una cantidad mensual en la columna Presupuesto de Categorías. El Resumen la compara con tu promedio.',
      'Agregar otro mes: descarga un CSV nuevo y crea otro archivo, o pega las filas nuevas al final de Movimientos y agrega una columna de mes en el Resumen.',
      'Google Sheets: drive.google.com > Nuevo > Subir archivo, y ábrelo con Hojas de cálculo de Google. O en Sheets, Archivo > Importar > Subir.',
      'Las transferencias entre tus cuentas y los pagos de tarjeta aparecen pero no se cuentan, para no contar nada dos veces.',
    ],
    file: 'tablero-de-dinero',
  },
};
export const labels = (lang) => LABELS[lang === 'es' ? 'es' : 'en'];
export const catName = (key, lang) => (CAT[key] ? CAT[key][lang === 'es' ? 'es' : 'en'] : key);

/**
 * Sheet specs for lib/xlsx.js. The Summary's numbers are SUMIFS formulas over Transactions
 * (with the computed values cached), so the file stays a working template after download.
 */
export function workbookSheets(dash, { lang = 'en', made = new Date().toISOString().slice(0, 10), budgets = {} } = {}) {
  const L = labels(lang);
  const T = `'${L.transactions}'`; const C = `'${L.categories}'`;
  const n = dash.rows.length; const last = n + 2001; // room for rows pasted in later
  const amt = `${T}!$E$2:$E$${last}`; const cat = `${T}!$D$2:$D$${last}`; const mon = `${T}!$B$2:$B$${last}`;
  const used = CATEGORIES.filter((c) => c.key === 'income' || c.key === 'other' || dash.months.some((m) => dash.byCat[c.key][m] !== 0));
  const catRows = CATEGORIES.map((c) => [catName(c.key, lang), L.types[c.group], budgets[c.key] ? { v: budgets[c.key], s: 'money' } : null]);

  // Transactions sheet
  const tRows = [[L.date, L.month, L.description, L.category, L.amount].map((v) => ({ v, s: 'head' }))];
  for (const r of dash.rows) tRows.push([{ d: r.date }, r.month, r.note, catName(r.category, lang), { v: r.amount, s: 'money' }]);

  // Summary sheet
  const M = dash.months; const firstM = 1; const lastM = M.length; // month columns B..
  const avgCol = lastM + 1; const totCol = lastM + 2; const budCol = lastM + 3; const vsCol = lastM + 4;
  const colL = (i) => String.fromCharCode(65 + i); // months are capped at 12, so columns stay within A..Q
  const s = [];
  s.push([{ v: L.title, s: 'title' }]);
  s.push([{ v: L.made(made), s: 'note' }]);
  s.push([]);
  const headRow = s.length;
  s.push([{ v: L.category, s: 'head' }, ...M.map((m) => ({ v: m, s: 'head' })), { v: L.avg, s: 'head' }, { v: L.total, s: 'head' }, { v: L.budget, s: 'head' }, { v: L.vsBudget, s: 'head' }]);
  const rowFor = (c, sign) => {
    const r = s.length + 1; // 1-based row number of this row
    const cells = [catName(c.key, lang)];
    M.forEach((m, i) => cells.push({ f: `${sign}SUMIFS(${amt},${cat},$A${r},${mon},${colL(firstM + i)}$${headRow + 1})`, v: dash.byCat[c.key][m], s: 'money' }));
    const vals = M.map((m) => dash.byCat[c.key][m]);
    cells.push({ f: `AVERAGE(${colL(firstM)}${r}:${colL(lastM)}${r})`, v: r2(vals.reduce((a, b) => a + b, 0) / (M.length || 1)), s: 'money' });
    cells.push({ f: `SUM(${colL(firstM)}${r}:${colL(lastM)}${r})`, v: r2(vals.reduce((a, b) => a + b, 0)), s: 'money' });
    const look = `INDEX(${C}!$C$2:$C$${CATEGORIES.length + 40},MATCH($A${r},${C}!$A$2:$A$${CATEGORIES.length + 40},0))`;
    const budRef = `IFERROR(IF(${look}="","",${look}),"")`;
    cells.push({ f: budRef, v: budgets[c.key] || undefined, s: 'money' });
    if (c.group === 'spend') cells.push({ f: `IF(${colL(budCol)}${r}="","",${colL(avgCol)}${r}-${colL(budCol)}${r})`, v: budgets[c.key] ? r2(vals.reduce((a, b) => a + b, 0) / (M.length || 1) - budgets[c.key]) : undefined, s: 'money' });
    s.push(cells);
    return r;
  };
  const incomeRow = rowFor(CAT.income, '');
  s.push([]);
  s.push([{ v: L.spending, s: 'bold' }]);
  const spendRows = used.filter((c) => c.group === 'spend').map((c) => rowFor(c, '-'));
  const span = (fn) => [...M.map((_, i) => colL(firstM + i)), colL(avgCol), colL(totCol)].map(fn);
  const totalRow = (label, fOf, vOf) => { const cells = [{ v: label, s: 'totalText' }]; span((col) => cells.push({ f: fOf(col), v: vOf(col), s: 'total' })); s.push(cells); return s.length; };
  const valAt = (key) => (col) => { const i = col.charCodeAt(0) - 65 - firstM; const vals = M.map((m) => dash.totals[m][key]); if (i < M.length) return vals[i]; const sum = r2(vals.reduce((a, b) => a + b, 0)); return col === colL(avgCol) ? r2(sum / (M.length || 1)) : sum; };
  const spendTotal = totalRow(L.totalSpend, (col) => (spendRows.length ? `SUM(${col}${spendRows[0]}:${col}${spendRows.at(-1)})` : '0'), valAt('spend'));
  s.push([]);
  const saveRows = used.filter((c) => c.group === 'save').map((c) => rowFor(c, '-'));
  const saveTotal = totalRow(L.saved, (col) => (saveRows.length ? `SUM(${col}${saveRows[0]}:${col}${saveRows.at(-1)})` : '0'), valAt('save'));
  const leftRow = totalRow(L.left, (col) => `${col}${incomeRow}-${col}${spendTotal}-${col}${saveTotal}`, valAt('left'));
  const rateCells = [{ v: L.rate, s: 'bold' }];
  span((col) => { const inc = valAt('income')(col); const kept = r2(valAt('left')(col) + valAt('save')(col)); rateCells.push({ f: `IF(${col}${incomeRow}>0,(${col}${leftRow}+${col}${saveTotal})/${col}${incomeRow},"")`, v: inc > 0 ? Math.round((kept / inc) * 1000) / 1000 : undefined, s: 'pct' }); });
  s.push(rateCells);
  s.push([]);
  s.push([{ v: L.notCounted, s: 'note' }]);
  rowFor(CAT.transfers, '-');

  const summary = { name: L.summary, rows: s, cols: [30, ...M.map(() => 13), 16, 14, 16, 18], freeze: { rows: headRow + 1, cols: 1 } };
  const transactions = { name: L.transactions, rows: tRows, cols: [12, 10, 48, 30, 14], freeze: { rows: 1 }, filter: true,
    lists: [{ ref: `D2:D${Math.max(2, n + 200)}`, source: `${C}!$A$2:$A$${CATEGORIES.length + 40}` }] };
  const categories = { name: L.categories, rows: [[L.category, L.type, L.budget].map((v) => ({ v, s: 'head' })), ...catRows], cols: [34, 26, 18], freeze: { rows: 1 } };
  const guide = { name: L.guide, rows: [[{ v: L.title, s: 'title' }], [{ v: L.tHead, s: 'note' }], [], ...L.steps.map((t, i) => [`${i + 1}. ${t}`])], cols: [120] };
  return [summary, transactions, categories, guide];
}
