"""Build the Money Made Simple product line: guide PDFs + spreadsheet templates.

    python launch/products/build.py            # build everything into launch/products/dist/
    python launch/products/build.py --check    # also recalculate every workbook in LibreOffice
                                               # and fail on any formula error (#REF!, #VALUE!, ...)
    python launch/products/build.py --only bill-cut-kit

Each product lives in its own folder with a `guide.html` (just the <section class="page"> blocks; this
script adds the head, the shared base.css and page numbers) and a spreadsheet builder in sheets.py.
PDFs are printed with headless Chromium through Node + Playwright, and the script fails if any page's
content overflows its 8.5x11 in box (the page clips it, so a buyer would silently lose text).
"""
from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import sys
import tempfile
import zipfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import sheets  # noqa: E402

CATALOG = json.loads((HERE / "catalog.json").read_text())

RENDER_JS = r"""
const { chromium } = require('playwright');
(async () => {
  const jobs = JSON.parse(process.argv[2]);
  const browser = await chromium.launch();
  const report = [];
  try {
    for (const [src, out] of jobs) {
      const page = await browser.newPage();
      await page.goto('file://' + src, { waitUntil: 'load' });
      const over = await page.evaluate(() => [...document.querySelectorAll('.page')]
        .map((p, i) => [i + 1, p.scrollHeight - p.clientHeight]).filter(([, d]) => d > 1));
      await page.pdf({ path: out, printBackground: true, preferCSSPageSize: true,
                       margin: { top: '0', right: '0', bottom: '0', left: '0' } });
      report.push({ src, overflow: over });
      await page.close();
    }
  } finally { await browser.close(); }
  console.log(JSON.stringify(report));
})().catch(e => { console.error(String(e && e.stack || e)); process.exit(1); });
"""


def wrap_guide(product: dict) -> str:
    body = (HERE / product["slug"] / "guide.html").read_text()
    css = (HERE / "base.css").read_text()
    title = product["name"]
    n = 0

    def folio(m: re.Match) -> str:
        nonlocal n
        n += 1
        opening = m.group(0)
        return opening if "cover" in opening else opening + f'<!--folio:{n}-->'

    body = re.sub(r'<section class="page[^"]*"[^>]*>', folio, body)
    # put the folio just before the closing tag of each numbered page
    parts = re.split(r"(<!--folio:\d+-->)", body)
    out = [parts[0]]
    for i in range(1, len(parts), 2):
        num = re.search(r"\d+", parts[i]).group(0)
        chunk = parts[i + 1]
        close = chunk.find("</section>")
        chunk = chunk[:close] + f'  <div class="folio"><span>{title}</span><span>{num}</span></div>\n' + chunk[close:]
        out.append(chunk)
    return (f'<!doctype html>\n<html lang="en">\n<head>\n<meta charset="utf-8">\n'
            f'<meta name="viewport" content="width=device-width, initial-scale=1">\n<title>{title}</title>\n'
            f'<style>\n{css}\n</style>\n</head>\n<body>\n{"".join(out)}\n</body>\n</html>\n')


COVER_JS = r"""
const { chromium } = require('playwright');
(async () => {
  const jobs = JSON.parse(process.argv[2]);
  const browser = await chromium.launch();
  try {
    for (const j of jobs) {
      const page = await browser.newPage({ viewport: { width: j.w, height: j.h } });
      await page.setContent(j.html, { waitUntil: 'load' });
      await page.screenshot({ path: j.out });
      await page.close();
    }
  } finally { await browser.close(); }
})().catch(e => { console.error(String(e && e.stack || e)); process.exit(1); });
"""


def cover_html(product: dict, w: int, h: int) -> str:
    """Store cover (Gumroad 1280x720 + 600x600 square) built from the guide's own cover page."""
    src = (HERE / product["slug"] / "guide.html").read_text()
    h1 = re.search(r"<h1[^>]*>(.*?)</h1>", src, re.S).group(1).replace("<br>", " ")
    art = re.search(r"<svg class=\"art\".*?</svg>", src, re.S).group(0).replace('class="art"', "")
    square = w == h
    title_size = 64 if square else 76
    layout = ("flex-direction:column;justify-content:space-between" if square else "align-items:center")
    art_size = 230 if square else 360
    return f"""<!doctype html><html><head><meta charset="utf-8"><style>
body{{margin:0;width:{w}px;height:{h}px;background:#0b1d13;color:#f4f1e8;font-family:Inter,system-ui,sans-serif;
display:flex;{layout};padding:{48 if square else 72}px;box-sizing:border-box;gap:40px;overflow:hidden}}
.t{{flex:1}} .tag{{color:#f2b134;letter-spacing:.18em;text-transform:uppercase;font-weight:700;font-size:{15 if square else 18}px}}
h1{{font-size:{title_size}px;line-height:.98;font-weight:900;letter-spacing:-.03em;margin:18px 0}}
h1 em{{font-style:normal;color:#2fbf71}}
.price{{display:inline-block;background:#2fbf71;color:#0b1d13;font-weight:900;border-radius:999px;padding:6px 18px;font-size:{22 if square else 26}px}}
svg{{width:{art_size}px;height:{art_size}px;flex:none;{'align-self:flex-end;margin-top:-180px' if square else ''}}}
</style></head><body><div class="t"><div class="tag">Money Made Simple &middot; {'Bundle' if product.get('bundle') else 'Guide + Spreadsheet'}</div>
<h1>{h1}</h1><span class="price">${product['price']}</span></div>{art}</body></html>"""


def render_covers(products: list[dict], out_root: Path) -> None:
    jobs = []
    for p in products:
        if not (HERE / p["slug"] / "guide.html").exists():
            continue
        for name, w, h in (("cover.png", 1280, 720), ("cover-square.png", 600, 600)):
            jobs.append({"html": cover_html(p, w, h), "w": w, "h": h, "out": str(out_root / p["slug"] / name)})
    with tempfile.NamedTemporaryFile("w", suffix=".js", delete=False) as fh:
        fh.write(COVER_JS)
    try:
        proc = subprocess.run(["node", fh.name, json.dumps(jobs)], capture_output=True, text=True,
                              env=node_env(), timeout=300)
    finally:
        Path(fh.name).unlink(missing_ok=True)
    if proc.returncode:
        raise SystemExit(f"cover render failed:\n{proc.stderr}")


def node_env() -> dict:
    import os
    env = dict(os.environ)
    if not env.get("NODE_PATH") and shutil.which("npm"):
        root = subprocess.run(["npm", "root", "-g"], capture_output=True, text=True).stdout.strip()
        env["NODE_PATH"] = root
    return env


def render_pdfs(jobs: list[tuple[Path, Path]]) -> list[dict]:
    with tempfile.NamedTemporaryFile("w", suffix=".js", delete=False) as fh:
        fh.write(RENDER_JS)
    try:
        proc = subprocess.run(["node", fh.name, json.dumps([[str(a), str(b)] for a, b in jobs])],
                              capture_output=True, text=True, env=node_env(), timeout=300)
    finally:
        Path(fh.name).unlink(missing_ok=True)
    if proc.returncode:
        raise SystemExit(f"PDF render failed:\n{proc.stderr}")
    return json.loads(proc.stdout.strip().splitlines()[-1])


def recalc_check(xlsx: Path) -> list[str]:
    """Recalculate in LibreOffice and return any cells holding an error value."""
    import openpyxl
    with tempfile.TemporaryDirectory() as tmp:
        subprocess.run(["soffice", "--headless", "--calc", "--convert-to", "xlsx", "--outdir", tmp, str(xlsx)],
                       capture_output=True, timeout=180, check=True)
        wb = openpyxl.load_workbook(Path(tmp) / xlsx.name, data_only=True)
        bad = []
        for ws in wb:
            for row in ws.iter_rows():
                for c in row:
                    if isinstance(c.value, str) and re.match(r"^#(REF|VALUE|NAME|DIV/0|N/A|NUM|NULL)", c.value):
                        bad.append(f"{ws.title}!{c.coordinate}={c.value}")
        return bad


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--only", help="build one product slug")
    ap.add_argument("--check", action="store_true", help="recalculate workbooks in LibreOffice")
    ap.add_argument("--out", default=str(HERE / "dist"))
    args = ap.parse_args()
    out_root = Path(args.out)
    products = [p for p in CATALOG["products"] if not args.only or p["slug"] == args.only]

    jobs, failures = [], []
    for p in products:
        d = out_root / p["slug"]
        d.mkdir(parents=True, exist_ok=True)
        if (HERE / p["slug"] / "guide.html").exists():
            html_path = d / f'{p["slug"]}.html'
            html_path.write_text(wrap_guide(p))
            jobs.append((html_path, d / p["pdf"]))
        if p.get("xlsx"):
            getattr(sheets, p["builder"])(d / p["xlsx"])
        if (HERE / p["slug"] / "LISTING.md").exists():
            shutil.copy(HERE / p["slug"] / "LISTING.md", d / "LISTING.md")

    render_covers(products, out_root)
    for r in render_pdfs(jobs) if jobs else []:
        if r["overflow"]:
            failures.append(f'{Path(r["src"]).name}: content overflows on pages {r["overflow"]}')

    if args.check:
        for p in products:
            if p.get("xlsx"):
                bad = recalc_check(out_root / p["slug"] / p["xlsx"])
                if bad:
                    failures.append(f'{p["xlsx"]}: {len(bad)} formula errors, e.g. {bad[:5]}')

    # zips buyers download (one file per product)
    existing = {e["slug"]: e for e in CATALOG.get("existing", [])}
    for p in products:
        d = out_root / p["slug"]
        files = [(d / p["pdf"], p["pdf"])] + ([(d / p["xlsx"], p["xlsx"])] if p.get("xlsx") else [])
        for idx, slug in enumerate(p.get("bundle", []), start=1):
            if slug in existing:
                e = existing[slug]
                folder = f"{idx}. {e['name']}".replace("$", "")
                files += [(HERE / e["dir"] / f, f"{folder}/{f}") for f in e["files"]]
                continue
            other = next(o for o in CATALOG["products"] if o["slug"] == slug)
            folder = f"{idx}. {other['name']}".replace("$", "")
            od = out_root / slug
            files += [(od / other["pdf"], f"{folder}/{other['pdf']}")]
            if other.get("xlsx"):
                files += [(od / other["xlsx"], f"{folder}/{other['xlsx']}")]
        missing = [str(f) for f, _ in files if not f.exists()]
        if missing:
            failures.append(f'{p["zip"]}: missing {missing} (build the other products first)')
            continue
        with zipfile.ZipFile(d / p["zip"], "w", zipfile.ZIP_DEFLATED) as z:
            for f, arc in files:
                z.write(f, arc)

    for f in failures:
        print("FAIL", f)
    print(f"built {len(products)} product(s) into {out_root}")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
