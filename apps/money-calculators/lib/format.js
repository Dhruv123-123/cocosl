export const money = (n, digits = 0) =>
  Number.isFinite(n)
    ? n.toLocaleString('en-US', { style: 'currency', currency: 'USD', maximumFractionDigits: digits, minimumFractionDigits: digits })
    : 'never';

export function duration(months, lang = 'en') {
  const es = lang === 'es';
  if (!Number.isFinite(months)) return es ? 'nunca (el pago no cubre los intereses)' : 'never (the payment does not cover the interest)';
  if (months === 0) return es ? 'ya lo logró' : 'already there';
  const y = Math.floor(months / 12);
  const m = months % 12;
  const parts = [];
  if (y) parts.push(es ? `${y} año${y === 1 ? '' : 's'}` : `${y} year${y === 1 ? '' : 's'}`);
  if (m) parts.push(es ? `${m} mes${m === 1 ? '' : 'es'}` : `${m} month${m === 1 ? '' : 's'}`);
  return parts.join(es ? ' y ' : ' ');
}

/** A link is live once the placeholder has been swapped for a real https URL. */
export const isLiveUrl = (url) => typeof url === 'string' && /^https:\/\//.test(url) && !/REPLACE_ME/i.test(url);

export const escapeHtml = (s) =>
  String(s).replace(/[&<>"']/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' })[c]);
