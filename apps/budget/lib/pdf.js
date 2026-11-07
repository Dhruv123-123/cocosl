// A tiny PDF writer for simple text reports (no library, works offline, nothing uploaded).
// US Letter pages, Helvetica and Helvetica-Bold (built into every PDF reader), WinAnsi text.
// lines: [{ text, right?, size?, bold?, gap?, rule? }]: `right` is drawn right-aligned on the same
// line (for amounts); `rule` draws a thin line; `gap` adds space before the line (points).

const W = 612;
const H = 792;
const M = 54;
const SWAP = { '‘': "'", '’': "'", '“': '"', '”': '"', '–': '-', '—': '-', '•': '-', '…': '...', ' ': ' ', '−': '-' };

/** Latin-1 safe text with PDF string escapes. */
export function pdfText(s) {
  return String(s ?? '')
    .replace(/[‘’“”–—•… −]/g, (c) => SWAP[c])
    .replace(/[^\x20-\xff]/g, '?')
    .replace(/[\\()]/g, (c) => `\\${c}`);
}

// Rough Helvetica width: good enough to wrap and right-align.
const width = (s, size) => [...String(s)].reduce((w, c) => w + (/[il.,:;'|!]/.test(c) ? 0.28 : /[mwMW@]/.test(c) ? 0.85 : /[A-Z0-9$#%&]/.test(c) ? 0.64 : 0.52), 0) * size;

export function wrap(text, size, max) {
  const words = String(text ?? '').split(/\s+/).filter(Boolean);
  const out = [];
  let line = '';
  for (const w of words) {
    const next = line ? `${line} ${w}` : w;
    if (line && width(next, size) > max) { out.push(line); line = w; } else line = next;
  }
  out.push(line);
  return out;
}

/** Build the PDF. Returns a Uint8Array. */
export function buildPdf(lines, { title = 'Report' } = {}) {
  const pages = [[]];
  let y = H - M;
  for (const l of lines) {
    const size = l.size || 11;
    const lead = size * 1.35;
    y -= l.gap || 0;
    if (l.rule) {
      if (y - 8 < M) { pages.push([]); y = H - M; }
      pages.at(-1).push(`0.6 w ${M} ${(y - 4).toFixed(1)} m ${W - M} ${(y - 4).toFixed(1)} l S`);
      y -= 10;
      continue;
    }
    const font = l.bold ? 'F2' : 'F1';
    const rightW = l.right ? width(l.right, size) + 12 : 0;
    const parts = wrap(l.text, size, W - 2 * M - rightW);
    parts.forEach((p, i) => {
      if (y - lead < M) { pages.push([]); y = H - M; }
      y -= lead;
      pages.at(-1).push(`BT /${font} ${size} Tf ${M} ${y.toFixed(1)} Td (${pdfText(p)}) Tj ET`);
      if (i === 0 && l.right) pages.at(-1).push(`BT /${font} ${size} Tf ${(W - M - width(l.right, size)).toFixed(1)} ${y.toFixed(1)} Td (${pdfText(l.right)}) Tj ET`);
    });
  }
  const objs = [];
  const add = (body) => { objs.push(body); return objs.length; };
  const catalog = add(null);
  const pagesId = add(null);
  const f1 = add('<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica /Encoding /WinAnsiEncoding >>');
  const f2 = add('<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica-Bold /Encoding /WinAnsiEncoding >>');
  const info = add(`<< /Title (${pdfText(title)}) /Producer (Money Made Simple) >>`);
  const kids = [];
  pages.forEach((ops, n) => {
    const footer = `BT /F1 8 Tf ${M} 30 Td (${pdfText(`${title} - page ${n + 1} of ${pages.length}`)}) Tj ET`;
    const stream = [...ops, footer].join('\n');
    const content = add(`<< /Length ${stream.length} >>\nstream\n${stream}\nendstream`);
    kids.push(add(`<< /Type /Page /Parent ${pagesId} 0 R /MediaBox [0 0 ${W} ${H}] /Resources << /Font << /F1 ${f1} 0 R /F2 ${f2} 0 R >> >> /Contents ${content} 0 R >>`));
  });
  objs[catalog - 1] = `<< /Type /Catalog /Pages ${pagesId} 0 R >>`;
  objs[pagesId - 1] = `<< /Type /Pages /Kids [${kids.map((k) => `${k} 0 R`).join(' ')}] /Count ${kids.length} >>`;

  let out = '%PDF-1.4\n%\xe2\xe3\xcf\xd3\n';
  const offsets = [];
  objs.forEach((body, i) => { offsets.push(out.length); out += `${i + 1} 0 obj\n${body}\nendobj\n`; });
  const xref = out.length;
  out += `xref\n0 ${objs.length + 1}\n0000000000 65535 f \n${offsets.map((o) => `${String(o).padStart(10, '0')} 00000 n \n`).join('')}`;
  out += `trailer\n<< /Size ${objs.length + 1} /Root ${catalog} 0 R /Info ${info} 0 R >>\nstartxref\n${xref}\n%%EOF\n`;
  const bytes = new Uint8Array(out.length);
  for (let i = 0; i < out.length; i++) bytes[i] = out.charCodeAt(i) & 0xff;
  return bytes;
}
