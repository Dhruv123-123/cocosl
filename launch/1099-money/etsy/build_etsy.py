"""Build the Etsy listing for 1099 Money's one Etsy product, the Quarterly Tax Tracker spreadsheet.

    python launch/1099-money/etsy/build_etsy.py [out_dir] [--edition 2027]
    (default out_dir: /mnt/project-files/content-factory/etsy/1099-money)

Etsy's 22 Oct 2026 rule bans AI-generated functional guides (instructions buyers rely on must be the seller's own
work). Our guides say honestly that AI helped draft them, so on Etsy we sell only the spreadsheet tracker, without
its PDF guide. The Rate & Contract Kit, the Freelancer Money Bundle and the Freelancer Tax Kit are Gumroad and
site only (`../products/build_gumroad.py`). The check in PR #6's launch/catalog/etsy_rules.py enforces the same rule.

It writes quarterly-tax-tracker/:
  files/    the digital file to upload (the .xlsx)
  images/   8 listing photos at 2700x2025, made from the real spreadsheet tabs
  LISTING-ETSY.md is copied from this folder.

Needs LibreOffice (spreadsheet pages), poppler (pdftoppm) and Playwright/Chromium.
"""
from __future__ import annotations

import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
BRAND = HERE.parent
ROOT = BRAND.parents[1]
sys.path.insert(0, str(ROOT / "src"))

EDITION = 2026  # `--edition 2027` packs the 2027 tax-year tracker (product/edition-2027/)
TRACKER = BRAND / "product"

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


def sheet_pages(xlsx: Path, titles: list[str], out: Path, prefix: str) -> list[Path]:
    """Print the workbook with LibreOffice (each tab one page wide, landscape) and return, for each title, the first
    page whose first line starts with it. Titles that aren't found are skipped."""
    from openpyxl import load_workbook
    wb = load_workbook(xlsx)  # temp copy printed one page wide, landscape, so columns aren't split
    for ws in wb.worksheets:
        ws.page_setup.orientation = "landscape"
        ws.page_setup.fitToWidth, ws.page_setup.fitToHeight = 1, 0
        ws.sheet_properties.pageSetUpPr.fitToPage = True
        ws.print_area = f"A1:{ws.cell(row=min(ws.max_row, 30), column=ws.max_column).coordinate}"
    work = out / prefix
    work.mkdir(parents=True, exist_ok=True)
    copy = work / xlsx.name
    wb.save(copy)
    try:
        subprocess.run(["soffice", "--headless", "--calc", "--convert-to", "pdf", "--outdir", str(work), str(copy)],
                       check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=180)
    except (OSError, subprocess.SubprocessError):
        return []
    pdf = work / (copy.stem + ".pdf")
    pages = page_pngs(pdf, work, prefix, dpi=170)
    firsts = []
    for i in range(1, len(pages) + 1):
        txt = subprocess.run(["pdftotext", "-f", str(i), "-l", str(i), str(pdf), "-"], capture_output=True, text=True).stdout
        firsts.append(txt.strip().split("\n")[0].strip().lower() if txt.strip() else "")
    found = []
    for t in titles:
        k = next((i for i, f in enumerate(firsts) if f.startswith(t.lower())), None)
        if k is not None:
            found.append(pages[k])
    return found


def sheet_png(xlsx: Path, sheet_keyword: str, out: Path, prefix: str) -> Path | None:
    """The page of the printed workbook for one tab (see sheet_pages)."""
    got = sheet_pages(xlsx, [sheet_keyword], out, prefix)
    return got[0] if got else None


SHOT_JS = """
const { chromium } = require('playwright');
(async () => {
  const b = await chromium.launch();
  const pg = await b.newPage({ viewport: { width: %d, height: %d }, deviceScaleFactor: 1.125 });  // saved at 2700x2025
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
           cover: Path, pages: list[Path], sheet: Path | None, formats: str, out: Path, tmp: Path,
           files: list[str] | None = None) -> list[Path]:
    """Eight listing photos at 2700x2025 (Etsy asks for 2,000 px or more on both sides).

    Photo 1 is clean (real pages only, centred, no text) per Etsy's first-photo advice; the text hero is photo 2.
    """
    out.mkdir(parents=True, exist_ok=True)
    chip_html = "".join(f"<span>{c}</span>" for c in chips)
    show = pages[1:3] if len(pages) > 2 else pages
    # 1 Clean first photo: real pages fanned and centred on cream, no words, safe for square crops
    fan = [show[0], cover] + show[1:2] if show and show[0] != cover else [cover]  # cover in front, centred
    rot = [-7, 0, 7][:len(fan)]
    fanned = "".join(
        f'<img class="page" src="{p.as_uri()}" style="position:absolute;left:50%;top:50%;height:1380px;'
        f'transform:translate(-50%,-50%) translateX({(k - (len(fan) - 1) / 2) * 330:.0f}px) rotate({r}deg);'
        f'z-index:{3 - abs(k - 1)}">'
        for k, (p, r) in enumerate(zip(fan, rot)))
    render(f' class="cream">{fanned}', out / "01-clean.png", tmp)
    # 2 Hero: title + real cover page
    render(f""">
      <div class="pad" style="right:1330px"><div class="k">{kicker}</div><h1 style="margin-top:40px">{title_html}</h1>
      <div class="chips">{chip_html}</div><div style="margin-top:60px"><span class="tag">INSTANT DOWNLOAD</span></div></div>
      <img class="page" src="{cover.as_uri()}" style="position:absolute;right:140px;top:170px;height:1460px;max-width:1120px">""",
           out / "02-hero.png", tmp)
    # 3 What's inside
    render(f""" class="cream"><div class="pad"><div class="k">What's inside</div><h2 style="margin:30px 0 40px">{name}</h2>
      <ul>{''.join(f'<li>{i}</li>' for i in inside)}</ul></div>""", out / "03-inside.png", tmp)
    # 4 The real spreadsheet
    if sheet is not None:
        render(f"""><div class="pad"><div class="k">The real spreadsheet</div>
          <img class="page" src="{sheet.as_uri()}" style="margin-top:40px;width:2120px;height:1400px;object-fit:contain;object-position:top left;background:#fff"></div>""",
               out / "04-spreadsheet.png", tmp)
    # 5 Real pages side by side
    two = "".join(f'<img class="page" src="{p.as_uri()}" style="height:1340px;max-width:1030px">' for p in show)
    render(f"""><div class="pad"><div class="k">Real pages from the download</div>
      <div style="display:flex;gap:50px;margin-top:50px;justify-content:center">{two}</div></div>""",
           out / "05-pages.png", tmp)
    # 6 Close-up: one page large enough to read
    close = pages[3] if len(pages) > 3 else show[-1]
    render(f""" class="cream"><img src="{close.as_uri()}" style="position:absolute;left:50%;top:-80px;width:1900px;transform:translateX(-50%);box-shadow:0 30px 80px rgba(0,0,0,.25)">
      <div style="position:absolute;left:0;right:0;bottom:0;height:300px;background:linear-gradient(rgba(247,243,234,0),#f7f3ea 60%)"></div>
      <div class="k" style="position:absolute;left:140px;bottom:90px">Close-up · {name}</div>""", out / "06-close-up.png", tmp)
    # 7 How it works
    render(f""" class="cream"><div class="pad"><div class="k">How it works</div><h2 style="margin:30px 0 40px">Download, open, fill in.</h2>
      <ul>{''.join(f'<li>{s}</li>' for s in steps)}</ul></div>
      <div class="foot" style="color:#14213d"><span>1099 Money</span><span>Digital download · nothing is shipped · educational, not tax or legal advice</span></div>""",
           out / "07-how-it-works.png", tmp)
    # 8 Files and formats
    flist = "".join(f"<li>{f}</li>" for f in (files or []))
    render(f"""><div class="pad"><div class="k">Files and formats</div><h2 style="margin:30px 0 40px;font-size:80px">Works with {formats}</h2>
      <ul>{flist}</ul></div>
      <div class="foot"><span>1099 Money</span><span>Instant download from your Etsy Purchases page</span></div>""",
           out / "08-files-and-formats.png", tmp)
    return [Path(o) for _, o in _QUEUE if Path(o).parent == out]


def build(out_root: Path) -> dict[str, list[Path]]:
    made: dict[str, list[Path]] = {}
    with tempfile.TemporaryDirectory() as t:
        tmp = Path(t)
        # ---------------- tracker ($15). The only 1099 Money product on Etsy, and spreadsheet only: Etsy's 22 Oct 2026
        # rule bans AI-generated functional guides, so the PDF guide, the Rate & Contract Kit, the bundle and the Tax
        # Kit are sold on Gumroad (and the site) only. See README.md.
        d = out_root / "quarterly-tax-tracker"
        files = d / "files"
        if files.exists():
            shutil.rmtree(files)
        files.mkdir(parents=True)
        shutil.copy(TRACKER / "Quarterly-Tax-Tracker.xlsx", files / "Quarterly-Tax-Tracker.xlsx")
        tabs = sheet_pages(TRACKER / "Quarterly-Tax-Tracker.xlsx",
                           ["The Quarterly Tax Tracker", "Quarterly estimate", "Income log", "Setup", "Mileage log",
                            "Deadlines"], tmp, "trx")
        if len(tabs) < 6:
            raise SystemExit("tracker: could not print the spreadsheet tabs (needs LibreOffice)")
        cover, quarterly, income, setup, mileage, deadlines = tabs
        imgs = images("The Quarterly Tax Tracker",
                      "Spreadsheet", "Quarterly<br><em>Tax</em><br>Tracker",
                      ["Excel", "Google Sheets", "Numbers", f"{EDITION} tax year"],
                      ["What to pay the IRS before each deadline, from your own logs",
                       "Safe harbor vs this year's tax, side by side",
                       "Income, expense (with categories) and mileage logs",
                       "Set-aside check: is your tax savings enough?",
                       f"Every {EDITION} deadline + all federal tax tables"],
                      ["Setup tab: filing status and last year's tax (about 5 minutes)",
                       "Log income, expenses and miles as you go",
                       "Before each deadline, pay the Suggested payment row",
                       "Type what you paid; the year updates itself"],
                      cover, [cover, income, mileage, setup, deadlines], quarterly,
                      "Excel, Google Sheets, Apple Numbers (.xlsx)", d / "images", tmp,
                      ["Quarterly-Tax-Tracker.xlsx: the spreadsheet (9 tabs)",
                       f"Tax tables and deadlines for the {EDITION} tax year"])
        shutil.copy(HERE / "quarterly-tax-tracker.md", d / "LISTING-ETSY.md")
        made["tracker"] = sorted(files.iterdir()) + imgs
        flush(tmp)
    shutil.copy(HERE / "README.md", out_root / "README.md")
    return made


def check(made: dict[str, list[Path]]) -> None:
    for name, fs in made.items():
        files = [f for f in fs if f.suffix != ".png"]
        assert 1 <= len(files) <= 5, (name, files)               # Etsy: up to 5 files per listing
        assert all(f.stat().st_size < 20 * 1024 * 1024 for f in files), name  # 20 MB each
        assert sum(f.suffix == ".png" for f in fs) >= 7, name
        assert not any(f.suffix in (".pdf", ".zip", ".docx") for f in files), (name, "no guides on Etsy (AI-guide rule)")
    assert set(made) == {"tracker"}, "only the spreadsheet tracker is sold on Etsy"


if __name__ == "__main__":
    argv = sys.argv[1:]
    if "--edition" in argv:
        k = argv.index("--edition")
        EDITION = int(argv[k + 1])
        del argv[k:k + 2]
        if EDITION != 2026:
            TRACKER = BRAND / "product" / f"edition-{EDITION}"
    out = Path(argv[0]) if argv else Path("/mnt/project-files/content-factory/etsy/1099-money")
    made = build(out)
    check(made)
    for k, fs in made.items():
        print(k, [f.name for f in fs])
