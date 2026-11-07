"""Money Made Simple, the ebook: a Kindle EPUB, a 6 x 9 in KDP paperback interior, and both covers.

    python launch/ebook/build_ebook.py [--out launch/ebook/dist] [--skip-pdf]

The text lives in launch/ebook/chapters/*.md (pandoc Markdown), in the order of ORDER below. Cross-references are
written as Chapter {{chapter-id}} and resolved to chapter numbers here, so chapters can be moved without breaking them.

Outputs (git-ignored):
  Money-Made-Simple.epub                  Kindle eBook (EPUB 3, reflowable, cover embedded)
  Money-Made-Simple-Kindle-Cover.jpg      1600 x 2560 px RGB JPEG, the Kindle cover upload
  Money-Made-Simple-Paperback-Interior.pdf  6 x 9 in, no bleed, fonts embedded, mirrored margins
  Money-Made-Simple-Paperback-Cover.pdf   full wrap: back + spine + front, 0.125 in bleed
  Money-Made-Simple-Paperback-Cover-preview.png

Nothing is uploaded. KDP_NOTES.md has the listing copy, prices and AI-disclosure answers.
"""
from __future__ import annotations

import argparse
import html
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / "launch" / "etsy"))
import build_etsy  # noqa: E402

CHAPTERS = HERE / "chapters"
ORDER = [
    "00-introduction.md", "01-part-one.md", "02-part-two.md", "02b-living-on-the-number.md",
    "02c-when-life-doesnt-fit.md", "03-part-three.md", "04a-emergency-fund.md", "04a2-big-goals.md",
    "04b-credit-and-investing.md", "05-part-five.md", "05b-questions.md", "06-back-matter.md",
]

TITLE = "Money Made Simple"
SUBTITLE = ("A Plain-English Guide to Budgeting in 20 Minutes a Week, Cutting Your Bills, Paying Off Debt and "
            "Starting to Invest")
AUTHOR = "Money Made Simple"
YEAR = 2026
STEM = "Money-Made-Simple"

TRIM_W, TRIM_H, BLEED = 6.0, 9.0, 0.125
SPINE_PER_PAGE = 0.002252      # white paper, black ink (KDP)
SPINE_TEXT_MIN_PAGES = 80      # KDP allows spine text from 79 pages; keep a page of margin
# Interior margins. KDP's minimums at 151-300 pages are 0.5 in inside and 0.25 in outside; these clear them at any
# length this book could reach.
M_TOP, M_BOTTOM, M_INSIDE, M_OUTSIDE = 0.7, 0.8, 0.8, 0.6

HEADING = re.compile(r"^# (?P<title>.+?)(?: \{(?P<attrs>[^}]*)\})?\s*$", re.M)
REF = re.compile(r"\{\{([a-z0-9-]+)\}\}")
BANNED = ("guarantee", "risk-free", "i've used", "bestseller", "best-seller", "get rich", "[your store link]")


# ---------------------------------------------------------------- text

def raw_source() -> str:
    return "\n\n".join((CHAPTERS / f).read_text() for f in ORDER)


def outline(src: str | None = None) -> list[dict]:
    """Every level-1 heading in order: parts, numbered chapters and unnumbered sections."""
    src = raw_source() if src is None else src
    out, n = [], 0
    for m in HEADING.finditer(src):
        attrs = m.group("attrs") or ""
        ident = next((a[1:] for a in attrs.split() if a.startswith("#")), "")
        kind = "part" if ".part" in attrs else "other" if ".unnumbered" in attrs else "chapter"
        if kind == "chapter":
            n += 1
        out.append(dict(title=m.group("title"), id=ident, kind=kind, num=n if kind == "chapter" else None))
    return out


def resolved_source() -> str:
    src = raw_source()
    nums = {h["id"]: h["num"] for h in outline(src) if h["kind"] == "chapter"}
    missing = sorted(set(REF.findall(src)) - set(nums))
    if missing:
        raise SystemExit(f"unknown chapter references: {missing}")
    return REF.sub(lambda m: str(nums[m.group(1)]), src)


def word_count(src: str | None = None) -> int:
    text = REF.sub("1", raw_source() if src is None else src)
    text = re.sub(r"\{[^}]*\}", "", text)
    return len(re.findall(r"[A-Za-z0-9$][A-Za-z0-9$,.'%()/-]*", text))


def check_copy(src: str) -> None:
    low = src.lower()
    hits = [w for w in BANNED if w in low]
    if hits:
        raise SystemExit(f"banned wording in the book: {hits}")
    for need in ("not financial", "fictional", "made up"):
        if need not in low:
            raise SystemExit(f"the book must say {need!r} somewhere")


def _split_part(title: str) -> tuple[str, str]:
    kick, _, rest = title.partition(": ")
    return kick, rest


def epub_markdown(src: str) -> str:
    """Numbered chapter headings, and a copyright section first."""
    def head(m: re.Match) -> str:
        attrs = m.group("attrs") or ""
        if ".part" in attrs or ".unnumbered" in attrs:
            return m.group(0)
        head.n += 1
        return f"# {head.n}. {m.group('title')} {{{attrs}}}"
    head.n = 0
    body = HEADING.sub(head, src)
    return f"# Copyright {{.unnumbered #copyright}}\n\n{copyright_md()}\n\n{body}"


def copyright_md() -> str:
    return f"""**{TITLE}:** {SUBTITLE}

Copyright © {YEAR} {AUTHOR}. All rights reserved. No part of this book may be reproduced or shared without
permission, except for brief quotations in reviews.

This book is general education about organizing your own money. It is not financial, tax, legal or investment advice,
and it doesn't know your situation. The people in its examples are fictional and their numbers are for illustration.
Figures that change each year, like retirement account limits, are {YEAR} figures; check the official sources listed
at the end of the book for current ones. The publisher isn't paid by any company mentioned.

This book was compiled and edited from {AUTHOR}'s guides, articles and newsletters. Its text was drafted with the
help of AI writing tools and then reviewed and edited by the publisher. The cover and page layouts were produced with
software, including code written with AI assistance. Worked examples were calculated with software and checked.

First edition, {YEAR}. Independently published."""


# ---------------------------------------------------------------- print interior

def pandoc_html(md: str) -> str:
    p = subprocess.run(["pandoc", "-f", "markdown-tex_math_dollars", "-t", "html5", "--wrap=none"],
                       input=md, capture_output=True, text=True, check=True)
    return p.stdout


def print_body_md(src: str) -> str:
    """Chapter and part headings become raw-HTML openers; everything else stays Markdown."""
    def head(m: re.Match) -> str:
        attrs, title = m.group("attrs") or "", m.group("title")
        ident = next((a[1:] for a in attrs.split() if a.startswith("#")), "")
        t = html.escape(title)
        if ".part" in attrs:
            kick, rest = _split_part(title)
            return (f'<section class="partpage"><div class="kick">{html.escape(kick)}</div>'
                    f'<h1 class="part">{html.escape(rest)}</h1></section>')
        if ".unnumbered" in attrs:
            return f'<div class="opener"><h1 id="{ident}">{t}</h1></div>'
        head.n += 1
        return (f'<div class="opener"><div class="kick">Chapter {head.n}</div>'
                f'<h1 id="{ident}">{t}</h1></div>')
    head.n = 0
    return HEADING.sub(head, src)


def toc_html(pages: dict[str, int] | None) -> str:
    rows = []
    for h in outline():
        key = h["title"]
        num = f"{pages[key]}" if pages else "000"
        if h["kind"] == "part":
            kick, rest = _split_part(h["title"])
            rows.append(f'<div class="t part"><span>{html.escape(kick)}: {html.escape(rest)}</span></div>')
            continue
        label = f'<b>{h["num"]}</b>&ensp;' if h["kind"] == "chapter" else ""
        rows.append(f'<div class="t"><span>{label}{html.escape(h["title"])}</span><i></i><span>{num}</span></div>')
    return '<section class="toc"><h1>Contents</h1>' + "".join(rows) + "</section>"


PRINT_CSS = f"""
@page {{ size: {TRIM_W}in {TRIM_H}in; margin: {M_TOP}in {M_OUTSIDE}in {M_BOTTOM}in {M_INSIDE}in;
  @bottom-center {{ content: counter(page); font: 500 8.5pt Inter, sans-serif; color: #444; vertical-align: top;
    padding-top: .2in; }} }}
@page :right {{ margin-left: {M_INSIDE}in; margin-right: {M_OUTSIDE}in; }}
@page :left {{ margin-left: {M_OUTSIDE}in; margin-right: {M_INSIDE}in; }}
@page front {{ @bottom-center {{ content: none; }} }}
@page partpage {{ @bottom-center {{ content: none; }} }}
html {{ -webkit-print-color-adjust: exact; print-color-adjust: exact; }}
body {{ margin: 0; font: 10.5pt/1.48 Caladea, Cambria, "Liberation Serif", serif; color: #111;
  hyphens: auto; text-align: justify; orphans: 2; widows: 2; }}
.front {{ page: front; }}
.titlepage {{ height: {TRIM_H - M_TOP - M_BOTTOM - 0.05}in; display: flex; flex-direction: column; text-align: left;
  break-after: page; }}
.titlepage .kick {{ margin-top: .9in; }}
.titlepage h1 {{ font: 900 34pt/1 Inter, sans-serif; letter-spacing: -.02em; margin: .12in 0 .2in; }}
.titlepage .sub {{ font: 400 12pt/1.4 Inter, sans-serif; color: #333; text-align: left; hyphens: manual; }}
.titlepage .by {{ margin-top: auto; font: 800 9.5pt Inter, sans-serif; letter-spacing: .14em; text-transform: uppercase; }}
.copyright {{ height: {TRIM_H - M_TOP - M_BOTTOM - 0.05}in; display: flex; flex-direction: column; justify-content: flex-end;
  font-size: 8.5pt; line-height: 1.5; color: #333; text-align: left; hyphens: manual; break-after: page; }}
.copyright p {{ margin: 0 0 .09in; }}
.toc {{ break-after: page; }}
.toc h1 {{ font: 900 20pt Inter, sans-serif; margin: .3in 0 .2in; }}
.toc .t {{ display: flex; align-items: baseline; gap: .06in; font: 400 9.4pt/1.35 Inter, sans-serif; margin: .035in 0;
  text-align: left; hyphens: manual; }}
.toc .t i {{ flex: 1; border-bottom: 1px dotted #888; transform: translateY(-3px); }}
.toc .t b {{ font-weight: 700; display: inline-block; width: .2in; }}
.toc .part {{ font-weight: 800; text-transform: uppercase; letter-spacing: .06em; font-size: 8pt; margin-top: .13in; }}
.kick {{ font: 700 8.5pt Inter, sans-serif; text-transform: uppercase; color: #555; }}
.partpage {{ page: partpage; break-before: page; break-after: page; height: {TRIM_H - M_TOP - M_BOTTOM - 0.1}in;
  display: flex; flex-direction: column; justify-content: center; text-align: center; }}
h1.part {{ font: 900 26pt/1.1 Inter, sans-serif; margin: .1in 0 0; letter-spacing: -.01em; }}
.opener {{ break-before: page; padding-top: .45in; margin-bottom: .22in; text-align: left; }}
.opener h1 {{ font: 900 20pt/1.12 Inter, sans-serif; margin: .06in 0 0; letter-spacing: -.01em; hyphens: manual; }}
.partpage + .opener {{ break-before: auto; }}
h2 {{ font: 800 12.5pt/1.25 Inter, sans-serif; margin: .24in 0 .07in; text-align: left; hyphens: manual;
  break-after: avoid; }}
h3 {{ font: 700 10.5pt/1.3 Inter, sans-serif; margin: .16in 0 .05in; text-align: left; break-after: avoid; }}
p {{ margin: 0 0 .085in; }}
ul, ol {{ margin: 0 0 .1in; padding-left: .24in; }}
li {{ margin: 0 0 .04in; }}
li > p {{ margin: 0; }}
blockquote {{ margin: .08in 0 .12in; padding: .02in 0 .02in .14in; border-left: 2pt solid #999; color: #222;
  text-align: left; hyphens: manual; break-inside: avoid; }}
blockquote p {{ margin: 0 0 .06in; }}
.line-block {{ margin: 0 0 .06in; }}
table {{ width: 100%; border-collapse: collapse; margin: .06in 0 .14in; font: 400 8.1pt/1.3 Inter, sans-serif;
  text-align: left; hyphens: manual; break-inside: avoid; }}
th {{ font-weight: 700; border-bottom: 1.2pt solid #333; padding: .035in .05in .035in 0; vertical-align: bottom; }}
td {{ border-bottom: .5pt solid #bbb; padding: .035in .05in .035in 0; vertical-align: top; }}
td:last-child, th:last-child {{ padding-right: 0; }}
strong {{ font-weight: 700; }}
"""


def interior_html(src: str, pages: dict[str, int] | None = None) -> str:
    body = pandoc_html(print_body_md(src))
    copyright = pandoc_html(copyright_md())
    front = (f'<div class="front"><section class="titlepage"><div class="kick">A plain-English guide</div>'
             f'<h1>{TITLE}</h1><div class="sub">{html.escape(SUBTITLE)}</div>'
             f'<div class="by">{AUTHOR}</div></section>'
             f'<section class="copyright">{copyright}</section>{toc_html(pages)}</div>')
    return (f'<!doctype html><html lang="en-US"><head><meta charset="utf-8"><title>{TITLE}</title>'
            f'<style>{PRINT_CSS}</style></head><body>{front}{body}</body></html>')


def page_texts(pdf: Path) -> list[str]:
    out = subprocess.run(["pdftotext", "-layout", str(pdf), "-"], capture_output=True, text=True, check=True).stdout
    return out.split("\f")[:-1] if out.endswith("\f") else out.split("\f")


def heading_pages(pdf: Path) -> dict[str, int]:
    """Where each part, chapter and section starts, found from the rendered PDF text."""
    texts = [re.sub(r"\s+", "", t) for t in page_texts(pdf)]
    found, start = {}, 3            # skip the title, copyright and the first contents page
    for h in outline():
        if h["kind"] == "part":
            kick, rest = _split_part(h["title"])
            key = re.sub(r"\s+", "", kick + rest).upper()
            match = lambda t: t.upper().startswith(key)  # noqa: E731
        else:
            key = re.sub(r"\s+", "", (f"CHAPTER{h['num']}" if h["kind"] == "chapter" else "") +
                         html.unescape(h["title"]))
            match = lambda t, k=key: t.replace("’", "'").upper().startswith(k.upper())  # noqa: E731
        for i in range(start, len(texts)):
            if match(texts[i]):
                found[h["title"]] = i + 1
                start = i + 1
                break
        else:
            raise SystemExit(f"could not find the page for {h['title']!r}")
    return found


def margin_problems(pdf: Path) -> list[str]:
    """Any word closer than 0.4 in to the page edge (KDP asks for 0.25 in outside and 0.5 in inside; the inside
    margin itself is 0.8 in, so this mostly guards the page numbers and the outside edge)."""
    out = subprocess.run(["pdftotext", "-bbox", str(pdf), "-"], capture_output=True, text=True, check=True).stdout
    probs, page = [], 0
    lim = 0.4 * 72
    W, H = TRIM_W * 72, TRIM_H * 72
    for line in out.splitlines():
        if "<page " in line:
            page += 1
        m = re.search(r'xMin="([\d.]+)" yMin="([\d.]+)" xMax="([\d.]+)" yMax="([\d.]+)">([^<]*)<', line)
        if m:
            x0, y0, x1, y1 = map(float, m.groups()[:4])
            if x0 < lim or y0 < lim or x1 > W - lim or y1 > H - lim:
                probs.append(f"p{page}: {m.group(5)!r} at ({x0:.0f},{y0:.0f})-({x1:.0f},{y1:.0f})")
    return probs


def pdf_pages(pdf: Path) -> int:
    info = subprocess.run(["pdfinfo", str(pdf)], capture_output=True, text=True, check=True).stdout
    return int(re.search(r"Pages:\s+(\d+)", info).group(1))


# ---------------------------------------------------------------- covers

def _bars(width_in: float) -> str:
    """The four-line plan as one stacked bar, the book's motif."""
    segs = [("Bills", 44, "#0b1d13"), ("Funds", 16, "#1e8a50"), ("Goals", 16, "#2fbf71"), ("Weekly", 24, "#f2b134")]
    x, parts = 0.0, []
    for name, pct, col in segs:
        w = pct * 4
        parts.append(f'<rect x="{x}" y="0" width="{w - 3}" height="46" rx="6" fill="{col}"/>'
                     f'<text x="{x + 2}" y="70" font-family="Inter" font-weight="800" font-size="15" fill="#0b1d13">'
                     f'{name}</text>')
        x += w
    return f'<svg viewBox="0 0 400 78" style="width:{width_in}in;display:block">{"".join(parts)}</svg>'


def _front(w: float, h: float, unit: str = "in") -> str:
    """The front cover, laid out in a w x h box (inches). Used for both the Kindle cover and the paperback."""
    s = w / 6.0      # scale against the 6 in paperback front
    return f'''<div class="front" style="width:{w}{unit};height:{h}{unit}">
  <div class="fpad" style="padding:{0.62 * s}in {0.55 * s}in {0.5 * s}in;height:{h - 1.05 * s}{unit}">
    <div class="kick" style="font-size:{11 * s}pt">A plain-English guide</div>
    <div class="ttl" style="font-size:{70 * s}pt">Money<br>Made<br><em>Simple</em></div>
    <div class="sub" style="font-size:{13.5 * s}pt;max-width:{4.7 * s}in">Budget in twenty minutes a week, cut your
      bills, pay off debt and start investing with $100 a month.</div>
    <div style="margin-top:auto">{_bars(4.5 * s)}</div>
    <div class="note" style="font-size:{10 * s}pt;margin-top:{0.12 * s}in">Four lines. One weekly number.</div>
  </div>
  <div class="band" style="height:{1.05 * s}in;font-size:{11 * s}pt;padding-left:{0.55 * s}in">MONEY MADE SIMPLE</div>
</div>'''


COVER_CSS = """
*{box-sizing:border-box} html,body{margin:0}
body{font-family:Inter,system-ui,sans-serif;color:#0b1d13;-webkit-print-color-adjust:exact;print-color-adjust:exact}
.front{position:relative;background:#f4f1e8;overflow:hidden}
.fpad{display:flex;flex-direction:column}
.kick{text-transform:uppercase;letter-spacing:.16em;font-weight:800;color:#1e8a50}
.ttl{font-family:"Inter Display",Inter,sans-serif;font-weight:900;letter-spacing:-.035em;line-height:.9;margin-top:.12in}
.ttl em{font-style:normal;color:#1e8a50}
.sub{color:#3b4a41;line-height:1.38;margin-top:.22in}
.note{font-weight:700;color:#3b4a41}
.band{position:absolute;left:0;right:0;bottom:0;background:#0b1d13;color:#f4f1e8;font-weight:800;letter-spacing:.16em;
  display:flex;align-items:center}
"""


def kindle_cover_html() -> str:
    # 800 x 1280 CSS px rendered at 2x = 1600 x 2560. 96 px = 1 in, so the box is 8.333 x 13.333 in.
    w, h = 800 / 96, 1280 / 96
    return (f'<!doctype html><html><head><meta charset="utf-8"><style>{COVER_CSS}</style></head>'
            f'<body>{_front(w, h)}</body></html>')


def spine_width(pages: int) -> float:
    return round(pages * SPINE_PER_PAGE, 4)


def cover_size(pages: int) -> tuple[float, float]:
    return round(BLEED * 2 + TRIM_W * 2 + spine_width(pages), 4), TRIM_H + BLEED * 2


BACK_HEAD = "Four lines. One weekly number. Twenty minutes a week."
BACK_BLURB = ("Most budgets fail because they ask for forty small decisions a day. This one asks for one decision a "
              "month and a twenty-minute check-in each week. Split your pay into bills, funds, goals and one weekly "
              "spending number, put the first three on autopilot, and spend the fourth however you like.")
BACK_BULLETS = [
    "Find your real numbers in one evening, including the costs that aren't monthly",
    "Cut forgotten subscriptions, with word-for-word scripts for lowering the bills you keep",
    "Put a date on paying off debt: avalanche or snowball, worked through with real numbers",
    "Read your credit reports, dispute errors and freeze your credit for free",
    "Start investing with $100 a month: which account, what to buy, and why fees matter",
]
BACK_FINE = ("Educational content for US readers, not financial, tax, legal or investment advice. Examples are "
             "fictional. Written with the help of AI tools and edited by the publisher.")


def paperback_cover_html(pages: int) -> str:
    W, H = cover_size(pages)
    sp = spine_width(pages)
    fw = TRIM_W + BLEED                      # each panel includes the outer bleed
    spine_text = ""
    if pages >= SPINE_TEXT_MIN_PAGES:
        fs = min(9.5, (sp - 0.125) * 72 * 0.72)
        spine_text = f'<div class="sptxt" style="font-size:{fs:.2f}pt">MONEY MADE SIMPLE</div>'
    bullets = "".join(f"<li>{html.escape(b)}</li>" for b in BACK_BULLETS)
    return f'''<!doctype html><html><head><meta charset="utf-8"><style>
@page{{size:{W}in {H}in;margin:0}}
{COVER_CSS}
.wrap{{position:relative;width:{W}in;height:{H}in;background:#f4f1e8;overflow:hidden}}
.panel{{position:absolute;top:0;height:{H}in}}
.back{{left:0;width:{fw}in;padding:{BLEED + 0.6}in 0.6in 0 {BLEED + 0.55}in}}
.back h2{{font-size:19pt;font-weight:900;letter-spacing:-.02em;line-height:1.12;margin:0 0 .16in}}
.back p{{font-size:10.5pt;line-height:1.5;color:#26352c;margin:0 0 .14in}}
.back ul{{font-size:10pt;line-height:1.5;color:#26352c;padding-left:.2in;margin:0}}
.back li{{margin-bottom:.05in}}
.back .fine{{font-size:7.5pt;color:#5b6a61;max-width:3.1in;margin-top:.2in;line-height:1.45}}
.spine{{left:{fw}in;width:{sp}in}}
.sptxt{{position:absolute;left:50%;top:50%;transform:translate(-50%,-50%) rotate(90deg);white-space:nowrap;
  font-weight:900;letter-spacing:.12em;color:#0b1d13}}
.fr{{left:{fw + sp}in;width:{fw}in}}
.fr .front{{position:absolute;left:0;top:{BLEED}in}}
.wband{{position:absolute;left:0;right:0;bottom:0;height:{1.05 + BLEED}in;background:#0b1d13}}
.wbrand{{position:absolute;left:{BLEED + 0.55}in;bottom:{BLEED + 0.38}in;color:#f4f1e8;font-weight:800;letter-spacing:.16em;
  font-size:11pt}}
</style></head><body><div class="wrap">
<div class="wband"></div>
<div class="panel back"><h2>{BACK_HEAD}</h2><p>{html.escape(BACK_BLURB)}</p><ul>{bullets}</ul>
  <div class="fine">{BACK_FINE}</div></div>
<div class="wbrand">MONEY MADE SIMPLE</div>
<div class="panel spine">{spine_text}</div>
<div class="panel fr">{_front(TRIM_W, TRIM_H).replace('class="band"', 'class="band" data-x="1"')}</div>
</div></body></html>'''


# ---------------------------------------------------------------- build

def build_epub(src: str, out: Path, cover_jpg: Path, work: Path) -> Path:
    md = work / "book.md"
    md.write_text(epub_markdown(src))
    meta = work / "meta.yaml"
    meta.write_text(f"""---
title:
- type: main
  text: "{TITLE}"
- type: subtitle
  text: "{SUBTITLE}"
creator:
- role: author
  text: "{AUTHOR}"
lang: en-US
date: "{YEAR}"
rights: "Copyright © {YEAR} {AUTHOR}. All rights reserved."
subject: [Personal finance, Budgeting, Debt, Investing]
description: "{html.escape(KINDLE_DESCRIPTION_SHORT)}"
---
""")
    epub = out / f"{STEM}.epub"
    subprocess.run(["pandoc", "-f", "markdown-tex_math_dollars", "-t", "epub3", str(meta), str(md), "-o", str(epub),
                    "--toc", "--toc-depth=1", "--split-level=1", f"--css={HERE / 'epub.css'}",
                    f"--epub-cover-image={cover_jpg}"], check=True)
    return epub


KINDLE_DESCRIPTION_SHORT = ("A short, plain-English money book: budget in twenty minutes a week, cut your bills, pay "
                            "off debt with a dated plan, fix your credit report and start investing with $100 a month.")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=str(HERE / "dist"))
    ap.add_argument("--skip-pdf", action="store_true")
    a = ap.parse_args()
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    src = resolved_source()
    check_copy(src)
    words = word_count()
    report = [f"words: {words:,}"]
    with tempfile.TemporaryDirectory() as tmp:
        work = Path(tmp)
        (work / "kindle.html").write_text(kindle_cover_html())
        png = work / "kindle.png"
        build_etsy.run_jobs([{"src": str(work / "kindle.html"), "png": str(png), "w": 800, "h": 1280, "scale": 2}])
        from PIL import Image
        jpg = out / f"{STEM}-Kindle-Cover.jpg"
        Image.open(png).convert("RGB").save(jpg, "JPEG", quality=92, optimize=True)
        assert Image.open(jpg).size == (1600, 2560)
        report.append(f"kindle cover: {jpg.name} 1600x2560")
        epub = build_epub(src, out, jpg, work)
        report.append(f"epub: {epub.name} {epub.stat().st_size // 1024} KB")
        if not a.skip_pdf:
            pdf = out / f"{STEM}-Paperback-Interior.pdf"
            (work / "interior.html").write_text(interior_html(src))
            build_etsy.run_jobs([{"src": str(work / "interior.html"), "pdf": str(pdf)}])
            pages = heading_pages(pdf)
            (work / "interior.html").write_text(interior_html(src, pages))
            build_etsy.run_jobs([{"src": str(work / "interior.html"), "pdf": str(pdf)}])
            if heading_pages(pdf) != pages:
                raise SystemExit("contents page numbers moved between passes")
            probs = margin_problems(pdf)
            if probs:
                raise SystemExit("text too close to the edge:\n" + "\n".join(probs[:20]))
            n = pdf_pages(pdf)
            W, H = cover_size(n)
            (work / "cover.html").write_text(paperback_cover_html(n))
            cw, chh = round(W * 96), round(H * 96)
            build_etsy.run_jobs([
                {"src": str(work / "cover.html"), "pdf": str(out / f"{STEM}-Paperback-Cover.pdf"), "w": cw, "h": chh},
                {"src": str(work / "cover.html"), "png": str(out / f"{STEM}-Paperback-Cover-preview.png"),
                 "w": cw, "h": chh}])
            report.append(f"paperback: {n} pages, 6 x 9 in; cover {W} x {H} in (spine {spine_width(n)} in)")
    print("\n".join(report))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
