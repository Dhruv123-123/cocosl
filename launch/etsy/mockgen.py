"""Covers and mockups without Canva: point it at a PDF (or page images), get every store image.

    python launch/etsy/mockgen.py my-planner.pdf --title "Weekly Budget Planner" --price 3
    python launch/etsy/mockgen.py guide.pdf --title "The Debt-Free Date Planner" --price 17 \
        --label "Guide + spreadsheet" --chips "Instant download,PDF + Excel" --pages 1,4,6 --out covers/
    python launch/etsy/mockgen.py --images p1.png p2.png p3.png --title "Savings Bingo" --sizes pin,square

Sizes (pick with --sizes, default all):
    etsy       2700x2025  seven images (laid out at 2000x1500, rendered at 1.35x): 01 clean (fanned pages, no text,
                          as Etsy advises for the first photo), 02 hero (title + pages), 03 inside (page grid),
                          04 details, 05-07 single-page close-ups
    gumroad    1280x720   cover
    square     600x600    thumbnail (Gumroad, Notion Marketplace)
    pin        1000x1500  Pinterest pin
    insta      1080x1350  Instagram portrait post

Only real pages from your file are shown, so the images never promise anything the download doesn't contain.
Needs: Node + Playwright (Chromium) and pdftoppm (poppler), same as the rest of the build.
build_etsy.py also calls this to add a Pinterest pin for every Etsy listing.
"""
from __future__ import annotations

import argparse
import html
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
ETSY_SCALE = 1.35   # Etsy recommends at least 2000 px on both sides: 2000x1500 layouts render at 2700x2025
SIZES = {"etsy": (2000, 1500), "gumroad": (1280, 720), "square": (600, 600), "pin": (1000, 1500), "insta": (1080, 1350)}
FONT = "Inter, system-ui, -apple-system, 'Segoe UI', Roboto, Arial, sans-serif"
INK, CREAM, GREEN, GREEN_D, GOLD = "#0b1d13", "#f4f1e8", "#2fbf71", "#1e8a50", "#f2b134"
E = html.escape


def pdf_pages(pdf: Path, work: Path, dpi: int = 90) -> list[Path]:
    d = work / f"pg-{pdf.stem}"
    d.mkdir(parents=True, exist_ok=True)
    subprocess.run(["pdftoppm", "-r", str(dpi), "-png", str(pdf), str(d / "p")], check=True, capture_output=True)
    return sorted(d.glob("p-*.png"))


def _css(w: int, h: int, bg: str, fg: str) -> str:
    return f"""*{{box-sizing:border-box}} body{{margin:0;width:{w}px;height:{h}px;overflow:hidden;position:relative;
background:{bg};color:{fg};font-family:{FONT}}}
.kick{{letter-spacing:.18em;text-transform:uppercase;font-weight:800;color:{GREEN_D if bg == CREAM else GOLD}}}
h1{{font-weight:900;letter-spacing:-.035em;line-height:.96;margin:0}}
.pg{{position:absolute;background:#fff;border-radius:6px;box-shadow:0 30px 60px rgba(11,29,19,.30),0 4px 12px rgba(11,29,19,.18)}}
.price{{display:inline-block;background:{GREEN};color:{INK};font-weight:900;border-radius:999px}}
.chips{{display:flex;flex-wrap:wrap;gap:14px}} .chips span{{border:3px solid {fg};border-radius:999px;font-weight:700;
background:{'#fff' if bg == CREAM else 'transparent'}}}
.brand{{position:absolute;font-weight:800;letter-spacing:.14em}}"""


def _doc(w, h, body, bg=CREAM, fg=INK) -> str:
    return f'<!doctype html><html><head><meta charset="utf-8"><style>{_css(w, h, bg, fg)}</style></head><body>{body}</body></html>'


def _img(p: Path, style: str) -> str:
    return f'<img class="pg" src="file://{p}" style="{style}">'


def _price(price) -> str:
    if price is None or price == "":
        return ""
    return "FREE" if float(price) == 0 else f"${float(price):g}" if float(price) % 1 else f"${int(float(price))}"


def fan(pages: list[Path], x: int, y: int, w: int, spread: int) -> str:
    """Up to three real pages fanned out; the middle one on top."""
    p = pages[:3]
    if len(p) == 1:
        return _img(p[0], f"left:{x + spread}px;top:{y}px;width:{w}px;transform:rotate(-2deg)")
    spots = [(x, y + 60, -7), (x + 2 * spread, y + 80, 7), (x + spread, y, 0)][:len(p)]
    order = [p[1], p[2], p[0]] if len(p) == 3 else [p[1], p[0]]
    return "".join(_img(pg, f"left:{sx}px;top:{sy}px;width:{w}px;transform:rotate({r}deg)") for pg, (sx, sy, r) in zip(order, spots))


def hero(o: dict, pages: list[Path], w: int, h: int) -> str:
    """Title block + fanned pages. Lays out landscape, square and portrait sizes."""
    title, label, price, chips = E(o["title"]), E(o.get("label") or ""), _price(o.get("price")), o.get("chips") or []
    s = min(w, h) / 1000
    if abs(w - h) <= w * .15:
        chips = []
    chip = "".join(f'<span style="font-size:{26 * s:.0f}px;padding:{9 * s:.0f}px {20 * s:.0f}px">{E(c)}</span>' for c in chips)
    tsize = (100 if len(o["title"]) < 24 else 82 if len(o["title"]) < 36 else 66) * s * (1.25 if h > w else 1)
    pr = f'<span class="price" style="font-size:{34 * s:.0f}px;padding:{8 * s:.0f}px {26 * s:.0f}px;margin-top:{24 * s:.0f}px">{price}</span>' if price else ""
    sub = f'<div style="font-size:{34 * s:.0f}px;line-height:1.3;color:#4b5a51;margin-top:{18 * s:.0f}px">{E(o["subtitle"])}</div>' if o.get("subtitle") else ""
    text = (f'<div class="kick" style="font-size:{24 * s:.0f}px">{label}</div><h1 style="font-size:{tsize:.0f}px;margin-top:{18 * s:.0f}px">{title}</h1>'
            f'{sub}{pr}<div class="chips" style="margin-top:{28 * s:.0f}px">{chip}</div>')
    brand = f'<div class="brand" style="font-size:{22 * s:.0f}px;left:{60 * s:.0f}px;bottom:{40 * s:.0f}px">{E(o.get("brand", ""))}</div>'
    if w > h * 1.15:      # landscape: text left, pages right
        tw = int(w * 0.42)
        pw = int(h * 0.62 / 1.294 * 1.0) if h / w < .6 else int(w * 0.28)
        body = (f'<div style="position:absolute;left:{int(w * .05)}px;top:0;bottom:0;width:{tw}px;display:flex;flex-direction:column;'
                f'justify-content:center;align-items:flex-start">{text}</div>'
                + fan(pages, int(w * .47), int(h * .2), pw, int(pw * .38)) + brand)
    elif h > w * 1.15:    # portrait: text top, pages bottom
        pw = int(w * .5)
        body = (f'<div style="position:absolute;left:{int(w * .07)}px;right:{int(w * .07)}px;top:{int(h * .06)}px">{text}</div>'
                + fan(pages, int(w * .06), int(h * .46), pw, int(w * .19)) + brand.replace("bottom:", "top:").replace(f"left:{60 * s:.0f}px", f"right:{60 * s:.0f}px"))
    else:                 # square
        pw = int(w * .42)
        body = (f'<div style="position:absolute;left:{int(w * .07)}px;right:{int(w * .07)}px;top:{int(h * .07)}px">{text}</div>'
                + fan(pages, int(w * .1), int(h * .52), pw, int(w * .2)))
    return _doc(w, h, body, o.get("bg", CREAM), INK if o.get("bg", CREAM) == CREAM else CREAM)


def clean(pages: list[Path], w: int, h: int, bg: str = CREAM) -> str:
    """The first photo: real pages fanned and centred, no text, so square and portrait crops keep the item."""
    pw = int(min(w * .4, h * .72 / 1.294))
    spread = int(pw * .42)
    x = (w - pw - 2 * spread) // 2 if len(pages) > 1 else (w - pw) // 2 - spread
    return _doc(w, h, fan(pages, x, int((h - pw * 1.294) / 2) - 40, pw, spread), bg)


def closeup(page: Path, w: int, h: int, bg: str = CREAM) -> str:
    """One page, big enough to read, centred."""
    ph = int(h * .9)
    return _doc(w, h, f'<img class="pg" src="file://{page}" style="left:50%;top:{(h - ph) // 2}px;height:{ph}px;'
                      f'transform:translateX(-50%)">', bg)


def etsy_set(o: dict, pages: list[Path], w: int, h: int, inside_pages: list[Path] | None = None,
             count: int | None = None) -> list[tuple[str, str]]:
    """(name, html) for the Etsy photo set, in upload order."""
    bg = o.get("bg", CREAM)
    out = [("mockup-01-clean", clean(pages, w, h, bg)), ("mockup-02-hero", hero(o, pages, w, h)),
           ("mockup-03-inside", inside(o, inside_pages or pages, w, h, count)), ("mockup-04-details", details(o, pages, w, h))]
    out += [(f"mockup-{5 + i:02d}-page-{i + 1}", closeup(p, w, h, bg)) for i, p in enumerate(pages[:3])]
    return out


def clear_old(out: Path) -> None:
    """Remove mockups from an earlier layout (only our own mockup-*.png files in this listing folder)."""
    for p in out.glob("mockup-*.png"):
        p.unlink()


WHATS_INSIDE = "What's inside"


def inside(o: dict, pages: list[Path], w: int, h: int, count: int | None = None) -> str:
    n = len(pages)
    cols = 5 if n > 8 else (4 if n > 3 else max(n, 1))
    rows = (n + cols - 1) // cols
    tw = min(460, int((w - 180 - (cols - 1) * 34) / cols), int((h - 330 - (rows - 1) * 34) / max(rows, 1) / 1.294))
    imgs = "".join(f'<img src="file://{p}" style="width:100%;box-shadow:0 18px 40px rgba(0,0,0,.35);border-radius:4px;background:#fff">' for p in pages)
    t = o.get("text") or {}  # optional wording for other languages; English by default
    what = (t["inside_count"].format(n=count) if count else t["inside_pages"].format(n=n)) if "inside_pages" in t else \
        (f"{count} items you get" if count else f"{n} of the pages you get")
    body = (f'<div style="padding:80px 90px 0"><div class="kick" style="font-size:30px">{E(t.get("inside_kick", WHATS_INSIDE))}</div>'
            f'<h1 style="font-size:84px;margin:12px 0 30px">{E(what)}</h1></div>'
            f'<div style="display:grid;gap:34px;justify-content:center;grid-template-columns:repeat({cols},{tw}px);padding:0 90px">{imgs}</div>')
    return _doc(w, h, body, INK, CREAM)


def details(o: dict, pages: list[Path], w: int, h: int) -> str:
    steps = o.get("steps") or [("Download", "Your files are ready the moment you pay."), ("Print", "US Letter or A4, at home, as often as you like."),
                               ("Fill in", "With a pen, or on a tablet in any app that writes on PDFs.")]
    st = "".join(f'<div style="background:#fff;border:4px solid {INK};border-radius:28px;padding:48px 44px"><div style="width:84px;height:84px;'
                 f'border-radius:50%;background:{GREEN};font-size:46px;font-weight:900;display:flex;align-items:center;justify-content:center;'
                 f'margin-bottom:22px">{i}</div><div style="font-size:46px;font-weight:800;margin-bottom:12px">{E(a)}</div>'
                 f'<div style="font-size:34px;line-height:1.35;color:#4b5a51">{E(b)}</div></div>' for i, (a, b) in enumerate(steps, 1))
    bullets = "".join(f"<li style='margin-bottom:8px'>{E(b)}</li>" for b in (o.get("bullets") or [])[:3])
    side = _img(pages[0], "left:1460px;top:800px;width:430px;transform:rotate(4deg)") if pages else ""
    t = o.get("text") or {}
    body = (f'<div style="padding:90px"><div class="kick" style="font-size:30px">{E(t.get("how_kick", "How it works"))}</div>'
            f'<h1 style="font-size:84px;margin:12px 0 30px">{E(t.get("how_title", "Ready in minutes"))}</h1>'
            f'<div style="display:grid;grid-template-columns:repeat(3,1fr);gap:40px">{st}</div>'
            + (f'<div class="kick" style="font-size:30px;margin-top:56px">{E(t.get("get_kick", "What you get"))}</div><ul style="font-size:36px;line-height:1.45;width:1280px;'
               f'padding-left:38px">{bullets}</ul>' if bullets else "") + f'</div>{side}'
            f'<div class="brand" style="left:90px;right:90px;bottom:60px;font-size:28px;display:flex;justify-content:space-between">'
            f'<span>{E(o.get("brand", ""))}</span><span>{E(o.get("footer", ""))}</span></div>')
    return _doc(w, h, body)


def generate(o: dict, pages: list[Path], out: Path, sizes=tuple(SIZES), run=None, inside_pages: list[Path] | None = None,
             count: int | None = None, prefix: str = "") -> list[Path]:
    """Write the images for one product. o: title, label, price, subtitle, chips, bullets, steps, brand, footer.
    pages: hero pages in order (first is the main one). Returns the PNG paths."""
    if run is None:
        from build_etsy import run_jobs as run
    out.mkdir(parents=True, exist_ok=True)
    work = Path(tempfile.mkdtemp(prefix="mockgen-"))
    jobs, outs = [], []

    def add(name, doc, w, h, scale=1):
        src = work / f"{name}.html"
        src.write_text(doc)
        png = out / f"{prefix}{name}.png"
        jobs.append({"src": str(src), "png": str(png), "w": w, "h": h, "scale": scale})
        outs.append(png)
    for size in sizes:
        w, h = SIZES[size]
        if size == "etsy":
            if not prefix:
                clear_old(out)
            for name, doc in etsy_set(o, pages, w, h, inside_pages, count):
                add(name, doc, w, h, ETSY_SCALE)
        else:
            add({"gumroad": "cover", "square": "cover-square", "pin": "pin", "insta": "insta"}[size],
                hero({**o, "bg": INK} if size in ("gumroad", "square") else o, pages, w, h), w, h)
    run(jobs)
    return outs


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("pdf", nargs="?", help="the product PDF (or use --images)")
    ap.add_argument("--images", nargs="*", help="page images instead of a PDF")
    ap.add_argument("--title", required=True)
    ap.add_argument("--subtitle")
    ap.add_argument("--price", type=float)
    ap.add_argument("--label", default="Printable · digital download")
    ap.add_argument("--chips", default="Instant download,Letter + A4,Print at home", help="comma-separated")
    ap.add_argument("--bullets", default="", help="'|'-separated lines for the details image")
    ap.add_argument("--brand", default="MONEY MADE SIMPLE")
    ap.add_argument("--footer", default="Digital file · nothing is shipped")
    ap.add_argument("--pages", default="", help="page numbers for the hero, e.g. 2,3,1 (default: 1,2,3)")
    ap.add_argument("--sizes", default=",".join(SIZES))
    ap.add_argument("--out", default="mockups")
    a = ap.parse_args()
    sys.path.insert(0, str(HERE))
    work = Path(tempfile.mkdtemp(prefix="mockgen-pages-"))
    if a.images:
        allp = [Path(p).resolve() for p in a.images]
    elif a.pdf:
        allp = pdf_pages(Path(a.pdf).resolve(), work)
    else:
        ap.error("give a PDF or --images")
    pick = [int(x) for x in a.pages.split(",") if x.strip()] or [1, 2, 3]
    hero_pages = [allp[i - 1] for i in pick if 0 < i <= len(allp)] or allp[:3]
    o = dict(title=a.title, subtitle=a.subtitle, price=a.price, label=a.label, brand=a.brand, footer=a.footer,
             chips=[c.strip() for c in a.chips.split(",") if c.strip()], bullets=[b for b in a.bullets.split("|") if b.strip()])
    outs = generate(o, hero_pages, Path(a.out), [s.strip() for s in a.sizes.split(",")], inside_pages=allp[:15])
    for p in outs:
        print(p)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
