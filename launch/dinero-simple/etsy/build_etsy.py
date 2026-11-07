"""Etsy editions of the five Dinero Simple products, with Spanish listings and listing images.

    python launch/dinero-simple/products/build.py          # first: PDFs and workbooks -> products/dist/
    python launch/dinero-simple/etsy/build_etsy.py [--out DIR]

Per product, DIR/<slug>/ gets the files to upload (Etsy: up to 5 files, 20 MB each), four 2700x2025
listing images (mockup-01-clean.png, the pages alone with no text, is the thumbnail) and LISTING.md
(title under 15 words, 13 tags, price, a description that opens with what the item is).
DIR/listings.csv has one row per listing.

Etsy rules this follows: the Etsy edition of each guide has no discount codes, store links or "reply to
your purchase email" lines (buyers are sent to Etsy messages and the shop instead), downloads come from
Etsy's Purchases page, and every description says AI tools helped.
"""
from __future__ import annotations

import argparse
import csv
import html
import re
import shutil
import subprocess
import sys
import tempfile
import zipfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
DS = HERE.parent
sys.path.insert(0, str(DS / "products"))

import build as products  # noqa: E402  (launch/dinero-simple/products/build.py)
from listings import LISTINGS, SHOP  # noqa: E402

DIST = DS / "products" / "dist"
MAX_MB = 20
PHOTO_SCALE = 1.35  # 2000x1500 layout rendered at 2700x2025: Etsy asks for at least 2000 px on both sides


def etsy_edition(product: dict) -> str:
    """The guide with every off-Etsy line (codes, store links, purchase-email support) swapped for Etsy-safe ones."""
    src = products.wrap_guide(product)
    src = re.sub(r"<p>Si compraste [^<]*c[óo]digo <strong>[A-Z0-9]+</strong>[^<]*</p>",
                 f"<p>Búscalo en la tienda {SHOP} en Etsy.</p>", src)
    src = src.replace("<p>¿Ya compraste uno? Contesta tu correo de compra y te mandamos un código por la diferencia.</p>",
                      "<p>¿Ya compraste uno de los kits? Escríbele a la tienda por mensajes de Etsy antes de comprar.</p>")
    src = src.replace("Los dos en [el enlace de tu tienda].", f"Los dos en la tienda {SHOP} en Etsy.")
    src = src.replace("¿Algo no funciona, o tienes una pregunta? Contesta tu correo de compra.",
                      "¿Algo no funciona, o tienes una pregunta? Escríbele a la tienda por mensajes de Etsy.")
    left = [x for x in ("código <strong>", "[el enlace de tu tienda]", "correo de compra", "gumroad") if x in src.lower() or x in src]
    if left:
        raise SystemExit(f"{product['slug']}: Etsy edition still mentions {left}")
    return src


def page_images(pdf: Path, out_dir: Path, prefix: str, dpi: int = 80) -> list[Path]:
    out_dir.mkdir(parents=True, exist_ok=True)
    subprocess.run(["pdftoppm", "-r", str(dpi), "-png", str(pdf), str(out_dir / prefix)], check=True, capture_output=True)
    return sorted(out_dir.glob(f"{prefix}-*.png"))


CSS = """
*{box-sizing:border-box} body{margin:0;width:2000px;height:1500px;overflow:hidden;font-family:Inter,system-ui,sans-serif;color:#14213d}
.cream{background:#fbf5e9} .ink{background:#14213d;color:#fbf5e9}
.kick{letter-spacing:.2em;text-transform:uppercase;font-weight:800;font-size:30px;color:#e2603f}
.ink .kick{color:#ff7a59}
h1{line-height:.97;font-weight:900;letter-spacing:-.035em;margin:26px 0}
h2{font-size:84px;font-weight:900;letter-spacing:-.03em;margin:0 0 30px}
.chips{display:flex;flex-wrap:wrap;gap:16px;margin-top:34px}
.chips span{border:3px solid #14213d;border-radius:999px;padding:12px 26px;font-size:30px;font-weight:700;background:#fff}
.pg{position:absolute;background:#fff;box-shadow:0 30px 60px rgba(20,33,61,.3),0 4px 12px rgba(20,33,61,.18);border-radius:6px}
.price{display:inline-block;background:#2ab7a9;color:#14213d;font-weight:900;font-size:40px;padding:12px 30px;border-radius:999px;margin-top:30px}
.grid{display:grid;gap:34px;justify-content:center}
.grid img{width:100%;box-shadow:0 18px 40px rgba(0,0,0,.35);border-radius:4px;background:#fff}
.steps{display:grid;grid-template-columns:repeat(3,1fr);gap:40px;margin-top:20px}
.step{background:#fff;border:4px solid #14213d;border-radius:28px;padding:44px 40px}
.step .n{width:84px;height:84px;border-radius:50%;background:#2ab7a9;font-size:46px;font-weight:900;display:flex;align-items:center;justify-content:center;margin-bottom:22px}
.step h3{font-size:46px;margin:0 0 12px} .step p{font-size:33px;line-height:1.35;margin:0;color:#4a5677}
ul.inc{font-size:34px;line-height:1.45;margin:30px 0 0;padding-left:38px;width:1260px} ul.inc li{margin-bottom:8px}
.foot{position:absolute;left:90px;right:90px;bottom:60px;display:flex;justify-content:space-between;font-size:28px;font-weight:700}
"""


def _doc(body: str, cls: str) -> str:
    return f'<!doctype html><html lang="es"><head><meta charset="utf-8"><style>{CSS}</style></head><body class="{cls}">{body}</body></html>'


def mockups(it: dict, hero: list[Path], inside: list[Path], out_dir: Path, work: Path) -> list[dict]:
    name = html.escape(it["name"]).replace("$", "&#36;")
    pos = [(900, 400, -7, 560), (1130, 320, 0, 600), (1360, 420, 7, 560)][:len(hero)]
    pages = "".join(f'<img class="pg" src="file://{p}" style="left:{x}px;top:{y}px;width:{w}px;transform:rotate({r}deg)">'
                    for p, (x, y, r, w) in zip(hero, pos))
    chips = "".join(f"<span>{html.escape(c)}</span>" for c in it["chips"])
    size = 92 if len(it["name"]) < 24 else 76
    b1 = f'''<div style="position:absolute;left:90px;top:0;bottom:0;width:780px;display:flex;flex-direction:column;justify-content:center">
      <div class="kick">En español &middot; descarga digital</div><h1 style="font-size:{size}px">{name}</h1>
      <div style="font-size:38px;line-height:1.35;color:#4a5677">{html.escape(it["pitch"])}</div>
      <div class="chips">{chips}</div></div>{pages}
      <div class="foot"><span>DINERO SIMPLE</span><span style="color:#e2603f">Archivo digital &middot; no se envía nada</span></div>'''
    n = len(inside)
    cols = 5 if n > 8 else (4 if n > 3 else n)
    rows = (n + cols - 1) // cols
    tw = min(460, int((1820 - (cols - 1) * 34) / cols), int((1500 - 330 - (rows - 1) * 34) / rows / 1.294))
    grid = "".join(f'<img src="file://{p}">' for p in inside)
    b2 = f'''<div style="padding:80px 90px 0"><div class="kick">Lo que incluye</div><h2>{html.escape(it["inside_title"])}</h2></div>
      <div class="grid" style="grid-template-columns:repeat({cols},{tw}px);padding:0 90px">{grid}</div>'''
    steps = [("Descarga", "Tus archivos están en Etsy &gt; Compras justo después de pagar."),
             ("Abre", "Lee la guía en PDF. Abre la hoja en Excel, Google Sheets o Numbers."),
             ("Llena", "Escribe en las celdas amarillas. Lo demás se calcula solo.")]
    st = "".join(f'<div class="step"><div class="n">{i}</div><h3>{a}</h3><p>{b}</p></div>' for i, (a, b) in enumerate(steps, 1))
    inc = "".join(f"<li>{html.escape(g)}</li>" for g in it["get"][:4 if it.get("bundle_of") else 3])
    side = f'<img class="pg" src="file://{hero[0]}" style="left:1470px;top:790px;width:420px;transform:rotate(4deg)">' if hero else ""
    b3 = f'''<div style="padding:90px"><div class="kick">Cómo funciona</div><h2>Listo en minutos</h2><div class="steps">{st}</div>
      <div class="kick" style="margin-top:56px">Lo que recibes</div><ul class="inc">{inc}</ul></div>{side}
      <div class="foot"><span>DINERO SIMPLE</span><span>Contenido educativo, no es asesoría financiera</span></div>'''
    # Etsy: first photo without text overlays or collage, item centred so square crops keep it (playbook on PR #2)
    cpos = [(470, 400, -8, 640), (680, 320, 0, 680), (890, 400, 8, 640)][:len(hero)]
    b0 = "".join(f'<img class="pg" src="file://{p}" style="left:{x}px;top:{y}px;width:{w}px;transform:rotate({r}deg)">'
                 for p, (x, y, r, w) in zip(hero, cpos))
    jobs = []
    for i, (body, cls, label) in enumerate([(b0, "cream", "clean"), (b1, "cream", "hero"), (b2, "ink", "inside"),
                                            (b3, "cream", "details")], 1):
        src = work / f"mock-{it['slug']}-{i}.html"
        src.write_text(_doc(body, cls))
        jobs.append({"src": str(src), "png": str(out_dir / f"mockup-{i:02d}-{label}.png"), "w": 2000, "h": 1500,
                     "scale": PHOTO_SCALE})
    return jobs


RENDER_JS = r"""
const { chromium } = require('playwright');
(async () => {
  const jobs = JSON.parse(require('fs').readFileSync(process.argv[2], 'utf8'));
  const browser = await chromium.launch();
  const report = [];
  try {
    for (const j of jobs) {
      const page = await browser.newPage({ viewport: { width: j.w || 1200, height: j.h || 900 }, deviceScaleFactor: j.scale || 1 });
      await page.goto('file://' + j.src, { waitUntil: 'load' });
      if (j.pdf) {
        const over = await page.evaluate(() => [...document.querySelectorAll('.page')]
          .map((p, i) => [i + 1, Math.max(p.scrollHeight - p.clientHeight, p.scrollWidth - p.clientWidth)]).filter(([, d]) => d > 1));
        await page.pdf({ path: j.pdf, printBackground: true, preferCSSPageSize: true, margin: { top: '0', right: '0', bottom: '0', left: '0' } });
        report.push({ out: j.pdf, overflow: over });
      } else {
        await page.screenshot({ path: j.png });
        report.push({ out: j.png, overflow: [] });
      }
      await page.close();
    }
  } finally { await browser.close(); }
  console.log(JSON.stringify(report));
})().catch(e => { console.error(String(e && e.stack || e)); process.exit(1); });
"""


def run(jobs: list[dict], work: Path) -> list[dict]:
    js, data = work / "r.js", work / "jobs.json"
    js.write_text(RENDER_JS)
    import json
    data.write_text(json.dumps(jobs))
    proc = subprocess.run(["node", str(js), str(data)], capture_output=True, text=True, env=products.node_env(), timeout=900)
    if proc.returncode:
        raise SystemExit(f"render failed:\n{proc.stderr[-3000:]}")
    return json.loads(proc.stdout.strip().splitlines()[-1])


# Etsy has banned AI-generated functional guides since Oct 22 2026 (research/scouting/ai-disclosure-rules-nov-2026.md
# on PR #2; the catalog check is launch/catalog/etsy_rules.py on PR #6). These five products are guides written with
# AI help, so they sell on Gumroad only. The listings stay as reference, in case Etsy's rule changes.
NOT_FOR_ETSY = ("> **NOT FOR ETSY.** Etsy has banned AI-generated functional guides since Oct 22 2026, and this "
                "product is a guide drafted with AI help. Sell it on Gumroad only. This listing is kept as reference "
                "in case the rule changes.\n\n")


def listing_md(it: dict, files: list[Path]) -> str:
    fee = round(0.20 + it["price"] * 0.065 + 0.25 + it["price"] * 0.03, 2)
    tags = "\n".join(f"{i}. {t}" for i, t in enumerate(it["tags"], 1))
    flist = "\n".join(f"- `{f.name}` ({f.stat().st_size / 1e6:.1f} MB)" for f in files)
    return NOT_FOR_ETSY + f"""# Etsy listing: {it['name']}

Spanish listing. Copy each field into Etsy (Shop Manager > Listings > Add a listing). Upload the four
mockups in order (01, the clean photo of the pages, is the thumbnail), then the digital files below. **A fluent Spanish speaker must
read the title, tags, description and the files before this goes live.** The title and first line were
shortened in November 2026 for Etsy's under-15-words guidance: check they still read naturally.

## Title ({len(it['title'].split())} words, {len(it['title'])}/140)
{it['title']}

## Price
${it['price']:.2f}. Etsy fees per sale about ${fee:.2f} (listing $0.20, transaction 6.5%, processing about 3% + $0.25), so you keep about **${it['price'] - fee:.2f}**.

## Listing details
- **Type:** Digital files
- **Who made it:** I did. **What is it:** A finished product. **When was it made:** the most recent range
- **Category:** {it['category']}
- **Renewal:** Automatic. **Quantity:** 999
- **Language:** if the shop's language is English, add this as the listing text anyway (Etsy shows it to everyone) or use it as the Spanish translation of an English listing. See README.md.

## Tags (13, each 20 characters or less; paste one at a time)
{tags}

## Description
```
{it['description']}
```

## Digital files to upload
{flist}
"""


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=str(HERE / "dist"))
    args = ap.parse_args()
    out_root = Path(args.out)
    by_slug = {p["slug"]: p for p in products.PRODUCTS}
    failures = []
    with tempfile.TemporaryDirectory() as tmp:
        work = Path(tmp)
        # 1. Etsy-edition PDFs for the guides that carry store-only lines
        jobs = []
        for it in LISTINGS:
            d = out_root / it["slug"]
            if d.exists():
                shutil.rmtree(d)
            d.mkdir(parents=True)
            if it["slug"] in by_slug:
                p = by_slug[it["slug"]]
                src = work / f"{it['slug']}.html"
                src.write_text(etsy_edition(p))
                jobs.append({"src": str(src), "pdf": str(d / p["pdf"])})
        for r in run(jobs, work):
            if r["overflow"]:
                failures.append(f"{Path(r['out']).name}: overflow on pages {r['overflow']}")
        # 2. files to upload
        uploads: dict[str, list[Path]] = {}
        for it in LISTINGS:
            d = out_root / it["slug"]
            if it["slug"] in products.EXISTING:
                e = products.EXISTING[it["slug"]]
                for f in e["files"]:
                    shutil.copy(e["dir"] / f, d / f)
                uploads[it["slug"]] = [d / f for f in e["files"]]
                continue
            p = by_slug[it["slug"]]
            files = [d / p["pdf"]]
            if p.get("xlsx"):
                shutil.copy(DIST / it["slug"] / p["xlsx"], d / p["xlsx"])
                files.append(d / p["xlsx"])
            uploads[it["slug"]] = files
        for it in LISTINGS:  # the bundle zip is built from the Etsy editions
            p = by_slug.get(it["slug"])
            if not p or not p.get("bundle"):
                continue
            d = out_root / it["slug"]
            z = d / p["zip"]
            with zipfile.ZipFile(z, "w", zipfile.ZIP_DEFLATED) as zf:
                for idx, slug in enumerate(p["bundle"], 1):
                    sub = next(x for x in LISTINGS if x["slug"] == slug)
                    for f in uploads[slug]:
                        zf.write(f, f"{idx}. {sub['name'].replace('$', '')}/{f.name}")
            uploads[it["slug"]].append(z)
        # 3. listing images from the real pages
        jobs = []
        for it in LISTINGS:
            d = out_root / it["slug"]
            if it.get("bundle_of"):
                firsts = []
                for slug in it["bundle_of"]:
                    pdf = next(f for f in uploads[slug] if f.suffix == ".pdf")
                    firsts += page_images(pdf, work / f"m-{it['slug']}", slug)[:1]
                hero, inside = firsts[:3], firsts
            else:
                pdf = next(f for f in uploads[it["slug"]] if f.suffix == ".pdf")
                imgs = page_images(pdf, work / f"m-{it['slug']}", "p")
                pick = lambda idx: [imgs[i - 1] for i in idx if 0 < i <= len(imgs)]  # noqa: E731
                hero, inside = pick(it["hero"]), pick(it["grid"])
            jobs += mockups(it, hero, inside, d, work)
        run(jobs, work)
        # 4. listing text + csv
        rows = []
        for it in LISTINGS:
            d = out_root / it["slug"]
            for f in uploads[it["slug"]]:
                if f.stat().st_size > MAX_MB * 1e6:
                    failures.append(f"{f.name} is over {MAX_MB} MB")
            if len(uploads[it["slug"]]) > 5:
                failures.append(f"{it['slug']}: more than 5 files")
            if len(it["title"].split()) >= 15 or not it["description"].startswith(it["what"]):
                failures.append(f"{it['slug']}: title of 15+ words, or the description doesn't open with what it is")
            if len(it["title"]) > 140 or len(it["tags"]) != 13 or any(len(t) > 20 for t in it["tags"]):
                failures.append(f"{it['slug']}: title or tags break Etsy limits")
            (d / "LISTING.md").write_text(listing_md(it, uploads[it["slug"]]))
            rows.append({"slug": it["slug"], "title": it["title"], "price": f"{it['price']:.2f}",
                         "tags": ", ".join(it["tags"]), "category": it["category"],
                         "files": " | ".join(f.name for f in uploads[it["slug"]])})
        with (out_root / "listings.csv").open("w", newline="") as fh:
            w = csv.DictWriter(fh, fieldnames=list(rows[0]))
            w.writeheader()
            w.writerows(rows)
        shutil.copy(HERE / "README.md", out_root / "README.md")
    for f in failures:
        print("FAIL", f)
    print(f"Built {len(LISTINGS)} Etsy listings into {out_root}" + (f" with {len(failures)} failures" if failures else ""))
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
