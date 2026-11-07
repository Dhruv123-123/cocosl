// Bill splitter for roommates and couples (split-bills.html, dividir-gastos.html). Pure functions, no DOM.
// 2 to 6 people. Each bill is split equally, by income (everyone pays the same share of what they earn) or by
// custom percentages. Splits are in whole cents and always add up to the bill. Then the fewest payments that
// settle everyone up, and a CSV and a plain-text summary to send to the group.

export const MAX_PEOPLE = 6;
export const METHODS = ['equal', 'income', 'custom'];
const c = (n) => Math.round(n * 100);
const d = (n) => n / 100;
const amt = (v) => { const x = Number(String(v ?? '').replace(/[$,\s]/g, '')); return Number.isFinite(x) && x >= 0 ? Math.round(x * 100) / 100 : NaN; };

export function emptyGroup(n = 2) {
  return { v: 1, people: Array.from({ length: n }, () => ({ name: '', income: 0, pct: Math.round(100 / n) })), method: 'income', bills: [] };
}
export const label = (g, i, lang = 'en') => g.people[i]?.name || `${lang === 'es' ? 'Persona' : 'Person'} ${i + 1}`;

export function loadGroup(json) {
  try {
    const g = typeof json === 'string' ? JSON.parse(json) : json;
    if (!g || !Array.isArray(g.people) || g.people.length < 2 || !Array.isArray(g.bills)) return emptyGroup();
    const people = g.people.slice(0, MAX_PEOPLE).map((p) => ({ name: String(p?.name || '').slice(0, 30), income: amt(p?.income) || 0, pct: Number.isFinite(+p?.pct) ? Math.max(0, +p.pct) : 0 }));
    const bills = g.bills.filter((b) => b && b.name && Number.isFinite(+b.amount) && +b.amount > 0)
      .map((b) => ({ id: String(b.id || Math.random().toString(36).slice(2, 10)), name: String(b.name).slice(0, 60), amount: Math.round(+b.amount * 100) / 100, paidBy: Number.isInteger(b.paidBy) && b.paidBy >= 0 && b.paidBy < people.length ? b.paidBy : 0, method: METHODS.includes(b.method) ? b.method : 'group' }));
    return { v: 1, people, method: METHODS.includes(g.method) ? g.method : 'income', bills };
  } catch { return emptyGroup(); }
}

/** Weights for a method, as fractions that add up to 1. Falls back to equal when the inputs don't add up to anything. */
export function weights(g, method = g.method) {
  const n = g.people.length;
  const eq = Array(n).fill(1 / n);
  if (method === 'income') { const t = g.people.reduce((s, p) => s + (p.income || 0), 0); return t > 0 ? g.people.map((p) => (p.income || 0) / t) : eq; }
  if (method === 'custom') { const t = g.people.reduce((s, p) => s + (p.pct || 0), 0); return t > 0 ? g.people.map((p) => (p.pct || 0) / t) : eq; }
  return eq;
}

/** Split an amount in cents by weights, largest remainder first, so the parts add up exactly. Returns dollars. */
export function splitCents(amount, w) {
  const total = c(amount);
  const raw = w.map((x) => total * x);
  const out = raw.map(Math.floor);
  let left = total - out.reduce((a, b) => a + b, 0);
  const order = raw.map((x, i) => [x - Math.floor(x), i]).sort((a, b) => b[0] - a[0] || a[1] - b[1]);
  for (let k = 0; left > 0; k = (k + 1) % order.length, left--) out[order[k][1]] += 1;
  return out.map(d);
}

/** Fewest payments to settle balances (cents). Positive balance = is owed money. */
export function settleUp(balances) {
  const cred = []; const debt = [];
  balances.forEach((b, i) => { if (b > 0) cred.push([i, b]); else if (b < 0) debt.push([i, -b]); });
  const moves = [];
  cred.sort((a, b) => b[1] - a[1] || a[0] - b[0]); debt.sort((a, b) => b[1] - a[1] || a[0] - b[0]);
  let i = 0; let j = 0;
  while (i < debt.length && j < cred.length) {
    const x = Math.min(debt[i][1], cred[j][1]);
    moves.push({ from: debt[i][0], to: cred[j][0], amount: d(x) });
    debt[i][1] -= x; cred[j][1] -= x;
    if (!debt[i][1]) i++;
    if (!cred[j][1]) j++;
  }
  return moves;
}

export function summary(g) {
  const n = g.people.length;
  const share = Array(n).fill(0); const paid = Array(n).fill(0);
  const rows = g.bills.map((b) => {
    const m = b.method === 'group' || !b.method ? g.method : b.method;
    const parts = splitCents(b.amount, weights(g, m));
    parts.forEach((p, i) => { share[i] += c(p); });
    paid[b.paidBy] += c(b.amount);
    return { ...b, used: m, parts };
  });
  const total = rows.reduce((t, r) => t + c(r.amount), 0);
  const incomes = g.people.map((p) => p.income || 0);
  const balance = share.map((s, i) => paid[i] - s);
  return {
    rows, total: d(total), share: share.map(d), paid: paid.map(d), balance: balance.map(d),
    pctOfIncome: share.map((s, i) => (incomes[i] ? d(s) / incomes[i] : null)),
    moves: settleUp(balance),
    weights: weights(g),
  };
}

const csvCell = (s) => (/[",\n]/.test(String(s)) ? `"${String(s).replace(/"/g, '""')}"` : String(s));
const H = {
  en: { bill: 'Bill', amount: 'Amount', paid: 'Paid by', how: 'Split', total: 'Total', owes: 'owes', share: 'Share', pays: 'Paid', bal: 'Balance', m: { equal: 'Equal', income: 'By income', custom: 'Custom' } },
  es: { bill: 'Gasto', amount: 'Monto', paid: 'Pagó', how: 'División', total: 'Total', owes: 'le paga a', share: 'Le toca', pays: 'Pagó', bal: 'Saldo', m: { equal: 'Igual', income: 'Por ingreso', custom: 'A la medida' } },
};
export function splitCsv(g, s, lang = 'en') {
  const h = H[lang] || H.en; const names = g.people.map((_, i) => label(g, i, lang));
  const lines = [[h.bill, h.amount, h.paid, h.how, ...names]];
  for (const r of s.rows) lines.push([r.name, r.amount.toFixed(2), names[r.paidBy], h.m[r.used], ...r.parts.map((p) => p.toFixed(2))]);
  lines.push([h.total, s.total.toFixed(2), '', '', ...s.share.map((p) => p.toFixed(2))]);
  lines.push([h.pays, '', '', '', ...s.paid.map((p) => p.toFixed(2))]);
  lines.push([h.bal, '', '', '', ...s.balance.map((p) => p.toFixed(2))]);
  return `${lines.map((l) => l.map(csvCell).join(',')).join('\r\n')}\r\n`;
}

/** A short message to paste into the group chat. */
export function splitText(g, s, lang = 'en', fmt = (n) => `$${n.toFixed(2)}`) {
  const names = g.people.map((_, i) => label(g, i, lang));
  const es = lang === 'es';
  const out = [es ? `Gastos compartidos este mes: ${fmt(s.total)}` : `Shared bills this month: ${fmt(s.total)}`];
  names.forEach((nm, i) => out.push(`${nm}: ${fmt(s.share[i])}${s.pctOfIncome[i] != null ? ` (${Math.round(s.pctOfIncome[i] * 100)}% ${es ? 'de su ingreso' : 'of income'})` : ''}`));
  out.push(s.moves.length ? (es ? 'Para quedar a mano:' : 'To settle up:') : (es ? 'Todos están a mano.' : 'Everyone is square.'));
  for (const m of s.moves) out.push(`${names[m.from]} → ${names[m.to]}: ${fmt(m.amount)}`);
  return out.join('\n');
}
