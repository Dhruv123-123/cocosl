"""Build the Dinero Simple workshop kits: editable slides (.pptx + .pdf), a facilitator guide and worksheets.

    python launch/dinero-simple/workshops/build_workshops.py           # -> workshops/dist/<slug>/
    python launch/dinero-simple/workshops/build_workshops.py --no-pdf  # .pptx and .html only

Content lives in content_*.py. Everything is Spanish and machine-written: a native speaker must review it
before any organization uses it.
"""
from __future__ import annotations

import argparse
import html
import shutil
import subprocess
import sys
import tempfile
import zipfile
from pathlib import Path

from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.util import Inches, Pt

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import content_estafas, content_presupuesto  # noqa: E402

WORKSHOPS = [content_estafas, content_presupuesto]
C = {k: RGBColor.from_string(v) for k, v in dict(ink="14213D", ink2="1F2E52", paper="FBF5E9", card="FFFDF8", green="2AB7A9", greend="11706A",
                                                coral="FF7A59", coralt="FFE8DF", tint="E2F4F1", muted="4A5468", line="E2D8C4", white="FFFFFF").items()}
FONT = "Arial"
W, H = Inches(13.333), Inches(7.5)
FOOT = "Dinero Simple · Información general, no asesoría financiera, legal ni de impuestos"


def _bg(slide, color):
    f = slide.background.fill
    f.solid()
    f.fore_color.rgb = color


def _box(slide, x, y, w, h, fill=None, line=None, shape=MSO_SHAPE.RECTANGLE):
    s = slide.shapes.add_shape(shape, x, y, w, h)
    if fill is None:
        s.fill.background()
    else:
        s.fill.solid()
        s.fill.fore_color.rgb = fill
    if line is None:
        s.line.fill.background()
    else:
        s.line.color.rgb = line
    s.shadow.inherit = False
    return s


def _text(slide, x, y, w, h, text, size=24, color=None, bold=False, align=PP_ALIGN.LEFT, anchor=MSO_ANCHOR.TOP):
    tb = slide.shapes.add_textbox(x, y, w, h)
    tf = tb.text_frame
    tf.word_wrap = True
    tf.vertical_anchor = anchor
    tf.margin_left = tf.margin_right = Inches(0.05)
    lines = text if isinstance(text, list) else [text]
    for i, ln in enumerate(lines):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.alignment = align
        r = p.add_run()
        r.text = ln
        r.font.size = Pt(size)
        r.font.name = FONT
        r.font.bold = bold
        r.font.color.rgb = color or C["ink"]
    return tb


def _header(slide, title, n, total):
    _bg(slide, C["paper"])
    _box(slide, 0, 0, W, Inches(0.12), C["green"])
    _text(slide, Inches(0.6), Inches(0.45), Inches(12.1), Inches(1.0), title, 36, C["ink"], True)
    _text(slide, Inches(0.6), Inches(6.95), Inches(10), Inches(0.4), FOOT, 11, C["muted"])
    _text(slide, Inches(11.7), Inches(6.95), Inches(1.0), Inches(0.4), f"{n}/{total}", 11, C["muted"], align=PP_ALIGN.RIGHT)


def _cards(slide, items, top=Inches(1.9), height=Inches(3.9), accent=C["green"]):
    n = len(items)
    gap = Inches(0.3)
    cw = int((Inches(12.1) - gap * (n - 1)) / n)
    for i, (head, body) in enumerate(items):
        x = Inches(0.6) + i * (cw + gap)
        _box(slide, x, top, cw, height, C["card"], C["line"])
        _box(slide, x, top, cw, Inches(0.12), accent)
        _text(slide, x + Inches(0.25), top + Inches(0.4), cw - Inches(0.5), Inches(1.3), head, 28 if n <= 3 else 24, C["ink"], True)
        _text(slide, x + Inches(0.25), top + Inches(1.7), cw - Inches(0.5), height - Inches(1.9), body, 22 if n <= 3 else 19, C["muted"])


def _list(slide, items, x, y, w, size=24, numbered=False, color=None):
    rows = [f"{i}.  {t}" if numbered else f"•  {t}" for i, t in enumerate(items, 1)]
    tb = _text(slide, x, y, w, Inches(5), rows, size, color)
    for p in tb.text_frame.paragraphs:
        p.space_after = Pt(12)
    return tb


def render_slide(prs, kind, title, body, notes, n, total):
    s = prs.slides.add_slide(prs.slide_layouts[6])
    if kind in ("title", "close"):
        _bg(s, C["ink"])
        _box(s, Inches(0.6), Inches(2.2), Inches(1.4), Inches(0.12), C["coral"])
        _text(s, Inches(0.6), Inches(2.5), Inches(12), Inches(1.6), title, 54 if kind == "title" else 48, C["white"], True)
        _text(s, Inches(0.6), Inches(4.1), Inches(11.5), Inches(1.4), body, 28, RGBColor.from_string("CFE9E5"))
        _text(s, Inches(0.6), Inches(6.6), Inches(12), Inches(0.5), "Dinero Simple · dinerosimple.netlify.app", 14, RGBColor.from_string("9FB0CC"))
    else:
        _header(s, title, n, total)
        if kind == "agenda":
            for i, (t, what) in enumerate(body):
                y = Inches(1.75) + i * Inches(0.78)
                _box(s, Inches(0.6), y, Inches(1.9), Inches(0.62), C["tint"])
                _text(s, Inches(0.6), y, Inches(1.9), Inches(0.62), f"{t} min", 20, C["greend"], True, PP_ALIGN.CENTER, MSO_ANCHOR.MIDDLE)
                _text(s, Inches(2.8), y, Inches(9.5), Inches(0.62), what, 24, anchor=MSO_ANCHOR.MIDDLE)
        elif kind == "big":
            _box(s, Inches(0.6), Inches(2.2), Inches(0.14), Inches(2.6), C["coral"])
            _text(s, Inches(1.1), Inches(2.1), Inches(11.4), Inches(2.8), body, 40, C["ink"], True, anchor=MSO_ANCHOR.MIDDLE)
        elif kind in ("three", "four"):
            _cards(s, body)
        elif kind == "message":
            msg, flags = body
            _box(s, Inches(0.6), Inches(1.8), Inches(6.2), Inches(4.6), C["white"], C["line"], MSO_SHAPE.ROUNDED_RECTANGLE)
            _text(s, Inches(0.9), Inches(2.1), Inches(5.6), Inches(4.0), msg, 24)
            _list(s, flags, Inches(7.3), Inches(1.9), Inches(5.4), 24, numbered=True)
        elif kind == "scam":
            lead, points = body
            _box(s, Inches(0.6), Inches(1.65), Inches(12.1), Inches(1.15), C["coralt"])
            _text(s, Inches(0.85), Inches(1.65), Inches(11.6), Inches(1.15), lead, 28, C["ink"], True, anchor=MSO_ANCHOR.MIDDLE)
            _list(s, points, Inches(0.8), Inches(3.15), Inches(11.8), 24)
        elif kind == "activity":
            sub, steps = body
            _box(s, Inches(0.6), Inches(1.65), Inches(4.0), Inches(0.7), C["green"], shape=MSO_SHAPE.ROUNDED_RECTANGLE)
            _text(s, Inches(0.6), Inches(1.65), Inches(4.0), Inches(0.7), sub, 20, C["white"], True, PP_ALIGN.CENTER, MSO_ANCHOR.MIDDLE)
            _list(s, steps, Inches(0.8), Inches(2.8), Inches(11.8), 30, numbered=True)
        elif kind == "steps":
            _list(s, body, Inches(0.8), Inches(1.75), Inches(11.8), 26, numbered=True)
        elif kind == "bullets":
            _list(s, body, Inches(0.8), Inches(1.75), Inches(11.8), 26)
        elif kind == "table":
            rows, foot = body
            for i, (a, b) in enumerate(rows):
                y = Inches(1.7) + i * Inches(0.75)
                head = i == 0
                _box(s, Inches(0.6), y, Inches(8.4), Inches(0.68), C["ink"] if head else C["card"], None if head else C["line"])
                _text(s, Inches(0.85), y, Inches(4.0), Inches(0.68), a, 22, C["white"] if head else C["ink"], head, anchor=MSO_ANCHOR.MIDDLE)
                _text(s, Inches(4.9), y, Inches(4.0), Inches(0.68), b, 22, C["white"] if head else C["greend"], True, anchor=MSO_ANCHOR.MIDDLE)
            _text(s, Inches(9.4), Inches(1.8), Inches(3.3), Inches(4.0), foot, 22, C["muted"])
        elif kind == "formula":
            f, rows = body
            _box(s, Inches(0.6), Inches(1.65), Inches(12.1), Inches(1.3), C["ink"], shape=MSO_SHAPE.ROUNDED_RECTANGLE)
            _text(s, Inches(0.6), Inches(1.65), Inches(12.1), Inches(1.3), f, 32, C["white"], True, PP_ALIGN.CENTER, MSO_ANCHOR.MIDDLE)
            _cards(s, rows, top=Inches(3.3), height=Inches(3.2), accent=C["coral"])
        elif kind == "example":
            for i, (a, b) in enumerate(body):
                last = i == len(body) - 1
                y = Inches(1.65) + i * Inches(0.8)
                _box(s, Inches(0.6), y, Inches(8.0), Inches(0.7), C["green"] if last else C["card"], None if last else C["line"])
                _text(s, Inches(0.85), y, Inches(4.5), Inches(0.7), a, 24, C["white"] if last else C["ink"], last, anchor=MSO_ANCHOR.MIDDLE)
                _text(s, Inches(5.0), y, Inches(3.4), Inches(0.7), b, 26, C["white"] if last else C["ink"], True, PP_ALIGN.RIGHT, MSO_ANCHOR.MIDDLE)
            _text(s, Inches(9.0), Inches(1.75), Inches(3.7), Inches(4.5), ["Ejemplo inventado.", "", "Cubre súper, gasolina, comida fuera y diversión.", "", "Sin categorías que vigilar."], 20, C["muted"])
        else:
            raise SystemExit(f"unknown slide kind {kind}")
    s.notes_slide.notes_text_frame.text = notes
    return s


def build_pptx(w, out: Path) -> Path:
    prs = Presentation()
    prs.slide_width, prs.slide_height = W, H
    total = len(w.S)
    for n, (kind, title, body, notes) in enumerate(w.S, 1):
        render_slide(prs, kind, title, body, notes, n, total)
    p = out / f"{w.SLUG}-diapositivas.pptx"
    prs.save(p)
    return p


CSS = """@page{size:letter;margin:0.55in}*{box-sizing:border-box}body{font-family:Helvetica,Arial,sans-serif;color:#14213d;font-size:10.5pt;line-height:1.4;margin:0}
h1{font-size:22pt;margin:0 0 4px}h2{font-size:14pt;color:#11706a;margin:18px 0 6px;border-bottom:2px solid #2ab7a9;padding-bottom:3px}h3{font-size:11.5pt;margin:12px 0 3px}
.k{color:#11706a;font-weight:700;text-transform:uppercase;letter-spacing:.06em;font-size:8.5pt}table{width:100%;border-collapse:collapse;margin:6px 0}
td,th{border:1px solid #e2d8c4;padding:5px 7px;text-align:left;vertical-align:top}th{background:#14213d;color:#fff}.note{background:#ffe8df;padding:8px 10px;border-left:4px solid #ff7a59;margin:8px 0}
.slide{page-break-inside:avoid}.ws{page-break-after:always}.ws:last-child{page-break-after:auto}.field{border:1px solid #e2d8c4;border-radius:6px;padding:9px 10px;margin:8px 0;min-height:52px}
.field b{display:block;margin-bottom:4px}.box{display:inline-block;width:12px;height:12px;border:1.5px solid #14213d;margin-right:8px;vertical-align:-2px}
.flags span{display:inline-block;border:1px solid #2ab7a9;border-radius:10px;padding:1px 8px;margin:4px 4px 0 0;font-size:9pt}.foot{font-size:8.5pt;color:#4a5468;margin-top:14px}"""


def guide_html(w) -> str:
    e = html.escape
    rows = "".join(f"<tr><td>{e(t)} min</td><td>{e(a)}</td></tr>" for t, a in w.AGENDA)
    slides = "".join(f"<div class='slide'><h3>{n}. {e(t)}</h3><p>{e(notes)}</p></div>" for n, (_, t, _, notes) in enumerate(w.S, 1))
    li = lambda xs: "".join(f"<li>{e(x)}</li>" for x in xs)
    return f"""<!doctype html><html lang="es"><head><meta charset="utf-8"><title>Guía para facilitar · {e(w.TITLE)}</title><style>{CSS}</style></head><body>
<div class="k">Dinero Simple · Guía para quien facilita</div><h1>{e(w.TITLE)}</h1><p>{e(w.SUBTITLE)} · {w.MINUTES} minutos · {len(w.S)} diapositivas · 2 hojas de trabajo</p>
<div class="note"><b>Antes de usar:</b> este material fue escrito con ayuda de IA y una persona hablante nativa debe revisarlo. Verifique también los datos de la lista de abajo la semana del taller.</div>
<h2>Horario</h2><table><tr><th>Minutos</th><th>Parte</th></tr>{rows}</table>
<h2>Materiales</h2><ul>{li(w.MATERIALS)}</ul>
<h2>Reglas para quien facilita</h2><ul>{li(w.RULES)}</ul>
<h2>Verificar antes del taller</h2><ul>{li(w.CHECK)}</ul>
<h2>Guion por diapositiva</h2><p>Las mismas notas vienen en las notas del presentador de las diapositivas.</p>{slides}
<p class="foot">Dinero Simple · dinerosimple.netlify.app · Información general, no asesoría financiera, legal ni de impuestos.</p></body></html>"""


def worksheets_html(w) -> str:
    e = html.escape
    pages = []
    for title, intro, fields, checks in w.WORKSHEETS:
        body = ""
        for label, text in fields:
            body += f"<div class='field'><b>{e(label)}</b>{e(text)}"
            if w is content_estafas and title.startswith("Hoja 1"):
                body += "<div class='flags'>Señales: " + "".join(f"<span>☐ {e(f)}</span>" for f in checks) + "</div><div>¿Qué haría?: __________________________________________</div>"
            body += "</div>"
        if checks and not (w is content_estafas and title.startswith("Hoja 1")):
            body += "<h2>Esta semana</h2>" + "".join(f"<p><span class='box'></span>{e(c)}</p>" for c in checks)
        pages.append(f"<div class='ws'><div class='k'>Dinero Simple · {e(w.TITLE)}</div><h1>{e(title)}</h1><p>{e(intro)}</p>{body}"
                     "<p class='foot'>Información general, no asesoría financiera, legal ni de impuestos. dinerosimple.netlify.app</p></div>")
    return f"<!doctype html><html lang='es'><head><meta charset='utf-8'><title>Hojas de trabajo · {e(w.TITLE)}</title><style>{CSS}</style></head><body>{''.join(pages)}</body></html>"


def to_pdf_html(pairs):
    from playwright.sync_api import sync_playwright
    with sync_playwright() as p:
        try:
            b = p.chromium.launch()
        except Exception:  # a pip Playwright newer than the installed browser: use the system Chromium
            exe = shutil.which("chromium") or "/opt/pw-browsers/chromium"
            b = p.chromium.launch(executable_path=exe)
        pg = b.new_page()
        for src, dst in pairs:
            pg.goto(src.as_uri())
            pg.pdf(path=str(dst), format="Letter", print_background=True)
        b.close()


def pptx_to_pdf(pptx: Path):
    with tempfile.TemporaryDirectory() as prof:
        subprocess.run(["soffice", f"-env:UserInstallation=file://{prof}", "--headless", "--convert-to", "pdf", "--outdir", str(pptx.parent), str(pptx)],
                       check=True, capture_output=True, timeout=240)


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=str(HERE / "dist"))
    ap.add_argument("--no-pdf", action="store_true")
    a = ap.parse_args(argv)
    root = Path(a.out)
    for w in WORKSHOPS:
        out = root / w.SLUG
        if out.exists():
            shutil.rmtree(out)
        out.mkdir(parents=True)
        pptx = build_pptx(w, out)
        g = out / f"{w.SLUG}-guia-para-facilitar.html"
        g.write_text(guide_html(w))
        ws = out / f"{w.SLUG}-hojas-de-trabajo.html"
        ws.write_text(worksheets_html(w))
        if not a.no_pdf:
            pptx_to_pdf(pptx)
            to_pdf_html([(g, g.with_suffix(".pdf")), (ws, ws.with_suffix(".pdf"))])
        with zipfile.ZipFile(root / f"{w.SLUG}.zip", "w", zipfile.ZIP_DEFLATED) as z:
            for f in sorted(out.iterdir()):
                z.write(f, f"{w.SLUG}/{f.name}")
        print(f"{w.SLUG}: {len(w.S)} slides -> {out}")


if __name__ == "__main__":
    main()
