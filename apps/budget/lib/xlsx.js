// A small .xlsx writer for the browser and Node, with no dependencies. It writes an Office Open XML
// workbook inside a ZIP archive using the stored (uncompressed) method, so it needs no compression library.
// Google Sheets (File > Import), Excel, Numbers and LibreOffice all open it.
//
// buildXlsx([{ name, rows, cols, freeze, filter, lists }]) -> Uint8Array
//   rows:   arrays of cells. A cell is null, a string, a number, or an object:
//           { v, s }  a value with a style name (see STYLES)
//           { f, v, s }  a formula (no leading '='), with v as the cached result shown before recalculation
//           { d: 'YYYY-MM-DD', s }  a real date
//   cols:   column widths in characters, e.g. [12, 40, 14]
//   freeze: { rows: 1, cols: 1 } freezes the header row and/or first column
//   filter: true adds a filter on the header row over all rows
//   lists:  [{ ref: 'D2:D500', source: "'Categories'!$A$2:$A$20" }] dropdowns

const enc = new TextEncoder();

// ---------- ZIP (stored) ----------
const CRC = (() => { const t = new Uint32Array(256); for (let n = 0; n < 256; n++) { let c = n; for (let k = 0; k < 8; k++) c = c & 1 ? 0xedb88320 ^ (c >>> 1) : c >>> 1; t[n] = c >>> 0; } return t; })();
export function crc32(bytes) { let c = 0xffffffff; for (let i = 0; i < bytes.length; i++) c = CRC[(c ^ bytes[i]) & 255] ^ (c >>> 8); return (c ^ 0xffffffff) >>> 0; }

export function zipStored(files) {
  const parts = []; const central = []; let offset = 0;
  const DOS_TIME = 0; const DOS_DATE = ((2026 - 1980) << 9) | (1 << 5) | 1; // fixed, so builds are repeatable
  for (const { name, data } of files) {
    const nameBytes = enc.encode(name);
    const bytes = typeof data === 'string' ? enc.encode(data) : data;
    const crc = crc32(bytes);
    const local = new DataView(new ArrayBuffer(30));
    local.setUint32(0, 0x04034b50, true); local.setUint16(4, 20, true); local.setUint16(6, 0x0800, true); local.setUint16(8, 0, true);
    local.setUint16(10, DOS_TIME, true); local.setUint16(12, DOS_DATE, true); local.setUint32(14, crc, true);
    local.setUint32(18, bytes.length, true); local.setUint32(22, bytes.length, true); local.setUint16(26, nameBytes.length, true); local.setUint16(28, 0, true);
    parts.push(new Uint8Array(local.buffer), nameBytes, bytes);
    const cd = new DataView(new ArrayBuffer(46));
    cd.setUint32(0, 0x02014b50, true); cd.setUint16(4, 20, true); cd.setUint16(6, 20, true); cd.setUint16(8, 0x0800, true); cd.setUint16(10, 0, true);
    cd.setUint16(12, DOS_TIME, true); cd.setUint16(14, DOS_DATE, true); cd.setUint32(16, crc, true); cd.setUint32(20, bytes.length, true); cd.setUint32(24, bytes.length, true);
    cd.setUint16(28, nameBytes.length, true); cd.setUint32(42, offset, true);
    central.push(new Uint8Array(cd.buffer), nameBytes);
    offset += 30 + nameBytes.length + bytes.length;
  }
  const cdSize = central.reduce((n, p) => n + p.length, 0);
  const end = new DataView(new ArrayBuffer(22));
  end.setUint32(0, 0x06054b50, true); end.setUint16(8, files.length, true); end.setUint16(10, files.length, true);
  end.setUint32(12, cdSize, true); end.setUint32(16, offset, true);
  const all = [...parts, ...central, new Uint8Array(end.buffer)];
  const out = new Uint8Array(all.reduce((n, p) => n + p.length, 0));
  let p = 0; for (const a of all) { out.set(a, p); p += a.length; }
  return out;
}

// ---------- Workbook ----------
const xml = (s) => String(s).replace(/[&<>"]/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' })[c])
  // Characters XML 1.0 forbids (control codes from odd bank exports).
  .replace(/[\u0000-\u0008\u000b\u000c\u000e-\u001f￾￿]/g, '');

export const STYLES = { text: 0, head: 1, money: 2, date: 3, bold: 4, total: 5, totalText: 6, note: 7, title: 8, pct: 9 };

const STYLES_XML = `<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<styleSheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">
<numFmts count="3"><numFmt numFmtId="164" formatCode="&quot;$&quot;#,##0.00;[Red]-&quot;$&quot;#,##0.00"/><numFmt numFmtId="165" formatCode="yyyy-mm-dd"/><numFmt numFmtId="166" formatCode="0%"/></numFmts>
<fonts count="5"><font><sz val="11"/><name val="Arial"/></font><font><b/><sz val="11"/><name val="Arial"/></font><font><b/><sz val="11"/><color rgb="FFFFFFFF"/><name val="Arial"/></font><font><i/><sz val="10"/><color rgb="FF5B6B61"/><name val="Arial"/></font><font><b/><sz val="16"/><name val="Arial"/></font></fonts>
<fills count="4"><fill><patternFill patternType="none"/></fill><fill><patternFill patternType="gray125"/></fill><fill><patternFill patternType="solid"><fgColor rgb="FF12291B"/><bgColor indexed="64"/></patternFill></fill><fill><patternFill patternType="solid"><fgColor rgb="FFFFF4D6"/><bgColor indexed="64"/></patternFill></fill></fills>
<borders count="2"><border><left/><right/><top/><bottom/><diagonal/></border><border><left/><right/><top style="thin"><color rgb="FF999999"/></top><bottom/><diagonal/></border></borders>
<cellStyleXfs count="1"><xf numFmtId="0" fontId="0" fillId="0" borderId="0"/></cellStyleXfs>
<cellXfs count="10">
<xf numFmtId="0" fontId="0" fillId="0" borderId="0" xfId="0"/>
<xf numFmtId="0" fontId="2" fillId="2" borderId="0" xfId="0" applyFont="1" applyFill="1"/>
<xf numFmtId="164" fontId="0" fillId="0" borderId="0" xfId="0" applyNumberFormat="1"/>
<xf numFmtId="165" fontId="0" fillId="0" borderId="0" xfId="0" applyNumberFormat="1"/>
<xf numFmtId="0" fontId="1" fillId="0" borderId="0" xfId="0" applyFont="1"/>
<xf numFmtId="164" fontId="1" fillId="3" borderId="1" xfId="0" applyNumberFormat="1" applyFont="1" applyFill="1" applyBorder="1"/>
<xf numFmtId="0" fontId="1" fillId="3" borderId="1" xfId="0" applyFont="1" applyFill="1" applyBorder="1"/>
<xf numFmtId="0" fontId="3" fillId="0" borderId="0" xfId="0" applyFont="1"/>
<xf numFmtId="0" fontId="4" fillId="0" borderId="0" xfId="0" applyFont="1"/>
<xf numFmtId="166" fontId="0" fillId="0" borderId="0" xfId="0" applyNumberFormat="1"/>
</cellXfs>
<cellStyles count="1"><cellStyle name="Normal" xfId="0" builtinId="0"/></cellStyles>
</styleSheet>`;

/** 0 -> A, 25 -> Z, 26 -> AA */
export function colName(i) { let s = ''; i += 1; while (i > 0) { const m = (i - 1) % 26; s = String.fromCharCode(65 + m) + s; i = Math.floor((i - 1) / 26); } return s; }
export const ref = (col, row) => `${colName(col)}${row + 1}`;

/** Days since 1899-12-30, the spreadsheet date serial. */
export function dateSerial(iso) {
  const m = /^(\d{4})-(\d{2})-(\d{2})$/.exec(iso || '');
  return m ? (Date.UTC(+m[1], +m[2] - 1, +m[3]) - Date.UTC(1899, 11, 30)) / 86400000 : null;
}

/** Sheet names: at most 31 characters, none of []:*?/\ */
export const sheetName = (s) => String(s).replace(/[[\]:*?/\\]/g, ' ').slice(0, 31).trim() || 'Sheet';
/** Quote a sheet name for a formula: 'Name' with ' doubled. */
export const sheetRef = (s) => `'${sheetName(s).replace(/'/g, "''")}'`;

function sheetXml(sheet, strings) {
  const str = (s) => { if (!strings.map.has(s)) { strings.map.set(s, strings.list.length); strings.list.push(s); } return strings.map.get(s); };
  const rowsXml = sheet.rows.map((row, r) => {
    const cells = (row || []).map((cell, c) => {
      if (cell === null || cell === undefined || cell === '') return '';
      const o = typeof cell === 'object' ? cell : { v: cell };
      const s = STYLES[o.s] ?? 0;
      const at = `r="${ref(c, r)}"${s ? ` s="${s}"` : ''}`;
      if (o.f) {
        const cached = typeof o.v === 'number' && Number.isFinite(o.v) ? `<v>${o.v}</v>` : '';
        return `<c ${at}><f>${xml(o.f)}</f>${cached}</c>`;
      }
      if (o.d) { const n = dateSerial(o.d); return n === null ? `<c ${at} t="s"><v>${str(String(o.d))}</v></c>` : `<c ${at}${s ? '' : ' s="3"'}><v>${n}</v></c>`; }
      if (typeof o.v === 'number') return Number.isFinite(o.v) ? `<c ${at}><v>${o.v}</v></c>` : '';
      return `<c ${at} t="s"><v>${str(String(o.v))}</v></c>`;
    }).join('');
    return `<row r="${r + 1}">${cells}</row>`;
  }).join('');
  const width = Math.max(1, ...sheet.rows.map((r) => (r || []).length));
  const fr = sheet.freeze?.rows || 0; const fc = sheet.freeze?.cols || 0;
  const pane = fr || fc
    ? `<pane${fc ? ` xSplit="${fc}"` : ''}${fr ? ` ySplit="${fr}"` : ''} topLeftCell="${ref(fc, fr)}" activePane="${fr && fc ? 'bottomRight' : fr ? 'bottomLeft' : 'topRight'}" state="frozen"/>`
    : '';
  const cols = sheet.cols?.length ? `<cols>${sheet.cols.map((w, i) => `<col min="${i + 1}" max="${i + 1}" width="${w}" customWidth="1"/>`).join('')}</cols>` : '';
  const filter = sheet.filter && sheet.rows.length > 1 ? `<autoFilter ref="A1:${ref(width - 1, sheet.rows.length - 1)}"/>` : '';
  const lists = sheet.lists?.length
    ? `<dataValidations count="${sheet.lists.length}">${sheet.lists.map((l) => `<dataValidation type="list" allowBlank="1" showErrorMessage="0" sqref="${l.ref}"><formula1>${xml(l.source)}</formula1></dataValidation>`).join('')}</dataValidations>`
    : '';
  return `<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships"><dimension ref="A1:${ref(width - 1, Math.max(0, sheet.rows.length - 1))}"/><sheetViews><sheetView workbookViewId="0">${pane}</sheetView></sheetViews><sheetFormatPr defaultRowHeight="15"/>${cols}<sheetData>${rowsXml}</sheetData>${filter}${lists}<pageMargins left="0.5" right="0.5" top="0.6" bottom="0.6" header="0.3" footer="0.3"/></worksheet>`;
}

export function buildXlsx(sheets, { title = '' } = {}) {
  const names = sheets.map((s) => sheetName(s.name));
  if (new Set(names.map((n) => n.toLowerCase())).size !== names.length) throw new Error('Sheet names must be different');
  const strings = { list: [], map: new Map() };
  const sheetFiles = sheets.map((s, i) => ({ name: `xl/worksheets/sheet${i + 1}.xml`, data: sheetXml(s, strings) }));
  const shared = `<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<sst xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main" count="${strings.list.length}" uniqueCount="${strings.list.length}">${strings.list.map((s) => `<si><t xml:space="preserve">${xml(s)}</t></si>`).join('')}</sst>`;
  const files = [
    { name: '[Content_Types].xml', data: `<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Default Extension="xml" ContentType="application/xml"/><Override PartName="/xl/workbook.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet.main+xml"/>${sheets.map((_, i) => `<Override PartName="/xl/worksheets/sheet${i + 1}.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml"/>`).join('')}<Override PartName="/xl/styles.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.styles+xml"/><Override PartName="/xl/sharedStrings.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.sharedStrings+xml"/><Override PartName="/docProps/core.xml" ContentType="application/vnd.openxmlformats-package.core-properties+xml"/></Types>` },
    { name: '_rels/.rels', data: `<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="xl/workbook.xml"/><Relationship Id="rId2" Type="http://schemas.openxmlformats.org/package/2006/relationships/metadata/core-properties" Target="docProps/core.xml"/></Relationships>` },
    { name: 'docProps/core.xml', data: `<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<cp:coreProperties xmlns:cp="http://schemas.openxmlformats.org/package/2006/metadata/core-properties" xmlns:dc="http://purl.org/dc/elements/1.1/"><dc:title>${xml(title)}</dc:title><dc:creator>Money Made Simple</dc:creator></cp:coreProperties>` },
    { name: 'xl/workbook.xml', data: `<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<workbook xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships"><bookViews><workbookView/></bookViews><sheets>${names.map((n, i) => `<sheet name="${xml(n)}" sheetId="${i + 1}" r:id="rId${i + 1}"/>`).join('')}</sheets>${sheets.some((s) => s.filter) ? `<definedNames>${sheets.map((s, i) => (s.filter && s.rows.length > 1 ? `<definedName name="_xlnm._FilterDatabase" localSheetId="${i}" hidden="1">${xml(sheetRef(s.name))}!$A$1:$${colName(Math.max(1, ...s.rows.map((r) => (r || []).length)) - 1)}$${s.rows.length}</definedName>` : '')).join('')}</definedNames>` : ''}<calcPr calcId="191029" fullCalcOnLoad="1"/></workbook>` },
    { name: 'xl/_rels/workbook.xml.rels', data: `<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">${sheets.map((_, i) => `<Relationship Id="rId${i + 1}" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet" Target="worksheets/sheet${i + 1}.xml"/>`).join('')}<Relationship Id="rId${sheets.length + 1}" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/styles" Target="styles.xml"/><Relationship Id="rId${sheets.length + 2}" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/sharedStrings" Target="sharedStrings.xml"/></Relationships>` },
    { name: 'xl/styles.xml', data: STYLES_XML },
    ...sheetFiles,
    { name: 'xl/sharedStrings.xml', data: shared },
  ];
  return zipStored(files);
}
