"""Build Etsy-ready versions of the three 1099 Money products.

    python launch/1099-money/etsy/build_etsy.py [out_dir]
    (default out_dir: /mnt/project-files/content-factory/etsy/1099-money)

For each product it writes:
  files/    the digital files to upload (Etsy: max 5 files per listing, 20 MB each)
  images/   listing images, 2400x1800 (4:3), made from the real guide pages and spreadsheet
  LISTING-ETSY.md is copied from this folder.

Etsy editions differ from the Gumroad ones only where Etsy's rules need it: no off-Etsy purchase
paths (upgrade codes by email become "see our Etsy shop"), and downloads come from Etsy's Purchases page.
Needs LibreOffice (spreadsheet screenshots), poppler (pdftoppm) and Playwright/Chromium.
"""
from __future__ import annotations

import shutil
import subprocess
import sys
import tempfile
import zipfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
BRAND = HERE.parent
ROOT = BRAND.parents[1]
sys.path.insert(0, str(ROOT / "src"))
from contentfactory.business.pdf import html_to_pdf  # noqa: E402

TRACKER = BRAND / "product"
KIT = BRAND / "products" / "rate-contract-kit"
BUNDLE = BRAND / "products" / "bundle"
CALENDAR = ROOT / "apps" / "freelance-tax" / "downloads" / "freelancer-tax-calendar-2027.pdf"

# Gumroad wording -> Etsy wording (keeps buyers on Etsy, per Etsy's fee-avoidance rules).
ETSY_SWAPS = [
    ("Already bought one? Email [your-email] for your upgrade code.",
     "It is in our Etsy shop. Already bought one there? Message us on Etsy for a coupon."),
    ("re-download from your purchase email.", "re-download any time from your Etsy Purchases page."),
]

W, H = 2400, 1800
CSS = """
*{box-sizing:border-box;margin:0;padding:0}
body{width:2400px;height:1800px;background:#14213d;color:#f7f3ea;font-family:Inter,system-ui,sans-serif;overflow:hidden;position:relative}
.cream{background:#f7f3ea;color:#14213d}
.k{font-weight:800;letter-spacing:.14em;text-transform:uppercase;color:#ff7a45;font-size:44px}
h1{font-size:150px;line-height:1.02;font-weight:900;letter-spacing:-.02em}
h1 em{font-style:normal;color:#3cc6a0}
h2{font-size:104px;line-height:1.05;font-weight:900;letter-spacing:-.02em}
p,li{font-size:52px;line-height:1.35}
.chips{display:flex;flex-wrap:wrap;gap:22px;margin-top:50px}
.chips span{border:4px solid currentColor;border-radius:999px;padding:16px 34px;font-size:40px;font-weight:700}
.pad{position:absolute;inset:130px 140px}
.page{box-shadow:0 30px 80px rgba(0,0,0,.35);border-radius:10px}
ul{list-style:none} li{padding:18px 0 18px 80px;position:relative;border-bottom:3px solid rgba(20,33,61,.12)}
li:before{content:"";position:absolute;left:0;top:30px;width:44px;height:44px;border-radius:50%;background:#3cc6a0}
.foot{position:absolute;left:140px;right:140px;bottom:90px;display:flex;justify-content:space-between;font-size:36px;opacity:.75}
.tag{display:inline-block;background:#ff7a45;color:#14213d;font-weight:900;font-size:46px;padding:14px 34px;border-radius:12px}
"""


def page_pngs(pdf: Path, out: Path, prefix: str, dpi: int = 110) -> list[Path]:
    subprocess.run(["pdftoppm", "-r", str(dpi), "-png", str(pdf), str(out / prefix)], check=True,
                   stderr=subprocess.DEVNULL)
    return sorted(out.glob(f"{prefix}-*.png"))


def sheet_png(xlsx: Path, sheet_keyword: str, out: Path, prefix: str) -> Path | None:
    """Print the workbook with LibreOffice and return the page that contains `sheet_keyword`."""
    from openpyxl import load_workbook
    wb = load_workbook(xlsx)  # temp copy printed one page wide, landscape, so columns aren't split
    for ws in wb.worksheets:
        ws.page_setup.orientation = "landscape"
        ws.page_setup.fitToWidth, ws.page_setup.fitToHeight = 1, 0
        ws.sheet_properties.pageSetUpPr.fitToPage = True
        ws.print_area = f"A1:{ws.cell(row=min(ws.max_row, 30), column=ws.max_column).coordinate}"
    copy = out / xlsx.name
    wb.save(copy)
    xlsx = copy
    try:
        subprocess.run(["soffice", "--headless", "--calc", "--convert-to", "pdf", "--outdir", str(out), str(xlsx)],
                       check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=180)
    except (OSError, subprocess.SubprocessError):
        return None
    pdf = out / (xlsx.stem + ".pdf")
    pages = page_pngs(pdf, out, prefix, dpi=170)
    for i, png in enumerate(pages, 1):
        txt = subprocess.run(["pdftotext", "-f", str(i), "-l", str(i), str(pdf), "-"], capture_output=True, text=True).stdout
        if sheet_keyword.lower() in txt.lower() and "how to use it" not in txt.lower() and "how it works" not in txt.lower():
            return png
    return None


SHOT_JS = """
const { chromium } = require('playwright');
(async () => {
  const b = await chromium.launch();
  const pg = await b.newPage({ viewport: { width: %d, height: %d } });
  for (const [src, out] of JSON.parse(process.argv[2])) {
    await pg.goto('file://' + src); await pg.waitForTimeout(150); await pg.screenshot({ path: out });
  }
  await b.close();
})();
""" % (W, H)
_QUEUE: list[tuple[str, str]] = []


def render(html: str, png: Path, tmp: Path) -> None:
    """Queue a 2400x1800 screenshot; flush() renders the queue in one browser."""
    f = tmp / (png.parent.parent.name + "-" + png.stem + ".html")
    f.write_text(f"<!doctype html><html><head><meta charset=utf-8><style>{CSS}</style></head><body{html}</body></html>")
    _QUEUE.append((str(f), str(png)))


def flush(tmp: Path) -> None:
    import json
    from contentfactory.business.pdf import _node_env
    js = tmp / "shot.js"
    js.write_text(SHOT_JS)
    subprocess.run(["node", str(js), json.dumps(_QUEUE)], check=True, env=_node_env(), timeout=600)
    _QUEUE.clear()


def images(name: str, kicker: str, title_html: str, chips: list[str], inside: list[str], steps: list[str],
           cover: Path, pages: list[Path], sheet: Path | None, formats: str, out: Path, tmp: Path) -> list[Path]:
    out.mkdir(parents=True, exist_ok=True)
    made = []
    chip_html = "".join(f"<span>{c}</span>" for c in chips)
    # 1 Hero: title + real cover page
    render(f""">
      <div class="pad" style="right:1330px"><div class="k">{kicker}</div><h1 style="margin-top:40px">{title_html}</h1>
      <div class="chips">{chip_html}</div><div style="margin-top:60px"><span class="tag">INSTANT DOWNLOAD</span></div></div>
      <img class="page" src="{cover.as_uri()}" style="position:absolute;right:140px;top:170px;height:1460px;max-width:1120px">""",
           out / "01-hero.png", tmp)
    # 2 What's inside
    render(f""" class="cream"><div class="pad"><div class="k">What's inside</div><h2 style="margin:30px 0 40px">{name}</h2>
      <ul>{''.join(f'<li>{i}</li>' for i in inside)}</ul></div>""", out / "02-inside.png", tmp)
    # 3 Real pages / spreadsheet
    if sheet is not None:
        render(f"""><div class="pad"><div class="k">The real spreadsheet</div>
          <img class="page" src="{sheet.as_uri()}" style="margin-top:40px;width:2120px;height:1400px;object-fit:contain;object-position:top left;background:#fff"></div>""",
               out / "03-spreadsheet.png", tmp)
    show = pages[1:3] if len(pages) > 2 else pages
    imgs = "".join(f'<img class="page" src="{p.as_uri()}" style="height:1340px;max-width:1030px">' for p in show)
    render(f"""><div class="pad"><div class="k">Inside the guide</div>
      <div style="display:flex;gap:50px;margin-top:50px;justify-content:center">{imgs}</div></div>""",
           out / "04-guide-pages.png", tmp)
    # 5 How it works + formats + disclaimer
    render(f""" class="cream"><div class="pad"><div class="k">How it works</div><h2 style="margin:30px 0 40px">Download, open, fill in the yellow cells.</h2>
      <ul>{''.join(f'<li>{s}</li>' for s in steps)}</ul>
      <p style="margin-top:50px;font-size:42px"><b>Works with:</b> {formats}</p></div>
      <div class="foot" style="color:#14213d"><span>1099 Money</span><span>Digital download · nothing is shipped · educational, not tax or legal advice</span></div>""",
           out / "05-how-it-works.png", tmp)
    return [Path(o) for _, o in _QUEUE if Path(o).parent == out]


def etsy_guide(folder: Path, html_name: str, pdf_name: str, out_pdf: Path, tmp: Path) -> Path:
    html = (folder / html_name).read_text()
    for a, b in ETSY_SWAPS:
        html = html.replace(a, b)
    f = tmp / html_name
    f.write_text(html)
    if not html_to_pdf(f, out_pdf):
        shutil.copy(folder / pdf_name, out_pdf)
    return out_pdf


def zip_dir(src: Path, dest: Path, arc_root: str) -> Path:
    with zipfile.ZipFile(dest, "w", zipfile.ZIP_DEFLATED) as z:
        for p in sorted(src.rglob("*")):
            if p.is_file():
                z.write(p, f"{arc_root}/{p.relative_to(src)}")
    return dest


def build(out_root: Path) -> dict[str, list[Path]]:
    made: dict[str, list[Path]] = {}
    with tempfile.TemporaryDirectory() as t:
        tmp = Path(t)
        # ---------------- tracker ($15)
        d = out_root / "quarterly-tax-tracker"
        files = d / "files"
        files.mkdir(parents=True, exist_ok=True)
        shutil.copy(TRACKER / "Quarterly-Tax-Tracker.xlsx", files / "Quarterly-Tax-Tracker.xlsx")
        shutil.copy(TRACKER / "The-Quarterly-Tax-Tracker.pdf", files / "The-Quarterly-Tax-Tracker-Guide.pdf")
        pages = page_pngs(TRACKER / "The-Quarterly-Tax-Tracker.pdf", tmp, "tr")
        sheet = sheet_png(TRACKER / "Quarterly-Tax-Tracker.xlsx", "Suggested payment", tmp, "trx")
        imgs = images("The Quarterly Tax Tracker",
                      "Spreadsheet + 10-page guide", "Quarterly<br><em>Tax</em><br>Tracker",
                      ["Excel", "Google Sheets", "Numbers", "2026 tax year"],
                      ["What to pay the IRS before each deadline, from your own logs",
                       "Safe harbor vs this year's tax, side by side",
                       "Income, expense (with categories) and mileage logs",
                       "Set-aside check: is your tax savings enough?",
                       "Every 2026 deadline + all federal tax tables",
                       "10-page guide with a $60,000 worked example"],
                      ["Setup tab: filing status and last year's tax (about 5 minutes)",
                       "Log income, expenses and miles as you go",
                       "Before each deadline, pay the Suggested payment row",
                       "Type what you paid; the year updates itself"],
                      pages[0], pages, sheet, "Excel, Google Sheets, Apple Numbers (.xlsx) · PDF guide", d / "images", tmp)
        shutil.copy(HERE / "quarterly-tax-tracker.md", d / "LISTING-ETSY.md")
        made["tracker"] = sorted(files.iterdir()) + imgs

        # ---------------- kit ($29)
        d = out_root / "rate-and-contract-kit"
        files = d / "files"
        files.mkdir(parents=True, exist_ok=True)
        shutil.copy(KIT / "Rate-and-Invoice-Kit.xlsx", files / "Rate-and-Invoice-Kit.xlsx")
        etsy_guide(KIT, "the-rate-and-contract-kit.html", "The-Rate-and-Contract-Kit.pdf",
                   files / "The-Rate-and-Contract-Kit-Guide.pdf", tmp)
        zip_dir(KIT / "templates", files / "Contract-and-Proposal-Templates.zip", "Templates")
        pages = page_pngs(files / "The-Rate-and-Contract-Kit-Guide.pdf", tmp, "kt")
        sheet = sheet_png(KIT / "Rate-and-Invoice-Kit.xlsx", "Your hourly floor", tmp, "ktx")
        imgs = images("The Rate & Contract Kit",
                      "Rate calculator + 4 templates", "Charge<br><em>enough.</em><br>Get paid.",
                      ["Excel", "Google Sheets", "Word", "Google Docs"],
                      ["Rate calculator with 2026 federal tax built in: your hourly floor",
                       "Project pricer with revision buffer and deposit",
                       "Proposal template that ends in one clear next step",
                       "13-clause freelance services agreement (plain English)",
                       "Change order for out-of-scope requests",
                       "Invoice template + invoice log that flags overdue clients"],
                      ["Rate Calculator: take-home, costs and real billable hours in",
                       "Price the project, send the proposal",
                       "Sign the agreement, invoice the deposit",
                       "Invoice on delivery; the log tracks who owes you"],
                      pages[0], pages, sheet, "Excel, Google Sheets, Numbers (.xlsx) · Word, Google Docs (.docx) · PDF guide",
                      d / "images", tmp)
        shutil.copy(HERE / "rate-and-contract-kit.md", d / "LISTING-ETSY.md")
        made["kit"] = sorted(files.iterdir()) + imgs

        # ---------------- bundle ($49)
        d = out_root / "freelancer-money-bundle"
        files = d / "files"
        files.mkdir(parents=True, exist_ok=True)
        stage = tmp / "bundle"
        (stage / "2-Quarterly-Tax-Tracker").mkdir(parents=True)
        (stage / "3-Rate-and-Contract-Kit").mkdir()
        (stage / "4-Client-Email-Scripts").mkdir()
        (stage / "5-Tax-Calendar").mkdir()
        shutil.copy(out_root / "quarterly-tax-tracker" / "files" / "Quarterly-Tax-Tracker.xlsx", stage / "2-Quarterly-Tax-Tracker")
        shutil.copy(out_root / "quarterly-tax-tracker" / "files" / "The-Quarterly-Tax-Tracker-Guide.pdf", stage / "2-Quarterly-Tax-Tracker")
        for f in (out_root / "rate-and-contract-kit" / "files").iterdir():
            shutil.copy(f, stage / "3-Rate-and-Contract-Kit")
        shutil.copy(BUNDLE / "Client-Email-Scripts.docx", stage / "4-Client-Email-Scripts")
        if CALENDAR.exists():
            shutil.copy(CALENDAR, stage / "5-Tax-Calendar")
        start = etsy_guide(BUNDLE, "the-freelancer-money-bundle.html", "Start-Here-Freelancer-Money-Bundle.pdf",
                           files / "1-Start-Here.pdf", tmp)
        zip_dir(stage, files / "Freelancer-Money-Bundle.zip", "Freelancer-Money-Bundle")
        pages = page_pngs(start, tmp, "bd")
        imgs = images("The Freelancer Money Bundle",
                      "Both kits + bonus", "Freelancer<br><em>Money</em><br>Bundle",
                      ["Tax tracker", "Rate & contract kit", "14 client emails", "2027 calendar"],
                      ["The Quarterly Tax Tracker (spreadsheet + 10-page guide)",
                       "The Rate & Contract Kit (spreadsheet + 4 templates + guide)",
                       "Bonus, bundle only: 14 client email scripts, inquiry to final notice",
                       "The 2027 Freelancer Tax Calendar (printable)",
                       "3-page start guide: set it all up in one afternoon"],
                      ["Open 1-Start-Here.pdf",
                       "Rate Calculator, then the tracker's Setup tab",
                       "Put your terms into the proposal and agreement once",
                       "Save the invoice and reminder emails as templates"],
                      pages[0], pages, sheet, "Excel, Google Sheets, Numbers · Word, Google Docs · PDF", d / "images", tmp)
        shutil.copy(HERE / "freelancer-money-bundle.md", d / "LISTING-ETSY.md")
        made["bundle"] = sorted(files.iterdir()) + imgs
        flush(tmp)
    shutil.copy(HERE / "README.md", out_root / "README.md")
    return made


def check(made: dict[str, list[Path]]) -> None:
    for name, fs in made.items():
        files = [f for f in fs if f.suffix != ".png"]
        assert 1 <= len(files) <= 5, (name, files)               # Etsy: up to 5 files per listing
        assert all(f.stat().st_size < 20 * 1024 * 1024 for f in files), name  # 20 MB each
        assert sum(f.suffix == ".png" for f in fs) >= 4, name


if __name__ == "__main__":
    out = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("/mnt/project-files/content-factory/etsy/1099-money")
    made = build(out)
    check(made)
    for k, fs in made.items():
        print(k, [f.name for f in fs])
