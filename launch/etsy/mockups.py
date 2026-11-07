"""Listing images for Etsy: 2000x1500 (4:3) PNGs built from the real pages of each product.

01 hero (the thumbnail), 02 what's inside, 03 how it works / details. Only real pages are shown, so the
images never promise anything the download doesn't contain.
"""
from __future__ import annotations

import html
from pathlib import Path

import listings

W, H = 2000, 1500
CSS = """
*{box-sizing:border-box} body{margin:0;width:2000px;height:1500px;overflow:hidden;font-family:Inter,system-ui,sans-serif;color:#0b1d13}
.cream{background:#f4f1e8} .ink{background:#0b1d13;color:#f4f1e8}
.kick{letter-spacing:.2em;text-transform:uppercase;font-weight:800;font-size:30px;color:#1e8a50}
.ink .kick{color:#f2b134}
h1{font-size:112px;line-height:.95;font-weight:900;letter-spacing:-.035em;margin:26px 0}
h2{font-size:84px;font-weight:900;letter-spacing:-.03em;margin:0 0 30px}
.chips{display:flex;flex-wrap:wrap;gap:16px;margin-top:34px}
.chips span{border:3px solid #0b1d13;border-radius:999px;padding:12px 26px;font-size:30px;font-weight:700;background:#fff}
.pg{position:absolute;background:#fff;box-shadow:0 30px 60px rgba(11,29,19,.28),0 4px 12px rgba(11,29,19,.18);border-radius:6px}
.badge{position:absolute;right:70px;top:60px;background:#2fbf71;color:#0b1d13;font-weight:900;font-size:34px;padding:16px 30px;border-radius:999px}
.grid{display:grid;gap:34px;justify-content:center}
.grid img{width:100%;box-shadow:0 18px 40px rgba(0,0,0,.35);border-radius:4px;background:#fff}
.steps{display:grid;grid-template-columns:repeat(3,1fr);gap:40px;margin-top:20px}
.step{background:#fff;border:4px solid #0b1d13;border-radius:28px;padding:48px 44px}
.step .n{width:84px;height:84px;border-radius:50%;background:#2fbf71;font-size:46px;font-weight:900;display:flex;align-items:center;justify-content:center;margin-bottom:22px}
.step h3{font-size:46px;margin:0 0 12px} .step p{font-size:34px;line-height:1.35;margin:0;color:#4b5a51}
ul.inc{font-size:32px;line-height:1.45;margin:30px 0 0;padding-left:38px} ul.inc li{margin-bottom:8px}
.foot{position:absolute;left:90px;right:90px;bottom:60px;display:flex;justify-content:space-between;font-size:28px;font-weight:700}
"""


def _doc(body: str, cls: str) -> str:
    return f'<!doctype html><html><head><meta charset="utf-8"><style>{CSS}</style></head><body class="{cls}">{body}</body></html>'


def _pages_for(it: dict, out_dir: Path, work: Path, page_images) -> tuple[list[Path], list[Path]]:
    """(hero page images, inside page images) for a listing."""
    if it["kind"] == "printable":
        pdf = next(out_dir.glob("*-Letter.pdf"))
    elif it["slug"] == "20-minute-budget":
        pdf = out_dir / "The-20-Minute-Budget.pdf"
    elif it.get("bundle") and it["kind"] == "bundle":
        pdf = None
    else:
        pdf = next(p for p in out_dir.glob("*.pdf"))
    if pdf is None or (it.get("bundle") and it["slug"] == "money-toolkit-bundle"):
        firsts = []
        for slug in it["bundle"]:
            sub = listings.BY_SLUG[slug]
            sd = out_dir.parent / slug
            spdf = next(sd.glob("*-Letter.pdf")) if sub["kind"] == "printable" else (
                sd / "The-20-Minute-Budget.pdf" if slug == "20-minute-budget" else next(sd.glob("*.pdf")))
            n = sub.get("hero", [1])[0] if sub["kind"] == "printable" else 1
            firsts += page_images(spdf, work / f"m-{it['slug']}", slug, n, n, 90)
        return firsts[:3], firsts
    imgs = page_images(pdf, work / f"m-{it['slug']}", "p", 1, 99, 90)
    pick = lambda idx: [imgs[i - 1] for i in idx if 0 < i <= len(imgs)]  # noqa: E731
    return pick(it.get("hero", [1, 2, 3])), pick(it.get("grid", list(range(1, 9))))


def _chips(it: dict) -> list[str]:
    if it["kind"] == "printable":
        return ["Instant download", "Letter + A4", "Undated", "Print at home"]
    if it["kind"] == "bundle":
        return ["Instant download", f"{len(it['bundle'])} printables", "Letter + A4", "Undated"]
    if it.get("bundle"):
        return ["Instant download", "5 guides + 5 spreadsheets", "Excel + Google Sheets"]
    return ["Instant download", "PDF guide", "Excel + Google Sheets + Numbers"]


def render(it: dict, out_dir: Path, work: Path, run_jobs, page_images) -> list[Path]:
    hero, inside = _pages_for(it, out_dir, work, page_images)
    name = html.escape(it["name"]).replace("$", "&#36;")
    kick = {"printable": "Printable &middot; digital download", "bundle": "Printable bundle &middot; digital download"}.get(
        it["kind"], "Guide + spreadsheet &middot; digital download")
    # 01 hero: three real pages fanned on the right
    pos = [(900, 400, -7, 560), (1130, 320, 0, 600), (1360, 420, 7, 560)][:len(hero)]
    pages = "".join(
        f'<img class="pg" src="file://{p}" style="left:{x}px;top:{y}px;width:{w}px;transform:rotate({r}deg)">'
        for p, (x, y, r, w) in zip(hero, pos))
    chips = "".join(f"<span>{c}</span>" for c in _chips(it))
    body1 = f'''<div style="position:absolute;left:90px;top:0;bottom:0;width:760px;display:flex;flex-direction:column;justify-content:center">
      <div class="kick">{kick}</div><h1 style="font-size:{96 if len(it["name"]) < 26 else 78}px">{name}</h1>
      <div style="font-size:38px;line-height:1.35;color:#4b5a51">{html.escape(it["hook"].split(". ")[0].rstrip("."))}.</div>
      <div class="chips">{chips}</div></div>{pages}
      <div class="foot"><span>MONEY MADE SIMPLE</span><span style="color:#1e8a50">Digital file &middot; nothing is shipped</span></div>'''
    # 02 inside: grid of real pages
    n = len(inside)
    cols = 5 if n > 8 else (4 if n > 3 else n)
    rows_ = (n + cols - 1) // cols
    tw = min(460, int((1820 - (cols - 1) * 34) / cols), int((1500 - 330 - (rows_ - 1) * 34) / rows_ / 1.294))
    grid = "".join(f'<img src="file://{p}">' for p in inside)
    body2 = f'''<div style="padding:80px 90px 0"><div class="kick">What's inside</div><h2>{len(inside)} {"items" if it.get("bundle") else "of the pages"} you get</h2></div>
      <div class="grid" style="grid-template-columns:repeat({cols},{tw}px);padding:0 90px">{grid}</div>'''
    # 03 details
    if it["kind"] == "product":
        steps = [("Download", "Your files are in Etsy &gt; Purchases right after you pay."),
                 ("Open", "Read the PDF guide. Open the spreadsheet in Excel, Google Sheets or Numbers."),
                 ("Fill in", "Type into the yellow cells. Everything else calculates for you.")]
    else:
        steps = [("Download", "Your files are in Etsy &gt; Purchases right after you pay."),
                 ("Print", "US Letter or A4. Print at 100%, as often as you like for personal use."),
                 ("Fill in", "With a pen, or on a tablet in any app that lets you write on PDFs.")]
    st = "".join(f'<div class="step"><div class="n">{i}</div><h3>{a}</h3><p>{b}</p></div>' for i, (a, b) in enumerate(steps, 1))
    inc = "".join(f"<li>{html.escape(g)}</li>" for g in it["get"][:3])
    side = f'<img class="pg" src="file://{hero[0]}" style="left:1460px;top:800px;width:430px;transform:rotate(4deg)">' if hero else ""
    body3 = f'''<div style="padding:90px"><div class="kick">How it works</div><h2>Ready in minutes</h2><div class="steps">{st}</div>
      <div class="kick" style="margin-top:56px">What you get</div><ul class="inc" style="width:1280px;font-size:36px">{inc}</ul></div>{side}
      <div class="foot"><span>MONEY MADE SIMPLE</span><span>Educational / organising tool, not financial advice</span></div>'''
    jobs, outs = [], []
    for i, (body, cls, label) in enumerate([(body1, "cream", "hero"), (body2, "ink", "inside"), (body3, "cream", "details")], 1):
        src = work / f"mock-{it['slug']}-{i}.html"
        src.write_text(_doc(body, cls))
        out = out_dir / f"mockup-{i:02d}-{label}.png"
        jobs.append({"src": str(src), "png": str(out), "w": W, "h": H})
        outs.append(out)
    run_jobs(jobs)
    return outs
