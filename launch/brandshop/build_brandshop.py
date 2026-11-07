"""Build the Scam Decoded and 1099 Money shop files: PDFs, the workbook, mockups, LISTING.md files and bundle zips.

    python launch/brandshop/build_brandshop.py [--brand scam-decoded 1099-money] [--no-mockups] [--check]

Output goes to launch/brandshop/dist/<brand>/<listing>/ (git-ignored). --check recalculates the workbook in LibreOffice
and fails on any formula error. Nothing is listed or uploaded anywhere.
"""
from __future__ import annotations

import argparse
import csv
import shutil
import subprocess
import sys
import tempfile
import zipfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import shop  # noqa: E402  (also puts launch/etsy on the path)
import build_etsy  # noqa: E402
import scam_decoded as SD  # noqa: E402
import ten99 as T  # noqa: E402
import ten99_sheet  # noqa: E402

SIZES = shop.SIZES

# Shorter cover lines for the mockups, where the listing name or the hook's first sentence doesn't fit or says too little.
MOCK = {
    "family-scam-safety-kit": ("Family Scam-Safety Kit", "Red flags, a family plan and what to do if it happens, in 11 printable pages."),
    "scam-fridge-cards": ("Scam Fridge Cards", "Six bold cards, one rule each, for the fridge or the desk."),
    "caller-id-script-card": ("Caller ID Script Card", "What to say when a suspicious call comes in, in large print."),
    "scam-safety-bundle": ("Scam-Safety Bundle", "The 11-page kit, six fridge cards and the caller ID script cards."),
    "freelancer-tax-planner-2027": ("2027 Freelancer Tax Planner", "Income, expenses, mileage and the four estimated-tax dates, in 25 printable pages."),
    "freelancer-tax-sheet-2027": ("2027 Freelancer Tax Tracker", "A Google Sheets and Excel tracker that adds itself up by month, quarter and category."),
    "freelancer-tax-bundle-2027": ("2027 Freelancer Tax Bundle", "The 25-page printable planner and the spreadsheet tracker together."),
}
CHIPS = {"sheet": ["Instant download", "Google Sheets + Excel"], "bundle": ["Instant download", "Printable + digital"]}


def doc(brand: shop.Brand, sections: list[tuple[str, str]], title: str, w: str, h: str, page_name: str,
        extra_css: str = "") -> str:
    body = "".join(f'<section class="{cls}">{html}</section>\n' for cls, html in sections)
    return (f'<!doctype html><html lang="en"><head><meta charset="utf-8"><title>{title}</title><style>'
            f'@page{{size:{page_name};margin:0}}\n{brand.css(w, h)}{extra_css}</style></head><body>{body}</body></html>')


def as_pages(cards: list[str]) -> list[tuple[str, str]]:
    """Cards rendered one per page, with the card itself as the measured .page (so overflow is caught)."""
    return [("page card" + (" dark" if 'class="card dark"' in c else ""), c.split(">", 1)[1].rsplit("</div>", 1)[0])
            for c in cards]


CARD_EXTRA = SD.CARD_CSS + SD.WALLET_CSS + ".page.sheet{ padding:.4in; }\n.page.card{ margin:0; }\n"


def scam_jobs(out: Path, work: Path) -> tuple[list[dict], dict[str, list[Path]]]:
    B, jobs, files = SD.BRAND, [], {}

    def add(slug: str, name: str, html: str) -> Path:
        d = out / slug
        d.mkdir(parents=True, exist_ok=True)
        src = work / f"{slug}-{name}.html"
        src.write_text(html)
        pdf = d / f"{name}.pdf"
        jobs.append({"src": str(src), "pdf": str(pdf)})
        files.setdefault(slug, []).append(pdf)
        return pdf

    for size, (w, h, pn) in SIZES.items():
        add("family-scam-safety-kit", f"Family-Scam-Safety-Kit-{size}",
            doc(B, [("page", p) for p in SD.kit_pages()], "Family Scam-Safety Kit", w, h, pn, CARD_EXTRA))
        add("scam-fridge-cards", f"Scam-Fridge-Cards-{size}",
            doc(B, [("page sheet", s) for s in SD.card_sheets(SD.fridge_cards())], "Scam Fridge Cards", w, h, pn, CARD_EXTRA))
        add("caller-id-script-card", f"Caller-ID-Script-Card-{size}",
            doc(B, [("page", SD.caller_id_large()), ("page sheet", SD.card_sheets([SD.caller_id_card()] * 2)[0]),
                    ("page sheet", SD.wallet_sheet())], "Caller ID Script Card", w, h, pn, CARD_EXTRA))
    add("scam-fridge-cards", "Scam-Fridge-Cards-4x6",
        doc(B, as_pages(SD.fridge_cards()), "Scam Fridge Cards 4x6", "6in", "4in", "6in 4in", CARD_EXTRA))
    add("caller-id-script-card", "Caller-ID-Script-Card-4x6",
        doc(B, as_pages([SD.caller_id_card()]), "Caller ID Script Card 4x6", "6in", "4in", "6in 4in", CARD_EXTRA))
    # A check-only render: each wallet card as its own measured page (not shipped).
    wsrc = work / "wallet-check.html"
    wsrc.write_text(doc(B, [("page wallet", SD.wallet_card().split(">", 1)[1].rsplit("</div>", 1)[0])], "wallet", "3.5in",
                        "2in", "3.5in 2in", CARD_EXTRA + ".page.wallet{ margin:0; }"))
    jobs.append({"src": str(wsrc), "pdf": str(work / "wallet-check.pdf")})
    return jobs, files


def ten99_jobs(out: Path, work: Path) -> tuple[list[dict], dict[str, list[Path]]]:
    B, jobs, files = T.BRAND, [], {}
    for size, (w, h, pn) in SIZES.items():
        d = out / "freelancer-tax-planner-2027"
        d.mkdir(parents=True, exist_ok=True)
        src = work / f"planner-{size}.html"
        src.write_text(doc(B, [("page", p) for p in T.planner_pages()], "2027 Freelancer Tax-Year Planner", w, h, pn))
        pdf = d / f"2027-Freelancer-Tax-Planner-{size}.pdf"
        jobs.append({"src": str(src), "pdf": str(pdf)})
        files.setdefault("freelancer-tax-planner-2027", []).append(pdf)
    d = out / "freelancer-tax-sheet-2027"
    d.mkdir(parents=True, exist_ok=True)
    src = work / "sheet-start.html"
    src.write_text(doc(B, [("page", sheet_start_page())], "Start here", "8.5in", "11in", "Letter"))
    pdf = d / "2027-Freelancer-Tax-Tracker-Start-Here.pdf"
    jobs.append({"src": str(src), "pdf": str(pdf)})
    xlsx = ten99_sheet.build(d / "2027-Freelancer-Tax-Tracker.xlsx")
    files["freelancer-tax-sheet-2027"] = [xlsx, pdf]
    return jobs, files


def sheet_start_page() -> str:
    tabs = [("Setup", "Your set-aside %, the IRS mileage rate once published, your income goal and the expense categories."),
            ("Income", "One row per payment: date, client, invoice, amount, and whether a 1099 is expected."),
            ("Expenses", "One row per business cost, with a category from the dropdown."),
            ("Mileage", "One row per business trip; the value uses the rate on Setup."),
            ("Months", "Income, expenses, profit and set-aside for each month, with a chart."),
            ("Quarters", "The four 2027 estimated-tax due dates, each quarter's profit and set-aside, and what you paid."),
            ("Categories", "Expense totals by category, ready for tax time."),
            ("Clients", "What each client paid you, and a tick when their 1099 arrives.")]
    rows = "".join(f"<tr><td class='wrap'><b>{a}</b></td><td class='wrap'>{b}</td></tr>" for a, b in tabs)
    return T.BRAND.page("Your tracker: <em>start here</em>", "2027 Freelancer Tax Tracker", f'''
      <h3 style="margin-top:0">Open it</h3>
      <ol class="steps big">
        <li><b>Google Sheets (free):</b> upload the .xlsx to Google Drive, open it, then File &gt; Save as Google Sheets.</li>
        <li><b>Excel or Apple Numbers:</b> just open the .xlsx.</li>
        <li>Delete the rows marked "(example)" on Income, Expenses, Mileage and Clients.</li>
        <li>Yellow cells are yours. Everything else is a formula; leave it alone.</li>
      </ol>
      <h3>The tabs</h3><table><tr><th style="width:20%">Tab</th><th>What it does</th></tr>{rows}</table>
      <div class="box fineprint" style="margin-top:auto">The tracker doesn't calculate your tax. The set-aside is your
      profit times a percentage you choose (pick it with a tax professional or the IRS Form 1040-ES worksheet). Federal due
      dates follow the IRS weekend and holiday rule; check irs.gov and your state. An organising tool, not tax, legal or
      financial advice. Made by 1099 Money with the help of AI tools.</div>''', kicker="1099 Money")


def sheet_preview_pages(xlsx: Path, work: Path) -> list[Path]:
    """Real pages of the workbook, printed by LibreOffice, for the mockups: Months, Quarters, Income."""
    subprocess.run(["soffice", "--headless", "--convert-to", "pdf", "--outdir", str(work), str(xlsx)],
                   capture_output=True, timeout=240, check=True)
    pdf = work / (xlsx.stem + ".pdf")
    text = subprocess.run(["pdftotext", "-layout", str(pdf), "-"], capture_output=True, text=True).stdout.split("\f")
    want = [f"{T.YEAR} month by month", "Estimated tax for", "Date paid"]
    picks = []
    for w in want:
        for i, t in enumerate(text):
            if w in t and i + 1 not in picks:
                picks.append(i + 1)
                break
    imgs = []
    for n in picks:
        imgs += build_etsy.page_images(pdf, work / "sheetprev", f"p{n}", n, n, 90)
    return imgs


def zip_bundle(name: Path, paths: list[Path]) -> Path:
    with zipfile.ZipFile(name, "w", zipfile.ZIP_DEFLATED) as z:
        for p in paths:
            z.write(p, p.name)
    return name


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--brand", nargs="*", default=["scam-decoded", "1099-money"])
    ap.add_argument("--out", default=str(HERE / "dist"))
    ap.add_argument("--no-mockups", action="store_true")
    ap.add_argument("--check", action="store_true", help="recalculate the workbook in LibreOffice")
    a = ap.parse_args()
    root = Path(a.out)
    work = Path(tempfile.mkdtemp(prefix="brandshop-"))
    failures: list[str] = []
    brands = {"scam-decoded": (SD, scam_jobs), "1099-money": (T, ten99_jobs)}
    for key in a.brand:
        mod, make = brands[key]
        out = root / key
        failures += [f"{key}: {x}" for x in shop.validate(mod.LISTINGS)]
        jobs, files = make(out, work)
        for r in build_etsy.run_jobs(jobs):
            if r["overflow"]:
                failures.append(f'{Path(r["out"]).name}: overflow on pages {r["overflow"]}')
        if key == "scam-decoded":
            b = out / "scam-safety-bundle"
            b.mkdir(parents=True, exist_ok=True)
            files["scam-safety-bundle"] = [zip_bundle(b / "Family-Scam-Safety-Bundle.zip",
                                                      [p for s in ("family-scam-safety-kit", "scam-fridge-cards", "caller-id-script-card") for p in files[s]])]
        else:
            b = out / "freelancer-tax-bundle-2027"
            b.mkdir(parents=True, exist_ok=True)
            files["freelancer-tax-bundle-2027"] = [zip_bundle(b / "2027-Freelancer-Tax-Bundle.zip",
                                                              files["freelancer-tax-planner-2027"] + files["freelancer-tax-sheet-2027"])]
            if a.check:
                sys.path.insert(0, str(shop.ROOT / "launch" / "products"))
                from build import recalc_check
                failures += recalc_check(files["freelancer-tax-sheet-2027"][0])
        for it in mod.LISTINGS:
            it["files"] = [p.name for p in files[it["slug"]]]
            if not (1 <= len(it["files"]) <= 5) or any(p.stat().st_size > 20 * 1024 * 1024 for p in files[it["slug"]]):
                failures.append(f"{it['slug']}: Etsy allows 1-5 files of 20 MB each")
        if not a.no_mockups:
            with mod.BRAND.mockup_theme() as mg:
                for it in mod.LISTINGS:
                    d = out / it["slug"]
                    pdfs = [p for p in files.get(it["slug"], []) if p.suffix == ".pdf" and "A4" not in p.name]
                    if it["kind"] == "bundle":
                        parts = [s for s in files if s != it["slug"]]
                        pdfs = [p for s in parts for p in files[s] if p.suffix == ".pdf" and "A4" not in p.name and "4x6" not in p.name]
                    if it["kind"] == "sheet":
                        pages = sheet_preview_pages(files[it["slug"]][0], work)
                    else:
                        pages = []
                        for p in pdfs:
                            pages += build_etsy.page_images(p, work / "pg" / it["slug"], p.stem, 1, 3 if it["kind"] != "kit" and it["kind"] != "print" else 9, 80)
                    hero = pages[:3] if it["kind"] not in ("bundle",) else [pages[0], pages[len(pages) // 2], pages[-1]]
                    mt, ms = MOCK[it["slug"]]
                    o = {"title": mt, "label": mod.BRAND.name, "price": it["price"], "brand": mod.BRAND.name.upper(),
                         "subtitle": ms, "chips": CHIPS.get(it["kind"], ["Instant download", "US Letter + A4"]),
                         "footer": "Educational, not advice"}
                    mg.generate(o, hero, d, sizes=("etsy", "gumroad", "square", "pin"), run=build_etsy.run_jobs,
                                inside_pages=pages[:10])
        for it in mod.LISTINGS:
            (out / it["slug"] / "LISTING.md").write_text(shop.listing_md(it, mod.BRAND))
        with open(out / "listings.csv", "w", newline="") as fh:
            w = csv.writer(fh)
            w.writerow(["slug", "title", "price", "tags", "files"])
            for it in mod.LISTINGS:
                w.writerow([it["slug"], it["title"], f"{it['price']:.2f}", ", ".join(it["tags"]), " | ".join(it["files"])])
    shutil.rmtree(work, ignore_errors=True)
    for f in failures:
        print("FAIL", f)
    print(f"built {', '.join(a.brand)} into {root}")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
