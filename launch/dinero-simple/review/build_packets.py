"""Build the two hand-off review packets for Dinero Simple: one for the native Spanish reviewer (everything in Spanish)
and one for the immigration attorney (every passage that touches the ITIN, immigration status or notarios).
Each is a single numbered PDF with a comment column, so Dhruv can hand each one off in one go.

    python3 launch/dinero-simple/review/build_packets.py          # dist/*.html + REVIEW_PACKETS.md
    python3 launch/dinero-simple/review/build_packets.py --pdf    # also dist/*.pdf (Chromium via Playwright)

Inputs are the committed sources (content-*.json, the site's content/, the guides, the welcome sequence, the brand's
bios) plus the built product/printable HTML in */dist/ (run the product, workshop, mayores and primer-ano builders
first; anything missing is listed in REVIEW_PACKETS.md, not silently skipped).

Lines that repeat across many posts (the CTA, the "not advice" line, series taglines) are reviewed once, in the
"Frases que se repiten" section, and shown as [R-n] wherever they appear.
"""
from __future__ import annotations

import html
import json
import os
import re
import subprocess
import sys
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
DS = HERE.parent
ROOT = DS.parents[1]
SITE = ROOT / "sites" / "dinero-simple" / "content"
DIST = HERE / "dist"
esc = html.escape

# Review speeds used for the hour estimates (a range: careful pass .. quick pass).
NATIVE_WPH = (1000, 1500)      # native-speaker edit of marketing and how-to copy, words per hour
ATTORNEY_WPH = (1500, 2500)    # legal-accuracy read of short passages, words per hour
ATTORNEY_SETUP_H = 1.0         # reading the brief and the claims list once

IMMIGRATION_RE = re.compile(r"\bitin\b|migratori|inmigraci|notari|uscis|\bvisas?\b|deport|consular|consulado|"
                            r"detenid|\bfianza|asilo|green card|residencia|ciudadan|acreditad|w-7", re.I)
CHUNK_WORDS = 170
REPEAT_MIN = 4

# Parts, in go-live order: (part title, [(label, kind, source)])
CONTENT_PARTS = [
    ("Parte 1 · Antes de lanzar", ["content.json", "content-month-1.json", "content-holiday-2026.json",
                                   "content-reto-ahorro-2026.json"]),
    ("Parte 2 · Enero y febrero de 2027", ["content-newyear-2027.json", "content-month-2.json", "content-estafas.json",
                                           "content-month-3.json"]),
    ("Parte 3 · Marzo y abril de 2027", ["content-month-4.json", "content-envios-2027.json",
                                         "content-credito-sin-ss-2027.json", "content-alertas-inmigrantes-2027.json",
                                         "content-month-5.json"]),
    ("Parte 4 · Mayo a septiembre de 2027", ["content-month-6.json", "content-month-7.json", "content-month-8.json",
                                             "content-month-9.json", "content-month-10.json"]),
]


def strip_html(s: str) -> str:
    s = re.sub(r"(?is)<(script|style|svg)[^>]*>.*?</\1>", " ", s)
    s = re.sub(r"(?i)<br\s*/?>|</(p|li|h[1-6]|div|tr|section)>", "\n", s)
    s = re.sub(r"<[^>]+>", " ", s)
    s = html.unescape(s)
    return "\n".join(" ".join(line.split()) for line in s.splitlines() if line.strip())


def strip_md(s: str) -> str:
    if s.startswith("---"):
        end = s.find("\n---", 3)
        front, s = s[3:end], s[end + 4:]
        keep = [line.split(":", 1)[1].strip() for line in front.splitlines()
                if re.match(r"(title|seo_title|short|subject|preheader|description|buy_label|guarantee|includes):", line)]
        s = "\n".join(keep) + "\n\n" + s
    s = strip_html(s) if "<" in s else s
    s = re.sub(r"!\[[^\]]*\]\([^)]*\)", "", s)
    s = re.sub(r"\[([^\]]+)\]\([^)]*\)", r"\1", s)
    s = re.sub(r"[*_`#>]+", "", s)
    return "\n".join(line.strip() for line in s.splitlines() if line.strip())


def chunks(text: str) -> list[str]:
    out, cur = [], []
    for para in [p for p in re.split(r"\n+", text) if p.strip()]:
        if cur and sum(len(x.split()) for x in cur) + len(para.split()) > CHUNK_WORDS:
            out.append("\n".join(cur))
            cur = []
        cur.append(para)
    if cur:
        out.append("\n".join(cur))
    return out


def item_text(it: dict) -> str:
    s = it["script"]
    lines = [f"Título: {s['title']}"]
    if s.get("thumbnail_text"):
        lines.append(f"Miniatura: {s['thumbnail_text']}")
    for g in s["segments"]:
        lines.append(f"[{g.get('heading', '')}] En pantalla: {g['on_screen_text']}")
        if g["narration"].strip() and g["narration"].strip() != g["on_screen_text"].strip():
            lines.append(f"Voz: {g['narration']}")
    lines.append("Texto de la publicación:")
    lines += [p for p in s["caption"].split("\n") if p.strip()]
    if s.get("description") and s["description"].strip() not in s["caption"]:
        lines += ["Descripción:"] + [p for p in s["description"].split("\n") if p.strip()]
    return "\n".join(lines)


class Packets:
    def __init__(self):
        self.entries: list[dict] = []     # {part, title, source, text, claims}
        self.missing: list[str] = []

    def add(self, part: str, title: str, source: str, text: str, claims: list[str] | None = None):
        if text.strip():
            self.entries.append({"part": part, "title": title, "source": source, "text": text, "claims": claims or []})

    def add_file(self, part: str, title: str, path: Path, kind: str = "md"):
        if not path.exists():
            self.missing.append(str(path.relative_to(ROOT)))
            return
        raw = path.read_text()
        text = strip_html(raw) if kind == "html" else strip_md(raw)
        self.add(part, title, str(path.relative_to(ROOT)), text)

    def add_pdf(self, part: str, title: str, path: Path):
        if not path.exists():
            self.missing.append(str(path.relative_to(ROOT)))
            return
        text = subprocess.run(["pdftotext", "-layout", str(path), "-"], capture_output=True, text=True).stdout
        text = "\n".join(" ".join(line.split()) for line in text.splitlines() if line.strip())
        self.add(part, title, str(path.relative_to(ROOT)), text)


FREEBIE = ROOT / "sites" / "dinero-simple" / "lead-magnet" / "tu-dinero-en-orden-en-7-dias.html"
SITE_JSON = ROOT / "sites" / "dinero-simple" / "site.json"
SITE_TEXT_KEYS = ("tagline", "description", "pillars", "email", "lead_magnet", "footer_links", "disclaimer",
                  "ai_disclosure", "ui", "free_tools")


def _strings(x, skip=("base", "path", "posts", "pillars", "provider", "action", "email_field", "file")):
    if isinstance(x, str):
        if x.strip() and not x.startswith(("/", "http")):
            yield x
    elif isinstance(x, dict):
        for k, v in x.items():
            if not k.startswith("_") and k not in skip:
                yield from _strings(v, skip)
    elif isinstance(x, list):
        for v in x:
            yield from _strings(v, skip)


def add_site_text(P: "Packets", part: str, tools: bool = True) -> None:
    """The words the site template itself shows (site.json): tagline, buttons, form notes, footer, tool names."""
    cfg = json.loads(SITE_JSON.read_text())
    lines = []
    for k in SITE_TEXT_KEYS:
        if k == "free_tools" and not tools:
            continue
        if k == "pillars":
            lines += [p["name"] if isinstance(p, dict) else str(p) for p in cfg.get(k, [])]
            continue
        lines += list(_strings(cfg.get(k)))
    P.add(part, "Sitio web · textos de la plantilla (botones, formularios, pie)", "sites/dinero-simple/site.json",
          "\n".join(dict.fromkeys(lines)))


def add_sequence(P: "Packets", part: str) -> None:
    import yaml
    seq = yaml.safe_load((ROOT / "brands" / "sequences" / "dinero-simple.yaml").read_text())
    lm = seq.get("lead_magnet") or {}
    P.add(part, "Correos de bienvenida · guía gratis (lista)", "brands/sequences/dinero-simple.yaml",
          "\n".join([lm.get("title", ""), lm.get("pitch", "")] + [f"{s['heading']}: " + " · ".join(s["items"])
                                                                  for s in lm.get("sections", [])]))
    for st in seq.get("steps", []):
        P.add(part, f"Correos de bienvenida · día {st['day_offset']}", "brands/sequences/dinero-simple.yaml",
              "\n".join([f"Asunto: {st['subject']}", f"Vista previa: {st.get('preheader', '')}",
                         f"Botón: {st.get('cta_label', '')}", strip_md(st["body_markdown"])]))
    P.add(part, "Correos de bienvenida · pie y página de venta", "brands/sequences/dinero-simple.yaml",
          "\n".join([seq.get("footer_note", "")] + [strip_md(json.dumps(p, ensure_ascii=False)) for p in seq.get("products", [])]))


LEAN_PART = "Lanzamiento ligero · todo lo que sale primero"


def gather_lean() -> "Packets":
    """Only what goes live in the lean launch (launch/dinero-simple/lean/lean_launch.py)."""
    sys.path.insert(0, str(DS / "lean"))
    import lean_launch as L
    import yaml
    P = Packets()
    brand = yaml.safe_load((ROOT / "brands" / "dinero-simple.yaml").read_text())
    bios = "\n".join(f"{k}: {v}" for k, v in (brand.get("bios") or {}).items())
    P.add(LEAN_PART, "Marca: bios, aviso de IA y llamado a la acción", "brands/dinero-simple.yaml",
          "\n".join([bios, f"Aviso de IA: {brand.get('ai_disclosure', '')}", f"Llamado a la acción: {brand.get('cta', '')}"]))
    add_site_text(P, LEAN_PART, tools=False)
    for page in L.SITE_PAGES:
        P.add_file(LEAN_PART, f"Sitio web · página · {page}", SITE / "pages" / f"{page}.md")
    P.add_file(LEAN_PART, "Guía gratis · Tu dinero en orden en 7 días (PDF)", FREEBIE, "html")
    add_sequence(P, LEAN_PART)
    for slug, dist in L.PRODUCTS.items():
        P.add_file(LEAN_PART, f"Sitio web · producto · {slug}", SITE / "products" / f"{slug}.md")
        P.add_file(LEAN_PART, f"Producto (PDF) · {dist}", DS / "products" / "dist" / dist / f"{dist}.html", "html")
    for slug in L.PRINTABLES:
        d = DS / "imprimibles" / "dist" / slug
        P.add_file(LEAN_PART, f"Imprimible · {slug} · anuncio", d / "LISTING.md")
        P.add_file(LEAN_PART, f"Imprimible · {slug}", d / f"{slug}.html", "html")
    for n, (week, day, time, pos) in enumerate(L.CALENDAR, 1):
        it = L.launch_items()[pos - 1]
        P.add(LEAN_PART, f"Semana {week} · {day} · {it['format']} · {it['script']['title']}",
              "launch/dinero-simple/content-lean.json", item_text(it), it["script"].get("claims_to_verify"))
    return P


def gather() -> Packets:
    P = Packets()
    p1 = CONTENT_PARTS[0][0]
    # Part 1: what a visitor sees on day one.
    import yaml
    brand = yaml.safe_load((ROOT / "brands" / "dinero-simple.yaml").read_text())
    bios = "\n".join(f"{k}: {v}" for k, v in (brand.get("bios") or {}).items())
    P.add(p1, "Marca: bios, aviso de IA y llamado a la acción", "brands/dinero-simple.yaml",
          "\n".join([bios, f"Aviso de IA: {brand.get('ai_disclosure', '')}", f"Llamado a la acción: {brand.get('cta', '')}"]))
    for sub in ("pages", "products", "emails", "blog"):
        for f in sorted((SITE / sub).glob("*.md")):
            P.add_file(p1, f"Sitio web · {sub} · {f.stem}", f)
    add_site_text(P, p1)
    P.add_file(p1, "Guía gratis · Tu dinero en orden en 7 días (PDF)", FREEBIE, "html")
    add_sequence(P, p1)
    for slug in ("recorte-de-gastos", "fecha-sin-deudas", "invertir-con-100", "paquete"):
        P.add_file(p1, f"Producto · {slug}", DS / "products" / "dist" / slug / f"{slug}.html", "html")
    P.add_file(p1, "Producto · El Presupuesto de 20 Minutos", DS / "product" / "el-presupuesto-de-20-minutos.html", "html")
    P.add_file(p1, "Producto · Cuaderno Tu primer año", DS / "primer-ano" / "dist" / "Cuaderno-Tu-Primer-Ano.html", "html")
    P.add_file(p1, "Producto · Cuaderno Tu primer año (Gumroad)", DS / "primer-ano" / "GUMROAD.md")
    for name in ("Guia-Estafas-Papas-y-Abuelos", "Lista-del-Refrigerador", "Tarjetas-de-Bolsillo"):
        P.add_file(p1, f"Guía gratis para mayores · {name}", DS / "mayores" / "dist" / f"{name}.html", "html")
    # Content, part by part.
    for part, files in CONTENT_PARTS:
        for f in files:
            for it in json.loads((DS / f).read_text()):
                fmt = it["format"]
                P.add(part, f"{f.removeprefix('content-').removesuffix('.json')} · {fmt} · {it['script']['title']}",
                      f"launch/dinero-simple/{f}", item_text(it), it["script"].get("claims_to_verify"))
    p2, p3 = CONTENT_PARTS[1][0], CONTENT_PARTS[2][0]
    P.add_file(p2, "Guía gratis · Temporada de impuestos 2027", DS / "GUIA_IMPUESTOS_2027.md")
    P.add_file(p2, "Boletín semanal (7 números)", DS / "NEWSLETTER.md")
    P.add_file(p2, "Canal de WhatsApp (30 días)", DS / "WHATSAPP_CHANNEL.md")
    P.add_file(p2, "Banco de respuestas (30)", DS / "ANSWER_BANK.md")
    for w in ("tu-presupuesto-en-20-minutos", "que-no-te-roben"):
        d = DS / "workshops" / "dist" / w
        P.add_file(p2, f"Taller · {w} · guía para facilitar", d / f"{w}-guia-para-facilitar.html", "html")
        P.add_file(p2, f"Taller · {w} · hojas de trabajo", d / f"{w}-hojas-de-trabajo.html", "html")
        P.add_pdf(p2, f"Taller · {w} · diapositivas", d / f"{w}-diapositivas.pdf")
    P.add_file(p3, "Guía gratis · Crédito sin Seguro Social", DS / "GUIA_CREDITO_SIN_SS.md")
    return P


def number(P: Packets):
    """Split every entry into chunks, pull out the lines that repeat, and number everything."""
    counts = Counter()
    for e in P.entries:
        e["lines"] = [x for x in e["text"].split("\n") if x.strip()]
        counts.update(set(x.strip() for x in e["lines"] if len(x.split()) >= 6))
    repeats = [line for line, n in counts.most_common() if n >= REPEAT_MIN]
    rid = {line: f"R-{i}" for i, line in enumerate(repeats, 1)}
    for e in P.entries:
        lines = [f"[{rid[x.strip()]}]" if x.strip() in rid else x for x in e["lines"]]
        e["chunks"] = chunks("\n".join(lines))
    return repeats


def words(texts) -> int:
    return sum(len(re.sub(r"\[R-\d+\]", "", t).split()) for t in texts)


def hours(n_words: int, wph: tuple[int, int], setup: float = 0.0) -> tuple[float, float]:
    return round(setup + n_words / wph[1], 1), round(setup + n_words / wph[0], 1)


CSS = """
@page{size:Letter;margin:0.55in 0.5in 0.6in}
body{font-family:"Inter",system-ui,Arial,sans-serif;font-size:9.6pt;line-height:1.38;color:#0d1b2a;margin:0}
h1{font-size:22pt;margin:0 0 6px} h2{font-size:15pt;margin:18px 0 6px;break-after:avoid;border-bottom:2px solid #2ec4b6}
.cover{break-after:page} .meta{color:#4a5868} .box{background:#e6f6f4;border-left:4px solid #2ec4b6;padding:8px 12px;margin:10px 0}
.warn{background:#fff1dc;border-left-color:#ff9f1c}
table{width:100%;border-collapse:collapse;margin:0 0 10px;table-layout:fixed}
td,th{border:1px solid #c9c3b6;padding:5px 6px;vertical-align:top;word-wrap:break-word}
th{background:#0d1b2a;color:#f4f1ea;text-align:left;font-size:8.6pt}
tr{break-inside:avoid} td.n{width:0.62in;font-weight:700;font-size:8.4pt} td.c{width:2.5in} td.t{white-space:pre-wrap}
.ok{display:inline-block;width:10px;height:10px;border:1.3px solid #0d1b2a;border-radius:2px;margin-right:4px;vertical-align:-1px}
.entry{font-weight:700;background:#f4f1ea} .src{font-weight:400;color:#4a5868;font-size:8pt}
.claims{font-size:8.2pt;color:#4a5868;white-space:pre-wrap}
"""


def table_rows(prefix: str, idx: int, e: dict, claims: bool = False) -> str:
    head = (f'<tr class="entry"><td class="n">{prefix}-{idx:03d}</td><td colspan="2">{esc(e["title"])} '
            f'<span class="src">· {esc(e["source"])}</span></td></tr>')
    rows = ""
    for j, c in enumerate(e["chunks"], 1):
        rows += (f'<tr><td class="n">{prefix}-{idx:03d}.{j}</td><td class="t">{esc(c)}</td>'
                 f'<td class="c"><span class="ok"></span>OK &nbsp; <span class="ok"></span>Cambiar:</td></tr>')
    if claims and e["claims"]:
        rows += (f'<tr><td class="n"></td><td class="claims" colspan="2">Context (English, from the claims list): '
                 f'{esc(chr(10).join(e["claims"]))}</td></tr>')
    return head + rows


def native_html(P: Packets, repeats: list[str], est: dict, lean: bool = False) -> str:
    parts, out, idx = [], [], 0
    rep = "".join(f'<tr><td class="n">R-{i}</td><td class="t">{esc(r)}</td><td class="c"><span class="ok"></span>OK '
                  f'&nbsp; <span class="ok"></span>Cambiar:</td></tr>' for i, r in enumerate(repeats, 1))
    current = None
    for e in P.entries:
        if e["part"] != current:
            if current is not None:
                out.append("</table>")
            current = e["part"]
            h = est["parts"][current]
            out.append(f'<h2>{esc(current)} <span class="src">· {h["entries"]} piezas · {h["words"]:,} palabras · '
                       f'{h["hours"][0]}–{h["hours"][1]} h</span></h2><table><tr><th style="width:0.62in">#</th>'
                       f'<th>Texto en español</th><th style="width:2.5in">Comentarios</th></tr>')
        idx += 1
        out.append(table_rows("N", idx, e))
    out.append("</table>")
    parts_list = "".join(f"<li>{esc(k)}: {v['entries']} piezas, {v['words']:,} palabras, {v['hours'][0]}–{v['hours'][1]} horas</li>"
                         for k, v in est["parts"].items())
    title = "Revisión de español nativo" + (" · lanzamiento ligero" if lean else "")
    scope = ("Solo lo que sale primero (el lanzamiento ligero): las páginas básicas del sitio, la guía gratis, los 5 "
             "correos de bienvenida, 2 productos y 4 semanas de publicaciones. Lo demás espera a una segunda ronda."
             if lean else "Todo el texto en español de Dinero Simple, en un solo documento numerado: publicaciones y "
             "videos, sitio web, correos, guías gratis y productos.")
    cover = f"""<section class="cover"><div class="meta">Dinero Simple · paquete de revisión</div>
      <h1>{title}</h1>
      <p>{scope} Todo lo escribió una máquina; necesitamos que suene natural para latinos en
      Estados Unidos (registro de tú, español latinoamericano neutro con un toque mexicano-americano).</p>
      <div class="box"><strong>Cómo revisar.</strong> Marca <em>OK</em> o <em>Cambiar</em> en cada fila y escribe tu cambio en
      la columna de comentarios (o en un PDF con comentarios). Las frases que se repiten en muchas publicaciones se revisan una
      sola vez, en la sección <em>Frases que se repiten</em>, y aparecen como [R-n] en el resto. Empieza por la Parte 1: es lo
      que se publica primero.</div>
      <div class="box warn">No cambies cifras, fechas ni datos legales: si algo parece incorrecto, márcalo y lo verificamos.
      Los pasajes sobre ITIN o inmigración también los revisa un abogado por separado.</div>
      <p><strong>Tamaño:</strong> {est['entries']} piezas, {est['rows']} filas, {est['words']:,} palabras.
      <strong>Tiempo estimado:</strong> {est['hours'][0]}–{est['hours'][1]} horas ({NATIVE_WPH[0]:,}–{NATIVE_WPH[1]:,} palabras por hora).</p>
      <ul>{parts_list}</ul></section>"""
    return (f'<!doctype html><html lang="es"><head><meta charset="utf-8"><title>{title}</title>'
            f"<style>{CSS}</style></head><body>{cover}<h2>Frases que se repiten · {len(repeats)}</h2><table><tr><th style='width:0.62in'>#</th>"
            f"<th>Frase</th><th style='width:2.5in'>Comentarios</th></tr>{rep}</table>{''.join(out)}</body></html>")


SENTENCE = re.compile(r"(?<=[.!?:])\s+|\n")
# A "referral" sentence only sends the reader to a lawyer or accredited representative (and away from notarios);
# it states no immigration rule. The attorney approves each distinct wording once, in the standard-lines section.
REFERRAL = re.compile(r"abogad|representante|organizaci[oó]n", re.I)
REFERRAL_HOW = re.compile(r"licencia|acreditad|ayuda legal|justice\.gov|colegio de abogados", re.I)
NOT_REFERRAL = re.compile(r"compart|acuerdo|afecta|riesgo|deport|\bICE\b|detenid|fianza|green card|residencia|"
                          r"ciudadan|visa|uscis|asilo|permiso|itin|w-7|consular|consulado|poder|tutela|hijos", re.I)


def standard_lines() -> dict[str, str]:
    sys.path.insert(0, str(DS / "src"))
    import safe_lines
    return dict(safe_lines.STANDARD)


def is_referral(sentence: str) -> bool:
    return bool(REFERRAL.search(sentence) and REFERRAL_HOW.search(sentence) and not NOT_REFERRAL.search(sentence))


def legal_text(chunk: str, standard: list[str]) -> str:
    """What is left of a chunk for the attorney once the standard lines and referral sentences are taken out."""
    for line in standard:
        chunk = chunk.replace(line, " ")
    chunk = re.sub(r"\[R-\d+\]", " ", chunk)
    return " ".join(x for x in SENTENCE.split(chunk) if x.strip() and not is_referral(x))


def attorney_entries(P: Packets, repeats: list[str] | None = None) -> tuple[list[dict], list[dict], list[str]]:
    """(entries to read, flagged entries fully covered by the standard lines, the standard lines to approve once).

    A paragraph goes to the attorney only if, after the standard lines and plain referral sentences are taken out,
    it still mentions the ITIN, immigration status, notarios, visas or consulates. Pieces flagged ATTORNEY REVIEW keep
    their flag; the attorney reads their matching paragraphs, and a flagged piece with none left is listed as covered."""
    std = list(standard_lines().values())
    referrals = {}
    for e in P.entries:
        for c in e["chunks"]:
            for x in SENTENCE.split(c):
                x = x.strip()
                if x and is_referral(x) and IMMIGRATION_RE.search(x) and x not in std:
                    referrals.setdefault(x, None)
    imm_repeats = [r for r in (repeats or []) if IMMIGRATION_RE.search(r) and not is_referral(r)]
    out, covered = [], []
    for e in P.entries:
        flagged = bool(e["claims"]) and e["claims"][0].startswith("ATTORNEY REVIEW")
        keep = [c for c in e["chunks"] if IMMIGRATION_RE.search(legal_text(c, std))]
        if keep:
            out.append({**e, "chunks": keep})
        elif flagged:
            covered.append(e)
    return out, covered, std + imm_repeats + list(referrals)


def attorney_html(A: list[dict], est: dict, lean: bool = False, standard: list[str] | None = None,
                  covered: list[dict] | None = None) -> str:
    std_rows = "".join(f'<tr><td class="n">S-{i}</td><td class="t">{esc(x)}</td><td class="c"><span class="ok"></span>OK '
                       f'&nbsp; <span class="ok"></span>Change:</td></tr>' for i, x in enumerate(standard or [], 1))
    cov = "".join(f"<li>{esc(e['title'])} <span class='src'>· {esc(e['source'])}</span></li>" for e in covered or [])
    extra = (f'<h2>Standard lines · approve once ({len(standard or [])})</h2><p class="meta">Lines that only send the reader '
             f'to a licensed attorney or accredited representative, and the few repeated status lines. Each wording is '
             f'reviewed here once; in the passages below they are taken out.</p><table><tr><th style="width:0.62in">#</th>'
             f'<th>Spanish text</th><th style="width:2.5in">Comments</th></tr>{std_rows}</table>')
    if cov:
        extra += (f'<h2>Flagged pieces covered by the standard lines ({len(covered)})</h2><p class="meta">Flagged ATTORNEY '
                  f'REVIEW, but their only immigration content is a standard line above. Listed so nothing is skipped '
                  f'silently.</p><ul>{cov}</ul>')
    scope = ("This is the lean-launch packet: only what goes live first (core site pages, the free 7-day guide, five "
             "welcome emails, two products and four weeks of posts). " if lean else "")
    body = "".join(table_rows("A", i, e, claims=True) for i, e in enumerate(A, 1))
    return f"""<!doctype html><html lang="en"><head><meta charset="utf-8"><title>Attorney review packet</title>
      <style>{CSS}</style></head><body><section class="cover"><div class="meta">Dinero Simple · review packet</div>
      <h1>Immigration attorney review{" · lean launch" if lean else ""}</h1>
      <p>{scope}Dinero Simple is a Spanish-language personal finance brand for US Hispanic adults, many of them recent arrivals.
      This packet holds every passage that mentions the ITIN, immigration status, notarios, visas or consulates: whole pieces
      that we flagged ATTORNEY REVIEW, and the individual paragraphs elsewhere that touch these topics. The text is in
      Spanish, so it needs a Spanish-reading licensed immigration attorney or DOJ-accredited representative.</p>
      <div class="box"><strong>What we need.</strong> Mark each row <em>OK</em> or <em>Change</em> and write the fix in the
      comment column. We are checking that nothing (1) gives legal advice about anyone's case, (2) could lead someone to
      a harmful step (for example, filing something that exposes them), (3) states an ITIN, IRS, SSA or USCIS rule
      incorrectly, or (4) fails to send immigration questions to a licensed attorney or accredited representative, never a
      notario. Rows with English "context" show the factual claims our fact-checker will also verify.</div>
      <p><strong>Size:</strong> {est['entries']} pieces, {est['rows']} rows, {est['words']:,} words. <strong>Estimated time:</strong>
      {est['hours'][0]}–{est['hours'][1]} hours ({ATTORNEY_WPH[0]:,}–{ATTORNEY_WPH[1]:,} words per hour, plus {ATTORNEY_SETUP_H:g} hour
      to read this brief and set up).</p></section>
      {extra}<h2>Passages to review</h2><table><tr><th style="width:0.62in">#</th><th>Spanish text</th>
      <th style="width:2.5in">Comments</th></tr>{body}</table></body></html>"""


def estimate(entries: list[dict], wph, setup=0.0, repeats=None) -> dict:
    w = words(c for e in entries for c in e["chunks"]) + (words(repeats) if repeats else 0)
    return {"entries": len(entries), "rows": sum(len(e["chunks"]) for e in entries), "words": w,
            "hours": hours(w, wph, setup)}


def summary_md(est_n: dict, est_a: dict, n_repeats: int, missing: list[str], lean: dict | None = None) -> str:
    parts = "\n".join(f"| {k} | {v['entries']} | {v['words']:,} | {v['hours'][0]}–{v['hours'][1]} |"
                      for k, v in est_n["parts"].items())
    miss = "\n".join(f"- `{m}`" for m in missing) or "- none"
    lean_rows = ""
    if lean:
        ln, la = lean["native"], lean["attorney"]
        lean_rows = f"""
## Lean launch first (send these two now)

Only what goes live first: core site pages, the free 7-day guide, the 5 welcome emails, El Kit para Recortar
Gastos, the Registro de Cuentas y Pagos printable and 4 weeks of posts (`lean/LEAN_LAUNCH.md`). Everything else is
phase 2 and stays off until the full packets below are done.

| Packet | Pieces | Rows | Words | Estimated hours |
|---|---|---|---|---|
| `Lean-Revision-Espanol-Nativo.pdf` | {ln['entries']} | {ln['rows']} | {ln['words']:,} | {ln['hours'][0]}–{ln['hours'][1]} |
| `Lean-Attorney-Review-Packet.pdf` | {la['entries']} | {la['rows']} | {la['words']:,} | {la['hours'][0]}–{la['hours'][1]} |

## Full packets (phase 2)
"""
    return f"""# Dinero Simple review packets
{lean_rows}
Two PDFs to hand off, built by `python3 launch/dinero-simple/review/build_packets.py --pdf` (they are in project files
`content-factory/dinero-simple/review-packets/`). Rebuild them after any copy change so the numbering matches.

| Packet | For | Pieces | Rows | Words | Estimated hours |
|---|---|---|---|---|---|
| `Revision-Espanol-Nativo.pdf` | native Spanish reviewer | {est_n['entries']} | {est_n['rows']} | {est_n['words']:,} | {est_n['hours'][0]}–{est_n['hours'][1]} |
| `Attorney-Review-Packet.pdf` | licensed immigration attorney or DOJ-accredited representative (reads Spanish) | {est_a['entries']} | {est_a['rows']} | {est_a['words']:,} | {est_a['hours'][0]}–{est_a['hours'][1]} |

Estimates: native review at {NATIVE_WPH[0]:,}–{NATIVE_WPH[1]:,} words per hour; attorney review at {ATTORNEY_WPH[0]:,}–{ATTORNEY_WPH[1]:,}
words per hour plus {ATTORNEY_SETUP_H:g} hour of setup. {n_repeats} lines that repeat across many posts (CTA, "not advice"
lines, series taglines) are reviewed once and counted once.

## Native review, in go-live order

Parts can go to different reviewers, or be paid for one at a time: only Part 1 blocks launch.

| Part | Pieces | Words | Hours |
|---|---|---|---|
{parts}

## What is in each packet

- **Native:** brand bios and AI line, every site page, product page, article and email, the welcome sequence, the
  paid product guides and the workbook, the free guides (taxes, credit, seniors), the newsletter, WhatsApp kit, answer
  bank, workshops, and every post and video script (on-screen text, voiceover, caption) from launch to September 2027.
- **Attorney:** every piece flagged ATTORNEY REVIEW (whole piece) plus every other paragraph that mentions the ITIN,
  immigration status, notarios, visas or consulates, with the English claims list as context.

## Sources that were missing when this was built

{miss}
"""


def to_pdf(src: Path, out: Path) -> None:
    js = ("const {chromium}=require('playwright');(async()=>{const b=await chromium.launch();const p=await b.newPage();"
          "await p.goto('file://" + str(src) + "');await p.pdf({path:'" + str(out) + "',format:'Letter',"
          "printBackground:true,displayHeaderFooter:true,headerTemplate:'<span></span>',"
          "footerTemplate:'<div style=\"font-size:7pt;width:100%;text-align:right;padding-right:0.5in\">"
          "<span class=pageNumber></span> / <span class=totalPages></span></div>',"
          "margin:{top:'0.5in',bottom:'0.55in',left:'0.5in',right:'0.5in'}});await b.close();})();")
    subprocess.run(["node", "-e", js], check=True, env={**os.environ, "NODE_PATH": "/opt/node22/lib/node_modules"})


def build(P: Packets | None = None) -> dict:
    P = P or gather()
    repeats = number(P)
    est_n = estimate(P.entries, NATIVE_WPH, repeats=repeats)
    est_n["parts"] = {}
    for part in dict.fromkeys(e["part"] for e in P.entries):
        es = [e for e in P.entries if e["part"] == part]
        est_n["parts"][part] = estimate(es, NATIVE_WPH, repeats=repeats if part in (CONTENT_PARTS[0][0], LEAN_PART) else None)
    A, covered, standard = attorney_entries(P, repeats)
    est_a = estimate(A, ATTORNEY_WPH, ATTORNEY_SETUP_H, repeats=standard)
    est_a["standard"], est_a["covered"] = len(standard), len(covered)
    return {"P": P, "repeats": repeats, "native": est_n, "attorney": est_a, "A": A, "covered": covered,
            "standard": standard}


def build_lean() -> dict:
    return build(gather_lean())


def main() -> None:
    DIST.mkdir(exist_ok=True)
    b, lean = build(), build_lean()
    for prefix, x in (("", b), ("Lean-", lean)):
        (DIST / f"{prefix}Revision-Espanol-Nativo.html").write_text(native_html(x["P"], x["repeats"], x["native"], lean=bool(prefix)))
        (DIST / f"{prefix}Attorney-Review-Packet.html").write_text(
            attorney_html(x["A"], x["attorney"], lean=bool(prefix), standard=x["standard"], covered=x["covered"]))
    (HERE / "REVIEW_PACKETS.md").write_text(summary_md(b["native"], b["attorney"], len(b["repeats"]), b["P"].missing + lean["P"].missing, lean))
    if "--pdf" in sys.argv:
        for name in ("Revision-Espanol-Nativo", "Attorney-Review-Packet"):
            for prefix in ("", "Lean-"):
                to_pdf(DIST / f"{prefix}{name}.html", DIST / f"{prefix}{name}.pdf")
    for label, x in (("full", b), ("lean", lean)):
        for k in ("native", "attorney"):
            e = x[k]
            print(f"{label} {k}: {e['entries']} pieces, {e['rows']} rows, {e['words']:,} words, {e['hours'][0]}-{e['hours'][1]} h")
    if b["P"].missing or lean["P"].missing:
        print("missing:", *(b["P"].missing + lean["P"].missing), sep="\n  ")


if __name__ == "__main__":
    main()
