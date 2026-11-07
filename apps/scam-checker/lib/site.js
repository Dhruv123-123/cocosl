// Website verdicts, shared by the link checker page and the browser extension. Pure functions so node can test them.
import { analyzeUrl, parseHost, analyzeMessage } from './scan.js';

// Big, legitimate hosts that contain a brand name but aren't that brand's site. The passive
// warning must almost never fire on a real site, so these are skipped.
const KNOWN_OK = ['amazonaws.com', 'cloudfront.net', 'googleusercontent.com', 'googleapis.com', 'gstatic.com', 'googlesyndication.com', 'blogspot.com', 'appspot.com', 'microsoftonline.com', 'azurewebsites.net', 'applestore.com', 'paypalobjects.com', 'fbcdn.net', 'cdninstagram.com', 'wikipedia.org', 'github.com', 'reddit.com'];

const onKnownOk = (host) => KNOWN_OK.some((d) => host === d || host.endsWith('.' + d));

/**
 * Judge the site in the address bar.
 * Returns { level: 'none' | 'official' | 'low' | 'medium' | 'high', host, issues }.
 * 'high' means a look-alike or brand-impersonating address with another red flag, the only case
 * the extension warns about without being asked.
 */
export function checkPage(url) {
  url = String(url || '').trim();
  // People paste "paypa1-login.com" without a scheme; treat it as a web address.
  if (url && !/^[a-z][a-z0-9+.-]*:/i.test(url) && /^[^\s/]+\.[a-z]{2,}/i.test(url)) url = `https://${url}`;
  let protocol;
  try { protocol = new URL(url).protocol; } catch { return { level: 'none', host: null, issues: [] }; }
  if (protocol !== 'http:' && protocol !== 'https:') return { level: 'none', host: null, issues: [] };
  const parsed = parseHost(url);
  if (!parsed) return { level: 'none', host: null, issues: [] };
  if (onKnownOk(parsed.host)) return { level: 'low', host: parsed.host, issues: [] };
  const r = analyzeUrl(url);
  if (r.official) return { level: 'official', host: r.host, issues: [] };
  const level = r.points >= 40 ? 'high' : r.points >= 20 ? 'medium' : 'low';
  return { level, host: r.host, issues: r.issues };
}

/** Badge text and colour for a page verdict, or null for no badge. */
export function badgeFor(level) {
  if (level === 'high') return { text: '!', color: '#c62828' };
  return null;
}

/** Text sent from a right-click: a link becomes its URL, a selection is trimmed and capped. */
export function menuText(info) {
  const raw = info.menuItemId === 'check-link' ? info.linkUrl : info.selectionText;
  return String(raw || '').trim().slice(0, 4000);
}

// Words on the page itself, checked only when the person opens the extension on that page.
// A page needs pressure (a deadline, a threat, "keep this secret") plus a scam pattern to be flagged,
// so ordinary shops and news pages with the word "urgent" stay quiet. Known official sites are skipped.
const PRESSURE = ['urgency', 'threat', 'secrecy'];
export function pageTextVerdict(text, url) {
  const page = checkPage(url);
  const host = page.host;
  if (page.level === 'none' || page.level === 'official' || (host && onKnownOk(host))) return { level: 'none', host, signals: [], categoryId: null };
  // Links in the page text are judged by the address bar check, not here.
  const plain = String(text || '').slice(0, 20000).replace(/\bhttps?:\/\/\S+/gi, ' ');
  const r = analyzeMessage(plain);
  const signals = r.signals.filter((x) => x.id !== 'money-amount' && x.id !== 'generic-greeting');
  const pressure = signals.some((x) => PRESSURE.includes(x.id));
  const pattern = signals.some((x) => !PRESSURE.includes(x.id));
  const level = pressure && pattern ? (r.score >= 60 ? 'high' : 'medium') : 'low';
  return { level, host, signals: level === 'low' ? [] : signals.slice(0, 4), categoryId: level === 'low' ? null : r.categoryId, score: r.score };
}

/**
 * The explainer for a scam type. explainers = { base, es?, map: { categoryId: slug | [enSlug, esSlug] } }.
 * Returns a full URL or null.
 */
export function explainerUrl(explainers, categoryId, lang = 'en') {
  if (!explainers || !categoryId) return null;
  const slug = explainers.map?.[categoryId];
  if (!slug) return null;
  const es = lang === 'es' && Array.isArray(slug) && slug[1] && explainers.es;
  const s = Array.isArray(slug) ? (es ? slug[1] : slug[0]) : slug;
  return /^[a-z0-9-]+$/.test(s) ? `${es ? explainers.es : explainers.base}${s}/` : null;
}
