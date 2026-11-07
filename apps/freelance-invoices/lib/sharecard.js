// GENERATED from apps/shared/ by tools/sync-shared.mjs. Edit the shared copy, not this one.
// Shareable result card: a 1080 x 1080 PNG drawn in the browser, so a result can be posted to
// Instagram, Facebook or a group chat. Nothing is uploaded. The card only ever shows what cardModel()
// puts on it (a total, a score, the site address): never names, merchants or anything typed in.
// Used by the subscription audit (budget/subscriptions.html) and the Scam Shield quiz (scam-checker/app/quiz.html).

export const SIZE = 1080;

export const BRANDS = {
  mms: { name: 'Money Made Simple', mark: 'MS', bg: '#0b1d13', ink: '#ffffff', accent: '#f2b134', soft: '#a7c4b2' },
  scam: { name: 'Scam Shield', mark: 'SS', bg: '#0d1b2a', ink: '#ffffff', accent: '#4fc3f7', soft: '#9fb3c8' },
};

const usd = (n) => (Number(n) || 0).toLocaleString('en-US', { style: 'currency', currency: 'USD', maximumFractionDigits: Number(n) >= 100 ? 0 : 2 });

/**
 * What the card says. kind 'subs': { yearly, count, showTotal }; kind 'quiz': { right, total }.
 * address: where people can try it (host + path, no query string).
 */
export function cardModel(kind, data = {}, address = '') {
  const url = String(address).replace(/^https?:\/\//, '').replace(/[?#].*$/, '').replace(/\/index\.html$/, '/').replace(/\.html$/, '');
  if (kind === 'subs') {
    const count = Math.max(0, Math.round(Number(data.count) || 0));
    const subs = `${count} subscription${count === 1 ? '' : 's'}`;
    return data.showTotal === false
      ? { brand: 'mms', kicker: 'My subscription audit', big: subs, line: 'Every one of them adds up. Find yours in 2 minutes.', cta: 'Free, private, no sign-up', url }
      : { brand: 'mms', kicker: 'My subscriptions cost', big: `${usd(data.yearly)} a year`, line: `${subs} · ${usd((Number(data.yearly) || 0) / 365)} a day`, cta: 'What do yours cost? Free, no sign-up', url };
  }
  if (kind === 'quiz') {
    const right = Math.max(0, Math.round(Number(data.right) || 0));
    const total = Math.max(1, Math.round(Number(data.total) || 10));
    const sharp = right / total >= 0.9;
    return { brand: 'scam', kicker: 'Scam or real?', big: `I spotted ${right} of ${total}`, line: sharp ? 'Think you can beat me?' : 'Scammers are good. Can you do better?', cta: 'Take the free 2-minute quiz', url };
  }
  throw new Error(`unknown card ${kind}`);
}

/** Split text into lines that fit maxWidth, using the context's current font. */
export function wrap(ctx, text, maxWidth) {
  const words = String(text).split(' ');
  const lines = [];
  let line = '';
  for (const w of words) {
    const test = line ? `${line} ${w}` : w;
    if (line && ctx.measureText(test).width > maxWidth) { lines.push(line); line = w; } else line = test;
  }
  if (line) lines.push(line);
  return lines;
}

/** Draw the card on a canvas (1080 x 1080). */
export function drawCard(canvas, m) {
  const b = BRANDS[m.brand];
  canvas.width = SIZE; canvas.height = SIZE;
  const ctx = canvas.getContext('2d');
  const font = (w, px) => `${w} ${px}px system-ui, -apple-system, "Segoe UI", Roboto, Arial, sans-serif`;
  ctx.fillStyle = b.bg; ctx.fillRect(0, 0, SIZE, SIZE);
  // corner glow
  const g = ctx.createRadialGradient(SIZE, 0, 40, SIZE, 0, 700);
  g.addColorStop(0, `${b.accent}55`); g.addColorStop(1, `${b.accent}00`);
  ctx.fillStyle = g; ctx.fillRect(0, 0, SIZE, SIZE);
  // brand mark
  ctx.fillStyle = b.accent;
  ctx.beginPath(); ctx.roundRect ? ctx.roundRect(80, 80, 96, 96, 24) : ctx.rect(80, 80, 96, 96); ctx.fill();
  ctx.fillStyle = b.bg; ctx.font = font(800, 40); ctx.textAlign = 'center'; ctx.textBaseline = 'middle';
  ctx.fillText(b.mark, 128, 130);
  ctx.textAlign = 'left'; ctx.textBaseline = 'alphabetic';
  ctx.fillStyle = b.ink; ctx.font = font(700, 40); ctx.fillText(b.name, 200, 142);
  // kicker, big number, line
  ctx.fillStyle = b.soft; ctx.font = font(600, 48); ctx.fillText(m.kicker, 80, 400);
  let px = 132;
  ctx.font = font(800, px);
  while (px > 64 && wrap(ctx, m.big, SIZE - 160).length > 2) { px -= 8; ctx.font = font(800, px); }
  ctx.fillStyle = b.accent;
  let y = 400 + px + 20;
  for (const l of wrap(ctx, m.big, SIZE - 160)) { ctx.fillText(l, 80, y); y += px * 1.05; }
  ctx.fillStyle = b.ink; ctx.font = font(500, 46);
  y += 20;
  for (const l of wrap(ctx, m.line, SIZE - 160)) { ctx.fillText(l, 80, y); y += 60; }
  // footer
  ctx.fillStyle = `${b.accent}`; ctx.fillRect(80, SIZE - 210, 120, 8);
  ctx.fillStyle = b.ink; ctx.font = font(700, 40); ctx.fillText(m.cta, 80, SIZE - 140);
  ctx.fillStyle = b.soft; ctx.font = font(500, 34);
  const shortUrl = m.url.length > 52 ? `${m.url.slice(0, 51)}…` : m.url;
  ctx.fillText(shortUrl, 80, SIZE - 88);
  return canvas;
}

/**
 * Make the PNG and share it (phone share sheet when the browser can share files) or download it.
 * Returns 'shared' | 'downloaded' | 'cancelled'.
 */
export async function shareCard(model, { filename = 'my-result.png', title = '', text = '', doc = globalThis.document, nav = globalThis.navigator } = {}) {
  const canvas = drawCard(doc.createElement('canvas'), model);
  const blob = await new Promise((r) => canvas.toBlob(r, 'image/png'));
  const File_ = globalThis.File;
  const file = File_ && blob ? new File_([blob], filename, { type: 'image/png' }) : null;
  const url = model.url ? `https://${model.url}` : undefined;
  if (file && nav?.canShare?.({ files: [file] })) {
    try { await nav.share({ files: [file], title, text: url ? `${text} ${url}`.trim() : text }); return 'shared'; }
    catch (e) { if (e?.name === 'AbortError') return 'cancelled'; }
  }
  const a = doc.createElement('a');
  a.href = URL.createObjectURL(blob);
  a.download = filename;
  doc.body.append(a); a.click(); a.remove();
  setTimeout(() => URL.revokeObjectURL(a.href), 4000);
  return 'downloaded';
}
