// Options for embedded calculators (?embed=1). Pure functions, used by app.js and tests.
// Partners style the widget with data attributes that embed.js passes on as URL parameters:
//   accent=1f6feb   theme=light|dark|auto   radius=0-24   licence=KEY
// A licence (config.embed.licensees) removes the credit link and adds the partner's own call to action,
// but only when the page embedding the widget is on one of the licensee's domains (checked with the referrer).
// That check stops casual copying; it isn't DRM. Hosted white-label builds are the real protection.

const HEX = /^#?([0-9a-f]{6}|[0-9a-f]{3})$/i;

export function normalizeHex(v) {
  const m = HEX.exec(String(v || '').trim());
  if (!m) return null;
  const h = m[1].length === 3 ? m[1].split('').map((c) => c + c).join('') : m[1];
  return `#${h.toLowerCase()}`;
}

// WCAG relative luminance, then pick black or white text, whichever contrasts more.
export function luminance(hex) {
  const n = parseInt(hex.slice(1), 16);
  const ch = [(n >> 16) & 255, (n >> 8) & 255, n & 255].map((c) => { const s = c / 255; return s <= 0.03928 ? s / 12.92 : ((s + 0.055) / 1.055) ** 2.4; });
  return 0.2126 * ch[0] + 0.7152 * ch[1] + 0.0722 * ch[2];
}
export const contrast = (a, b) => { const [x, y] = [luminance(a), luminance(b)].sort((p, q) => q - p); return (x + 0.05) / (y + 0.05); };
export const inkFor = (hex) => (contrast(hex, '#0b1d13') >= contrast(hex, '#ffffff') ? '#0b1d13' : '#ffffff');

export function hostAllowed(referrer, domains = []) {
  let host;
  try { host = new URL(referrer).hostname.toLowerCase(); } catch { return false; }
  return domains.some((d) => { const x = String(d).toLowerCase().replace(/^\*\./, ''); return host === x || host.endsWith(`.${x}`); });
}

const safeUrl = (u) => (/^https:\/\/[^\s"'<>]+$/.test(String(u || '')) ? u : null);

/**
 * params: URLSearchParams of the embedded page. referrer: document.referrer. embedConfig: config.embed.
 * Returns what the page should apply.
 */
export function embedOptions(params, referrer, embedConfig = {}) {
  const accent = normalizeHex(params.get('accent'));
  const theme = ['light', 'dark'].includes(params.get('theme')) ? params.get('theme') : 'auto';
  const r = Number(params.get('radius'));
  const radius = params.has('radius') && Number.isFinite(r) ? Math.min(24, Math.max(0, Math.round(r))) : null;
  const key = String(params.get('licence') || params.get('license') || '').trim();
  const lic = key ? (embedConfig.licensees || []).find((l) => l.key === key) : null;
  const licensed = !!(lic && hostAllowed(referrer, lic.domains));
  const legacyUnbranded = params.get('brand') === '0' && !!embedConfig.allowUnbranded;
  const cta = licensed && lic.cta && safeUrl(lic.cta.url) && lic.cta.label ? { label: String(lic.cta.label).slice(0, 60), url: lic.cta.url } : null;
  return {
    accent, accentInk: accent ? inkFor(accent) : null, theme, radius,
    licensed, partner: licensed ? String(lic.name || '').slice(0, 60) : '', cta,
    showCredit: !(licensed || legacyUnbranded),
    licenceProblem: key && !licensed ? (lic ? 'domain' : 'key') : null,
  };
}
