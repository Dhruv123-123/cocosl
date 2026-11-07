"""Build the print-on-demand starter set: print-ready PNGs (3 aspect ratios, 300 DPI), previews and listing copy.

    python launch/pod/build_pod.py [--only slug ...] [--out launch/pod/dist]

Nothing is uploaded anywhere. Output is git-ignored (dist/).
"""
from __future__ import annotations

import argparse
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(ROOT / "launch" / "etsy"))

import build_etsy  # noqa: E402
import posters  # noqa: E402

CSS_PX = 96


def poster_html(p: dict, ratio: str) -> str:
    """The printable page's chart, re-set as a poster: big title band, the chart centred and scaled up, brand footer."""
    r = posters.RATIOS[ratio]
    body = build_etsy.ALL_PRINTABLES[p["source"]]()[p["page"] - 1]
    chart = body[body.index('<div class="fill">') + len('<div class="fill">'):body.index('<div class="foot">')]
    chart = chart[:chart.rindex("</div>")]
    title = p["name"].replace(" Poster", "")
    words = title.split()
    head = " ".join(words[:-1]) + f' <em>{words[-1]}</em>' if len(words) > 1 else title
    sub = p["hook"].split(". ")[0].rstrip(".") + "."
    css = (build_etsy.HERE / "printables.css").read_text().replace(
        "--w:8.5in; --h:11in;", f"--w:{r['w_in']}in; --h:{r['h_in']}in;")
    extra = f"""html,body{{background:#fff}} .page{{margin:0;padding:0.55in 0.6in 0.45in}}
      .ptop{{text-align:center;margin-bottom:0.16in}}
      .ptop .kick{{font-size:10pt;margin-bottom:6px}}
      .ptop h1{{font-size:{p.get('title_pt', 40)}pt;font-weight:900;letter-spacing:-.03em;line-height:1;margin:0}}
      .ptop h1 em{{font-style:normal;color:var(--green-d)}}
      .ptop p{{font-size:11pt;color:var(--muted);margin:8px auto 0;max-width:6.4in}}
      .chart{{flex:1;display:flex;flex-direction:column;justify-content:center;zoom:{p.get('zoom', 1.12)}}}
      .chart [style*="margin-top:auto"]{{margin-top:0.3in !important}}
      .pfoot{{display:flex;justify-content:space-between;align-items:center;border-top:2px solid var(--ink);padding-top:8px;
        margin-top:0.12in;font-size:9pt;font-weight:800;letter-spacing:.12em;text-transform:uppercase}}
      .pfoot span:last-child{{color:var(--green-d);letter-spacing:.04em;text-transform:none;font-weight:600}}"""
    page = (f'<div class="ptop"><div class="kick">Colour it in as you go</div><h1>{head}</h1><p>{sub}</p></div>'
            f'<div class="chart">{chart}</div>'
            f'<div class="pfoot"><span>Money Made Simple</span><span>An organising tool, not financial advice</span></div>')
    return (f'<!doctype html><html><head><meta charset="utf-8"><style>{css}\n{extra}</style></head>'
            f'<body><section class="page">{page}</section></body></html>')


def listing_md(p: dict) -> str:
    tags = "\n".join(f"{i}. {t}" for i, t in enumerate(p["tags"], 1))
    files = "\n".join(f"- `{p['slug']}-{k}.png` ({v['px'][0]}x{v['px'][1]} px): {v['sizes']}" for k, v in posters.RATIOS.items())
    return f"""# {p['name']} (print on demand)

Made from page {p['page']} of the `{p['source']}` printable. Nothing here has been uploaded or listed.

## Print files (PNG, sRGB, 300 DPI at the largest size listed)
{files}

In Printify: Add product > Posters (matte, vertical) > upload the master whose shape matches the size, then check the
print-area preview for every size you enable. Turn off any size whose preview crops the chart.

## Title ({len(p['title'])}/140, {len(p['title'].split())} words)
{p['title']}

## Tags
{tags}

## Price
{posters.PRICE_NOTE}

## Etsy settings
- **Who made it:** I did. **What is it:** A finished product. **Production partner:** your Printify print provider
  (Shop Manager > Settings > Production partners), and say so in the description (already in the text below).
- **Section:** Wall Posters. **Category:** Art & Collectibles > Prints > Posters (or the closest Etsy offers).
- **Attributes:** Orientation: Vertical. Primary color: White. Secondary color: Green. Framing: Unframed (or as chosen).

## Photos
First photo: `listing-01-framed-square.jpg` (2400x2400, square, no text: Etsy wants the first photo landscape or
square). Then Printify's own room and frame mockups for the sizes you enable. `preview.jpg` is for your own checks.

## Description
```
{posters.description(p)}
```
"""


def framed_square(poster) -> "Image.Image":
    """Etsy's first photo must be landscape or square: the real poster in a plain frame, centred on a wall, no text.
    2400x2400. Printify's room mockups can follow as photos 2 onwards."""
    from PIL import Image, ImageDraw, ImageFilter
    S = 2400
    img = Image.new("RGB", (S, S), "#ece8df")
    ph = 1500
    pw = ph * 3 // 4
    art = poster.convert("RGB").resize((pw, ph), Image.LANCZOS)
    mat, frame = 70, 26
    fw, fh = pw + 2 * (mat + frame), ph + 2 * (mat + frame)
    x, y = (S - fw) // 2, (S - fh) // 2 - 60
    shadow = Image.new("L", (S, S), 0)
    ImageDraw.Draw(shadow).rectangle([x + 18, y + 40, x + fw + 18, y + fh + 40], fill=120)
    img.paste(Image.new("RGB", (S, S), "#b9b3a6"), (0, 0), shadow.filter(ImageFilter.GaussianBlur(40)))
    d = ImageDraw.Draw(img)
    d.rectangle([x, y, x + fw, y + fh], fill="#1d1d1b")
    d.rectangle([x + frame, y + frame, x + fw - frame, y + fh - frame], fill="#fbfaf6")
    img.paste(art, (x + frame + mat, y + frame + mat))
    return img


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--only", nargs="*")
    ap.add_argument("--out", default=str(HERE / "dist"))
    args = ap.parse_args()
    out = Path(args.out)
    items = [p for p in posters.POSTERS if not args.only or p["slug"] in args.only]
    work = Path(tempfile.mkdtemp(prefix="pod-"))
    jobs, checks = [], []
    for p in items:
        d = out / p["slug"]
        d.mkdir(parents=True, exist_ok=True)
        for k, r in posters.RATIOS.items():
            src = work / f"{p['slug']}-{k}.html"
            src.write_text(poster_html(p, k))
            w, h = round(r["w_in"] * CSS_PX), round(r["h_in"] * CSS_PX)
            jobs.append({"src": str(src), "png": str(d / f"{p['slug']}-{k}.png"), "w": w, "h": h, "scale": r["px"][0] / w})
            checks.append({"src": str(src), "pdf": str(work / f"{p['slug']}-{k}.pdf"), "w": w, "h": h})
        (d / "LISTING.md").write_text(listing_md(p))
    failures = [f"{Path(r['out']).name}: overflow {r['overflow']}" for r in build_etsy.run_jobs(checks) if r["overflow"]]
    for j in jobs:  # one at a time keeps memory down for 30-40 MP screenshots
        build_etsy.run_jobs([j])
    from PIL import Image
    Image.MAX_IMAGE_PIXELS = None
    for p in items:
        d = out / p["slug"]
        for k, r in posters.RATIOS.items():
            f = d / f"{p['slug']}-{k}.png"
            with Image.open(f) as im:
                if im.size != r["px"]:
                    failures.append(f"{f.name}: {im.size} != {r['px']}")
                if k == "3x4":
                    im.convert("RGB").resize((900, 1200)).save(d / "preview.jpg", quality=85)
                    framed_square(im).save(d / "listing-01-framed-square.jpg", quality=90)
            if f.stat().st_size > 100 * 1024 * 1024:
                failures.append(f"{f.name}: over Printify's 100 MB limit")
    if items and not args.only:
        sheet = Image.new("RGB", (5 * 460 + 60, 2 * 620 + 40), "#f4f1e8")
        for i, p in enumerate(items):
            with Image.open(out / p["slug"] / "preview.jpg") as im:
                sheet.paste(im.resize((420, 560)), (40 + (i % 5) * 460, 30 + (i // 5) * 620))
        sheet.save(out / "contact-sheet.jpg", quality=85)
    for f in failures:
        print("FAIL", f)
    print(f"built {len(items)} poster(s) into {out}")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
