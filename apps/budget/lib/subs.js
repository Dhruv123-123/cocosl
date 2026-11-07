// Subscription audit: the 30 most common US subscriptions, typical prices, how to cancel each one,
// and the yearly-total maths. Pure data and functions, no DOM.
//
// Prices are typical US list prices for the most common plan, checked in November 2026 against
// published price trackers. They change often, so the page pre-fills them and asks people to edit them
// to what they pay. Cancel steps and links are from each company's own help or account pages.

export const PRICES_CHECKED = 'November 2026';

// how: the steps; url: the company's own page; store: true when people often subscribe through
// Apple or Google Play, in which case the subscription has to be cancelled there.
export const SERVICES = [
  // Streaming
  { id: 'netflix', name: 'Netflix', group: 'tv', price: 19.99, per: 'month', keys: ['netflix'], url: 'https://help.netflix.com/en/node/407', how: 'Account > Manage membership > Cancel, then Finish cancellation. Deleting the app does not cancel.' },
  { id: 'hulu', name: 'Hulu', group: 'tv', price: 11.99, per: 'month', keys: ['hulu'], url: 'https://secure.hulu.com/account', how: 'Sign in on the website, open Account, and choose Cancel under Your subscription.', store: true },
  { id: 'disney', name: 'Disney+', group: 'tv', price: 12.49, per: 'month', keys: ['disney'], url: 'https://www.disneyplus.com/account', how: 'Account > Subscription > Cancel subscription. If it came in a bundle, cancel the bundle.', store: true },
  { id: 'hbomax', name: 'HBO Max', group: 'tv', price: 10.99, per: 'month', keys: ['hbo max', 'hbomax', 'max.com'], url: 'https://help.hbomax.com', how: 'Profile > Settings > Subscription > Manage subscription > Cancel. If you pay through a phone or TV provider, cancel with them.', store: true },
  { id: 'peacock', name: 'Peacock', group: 'tv', price: 12.99, per: 'month', keys: ['peacock'], url: 'https://www.peacocktv.com/account', how: 'Account > Plans & payment > Change plan > Cancel plan.', store: true },
  { id: 'paramount', name: 'Paramount+', group: 'tv', price: 8.99, per: 'month', keys: ['paramount'], url: 'https://www.paramountplus.com/account/', how: 'Account > Cancel subscription.', store: true },
  { id: 'appletv', name: 'Apple TV', group: 'tv', price: 14.99, per: 'month', keys: ['apple tv'], url: 'https://support.apple.com/en-us/118428', how: 'iPhone: Settings > your name > Subscriptions > Apple TV > Cancel. On a bank statement it shows as APPLE.COM/BILL.' },
  { id: 'prime', name: 'Amazon Prime', group: 'shop', price: 14.99, per: 'month', keys: ['amazon prime', 'prime membership', 'amzn prime', 'prime video'], url: 'https://www.amazon.com/gp/primecentral', how: 'Prime membership page > Manage membership > End membership. If you haven\'t used the benefits, you may get a refund.' },
  { id: 'ytpremium', name: 'YouTube Premium', group: 'tv', price: 15.99, per: 'month', keys: ['youtube premium', 'youtubepremium', 'youtube music'], url: 'https://www.youtube.com/paid_memberships', how: 'Purchases and memberships > Manage membership > Deactivate, then Continue to cancel.', store: true },
  { id: 'yttv', name: 'YouTube TV', group: 'tv', price: 82.99, per: 'month', keys: ['youtube tv', 'youtubetv'], url: 'https://tv.youtube.com/settings', how: 'Settings > Membership > Manage > Cancel membership. You can pause instead for a few weeks.' },
  // Music and audio
  { id: 'spotify', name: 'Spotify', group: 'music', price: 12.99, per: 'month', keys: ['spotify'], url: 'https://support.spotify.com/us/article/cancel-premium/', how: 'Sign in at spotify.com > Account > Manage your plan > Cancel Premium. You go back to free at the next billing date.' },
  { id: 'applemusic', name: 'Apple Music', group: 'music', price: 10.99, per: 'month', keys: ['apple music'], url: 'https://support.apple.com/en-us/118428', how: 'iPhone: Settings > your name > Subscriptions > Apple Music > Cancel. Check for an Apple One bundle too.' },
  { id: 'audible', name: 'Audible', group: 'music', price: 14.95, per: 'month', keys: ['audible'], url: 'https://www.audible.com', how: 'On the website, not the app: Account details > Cancel membership. Spend your credits first: unused ones go away when you cancel.' },
  // Storage, software and AI
  { id: 'icloud', name: 'iCloud+', group: 'apps', price: 2.99, per: 'month', keys: ['icloud'], url: 'https://support.apple.com/en-us/118428', how: 'iPhone: Settings > your name > iCloud > Manage storage > Change storage plan > Downgrade options. Clear space first so nothing stops backing up.' },
  { id: 'googleone', name: 'Google One', group: 'apps', price: 1.99, per: 'month', keys: ['google one', 'google storage', 'googleone'], url: 'https://one.google.com', how: 'Google One > Settings > Cancel membership. Over the free 15 GB, Gmail stops getting new mail, so clear space first.', store: true },
  { id: 'microsoft365', name: 'Microsoft 365', group: 'apps', price: 9.99, per: 'month', keys: ['microsoft 365', 'microsoft*365', 'msft 365', 'office 365'], url: 'https://account.microsoft.com/services', how: 'Microsoft account > Subscriptions > Manage > Cancel subscription (or turn off recurring billing).' },
  { id: 'chatgpt', name: 'ChatGPT Plus', group: 'apps', price: 20.0, per: 'month', keys: ['openai', 'chatgpt'], url: 'https://help.openai.com/en/articles/7232927-how-do-i-cancel-my-chatgpt-plus-subscription', how: 'In ChatGPT: your name > My plan > Manage my subscription > Cancel plan. If you subscribed in the iPhone or Android app, cancel there.', store: true },
  { id: 'adobe', name: 'Adobe', group: 'apps', price: 19.99, per: 'month', keys: ['adobe'], url: 'https://account.adobe.com/plans', how: 'Adobe account > Plans > Manage plan > Cancel your plan. Annual plans paid monthly can charge an early-cancel fee: check before you confirm.' },
  { id: 'canva', name: 'Canva Pro', group: 'apps', price: 15.0, per: 'month', keys: ['canva'], url: 'https://www.canva.com/settings/billing-and-plans', how: 'Settings > Billing & plans > the plan > Cancel subscription.', store: true },
  { id: 'dropbox', name: 'Dropbox', group: 'apps', price: 11.99, per: 'month', keys: ['dropbox'], url: 'https://www.dropbox.com/account/plan', how: 'On the website: Settings > Plan > Cancel plan. Over the free 2 GB, files stop syncing.' },
  // Games
  { id: 'xbox', name: 'Xbox Game Pass', group: 'games', price: 29.99, per: 'month', keys: ['xbox', 'game pass'], url: 'https://account.microsoft.com/services', how: 'Microsoft account > Subscriptions > Game Pass > Manage > Cancel subscription.' },
  { id: 'psplus', name: 'PlayStation Plus', group: 'games', price: 9.99, per: 'month', keys: ['playstation', 'sony interactive', 'psn'], url: 'https://www.playstation.com/en-us/support/', how: 'On the console: Settings > Users and accounts > Account > Payment and subscriptions > Subscriptions > Turn off auto-renew.' },
  { id: 'nintendo', name: 'Nintendo Switch Online', group: 'games', price: 19.99, per: 'year', keys: ['nintendo'], url: 'https://accounts.nintendo.com', how: 'Nintendo Account > Shop menu > Nintendo Switch Online > turn off automatic renewal.' },
  // Delivery and shopping memberships
  { id: 'dashpass', name: 'DoorDash DashPass', group: 'shop', price: 9.99, per: 'month', keys: ['dashpass', 'doordash dashpass'], url: 'https://help.doordash.com', how: 'In the app: Account > Manage DashPass > End subscription.', store: true },
  { id: 'uberone', name: 'Uber One', group: 'shop', price: 9.99, per: 'month', keys: ['uber one'], url: 'https://help.uber.com', how: 'In the Uber app: Account > Uber One > Manage membership > End membership.', store: true },
  { id: 'instacart', name: 'Instacart+', group: 'shop', price: 9.99, per: 'month', keys: ['instacart+', 'instacart plus', 'instacart membership'], url: 'https://www.instacart.com/help', how: 'Account > Instacart+ > Manage membership > End membership.' },
  { id: 'walmart', name: 'Walmart+', group: 'shop', price: 12.95, per: 'month', keys: ['walmart+', 'walmart plus', 'wmt plus'], url: 'https://www.walmart.com/account', how: 'Account > Walmart+ > Manage membership > Cancel membership.' },
  { id: 'costco', name: 'Costco membership', group: 'shop', price: 65, per: 'year', keys: ['costco membership', 'costco annual', 'costco renewal'], url: 'https://customerservice.costco.com', how: 'Ask at any warehouse membership counter or call member services. Costco refunds the membership fee if you\'re not satisfied.' },
  // Health and learning
  { id: 'planetfitness', name: 'Planet Fitness', group: 'health', price: 15.0, per: 'month', keys: ['planet fitness', 'pf black card'], url: 'https://www.planetfitness.com', how: 'Look for a cancel option in the app or website under Account. If there isn\'t one, cancel at your home club or by certified letter, and keep the receipt.' },
  { id: 'duolingo', name: 'Duolingo Super', group: 'health', price: 12.99, per: 'month', keys: ['duolingo'], url: 'https://support.duolingo.com', how: 'Most people subscribe in the app: cancel in Apple or Google Play subscriptions. Web subscribers: Settings > Super > Cancel.', store: true },
];

export const GROUPS = [
  ['tv', 'TV and video'],
  ['music', 'Music and audiobooks'],
  ['apps', 'Storage, software and AI'],
  ['games', 'Games'],
  ['shop', 'Shopping and delivery'],
  ['health', 'Fitness and learning'],
];

export const STORE_HELP = {
  apple: { name: 'Apple', url: 'https://support.apple.com/en-us/118428', how: 'iPhone: Settings > your name > Subscriptions. Anything billed as APPLE.COM/BILL is cancelled here.' },
  google: { name: 'Google Play', url: 'https://play.google.com/store/account/subscriptions', how: 'Google Play > Profile > Payments & subscriptions > Subscriptions.' },
};

const round2 = (n) => Math.round((n + Number.EPSILON) * 100) / 100;
export const yearlyOf = (price, per) => round2((Number(price) || 0) * (per === 'year' ? 1 : per === 'week' ? 52 : 12));

/**
 * picks: [{ price, per }] for each ticked or added subscription.
 * Returns { count, monthly, yearly, daily, tenYears }.
 */
export function totals(picks) {
  const ok = picks.filter((p) => Number(p.price) > 0);
  const yearly = round2(ok.reduce((s, p) => s + yearlyOf(p.price, p.per), 0));
  return { count: ok.length, yearly, monthly: round2(yearly / 12), daily: round2(yearly / 365), tenYears: round2(yearly * 10) };
}

/** The "aha" line comparing a guess (per month) with the real monthly total. Null when there's no guess. */
export function guessLine(guess, monthly) {
  const g = Number(guess);
  if (!(g > 0) || !(monthly > 0)) return null;
  const ratio = monthly / g;
  if (ratio >= 1.15) return { kind: 'more', ratio: Math.round(ratio * 10) / 10, gap: round2(monthly - g) };
  if (ratio <= 0.85) return { kind: 'less', ratio: Math.round(ratio * 10) / 10, gap: round2(g - monthly) };
  return { kind: 'close', ratio: 1, gap: round2(Math.abs(monthly - g)) };
}

/** Find the service a bank-statement charge belongs to (merchant key from recurring.js, or the raw note). */
export function matchService(text) {
  const s = String(text || '').toLowerCase();
  if (!s) return null;
  // Longest key first, so "youtube tv" wins over "youtube premium" style overlaps.
  let best = null;
  for (const sv of SERVICES) for (const k of sv.keys) if (s.includes(k) && (!best || k.length > best.k.length)) best = { sv, k };
  return best ? best.sv : null;
}

/** Charges billed by the app stores, which have to be cancelled there. */
export function storeFor(text) {
  const s = String(text || '').toLowerCase();
  if (/apple\.com\/bill|apple\.com bill|itunes/.test(s)) return 'apple';
  if (/google \*|google\*|google play/.test(s)) return 'google';
  return null;
}
