// Small date helpers on YYYY-MM-DD strings (local calendar days, no time zones).
export const isDay = (s) => typeof s === 'string' && /^\d{4}-\d{2}-\d{2}$/.test(s) && !Number.isNaN(Date.parse(`${s}T00:00:00Z`));
const toUtc = (s) => { const [y, m, d] = s.split('-').map(Number); return Date.UTC(y, m - 1, d); };
export const fromUtc = (ms) => new Date(ms).toISOString().slice(0, 10);
export const addDays = (s, n) => fromUtc(toUtc(s) + n * 86400000);
export const daysBetween = (a, b) => Math.round((toUtc(b) - toUtc(a)) / 86400000);
export function today(now = new Date()) {
  return `${now.getFullYear()}-${String(now.getMonth() + 1).padStart(2, '0')}-${String(now.getDate()).padStart(2, '0')}`;
}
/** Whole months from a to b (b's day before a's day doesn't count as a full month). */
export function monthsBetween(a, b) {
  const [ay, am, ad] = a.split('-').map(Number);
  const [by, bm, bd] = b.split('-').map(Number);
  return (by - ay) * 12 + (bm - am) - (bd < ad ? 1 : 0);
}
export function addMonths(s, n) {
  const [y, m, d] = s.split('-').map(Number);
  const last = new Date(Date.UTC(y, m - 1 + n + 1, 0)).getUTCDate();
  return fromUtc(Date.UTC(y, m - 1 + n, Math.min(d, last)));
}
export const prettyDay = (s) => (isDay(s) ? new Date(`${s}T12:00:00`).toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' }) : '');
