"""Build the Etsy shop: printables (Letter + A4), Etsy editions of the six products, mockups, listings.

    python launch/products/build.py --check      # first: the product PDFs/spreadsheets
    python launch/etsy/build_etsy.py             # then: everything for Etsy, into launch/etsy/dist/

Per listing, dist/<slug>/ gets the files to upload (Etsy allows 5 files, 20 MB each), mockup images
(2000x1500, 4:3, which is what Etsy's grid shows) and LISTING.md with the title, 13 tags and description.
The build fails if a printable page overflows, or if a listing breaks Etsy's limits.
"""
from __future__ import annotations

import argparse
import csv
import html
import json
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(ROOT / "launch" / "products"))

import listings  # noqa: E402
import printables  # noqa: E402
import printables_more  # noqa: E402
from build import node_env, wrap_guide  # noqa: E402  (launch/products/build.py)

PRODUCTS_DIST = ROOT / "launch" / "products" / "dist"
ALL_PRINTABLES = {**printables.PRINTABLES, **printables_more.MORE}
SIZES = {"Letter": ("8.5in", "11in", "Letter"), "A4": ("210mm", "297mm", "A4")}

RENDER_JS = r"""
const { chromium } = require('playwright');
(async () => {
  const jobs = JSON.parse(require('fs').readFileSync(process.argv[2], 'utf8'));
  const browser = await chromium.launch();
  const report = [];
  try {
    for (const j of jobs) {
      const page = await browser.newPage({ viewport: { width: j.w || 1200, height: j.h || 900 } });
      if (j.html) await page.setContent(j.html, { waitUntil: 'load' });
      else await page.goto('file://' + j.src, { waitUntil: 'load' });
      if (j.pdf) {
        const over = await page.evaluate(() => [...document.querySelectorAll('.page')]
          .map((p, i) => [i + 1, Math.max(p.scrollHeight - p.clientHeight, p.scrollWidth - p.clientWidth)]).filter(([, d]) => d > 1));
        await page.pdf({ path: j.pdf, printBackground: true, preferCSSPageSize: true,
                         margin: { top: '0', right: '0', bottom: '0', left: '0' } });
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


def run_jobs(jobs: list[dict]) -> list[dict]:
    if not jobs:
        return []
    with tempfile.TemporaryDirectory() as tmp:
        js, data = Path(tmp) / "r.js", Path(tmp) / "jobs.json"
        js.write_text(RENDER_JS)
        data.write_text(json.dumps(jobs))
        proc = subprocess.run(["node", str(js), str(data)], capture_output=True, text=True, env=node_env(), timeout=900)
    if proc.returncode:
        raise SystemExit(f"render failed:\n{proc.stderr[-3000:]}")
    return json.loads(proc.stdout.strip().splitlines()[-1])


def printable_html(slug: str, size: str) -> str:
    w, h, name = SIZES[size]
    css = (HERE / "printables.css").read_text().replace("--w:8.5in; --h:11in;", f"--w:{w}; --h:{h};")
    pages = "".join(f'<section class="page">{p}</section>\n' for p in ALL_PRINTABLES[slug]())
    title = listings.BY_SLUG[slug]["name"]
    return (f'<!doctype html><html lang="en"><head><meta charset="utf-8"><title>{html.escape(title)}</title>'
            f'<style>@page{{size:{name};margin:0}}\n{css}</style></head><body>{pages}</body></html>')


def etsy_edition(product_slug: str, product: dict) -> str:
    """The product guide with Gumroad-specific lines swapped for Etsy-safe ones (no off-Etsy links or codes)."""
    src = wrap_guide(product)
    src = re.sub(r"<p>[^<]*code <strong>[A-Z0-9]+</strong>[^<]*</p>",
                 "<p>Search for it in the Money Made Simple shop on Etsy.</p>", src)
    src = src.replace("<p>Already bought one? Email us your receipt and we'll send a code for the difference.</p>",
                      "<p>Already bought one? Message the shop on Etsy before you order.</p>")
    src = src.replace("Find both at [your store link].", "Find both in the Money Made Simple shop on Etsy.")
    src = src.replace("Something broken, or a question? Reply to your purchase email.",
                      "Something broken, or a question? Message the shop on Etsy.")
    assert "[your store link]" not in src and "BILLCUT5" not in src, product_slug
    return src


def page_images(pdf: Path, out_dir: Path, prefix: str, first: int = 1, last: int = 99, dpi: int = 80) -> list[Path]:
    out_dir.mkdir(parents=True, exist_ok=True)
    subprocess.run(["pdftoppm", "-r", str(dpi), "-png", "-f", str(first), "-l", str(last), str(pdf), str(out_dir / prefix)],
                   check=True, capture_output=True)
    return sorted(out_dir.glob(f"{prefix}-*.png"))


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--only", nargs="*", help="one or more listing slugs")
    ap.add_argument("--out", default=str(HERE / "dist"))
    ap.add_argument("--no-mockups", action="store_true")
    args = ap.parse_args()
    out = Path(args.out)
    failures = listings.validate()
    items = [x for x in listings.LISTINGS if not args.only or x["slug"] in args.only]
    pcat = {p["slug"]: p for p in json.loads((ROOT / "launch/products/catalog.json").read_text())["products"]}
    work = Path(tempfile.mkdtemp(prefix="etsy-"))
    jobs = []

    for it in items:
        d = out / it["slug"]
        d.mkdir(parents=True, exist_ok=True)
        if it["kind"] == "printable":
            for size in SIZES:
                src = work / f'{it["slug"]}-{size}.html'
                src.write_text(printable_html(it["slug"], size))
                jobs.append({"src": str(src), "pdf": str(d / f'{it["file_stem"]}-{size}.pdf')})
        elif it["kind"] == "product" and it["slug"] in pcat:
            p = pcat[it["slug"]]
            src = work / f'{it["slug"]}.html'
            src.write_text(etsy_edition(it["slug"], p))
            jobs.append({"src": str(src), "pdf": str(d / p["pdf"])})
    for r in run_jobs(jobs):
        if r["overflow"]:
            failures.append(f'{Path(r["out"]).name}: overflow on pages {r["overflow"]}')

    # spreadsheets, existing budget, zips
    for it in items:
        d = out / it["slug"]
        if it["kind"] == "product":
            if it["slug"] == "20-minute-budget":
                for f in ("The-20-Minute-Budget.pdf", "20-Minute-Budget-Template.xlsx"):
                    shutil.copy(ROOT / "launch/product" / f, d / f)
            elif it["slug"] in pcat and pcat[it["slug"]].get("xlsx"):
                x = PRODUCTS_DIST / it["slug"] / pcat[it["slug"]]["xlsx"]
                if not x.exists():
                    failures.append(f"{x} missing: run launch/products/build.py first")
                else:
                    shutil.copy(x, d / x.name)
        if it.get("bundle"):
            _zip_bundle(it, out, failures)

    if not args.no_mockups:
        import mockups
        for it in items:
            mockups.render(it, out / it["slug"], work, run_jobs, page_images)

    for it in items:
        (out / it["slug"] / "LISTING.md").write_text(listings.listing_md(it))
    with open(out / "listings.csv", "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["slug", "title", "price", "tags", "category", "files"])
        for it in listings.LISTINGS:
            w.writerow([it["slug"], it["title"], f'{it["price"]:.2f}', ", ".join(it["tags"]), it["category"],
                        " | ".join(f.name for f in upload_files(out / it["slug"]))])
    for it in items:
        files = upload_files(out / it["slug"])
        if not files or len(files) > 5 or any(f.stat().st_size > 20 * 1024 * 1024 for f in files):
            failures.append(f'{it["slug"]}: {len(files)} upload files (Etsy allows 1-5, 20 MB each)')
    shutil.rmtree(work, ignore_errors=True)
    for f in failures:
        print("FAIL", f)
    print(f"built {len(items)} Etsy listing(s) into {out}")
    return 1 if failures else 0


def upload_files(d: Path) -> list[Path]:
    return sorted(p for p in d.glob("*") if p.suffix in (".pdf", ".xlsx", ".zip"))


def _zip_bundle(it: dict, out: Path, failures: list[str]) -> None:
    import zipfile
    d = out / it["slug"]
    with zipfile.ZipFile(d / f'{it["file_stem"]}.zip', "w", zipfile.ZIP_DEFLATED) as z:
        for i, slug in enumerate(it["bundle"], start=1):
            sub = listings.BY_SLUG[slug]
            files = upload_files(out / slug)
            if not files:
                failures.append(f"{it['slug']}: build {slug} first")
            for f in files:
                z.write(f, f"{i:02d} {sub['name'].replace('$', '')}/{f.name}")


if __name__ == "__main__":
    raise SystemExit(main())
