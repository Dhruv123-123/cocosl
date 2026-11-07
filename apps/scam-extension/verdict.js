// Page and link verdicts for the browser extension. Pure functions so node can test them.
import { analyzeUrl, parseHost } from './lib/scan.js';

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
