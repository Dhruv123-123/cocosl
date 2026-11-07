// Subscription finder: spot recurring charges in a list of transactions.
// Input: [{ date: 'YYYY-MM-DD', amount (spending > 0), note }] as produced by importBankCsv().

const KNOWN = ['netflix', 'spotify', 'hulu', 'disney', 'hbo', 'max.com', 'paramount', 'peacock', 'apple.com/bill', 'apple', 'icloud', 'google', 'youtube', 'amazon prime', 'prime video', 'audible', 'kindle', 'microsoft', 'xbox', 'playstation', 'nintendo', 'adobe', 'dropbox', 'canva', 'chatgpt', 'openai', 'claude', 'anthropic', 'patreon', 'onlyfans', 'twitch', 'duolingo', 'headspace', 'calm', 'peloton', 'planet fitness', 'gym', 'fitness', 'crunch', 'equinox', 'hellofresh', 'factor', 'doordash dashpass', 'dashpass', 'uber one', 'instacart', 'walmart+', 'costco', 'sirius', 'nytimes', 'new york times', 'wsj', 'washington post', 'medium', 'substack', 'linkedin', 'tinder', 'bumble', 'hinge', 'match.com', 'norton', 'mcafee', 'nordvpn', 'expressvpn', '1password', 'lastpass', 'verizon', 't-mobile', 'at&t', 'mint mobile', 'comcast', 'xfinity', 'spectrum', 'geico', 'progressive', 'state farm', 'lemonade', 'ring', 'adt', 'chewy'];

/** Turn "POS DEBIT 11/03 NETFLIX.COM 866-579-7172 CA #4821" into "netflix.com". */
export function merchantKey(note) {
  let s = String(note || '').toLowerCase();
  s = s.replace(/\b(pos|debit|credit|card|purchase|recurring|payment|pmt|ach|online|web|withdrawal|checkcard|visa|mastercard|preauthorized|autopay|bill pay|transaction)\b/g, ' ');
  s = s.replace(/\b\d{1,2}\/\d{1,2}(\/\d{2,4})?\b/g, ' ');          // dates
  s = s.replace(/\b\d{3}[-.\s]?\d{3}[-.\s]?\d{4}\b/g, ' ');           // phone numbers
  s = s.replace(/[#*]\s*\w*\d\w*/g, ' ');                            // #1234, *AB12CD reference codes
  s = s.replace(/\b[a-z]*\d[a-z\d]*\b/g, ' ');                        // tokens containing digits
  s = s.replace(/\s+\b(ca|ny|tx|fl|wa|il|us|usa|nv|ma|nj|pa|ga|oh|mi|nc|va|az|co|or)\b\s*$/g, ' '); // trailing state code
  s = s.replace(/[^a-z.&+' ]/g, ' ').replace(/\s+/g, ' ').trim();
  return s.split(' ').slice(0, 3).join(' ') || 'unknown';
}

const DAY = 86400000;
const toDay = (d) => Date.parse(d + 'T00:00:00Z') / DAY;
const median = (xs) => { const a = [...xs].sort((x, y) => x - y); const m = a.length >> 1; return a.length % 2 ? a[m] : (a[m - 1] + a[m]) / 2; };
const round2 = (n) => Math.round(n * 100) / 100;

const CADENCES = [
  { name: 'weekly', days: 7, min: 6, max: 8, perYear: 52 },
  { name: 'every 2 weeks', days: 14, min: 13, max: 16, perYear: 26 },
  { name: 'monthly', days: 30.4, min: 26, max: 35, perYear: 12 },
  { name: 'every 3 months', days: 91, min: 85, max: 98, perYear: 4 },
  { name: 'yearly', days: 365, min: 350, max: 380, perYear: 1 },
];

export const isKnownSubscription = (key) => KNOWN.some((k) => key.includes(k));

/**
 * Returns { subscriptions: [...], monthlyTotal, yearlyTotal }.
 * Each subscription: { name, key, cadence, amount, yearly, count, lastDate, nextDate, priceChange, confidence }.
 */
export function findRecurring(transactions, { today = null } = {}) {
  const groups = new Map();
  for (const t of transactions) {
    if (!(t.amount > 0) || !/^\d{4}-\d{2}-\d{2}$/.test(t.date)) continue;
    const key = merchantKey(t.note);
    if (!groups.has(key)) groups.set(key, { key, name: t.note, items: [] });
    groups.get(key).items.push(t);
  }
  const subs = [];
  for (const g of groups.values()) {
    const items = g.items.sort((a, b) => a.date.localeCompare(b.date));
    const known = isKnownSubscription(g.key);
    const amounts = items.map((i) => i.amount);
    const typical = median(amounts);
    if (items.length < 2) continue;
    const gaps = items.slice(1).map((it, i) => toDay(it.date) - toDay(items[i].date)).filter((d) => d > 0);
    if (!gaps.length) continue;
    const gap = median(gaps);
    const cadence = CADENCES.find((c) => gap >= c.min && gap <= c.max);
    if (!cadence) continue;
    // Regular gaps: most gaps within the cadence window.
    const regular = gaps.filter((d) => d >= cadence.min && d <= cadence.max).length / gaps.length;
    // Similar amounts: within 25% of the typical charge (prices rise; usage-based bills wobble).
    const steady = amounts.filter((a) => Math.abs(a - typical) <= typical * 0.25).length / amounts.length;
    if (regular < 0.6 || steady < 0.6) continue;
    // Weekly groceries or coffee look regular too: only count weekly/fortnightly when it's a known service
    // or the amount is identical every time.
    const identical = amounts.every((a) => Math.abs(a - amounts[0]) < 0.01);
    if (cadence.days < 20 && !known && !identical) continue;
    const latest = items.at(-1).amount;
    const first = items[0].amount;
    const last = items.at(-1).date;
    const next = new Date((toDay(last) + cadence.days) * DAY).toISOString().slice(0, 10);
    let confidence = 'likely';
    if (known || (identical && items.length >= 3)) confidence = 'very likely';
    else if (items.length === 2) confidence = 'possible';
    const stale = today && toDay(today) - toDay(last) > cadence.max * 1.5; // probably already cancelled
    subs.push({
      name: tidyName(g.name),
      key: g.key,
      cadence: cadence.name,
      amount: round2(latest),
      yearly: round2(latest * cadence.perYear),
      count: items.length,
      lastDate: last,
      nextDate: next,
      priceChange: latest > first + 0.009 ? round2(latest - first) : 0,
      confidence,
      stale: Boolean(stale),
    });
  }
  subs.sort((a, b) => b.yearly - a.yearly);
  const active = subs.filter((s) => !s.stale);
  const yearlyTotal = round2(active.reduce((s, x) => s + x.yearly, 0));
  return { subscriptions: subs, yearlyTotal, monthlyTotal: round2(yearlyTotal / 12) };
}

function tidyName(note) {
  const key = merchantKey(note);
  return key.replace(/\b\w/g, (c) => c.toUpperCase()).replace(/\.Com\b/, '.com');
}
